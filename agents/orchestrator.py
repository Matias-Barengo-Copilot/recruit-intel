import time
from typing import Callable, Optional

from agents.base import PipelineContext, SearchCriteria, ProgressCallback
from agents.linkedin_agent import LinkedInAgent
from agents.facebook_agent import FacebookAgent
from agents.search_agent import SearchAgent
from agents.scoring_agent import ScoringAgent
from agents.outreach_agent import OutreachAgent


class RecruitPipeline:
    def __init__(
        self,
        openai_api_key: str = "",
        tavily_api_key: str = "",
        model: str = "gpt-4o-mini",
        weights: dict | None = None,
    ):
        self.agents = [
            LinkedInAgent(),
            FacebookAgent(),
            SearchAgent(tavily_api_key=tavily_api_key),
            ScoringAgent(openai_api_key=openai_api_key, model=model, weights=weights),
            OutreachAgent(openai_api_key=openai_api_key, model=model),
        ]

    def run(
        self,
        criteria: SearchCriteria,
        progress_callback: Optional[ProgressCallback] = None,
    ) -> PipelineContext:
        context = PipelineContext(criteria=criteria)

        for agent in self.agents:
            context.current_stage = agent.name
            if progress_callback:
                progress_callback(agent.name, "running", None)

            context = agent.run(context)

            last_log = context.agent_logs[-1] if context.agent_logs else None
            duration = last_log.duration if last_log else 0

            if progress_callback:
                progress_callback(agent.name, "complete", duration)

        return context
