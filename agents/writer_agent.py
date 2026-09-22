"""
Agent 4: Report Writer Agent (The Writer) ✍️

Produces a polished, well-structured research report with executive summary,
detailed sections, inline citations, data visualizations, and bibliography.
Adapts tone for the target audience (academic / business / casual).
"""

from __future__ import annotations

import logging
from collections import Counter

from langchain_core.messages import HumanMessage, SystemMessage

from core.llm import get_llm
from core.state import ResearchState
from utils.citations import CitationManager

logger = logging.getLogger(__name__)

REPORT_PROMPT = """You are an expert research report writer. Write a comprehensive,
well-structured research report based on the synthesis analysis provided.

**Research Query:** {query}
**Target Audience:** {audience}

## Synthesis Analysis:

### Themes:
{themes}

### Key Insights:
{insights}

### Consensus Areas:
{consensus}

### Conflicting Viewpoints:
{conflicts}

### Data Points:
{data_points}

## Source Information:
{sources}

---

## Writing Instructions:

1. **Title**: Create a compelling, descriptive title for the report
2. **Executive Summary**: 3-4 sentence overview of key findings
3. **Introduction**: Brief context about why this topic matters
4. **Main Body**: Organize into 3-5 thematic sections based on the themes above.
   - Each section should have a descriptive heading
   - Include specific facts, data, and evidence
   - Reference sources using [N] notation where N is the source number
5. **Key Takeaways**: Bullet-pointed summary of the most important findings
6. **Future Outlook**: Brief section on predictions, gaps, and open questions

## Tone Guidelines:
- **Academic**: Formal, precise, heavy on evidence and methodology
- **Business**: Executive-friendly, action-oriented, focus on implications
- **Casual**: Engaging, accessible, uses analogies and plain language

Current audience: **{audience}**

## Formatting Rules:
- Use Markdown formatting (headers ##, bold **, lists -, etc.)
- Use [N] for inline source citations
- Include quantitative data where available
- Keep paragraphs concise (3-5 sentences max)
- Use emoji sparingly for section headers to aid scannability

Write the full report now.
"""


def run_writer_agent(state: ResearchState) -> dict:
    """
    Execute the Report Writer Agent.

    1. Formats all synthesis data for the writing prompt
    2. Generates a comprehensive Markdown report
    3. Injects proper citations
    4. Generates bibliography
    5. Prepares word frequency data for word cloud

    Args:
        state: Current LangGraph state.

    Returns:
        State update with report, report_html, visual_data, and agent_logs.
    """
    query = state["query"]
    audience = state.get("audience", "business")
    synthesis = state.get("synthesis", {})
    extracted_content = state.get("extracted_content", [])
    search_results = state.get("search_results", [])

    logger.info(f"✍️ Writer Agent: Generating {audience} report for: {query}")

    if not synthesis:
        return {
            "report": "# Research Report\n\nInsufficient data to generate a report.",
            "status": "report_complete",
            "agent_logs": ["✍️ Writer Agent: No synthesis data available"],
        }

    # Step 1: Build citation manager
    citation_mgr = CitationManager()
    for item in extracted_content:
        if item.get("url"):
            citation_mgr.register_source(
                url=item["url"],
                title=item.get("title", ""),
                author=item.get("author", ""),
                date=item.get("date", ""),
            )

    # Step 2: Format synthesis data for the prompt
    themes_str = _format_themes(synthesis.get("themes", []))
    insights_str = _format_list(synthesis.get("key_insights", []))
    consensus_str = _format_list(synthesis.get("consensus_areas", []))
    conflicts_str = _format_conflicts(synthesis.get("conflicting_views", []))
    data_points_str = _format_data_points(synthesis.get("data_points", []))
    sources_str = _format_sources(extracted_content, citation_mgr)

    # Step 3: Generate the report via Gemini
    report = _generate_report(
        query=query,
        audience=audience,
        themes=themes_str,
        insights=insights_str,
        consensus=consensus_str,
        conflicts=conflicts_str,
        data_points=data_points_str,
        sources=sources_str,
    )

    # Step 4: Append bibliography
    bibliography = citation_mgr.format_bibliography()
    if bibliography:
        report += f"\n\n---\n\n{bibliography}"

    # Step 5: Generate word frequency data for word cloud
    word_freq = _compute_word_frequencies(synthesis)
    visual_data = state.get("visual_data", [])
    if word_freq:
        visual_data.append({
            "type": "word_cloud",
            "title": "Key Terms",
            "word_freq": word_freq,
        })

    # Step 6: Add source quality chart data
    if search_results:
        visual_data.append({
            "type": "source_quality",
            "title": "Source Relevance Scores",
            "sources": search_results[:10],
        })

    log_msg = (
        f"✍️ Writer Agent: Generated {len(report)} char report, "
        f"{len(citation_mgr.get_all_sources())} citations, "
        f"{audience} tone"
    )
    logger.info(log_msg)

    return {
        "report": report,
        "visual_data": visual_data,
        "status": "report_complete",
        "agent_logs": [log_msg],
    }


