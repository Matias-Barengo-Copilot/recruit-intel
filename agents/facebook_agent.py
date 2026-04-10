import time
from agents.base import BaseAgent, PipelineContext
from utils.geo import extract_state, get_distance, are_adjacent


class FacebookAgent(BaseAgent):
    name = "Facebook Enrichment Agent"
    description = "Enriches candidate profiles with spouse and family connection data"

    def run(self, context: PipelineContext) -> PipelineContext:
        start = time.time()
        criteria = context.criteria
        target_city = criteria.target_location.split(",")[0].strip().lower()
        target_state = criteria.target_state

        enriched = 0
        for candidate in context.candidates:
            score = 0.0

            # Spouse location scoring
            if candidate.spouse_location:
                spouse_state = extract_state(candidate.spouse_location)
                spouse_distance = get_distance(candidate.spouse_location, criteria.target_location)

                if spouse_distance is not None and spouse_distance < 50:
                    score = max(score, 1.0)
                elif spouse_state == target_state:
                    score = max(score, 0.8)
                elif are_adjacent(target_state, spouse_state):
                    score = max(score, 0.5)
                else:
                    score = max(score, 0.2)

            # Geographic ties scoring
            if candidate.geographic_ties:
                ties_lower = candidate.geographic_ties.lower()
                if target_city in ties_lower:
                    score = max(score, 1.0)
                elif target_state.lower() in ties_lower or any(
                    kw in ties_lower for kw in ["indiana", target_state.lower()]
                ):
                    score = max(score, 0.8)
                elif "midwest" in ties_lower:
                    score = max(score, 0.4)

            candidate.family_proximity_score = score
            if score > 0:
                enriched += 1

        duration = time.time() - start
        self._log(
            context,
            f"Enriched {enriched}/{len(context.candidates)} candidates with family/spouse connection data",
            candidates_affected=enriched,
            duration=duration,
        )
        return context
