"""
Agent 1: Web Search Agent (The Scout) 🔍

Breaks the user's research query into targeted sub-queries and searches
the web for each in parallel. Returns ranked, deduplicated results.
"""

from __future__ import annotations

import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from langchain_core.messages import HumanMessage, SystemMessage

from core.llm import get_llm
from core.state import ResearchState
from tools import web_search

logger = logging.getLogger(__name__)

DECOMPOSITION_PROMPT = """You are a research query decomposition expert.

Given a research topic, generate {n} targeted sub-queries that will help
find comprehensive, up-to-date information on the topic.

Rules:
- Each sub-query should target a DIFFERENT aspect of the topic
- Include time-relevant keywords (e.g., "2025", "2026", "latest", "recent")
- Include specific entity names when relevant (companies, researchers, etc.)
- Mix broad overview queries with specific technical queries
- Make queries search-engine-friendly (not questions, but keyword-rich phrases)

Return your response as a JSON array of strings. Example:
["sub query 1", "sub query 2", "sub query 3"]

IMPORTANT: Return ONLY the JSON array, no other text.
"""


def run_search_agent(state: ResearchState) -> dict:
    """
    Execute the Web Search Agent.

    1. Uses Gemini to decompose the query into sub-queries
    2. Searches the web for sub-queries in parallel
    3. Deduplicates and ranks results

    Args:
        state: Current LangGraph state.

    Returns:
        State update dict with sub_queries, search_results, status, and agent_logs.
    """
    query = state["query"]
    existing_sub_queries = state.get("sub_queries", [])
    gaps = state.get("gaps_identified", [])

    logger.info(f"🔍 Search Agent activated for: {query}")

    # If we have gaps from the Synthesis Agent, search those instead
    if gaps and state.get("iteration_count", 0) > 0:
        sub_queries = gaps
        logger.info(f"  Searching {len(sub_queries)} gap-filling queries")
    elif existing_sub_queries and state.get("iteration_count", 0) > 0:
        # Already have sub-queries from a previous run, skip decomposition
        sub_queries = existing_sub_queries
    else:
        # Fresh run: decompose the query
        sub_queries = _decompose_query(query)

    # Search the web for all sub-queries IN PARALLEL for maximum speed
    all_results = []
    with ThreadPoolExecutor(max_workers=min(5, len(sub_queries))) as executor:
        future_to_sq = {executor.submit(web_search.search, sq): sq for sq in sub_queries}
        for future in as_completed(future_to_sq):
            try:
                results = future.result()
                all_results.extend(results)
            except Exception as e:
                logger.warning(f"Failed web search for a sub-query: {e}")

    # Deduplicate by URL
    seen_urls = set()
    unique_results = []
    for r in all_results:
        if r["url"] not in seen_urls:
            seen_urls.add(r["url"])
            unique_results.append(r)

    # Sort by relevance score (descending)
    unique_results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)

    log_msg = (
        f"🔍 Search Agent: Generated {len(sub_queries)} sub-queries, "
        f"found {len(unique_results)} unique results"
    )
    logger.info(log_msg)

    return {
        "sub_queries": sub_queries,
        "search_results": unique_results,
        "status": "search_complete",
        "agent_logs": [log_msg],
    }


def _decompose_query(query: str) -> list[str]:
    """Use Gemini to break a research query into targeted sub-queries."""
    llm = get_llm(temperature=0.4)

    messages = [
        SystemMessage(content=DECOMPOSITION_PROMPT.format(n=5)),
        HumanMessage(content=f"Research topic: {query}"),
    ]

    try:
        response = llm.invoke(messages)
        raw_content = response.content
        if isinstance(raw_content, list):
            content = "".join([str(item.get("text", item)) if isinstance(item, dict) else str(item) for item in raw_content]).strip()
        else:
            content = str(raw_content).strip()

        # Clean up potential markdown code block wrapping
        if content.startswith("```"):
            content = content.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

        sub_queries = json.loads(content)
        if isinstance(sub_queries, list) and all(isinstance(q, str) for q in sub_queries):
            return sub_queries[:5]
    except (json.JSONDecodeError, Exception) as e:
        logger.warning(f"Failed to parse sub-queries: {e}")

    # Fallback: simple keyword variations
    return [
        f"{query} latest developments 2025 2026",
        f"{query} research breakthroughs",
        f"{query} key challenges and solutions",
        f"{query} industry applications",
        f"{query} future outlook predictions",
    ]
