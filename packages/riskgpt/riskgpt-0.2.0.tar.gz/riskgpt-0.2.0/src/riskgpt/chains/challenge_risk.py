from chains.base import BaseChain
from helpers.prompt_loader import load_prompt
from langchain_core.output_parsers import PydanticOutputParser
from models.chains.questions import (
    ChallengeRiskRequest,
    ChallengeRiskResponse,
)


async def challenge_risk_chain(
    request: ChallengeRiskRequest,
) -> ChallengeRiskResponse:
    """
    Chain to generate challenging questions for a specific risk.

    This chain takes a risk and business context and generates challenging questions
    that can help stakeholders better understand and address the risk. The questions
    are tailored to the specified audience and focus areas.
    """
    prompt_data = load_prompt("challenge_risk")

    parser = PydanticOutputParser(pydantic_object=ChallengeRiskResponse)
    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        prompt_name="challenge_risk",
    )

    inputs = request.model_dump(mode="json", exclude_none=True)
    inputs["focus_areas"] = (
        ", ".join(request.focus_areas) if request.focus_areas else "--"
    )
    return await chain.invoke(inputs)
