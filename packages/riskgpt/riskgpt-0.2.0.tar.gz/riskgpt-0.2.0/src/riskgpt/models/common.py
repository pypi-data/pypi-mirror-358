"""
Common models for RiskGPT.

This module contains common models used across multiple chains in the RiskGPT system.
"""

from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class BusinessContext(BaseModel):
    """Standardized schema for business context information."""

    project_id: str = Field(
        description="Unique identifier for the project",
        examples=["PRJ-2023-001", "CRM-ROLLOUT-Q1"],
    )
    project_description: Optional[str] = Field(
        default=None,
        description="Detailed description of the project",
        examples=[
            "Implementation of a new CRM system",
            "Migration to cloud infrastructure",
        ],
    )
    domain_knowledge: Optional[str] = Field(
        default=None,
        description="Specific domain knowledge relevant to the project",
        examples=[
            "The company operates in the B2B sector",
            "Previous attempts at similar projects failed due to...",
        ],
    )
    business_area: Optional[str] = Field(
        default=None,
        description="Business area or department the project belongs to",
        examples=["Sales", "Marketing", "IT", "Finance"],
    )
    industry_sector: Optional[str] = Field(
        default=None,
        description="Industry sector the project operates in",
        examples=["Healthcare", "Finance", "Manufacturing", "Retail"],
    )
    document_refs: Optional[List[str]] = Field(
        default=None,
        description="References to document UUIDs from the document microservice",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "project_id": "CRM-2023",
                "project_description": "Implementation of a new CRM system",
                "domain_knowledge": "The company operates in the B2B sector",
                "business_area": "Sales",
                "industry_sector": "Technology",
                "document_refs": ["doc-uuid-1", "doc-uuid-2"],
            }
        }
    )

    def get_domain_section(self) -> str:
        """Return formatted domain knowledge section if available."""
        return (
            f"Domain knowledge: {self.domain_knowledge}"
            if self.domain_knowledge
            else ""
        )


class Dist(BaseModel):
    """Generic distribution model."""

    name: str = Field(description="Name of the distribution")
    parameters: Optional[Dict[str, float]] = Field(
        default=None, description="Parameters of the distribution"
    )
    source: Optional[str] = Field(
        default=None, description="Source of the distribution"
    )
    correlation_tag: Optional[str] = Field(
        default=None, description="Tag for correlation analysis"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "normal",
                "parameters": {"mean": 100.0, "std": 10.0},
                "source": "historical data",
                "correlation_tag": "market_volatility",
            }
        }
    )


class Prompt(BaseModel):
    """Model for prompt templates."""

    version: str
    description: str
    template: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "version": "1.0",
                "description": "Template for generating risk assessments",
                "template": "Given the following business context: {business_context}, assess the risk: {risk_description}",
            }
        }
    )
