import time
from agents.base import BaseAgent, PipelineContext
from utils.scoring import calculate_all_scores, get_tier, build_template_rationale


class ScoringAgent(BaseAgent):
    name = "Scoring Agent"
    description = "Calculates relocation likelihood scores for each candidate"

    def __init__(self, openai_api_key: str = "", model: str = "gpt-4o-mini", weights: dict | None = None):
        self.openai_api_key = openai_api_key
        self.model = model
        self.weights = weights

    def run(self, context: PipelineContext) -> PipelineContext:
        start = time.time()
        criteria = context.criteria

        for candidate in context.candidates:
            breakdown = calculate_all_scores(candidate, criteria, self.weights)
            candidate.score_breakdown = breakdown
            candidate.total_score = round(sum(breakdown.values()), 1)
            candidate.score_tier = get_tier(candidate.total_score)

        # Generate rationales
        if self.openai_api_key:
            self._generate_ai_rationales(context)
        else:
            for candidate in context.candidates:
                candidate.score_rationale = build_template_rationale(candidate, criteria)

        # Sort by score
        context.candidates.sort(key=lambda c: c.total_score, reverse=True)

        duration = time.time() - start
        tiers = {}
        for c in context.candidates:
            tiers[c.score_tier] = tiers.get(c.score_tier, 0) + 1
        tier_summary = ", ".join(f"{v} {k}" for k, v in tiers.items())

        self._log(
            context,
            f"Scored {len(context.candidates)} candidates: {tier_summary}",
            candidates_affected=len(context.candidates),
            duration=duration,
        )
        return context

    def _generate_ai_rationales(self, context: PipelineContext):
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)

            for candidate in context.candidates:
                bd = candidate.score_breakdown
                bd_text = ", ".join(f"{k}: {v:.0f}" for k, v in bd.items())
                prompt = (
                    f"You are a dental recruitment analyst for P1 Dental Partners. "
                    f"Write a 2-3 sentence rationale for why this candidate is a {candidate.score_tier} "
                    f"for relocation to {context.criteria.target_location}.\n\n"
                    f"Candidate: {candidate.name}, currently in {candidate.current_location}, "
                    f"graduated from {candidate.school} in {candidate.grad_year}.\n"
                    f"Score: {candidate.total_score:.0f}/100\n"
                    f"Breakdown: {bd_text}\n"
                    f"Distance: {candidate.distance_to_target_miles:.0f} miles\n"
                    f"Tax savings: ${candidate.estimated_tax_savings:,.0f}/year\n"
                    f"Spouse location: {candidate.spouse_location or 'Unknown'}\n"
                    f"Geographic ties: {candidate.geographic_ties or 'None noted'}\n\n"
                    f"Be specific. Reference actual data points."
                )

                response = client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=200,
                    temperature=0.7,
                )
                candidate.score_rationale = response.choices[0].message.content.strip()

        except Exception:
            # Fallback to template rationale
            for candidate in context.candidates:
                if not candidate.score_rationale:
                    candidate.score_rationale = build_template_rationale(candidate, context.criteria)
