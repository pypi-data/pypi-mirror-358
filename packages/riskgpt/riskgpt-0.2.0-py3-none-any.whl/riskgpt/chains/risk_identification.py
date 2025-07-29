from chains.base import BaseChain
from helpers.prompt_loader import load_prompt
from langchain_core.output_parsers import PydanticOutputParser
from models.chains.risk import RiskRequest, RiskResponse


async def risk_identification_chain(request: RiskRequest) -> RiskResponse:
    prompt_data = load_prompt("risk_identification")

    parser = PydanticOutputParser(pydantic_object=RiskResponse)
    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        prompt_name="risk_identification",
    )

    inputs = request.model_dump(mode="json", exclude_none=True)
    return await chain.invoke(inputs)
