"""
Correlation models for RiskGPT.

This module contains models for correlation analysis between risks.
"""

from typing import List, Optional

from models.base import BaseRequest, BaseResponse
from models.chains.risk import Risk
from models.common import BusinessContext
from pydantic import BaseModel, ConfigDict


class CorrelationTag(BaseModel):
    tag: str
    justification: str
    risk_ids: List[str]  # Use risk IDs or titles from the provided 'risks' input

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tag": "Technical Infrastructure",
                "justification": "These risks are related to the technical infrastructure of the CRM system",
                "risk_ids": ["RISK-001", "RISK-003"],
            }
        }
    )


class CorrelationTagRequest(BaseRequest):
    """Input model for defining correlation tags."""

    business_context: BusinessContext
    risks: List[Risk]
    known_drivers: Optional[List[str]] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "business_context": {
                    "project_id": "CRM-2023",
                    "project_description": "Implementation of a new CRM system",
                },
                "risks": [
                    {
                        "id": "RISK-001",
                        "title": "Data Migration Failure",
                        "description": "Risk of losing critical customer data during migration to the new CRM system",
                        "category": "Technical",
                    },
                    {
                        "id": "RISK-003",
                        "title": "Integration Issues",
                        "description": "Risk of integration issues with existing systems",
                        "category": "Technical",
                    },
                ],
                "known_drivers": ["Technical complexity", "Data quality"],
            }
        }
    )


class CorrelationTagResponse(BaseResponse):
    """Output model containing correlation tags."""

    correlation_tags: List[CorrelationTag]
    rationale: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "correlation_tags": [
                    {
                        "tag": "Technical Infrastructure",
                        "justification": "These risks are related to the technical infrastructure of the CRM system",
                        "risk_ids": ["RISK-001", "RISK-003"],
                    },
                    {
                        "tag": "Data Management",
                        "justification": "These risks are related to data management in the CRM system",
                        "risk_ids": ["RISK-001", "RISK-002"],
                    },
                ],
                "rationale": "The correlation tags were identified based on common themes across the risks.",
                "model_version": "1.0",
                "response_info": {
                    "consumed_tokens": 1300,
                    "total_cost": 0.026,
                    "prompt_name": "correlation_tags",
                    "model_name": "gpt-4",
                },
            }
        }
    )
