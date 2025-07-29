from chains.base import BaseChain
from helpers.prompt_loader import load_prompt
from langchain_core.output_parsers import PydanticOutputParser
from models.chains.categorization import CategoryRequest, CategoryResponse


async def risk_categories_chain(request: CategoryRequest) -> CategoryResponse:
    """Asynchronous wrapper around :func:`get_categories_chain`."""
    prompt_data = load_prompt("risk_categories")

    parser = PydanticOutputParser(pydantic_object=CategoryResponse)
    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        prompt_name="risk_categories",
    )

    inputs = request.model_dump(mode="json", exclude_none=True)
    return await chain.invoke(inputs)
