"""
Web Search Tool — Tavily (primary) + DuckDuckGo (fallback).

Provides a unified search interface that automatically selects the best
available search provider based on configured API keys.
"""

from __future__ import annotations

import logging

import config

logger = logging.getLogger(__name__)


def search(query: str, max_results: int | None = None) -> list[dict]:
    """
    Execute a web search and return structured results.

    Args:
        query: The search query string.
        max_results: Override the default max results per query.

    Returns:
        List of dicts, each with keys: url, title, snippet, relevance_score
    """
    n = max_results or config.MAX_SEARCH_RESULTS
    if config.USE_TAVILY:
        return _search_tavily(query, n)
    return _search_duckduckgo(query, n)


def _search_tavily(query: str, max_results: int) -> list[dict]:
    """Search using the Tavily API (purpose-built for AI agents)."""
    try:
        from tavily import TavilyClient

        client = TavilyClient(api_key=config.TAVILY_API_KEY)
        response = client.search(
            query=query,
            max_results=max_results,
            search_depth="basic",
            include_answer=False,
        )
        results = []
        for item in response.get("results", []):
            results.append({
                "url": item.get("url", ""),
                "title": item.get("title", ""),
                "snippet": item.get("content", ""),
                "relevance_score": item.get("score", 0.5),
            })
        logger.info(f"Tavily returned {len(results)} results for: {query}")
        return results
    except Exception as e:
        logger.warning(f"Tavily search failed: {e}. Falling back to DuckDuckGo.")
        return _search_duckduckgo(query, max_results)


def _search_duckduckgo(query: str, max_results: int) -> list[dict]:
    """Search using DuckDuckGo (free, no API key required)."""
    try:
        from duckduckgo_search import DDGS

        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "url": r.get("href", ""),
                    "title": r.get("title", ""),
                    "snippet": r.get("body", ""),
                    "relevance_score": 0.5,  # DDG doesn't provide relevance scores
                })
        logger.info(f"DuckDuckGo returned {len(results)} results for: {query}")
        return results
    except Exception as e:
        logger.error(f"DuckDuckGo search failed: {e}")
        return []
