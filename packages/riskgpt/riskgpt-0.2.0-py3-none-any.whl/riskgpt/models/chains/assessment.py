"""
Assessment models for RiskGPT.

This module contains models for risk assessment.
"""

from typing import List, Optional

from models.base import BaseRequest, BaseResponse
from models.common import BusinessContext, Dist
from pydantic import BaseModel, ConfigDict, Field


class AssessmentRequest(BaseRequest):
    """
    Input model for assessing a risk's impact.

    Can include document_refs to reference relevant documents from the document microservice.
    """

    business_context: BusinessContext = Field(
        description="Business context information"
    )
    risk_title: str = Field(
        description="Title of the risk being assessed",
    )
    risk_description: str = Field(description="Risk description to assess")
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
                },
                "risk_title": "CRM Implementation Failure",
                "risk_description": "There is a 30% probability that the CRM implementation will experience critical technical failures within the first 3 months of deployment.",
            }
        }
    )


class QuantitativeAssessment(BaseModel):
    """Nested model for quantitative risk assessment."""

    minimum: Optional[float] = Field(
        default=None, description="Minimum value of the risk assessment"
    )
    most_likely: Optional[float] = Field(
        default=None, description="Most likely value of the risk assessment"
    )
    maximum: Optional[float] = Field(
        default=None, description="Maximum value of the risk assessment"
    )
    distribution: Optional[str] = Field(
        default=None, description="Distribution type (e.g., normal, triangular)"
    )
    distribution_fit: Optional[Dist] = Field(
        default=None, description="Fitted distribution parameters"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "minimum": 50000.0,
                "most_likely": 100000.0,
                "maximum": 200000.0,
                "distribution": "triangular",
                "distribution_fit": {
                    "name": "triangular",
                    "parameters": {"min": 50000.0, "mode": 100000.0, "max": 200000.0},
                },
            }
        }
    )


class AssessmentResponse(BaseResponse):
    """
    Output model for a risk impact assessment.

    Can include document_refs to reference relevant documents from the document microservice.
    The legacy references field is maintained for backward compatibility.
    """

    quantitative: Optional[QuantitativeAssessment] = Field(
        default=None, description="Quantitative assessment details"
    )
    impact: Optional[float] = Field(
        default=None, description="Impact score (0-1 or monetary value)"
    )
    probability: Optional[float] = Field(
        default=None, description="Probability score (0-1)"
    )
    evidence: Optional[str] = Field(
        default=None, description="Evidence supporting the assessment"
    )
    references: Optional[List[str]] = Field(
        default=None, description="References used for the assessment"
    )
    document_refs: Optional[List[str]] = Field(
        default=None,
        description="References to document UUIDs from the document microservice",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "quantitative": {
                    "minimum": 50000.0,
                    "most_likely": 100000.0,
                    "maximum": 200000.0,
                    "distribution": "triangular",
                },
                "impact": 0.7,
                "probability": 0.3,
                "evidence": "Based on historical data from similar CRM implementations",
                "references": [
                    "Industry report on CRM implementations",
                    "Internal lessons learned",
                ],
                "model_version": "1.0",
                "response_info": {
                    "consumed_tokens": 1400,
                    "total_cost": 0.028,
                    "prompt_name": "risk_assessment",
                    "model_name": "gpt-4",
                },
            }
        }
    )
