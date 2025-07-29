from chains.base import BaseChain
from helpers.prompt_loader import load_prompt
from langchain_core.output_parsers import PydanticOutputParser
from models.chains.questions import (
    ChallengeQuestionsRequest,
    ChallengeQuestionsResponse,
)


async def challenge_questions_chain(
    request: ChallengeQuestionsRequest,
) -> ChallengeQuestionsResponse:
    """
    Chain to generate challenging questions from business context for internet search.

    This chain takes a business context and generates challenging questions that can be
    used as search queries for internet research. The questions are tailored to the
    specified audience and focus areas.
    """
    prompt_data = load_prompt("challenge_questions")

    parser = PydanticOutputParser(pydantic_object=ChallengeQuestionsResponse)
    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        prompt_name="challenge_questions",
    )

    inputs = request.model_dump(mode="json", exclude_none=True)
    inputs["focus_areas"] = (
        ", ".join(request.focus_areas) if request.focus_areas else "--"
    )
    return await chain.invoke(inputs)
