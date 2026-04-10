# Recruit Intel

Multi-agent AI system for P1 Dental Partners that identifies, scores, and drafts personalized outreach for dental provider candidates.

## What It Does

Recruit Intel runs a 5-agent pipeline to find candidates likely to relocate to a target market:

1. **LinkedIn Search Agent** — Finds candidates by specialty and geographic proximity
2. **Facebook Enrichment Agent** — Enriches profiles with spouse/family connection data
3. **Web Search Agent** — Gathers alumni network ties, tax comparisons, and web intelligence via Tavily
4. **Scoring Agent** — Calculates relocation likelihood (0-100) using 6 weighted factors
5. **Outreach Agent** — Generates personalized recruitment emails using discovered hooks

## Demo

![Dashboard](https://img.shields.io/badge/Streamlit-Running-brightgreen)

```
Endodontist search near South Bend, IN:
  #1  Dr. David Patel     — 80 pts (Hot Lead)     — Fort Wayne, IN (71 mi)
  #2  Dr. Ashley Davis     — 78 pts (Warm Prospect) — Madison, WI (188 mi)
  #3  Dr. Michael Thomas   — 75 pts (Warm Prospect) — Dayton, OH (171 mi)
```

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API keys (optional)

Copy `.env.example` to `.env` and add your keys:

```bash
cp .env.example .env
```

```
OPENAI_API_KEY=sk-your-key-here
TAVILY_API_KEY=tvly-your-key-here
```

The app works fully offline without any API keys — AI-generated emails and rationale fall back to template-based output.

### 3. Run the app

```bash
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

### 4. Use the pipeline

1. Set search criteria in the sidebar (specialty, target location, distance)
2. Click **Run Recruit Intel Pipeline**
3. Browse results across 4 tabs:
   - **Agent Workflow** — see each agent's progress and timing
   - **Candidate Rankings** — sorted table with tier badges
   - **Score Comparison** — horizontal bar chart comparing all candidates
   - **Candidate Dossier** — deep-dive with radar chart, score breakdown, editable outreach email

## Scoring Model

| Factor | Max Points | What It Measures |
|--------|-----------|-----------------|
| Geographic Proximity | 25 | Distance from candidate to target location |
| Alumni/School Ties | 20 | Candidate's school connection to target region |
| Family/Spouse Ties | 20 | Spouse location and family connections nearby |
| Tax Advantage | 15 | Estimated annual tax savings from relocation |
| Geographic Ties | 10 | Mentioned ties to target city/state in profile |
| Career Stage | 10 | Years post-graduation (3-8 years = most mobile) |

Score weights are adjustable via sidebar sliders.

**Tiers:** Hot Lead (80-100) | Warm Prospect (60-79) | Worth Exploring (40-59) | Long Shot (0-39)

## Tech Stack

- **Python + Streamlit** — interactive dashboard with zero frontend build step
- **OpenAI GPT-4o-mini** — scoring rationale and outreach email generation
- **Tavily** — web search enrichment (free tier: 1000 searches/month)
- **pandas + openpyxl** — Excel data processing
- **Plotly** — radar charts and bar charts

## Project Structure

```
recruit-intel/
├── app.py                  # Streamlit entry point
├── config.py               # API keys and defaults
├── agents/                 # 5-agent pipeline
│   ├── base.py             # Shared dataclasses (CandidateProfile, PipelineContext)
│   ├── linkedin_agent.py   # Agent 1: candidate search
│   ├── facebook_agent.py   # Agent 2: family enrichment
│   ├── search_agent.py     # Agent 3: alumni + tax + web search
│   ├── scoring_agent.py    # Agent 4: relocation scoring
│   ├── outreach_agent.py   # Agent 5: email generation
│   └── orchestrator.py     # Pipeline runner
├── utils/                  # Shared utilities
│   ├── data_loader.py      # Excel loading
│   ├── geo.py              # City coordinates + distance
│   ├── scoring.py          # Scoring algorithm
│   └── hooks.py            # Outreach template parser
├── ui/                     # Streamlit components
│   ├── sidebar.py          # Search form
│   ├── workflow_viz.py     # Agent pipeline visualization
│   ├── candidate_table.py  # Rankings table
│   ├── score_chart.py      # Radar + bar charts
│   └── dossier_card.py     # Candidate deep-dive
└── data/                   # Synthetic data (Excel + text)
    ├── p1_dental_provider_candidates.xlsx
    ├── p1_dental_alumni_networks.xlsx
    ├── p1_dental_tax_rates.xlsx
    └── outreach_hooks.txt
```

## Data

All data is synthetic (20 endodontist candidates, 8 university alumni networks, 7 state tax rates). No actual LinkedIn/Facebook scraping — agents read from local Excel files as stubs.
