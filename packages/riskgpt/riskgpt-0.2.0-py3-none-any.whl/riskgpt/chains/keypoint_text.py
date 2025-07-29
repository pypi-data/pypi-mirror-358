from chains.base import BaseChain
from helpers.prompt_loader import load_prompt
from langchain_core.output_parsers import PydanticOutputParser
from models.workflows.context import (
    KeyPointTextRequest,
    KeyPointTextResponse,
)


async def keypoint_text_chain(
    request: KeyPointTextRequest,
) -> KeyPointTextResponse:
    """
    Chain to generate text from key points with Harvard-style citations.

    This chain takes a list of KeyPoint objects and generates a coherent text
    that incorporates all the key points with proper Harvard-style citations.
    The output includes both the text with inline citations and a references
    section formatted in Harvard style.
    """
    prompt_data = load_prompt("keypoint_text")

    parser = PydanticOutputParser(pydantic_object=KeyPointTextResponse)
    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        prompt_name="keypoint_text",
    )

    inputs = {
        "key_points": "\n".join(
            [
                f"- {kp.topic.value}: {kp.content} {kp.source_url}"
                for kp in request.key_points
            ]
        )
    }
    return await chain.invoke(inputs)
