"""
Mitigation models for RiskGPT.

This module contains models for risk mitigation measures.
"""

from typing import List, Optional

from models.base import BaseRequest, BaseResponse
from models.chains.drivers import RiskDriver
from models.chains.risk import Risk
from models.common import BusinessContext
from pydantic import BaseModel, ConfigDict, Field


class MitigationRequest(BaseRequest):
    """Input model for risk mitigation measures."""

    business_context: BusinessContext = Field(
        description="Business context information"
    )
    risk: Risk = Field(description="Risk information to identify mitigations for")
    risk_drivers: Optional[List[RiskDriver]] = Field(
        default=None,
        description="List of risk drivers to consider for mitigation identification",
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
                "risk_drivers": [
                    {
                        "driver": "Inadequate testing",
                        "explanation": "Insufficient testing of the CRM system may lead to undetected bugs.",
                        "influences": "both",
                    }
                ],
            }
        }
    )


class Mitigation(BaseModel):
    driver: str = Field(
        description="Short description of the risk driver related to the mitigation"
    )
    mitigation: str = Field(description="Short description of the mitigation measure")
    explanation: str = Field(
        description="Detailed explanation of how the mitigation addresses the risk"
    )
    reference: Optional[str] = Field(
        default=None, description="Reference for the mitigation measure"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "driver": "Inadequate testing",
                "mitigation": "Implement comprehensive testing strategy",
                "explanation": "A comprehensive testing strategy including unit tests, integration tests, and user acceptance testing will help identify and fix issues before deployment.",
                "reference": "https://example.com/testing-best-practices",
            }
        }
    )


class MitigationResponse(BaseResponse):
    """Output model containing mitigation measures."""

    mitigations: List[Mitigation]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "mitigations": [
                    {
                        "driver": "Inadequate testing",
                        "mitigation": "Implement comprehensive testing strategy",
                        "explanation": "A comprehensive testing strategy including unit tests, integration tests, and user acceptance testing will help identify and fix issues before deployment.",
                        "reference": "https://example.com/testing-best-practices",
                    },
                    {
                        "driver": "Lack of data backup",
                        "mitigation": "Implement automated backup system",
                        "explanation": "An automated backup system will ensure that data is regularly backed up and can be restored in case of migration issues.",
                        "reference": "https://example.com/data-backup-strategies",
                    },
                ],
                "model_version": "1.0",
                "response_info": {
                    "consumed_tokens": 1350,
                    "total_cost": 0.027,
                    "prompt_name": "risk_mitigations",
                    "model_name": "gpt-4",
                },
            }
        }
    )


class CostBenefitRequest(BaseRequest):
    """Input for cost-benefit analysis of mitigations."""

    business_context: BusinessContext = Field(
        description="Business context information"
    )
    risk_title: str = Field(description="Title of the risk to analyze mitigations for")
    risk_description: str = Field(
        description="Risk description to analyze mitigations for"
    )
    mitigations: List[str] = Field(description="List of mitigation measures to analyze")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "business_context": {
                    "project_id": "CRM-2023",
                    "project_description": "Implementation of a new CRM system",
                },
                "risk_title": "Data Migration Failure",
                "risk_description": "Risk of losing critical customer data during migration to the new CRM system",
                "mitigations": [
                    "Implement comprehensive testing strategy",
                    "Implement automated backup system",
                ],
            }
        }
    )


class CostBenefit(BaseModel):
    """Model for cost-benefit analysis of a single mitigation measure."""

    mitigation: str = Field(description="Mitigation measure being analyzed")
    cost: Optional[str] = Field(
        default=None, description="Cost estimate for the mitigation"
    )
    benefit: Optional[str] = Field(
        default=None, description="Benefit estimate for the mitigation"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "mitigation": "Implement comprehensive testing strategy",
                "cost": "Medium - Requires additional resources and time",
                "benefit": "High - Significantly reduces the risk of data loss during migration",
            }
        }
    )


class CostBenefitResponse(BaseResponse):
    """Output model containing cost-benefit analyses."""

    analyses: List[CostBenefit] = Field(
        description="List of cost-benefit analyses for mitigation measures"
    )
    references: Optional[List[str]] = Field(
        default=None, description="References used for the analyses"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "analyses": [
                    {
                        "mitigation": "Implement comprehensive testing strategy",
                        "cost": "Medium - Requires additional resources and time",
                        "benefit": "High - Significantly reduces the risk of data loss during migration",
                    },
                    {
                        "mitigation": "Implement automated backup system",
                        "cost": "Low - Can be implemented with existing resources",
                        "benefit": "High - Ensures data can be recovered in case of migration issues",
                    },
                ],
                "references": [
                    "Industry best practices for CRM implementations",
                    "Internal cost-benefit analysis guidelines",
                ],
                "model_version": "1.0",
                "response_info": {
                    "consumed_tokens": 1400,
                    "total_cost": 0.028,
                    "prompt_name": "get_cost_benefit",
                    "model_name": "gpt-4",
                },
            }
        }
    )
