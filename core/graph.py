"""
LangGraph Orchestrator — The conductor that routes work between agents.

Constructs a StateGraph with conditional edges:
  Search → Reader → Synthesis → [gap check] → Writer
                                    ↓ (if gaps)
                                  Search (loop)

Maximum of MAX_RESEARCH_ITERATIONS gap-filling loops.
"""

from __future__ import annotations

import logging

from langgraph.graph import END, StateGraph

import config
from agents.search_agent import run_search_agent
from agents.reader_agent import run_reader_agent
from agents.synthesis_agent import run_synthesis_agent
from agents.writer_agent import run_writer_agent
from core.state import ResearchState

logger = logging.getLogger(__name__)


def _should_research_more(state: ResearchState) -> str:
    """
    Conditional edge: decide whether to loop back for more research
    or proceed to the report writer.

    Returns:
        'search' if gaps exist and we haven't exceeded max iterations,
        'writer' otherwise.
    """
    iteration = state.get("iteration_count", 0)
    gaps = state.get("gaps_identified", [])

    if gaps and iteration < config.MAX_RESEARCH_ITERATIONS:
        logger.info(
            f"🔄 Gap-filling loop: {len(gaps)} gaps, "
            f"iteration {iteration + 1}/{config.MAX_RESEARCH_ITERATIONS}"
        )
        return "search"
    else:
        if gaps:
            logger.info(f"⏭️  Skipping {len(gaps)} gaps (max iterations reached)")
        return "writer"


def _increment_iteration(state: ResearchState) -> dict:
    """Increment the iteration counter before re-searching."""
    return {
        "iteration_count": state.get("iteration_count", 0) + 1,
        "agent_logs": [f"🔄 Starting research iteration {state.get('iteration_count', 0) + 2}"],
    }


def build_research_graph() -> StateGraph:
    """
    Construct and compile the LangGraph research pipeline.

    Graph flow:
        search → reader → synthesis → [conditional] → writer → END
                                           ↓ (gaps)
                                      increment → search (loop)

    Returns:
        A compiled LangGraph graph ready for .invoke() or .stream().
    """
    graph = StateGraph(ResearchState)

    # ── Register nodes ──
    graph.add_node("search", run_search_agent)
    graph.add_node("reader", run_reader_agent)
    graph.add_node("synthesis", run_synthesis_agent)
    graph.add_node("increment_iteration", _increment_iteration)
    graph.add_node("writer", run_writer_agent)

    # ── Define edges ──
    graph.set_entry_point("search")
    graph.add_edge("search", "reader")
    graph.add_edge("reader", "synthesis")

    # Conditional: after synthesis, either loop or write
    graph.add_conditional_edges(
        "synthesis",
        _should_research_more,
        {
            "search": "increment_iteration",
            "writer": "writer",
        },
    )

    # Loop edge: after incrementing, go back to search
    graph.add_edge("increment_iteration", "search")

    # Terminal edge
    graph.add_edge("writer", END)

    compiled = graph.compile()
    logger.info("✅ Research graph compiled successfully")
    return compiled


def run_research(
    query: str,
    audience: str = "business",
    stream_callback=None,
) -> ResearchState:
    """
    Execute the full research pipeline.

    Args:
        query: The user's research question.
        audience: Report tone: 'academic', 'business', or 'casual'.
        stream_callback: Optional callback(agent_name, status_msg) for live updates.

    Returns:
        The final ResearchState with the completed report.
    """
    graph = build_research_graph()

    initial_state: ResearchState = {
        "query": query,
        "audience": audience,
        "sub_queries": [],
        "search_results": [],
        "extracted_content": [],
        "vector_store_id": "",
        "synthesis": {},
        "gaps_identified": [],
        "report": "",
        "report_html": "",
        "visual_data": [],
        "iteration_count": 0,
        "status": "started",
        "agent_logs": [f"🚀 Research started: {query}"],
    }

    logger.info(f"🚀 Starting research pipeline for: {query}")

    # Stream through graph events for live updates
    final_state = None
    for event in graph.stream(initial_state, {"recursion_limit": 25}):
        for node_name, node_state in event.items():
            status = node_state.get("status", "")
            logs = node_state.get("agent_logs", [])

            if stream_callback and logs:
                for log in logs:
                    stream_callback(node_name, log)

            final_state = node_state
            logger.info(f"  Node '{node_name}' completed: {status}")

    # Merge final state with initial state to ensure all fields present
    if final_state:
        merged = {**initial_state}
        for key, value in final_state.items():
            if value:  # Only overwrite if there's actual data
                merged[key] = value
        return merged

    return initial_state
