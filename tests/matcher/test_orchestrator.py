from __future__ import annotations

import pytest

from opportunity_agent.matcher.base import BaseMatcher
from opportunity_agent.matcher.orchestrator import MatchOrchestrator
from opportunity_agent.models.candidate import CandidateProfile
from opportunity_agent.models.job import JobPosting
from opportunity_agent.models.match import MatchResult


class MockMatcher(BaseMatcher):
    """Stub matcher simulating matching results or raising errors on specific jobs."""

    def __init__(self) -> None:
        self.active_calls = 0
        self.max_observed_concurrency = 0

    def match(self, candidate: CandidateProfile, job: JobPosting) -> MatchResult:
        self.active_calls += 1
        if self.active_calls > self.max_observed_concurrency:
            self.max_observed_concurrency = self.active_calls

        if "Fail" in job.title:
            self.active_calls -= 1
            raise RuntimeError(f"LLM failure evaluating job '{job.title}'")

        result = MatchResult(
            job=job,
            overall_score=80.0,
            skill_score=80.0,
            education_score=80.0,
            experience_score=80.0,
            research_score=80.0,
            publication_score=80.0,
        )
        self.active_calls -= 1
        return result


@pytest.fixture
def sample_candidate() -> CandidateProfile:
    return CandidateProfile(name="Alice Scientist")


@pytest.fixture
def sample_jobs() -> list[JobPosting]:
    return [
        JobPosting(
            id="1",
            title="Job One",
            organization="Org A",
            url="https://example.com/1",
        ),
        JobPosting(
            id="2",
            title="Job Two",
            organization="Org B",
            url="https://example.com/2",
        ),
        JobPosting(
            id="3",
            title="Failing Job",
            organization="Org C",
            url="https://example.com/3",
        ),
    ]


@pytest.mark.asyncio
async def test_match_jobs_success_and_exception_handling(
    sample_candidate: CandidateProfile, sample_jobs: list[JobPosting]
) -> None:
    """
    Verify that valid jobs return MatchResult objects while failing jobs
    are safely filtered out without raising an unhandled exception.
    """
    matcher = MockMatcher()
    orchestrator = MatchOrchestrator(matcher=matcher, max_concurrent_evaluations=5)

    results = await orchestrator.match_jobs(sample_candidate, sample_jobs)

    # 1. Failing Job (index 2) should be filtered out
    assert len(results) == 2

    # 2. Results should preserve output type and original valid jobs
    assert all(isinstance(res, MatchResult) for res in results)
    titles = [res.job.title for res in results]
    assert "Job One" in titles
    assert "Job Two" in titles
    assert "Failing Job" not in titles


@pytest.mark.asyncio
async def test_match_jobs_empty_input(sample_candidate: CandidateProfile) -> None:
    """Verify that passing an empty job list immediately returns an empty list."""
    matcher = MockMatcher()
    orchestrator = MatchOrchestrator(matcher=matcher)

    results = await orchestrator.match_jobs(sample_candidate, [])

    assert results == []


@pytest.mark.asyncio
async def test_match_jobs_respects_semaphore_concurrency(
    sample_candidate: CandidateProfile,
) -> None:
    """
    Verify that the orchestrator limits max concurrent calls using the semaphore.
    """

    class SlowMatcher(BaseMatcher):
        def __init__(self) -> None:
            self.active_calls = 0
            self.max_observed_concurrency = 0

        def match(self, candidate: CandidateProfile, job: JobPosting) -> MatchResult:
            self.active_calls += 1
            if self.active_calls > self.max_observed_concurrency:
                self.max_observed_concurrency = self.active_calls

            # Simulate blocking computation/network IO
            import time

            time.sleep(0.05)

            self.active_calls -= 1
            return MatchResult(
                job=job,
                overall_score=75.0,
                skill_score=75.0,
                education_score=75.0,
                experience_score=75.0,
                research_score=75.0,
                publication_score=75.0,
            )

    slow_matcher = SlowMatcher()
    max_concurrency = 2
    orchestrator = MatchOrchestrator(
        matcher=slow_matcher, max_concurrent_evaluations=max_concurrency
    )

    # Submit 6 jobs simultaneously
    test_jobs = [
        JobPosting(
            id=str(i),
            title=f"Job {i}",
            organization="Org",
            url=f"https://example.com/{i}",
        )
        for i in range(6)
    ]

    results = await orchestrator.match_jobs(sample_candidate, test_jobs)

    assert len(results) == 6
    # Observed concurrency in the thread pool should never exceed the semaphore limit
    assert slow_matcher.max_observed_concurrency <= max_concurrency
