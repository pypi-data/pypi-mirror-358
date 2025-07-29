"""Workflow for risk identification and assessment with document integration."""

from __future__ import annotations

from typing import Any, Dict, List

import requests
from api import fetch_documents
from chains.risk_assessment import risk_assessment_chain
from chains.risk_identification import risk_identification_chain
from config.settings import RiskGPTSettings
from helpers.circuit_breaker import document_service_breaker, with_fallback
from helpers.search import search
from langgraph.graph import END, StateGraph
from logger import logger
from models import BusinessContext
from models.base import ResponseInfo
from models.chains import RiskRequest, RiskResponse
from models.chains.assessment import AssessmentRequest


def _documents_fallback(context: BusinessContext) -> List[str]:
    """Fallback when the document service is unavailable."""
    logger.warning("Document service unavailable, returning empty list")
    return []


@document_service_breaker
@with_fallback(_documents_fallback)
def fetch_relevant_documents(context: BusinessContext) -> List[str]:
    """Fetch relevant document UUIDs from the document service."""
    logger.info("Fetching relevant documents for project %s", context.project_id)
    settings = RiskGPTSettings()
    if not settings.DOCUMENT_SERVICE_URL:
        logger.warning("DOCUMENT_SERVICE_URL not configured")
        return []

    url = f"{settings.DOCUMENT_SERVICE_URL.rstrip('/')}/search"
    try:
        resp = requests.post(url, json=context.model_dump(), timeout=10)
        resp.raise_for_status()
    except Exception as exc:
        logger.error("Document service request failed: %s", exc)
        raise

    try:
        data = resp.json()
    except Exception:
        logger.warning("Invalid JSON response from document service")
        return []

    if isinstance(data, dict):
        docs = data.get("documents")
    else:
        docs = data

    if not isinstance(docs, list):
        logger.warning("Unexpected document service response format")
        return []

    return [str(d) for d in docs]


