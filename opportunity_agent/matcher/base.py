from __future__ import annotations

from abc import ABC, abstractmethod

from opportunity_agent.models.candidate import CandidateProfile
from opportunity_agent.models.job import JobPosting
from opportunity_agent.models.match import MatchResult


class BaseMatcher(ABC):
    """
    Abstract interface for matching CandidateProfiles against JobPostings.
    """

    @abstractmethod
    def match(self, candidate: CandidateProfile, job: JobPosting) -> MatchResult:
        """
        Evaluate match fit between a candidate profile and job posting.

        Args:
            candidate: Parsed candidate profile.
            job: Target job posting.

        Returns:
            MatchResult: Scores, strengths, gaps, and decision reasoning.
        """
