from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional, Callable


@dataclass
class CandidateProfile:
    provider_id: str
    name: str
    specialty: str
    current_location: str
    school: str
    grad_year: int
    current_employer: str
    spouse_name: Optional[str] = None
    spouse_location: Optional[str] = None
    geographic_ties: Optional[str] = None
    linkedin_url: Optional[str] = None
    # Enrichment fields
    distance_to_target_miles: Optional[float] = None
    alumni_network_strength: Optional[str] = None
    alumni_in_target_region: bool = False
    school_in_target_state: bool = False
    current_state_tax: Optional[dict] = None
    target_state_tax: Optional[dict] = None
    estimated_tax_savings: Optional[float] = None
    family_proximity_score: float = 0.0
    search_findings: list[str] = field(default_factory=list)
    # Scoring
    score_breakdown: dict[str, float] = field(default_factory=dict)
    total_score: float = 0.0
    score_tier: str = ""
    score_rationale: str = ""
    # Outreach
    recommended_hooks: list[str] = field(default_factory=list)
    outreach_email: str = ""


@dataclass
class SearchCriteria:
    specialty: str = "Endodontist"
    target_location: str = "South Bend, IN"
    target_state: str = ""
    max_distance_miles: float = 300.0
    min_grad_year: int = 2010
    max_grad_year: int = 2026

    def __post_init__(self):
        if not self.target_state and ", " in self.target_location:
            self.target_state = self.target_location.split(", ")[-1].strip()


@dataclass
class AgentLog:
    agent_name: str
    status: str = "pending"
    message: str = ""
    duration: float = 0.0
    candidates_affected: int = 0


@dataclass
class PipelineContext:
    criteria: SearchCriteria
    candidates: list[CandidateProfile] = field(default_factory=list)
    agent_logs: list[AgentLog] = field(default_factory=list)
    current_stage: str = ""


ProgressCallback = Callable[[str, str, Optional[float]], None]


class BaseAgent:
    name: str = "BaseAgent"
    description: str = ""

    def run(self, context: PipelineContext) -> PipelineContext:
        raise NotImplementedError

    def _log(self, context: PipelineContext, message: str, candidates_affected: int = 0, duration: float = 0.0):
        context.agent_logs.append(AgentLog(
            agent_name=self.name,
            status="complete",
            message=message,
            duration=round(duration, 2),
            candidates_affected=candidates_affected,
        ))
