from __future__ import annotations

from typing import Any, Dict, List, TypedDict

from chains.communicate_risks import communicate_risks_chain
from chains.correlation_tags import correlation_tags_chain
from chains.risk_assessment import risk_assessment_chain
from chains.risk_drivers import risk_drivers_chain
from chains.risk_identification import risk_identification_chain
from chains.risk_mitigations import risk_mitigations_chain
from config.settings import RiskGPTSettings
from langgraph.graph import END, StateGraph
from logger import logger
from models.base import ResponseInfo
from models.chains import (
    CommunicationRequest,
    CorrelationTag,
    CorrelationTagRequest,
    Mitigation,
    MitigationRequest,
    Risk,
    RiskRequest,
)
from models.chains.assessment import AssessmentRequest
from models.chains.drivers import DriverRequest, RiskDriver
from models.enums import AudienceEnum
from models.workflows.presentation import (
    PresentationRequest,
    PresentationResponse,
)

settings = RiskGPTSettings()


def apply_audience_formatting(
    resp: PresentationResponse, audience: AudienceEnum
) -> PresentationResponse:
    """Adjust output fields based on the target audience."""
    if audience == AudienceEnum.executive:
        resp.main_risks = resp.main_risks[:3]
        resp.chart_placeholders = ["executive_overview_chart"]
        resp.open_questions = None
    elif audience == AudienceEnum.workshop:
        resp.open_questions = ["Discuss mitigation priorities"]
    elif audience == AudienceEnum.risk_internal:
        resp.appendix = (resp.appendix or "") + "\n[Model parameters]"
    elif audience == AudienceEnum.audit:
        resp.appendix = (resp.appendix or "") + "\n[Audit trail]"
    elif audience == AudienceEnum.regulator:
        resp.appendix = (resp.appendix or "") + "\n[Compliance mapping]"
    elif audience == AudienceEnum.project_owner:
        resp.appendix = (resp.appendix or "") + "\n[Project milestones]"
    elif audience == AudienceEnum.investor:
        resp.appendix = (resp.appendix or "") + "\n[Financial impact]"
    elif audience == AudienceEnum.operations:
        resp.appendix = (resp.appendix or "") + "\n[KRI dashboard]"
    return resp


class State(TypedDict):
    request: PresentationRequest
    risks: List[Risk]
    assessments: List[AssessmentRequest]
    drivers: List[List[RiskDriver]]
    mitigations: List[List[Mitigation]]
    correlation_tags: List[CorrelationTag]
    response: PresentationResponse
    response_info: ResponseInfo


