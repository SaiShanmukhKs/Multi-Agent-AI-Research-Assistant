"""
LangGraph state definition for the Multi-Agent Research Assistant.

The ResearchState is the shared data structure that flows through the entire
agent pipeline. Each agent reads from and writes to this state.
"""

from __future__ import annotations

import operator
from typing import Annotated, TypedDict


def _merge_lists(left: list, right: list) -> list:
    """Reducer that appends new items to an existing list (no duplicates by URL)."""
    seen_urls = {item.get("url") for item in left if isinstance(item, dict) and "url" in item}
    merged = list(left)
    for item in right:
        if isinstance(item, dict) and "url" in item:
            if item["url"] not in seen_urls:
                merged.append(item)
                seen_urls.add(item["url"])
        else:
            merged.append(item)
    return merged


class ResearchState(TypedDict):
    """Shared state object passed between all agents in the LangGraph pipeline."""

    # ── User Input ──
    query: str                                                  # Original user query
    audience: str                                               # Report audience: academic / business / casual

    # ── Search Agent outputs ──
    sub_queries: list[str]                                      # Generated sub-questions
    search_results: Annotated[list[dict], _merge_lists]         # Ranked search results (URL, title, snippet, score)

    # ── Reader Agent outputs ──
    extracted_content: Annotated[list[dict], _merge_lists]      # Parsed document content with source info
    vector_store_id: str                                        # ChromaDB collection name for this session

    # ── Synthesis Agent outputs ──
    synthesis: dict                                             # Structured analysis (themes, insights, evidence)
    gaps_identified: list[str]                                  # Knowledge gaps for re-search

    # ── Writer Agent output ──
    report: str                                                 # Final Markdown report
    report_html: str                                            # HTML version of the report
    visual_data: list[dict]                                     # Data for charts/visuals in the report

    # ── Orchestrator metadata ──
    iteration_count: int                                        # Loop counter (prevent infinite loops)
    status: str                                                 # Current pipeline status
    agent_logs: Annotated[list[str], operator.add]              # Append-only log of agent actions
