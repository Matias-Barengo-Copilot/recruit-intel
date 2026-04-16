import plotly.graph_objects as go
import streamlit as st
from agents.base import CandidateProfile, PipelineContext

CHART_TEXT_COLOR = "#1B2F54"
CHART_GRID_COLOR = "#2D4A6E"
CHART_BG = "rgba(0,0,0,0)"

FACTOR_LABELS = {
    "proximity": "Proximity",
    "alumni": "Alumni Ties",
    "family": "Family/Spouse",
    "tax": "Tax Advantage",
    "geographic_ties": "Geo Ties",
    "career_stage": "Career Stage",
}


def render_radar_chart(candidate: CandidateProfile, weights: dict[str, float]):
    categories = list(FACTOR_LABELS.values())
    factor_keys = list(FACTOR_LABELS.keys())

    # Normalize scores to percentage of max
    values = []
    for key in factor_keys:
        score = candidate.score_breakdown.get(key, 0)
        max_score = weights.get(key, 1)
        pct = (score / max_score * 100) if max_score > 0 else 0
        values.append(round(pct, 1))

    # Close the polygon
    values_closed = values + [values[0]]
    categories_closed = categories + [categories[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=categories_closed,
        fill="toself",
        fillcolor="rgba(181, 25, 66, 0.15)",
        line=dict(color="rgb(181, 25, 66)", width=2),
        name=candidate.name,
    ))

    fig.update_layout(
        polar=dict(
            bgcolor=CHART_BG,
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                ticksuffix="%",
                tickfont=dict(color=CHART_TEXT_COLOR, size=10),
                gridcolor=CHART_GRID_COLOR,
            ),
            angularaxis=dict(
                tickfont=dict(color=CHART_TEXT_COLOR, size=11),
                gridcolor=CHART_GRID_COLOR,
            ),
        ),
        paper_bgcolor=CHART_BG,
        font=dict(color=CHART_TEXT_COLOR),
        showlegend=False,
        margin=dict(l=40, r=40, t=20, b=20),
        height=300,
    )
    st.plotly_chart(fig, width="stretch")


def render_score_comparison(context: PipelineContext):
    if not context or not context.candidates:
        return

    names = [c.name for c in context.candidates]
    scores = [c.total_score for c in context.candidates]
    colors = []
    for c in context.candidates:
        if c.score_tier == "Hot Lead":
            colors.append("#B51942")
        elif c.score_tier == "Warm Prospect":
            colors.append("#C97A1E")
        elif c.score_tier == "Worth Exploring":
            colors.append("#1EAD65")
        else:
            colors.append("#4A5568")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=scores,
        y=names,
        orientation="h",
        marker_color=colors,
        text=[f"{s:.0f}" for s in scores],
        textposition="outside",
        textfont=dict(size=12, color=CHART_TEXT_COLOR),
        cliponaxis=False,
    ))

    fig.update_layout(
        xaxis_title="Relocation Score",
        xaxis=dict(
            range=[0, 110],
            tickfont=dict(color=CHART_TEXT_COLOR),
            title_font=dict(color=CHART_TEXT_COLOR),
            gridcolor=CHART_GRID_COLOR,
        ),
        yaxis=dict(
            autorange="reversed",
            tickfont=dict(color=CHART_TEXT_COLOR),
            gridcolor=CHART_GRID_COLOR,
        ),
        margin=dict(l=10, r=40, t=10, b=30),
        height=max(400, len(names) * 40),
        bargap=0.25,
        paper_bgcolor=CHART_BG,
        plot_bgcolor=CHART_BG,
        font=dict(color=CHART_TEXT_COLOR),
    )
    st.plotly_chart(fig, width="stretch")
