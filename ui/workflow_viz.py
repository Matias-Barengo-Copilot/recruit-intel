import streamlit as st
from agents.base import PipelineContext


AGENT_ICONS = {
    "LinkedIn Search Agent": "🔍",
    "Facebook Enrichment Agent": "👥",
    "Web Search & Data Agent": "🌐",
    "Scoring Agent": "📊",
    "Outreach Agent": "✉️",
}

AGENT_DESCRIPTIONS = {
    "LinkedIn Search Agent": "Searches provider candidates by specialty and location from database",
    "Facebook Enrichment Agent": "Enriches profiles with spouse, family, and geographic connection data",
    "Web Search & Data Agent": "Gathers alumni network data, tax comparisons, and web intelligence",
    "Scoring Agent": "Calculates relocation likelihood scores using 6-factor weighted model",
    "Outreach Agent": "Generates personalized recruitment emails using discovered hooks",
}


def render_workflow(context: PipelineContext | None):
    st.subheader("Agent Pipeline")

    if context is None:
        st.info("Configure search criteria in the sidebar and click **Run Recruit Intel Pipeline** to start.")
        _render_empty_pipeline()
        return

    _render_completed_pipeline(context)


def _render_empty_pipeline():
    agent_names = [
        "LinkedIn Search Agent",
        "Facebook Enrichment Agent",
        "Web Search & Data Agent",
        "Scoring Agent",
        "Outreach Agent",
    ]
    for name in agent_names:
        icon = AGENT_ICONS.get(name, "⚙️")
        desc = AGENT_DESCRIPTIONS.get(name, "")
        with st.container(border=True):
            cols = st.columns([0.5, 5, 2])
            with cols[0]:
                st.write(icon)
            with cols[1]:
                st.markdown(f"**{name}**")
                st.caption(desc)
            with cols[2]:
                st.caption("⏳ Waiting")


def _render_completed_pipeline(context: PipelineContext):
    total_duration = sum(log.duration for log in context.agent_logs)

    for log in context.agent_logs:
        icon = AGENT_ICONS.get(log.agent_name, "⚙️")
        with st.container(border=True):
            cols = st.columns([0.5, 5, 2])
            with cols[0]:
                st.write(icon)
            with cols[1]:
                st.markdown(f"**{log.agent_name}**")
                st.caption(log.message)
            with cols[2]:
                st.markdown(f"✅ {log.duration:.1f}s")
                if log.candidates_affected:
                    st.caption(f"{log.candidates_affected} candidates")

    st.success(f"Pipeline complete in {total_duration:.1f}s — {len(context.candidates)} candidates processed")

    # Flow diagram
    _render_flow_diagram(context)


def _render_flow_diagram(context: PipelineContext):
    with st.expander("Pipeline Flow Diagram", expanded=False):
        dot = "digraph G {\n"
        dot += '  rankdir=LR;\n'
        dot += '  node [shape=box, style="rounded,filled", fontname="Arial", fontsize=10];\n'

        for i, log in enumerate(context.agent_logs):
            short_name = log.agent_name.replace(" Agent", "").replace(" & Data", "")
            color = "#1EAD65"  # P1 brand green for completed agents
            dot += f'  n{i} [label="{short_name}\\n{log.duration:.1f}s", fillcolor="{color}"];\n'

        for i in range(len(context.agent_logs) - 1):
            dot += f"  n{i} -> n{i+1};\n"

        dot += "}"
        st.graphviz_chart(dot)
