import plotly.graph_objects as go
import streamlit as st
from agents.base import CandidateProfile, PipelineContext


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
        fillcolor="rgba(99, 110, 250, 0.2)",
        line=dict(color="rgb(99, 110, 250)", width=2),
        name=candidate.name,
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], ticksuffix="%"),
        ),
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
            colors.append("#FF4B4B")
        elif c.score_tier == "Warm Prospect":
            colors.append("#FFA500")
        elif c.score_tier == "Worth Exploring":
            colors.append("#FFD700")
        else:
            colors.append("#CCCCCC")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=scores,
        y=names,
        orientation="h",
        marker_color=colors,
        text=[f"{s:.0f}" for s in scores],
        textposition="outside",
        textfont=dict(size=12),
        cliponaxis=False,
    ))

    fig.update_layout(
        xaxis_title="Relocation Score",
        xaxis=dict(range=[0, 110]),
        yaxis=dict(autorange="reversed"),
        margin=dict(l=10, r=40, t=10, b=30),
        height=max(400, len(names) * 40),
        bargap=0.25,
    )
    st.plotly_chart(fig, width="stretch")
