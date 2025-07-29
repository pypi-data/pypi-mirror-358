"""
Presentation models for RiskGPT.

This module contains models for presentation-oriented risk summaries.
"""

from typing import List, Optional

from models.base import BaseRequest, BaseResponse
from models.common import BusinessContext
from models.enums import AudienceEnum
from pydantic import Field


class PresentationRequest(BaseRequest):
    """Input model for presentation-oriented summaries."""

    business_context: BusinessContext = Field(
        description="Business context information"
    )
    audience: AudienceEnum = Field(description="Target audience for the presentation")
    focus_areas: Optional[List[str]] = Field(
        default=None, description="Specific areas to focus on in the presentation"
    )


class PresentationResponse(BaseResponse):
    """Structured output for presentation-ready summaries."""

    executive_summary: str = Field(
        description="High-level summary for executive audience"
    )
    main_risks: List[str] = Field(description="List of main risks to highlight")
    quantitative_summary: Optional[str] = Field(
        default=None, description="Summary of quantitative risk assessments"
    )
    key_drivers: Optional[List[str]] = Field(
        default=None, description="Key risk drivers to highlight"
    )
    correlation_tags: Optional[List[str]] = Field(
        default=None, description="Tags indicating correlations between risks"
    )
    mitigations: Optional[List[str]] = Field(
        default=None, description="Key mitigation measures to highlight"
    )
    open_questions: Optional[List[str]] = Field(
        default=None, description="Open questions requiring further investigation"
    )
    chart_placeholders: Optional[List[str]] = Field(
        default=None, description="Suggestions for charts to include"
    )
    appendix: Optional[str] = Field(
        default=None, description="Additional technical details for appendix"
    )
