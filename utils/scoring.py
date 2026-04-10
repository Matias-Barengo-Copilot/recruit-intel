from agents.base import CandidateProfile, SearchCriteria


def score_proximity(distance: float | None, max_pts: float = 25) -> float:
    if distance is None:
        return 0
    if distance < 50:
        return max_pts
    elif distance < 100:
        return max_pts * 0.80
    elif distance < 200:
        return max_pts * 0.60
    elif distance < 300:
        return max_pts * 0.40
    elif distance < 500:
        return max_pts * 0.20
    return 0


def score_alumni(candidate: CandidateProfile, max_pts: float = 20) -> float:
    if candidate.school_in_target_state:
        return max_pts
    strength = (candidate.alumni_network_strength or "").lower()
    if strength == "very strong":
        return max_pts * 0.75
    elif strength == "strong":
        return max_pts * 0.50
    elif strength == "moderate":
        return max_pts * 0.25
    return 0


def score_family(candidate: CandidateProfile, max_pts: float = 20) -> float:
    return round(candidate.family_proximity_score * max_pts, 1)


def score_tax(savings: float | None, max_pts: float = 15) -> float:
    if savings is None:
        return 0
    if savings > 15000:
        return max_pts
    elif savings > 8000:
        return max_pts * 0.67
    elif savings > 3000:
        return max_pts * 0.33
    return 0


def score_geographic_ties(candidate: CandidateProfile, criteria: SearchCriteria, max_pts: float = 10) -> float:
    ties = (candidate.geographic_ties or "").lower()
    target_city = criteria.target_location.split(",")[0].strip().lower()
    target_state_full = {
        "IN": "indiana", "IL": "illinois", "OH": "ohio",
        "MI": "michigan", "WI": "wisconsin",
    }.get(criteria.target_state, criteria.target_state.lower())

    if target_city in ties:
        return max_pts
    if target_state_full in ties or criteria.target_state.lower() in ties:
        return max_pts * 0.7
    if "midwest" in ties:
        return max_pts * 0.4
    return 0


def score_career_stage(grad_year: int, current_year: int = 2026, max_pts: float = 10) -> float:
    years_out = current_year - grad_year
    if 3 <= years_out <= 8:
        return max_pts
    elif 1 <= years_out < 3:
        return max_pts * 0.7
    elif 8 < years_out <= 15:
        return max_pts * 0.5
    elif years_out > 15:
        return max_pts * 0.2
    return 0


def calculate_all_scores(
    candidate: CandidateProfile,
    criteria: SearchCriteria,
    weights: dict[str, float] | None = None,
) -> dict[str, float]:
    from config import Config
    w = weights or Config.DEFAULT_WEIGHTS

    breakdown = {
        "proximity": score_proximity(candidate.distance_to_target_miles, w["proximity"]),
        "alumni": score_alumni(candidate, w["alumni"]),
        "family": score_family(candidate, w["family"]),
        "tax": score_tax(candidate.estimated_tax_savings, w["tax"]),
        "geographic_ties": score_geographic_ties(candidate, criteria, w["geographic_ties"]),
        "career_stage": score_career_stage(candidate.grad_year, max_pts=w["career_stage"]),
    }
    return breakdown


def get_tier(score: float) -> str:
    if score >= 80:
        return "Hot Lead"
    elif score >= 60:
        return "Warm Prospect"
    elif score >= 40:
        return "Worth Exploring"
    return "Long Shot"


def build_template_rationale(candidate: CandidateProfile, criteria: SearchCriteria) -> str:
    parts = []
    bd = candidate.score_breakdown

    if bd.get("proximity", 0) > 0 and candidate.distance_to_target_miles:
        parts.append(f"located just {candidate.distance_to_target_miles:.0f} miles from {criteria.target_location}")
    if bd.get("alumni", 0) > 0:
        parts.append(f"{candidate.school} alumni with {candidate.alumni_network_strength or 'regional'} network presence")
    if bd.get("family", 0) > 0:
        if candidate.spouse_location:
            parts.append(f"spouse connected to {candidate.spouse_location}")
        if candidate.geographic_ties:
            parts.append(f"geographic ties: {candidate.geographic_ties}")
    if bd.get("tax", 0) > 0 and candidate.estimated_tax_savings:
        parts.append(f"potential tax savings of ${candidate.estimated_tax_savings:,.0f}/year")
    if bd.get("career_stage", 0) >= 8:
        years_out = 2026 - candidate.grad_year
        parts.append(f"{years_out} years post-graduation (prime relocation window)")

    if not parts:
        return f"Dr. {candidate.name.split()[-1]} scored {candidate.total_score:.0f}/100 based on available data."

    joined = "; ".join(parts)
    return f"Dr. {candidate.name.split()[-1]} is a {candidate.score_tier} ({candidate.total_score:.0f}/100): {joined}."
