import sys
import os

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from agents.base import SearchCriteria, PipelineContext
from agents.orchestrator import RecruitPipeline
from ui.sidebar import render_sidebar
from ui.workflow_viz import render_workflow
from ui.candidate_table import render_candidate_table
from ui.score_chart import render_score_comparison
from ui.dossier_card import render_dossier

st.set_page_config(
    page_title="Recruit Intel — P1 Dental Partners",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Session State ---
if "pipeline_context" not in st.session_state:
    st.session_state.pipeline_context = None
if "pipeline_running" not in st.session_state:
    st.session_state.pipeline_running = False

# --- Sidebar ---
sidebar = render_sidebar()

# --- Run Pipeline ---
if sidebar["run_clicked"] and not st.session_state.pipeline_running:
    st.session_state.pipeline_running = True
    st.session_state.pipeline_context = None

    criteria = SearchCriteria(
        specialty=sidebar["specialty"],
        target_location=sidebar["target_location"],
        max_distance_miles=float(sidebar["max_distance"]),
        min_grad_year=sidebar["min_grad_year"],
        max_grad_year=sidebar["max_grad_year"],
    )

    pipeline = RecruitPipeline(
        openai_api_key=sidebar["openai_key"],
        tavily_api_key=sidebar["tavily_key"],
        model="gpt-4o-mini",
        weights=sidebar["weights"],
    )

    # Run with progress display
    progress_area = st.empty()
    with progress_area.container():
        st.subheader("Running Agent Pipeline...")
        agent_statuses = {}

        def progress_callback(agent_name: str, status: str, duration: float | None):
            agent_statuses[agent_name] = (status, duration)

        context = pipeline.run(criteria, progress_callback=progress_callback)

    progress_area.empty()
    st.session_state.pipeline_context = context
    st.session_state.pipeline_running = False
    st.rerun()

# --- Main Content ---
context: PipelineContext | None = st.session_state.pipeline_context

# Header
st.markdown("# 🔍 Recruit Intel")
st.markdown("*Multi-Agent Provider Recruitment Intelligence Platform — P1 Dental Partners*")

if context:
    st.success(
        f"Pipeline complete: **{len(context.candidates)} candidates** found for "
        f"**{context.criteria.specialty}** near **{context.criteria.target_location}**"
    )

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Agent Workflow", "Candidate Rankings", "Score Comparison", "Candidate Dossier"])

with tab1:
    render_workflow(context)

with tab2:
    render_candidate_table(context)

with tab3:
    st.subheader("Score Comparison")
    if context and context.candidates:
        render_score_comparison(context)
    else:
        st.info("Run the pipeline to see score comparisons.")

with tab4:
    render_dossier(context, sidebar["weights"])
