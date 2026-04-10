import time
from agents.base import BaseAgent, PipelineContext
from utils.data_loader import load_outreach_hooks
from utils.hooks import parse_hooks, select_hooks_for_candidate, build_template_email


class OutreachAgent(BaseAgent):
    name = "Outreach Agent"
    description = "Generates personalized recruitment emails using discovered hooks"

    def __init__(self, openai_api_key: str = "", model: str = "gpt-4o-mini"):
        self.openai_api_key = openai_api_key
        self.model = model

    def run(self, context: PipelineContext) -> PipelineContext:
        start = time.time()
        criteria = context.criteria

        raw_hooks = load_outreach_hooks()
        categories = parse_hooks(raw_hooks)

        for candidate in context.candidates:
            hooks = select_hooks_for_candidate(candidate, categories, criteria, top_n=3)
            candidate.recommended_hooks = hooks

        # Generate emails
        if self.openai_api_key:
            self._generate_ai_emails(context, categories)
        else:
            for candidate in context.candidates:
                candidate.outreach_email = build_template_email(
                    candidate, criteria, candidate.recommended_hooks
                )

        duration = time.time() - start
        self._log(
            context,
            f"Generated personalized outreach emails for {len(context.candidates)} candidates",
            candidates_affected=len(context.candidates),
            duration=duration,
        )
        return context

    def _generate_ai_emails(self, context: PipelineContext, categories):
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)

            for candidate in context.candidates:
                hooks_text = "\n".join(f"- {h}" for h in candidate.recommended_hooks) if candidate.recommended_hooks else "No specific hooks identified."
                last_name = candidate.name.split()[-1] if candidate.name else "Doctor"

                prompt = (
                    f"You are drafting a personalized recruitment email for P1 Dental Partners.\n\n"
                    f"Target candidate: Dr. {candidate.name}\n"
                    f"Current location: {candidate.current_location}\n"
                    f"School: {candidate.school}\n"
                    f"Target role: Lead {candidate.specialty} in {context.criteria.target_location}\n"
                    f"Relocation score: {candidate.total_score:.0f}/100 ({candidate.score_tier})\n"
                    f"Tax savings: ${candidate.estimated_tax_savings:,.0f}/year\n"
                    f"Distance: {candidate.distance_to_target_miles:.0f} miles\n"
                    f"Spouse: {candidate.spouse_name or 'Unknown'} in {candidate.spouse_location or 'Unknown'}\n"
                    f"Geographic ties: {candidate.geographic_ties or 'None noted'}\n\n"
                    f"Key hooks to weave in:\n{hooks_text}\n\n"
                    f"Score rationale: {candidate.score_rationale}\n\n"
                    f"Write a warm, professional 150-word email. Start with 'Dear Dr. {last_name}'. "
                    f"Mention P1 Dental Partners by name. End with a clear call to action (schedule a call). "
                    f"Do NOT use generic flattery. Be specific to THIS candidate's background."
                )

                response = client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=350,
                    temperature=0.8,
                )
                candidate.outreach_email = response.choices[0].message.content.strip()

        except Exception:
            for candidate in context.candidates:
                if not candidate.outreach_email:
                    candidate.outreach_email = build_template_email(
                        candidate, context.criteria, candidate.recommended_hooks
                    )
