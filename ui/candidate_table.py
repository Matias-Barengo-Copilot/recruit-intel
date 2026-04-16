import streamlit as st
import pandas as pd
from agents.base import PipelineContext


TIER_COLORS = {
    "Hot Lead": "🔴",
    "Warm Prospect": "🟠",
    "Worth Exploring": "🟢",
    "Long Shot": "⚪",
}


def render_candidate_table(context: PipelineContext | None):
    st.subheader("Candidate Rankings")

    if context is None or not context.candidates:
        st.info("Run the pipeline to see ranked candidates.")
        return

    # Summary metrics
    tiers = {}
    for c in context.candidates:
        tiers[c.score_tier] = tiers.get(c.score_tier, 0) + 1

    cols = st.columns(4)
    tier_order = ["Hot Lead", "Warm Prospect", "Worth Exploring", "Long Shot"]
    for i, tier in enumerate(tier_order):
        count = tiers.get(tier, 0)
        with cols[i]:
            st.metric(f"{TIER_COLORS.get(tier, '')} {tier}", count)

    st.divider()

    # Build table data
    rows = []
    for rank, c in enumerate(context.candidates, 1):
        top_hook = ""
        if c.score_breakdown:
            top_factor = max(c.score_breakdown, key=c.score_breakdown.get)
            top_hook = top_factor.replace("_", " ").title()

        rows.append({
            "Rank": rank,
            "Name": c.name,
            "Score": f"{c.total_score:.0f}",
            "Tier": f"{TIER_COLORS.get(c.score_tier, '')} {c.score_tier}",
            "Location": c.current_location,
            "Distance": f"{c.distance_to_target_miles:.0f} mi" if c.distance_to_target_miles else "N/A",
            "School": c.school.split(",")[0].split("+")[0].strip()[:30],
            "Top Factor": top_hook,
        })

    df = pd.DataFrame(rows)
    st.dataframe(
        df,
        width="stretch",
        hide_index=True,
        column_config={
            "Rank": st.column_config.NumberColumn(width="small"),
            "Score": st.column_config.TextColumn(width="small"),
            "Distance": st.column_config.TextColumn(width="small"),
        },
    )
