"""
Report Visual Elements Generator.

Creates Plotly charts, comparison tables, timeline visualizations,
and key-stats cards for embedding in research reports rendered via Streamlit.
"""

from __future__ import annotations

import plotly.graph_objects as go
import plotly.express as px


# ──────────────────────────────────────────────
# Color Palette (consistent across all visuals)
# ──────────────────────────────────────────────
COLORS = {
    "primary": "#6C63FF",
    "secondary": "#FF6584",
    "accent": "#43E97B",
    "info": "#00D2FF",
    "warning": "#FFD93D",
    "bg_dark": "#0F0F1A",
    "bg_card": "#1A1A2E",
    "text": "#E0E0FF",
    "text_muted": "#8888AA",
}

GRADIENT_COLORS = [
    "#6C63FF", "#00D2FF", "#43E97B", "#FFD93D",
    "#FF6584", "#A855F7", "#F97316", "#06B6D4",
]


def _apply_dark_layout(fig: go.Figure, title: str = "") -> go.Figure:
    """Apply a consistent dark theme to any Plotly figure."""
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=18, color=COLORS["text"], family="Inter, sans-serif"),
            x=0.5,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=COLORS["text_muted"], family="Inter, sans-serif"),
        margin=dict(l=40, r=40, t=60, b=40),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=COLORS["text"]),
        ),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.1)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.1)"),
    )
    return fig


def create_comparison_bar_chart(
    categories: list[str],
    values: list[float],
    title: str = "Comparison",
    value_label: str = "Value",
) -> go.Figure:
    """
    Create a horizontal bar chart for comparing items.

    Args:
        categories: Labels for each bar.
        values: Numeric values for each bar.
        title: Chart title.
        value_label: Label for the value axis.
    """
    colors = GRADIENT_COLORS[: len(categories)]
    fig = go.Figure(go.Bar(
        y=categories,
        x=values,
        orientation="h",
        marker=dict(
            color=colors,
            line=dict(width=0),
            cornerradius=6,
        ),
        text=[f"{v:.1f}" if isinstance(v, float) else str(v) for v in values],
        textposition="outside",
        textfont=dict(color=COLORS["text"]),
    ))
    fig = _apply_dark_layout(fig, title)
    fig.update_layout(
        xaxis_title=value_label,
        yaxis=dict(autorange="reversed"),
        height=max(300, len(categories) * 50),
    )
    return fig


def create_pie_chart(
    labels: list[str],
    values: list[float],
    title: str = "Distribution",
) -> go.Figure:
    """
    Create a donut chart showing distribution of categories.

    Args:
        labels: Category labels.
        values: Numeric values.
        title: Chart title.
    """
    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.55,
        marker=dict(colors=GRADIENT_COLORS[: len(labels)]),
        textinfo="label+percent",
        textfont=dict(color="white", size=12),
        hovertemplate="<b>%{label}</b><br>Value: %{value}<br>Share: %{percent}<extra></extra>",
    ))
    fig = _apply_dark_layout(fig, title)
    fig.update_layout(height=400)
    return fig


def create_timeline(
    dates: list[str],
    events: list[str],
    title: str = "Timeline",
) -> go.Figure:
    """
    Create a timeline visualization for chronological events.

    Args:
        dates: List of date strings.
        events: List of event descriptions.
        title: Chart title.
    """
    fig = go.Figure()
    for i, (date, event) in enumerate(zip(dates, events)):
        fig.add_trace(go.Scatter(
            x=[date],
            y=[0],
            mode="markers+text",
            marker=dict(
                size=20,
                color=GRADIENT_COLORS[i % len(GRADIENT_COLORS)],
                line=dict(width=2, color="white"),
            ),
            text=[f"<b>{event[:40]}</b>"],
            textposition="top center",
            textfont=dict(size=10, color=COLORS["text"]),
            hovertemplate=f"<b>{date}</b><br>{event}<extra></extra>",
            showlegend=False,
        ))

    fig = _apply_dark_layout(fig, title)
    fig.update_layout(
        height=300,
        yaxis=dict(visible=False, range=[-1, 2]),
        xaxis=dict(title=""),
    )
    return fig


