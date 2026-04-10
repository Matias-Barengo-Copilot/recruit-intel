# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Recruit Intel is a multi-agent AI system for P1 Dental Partners that identifies, scores, and drafts personalized outreach for dental provider candidates. It uses a 5-agent sequential pipeline to process synthetic candidate data and produce ranked dossiers with relocation likelihood scores.

## Commands

```bash
# Run the app
streamlit run app.py

# Install dependencies
pip install -r requirements.txt

# Quick offline pipeline test (no API keys needed)
python -c "
import sys; sys.path.insert(0, '.')
from agents.base import SearchCriteria
from agents.orchestrator import RecruitPipeline
ctx = RecruitPipeline().run(SearchCriteria())
for c in ctx.candidates[:5]: print(f'{c.name}: {c.total_score:.0f} pts')
"
```

## Architecture

**Agent Pipeline** (sequential, in `agents/`):
1. `LinkedInAgent` — reads `p1_dental_provider_candidates.xlsx`, filters by specialty + distance
2. `FacebookAgent` — enriches with spouse/family proximity scores from same Excel data
3. `SearchAgent` — matches alumni networks + tax rates from Excel; optionally runs Tavily web searches
4. `ScoringAgent` — calculates 0-100 relocation score using 6 weighted factors; optionally generates AI rationale via OpenAI
5. `OutreachAgent` — selects hook templates from `outreach_hooks.txt`, fills placeholders; optionally generates natural email via OpenAI

**Orchestrator** (`agents/orchestrator.py`): Runs agents 1-5 in order, passing a shared `PipelineContext` (defined in `agents/base.py`) through each. Supports a `progress_callback` for real-time UI updates.

**Scoring** (`utils/scoring.py`): Pure functions, no LLM. Six factors: proximity (25pts), alumni (20), family (20), tax (15), geographic_ties (10), career_stage (10). Weights are adjustable via the sidebar.

**Data** (`data/`): Synthetic Excel files. `p1_dental_provider_candidates.xlsx` (20 endodontists), `p1_dental_alumni_networks.xlsx` (8 schools), `p1_dental_tax_rates.xlsx` (7 states), `outreach_hooks.txt` (6 hook categories with templates).

**Geo** (`utils/geo.py`): Hardcoded city coordinates for ~20 Midwest cities. Haversine distance formula. No external geocoding API.

**UI** (`ui/`): Streamlit components. Single-page app with 4 tabs: Agent Workflow, Candidate Rankings, Score Comparison, Candidate Dossier.

## Key Design Decisions

- Custom agent orchestration (not LangGraph/CrewAI) — the pipeline is strictly sequential, no branching or loops needed
- Hardcoded city coordinates — deterministic, offline, covers all cities in dataset. Add new cities to `CITY_COORDS` dict in `utils/geo.py`
- Tax rates may have `%` suffix in Excel — parsed by `_parse_pct()` in `search_agent.py`
- All API calls (OpenAI, Tavily) have offline fallbacks — template-based rationale and emails work without any API keys
- `sys.path.insert(0, ...)` in `app.py` ensures imports work when Streamlit runs from project root

## API Keys

Configured via `.env` file (loaded by `python-dotenv` in `config.py`):
- `OPENAI_API_KEY` — GPT-4o-mini for scoring rationale + outreach emails
- `TAVILY_API_KEY` — web search enrichment (free tier: 1000 searches/mo)
