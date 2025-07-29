from __future__ import annotations

from typing import Annotated, List, TypedDict, TypeVar

from chains.keypoint_text import keypoint_text_chain
from helpers.extraction import extract_key_points
from helpers.search import search, settings
from langgraph.graph import END, StateGraph, add_messages
from models.base import ResponseInfo
from models.enums import TopicEnum
from models.utils.search import SearchRequest, SearchResponse, Source
from models.workflows.context import (
    EnrichContextRequest,
    EnrichContextResponse,
    ExtractKeyPointsRequest,
    ExtractKeyPointsResponse,
    KeyPoint,
    KeyPointTextRequest,
    KeyPointTextResponse,
)

# Define reducer functions for lists
T = TypeVar("T")


def extend_list(existing: List[T] | None, new: List[T]) -> List[T]:
    """Combine two lists by extending the existing list with the new one."""
    if existing is None:
        return new
    return existing + new


def append_to_list(existing: List[T] | None, new: T) -> List[T]:
    """Append a single item to a list."""
    if existing is None:
        return [new]
    return existing + [new]


class State(TypedDict):
    messages: Annotated[list, add_messages]

    sources: Annotated[List[Source], extend_list]
    key_points: Annotated[List[KeyPoint], extend_list]
    response_info_list: Annotated[List[ResponseInfo], extend_list]

    search_failed: bool
    keypoint_text_response: KeyPointTextResponse
    response: EnrichContextResponse


def topic_search(
    state: State,
    request: EnrichContextRequest,
    topic: TopicEnum,
    max_results: int | None = None,
) -> State:
    if max_results is None:
        max_results = settings.MAX_SEARCH_RESULTS

    query = request.create_search_query()
    search_request = SearchRequest(
        query=query,
        source_type=topic.value,
        max_results=max_results,
    )
    search_response: SearchResponse = search(search_request)

    sources: List[Source] = state.get("sources", [])
    existing_urls = {source.url for source in sources}

    # Convert SearchResult objects to Source objects
    new_sources = [
        Source.from_search_result(item, topic)
        for item in search_response.results
        if item.url not in existing_urls
    ]

    state["sources"] = new_sources

    if not search_response.success:
        state["search_failed"] = True
    return state


async def extract_topic_key_points(state: State, topic: TopicEnum) -> State:
    # Filter sources by topic
    sources: List[Source] = state.get("sources", [])
    topic_sources = [source for source in sources if source.topic == topic]

    for source in topic_sources:
        request = ExtractKeyPointsRequest.from_source(source)
        response: ExtractKeyPointsResponse = await extract_key_points(request)

        # Attach source.url to each point in response.points
        for point in response.points:
            point.source_url = source.url

        state.setdefault("response_info_list", []).append(response.response_info)
        state.setdefault("key_points", []).extend(response.points)

    return state


def aggregate_response_info(state):
    total_tokens = 0
    total_cost = 0.0
    model_name = ""
    response_info_list = state.get("response_info_list", [])
    if response_info_list:
        total_cost = sum(info.total_cost for info in response_info_list)
        total_tokens = sum(info.consumed_tokens for info in response_info_list)
        model_name = response_info_list[-1].model_name
    return ResponseInfo(
        consumed_tokens=total_tokens,
        total_cost=total_cost,
        prompt_name="external_context_enrichment",
        model_name=model_name,
    )


