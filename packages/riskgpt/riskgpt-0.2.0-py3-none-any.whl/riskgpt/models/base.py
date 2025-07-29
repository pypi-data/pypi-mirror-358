"""
Base models and common utilities for RiskGPT.

This module contains the base models and common utilities used throughout the RiskGPT system.
"""

from typing import Optional

from models.enums import LanguageEnum
from pydantic import BaseModel, ConfigDict, Field


class ResponseInfo(BaseModel):
    """Information about the response processing."""

    consumed_tokens: int
    total_cost: float
    prompt_name: str
    model_name: str
    error: Optional[str] = None


def default_response_info(
    prompt_name: str = "unknown",
    model_name: str = "unknown",
    consumed_tokens: int = 0,
    total_cost: float = 0.0,
    error: Optional[str] = None,
) -> ResponseInfo:
    """Create a default ResponseInfo object."""
    return ResponseInfo(
        consumed_tokens=consumed_tokens,
        total_cost=total_cost,
        prompt_name=prompt_name,
        model_name=model_name,
        error=error,
    )


class BaseResponse(BaseModel):
    """Base class for all response models."""

    model_version: str = Field(
        default="1.0", description="Schema version for backward compatibility"
    )
    response_info: ResponseInfo = Field(
        default_factory=default_response_info,
        description="Information about the response processing",
    )


class BaseRequest(BaseModel):
    """Base class for all request models."""

    model_version: str = Field(
        default="1.0", description="Schema version for backward compatibility"
    )
    language: Optional[LanguageEnum] = Field(
        default=LanguageEnum.english, description="Language for the response"
    )

    model_config = ConfigDict(use_enum_values=True)
