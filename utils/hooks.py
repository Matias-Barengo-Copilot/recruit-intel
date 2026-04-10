from __future__ import annotations

import re
from dataclasses import dataclass
from agents.base import CandidateProfile, SearchCriteria
from utils.geo import extract_state, get_state_full_name


@dataclass
class HookCategory:
    name: str
    templates: list[str]


def parse_hooks(raw_text: str) -> dict[str, HookCategory]:
    categories: dict[str, HookCategory] = {}
    current_name = None
    current_templates: list[str] = []

    for line in raw_text.splitlines():
        header_match = re.match(r"^===\s*(.+?)\s*===$", line.strip())
        if header_match:
            if current_name and current_templates:
                key = current_name.lower().replace("/", "_").replace(" ", "_")
                categories[key] = HookCategory(name=current_name, templates=current_templates)
            current_name = header_match.group(1)
            current_templates = []
        elif line.strip().startswith("- "):
            template = line.strip()[2:].strip().strip('"')
            current_templates.append(template)
        elif line.strip().startswith("Hook "):
            pass  # Skip sample combination headers
        elif line.strip().startswith('"') and current_name == "SAMPLE COMBINATION HOOKS":
            template = line.strip().strip('"')
            current_templates.append(template)

    if current_name and current_templates:
        key = current_name.lower().replace("/", "_").replace(" ", "_")
        categories[key] = HookCategory(name=current_name, templates=current_templates)

    return categories


def fill_template(template: str, candidate: CandidateProfile, criteria: SearchCriteria) -> str:
    current_state = extract_state(candidate.current_location)
    target_state = criteria.target_state

    replacements = {
        "{SCHOOL}": candidate.school.split(",")[0].split("+")[0].strip() if candidate.school else "",
        "{TARGET_CITY}": criteria.target_location,
        "{CURRENT_CITY}": candidate.current_location,
        "{CURRENT_STATE}": get_state_full_name(current_state),
        "{STATE}": get_state_full_name(target_state),
        "{TAX_SAVINGS}": f"{candidate.estimated_tax_savings:,.0f}" if candidate.estimated_tax_savings else "significant",
        "{LAST_NAME}": candidate.name.split()[-1] if candidate.name else "",
        "{FIRST_NAME}": candidate.name.split()[0] if candidate.name else "",
        "{DISTANCE}": f"{candidate.distance_to_target_miles:.0f} miles" if candidate.distance_to_target_miles else "nearby",
        "{SPOUSE_LOCATION}": candidate.spouse_location or "the region",
        "{FAMILY_LOCATION}": candidate.geographic_ties or "the Midwest",
        "{REGION}": "Midwest",
        "{SPOUSE_FIELD}": "",
        "{INDUSTRY}": "healthcare",
        "{LIFESTYLE_FEATURE}": "outdoor recreation and community events",
    }

    result = template
    for key, value in replacements.items():
        result = result.replace(key, value)
    return result


def select_hooks_for_candidate(
    candidate: CandidateProfile,
    categories: dict[str, HookCategory],
    criteria: SearchCriteria,
    top_n: int = 3,
) -> list[str]:
    score_to_category = {
        "alumni": "alumni_ties",
        "tax": "tax_savings",
        "family": "family_spouse_ties",
        "proximity": "geographic_proximity",
        "career_stage": "career_growth",
        "geographic_ties": "lifestyle",
    }

    ranked_factors = sorted(
        candidate.score_breakdown.items(),
        key=lambda x: x[1],
        reverse=True,
    )

    selected: list[str] = []
    used_categories: set[str] = set()

    for factor_name, score in ranked_factors:
        if score <= 0 or len(selected) >= top_n:
            break
        cat_key = score_to_category.get(factor_name, "")
        if cat_key and cat_key in categories and cat_key not in used_categories:
            cat = categories[cat_key]
            if cat.templates:
                filled = fill_template(cat.templates[0], candidate, criteria)
                selected.append(filled)
                used_categories.add(cat_key)

    return selected


def build_template_email(candidate: CandidateProfile, criteria: SearchCriteria, hooks: list[str]) -> str:
    last_name = candidate.name.split()[-1] if candidate.name else "Doctor"
    lines = [f"Dear Dr. {last_name},\n"]

    if hooks:
        lines.append(hooks[0] + "\n")
        if len(hooks) > 1:
            lines.append("Additionally, " + hooks[1][0].lower() + hooks[1][1:] + "\n")
        if len(hooks) > 2:
            lines.append(hooks[2] + "\n")
    else:
        lines.append(
            f"I'm reaching out about an exciting endodontics opportunity with P1 Dental Partners in {criteria.target_location}.\n"
        )

    lines.append(
        "P1 Dental Partners is a 60+ location network offering clinical autonomy, "
        "partnership track within 3-5 years, and enterprise-level support.\n"
    )
    lines.append(
        "Would you be open to a brief conversation to learn more? "
        "I'd love to schedule a 15-minute call at your convenience.\n"
    )
    lines.append("Best regards,\nP1 Dental Partners Recruitment Team")

    return "\n".join(lines)
