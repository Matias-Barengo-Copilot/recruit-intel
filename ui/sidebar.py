import streamlit as st
from config import Config


def render_sidebar() -> dict:
    with st.sidebar:
        st.image("assets/logo.png", use_container_width=True)
        st.caption("Recruit Intel — Multi-Agent Provider Recruitment")

        st.divider()
        st.subheader("Search Criteria")

        specialty = st.selectbox("Specialty", ["Endodontist", "Orthodontist", "Periodontist", "Prosthodontist"], index=0)
        target_location = st.text_input("Target Location", value="South Bend, IN")
        max_distance = st.slider("Max Distance (miles)", 50, 500, int(Config.DEFAULT_MAX_DISTANCE), step=25)

        col1, col2 = st.columns(2)
        with col1:
            min_grad_year = st.number_input("Min Grad Year", 2000, 2026, 2010)
        with col2:
            max_grad_year = st.number_input("Max Grad Year", 2000, 2026, 2026)

        st.divider()
        st.subheader("API Configuration")

        openai_key = st.text_input(
            "OpenAI API Key",
            value=Config.OPENAI_API_KEY,
            type="password",
            help="For AI-generated rationale and outreach emails",
        )
        tavily_key = st.text_input(
            "Tavily API Key",
            value=Config.TAVILY_API_KEY,
            type="password",
            help="For web search enrichment (free tier: 1000/mo)",
        )
        offline_mode = st.toggle("Offline Mode", value=False, help="Skip all API calls, use template-based output")

        if offline_mode:
            openai_key = ""
            tavily_key = ""

        st.divider()
        with st.expander("Score Weights", expanded=False):
            weights = {}
            weights["proximity"] = st.slider("Proximity", 0, 30, Config.DEFAULT_WEIGHTS["proximity"])
            weights["alumni"] = st.slider("Alumni Ties", 0, 30, Config.DEFAULT_WEIGHTS["alumni"])
            weights["family"] = st.slider("Family/Spouse", 0, 30, Config.DEFAULT_WEIGHTS["family"])
            weights["tax"] = st.slider("Tax Advantage", 0, 20, Config.DEFAULT_WEIGHTS["tax"])
            weights["geographic_ties"] = st.slider("Geographic Ties", 0, 15, Config.DEFAULT_WEIGHTS["geographic_ties"])
            weights["career_stage"] = st.slider("Career Stage", 0, 15, Config.DEFAULT_WEIGHTS["career_stage"])
            total_w = sum(weights.values())
            st.caption(f"Total weight: {total_w} pts")

        run_clicked = st.button("Run Recruit Intel Pipeline", type="primary", width="stretch")

        return {
            "specialty": specialty,
            "target_location": target_location,
            "max_distance": max_distance,
            "min_grad_year": min_grad_year,
            "max_grad_year": max_grad_year,
            "openai_key": openai_key,
            "tavily_key": tavily_key,
            "offline_mode": offline_mode,
            "weights": weights,
            "run_clicked": run_clicked,
        }
