from chains.base import BaseChain
from helpers.prompt_loader import load_prompt
from langchain_core.output_parsers import PydanticOutputParser
from models.chains.questions import (
    ChallengeRisksRequest,
    ChallengeRisksResponse,
)


async def challenge_risks_chain(
    request: ChallengeRisksRequest,
) -> ChallengeRisksResponse:
    """
    Chain to generate challenging questions for multiple risks.

    This chain takes a list of risks and business context and generates challenging
    questions for each risk. The questions are tailored to the specified audience
    and focus areas.
    """
    prompt_data = load_prompt("challenge_risks")

    parser = PydanticOutputParser(pydantic_object=ChallengeRisksResponse)
    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        prompt_name="challenge_risks",
    )

    inputs = request.model_dump(mode="json", exclude_none=True)
    inputs["focus_areas"] = (
        ", ".join(request.focus_areas) if request.focus_areas else "--"
    )
    return await chain.invoke(inputs)
