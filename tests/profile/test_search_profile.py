from __future__ import annotations

import json

import pytest

from opportunity_agent.llm.fake_client import FakeLLMClient
from opportunity_agent.models.candidate import CandidateProfile, Experience
from opportunity_agent.profile.search_profile import SearchProfileGenerator
from opportunity_agent.search.base import SearchProfile


@pytest.fixture
def sample_candidate_profile() -> CandidateProfile:
    return CandidateProfile(
        name="Alice Scientist",
        email="alice@example.com",
        location="Germany",
        experience=[
            Experience(
                title="Quantum Researcher",
                organization="Max Planck Institute",
                start_date=None,
                end_date=None,
            )
        ],
        programming_languages=["Python", "C++"],
        tools=["PyTorch", "Qiskit"],
        research_interests=["Quantum Computing", "Many-Body Physics"],
    )


@pytest.fixture
def sample_llm_search_response() -> dict:
    return {
        "keywords": ["Quantum Computing", "Qiskit", "PyTorch"],
        "job_titles": ["Quantum Researcher", "Research Engineer"],
        "countries": ["Germany", "Switzerland"],
        "job_types": ["PhD", "Postdoc"],
        "search_queries": [
            "Quantum Researcher PyTorch Qiskit",
            "Quantum Computing Research Engineer Germany",
        ],
    }


def test_generate_search_profile_success(
    sample_candidate_profile: CandidateProfile,
    sample_llm_search_response: dict,
) -> None:
    """Test standard happy-path conversion from CandidateProfile to SearchProfile."""
    fake_llm = FakeLLMClient(responses=[sample_llm_search_response])
    generator = SearchProfileGenerator(llm=fake_llm)

    search_profile = generator.generate(sample_candidate_profile)

    # Asserts on returned model
    assert isinstance(search_profile, SearchProfile)
    assert search_profile.keywords == ["Quantum Computing", "Qiskit", "PyTorch"]
    assert search_profile.job_titles == ["Quantum Researcher", "Research Engineer"]
    assert search_profile.countries == ["Germany", "Switzerland"]
    assert len(search_profile.search_queries) == 2

    # Asserts on LLM interaction
    assert fake_llm.call_count == 1
    assert "Alice Scientist" in fake_llm.recorded_texts[0]


def test_generate_search_profile_passes_schema_and_prompt(
    sample_candidate_profile: CandidateProfile,
    sample_llm_search_response: dict,
) -> None:
    """Verify that the generator correctly dumps candidate JSON into the LLM call."""
    fake_llm = FakeLLMClient(responses=[sample_llm_search_response])
    generator = SearchProfileGenerator(llm=fake_llm)

    generator.generate(sample_candidate_profile)

    # Check that candidate's JSON payload excludes nulls/defaults cleanly
    passed_text = fake_llm.recorded_texts[0]
    candidate_dict = json.loads(passed_text)

    assert candidate_dict["name"] == "Alice Scientist"
    assert "Python" in candidate_dict["programming_languages"]


def test_generate_search_profile_llm_exception_fallback(
    sample_candidate_profile: CandidateProfile,
) -> None:
    """Test that when LLM throws an exception, the generator falls back safely."""
    fake_llm = FakeLLMClient(exception_to_raise=RuntimeError("API Service Unavailable"))
    generator = SearchProfileGenerator(llm=fake_llm)

    search_profile = generator.generate(sample_candidate_profile)
    print(search_profile)

    # Asserts fallback behavior
    assert isinstance(search_profile, SearchProfile)
    assert search_profile.keywords == [
        "Python",
        "C++",
        "PyTorch",
        "Qiskit",
        "Quantum Computing",
        "Many-Body Physics",
    ]
    assert search_profile.job_titles == ["Quantum Researcher"]
    assert search_profile.countries == ["Germany"]
    assert len(search_profile.search_queries) == 2
    assert "Quantum Researcher Python C++" in search_profile.search_queries[0]


def test_generate_search_profile_invalid_llm_data_fallback(
    sample_candidate_profile: CandidateProfile,
) -> None:
    """Test fallback execution when LLM returns malformed data structure."""
    bad_response = {"keywords": "Not a list, invalid data type"}
    fake_llm = FakeLLMClient(responses=[bad_response])
    generator = SearchProfileGenerator(llm=fake_llm)

    search_profile = generator.generate(sample_candidate_profile)

    # Generator catches Pydantic ValidationError and uses fallback logic
    assert isinstance(search_profile, SearchProfile)
    assert "Python" in search_profile.keywords
    assert search_profile.job_titles == ["Quantum Researcher"]


def test_fallback_handles_empty_candidate_fields() -> None:
    """Test fallback mechanism when candidate has missing location and experience."""
    minimal_candidate = CandidateProfile(name="John Doe")
    fake_llm = FakeLLMClient(exception_to_raise=TimeoutError("Request Timeout"))
    generator = SearchProfileGenerator(llm=fake_llm)

    search_profile = generator.generate(minimal_candidate)

    assert isinstance(search_profile, SearchProfile)
    assert search_profile.keywords == []
    assert search_profile.job_titles == ["Researcher"]  # Default fallback title
    assert search_profile.countries == []
    assert search_profile.search_queries == ["Researcher"]