def _generate_report(
    query: str,
    audience: str,
    themes: str,
    insights: str,
    consensus: str,
    conflicts: str,
    data_points: str,
    sources: str,
) -> str:
    """Generate the report content using Gemini."""
    llm = get_llm(temperature=0.4, max_tokens=8192)

    messages = [
        SystemMessage(content="You are an expert research report writer. Write in Markdown."),
        HumanMessage(content=REPORT_PROMPT.format(
            query=query,
            audience=audience,
            themes=themes,
            insights=insights,
            consensus=consensus,
            conflicts=conflicts,
            data_points=data_points,
            sources=sources,
        )),
    ]

    try:
        response = llm.invoke(messages)
        return response.content.strip()
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        return (
            f"# Research Report: {query}\n\n"
            "Report generation encountered an error. "
            "Please check your API key and try again."
        )


def _format_themes(themes: list[dict]) -> str:
    """Format themes list for the prompt."""
    if not themes:
        return "No specific themes identified."
    parts = []
    for t in themes:
        part = f"**{t.get('title', 'Unnamed')}**: {t.get('description', '')}"
        evidence = t.get("evidence", [])
        if evidence:
            part += "\n  Evidence: " + "; ".join(evidence[:3])
        parts.append(part)
    return "\n".join(parts)


def _format_list(items: list[str]) -> str:
    """Format a simple list for the prompt."""
    if not items:
        return "None identified."
    return "\n".join(f"- {item}" for item in items)


def _format_conflicts(conflicts: list[dict]) -> str:
    """Format conflicting viewpoints for the prompt."""
    if not conflicts:
        return "No significant conflicts found."
    parts = []
    for c in conflicts:
        parts.append(
            f"**{c.get('topic', 'Unknown')}**: "
            f"View A: {c.get('view_a', 'N/A')} vs View B: {c.get('view_b', 'N/A')}"
        )
    return "\n".join(parts)


def _format_data_points(data_points: list[dict]) -> str:
    """Format data points for the prompt."""
    if not data_points:
        return "No quantitative data available."
    parts = []
    for dp in data_points:
        parts.append(f"- **{dp.get('label', '')}**: {dp.get('value', '')} (Source: {dp.get('source', 'N/A')})")
    return "\n".join(parts)


def _format_sources(content: list[dict], citation_mgr: CitationManager) -> str:
    """Format source information with citation numbers."""
    if not content:
        return "No sources available."
    parts = []
    for item in content:
        url = item.get("url", "")
        citation = citation_mgr.get_citation(url) if url else "[?]"
        parts.append(f"{citation} {item.get('title', 'Unknown')} — {url}")
    return "\n".join(parts)


def _compute_word_frequencies(synthesis: dict) -> dict[str, int]:
    """Extract word frequencies from the synthesis for word cloud generation."""
    # Collect all text from themes, insights, etc.
    all_text = []
    for theme in synthesis.get("themes", []):
        all_text.append(theme.get("title", ""))
        all_text.append(theme.get("description", ""))
        all_text.extend(theme.get("evidence", []))
    all_text.extend(synthesis.get("key_insights", []))
    all_text.extend(synthesis.get("consensus_areas", []))

    # Combine and count words
    combined = " ".join(all_text).lower()
    words = combined.split()

    # Filter out common stop words
    stop_words = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "must", "shall", "can", "to", "of", "in",
        "for", "on", "with", "at", "by", "from", "as", "into", "through",
        "during", "before", "after", "above", "below", "between", "and",
        "but", "or", "nor", "not", "so", "yet", "both", "either", "neither",
        "each", "every", "all", "any", "few", "more", "most", "other", "some",
        "such", "no", "only", "own", "same", "than", "too", "very", "just",
        "that", "this", "these", "those", "it", "its", "they", "their", "them",
        "we", "our", "us", "he", "she", "his", "her", "him", "my", "your",
        "what", "which", "who", "whom", "when", "where", "why", "how", "if",
        "then", "else", "also", "about", "up", "out", "off", "over", "under",
    }

    filtered = [w for w in words if len(w) > 2 and w not in stop_words and w.isalpha()]
    freq = Counter(filtered)

    # Return top 50 words
    return dict(freq.most_common(50))
