"""
Risk models for RiskGPT.

This module contains models for risk identification and representation.
"""

from typing import List, Optional

from models.base import BaseRequest, BaseResponse
from models.common import BusinessContext
from pydantic import BaseModel, ConfigDict, Field


class Risk(BaseModel):
    """
    Representation of a single risk.

    A risk can be linked to relevant documents via document_refs field,
    which contains UUIDs of documents from the document microservice.
    """

    id: Optional[str] = Field(
        default=None, description="Unique identifier for the risk"
    )
    title: str = Field(description="Short title of the risk")
    description: str = Field(description="Detailed description of the risk")
    category: Optional[str] = Field(
        default=None, description="Category the risk belongs to"
    )
    document_refs: Optional[List[str]] = Field(
        default=None,
        description="References to document UUIDs from the document microservice",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Data Migration Failure",
                "description": "Risk of losing critical customer data during migration to the new CRM system",
                "category": "Technical",
            }
        }
    )


class RiskRequest(BaseRequest):
    """
    Input model for risk identification.

    Can include document_refs to reference relevant documents from the document microservice.
    """

    business_context: BusinessContext = Field(
        description="Business context information"
    )
    category: str = Field(description="Risk category to identify risks for")
    max_risks: Optional[int] = Field(
        default=5, description="Maximum number of risks to identify", ge=1, le=20
    )
    existing_risks: Optional[List[Risk]] = Field(
        default=None, description="List of existing risks to consider"
    )
    document_refs: Optional[List[str]] = Field(
        default=None,
        description="References to document UUIDs from the document microservice",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "business_context": {
                    "project_id": "CRM-2023",
                    "project_description": "Implementation of a new CRM system",
                    "language": "en",
                },
                "category": "Technical",
                "max_risks": 5,
                "existing_risks": ["Data migration failure"],
            }
        }
    )


class IdentifiedRisk(BaseModel):
    title: str = Field(description="Short title of the identified risk")
    description: str = Field(description="Detailed description of the identified risk")
    reference: Optional[str] = Field(
        default=None, description="Reference to the source of the risk information"
    )


class RiskResponse(BaseResponse):
    """
    Output model for identified risks.

    Can include document_refs to reference relevant documents from the document microservice.
    The legacy references field is maintained for backward compatibility.
    """

    risks: List[IdentifiedRisk]

    document_refs: Optional[List[str]] = Field(
        default=None,
        description="References to document UUIDs from the document microservice",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
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
                "references": [
                    "Industry report on CRM implementations",
                    "Internal lessons learned",
                ],
                "model_version": "1.0",
                "response_info": {
                    "consumed_tokens": 1500,
                    "total_cost": 0.03,
                    "prompt_name": "risk_identification",
                    "model_name": "gpt-4",
                },
            }
        }
    )
