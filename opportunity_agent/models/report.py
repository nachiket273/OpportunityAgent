from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from opportunity_agent.models.candidate import CandidateProfile
from opportunity_agent.models.match import MatchResult


@dataclass(slots=True)
class OpportunityReport:
    """
    Report container wrapping candidate details, metadata, and matched opportunities.
    """

    candidate: CandidateProfile
    results: list[MatchResult] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.now)
