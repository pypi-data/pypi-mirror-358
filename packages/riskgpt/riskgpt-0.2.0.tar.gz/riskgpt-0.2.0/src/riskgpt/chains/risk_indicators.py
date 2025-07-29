from chains.base import BaseChain
from helpers.prompt_loader import load_prompt
from langchain_core.output_parsers import PydanticOutputParser
from models.chains.monitoring import (
    RiskIndicatorRequest,
    RiskIndicatorResponse,
)


async def risk_indicators_chain(request: RiskIndicatorRequest) -> RiskIndicatorResponse:
    """Chain to get monitoring information based on the request."""

    prompt_data = load_prompt("risk_indicators")

    parser = PydanticOutputParser(pydantic_object=RiskIndicatorResponse)
    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        prompt_name="risk_indicators",
    )

    inputs = request.model_dump(mode="json", exclude_none=True)
    return await chain.invoke(inputs)
