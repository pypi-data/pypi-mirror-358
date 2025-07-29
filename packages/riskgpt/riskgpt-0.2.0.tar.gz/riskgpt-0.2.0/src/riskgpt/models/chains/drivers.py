"""
Driver models for RiskGPT.

This module contains models for risk driver identification.
"""

from typing import List, Literal, Optional

from models.base import BaseRequest, BaseResponse
from models.chains.risk import Risk
from models.common import BusinessContext
from pydantic import BaseModel, ConfigDict, Field


class DriverRequest(BaseRequest):
    """Input model for risk driver identification."""

    business_context: BusinessContext = Field(
        description="Business context information"
    )
    risk: Risk = Field(
        description="Risk information including title and description",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "business_context": {
                    "project_id": "CRM-2023",
                    "project_description": "Implementation of a new CRM system",
                    "language": "en",
                },
                "risk_description": "There is a 30% probability that the CRM implementation will experience critical technical failures within the first 3 months of deployment.",
            }
        }
    )


class RiskDriver(BaseModel):
    driver: str = Field(description="Short description of the risk driver")
    explanation: str = Field(description="Detailed explanation of the risk driver")
    influences: Literal["likelihood", "impact", "both"] = Field(
        description="How the driver influences the risk: likelihood, impact, or both"
    )
    reference: Optional[str] = Field(
        default=None, description="Reference for the risk driver"
    )


class DriverResponse(BaseResponse):
    """Output model containing risk drivers."""

    drivers: List[RiskDriver]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "drivers": [
                    {
                        "driver": "Inadequate testing",
                        "explanation": "Insufficient testing of the CRM system may lead to undetected bugs.",
                        "influences": "both",
                        "reference": "https://example.com/testing-guidelines",
                    },
                    {
                        "driver": "Lack of user training",
                        "explanation": "Users not trained properly may misuse the CRM system, leading to errors.",
                        "influences": "likelihood",
                    },
                ]
            }
        }
    )
