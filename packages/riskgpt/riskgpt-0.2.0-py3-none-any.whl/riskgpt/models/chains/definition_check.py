"""
Definition check models for RiskGPT.

This module contains models for checking and revising risk definitions.
"""

from typing import Optional

from models.base import BaseRequest, BaseResponse
from pydantic import ConfigDict, Field


class DefinitionCheckRequest(BaseRequest):
    """Input model for checking and revising a risk definition."""

    risk_title: str = Field(description="Title of the risk being checked")
    risk_description: str = Field(description="Risk description to check and revise")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "risk_title": "Resource Allocation Risk",
                "risk_description": "The project may fail due to lack of resources",
            }
        }
    )


class DefinitionCheckResponse(BaseResponse):
    """Output model for a revised risk definition."""

    revised_title: str = Field(description="Revised risk title")
    revised_description: str = Field(description="Revised risk description")
    rationale: Optional[str] = Field(
        default=None, description="Rationale for the revisions made"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "revised_title": "Insufficient Resource Availability for Project Tasks",
                "revised_description": "Resource shortages caused by inaccurate planning or unforeseen constraints threaten to delay project milestones, increase costs, or reduce quality",
                "rationale": "The original risk description was generic; it was revised to specify the event (resource shortages), identify potential causes (inaccurate planning or unforeseen constraints), and clearly state the possible impacts (delays, cost increases, quality reduction).",
            }
        }
    )
