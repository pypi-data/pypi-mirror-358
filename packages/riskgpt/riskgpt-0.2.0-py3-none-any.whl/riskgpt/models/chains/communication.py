"""
Communication models for RiskGPT.

This module contains models for the communicate_risks chain.
"""

from typing import List, Optional

from models.base import BaseRequest, BaseResponse
from models.chains.risk import Risk
from models.common import BusinessContext
from models.enums import AudienceEnum
from pydantic import ConfigDict, Field


class CommunicationRequest(BaseRequest):
    """Input for summarising risks for stakeholders."""

    business_context: BusinessContext
    audience: AudienceEnum = Field(
        default=AudienceEnum.executive,
        description="Target audience for the communication",
    )
    risks: List[Risk]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "business_context": {
                    "project_id": "CRM-2023",
                    "project_description": "Implementation of a new CRM system",
                },
                "audience": "executive",
                "risks": [
                    {
                        "title": "Data Migration Failure",
                        "description": "Risk of losing critical customer data during migration to the new CRM system",
                        "category": "Technical",
                    },
                    {
                        "title": "User Adoption Issues",
                        "description": "Risk of low user adoption due to resistance to change",
                        "category": "Organizational",
                    },
                ],
            }
        }
    )


class CommunicationResponse(BaseResponse):
    """Output model for risk communication."""

    summary: str = Field(description="Audience-specific summary of risks")
    key_points: List[str] = Field(
        default_factory=list, description="Key points for communication"
    )
    technical_annex: Optional[str] = Field(
        default=None, description="Technical details for analysts"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "summary": "The CRM implementation project faces two significant risks: potential data loss during migration and user adoption challenges. These risks could impact project success and should be addressed with appropriate mitigation strategies.",
                "key_points": [
                    "Data migration presents technical challenges that could result in data loss",
                    "User adoption may be hindered by resistance to change",
                    "Mitigation strategies should focus on testing and change management",
                ],
                "technical_annex": "Detailed technical analysis of the data migration process and potential failure points...",
                "model_version": "1.0",
                "response_info": {
                    "consumed_tokens": 1350,
                    "total_cost": 0.027,
                    "prompt_name": "communicate_risks",
                    "model_name": "gpt-4",
                },
            }
        }
    )
