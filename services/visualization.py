"""Visualization service: Plotly charts and Mermaid diagrams."""
from __future__ import annotations

from typing import Any

import plotly.graph_objects as go


def reports_over_time_chart(dates: list[str]) -> go.Figure:
    """Line chart of reports created per day."""
    import pandas as pd
    if not dates:
        dates = ["No data"]
    df = pd.DataFrame({"date": pd.to_datetime(dates, errors="coerce")})
    df = df.groupby(df["date"].dt.date).size().reset_index(name="count")
    fig = go.Figure(data=[go.Scatter(x=df["date"], y=df["count"], mode="lines+markers",
                                     line=dict(color="#2563eb", width=3))])
    fig.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=30, b=20),
                      height=300, title="Reports Over Time")
    return fig


def topics_bar_chart(topics: list[tuple[str, int]]) -> go.Figure:
    """Horizontal bar chart of most researched topics."""
    if not topics:
        topics = [("No data", 1)]
    labels, counts = zip(*topics)
    fig = go.Figure(data=[go.Bar(x=list(counts), y=list(labels), orientation="h",
                                 marker_color="#16a34a")])
    fig.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=30, b=20),
                      height=300, title="Most Researched Topics")
    return fig


def confidence_gauge(confidence: float) -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=confidence * 100,
        title={"text": "Confidence %"},
        gauge={"axis": {"range": [0, 100]},
               "bar": {"color": "#2563eb"},
               "steps": [
                   {"range": [0, 40], "color": "#fee2e2"},
                   {"range": [40, 70], "color": "#fef9c3"},
                   {"range": [70, 100], "color": "#dcfce7"},
               ]},
    ))
    fig.update_layout(template="plotly_dark", height=250, margin=dict(l=20, r=20, t=40, b=20))
    return fig


def swot_radar(swot: dict[str, list[str]]) -> go.Figure:
    categories = ["Strengths", "Weaknesses", "Opportunities", "Threats"]
    values = [len(swot.get(k.lower(), [])) for k in categories]
    fig = go.Figure(data=go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill="toself",
        line=dict(color="#0ea5e9"),
    ))
    fig.update_layout(template="plotly_dark", polar=dict(radialaxis=dict(visible=True, range=[0, max(values + [1]) + 1])),
                      height=300, title="SWOT Analysis")
    return fig


def mermaid_mindmap(query: str, keywords: list[str]) -> str:
    """Generate a Mermaid mind map definition."""
    nodes = []
    for i, kw in enumerate(keywords[:8]):
        nodes.append(f"    node{i}({kw})")
    links = "\n".join(f"    root --- node{i}" for i in range(len(nodes)))
    body = "\n".join(nodes)
    return f"mindmap\n  root(({query}))\n{links}\n{body}" if keywords else f"mindmap\n  root(({query}))"


def mermaid_flowchart(query: str) -> str:
    return f"""flowchart LR
    A[User Query: {query}] --> B[Planner Agent]
    B --> C[Search Agent]
    B --> D[RAG Agent]
    C --> E[Fact Verification]
    D --> E
    E --> F[Writer Agent]
    F --> G[Critic Agent]
    G --> H[Enrichment Agent]
    H --> I[Citation Agent]
    H --> J[Presentation Agent]
    H --> K[Interview Agent]
    H --> L[Quiz Agent]
"""


def mermaid_timeline(timeline: list[dict[str, str]]) -> str:
    if not timeline:
        return "timeline\n    title Research Timeline\n    No timeline data"
    lines = ["timeline", "    title Research Timeline"]
    for item in timeline:
        lines.append(f"    {item.get('year','')}: {item.get('event','')}")
    return "\n".join(lines)
