from typing import List, Optional

from models.base import BaseResponse
from models.common import BusinessContext
from models.enums import TopicEnum
from models.utils.search import Source
from pydantic import BaseModel


class KeyPoint(BaseModel):
    """Model for a key point extracted from a source."""

    content: str
    topic: TopicEnum
    source_url: Optional[str] = None


class ExtractKeyPointsRequest(BaseModel):
    """Input model for extracting key points from a source."""

    source_type: str
    content: str

    @classmethod
    def from_source(cls, source: Source) -> "ExtractKeyPointsRequest":
        """Create an ExtractKeyPointsRequest from a Source object."""
        return ExtractKeyPointsRequest(
            source_type=source.type,
            content=f"Title: {source.title}\n\nContent: {source.content}",
        )

    class Config:
        schema_extra = {
            "example": {
                "source_type": "NEWS",
                "content": "This is an example content from a news article.",
            }
        }


class ExtractKeyPointsResponse(BaseResponse):
    """Model for key points extracted from a source."""

    points: List[KeyPoint] = []

    class Config:
        schema_extra = {
            "example": {
                "points": [
                    {
                        "content": "Key point 1",
                        "topic": "NEWS",
                        "source_url": "https://example.com",
                    },
                    {
                        "content": "Key point 2",
                        "topic": "NEWS",
                        "source_url": "https://example.com",
                    },
                    {
                        "content": "Key point 3",
                        "topic": "NEWS",
                        "source_url": "https://example.com",
                    },
                ],
                "response_info": {"token_usage": 100, "cost": 0.01},
            }
        }


class EnrichContextRequest(BaseModel):
    """Input model for external context enrichment."""

    business_context: BusinessContext
    focus_keywords: Optional[List[str]] = None
    time_horizon_months: Optional[int] = 12

    def create_search_query(self) -> str:
        """Create a search query based on the business context and focus keywords."""
        keywords = " ".join(self.focus_keywords) if self.focus_keywords else ""
        return f"{self.business_context.project_description} {keywords}".strip()


class EnrichContextResponse(BaseResponse):
    """Output model containing summarised external information."""

    sector_summary: str
    workshop_recommendations: List[str]
    full_report: Optional[str] = None


class KeyPointTextRequest(BaseModel):
    """Request model for generating text from key points."""

    key_points: List[KeyPoint]


class KeyPointTextResponse(BaseResponse):
    """Output model containing text generated from key points with Harvard-style citations."""

    text: str
    references: List[str]

    def format_output(self) -> str:
        """Format the output text with references."""
        formatted_references = "\n".join(self.references)
        return f"{self.text}\n\nReferences:\n{formatted_references}"