def _build_graph(request: PresentationRequest):
    graph = StateGraph(State)

    totals: Dict[str, float | int] = {"tokens": 0, "cost": 0.0}

    def initialize_state(state: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize the state with the request if it exists in the input."""
        if "request" in state and isinstance(state["request"], PresentationRequest):
            # Use the request from the input state
            pass
        else:
            # Use the request passed to _build_graph
            state["request"] = request
        return state

    async def identify_risks(state: Dict[str, Any]) -> Dict[str, Any]:
        req = state["request"]
        category = (req.focus_areas or ["General"])[0]
        logger.info("Identify risks for category '%s'", category)
        res = await risk_identification_chain(
            RiskRequest(
                business_context=req.business_context,
                category=category,
            )
        )
        if res.response_info:
            totals["tokens"] += res.response_info.consumed_tokens
            totals["cost"] += res.response_info.total_cost
        state["risks"] = res.risks
        return state

    async def assess_risks(state: Dict[str, Any]) -> Dict[str, Any]:
        req = state["request"]
        assessments = []
        for risk in state.get("risks", []):
            logger.info("Assess risk '%s'", risk.title)
            assess = await risk_assessment_chain(
                AssessmentRequest(
                    business_context=req.business_context,
                    risk_description=risk.description,
                    risk_title=risk.title,
                )
            )
            if assess.response_info:
                totals["tokens"] += assess.response_info.consumed_tokens
                totals["cost"] += assess.response_info.total_cost
            assessments.append(assess)
        state["assessments"] = assessments
        return state

    async def drivers(state: Dict[str, Any]) -> Dict[str, Any]:
        req = state["request"]
        driver_lists: List[List[str]] = []
        for risk in state.get("risks", []):
            logger.info("Get drivers for '%s'", risk.title)
            res = await risk_drivers_chain(
                DriverRequest(
                    business_context=req.business_context,
                    risk=risk,
                )
            )
            if res.response_info:
                totals["tokens"] += res.response_info.consumed_tokens
                totals["cost"] += res.response_info.total_cost
            driver_lists.append(res.drivers)
        state["drivers"] = driver_lists
        return state

    async def mitigations(state: Dict[str, Any]) -> Dict[str, Any]:
        req = state["request"]
        mitigation_lists: List[List[str]] = []
        for risk, drv in zip(state.get("risks", []), state.get("drivers", [])):
            logger.info("Get mitigations for '%s'", risk.title)
            res = await risk_mitigations_chain(
                MitigationRequest(
                    business_context=req.business_context,
                    risk=risk,
                    risk_drivers=drv,
                )
            )
            if res.response_info:
                totals["tokens"] += res.response_info.consumed_tokens
                totals["cost"] += res.response_info.total_cost
            mitigation_lists.append(res.mitigations)
        state["mitigations"] = mitigation_lists
        return state

    async def correlation(state: Dict[str, Any]) -> Dict[str, Any]:
        req = state["request"]
        known = [d for lst in state.get("drivers", []) for d in lst]
        logger.info("Define correlation tags")
        res = await correlation_tags_chain(
            CorrelationTagRequest(
                business_context=req.business_context,
                risks=state.get("risks", []),
                known_drivers=known or None,
            )
        )
        if res.response_info:
            totals["tokens"] += res.response_info.consumed_tokens
            totals["cost"] += res.response_info.total_cost
        state["correlation_tags"] = res.tags
        return state

    async def summary(state: Dict[str, Any]) -> Dict[str, Any]:
        req = state["request"]
        lines = []
        for risk, assess in zip(state.get("risks", []), state.get("assessments", [])):
            line = f"{risk.title}: P={assess.probability or 'n/a'}, I={assess.impact or 'n/a'}"
            lines.append(line)
        text = "\n".join(lines)
        com = await communicate_risks_chain(
            CommunicationRequest(
                business_context=req.business_context,
                audience=req.audience,
                risks=state.get("risks", []),
            )
        )
        if com.response_info:
            totals["tokens"] += com.response_info.consumed_tokens
            totals["cost"] += com.response_info.total_cost
        resp = PresentationResponse(
            executive_summary=com.executive_summary,
            main_risks=[r.title for r in state.get("risks", [])],
            quantitative_summary=text,
            key_drivers=[d for lst in state.get("drivers", []) for d in lst],
            correlation_tags=state.get("../prompts/correlation_tags"),
            mitigations=[m for lst in state.get("mitigations", []) for m in lst],
            open_questions=[],
            chart_placeholders=["risk_overview_chart"],
            appendix=com.technical_annex,
        )
        resp.response_info = ResponseInfo(
            consumed_tokens=int(totals["tokens"]),
            total_cost=float(totals["cost"]),
            prompt_name="prepare_presentation_output",
            model_name=settings.OPENAI_MODEL_NAME,
        )
        state["response"] = apply_audience_formatting(resp, req.audience)
        return state

    graph.add_node("initialize", initialize_state)
    graph.add_node("identify_risks", identify_risks)
    graph.add_node("assess_risks", assess_risks)
    graph.add_node("drivers", drivers)
    graph.add_node("mitigations", mitigations)
    graph.add_node("correlation", correlation)
    graph.add_node("summary", summary)

    graph.set_entry_point("initialize")
    graph.add_edge("initialize", "identify_risks")
    graph.add_edge("identify_risks", "assess_risks")
    graph.add_edge("assess_risks", "drivers")
    graph.add_edge("drivers", "mitigations")
    graph.add_edge("mitigations", "correlation")
    graph.add_edge("correlation", "summary")
    graph.add_edge("summary", END)

    return graph.compile()


async def prepare_presentation_output(
    request: PresentationRequest,
) -> PresentationResponse:
    """Run the presentation workflow asynchronously and return a structured response."""

    app = _build_graph(request)
    result = await app.ainvoke({"request": request})
    return result["response"]
