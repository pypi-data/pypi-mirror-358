from chains.base import BaseChain
from helpers.prompt_loader import load_prompt
from langchain_core.output_parsers import PydanticOutputParser
from models.chains.mitigation import CostBenefitRequest, CostBenefitResponse


async def cost_benefit_chain(request: CostBenefitRequest) -> CostBenefitResponse:
    """
    Cost-benefit analysis chain for risk mitigation measures.
    This chain evaluates the cost and benefit of proposed mitigations
    based on the provided risk description and business context.
    """

    prompt_data = load_prompt("cost_benefit")

    parser = PydanticOutputParser(pydantic_object=CostBenefitResponse)
    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        prompt_name="cost_benefit",
    )

    inputs = request.model_dump(mode="json", exclude_none=True)
    return await chain.invoke(inputs)
