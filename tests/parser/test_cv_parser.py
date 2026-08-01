from datetime import date

import pytest

from opportunity_agent.llm.fake_client import FakeLLMClient
from opportunity_agent.parser.cv_parser import CVParser


@pytest.fixture
def sample_raw_cv_text() -> str:
    return """
    Jane Doe
    Email: jane.doe@example.com
    Phone: +1-555-0199
    Software Engineer at Tech Corp (2020 - Present)
    Skills: Python, Docker, PostgreSQL
    """


@pytest.fixture
def valid_candidate_dict() -> dict:
    return {
        "name": "Jane Doe",
        "email": "jane.doe@example.com",
        "phone": "+1-555-0199",
        "location": "New York, USA",
        "education": [],
        "experience": [
            {
                "title": "Software Engineer",
                "organization": "Tech Corp",
                "start_date": date(2020, 1, 1),
                "end_date": date(2026, 1, 1),
                "location": None,
                "description": [],
            }
        ],
        "publications": [],
        "projects": [],
        "technical_skills": [
            {"name": "Python", "category": "language", "confidence": 1.0},
            {"name": "Docker", "category": "tool", "confidence": 1.0},
        ],
        "programming_languages": ["Python"],
        "tools": ["Docker"],
        "research_interests": [],
        "certifications": [],
    }


def test_cv_parser_with_fake_llm(sample_raw_cv_text, valid_candidate_dict):
    # Prepare the fake LLM client with a pre-defined response
    fake_response = valid_candidate_dict
    fake_llm_client = FakeLLMClient(responses=[fake_response])

    # Initialize the CVParser with the fake LLM client
    cv_parser = CVParser(llm=fake_llm_client)

    # Parse the sample raw CV text
    parsed_candidate = cv_parser.parse(sample_raw_cv_text)

    # Assert that the parsed candidate matches the expected valid candidate dictionary
    assert parsed_candidate.model_dump()["profile"] == valid_candidate_dict

    # Assert that the LLM client was called exactly once
    assert fake_llm_client.call_count == 1

    # Assert that the recorded prompt and text are as expected
    assert len(fake_llm_client.recorded_prompts) == 1
    assert len(fake_llm_client.recorded_texts) == 1


def test_cv_parser_generates_warnings(sample_raw_cv_text, valid_candidate_dict):
    """Test that missing phone/email accurately triggers business logic warnings."""
    # Omit email from payload
    incomplete_dict = valid_candidate_dict.copy()
    incomplete_dict["email"] = None

    fake_client = FakeLLMClient(responses=[incomplete_dict])
    parser = CVParser(llm=fake_client)

    result = parser.parse(sample_raw_cv_text)

    assert result.is_successful is True
    assert any(
        "MISSING_DATA: No candidate email address detected." in w
        for w in result.warnings
    )


def test_cv_parser_agentic_retry(sample_raw_cv_text, valid_candidate_dict):
    """
    Test agentic behavior:
    First call returns invalid structure, second call returns corrected structure.
    """
    invalid_dict = {"invalid_schema_key": "bad data"}  # Fails Pydantic validation

    fake_client = FakeLLMClient(responses=[invalid_dict, valid_candidate_dict])
    parser = CVParser(llm=fake_client, max_retries=2)

    result = parser.parse(sample_raw_cv_text)

    # Asserts
    assert result.is_successful is True
    assert fake_client.call_count == 2  # Proves retry mechanism executed!
    # Assert that second prompt contained the reflection feedback
    assert (
        "CRITICAL: Your previous output failed validation"
        in fake_client.recorded_prompts[1]
    )


def test_cv_parser_max_retries_exceeded(sample_raw_cv_text):
    """Test graceful degradation when LLM output fails repeatedly."""
    bad_response = {
        "name": 12345
    }  # Invalid data types triggering schema error repeatedly

    fake_client = FakeLLMClient(responses=[bad_response])
    parser = CVParser(llm=fake_client, max_retries=2)

    result = parser.parse(sample_raw_cv_text)

    assert result.is_successful is False
    assert fake_client.call_count == 3  # Initial attempt + 2 retries
    assert any("Failed to parse CV" in w for w in result.warnings)
