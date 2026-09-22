"""
Agent 3: Synthesis Agent (The Thinker) 🧠

Analyzes all gathered information, cross-references sources, identifies
patterns and contradictions, spots knowledge gaps, and organizes findings
into thematic clusters. Can trigger a feedback loop for more research.
"""

from __future__ import annotations

import json
import logging

from langchain_core.messages import HumanMessage, SystemMessage

from core.llm import get_llm
from core.state import ResearchState
from tools import vector_store

logger = logging.getLogger(__name__)

SYNTHESIS_PROMPT = """You are a senior research analyst performing deep synthesis of
gathered information on the following research topic:

**Research Query:** {query}

You have access to extracted information from multiple sources. Your job is to:
1. Cross-reference facts across sources
2. Identify areas of consensus and conflicting viewpoints
3. Spot patterns and emerging trends
4. Organize findings into thematic clusters
5. Identify any significant knowledge gaps that need more research

## Extracted Information from Sources:

{extracted_info}

## Relevant Context from Vector Database:

{rag_context}

---

Return your analysis as a JSON object with this structure:
{{
    "themes": [
        {{
            "title": "Theme title",
            "description": "2-3 sentence description of this theme",
            "evidence": ["Key fact 1 from source", "Key fact 2 from source"],
            "source_urls": ["url1", "url2"]
        }}
    ],
    "key_insights": [
        "Major insight or conclusion 1",
        "Major insight or conclusion 2"
    ],
    "consensus_areas": ["Areas where sources agree"],
    "conflicting_views": [
        {{
            "topic": "The debated topic",
            "view_a": "One perspective",
            "view_b": "Opposing perspective"
        }}
    ],
    "data_points": [
        {{
            "label": "Metric or data name",
            "value": "The value or statistic",
            "source": "Where this data came from"
        }}
    ],
    "knowledge_gaps": ["Gap 1 that needs more research", "Gap 2"],
    "timeline_events": [
        {{
            "date": "2025 or specific date",
            "event": "What happened"
        }}
    ]
}}

IMPORTANT: Return ONLY valid JSON, no other text. Be thorough but factual.
"""


def run_synthesis_agent(state: ResearchState) -> dict:
    """
    Execute the Synthesis Agent.

    1. Gathers all extracted content
    2. Queries the vector DB for relevant context
    3. Uses Gemini for deep analysis
    4. Identifies knowledge gaps for potential re-search

    Args:
        state: Current LangGraph state.

    Returns:
        State update with synthesis, gaps_identified, visual_data, and agent_logs.
    """
    query = state["query"]
    extracted_content = state.get("extracted_content", [])
    collection_name = state.get("vector_store_id", "")

    logger.info(f"🧠 Synthesis Agent activated with {len(extracted_content)} sources")

    if not extracted_content:
        return {
            "synthesis": {"themes": [], "key_insights": ["Insufficient data for synthesis."]},
            "gaps_identified": [query],
            "status": "synthesis_complete",
            "agent_logs": ["🧠 Synthesis Agent: No content to synthesize"],
        }

    # Step 1: Format extracted content for the prompt
    extracted_info = _format_extracted_content(extracted_content)

    # Step 2: Get relevant context from vector DB
    rag_context = ""
    if collection_name:
        rag_results = vector_store.query_collection(
            collection_name=collection_name,
            query=query,
            n_results=15,
        )
        rag_context = _format_rag_results(rag_results)

    # Step 3: Run synthesis with Gemini
    synthesis = _run_synthesis(query, extracted_info, rag_context)

    # Step 4: Extract visual data for the report
    visual_data = _extract_visual_data(synthesis)

    # Step 5: Identify gaps
    gaps = synthesis.get("knowledge_gaps", [])

    log_msg = (
        f"🧠 Synthesis Agent: Identified {len(synthesis.get('themes', []))} themes, "
        f"{len(synthesis.get('key_insights', []))} insights, "
        f"{len(gaps)} knowledge gaps"
    )
    logger.info(log_msg)

    return {
        "synthesis": synthesis,
        "gaps_identified": gaps,
        "visual_data": visual_data,
        "status": "synthesis_complete",
        "agent_logs": [log_msg],
    }


def _format_extracted_content(content: list[dict]) -> str:
    """Format extracted content into a readable string for the LLM."""
    parts = []
    for i, item in enumerate(content, 1):
        part = f"### Source {i}: {item.get('title', 'Unknown')}\n"
        part += f"URL: {item.get('url', 'N/A')}\n"
        if item.get("summary"):
            part += f"Summary: {item['summary']}\n"
        if item.get("key_facts"):
            part += "Key Facts:\n"
            for fact in item["key_facts"][:5]:
                part += f"  - {fact}\n"
        if item.get("data_points"):
            part += "Data Points:\n"
            for dp in item["data_points"][:3]:
                part += f"  - {dp}\n"
        if item.get("entities"):
            part += f"Entities: {', '.join(item['entities'][:10])}\n"
        parts.append(part)
    return "\n---\n".join(parts)


def _format_rag_results(results: list[dict]) -> str:
    """Format RAG retrieval results into context string."""
    if not results:
        return "No additional context available."

    parts = []
    for i, r in enumerate(results, 1):
        source = r.get("metadata", {}).get("source_url", "Unknown")
        parts.append(f"[Context {i}] (Source: {source})\n{r['text'][:500]}")
    return "\n\n".join(parts)


def _run_synthesis(query: str, extracted_info: str, rag_context: str) -> dict:
    """Run the synthesis LLM call."""
    llm = get_llm(temperature=0.3, max_tokens=8192)

    messages = [
        SystemMessage(content="You are a senior research analyst. Return only valid JSON."),
        HumanMessage(content=SYNTHESIS_PROMPT.format(
            query=query,
            extracted_info=extracted_info,
            rag_context=rag_context,
        )),
    ]

    try:
        response = llm.invoke(messages)
        content = response.content.strip()

        # Clean up potential markdown code block wrapping
        if content.startswith("```"):
            content = content.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

        return json.loads(content)
    except (json.JSONDecodeError, Exception) as e:
        logger.error(f"Synthesis parsing failed: {e}")
        return {
            "themes": [],
            "key_insights": ["Analysis could not be fully completed due to a processing error."],
            "consensus_areas": [],
            "conflicting_views": [],
            "data_points": [],
            "knowledge_gaps": [f"{query} — requires re-analysis"],
            "timeline_events": [],
        }


def _extract_visual_data(synthesis: dict) -> list[dict]:
    """Extract data suitable for chart generation from the synthesis."""
    visuals = []

    # Data points → bar chart
    data_points = synthesis.get("data_points", [])
    if data_points:
        visuals.append({
            "type": "bar_chart",
            "title": "Key Data Points",
            "labels": [dp.get("label", "") for dp in data_points],
            "values": [dp.get("value", "") for dp in data_points],
        })

    # Timeline events → timeline
    timeline = synthesis.get("timeline_events", [])
    if timeline:
        visuals.append({
            "type": "timeline",
            "title": "Timeline of Key Events",
            "dates": [t.get("date", "") for t in timeline],
            "events": [t.get("event", "") for t in timeline],
        })

    # Themes → radar/pie chart data
    themes = synthesis.get("themes", [])
    if themes:
        visuals.append({
            "type": "theme_distribution",
            "title": "Research Theme Distribution",
            "labels": [t.get("title", "") for t in themes],
            "values": [len(t.get("evidence", [])) for t in themes],
        })

    return visuals