def create_radar_chart(
    categories: list[str],
    values: list[float],
    title: str = "Multi-Dimensional Analysis",
) -> go.Figure:
    """
    Create a radar/spider chart for multi-dimensional comparisons.

    Args:
        categories: Dimension labels around the radar.
        values: Values for each dimension (0-100 scale).
        title: Chart title.
    """
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],  # Close the polygon
        theta=categories + [categories[0]],
        fill="toself",
        fillcolor="rgba(108, 99, 255, 0.2)",
        line=dict(color=COLORS["primary"], width=2),
        marker=dict(size=8, color=COLORS["primary"]),
    ))
    fig = _apply_dark_layout(fig, title)
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                visible=True,
                gridcolor="rgba(255,255,255,0.1)",
                linecolor="rgba(255,255,255,0.1)",
            ),
            angularaxis=dict(
                gridcolor="rgba(255,255,255,0.1)",
                linecolor="rgba(255,255,255,0.1)",
            ),
        ),
        height=450,
    )
    return fig


def create_key_stats_html(stats: list[dict]) -> str:
    """
    Generate HTML for key statistics highlight cards.

    Args:
        stats: List of dicts with keys: label, value, icon (emoji), color (optional)

    Returns:
        HTML string for embedding via st.markdown(unsafe_allow_html=True).
    """
    cards_html = ""
    for i, stat in enumerate(stats):
        color = stat.get("color", GRADIENT_COLORS[i % len(GRADIENT_COLORS)])
        cards_html += f"""
        <div style="
            background: linear-gradient(135deg, {color}22, {color}08);
            border: 1px solid {color}44;
            border-radius: 16px;
            padding: 20px 24px;
            text-align: center;
            min-width: 160px;
            flex: 1;
            backdrop-filter: blur(10px);
        ">
            <div style="font-size: 28px; margin-bottom: 8px;">{stat.get('icon', '📊')}</div>
            <div style="font-size: 28px; font-weight: 700; color: {color}; margin-bottom: 4px;">
                {stat['value']}
            </div>
            <div style="font-size: 13px; color: {COLORS['text_muted']}; text-transform: uppercase; letter-spacing: 1px;">
                {stat['label']}
            </div>
        </div>
        """

    return f"""
    <div style="display: flex; gap: 16px; flex-wrap: wrap; margin: 20px 0;">
        {cards_html}
    </div>
    """


def create_source_quality_chart(sources: list[dict]) -> go.Figure:
    """
    Create a chart showing the quality/relevance scores of sources used.

    Args:
        sources: List of dicts with keys: title, relevance_score

    Returns:
        Plotly figure showing source quality distribution.
    """
    titles = [s.get("title", "Unknown")[:35] + "..." for s in sources]
    scores = [s.get("relevance_score", 0.5) * 100 for s in sources]

    fig = go.Figure(go.Bar(
        x=scores,
        y=titles,
        orientation="h",
        marker=dict(
            color=scores,
            colorscale=[[0, COLORS["secondary"]], [0.5, COLORS["warning"]], [1, COLORS["accent"]]],
            line=dict(width=0),
            cornerradius=6,
        ),
        text=[f"{s:.0f}%" for s in scores],
        textposition="outside",
        textfont=dict(color=COLORS["text"]),
    ))
    fig = _apply_dark_layout(fig, "📊 Source Relevance Scores")
    fig.update_layout(
        xaxis_title="Relevance Score (%)",
        xaxis=dict(range=[0, 110]),
        yaxis=dict(autorange="reversed"),
        height=max(300, len(sources) * 50),
    )
    return fig


def create_word_cloud_figure(word_freq: dict[str, int]) -> go.Figure | None:
    """
    Create a word cloud visualization from word frequencies.

    Args:
        word_freq: Dict mapping words to their frequency counts.

    Returns:
        Plotly figure with word cloud, or None if wordcloud lib is unavailable.
    """
    try:
        from wordcloud import WordCloud
        import numpy as np
        from io import BytesIO
        from PIL import Image

        wc = WordCloud(
            width=800,
            height=400,
            background_color=None,
            mode="RGBA",
            colormap="cool",
            max_words=60,
            prefer_horizontal=0.7,
        ).generate_from_frequencies(word_freq)

        # Convert to image bytes
        img_buffer = BytesIO()
        wc.to_image().save(img_buffer, format="PNG")
        img_buffer.seek(0)

        img = Image.open(img_buffer)
        img_array = np.array(img)

        fig = go.Figure()
        fig.add_trace(go.Image(z=img_array))
        fig = _apply_dark_layout(fig, "🔤 Key Terms")
        fig.update_layout(
            height=400,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
        )
        return fig
    except ImportError:
        return None
