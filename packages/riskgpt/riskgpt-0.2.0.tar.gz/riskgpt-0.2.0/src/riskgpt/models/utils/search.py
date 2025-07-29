from models.enums import TopicEnum
from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    title: str = Field(default="", description="Title of the search result")
    url: str = Field(default="", description="URL of the search result")
    date: str = Field(default="", description="Date of the search result, if available")
    type: str = Field(
        default="",
        description="Type of the source (e.g., news, professional, regulatory, peer)",
    )
    content: str = Field(
        default="", description="Brief content or snippet from the source"
    )
    score: float = Field(
        default=0.0, description="Relevance score of the search result, if applicable"
    )


class Source(SearchResult):
    """Source class that extends SearchResult with topic information."""

    topic: TopicEnum

    @classmethod
    def from_search_result(
        cls, search_result: SearchResult, topic: TopicEnum
    ) -> "Source":
        """Create a Source from a SearchResult and a topic."""
        return cls(
            title=search_result.title,
            url=search_result.url,
            date=search_result.date,
            type=search_result.type,
            content=search_result.content,
            topic=topic,
        )


class SearchRequest(BaseModel):
    """Request model for search queries."""

    query: str = Field(description="Search query string")
    source_type: str = Field(
        default="",
        description="Type of source to search (e.g., news, professional, regulatory, peer)",
    )
    max_results: int = Field(
        default=3, ge=1, le=100, description="Maximum number of results to return"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "latest developments in AI regulation",
                "source_type": "news",
            }
        }
    }


class SearchResponse(BaseModel):
    """Response model for search results."""

    results: list[SearchResult] = Field(
        default_factory=list, description="List of search results"
    )
    success: bool = Field(
        default=True, description="Indicates if the search was successful"
    )
    error_message: str = Field(
        default="", description="Error message if the search failed"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "results": [
                    {
                        "title": "Example Title",
                        "url": "https://example.com",
                        "date": "2023-10-01",
                        "type": "news",
                        "content": "This is an example content.",
                    }
                ],
                "success": True,
                "error_message": "",
            }
        }
    }
