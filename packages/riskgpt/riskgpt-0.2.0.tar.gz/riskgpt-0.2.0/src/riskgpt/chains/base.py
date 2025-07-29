from __future__ import annotations

import typing
from typing import Any, Dict, Optional

from config.settings import RiskGPTSettings
from helpers.circuit_breaker import openai_breaker, with_fallback
from helpers.memory_factory import get_memory
from helpers.misc import flatten_dict
from helpers.prompt_loader import load_system_prompt
from langchain.chat_models import init_chat_model
from langchain_community.callbacks import get_openai_callback
from langchain_core.output_parsers import BaseOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langsmith import traceable
from logger import logger
from models.base import ResponseInfo


class BaseChain:
    """Reusable chain setup for prompt -> model -> parser pattern."""

    def __init__(
        self,
        prompt_template: str,
        parser: BaseOutputParser,
        *,
        settings: Optional[RiskGPTSettings] = None,
        prompt_name: str = "",
    ) -> None:
        self.settings = settings or RiskGPTSettings()
        self.prompt_name = prompt_name
        self.parser = parser

        self.prompt = ChatPromptTemplate.from_template(
            template=prompt_template,
            partial_variables=self._partial_variables(),
        )

        if self.settings.OPENAI_API_KEY:
            self.model = init_chat_model(
                api_key=self.settings.OPENAI_API_KEY,
                temperature=self.settings.TEMPERATURE,
                model=self.settings.OPENAI_MODEL_NAME,
                max_tokens=self.settings.MAX_TOKENS,  # type: ignore
            )
        else:
            raise ValueError(
                "OPENAI_API_KEY is not set. Please provide a valid API key."
            )

        self.memory = get_memory(self.settings)
        self.chain = self.prompt | self.model | self.parser

    def _partial_variables(self) -> Dict[str, str]:
        fmt = self.parser.get_format_instructions()
        fmt = fmt.replace("{", "{{").replace("}", "}}")
        return {"format_instructions": fmt}

    async def _fallback_response(self, inputs: Dict[str, Any]):
        """Fallback response when the circuit is open."""
        logger.warning(
            "Circuit is open for OpenAI API, using fallback response for '%s'",
            self.prompt_name or "prompt",
        )

        # If we have a parser with a pydantic object, create a minimal valid response
        if hasattr(self.parser, "pydantic_object"):
            try:
                # Create a minimal valid instance of the pydantic object
                data: Dict[str, Any] = {}
                for name, field in self.parser.pydantic_object.model_fields.items():
                    if field.is_required():
                        if (
                            field.annotation is str
                            or typing.get_origin(field.annotation) is str
                        ):
                            data[name] = "Service temporarily unavailable"
                        elif (
                            field.annotation is list
                            or typing.get_origin(field.annotation) is list
                        ):
                            data[name] = []
                        else:
                            data[name] = None

                result = self.parser.pydantic_object.model_validate(data)

                # Add response info if supported
                if hasattr(result, "response_info"):
                    result.response_info = ResponseInfo(
                        consumed_tokens=0,
                        total_cost=0.0,
                        prompt_name=self.prompt_name,
                        model_name=self.settings.OPENAI_MODEL_NAME,
                        error="Service temporarily unavailable",
                    )
                return result
            except Exception as e:
                logger.error("Failed to create fallback response: %s", e)

        # If we can't create a valid pydantic object, return a simple dict
        return {"error": "Service temporarily unavailable"}

    @openai_breaker
    @with_fallback(_fallback_response)
    @traceable
    async def invoke(self, inputs: Dict[str, Any]):
        """Invoke the underlying chain asynchronously."""
        with get_openai_callback() as cb:
            inputs = flatten_dict(inputs)
            inputs["system_prompt"] = load_system_prompt()

            result = await self.chain.ainvoke(inputs, memory=self.memory)
            if hasattr(result, "response_info"):
                result.response_info = ResponseInfo(
                    consumed_tokens=cb.total_tokens,
                    total_cost=cb.total_cost,
                    prompt_name=self.prompt_name,
                    model_name=self.settings.OPENAI_MODEL_NAME,
                )
            logger.info(
                "Consumed %s tokens (%.4f USD) for '%s' using %s",
                cb.total_tokens,
                cb.total_cost,
                self.prompt_name or "prompt",
                self.settings.OPENAI_MODEL_NAME,
            )
        return result
