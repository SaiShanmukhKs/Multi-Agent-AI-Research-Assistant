"""
Multi-Agent Research Assistant — Streamlit Frontend.

Premium dark-themed UI with live agent pipeline tracking,
interactive Plotly charts, and report export functionality.
"""

import streamlit as st
import time
import os
import logging

# ── Page Config (must be first st call) ──
st.set_page_config(
    page_title="Multi-Agent Research Assistant",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Load custom CSS ──
css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Logging setup ──
logging.basicConfig(level=logging.INFO)

# ── Imports (after page config) ──
import config
from core.graph import run_research
from utils.report_visuals import (
    create_comparison_bar_chart,
    create_pie_chart,
    create_timeline,
    create_radar_chart,
    create_key_stats_html,
    create_source_quality_chart,
    create_word_cloud_figure,
)


def main():
    """Main application entry point."""

    # ════════════════════════════════════════════
    # HERO SECTION
    # ════════════════════════════════════════════
    st.markdown(
        '<h1 class="hero-title">🔬 Multi-Agent Research Assistant</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="hero-subtitle">'
        '4 AI agents collaborate to research any topic — '
        'from web search to a polished, cited report'
        '</p>',
        unsafe_allow_html=True,
    )

    # ════════════════════════════════════════════
    # SIDEBAR — Configuration
    # ════════════════════════════════════════════
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        st.divider()

        audience = st.selectbox(
            "📎 Report Audience",
            options=config.REPORT_AUDIENCE_OPTIONS,
            index=config.REPORT_AUDIENCE_OPTIONS.index(config.DEFAULT_AUDIENCE),
            help="Controls the tone and depth of the final report",
        )

        max_iterations = st.slider(
            "🔄 Max Research Loops",
            min_value=1,
            max_value=3,
            value=config.MAX_RESEARCH_ITERATIONS,
            help="How many gap-filling loops the system can perform",
        )

        st.divider()

        # API key status
        st.markdown("### 🔑 API Status")
        if config.GOOGLE_API_KEY:
            st.success("✅ Google Gemini API", icon="🟢")
        else:
            st.error("❌ Google API Key missing", icon="🔴")
            st.caption("Set `GOOGLE_API_KEY` in your `.env` file")

        if config.USE_TAVILY:
            st.success("✅ Tavily Search API", icon="🟢")
        else:
            st.info("🔵 Using DuckDuckGo (free)", icon="ℹ️")

        st.divider()

        # Agent legend
        st.markdown("### 🤖 Agent Pipeline")
        agents_info = [
            ("🔍", "Scout", "Web search & query decomposition"),
            ("📄", "Analyst", "Document reading & RAG indexing"),
            ("🧠", "Thinker", "Synthesis & gap detection"),
            ("✍️", "Writer", "Report generation & citations"),
        ]
        for icon, name, desc in agents_info:
            st.markdown(
                f'<div class="agent-card">'
                f'<span class="agent-icon">{icon}</span>'
                f'<span class="agent-name">{name}</span>'
                f'<div class="agent-status">{desc}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # ════════════════════════════════════════════
    # MAIN — Research Input
    # ════════════════════════════════════════════

    # Check API key before allowing research
    if not config.GOOGLE_API_KEY:
        st.warning(
            "⚠️ **Google API Key Required** — Please set your `GOOGLE_API_KEY` in a `.env` file "
            "in the project root. Get one at [Google AI Studio](https://aistudio.google.com/app/apikey).",
            icon="🔑",
        )
        st.stop()

    # Input area
    col1, col2 = st.columns([5, 1])
    with col1:
        query = st.text_input(
            "🔎 What would you like to research?",
            placeholder="e.g., Latest advancements in quantum error correction",
            label_visibility="collapsed",
        )
    with col2:
        research_btn = st.button("🚀 Research", use_container_width=True, type="primary")

    # Example queries
    st.markdown(
        "<div style='text-align:center; margin: -8px 0 24px 0;'>"
        "<span style='color:#8888AA; font-size:0.85rem;'>Try: </span>"
        "<span style='color:#6C63FF; font-size:0.85rem;'>"
        "\"AI in drug discovery 2025\" · "
        "\"Quantum computing vs classical for optimization\" · "
        "\"Impact of LLMs on software engineering\""
        "</span></div>",
        unsafe_allow_html=True,
    )

    # ════════════════════════════════════════════
    # RESEARCH EXECUTION
    # ════════════════════════════════════════════
    if research_btn and query:
        # Update config with sidebar values
        config.MAX_RESEARCH_ITERATIONS = max_iterations

        # Session state for results
        st.session_state["research_running"] = True

        # Agent progress tracking
        agent_phases = {
            "search": {"icon": "🔍", "name": "Web Search Agent", "status": "pending"},
            "reader": {"icon": "📄", "name": "Document Reader Agent", "status": "pending"},
            "synthesis": {"icon": "🧠", "name": "Synthesis Agent", "status": "pending"},
            "increment_iteration": {"icon": "🔄", "name": "Gap-Filling Loop", "status": "pending"},
            "writer": {"icon": "✍️", "name": "Report Writer Agent", "status": "pending"},
        }

        # Progress display
        st.markdown("---")
        st.markdown("### 🔄 Research Pipeline")

        progress_bar = st.progress(0)
        status_text = st.empty()
        agent_log_container = st.container()

        agent_progress_cols = st.columns(4)
        agent_placeholders = {}
        main_agents = ["search", "reader", "synthesis", "writer"]
        for i, agent_key in enumerate(main_agents):
            info = agent_phases[agent_key]
            with agent_progress_cols[i]:
                agent_placeholders[agent_key] = st.empty()
                agent_placeholders[agent_key].markdown(
                    f'<div class="agent-card">'
                    f'<span class="agent-icon">{info["icon"]}</span> '
                    f'<span class="agent-name">{info["name"]}</span>'
                    f'<div class="agent-status">⏳ Waiting...</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        logs_collected = []

        def update_callback(node_name: str, log_msg: str):
            """Callback to update UI as agents complete."""
            logs_collected.append(log_msg)

            # Map node to progress
            progress_map = {"search": 0.25, "reader": 0.50, "synthesis": 0.75, "writer": 1.0, "increment_iteration": 0.60}
            progress = progress_map.get(node_name, 0)
            progress_bar.progress(progress)
            status_text.markdown(f"**{log_msg}**")

            # Update agent cards
            if node_name in agent_placeholders:
                info = agent_phases[node_name]
                agent_placeholders[node_name].markdown(
                    f'<div class="agent-card complete">'
                    f'<span class="agent-icon">{info["icon"]}</span> '
                    f'<span class="agent-name">{info["name"]}</span>'
                    f'<div class="agent-status">✅ Complete</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        # Run the research pipeline
        try:
            with st.spinner("🔬 Agents are working..."):
                result = run_research(
                    query=query,
                    audience=audience,
                    stream_callback=update_callback,
                )

            progress_bar.progress(1.0)
            status_text.markdown("**✅ Research complete!**")
            st.session_state["result"] = result
            st.session_state["logs"] = logs_collected

        except Exception as e:
            st.error(f"❌ Research pipeline failed: {str(e)}", icon="🚨")
            st.exception(e)
            st.stop()

    # ════════════════════════════════════════════
    # RESULTS DISPLAY
    # ════════════════════════════════════════════
    if "result" in st.session_state:
        result = st.session_state["result"]
        report = result.get("report", "")
        visual_data = result.get("visual_data", [])
        search_results = result.get("search_results", [])
        synthesis = result.get("synthesis", {})
        extracted_content = result.get("extracted_content", [])
        logs = st.session_state.get("logs", [])

        st.markdown("---")

        # ── Key Stats Cards ──
        stats = [
            {"icon": "🔍", "label": "Sources Found", "value": str(len(search_results)), "color": "#6C63FF"},
            {"icon": "📄", "label": "Documents Read", "value": str(len(extracted_content)), "color": "#00D2FF"},
            {"icon": "🧠", "label": "Themes Identified", "value": str(len(synthesis.get("themes", []))), "color": "#43E97B"},
            {"icon": "💡", "label": "Key Insights", "value": str(len(synthesis.get("key_insights", []))), "color": "#FFD93D"},
        ]
        st.markdown(create_key_stats_html(stats), unsafe_allow_html=True)

        # ── Tabbed Results ──
        tab_report, tab_visuals, tab_sources, tab_logs = st.tabs([
            "📝 Research Report",
            "📊 Visualizations",
            "🔗 Sources",
            "📋 Agent Logs",
        ])

        # ── TAB 1: Report ──
        with tab_report:
            if report:
                st.markdown(f'<div class="report-container">\n\n{report}\n\n</div>', unsafe_allow_html=True)

                # Download buttons
                st.markdown("---")
                dl_col1, dl_col2, _ = st.columns([1, 1, 3])
                with dl_col1:
                    st.download_button(
                        label="📥 Download Markdown",
                        data=report,
                        file_name="research_report.md",
                        mime="text/markdown",
                    )
                with dl_col2:
                    # Simple HTML export
                    html_content = _generate_html_report(report, result.get("query", ""))
                    st.download_button(
                        label="📥 Download HTML",
                        data=html_content,
                        file_name="research_report.html",
                        mime="text/html",
                    )
            else:
                st.warning("No report was generated.")

        # ── TAB 2: Visualizations ──
        with tab_visuals:
            st.markdown("### 📊 Research Visualizations")

            if not visual_data and not search_results:
                st.info("No visual data was generated for this research.")
            else:
                for viz in visual_data:
                    viz_type = viz.get("type", "")

                    if viz_type == "theme_distribution":
                        labels = viz.get("labels", [])
                        values = viz.get("values", [])
                        if labels and values:
                            v_col1, v_col2 = st.columns(2)
                            with v_col1:
                                fig = create_pie_chart(labels, values, viz.get("title", "Theme Distribution"))
                                st.plotly_chart(fig, use_container_width=True)
                            with v_col2:
                                if len(labels) >= 3:
                                    # Normalize values for radar chart
                                    max_val = max(values) if max(values) > 0 else 1
                                    norm_values = [(v / max_val) * 100 for v in values]
                                    fig = create_radar_chart(labels, norm_values, "Theme Depth Analysis")
                                    st.plotly_chart(fig, use_container_width=True)

                    elif viz_type == "timeline":
                        dates = viz.get("dates", [])
                        events = viz.get("events", [])
                        if dates and events:
                            fig = create_timeline(dates, events, viz.get("title", "Timeline"))
                            st.plotly_chart(fig, use_container_width=True)

                    elif viz_type == "bar_chart":
                        labels = viz.get("labels", [])
                        values = viz.get("values", [])
                        if labels and values:
                            # Try to convert values to floats
                            numeric_values = []
                            valid_labels = []
                            for l, v in zip(labels, values):
                                try:
                                    numeric_values.append(float(str(v).replace("%", "").replace(",", "")))
                                    valid_labels.append(l)
                                except (ValueError, TypeError):
                                    pass
                            if valid_labels:
                                fig = create_comparison_bar_chart(
                                    valid_labels, numeric_values,
                                    viz.get("title", "Data Comparison"),
                                )
                                st.plotly_chart(fig, use_container_width=True)

                    elif viz_type == "word_cloud":
                        word_freq = viz.get("word_freq", {})
                        if word_freq:
                            fig = create_word_cloud_figure(word_freq)
                            if fig:
                                st.plotly_chart(fig, use_container_width=True)

                    elif viz_type == "source_quality":
                        sources = viz.get("sources", [])
                        if sources:
                            fig = create_source_quality_chart(sources)
                            st.plotly_chart(fig, use_container_width=True)

        # ── TAB 3: Sources ──
        with tab_sources:
            st.markdown("### 🔗 Sources Used")
            if extracted_content:
                for i, item in enumerate(extracted_content, 1):
                    with st.expander(f"**[{i}]** {item.get('title', 'Unknown Source')}", expanded=False):
                        st.markdown(f"🔗 **URL:** [{item.get('url', 'N/A')}]({item.get('url', '#')})")
                        st.markdown(f"📊 **Words:** {item.get('word_count', 'N/A')}")
                        if item.get("summary"):
                            st.markdown(f"📝 **Summary:** {item['summary']}")
                        if item.get("key_facts"):
                            st.markdown("**Key Facts:**")
                            for fact in item["key_facts"][:5]:
                                st.markdown(f"  - {fact}")
                        if item.get("entities"):
                            st.markdown(f"**Entities:** {', '.join(item['entities'][:10])}")
            else:
                st.info("No sources were processed.")

        # ── TAB 4: Agent Logs ──
        with tab_logs:
            st.markdown("### 📋 Agent Activity Log")
            if logs:
                for log in logs:
                    st.markdown(
                        f'<div class="agent-card" style="padding:12px 16px; margin:4px 0;">{log}</div>',
                        unsafe_allow_html=True,
                    )
            else:
                st.info("No logs available.")


def _generate_html_report(markdown_report: str, title: str) -> str:
    """Generate a standalone HTML version of the report."""
    # Simple markdown-to-HTML conversion using basic replacements
    import re

    html = markdown_report

    # Convert headers
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

    # Convert bold and italic
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

    # Convert bullet points
    html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)

    # Convert links
    html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2" target="_blank">\1</a>', html)

    # Wrap paragraphs
    paragraphs = html.split('\n\n')
    processed = []
    for p in paragraphs:
        p = p.strip()
        if p and not p.startswith('<h') and not p.startswith('<li'):
            p = f'<p>{p}</p>'
        processed.append(p)
    html = '\n'.join(processed)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} — Research Report</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #0a0a1a, #0f0f2e, #1a0a2e);
            color: #E0E0FF;
            line-height: 1.7;
            padding: 40px 20px;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: rgba(26, 26, 46, 0.4);
            border: 1px solid rgba(108, 99, 255, 0.15);
            border-radius: 24px;
            padding: 48px;
            backdrop-filter: blur(16px);
        }}
        h1 {{
            background: linear-gradient(135deg, #6C63FF, #00D2FF, #43E97B);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.2rem;
            margin-bottom: 24px;
            border-bottom: 2px solid rgba(108, 99, 255, 0.3);
            padding-bottom: 16px;
        }}
        h2 {{ color: #6C63FF; margin: 32px 0 16px; font-size: 1.5rem; }}
        h3 {{ color: #00D2FF; margin: 24px 0 12px; font-size: 1.2rem; }}
        p {{ margin: 12px 0; color: #c0c0dd; }}
        li {{ margin: 6px 0 6px 24px; color: #c0c0dd; }}
        strong {{ color: #E0E0FF; }}
        a {{ color: #43E97B; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        blockquote {{
            border-left: 3px solid #6C63FF;
            padding-left: 16px;
            color: #8888AA;
            font-style: italic;
            margin: 16px 0;
        }}
        .footer {{
            text-align: center;
            margin-top: 48px;
            color: #8888AA;
            font-size: 0.85rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        {html}
        <div class="footer">
            Generated by Multi-Agent Research Assistant 🔬
        </div>
    </div>
</body>
</html>"""


if __name__ == "__main__":
    main()
