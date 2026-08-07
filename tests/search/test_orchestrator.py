from __future__ import annotations

import pytest

from opportunity_agent.llm.fake_client import FakeLLMClient
from opportunity_agent.models.candidate import CandidateProfile, Experience
from opportunity_agent.models.job import JobPosting
from opportunity_agent.models.profile import SearchProfile
from opportunity_agent.search.base import BaseSearchProvider
from opportunity_agent.search.orchestrator import OpportunitySearchOrchestrator

# ============================================================================
# Dummy Search Providers for Orchestrator Testing
# ============================================================================


class MockSuccessfulProvider(BaseSearchProvider):
    source_name = "mock_provider_1"

    async def search(self, profile: SearchProfile, limit: int = 10) -> list[JobPosting]:
        return [
            JobPosting(
                id="job-1",
                title="Quantum ML Engineer",
                organization="Max Planck Institute",
                url="https://example.com/job/1",
                source=self.source_name,
            ),
            JobPosting(
                id="job-2",
                title="Research Scientist",
                organization="CERN",
                url="https://example.com/job/2",
                source=self.source_name,
            ),
        ][:limit]


class MockDuplicateProvider(BaseSearchProvider):
    source_name = "mock_provider_2"

    async def search(self, profile: SearchProfile, limit: int = 10) -> list[JobPosting]:
        return [
            # Exact duplicate URL of job-1 from mock_provider_1
            JobPosting(
                id="job-1-dup",
                title="Quantum ML Engineer",
                organization="Max Planck Institute",
                url="https://example.com/job/1",
                source=self.source_name,
            ),
            # Unique job posting
            JobPosting(
                id="job-3",
                title="Postdoc in Quantum Computing",
                organization="ETH Zurich",
                url="https://example.com/job/3",
                source=self.source_name,
            ),
        ][:limit]


class MockFailingProvider(BaseSearchProvider):
    source_name = "failing_provider"

    async def search(self, profile: SearchProfile, limit: int = 10) -> list[JobPosting]:
        raise RuntimeError("Provider API Unavailable")


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def sample_candidate_profile() -> CandidateProfile:
    return CandidateProfile(
        name="Alice Scientist",
        location="Germany",
        experience=[Experience(title="Quantum Researcher", organization="MPI")],
        programming_languages=["Python", "C++"],
        tools=["PyTorch"],
        research_interests=["Quantum Computing"],
    )


@pytest.fixture
def sample_llm_search_response() -> dict:
    return {
        "keywords": ["Quantum Computing", "PyTorch"],
        "job_titles": ["Quantum Researcher"],
        "countries": ["Germany"],
        "job_types": ["PhD"],
        "search_queries": ["Quantum Researcher PyTorch Germany"],
    }


# ============================================================================
# Unit Tests for OpportunitySearchOrchestrator
# ============================================================================


@pytest.mark.asyncio
async def test_orchestrator_search_success(
    sample_candidate_profile: CandidateProfile,
    sample_llm_search_response: dict,
) -> None:
    """Test standard happy-path search execution across multiple providers."""
    fake_llm = FakeLLMClient(responses=[sample_llm_search_response])
    provider1 = MockSuccessfulProvider()

    orchestrator = OpportunitySearchOrchestrator(llm=fake_llm, providers=[provider1])

    search_profile, postings = await orchestrator.search_for_candidate(
        sample_candidate_profile, limit_per_provider=5
    )

    # Verify SearchProfile generation
    assert isinstance(search_profile, SearchProfile)
    assert search_profile.keywords == ["Quantum Computing", "PyTorch"]

    # Verify aggregated postings
    assert len(postings) == 2
    assert postings[0].title == "Quantum ML Engineer"
    assert postings[1].title == "Research Scientist"


@pytest.mark.asyncio
async def test_orchestrator_deduplicates_postings(
    sample_candidate_profile: CandidateProfile,
    sample_llm_search_response: dict,
) -> None:
    """
    Verify that duplicate postings across providers (by URL or title+org) are removed.
    """
    fake_llm = FakeLLMClient(responses=[sample_llm_search_response])
    provider1 = MockSuccessfulProvider()
    provider2 = MockDuplicateProvider()

    orchestrator = OpportunitySearchOrchestrator(
        llm=fake_llm, providers=[provider1, provider2]
    )

    _, postings = await orchestrator.search_for_candidate(sample_candidate_profile)

    # Provider 1 returned 2 jobs. Provider 2 returned 1 duplicate + 1 new job.
    # Total unique jobs should be 3 instead of 4.
    assert len(postings) == 3
    urls = [job.url for job in postings]
    assert urls.count("https://example.com/job/1") == 1


@pytest.mark.asyncio
async def test_orchestrator_resilience_on_provider_failure(
    sample_candidate_profile: CandidateProfile,
    sample_llm_search_response: dict,
) -> None:
    """
    Verify that if one provider fails, the orchestrator still returns
    results from healthy providers.
    """
    fake_llm = FakeLLMClient(responses=[sample_llm_search_response])
    healthy_provider = MockSuccessfulProvider()
    failing_provider = MockFailingProvider()

    orchestrator = OpportunitySearchOrchestrator(
        llm=fake_llm, providers=[healthy_provider, failing_provider]
    )

    # Execution should not raise RuntimeError from failing_provider
    search_profile, postings = await orchestrator.search_for_candidate(
        sample_candidate_profile
    )

    assert isinstance(search_profile, SearchProfile)
    assert len(postings) == 2  # Postings from healthy_provider returned successfully
    assert postings[0].source == "mock_provider_1"


def test_deduplicate_postings_fallback_key() -> None:
    """
    Verify deduplication fallback when postings
    lack URLs (deduplicates by title + organization).
    """
    fake_llm = FakeLLMClient()
    orchestrator = OpportunitySearchOrchestrator(llm=fake_llm, providers=[])

    postings_no_url = [
        JobPosting(
            id="1",
            title="Data Scientist",
            organization="Acme Corp",
            url="",
        ),
        JobPosting(
            id="2",
            title="Data Scientist",  # Same title and org, different ID and no URL
            organization="Acme Corp",
            url="",
        ),
        JobPosting(
            id="3",
            title="ML Engineer",
            organization="Acme Corp",
            url="",
        ),
    ]

    deduped = orchestrator._deduplicate_postings(postings_no_url)

    assert len(deduped) == 2
    assert deduped[0].title == "Data Scientist"
    assert deduped[1].title == "ML Engineer"
