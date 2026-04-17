import time
import pandas as pd
from agents.base import BaseAgent, PipelineContext, CandidateProfile
from utils.data_loader import load_candidates
from utils.geo import get_distance


class LinkedInAgent(BaseAgent):
    name = "LinkedIn Search Agent"
    description = "Searches for provider candidates by specialty and location"

    def run(self, context: PipelineContext) -> PipelineContext:
        start = time.time()
        criteria = context.criteria

        df = load_candidates()

        # Filter by specialty
        mask = df["Specialty"].str.lower() == criteria.specialty.lower()
        filtered = df[mask]

        candidates = []
        for _, row in filtered.iterrows():
            location = str(row.get("CurrentLocation", ""))
            distance = get_distance(location, criteria.target_location)

            # Filter by max distance
            if distance is not None and distance > criteria.max_distance_miles:
                continue

            grad_year = int(row.get("GradYear", 0))
            if grad_year < criteria.min_grad_year or grad_year > criteria.max_grad_year:
                continue

            candidate = CandidateProfile(
                provider_id=str(row.get("ProviderID", "")),
                name=str(row.get("Name", "")),
                specialty=str(row.get("Specialty", "")),
                current_location=location,
                school=str(row.get("School", "")),
                grad_year=grad_year,
                current_employer=str(row.get("CurrentEmployer", "")),
                spouse_name=str(row.get("SpouseName", "")) if pd.notna(row.get("SpouseName")) else None,
                spouse_location=str(row.get("SpouseLocation", "")) if pd.notna(row.get("SpouseLocation")) else None,
                geographic_ties=str(row.get("GeographicTies", "")) if pd.notna(row.get("GeographicTies")) else None,
                linkedin_url=str(row.get("LinkedInURL", "")) if pd.notna(row.get("LinkedInURL")) else None,
                distance_to_target_miles=distance,
            )
            candidates.append(candidate)

        context.candidates = candidates
        duration = time.time() - start
        self._log(
            context,
            f"Found {len(candidates)} {criteria.specialty} candidates within {criteria.max_distance_miles:.0f} miles of {criteria.target_location}",
            candidates_affected=len(candidates),
            duration=duration,
        )
        return context
