from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from opportunity_agent.llm.fake_client import FakeLLMClient
from opportunity_agent.models.job import JobPosting
from opportunity_agent.models.profile import SearchProfile
from opportunity_agent.search.llm_scraper import (
    LLMWebScraperProvider,
)


@pytest.fixture
def sample_search_profile() -> SearchProfile:
    return SearchProfile(
        keywords=["Python", "PyTorch", "Quantum Computing"],
        job_titles=["Research Engineer"],
        countries=["Germany"],
        job_types=["PhD"],
        search_queries=["Research Engineer Quantum Computing PyTorch"],
    )


@pytest.fixture
def sample_job_posting_dict() -> dict:
    return {
        "jobs": [
            {
                "id": "job-101",
                "title": "Quantum ML Engineer",
                "organization": "Max Planck Institute",
                "country": "Germany",
                "url": "https://example.com/jobs/101",
                "description": "Research position in quantum algorithms.",
                "source": "generic_llm_scraper",
            }
        ]
    }


# ============================================================================
# 1. Unit Tests for Helper Methods (_build_search_queries & _clean_html)
# ============================================================================


def test_build_search_queries_uses_llm_queries(
    sample_search_profile: SearchProfile,
) -> None:
    """Verify that _build_search_queries prioritizes LLM-suggested search_queries."""
    fake_llm = FakeLLMClient()
    provider = LLMWebScraperProvider(llm=fake_llm, base_url="https://example.com/jobs")

    queries = provider._build_search_queries(sample_search_profile)

    assert queries == ["Research Engineer Quantum Computing PyTorch"]


def test_build_search_queries_fallback_construction() -> None:
    """Verify fallback query construction when search_queries is empty."""
    profile_no_queries = SearchProfile(
        keywords=["Python", "PyTorch", "Quantum", "Physics"],
        job_titles=["Research Scientist"],
        job_types=["Postdoc"],
    )
    fake_llm = FakeLLMClient()
    provider = LLMWebScraperProvider(llm=fake_llm, base_url="https://example.com/jobs")

    queries = provider._build_search_queries(profile_no_queries)

    assert len(queries) == 3
    assert "Research Scientist Python PyTorch" in queries[0]
    assert "Quantum Physics" in queries[1]
    assert "Postdoc Python" in queries[2]


def test_clean_html_removes_unwanted_tags() -> None:
    """Verify that _clean_html strips scripts, styles, headers, and nav elements."""
    raw_html = """
    <html>
        <head><style>body { color: red; }</style></head>
        <body>
            <nav><a href="/home">Home</a></nav>
            <script>console.log("ignore me");</script>
            <h1>Quantum Research Scientist</h1>
            <p>We are hiring at Max Planck Institute.</p>
            <footer>Contact us</footer>
        </body>
    </html>
    """
    fake_llm = FakeLLMClient()
    provider = LLMWebScraperProvider(llm=fake_llm, base_url="https://example.com/jobs")

    cleaned_text = provider._clean_html(raw_html)

    assert "Quantum Research Scientist" in cleaned_text
    assert "Max Planck Institute" in cleaned_text
    assert "console.log" not in cleaned_text
    assert "Home" not in cleaned_text
    assert "Contact us" not in cleaned_text


# ============================================================================
# 2. Async Integration Tests for `search`
# ============================================================================


@pytest.mark.asyncio
async def test_search_success_flow(
    sample_search_profile: SearchProfile, sample_job_posting_dict: dict
) -> None:
    """Test standard execution flow mocking Playwright HTML fetching."""
    mock_html = "<html><body><h1>Quantum ML Engineer</h1></body></html>"
    fake_llm = FakeLLMClient(responses=[sample_job_posting_dict])
    provider = LLMWebScraperProvider(llm=fake_llm, base_url="https://example.com/jobs")

    # Mock _fetch_rendered_html to avoid launching real browser
    with patch.object(
        provider, "_fetch_rendered_html", new_callable=AsyncMock
    ) as mock_fetch:
        mock_fetch.return_value = mock_html

        jobs = await provider.search(sample_search_profile, limit=5)

        assert len(jobs) == 1
        assert isinstance(jobs[0], JobPosting)
        assert jobs[0].title == "Quantum ML Engineer"
        assert jobs[0].organization == "Max Planck Institute"
        assert jobs[0].source == "LLM Web Scraper"

        # Verify LLM was called with expected schema
        assert fake_llm.call_count == 1


@pytest.mark.asyncio
async def test_search_handles_empty_html(sample_search_profile: SearchProfile) -> None:
    """Verify that search returns an empty list if Playwright fails to fetch HTML."""
    fake_llm = FakeLLMClient()
    provider = LLMWebScraperProvider(llm=fake_llm, base_url="https://example.com/jobs")

    with patch.object(
        provider, "_fetch_rendered_html", new_callable=AsyncMock
    ) as mock_fetch:
        mock_fetch.return_value = ""  # Browser return empty/failed page

        jobs = await provider.search(sample_search_profile, limit=5)

        assert jobs == []
        assert fake_llm.call_count == 0  # LLM should not be called if HTML is empty


@pytest.mark.asyncio
async def test_search_handles_llm_exception(
    sample_search_profile: SearchProfile,
) -> None:
    """Verify graceful handling when LLM parsing throws an exception."""
    mock_html = "<html><body><h1>Jobs Page</h1></body></html>"
    fake_llm = FakeLLMClient(exception_to_raise=RuntimeError("LLM Parsing Failure"))
    provider = LLMWebScraperProvider(llm=fake_llm, base_url="https://example.com/jobs")

    with patch.object(
        provider, "_fetch_rendered_html", new_callable=AsyncMock
    ) as mock_fetch:
        mock_fetch.return_value = mock_html

        jobs = await provider.search(sample_search_profile, limit=5)

        # Should catch exception internally and return empty job list without raising
        assert jobs == []


@pytest.mark.asyncio
async def test_fetch_rendered_html_playwright_exception() -> None:
    """
    Verify _fetch_rendered_html catches Playwright browser exceptions and logs error.
    """
    fake_llm = FakeLLMClient()
    provider = LLMWebScraperProvider(llm=fake_llm, base_url="https://example.com/jobs")

    # Mock async_playwright context manager raising a TimeoutError
    with patch("opportunity_agent.search.llm_scraper.async_playwright") as mock_pw:
        mock_pw.side_effect = Exception("Playwright launch timeout")

        html_result = await provider._fetch_rendered_html(
            "https://example.com/jobs?q=test"
        )

        assert html_result == ""
