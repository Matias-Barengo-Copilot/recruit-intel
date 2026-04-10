import streamlit as st
from agents.base import PipelineContext, CandidateProfile
from ui.score_chart import render_radar_chart, FACTOR_LABELS


def render_dossier(context: PipelineContext | None, weights: dict[str, float]):
    st.subheader("Candidate Dossier")

    if context is None or not context.candidates:
        st.info("Run the pipeline to view candidate dossiers.")
        return

    candidate_names = [f"#{i+1} — {c.name} ({c.total_score:.0f} pts)" for i, c in enumerate(context.candidates)]
    selected_idx = st.selectbox("Select Candidate", range(len(candidate_names)), format_func=lambda i: candidate_names[i])

    candidate = context.candidates[selected_idx]
    _render_candidate_detail(candidate, context, weights)


def _render_candidate_detail(candidate: CandidateProfile, context: PipelineContext, weights: dict[str, float]):
    # Tier badge
    tier_colors = {
        "Hot Lead": "red",
        "Warm Prospect": "orange",
        "Worth Exploring": "blue",
        "Long Shot": "gray",
    }
    color = tier_colors.get(candidate.score_tier, "gray")
    st.markdown(f"### {candidate.name}")
    st.markdown(f":{color}[**{candidate.score_tier}** — {candidate.total_score:.0f}/100]")

    st.divider()

    # Two column layout
    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown("#### Profile")
        detail_rows = {
            "Provider ID": candidate.provider_id,
            "Specialty": candidate.specialty,
            "Current Location": candidate.current_location,
            "Distance to Target": f"{candidate.distance_to_target_miles:.0f} miles" if candidate.distance_to_target_miles else "N/A",
            "School": candidate.school,
            "Graduation Year": str(candidate.grad_year),
            "Current Employer": candidate.current_employer,
            "Spouse": f"{candidate.spouse_name or 'N/A'} ({candidate.spouse_location or 'N/A'})",
            "Geographic Ties": candidate.geographic_ties or "None noted",
        }
        for label, value in detail_rows.items():
            st.markdown(f"**{label}:** {value}")

    with col2:
        st.markdown("#### Score Breakdown")
        render_radar_chart(candidate, weights)

    # Score details table
    st.markdown("#### Score Details")
    score_cols = st.columns(len(candidate.score_breakdown))
    for i, (factor, pts) in enumerate(candidate.score_breakdown.items()):
        max_pts = weights.get(factor, 0)
        label = FACTOR_LABELS.get(factor, factor)
        with score_cols[i]:
            pct = (pts / max_pts * 100) if max_pts > 0 else 0
            st.metric(label, f"{pts:.0f}/{max_pts}", f"{pct:.0f}%")

    # Rationale
    st.markdown("#### AI Analysis")
    st.info(candidate.score_rationale)

    # Tax info
    if candidate.estimated_tax_savings and candidate.estimated_tax_savings > 0:
        st.markdown("#### Tax Advantage")
        tax_cols = st.columns(3)
        with tax_cols[0]:
            if candidate.current_state_tax:
                st.metric("Current State Tax", f"{candidate.current_state_tax['income']:.2f}%")
        with tax_cols[1]:
            if candidate.target_state_tax:
                st.metric("Target State Tax", f"{candidate.target_state_tax['income']:.2f}%")
        with tax_cols[2]:
            st.metric("Est. Annual Savings", f"${candidate.estimated_tax_savings:,.0f}")

    # Hooks
    if candidate.recommended_hooks:
        st.markdown("#### Recommended Hooks")
        for hook in candidate.recommended_hooks:
            st.markdown(f"- {hook}")

    # Outreach email
    st.markdown("#### Outreach Email Draft")
    st.text_area(
        "Email (editable)",
        value=candidate.outreach_email,
        height=250,
        key=f"email_{candidate.provider_id}",
    )

    # Search findings
    if candidate.search_findings and candidate.search_findings[0] != "[Offline mode - web search skipped]":
        with st.expander("Web Search Findings"):
            for finding in candidate.search_findings:
                st.markdown(f"- {finding}")
