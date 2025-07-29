"""
Categorization models for RiskGPT.

This module contains models for risk category identification.
"""

from typing import List, Optional

from models.base import BaseRequest, BaseResponse
from models.common import BusinessContext
from pydantic import ConfigDict, Field


class CategoryRequest(BaseRequest):
    """Input model for category identification."""

    business_context: BusinessContext = Field(
        description="Business context information"
    )
    existing_categories: Optional[List[str]] = Field(
        default=None, description="List of existing categories to consider"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "business_context": {
                    "project_id": "CRM-2023",
                    "project_description": "Implementation of a new CRM system",
                },
                "existing_categories": ["Technical", "Organizational"],
            }
        }
    )


class CategoryResponse(BaseResponse):
    """Output model for identified categories."""

    categories: List[str] = Field(description="List of identified risk categories")
    rationale: Optional[str] = Field(
        default=None, description="Explanation for the identified categories"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "categories": ["Technical", "Organizational", "Financial", "Legal"],
                "rationale": "These categories cover the main risk areas for a CRM implementation project.",
                "model_version": "1.0",
                "response_info": {
                    "consumed_tokens": 1250,
                    "total_cost": 0.025,
                    "prompt_name": "risk_categories",
                    "model_name": "gpt-4",
                },
            }
        }
    )
