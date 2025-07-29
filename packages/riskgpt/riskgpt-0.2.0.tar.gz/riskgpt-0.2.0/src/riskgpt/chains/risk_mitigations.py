from chains.base import BaseChain
from helpers.prompt_loader import load_prompt
from langchain_core.output_parsers import PydanticOutputParser
from models.chains.mitigation import MitigationRequest, MitigationResponse


async def risk_mitigations_chain(request: MitigationRequest) -> MitigationResponse:
    """
    Get mitigations for a given risk.
    """
    prompt_data = load_prompt("risk_mitigations")

    parser = PydanticOutputParser(pydantic_object=MitigationResponse)
    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        prompt_name="risk_mitigations",
    )

    inputs = request.model_dump(mode="json", exclude_none=True)
    return await chain.invoke(inputs)
