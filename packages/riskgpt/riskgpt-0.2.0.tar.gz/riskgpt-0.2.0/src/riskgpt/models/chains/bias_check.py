"""
Bias check models for RiskGPT.

This module contains models for checking biases in risk descriptions.
"""

from typing import List, Optional

from models.base import BaseResponse
from models.common import BusinessContext
from pydantic import BaseModel, ConfigDict


class BiasCheckRequest(BaseModel):
    """Input for checking risk description biases."""

    business_context: Optional[BusinessContext] = None
    risk_description: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "business_context": {
                    "project_id": "CRM-2023",
                    "project_description": "Implementation of a new CRM system",
                },
                "risk_description": "There is a 30% probability that the CRM implementation will experience critical technical failures within the first 3 months of deployment.",
            }
        }
    )


class BiasCheckResponse(BaseResponse):
    """Output model containing identified biases and suggestions."""

    biases: List[str]
    suggestions: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "biases": ["Overconfidence bias", "Anchoring bias"],
                "suggestions": "Consider using a range of probabilities instead of a single value. Also, provide more context about the basis for the 30% probability estimate.",
                "model_version": "1.0",
                "response_info": {
                    "consumed_tokens": 1200,
                    "total_cost": 0.024,
                    "prompt_name": "check_bias",
                    "model_name": "gpt-4",
                },
            }
        }
    )
