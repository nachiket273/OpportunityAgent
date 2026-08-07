from __future__ import annotations

import pytest

from opportunity_agent.llm.fake_client import FakeLLMClient
from opportunity_agent.matcher.llm_matcher import LLMMatcher
from opportunity_agent.models.candidate import CandidateProfile, Experience
from opportunity_agent.models.job import JobPosting, JobType
from opportunity_agent.models.match import MatchResult


@pytest.fixture
def sample_candidate() -> CandidateProfile:
    return CandidateProfile(
        name="Alice Scientist",
        experience=[Experience(title="Quantum Researcher", organization="MPI")],
        programming_languages=["Python", "C++"],
        tools=["PyTorch", "Qiskit"],
        research_interests=["Quantum Computing"],
    )


@pytest.fixture
def sample_job() -> JobPosting:
    return JobPosting(
        id="job-101",
        title="Quantum Machine Learning Engineer",
        organization="Max Planck Institute",
        url="https://example.com/job/101",
        description="Seeking researcher with strong Python and Qiskit experience.",
        job_type=JobType.RESEARCH_ENGINEER,
    )


@pytest.fixture
def sample_match_llm_response() -> dict:
    return {
        "overall_score": 91.0,
        "skill_score": 88.0,
        "education_score": 100.0,
        "experience_score": 90.0,
        "research_score": 95.0,
        "publication_score": 82.0,
        "strengths": [
            "Strong Quantum Computing background",
            "Proficient in Python and Qiskit",
        ],
        "missing_requirements": ["CUDA"],
        "reasoning": "Excellent fit for Quantum ML Engineer position."
        "Strong skills in PyTorch and Qiskit.",
    }


def test_llm_matcher_success_flow(
    sample_candidate: CandidateProfile,
    sample_job: JobPosting,
    sample_match_llm_response: dict,
) -> None:
    """Test successful match evaluation using FakeLLMClient."""
    fake_llm = FakeLLMClient(responses=[sample_match_llm_response])
    matcher = LLMMatcher(llm=fake_llm)

    result = matcher.match(sample_candidate, sample_job)

    # Asserts on returned MatchResult
    assert isinstance(result, MatchResult)
    assert result.job.id == "job-101"
    assert result.overall_score == 91.0
    assert result.education_score == 100.0
    assert "CUDA" in result.missing_requirements
    assert "Strong Quantum Computing background" in result.strengths
    assert "Excellent fit" in result.reasoning

    # Verify LLM interaction
    assert fake_llm.call_count == 1
    assert "Alice Scientist" in fake_llm.recorded_texts[0]
    assert "Quantum Machine Learning Engineer" in fake_llm.recorded_texts[0]


def test_llm_matcher_handles_exception(
    sample_candidate: CandidateProfile,
    sample_job: JobPosting,
) -> None:
    """Test that LLMMatcher degrades gracefully when LLM fails."""
    fake_llm = FakeLLMClient(exception_to_raise=RuntimeError("LLM Service Timeout"))
    matcher = LLMMatcher(llm=fake_llm)

    result = matcher.match(sample_candidate, sample_job)

    assert isinstance(result, MatchResult)
    assert result.overall_score == 0.0
    assert "Unable to complete automated evaluation" in result.missing_requirements
    assert "Evaluation failed due to error" in result.reasoning
