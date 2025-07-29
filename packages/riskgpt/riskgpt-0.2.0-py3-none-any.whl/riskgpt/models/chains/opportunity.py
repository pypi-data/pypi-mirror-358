"""
Opportunity models for RiskGPT.

This module contains models for identifying opportunities from risks.
"""

from typing import List, Optional

from models.base import BaseRequest, BaseResponse
from models.chains.risk import Risk
from models.common import BusinessContext
from pydantic import BaseModel, ConfigDict, Field


class OpportunityRequest(BaseRequest):
    """Input for identifying opportunities."""

    business_context: BusinessContext = Field(
        description="Business context information"
    )
    risk: Risk = Field(description="Risk for which opportunities are to be identified")

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


class Opportunity(BaseModel):
    opportunity: str = Field(description="Description of the identified opportunity")
    explanation: str = Field(
        description="Explanation of how this opportunity relates to the risk"
    )
    category: Optional[str] = Field(
        default=None, description="Category of the opportunity, if applicable"
    )
    reference: Optional[str] = Field(
        default=None, description="Reference or source for the opportunity"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "opportunity": "Implement data quality improvement process",
                "explanation": "The risk of data migration failure presents an opportunity to implement a comprehensive data quality improvement process that will benefit the organization beyond the CRM implementation.",
                "category": "Process Improvement",
                "reference": "Industry best practices for data management",
            }
        }
    )


class OpportunityResponse(BaseResponse):
    """Output model containing identified opportunities."""

    opportunities: List[Opportunity]
