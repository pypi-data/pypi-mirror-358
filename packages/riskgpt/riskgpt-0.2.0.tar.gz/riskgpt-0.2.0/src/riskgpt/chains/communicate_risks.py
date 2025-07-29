from chains.base import BaseChain
from helpers.prompt_loader import load_prompt
from langchain_core.output_parsers import PydanticOutputParser
from models.chains.communication import (
    CommunicationRequest,
    CommunicationResponse,
)


async def communicate_risks_chain(
    request: CommunicationRequest,
) -> CommunicationResponse:
    """
    Chain to communicate risks effectively.
    This chain generates a summary and key points for communicating risks
    based on the provided business context and risk description.
    """

    prompt_data = load_prompt("communicate_risks")

    parser = PydanticOutputParser(pydantic_object=CommunicationResponse)
    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        prompt_name="communicate_risks",
    )

    inputs = request.model_dump(mode="json", exclude_none=True)
    return await chain.invoke(inputs)