def get_enrich_context_graph(request: EnrichContextRequest):
    """
    Returns the uncompiled graph for visualization purposes.

    This method can be used in Jupyter notebooks to visualize the graph structure.

    Example:
        ```python
        from IPython.display import Image, display
        from src.workflows.enrich_context import get_enrich_context_graph
        from src.models.workflows.context import ExternalContextRequest
        from src.models.common import BusinessContext

        # Create a request
        request = ExternalContextRequest(
            business_context=BusinessContext(
                project_id="Sample Project",
                project_description="A sample project for visualization",
                domain_knowledge="sample domain",
            ),
            focus_keywords=["sample", "keywords"],
        )

        # Get the graph
        graph = get_enrich_context_graph(request)

        # Visualize the graph
        try:
            display(Image(graph.get_graph().draw_mermaid_png()))
        except Exception as e:
            print(f"Could not visualize graph: {e}")
            print("Make sure you have graphviz installed.")
        ```
    """
    graph = StateGraph(State)

    def news_search(state: State) -> State:
        return topic_search(state, request, TopicEnum.NEWS)

    def professional_search(state: State) -> State:
        return topic_search(state, request, TopicEnum.LINKEDIN)

    def regulatory_search(state: State) -> State:
        return topic_search(state, request, TopicEnum.REGULATORY)

    async def extract_news_key_points(state: State) -> State:
        return await extract_topic_key_points(state, TopicEnum.NEWS)

    async def extract_professional_key_points(state: State) -> State:
        return await extract_topic_key_points(state, TopicEnum.LINKEDIN)

    async def extract_regulatory_key_points(state: State) -> State:
        return await extract_topic_key_points(state, TopicEnum.REGULATORY)

    async def summarize_key_points(state: State) -> State:
        """Summarize key points for a specific topic."""

        kp_text_request = KeyPointTextRequest(key_points=state.get("key_points", []))
        response: KeyPointTextResponse = await keypoint_text_chain(kp_text_request)

        state["keypoint_text_response"] = response

        if response.response_info:
            state.setdefault("response_info_list", []).append(response.response_info)
        return state

    async def aggregate(state: State) -> State:
        sources: List[Source] = state.get("sources", [])

        if not sources:
            if state.get("search_failed"):
                summary = "No external data retrieved due to network restrictions or missing dependencies"
            else:
                summary = "No recent relevant information found"
            full_report = None
            recommendation = None
        else:
            summary = f"Collected {len(sources)} external sources for {request.business_context.project_id}."

            kp_text_response = state.get("keypoint_text_response")
            full_report = kp_text_response.format_output() if kp_text_response else None

            sorted_sources = sorted(sources, key=lambda s: s.score, reverse=True)
            recommendation = [
                f"Review source: {s.title} ({s.url})" for s in sorted_sources[:2]
            ]

        response = EnrichContextResponse(
            sector_summary=summary,
            workshop_recommendations=recommendation if recommendation else [],
            full_report=full_report,
        )
        response.response_info = aggregate_response_info(state)

        state["response"] = response
        return state

    # Define a start node that will be the entry point
    def start(state: State) -> State:
        # Initialize state if needed
        return state

    # Add nodes to the graph
    graph.add_node("start", start)
    graph.add_node("news", news_search)
    graph.add_node("professional", professional_search)
    graph.add_node("regulatory", regulatory_search)
    graph.add_node("extract_news_key_points", extract_news_key_points)
    graph.add_node("extract_professional_key_points", extract_professional_key_points)
    graph.add_node("extract_regulatory_key_points", extract_regulatory_key_points)
    graph.add_node("aggregate", aggregate)
    graph.add_node("summarize_key_points", summarize_key_points)

    # Set up the graph with parallel processing
    graph.set_entry_point("start")

    # Branch from start to all three search operations
    graph.add_edge("start", "news")
    graph.add_edge("start", "professional")
    graph.add_edge("start", "regulatory")

    # After each search, extract key points from that source type
    graph.add_edge("news", "extract_news_key_points")
    graph.add_edge("professional", "extract_professional_key_points")
    graph.add_edge("regulatory", "extract_regulatory_key_points")

    # Join all extraction results to summarize key points
    graph.add_edge("extract_news_key_points", "summarize_key_points")
    graph.add_edge("extract_professional_key_points", "summarize_key_points")
    graph.add_edge("extract_regulatory_key_points", "summarize_key_points")

    # Final steps
    graph.add_edge("summarize_key_points", "aggregate")
    graph.add_edge("aggregate", END)

    return graph


def _build_graph(request: EnrichContextRequest):
    return get_enrich_context_graph(request).compile()


async def enrich_context(
    request: EnrichContextRequest,
) -> EnrichContextResponse:
    """Run the external context enrichment workflow asynchronously."""

    app = _build_graph(request)
    result = await app.ainvoke({})
    return result["response"]
