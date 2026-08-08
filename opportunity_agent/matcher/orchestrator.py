from __future__ import annotations

import asyncio

from opportunity_agent.matcher.base import BaseMatcher
from opportunity_agent.models.candidate import CandidateProfile
from opportunity_agent.models.job import JobPosting
from opportunity_agent.models.match import MatchResult


class MatchOrchestrator:
    """
    Orchestrates batch matching of a CandidateProfile against multiple JobPostings
    concurrently, with rate limiting, sorting, and score filtering.
    """

    def __init__(
        self,
        matcher: BaseMatcher,
        max_concurrent_evaluations: int = 5,
    ) -> None:
        """
        Args:
            matcher: Strategy instance implementing BaseMatcher.
            max_concurrent_evaluations: Semaphore limit for concurrent LLM requests.
            min_score_threshold: Minimum overall_score required to include
                                 in final output.
        """
        self.matcher = matcher
        self.semaphore = asyncio.Semaphore(max_concurrent_evaluations)

    async def match_jobs(
        self,
        candidate: CandidateProfile,
        jobs: list[JobPosting],
    ) -> list[MatchResult]:
        """
        Evaluates a list of job postings concurrently against a candidate profile.

        Returns:
            list[MatchResult]: List of matched results.
        """
        if not jobs:
            return []

        tasks = [self._match_single_job(candidate, job) for job in jobs]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        valid_results: list[MatchResult] = [
            res for res in results if isinstance(res, MatchResult)
        ]

        return valid_results

    async def _match_single_job(
        self, candidate: CandidateProfile, job: JobPosting
    ) -> MatchResult:
        """
        Executes a single job match inside an async worker thread bounded by semaphore.
        """
        async with self.semaphore:
            # Runs synchronous BaseMatcher inside an async executor to prevent blocking
            return await asyncio.to_thread(self.matcher.match, candidate, job)
