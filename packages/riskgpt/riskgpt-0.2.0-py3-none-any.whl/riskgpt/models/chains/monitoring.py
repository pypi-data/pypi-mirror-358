"""
Monitoring models for RiskGPT.

This module contains models for deriving monitoring indicators for risks.
"""

from typing import List, Literal, Optional

from models.base import BaseRequest, BaseResponse
from models.chains.risk import Risk
from models.common import BusinessContext
from pydantic import BaseModel, ConfigDict, Field


class RiskIndicatorRequest(BaseRequest):
    """Input for deriving monitoring indicators."""

    business_context: BusinessContext = Field(
        description="Business context information"
    )
    risk: Risk = Field(
        description="Risk information for which monitoring indicators are derived"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "business_context": {
                    "project_id": "CRM-2023",
                    "project_description": "Implementation of a new CRM system",
                },
                "risk": {
                    "title": "Data Migration Failure",
                    "description": "Risk of losing critical customer data during migration to the new CRM system",
                    "category": "Technical",
                },
            }
        }
    )


class RiskIndicator(BaseModel):
    indicator: str = Field(description="Name of the monitoring indicator")
    type: Literal["leading", "lagging", "both"] = Field(
        description="Type of the indicator, whether it is leading, lagging, or both"
    )
    explanation: str = Field(
        description="Explanation of the indicator and its relevance to the risk"
    )
    action: Optional[str] = Field(
        default=None, description="Recommended action based on the indicator"
    )
    reference: Optional[str] = Field(
        default=None, description="Reference for the indicator, if applicable"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "indicator": "Data integrity check failure rate",
                "type": "leading",
                "explanation": "Monitors the rate of data integrity check failures during test migrations, which can predict potential issues in the final migration.",
                "action": "If failure rate exceeds 5%, pause migration and investigate data integrity issues.",
                "reference": "Industry standard for CRM data migration",
            }
        }
    )


class RiskIndicatorResponse(BaseResponse):
    """Output model containing monitoring indicators."""

    indicators: List[RiskIndicator]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "indicators": [
                    {
                        "indicator": "Data integrity check failure rate",
                        "type": "leading",
                        "explanation": "Monitors the rate of data integrity check failures during test migrations, which can predict potential issues in the final migration.",
                        "action": "If failure rate exceeds 5%, pause migration and investigate data integrity issues.",
                        "reference": "Industry standard for CRM data migration",
                    },
                    {
                        "indicator": "Data loss incidents",
                        "type": "lagging",
                        "explanation": "Tracks actual incidents of data loss during the migration process.",
                        "action": "If any data loss is detected, immediately restore from backup and review migration process.",
                        "reference": "Company data security policy",
                    },
                ],
                "model_version": "1.0",
                "response_info": {
                    "consumed_tokens": 1250,
                    "total_cost": 0.025,
                    "prompt_name": "get_monitoring_indicators",
                    "model_name": "gpt-4",
                },
            }
        }
    )