def _build_risk_workflow_graph(request: RiskRequest, use_full_workflow: bool = True):
    """
    Build and compile the risk workflow graph.

    Args:
        request: The risk request containing business context and category
    """

    if StateGraph is None:
        raise ImportError("langgraph is required for this workflow")

    graph = StateGraph(Dict[str, Any])

    settings = RiskGPTSettings()
    totals: Dict[str, float | int] = {"tokens": 0, "cost": 0.0}

    def initialize_state(state: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize the state with the request if it exists in the input."""
        if "request" in state and isinstance(state["request"], RiskRequest):
            # Use the request from the input state
            pass
        else:
            # Use the request passed to _build_graph
            state["request"] = request

        return state

    async def search_for_context(state: Dict[str, Any]) -> Dict[str, Any]:
        """Search for relevant context using the search provider."""
        req = state["request"]
        logger.info("Searching for context related to '%s'", req.category)

        # Build search query from business context and category
        query = f"{req.business_context.project_description or req.business_context.project_id} {req.business_context.domain_knowledge or ''} {req.category} risks"

        # Perform search
        search_results, success = search(query, "risk_context")
        if success and search_results:
            state["search_results"] = search_results
            logger.info("Found %d search results", len(search_results))

            # Extract references from search results
            references = [result.get("title", "") for result in search_results]
            state["references"] = references
        else:
            logger.warning("Search failed or returned no results")
            state["search_results"] = []
            state["references"] = []

        return state

    def fetch_documents_step(state: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch relevant documents for the business context."""
        req = state["request"]
        logger.info(
            "Fetching documents for project '%s'", req.business_context.project_id
        )

        # Call the API helper that integrates with the document service
        document_refs = fetch_documents(req.business_context)
        state["document_refs"] = document_refs

        logger.info("Found %d relevant documents", len(document_refs))
        return state

    async def identify_risks(state: Dict[str, Any]) -> Dict[str, Any]:
        """Identify risks using direct implementation to avoid circular dependency."""
        req = state["request"]
        logger.info("Identify risks for category '%s'", req.category)

        # Create a copy of the request with document_refs if available
        risk_request = RiskRequest(
            business_context=req.business_context,
            category=req.category,
            max_risks=req.max_risks,
            existing_risks=req.existing_risks,
        )

        # If we have document_refs in the state, add them to the request
        if "document_refs" in state and state["document_refs"]:
            risk_request.document_refs = state["document_refs"]

        res = await risk_identification_chain(risk_request)

        if res.response_info:
            totals["tokens"] += res.response_info.consumed_tokens
            totals["cost"] += res.response_info.total_cost

        # Add search references if they exist in the state
        if "references" in state and state["references"]:
            res.references = state["references"]

        # Add document_refs if they exist in the state
        if (
            "document_refs" in state
            and state["document_refs"]
            and not hasattr(res, "document_refs")
        ):
            res.document_refs = state["document_refs"]

        state["risks"] = res.risks
        state["risk_response"] = res
        return state

    async def assess_risks(state: Dict[str, Any]) -> Dict[str, Any]:
        """Assess each identified risk using the get_assessment_chain."""
        req = state["request"]
        assessments = []

        for risk in state.get("risks", []):
            logger.info("Assess risk '%s'", risk.title)

            # Create assessment request
            assessment_request = AssessmentRequest(
                business_context=req.business_context,
                risk_description=risk.description,
                risk_title=risk.title,
            )

            # If we have document_refs in the state, add them to the request
            if "document_refs" in state and state["document_refs"]:
                assessment_request.document_refs = state["document_refs"]

            # If we have references in the state, add them to the request context
            if "references" in state and state["references"]:
                # We can't directly add references to the request, but we can enhance the context
                additional_context = (
                    f"\nRelevant references: {', '.join(state['references'])}"
                )
                assessment_request.risk_description += additional_context

            assess = await risk_assessment_chain(assessment_request)

            if assess.response_info:
                totals["tokens"] += assess.response_info.consumed_tokens
                totals["cost"] += assess.response_info.total_cost

            # Add document_refs to the response if they exist in the state
            if (
                "document_refs" in state
                and state["document_refs"]
                and not hasattr(assess, "document_refs")
            ):
                assess.document_refs = state["document_refs"]

            assessments.append(assess)

        state["assessments"] = assessments
        return state

    def prepare_response(state: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare the final response."""
        risk_response = state.get("risk_response")

        # Create a new response with the same risks
        # Check if risk_response is None before accessing its attributes
        if risk_response is None:
            # If risk_response is None, create a response with empty lists
            response = RiskResponse(
                risks=[],
            )
        else:
            response = RiskResponse(
                risks=risk_response.risks,
            )

        # Add document_refs if they exist in the state
        if "document_refs" in state and state["document_refs"]:
            response.document_refs = state["document_refs"]

        # Add response info
        response.response_info = ResponseInfo(
            consumed_tokens=int(totals["tokens"]),
            total_cost=float(totals["cost"]),
            prompt_name="risk_workflow",
            model_name=settings.OPENAI_MODEL_NAME,
        )

        state["response"] = response
        return state

    # Add nodes to the graph
    graph.add_node("initialize", initialize_state)
    graph.add_node("search_for_context", search_for_context)
    graph.add_node("fetch_documents", fetch_documents_step)
    graph.add_node("identify_risks", identify_risks)
    graph.add_node("assess_risks", assess_risks)
    graph.add_node("prepare_response", prepare_response)

    # Set the entry point
    graph.set_entry_point("initialize")

    # Add edges to define the flow (always full workflow)
    graph.add_edge("initialize", "search_for_context")
    graph.add_edge("search_for_context", "fetch_documents")
    graph.add_edge("fetch_documents", "identify_risks")
    graph.add_edge("identify_risks", "assess_risks")
    graph.add_edge("assess_risks", "prepare_response")

    graph.add_edge("prepare_response", END)

    return graph.compile()


async def risk_workflow(request: RiskRequest) -> RiskResponse:
    """
    Asynchronous version of the risk workflow.

    Args:
        request: The risk request containing business context and category

    Returns:
        A risk response containing identified risks and document references
    """
    app = _build_risk_workflow_graph(request)
    result = await app.ainvoke({"request": request})
    return result["response"]
