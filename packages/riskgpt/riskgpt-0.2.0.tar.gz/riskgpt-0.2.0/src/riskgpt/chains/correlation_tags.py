from chains.base import BaseChain
from helpers.prompt_loader import load_prompt
from langchain_core.output_parsers import PydanticOutputParser
from models.chains.correlation import (
    CorrelationTagRequest,
    CorrelationTagResponse,
)


async def correlation_tags_chain(
    request: CorrelationTagRequest,
) -> CorrelationTagResponse:
    for risk in request.risks:
        if not risk.id:
            raise ValueError("Each risk must have a unique identifier (id).")

    prompt_data = load_prompt("correlation_tags")

    parser = PydanticOutputParser(pydantic_object=CorrelationTagResponse)
    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        prompt_name="correlation_tags",
    )

    inputs = request.model_dump(mode="json", exclude_none=True)
    return await chain.invoke(inputs)
