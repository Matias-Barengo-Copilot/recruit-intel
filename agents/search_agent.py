import time
from agents.base import BaseAgent, PipelineContext
from utils.data_loader import load_alumni_networks, load_tax_rates
from utils.geo import extract_state, get_state_full_name
from config import Config


def _parse_pct(value) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip().rstrip("%")
    try:
        return float(s)
    except ValueError:
        return 0.0


class SearchAgent(BaseAgent):
    name = "Web Search & Data Agent"
    description = "Searches for alumni ties, geographic connections, and tax data"

    def __init__(self, tavily_api_key: str = ""):
        self.tavily_api_key = tavily_api_key

    def run(self, context: PipelineContext) -> PipelineContext:
        start = time.time()
        criteria = context.criteria

        # Load alumni networks
        alumni_df = load_alumni_networks()
        alumni_map = {}
        for _, row in alumni_df.iterrows():
            school_name = str(row.get("School", "")).lower()
            location = str(row.get("Location", ""))
            alumni_map[school_name] = {
                "location": location,
                "network_size": str(row.get("NetworkSize", "")),
                "regional_presence": str(row.get("RegionalPresence", "")),
            }

        # Load tax rates
        tax_df = load_tax_rates()
        tax_map = {}
        for _, row in tax_df.iterrows():
            state_name = str(row.get("State", "")).strip()
            tax_map[state_name.lower()] = {
                "income": _parse_pct(row.get("IncomeTaxRate", 0)),
                "sales": _parse_pct(row.get("SalesTaxRate", 0)),
                "property": _parse_pct(row.get("PropertyTaxRate", 0)),
            }

        target_state_full = get_state_full_name(criteria.target_state).lower()
        target_tax = tax_map.get(target_state_full)

        # Tavily search setup
        tavily_client = None
        if self.tavily_api_key:
            try:
                from tavily import TavilyClient
                tavily_client = TavilyClient(api_key=self.tavily_api_key)
            except Exception:
                pass

        search_count = 0
        for candidate in context.candidates:
            # Alumni matching
            candidate_school_lower = candidate.school.lower()
            matched_alumni = None
            for school_key, alumni_info in alumni_map.items():
                if school_key in candidate_school_lower or any(
                    word in candidate_school_lower
                    for word in school_key.split()
                    if len(word) > 3
                ):
                    matched_alumni = alumni_info
                    break

            if matched_alumni:
                candidate.alumni_network_strength = matched_alumni["regional_presence"]
                alumni_location = matched_alumni["location"]
                alumni_state = extract_state(alumni_location)
                candidate.school_in_target_state = alumni_state == criteria.target_state

            # Tax computation
            current_state = extract_state(candidate.current_location)
            current_state_full = get_state_full_name(current_state).lower()
            current_tax = tax_map.get(current_state_full)

            if current_tax and target_tax:
                candidate.current_state_tax = current_tax
                candidate.target_state_tax = target_tax
                income_diff = current_tax["income"] - target_tax["income"]
                candidate.estimated_tax_savings = round(
                    (income_diff / 100) * Config.ASSUMED_INCOME
                ) if income_diff > 0 else 0

            # Tavily web search
            if tavily_client:
                try:
                    query = f"{candidate.name} endodontist {candidate.school.split(',')[0]}"
                    response = tavily_client.search(query=query, max_results=3)
                    results = response.get("results", [])
                    candidate.search_findings = [
                        f"{r.get('title', '')}: {r.get('content', '')[:200]}"
                        for r in results
                    ]
                    search_count += 1
                except Exception:
                    candidate.search_findings = ["[Search failed]"]
            else:
                candidate.search_findings = ["[Offline mode - web search skipped]"]

        duration = time.time() - start
        msg = f"Matched alumni networks and computed tax savings for {len(context.candidates)} candidates"
        if search_count:
            msg += f"; ran {search_count} web searches via Tavily"
        self._log(context, msg, candidates_affected=len(context.candidates), duration=duration)
        return context
