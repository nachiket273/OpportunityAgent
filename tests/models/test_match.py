from datetime import date

import pytest
from pydantic import ValidationError

from opportunity_agent.models.candidate import Skill
from opportunity_agent.models.job import (
    EmploymentType,
    JobPosting,
    JobRequirement,
    JobType,
)
from opportunity_agent.models.match import MatchResult

# ==========================================
# FIXTURES
# ==========================================


@pytest.fixture
def sample_skill():
    return Skill(name="Python", category="programming", confidence=0.95)


@pytest.fixture
def sample_job_requirement(sample_skill):
    return JobRequirement(
        required_skills=[sample_skill],
        preferred_skills=[Skill(name="PyTorch", category="framework")],
        required_degree="Master's",
        experience_years=3,
        programming_languages=["Python", "C++"],
        visa_sponsorship=True,
    )


@pytest.fixture
def sample_job_posting(sample_job_requirement):
    return JobPosting(
        id="job_123",
        title="ML Engineer",
        organization="AI Corp",
        employment_type=EmploymentType.FULL_TIME,
        job_type=JobType.ML_ENGINEER,
        posted_date=date(2026, 1, 15),
        requirements=sample_job_requirement,
    )


@pytest.fixture
def sample_match_result(sample_job_posting):
    return MatchResult(
        job=sample_job_posting,
        overall_score=88.5,
        skill_score=90.0,
        education_score=100.0,
        experience_score=80.0,
        research_score=75.0,
        publication_score=0.0,
        strengths=["Strong Python background", "Relevant degree"],
        missing_requirements=["PhD preferred"],
        reasoning="Overall strong candidate with solid core skills.",
    )


# ==========================================
# TESTS FOR Skill & JobRequirement
# ==========================================


def test_skill_defaults():
    skill = Skill(name="Docker")
    assert skill.name == "Docker"
    assert skill.category is None
    assert skill.confidence == 1.0


def test_job_requirement_defaults():
    req = JobRequirement()
    assert req.required_skills == []
    assert req.preferred_skills == []
    assert req.visa_sponsorship is None


# ==========================================
# TESTS FOR JobPosting
# ==========================================


def test_job_posting_valid_instantiation(sample_job_posting):
    assert sample_job_posting.id == "job_123"
    assert sample_job_posting.job_type == JobType.ML_ENGINEER
    assert sample_job_posting.job_type.value == "Machine Learning Engineer"
    assert sample_job_posting.requirements.required_skills[0].name == "Python"


def test_job_posting_invalid_enum():
    with pytest.raises(ValidationError) as exc_info:
        JobPosting(
            id="job_999",
            title="DevOps",
            organization="Tech Co",
            job_type="InvalidJobType",  # Should trigger validation error
        )
    assert "job_type" in str(exc_info.value)


def test_job_posting_date_coercion():
    # Pydantic automatically parses valid ISO date strings into date objects
    job = JobPosting(
        id="job_456",
        title="Data Scientist",
        organization="Data Inc",
        posted_date="2026-02-10",
    )
    assert job.posted_date == date(2026, 2, 10)


# ==========================================
# TESTS FOR MatchResult
# ==========================================


def test_match_result_valid_instantiation(sample_match_result):
    assert sample_match_result.overall_score == 88.5
    assert len(sample_match_result.strengths) == 2
    assert sample_match_result.job.title == "ML Engineer"


def test_match_result_defaults(sample_job_posting):
    result = MatchResult(
        job=sample_job_posting,
        overall_score=70.0,
        skill_score=70.0,
        education_score=70.0,
        experience_score=70.0,
        research_score=70.0,
        publication_score=70.0,
    )
    # Check default factories and string assignments
    assert result.strengths == []
    assert result.missing_requirements == []
    assert result.reasoning == ""


def test_match_result_missing_required_fields():
    with pytest.raises(ValidationError) as exc_info:
        MatchResult(overall_score=90.0)  # Missing 'job' and all specific scores

    errors = exc_info.value.errors()
    field_names = [err["loc"][0] for err in errors]

    assert "job" in field_names
    assert "skill_score" in field_names
    assert "education_score" in field_names


def test_match_result_type_coercion(sample_job_posting):
    # Pydantic converts valid numeric strings to floats automatically
    result = MatchResult(
        job=sample_job_posting,
        overall_score="85.5",  # Passed as string
        skill_score=80,  # Passed as int
        education_score=90.0,
        experience_score=85.0,
        research_score=70.0,
        publication_score=50.0,
    )
    assert isinstance(result.overall_score, float)
    assert result.overall_score == 85.5
    assert isinstance(result.skill_score, float)


# ==========================================
# SERIALIZATION & DESERIALIZATION TESTS
# ==========================================


def test_serialization_and_deserialization(sample_match_result):
    # Test converting to dict and back
    data_dict = sample_match_result.model_dump()
    reconstructed = MatchResult.model_validate(data_dict)
    assert reconstructed == sample_match_result

    # Test converting to JSON and back
    json_data = sample_match_result.model_dump_json()
    reconstructed_from_json = MatchResult.model_validate_json(json_data)
    assert reconstructed_from_json == sample_match_result
