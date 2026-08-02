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

# ==============================================================================
# Enum Tests
# ==============================================================================


def test_job_type_enum_values():
    """Verify JobType enum string representation and member values."""
    assert JobType.PHD == "PhD"
    assert JobType.ML_ENGINEER == "Machine Learning Engineer"
    assert JobType.SOFTWARE_ENGINEER == "Software Engineer"


def test_employment_type_enum_values():
    """Verify EmploymentType enum string representation and member values."""
    assert EmploymentType.FULL_TIME == "Full Time"
    assert EmploymentType.CONTRACT == "Contract"
    assert EmploymentType.INTERNSHIP == "Internship"


# ==============================================================================
# JobRequirement Tests
# ==============================================================================


def test_job_requirement_defaults():
    """Verify default values for an empty JobRequirement instance."""
    req = JobRequirement()

    assert req.required_skills == []
    assert req.preferred_skills == []
    assert req.required_degree is None
    assert req.experience_years is None
    assert req.programming_languages == []
    assert req.research_domains == []
    assert req.documents_required == []
    assert req.languages == []
    assert req.visa_sponsorship is None


def test_job_requirement_full_initialization():
    """Verify initialization of JobRequirement with populated fields."""
    skill = Skill(name="PyTorch", confidence=0.9)
    req = JobRequirement(
        required_skills=[skill],
        required_degree="Master's",
        experience_years=3,
        programming_languages=["Python", "C++"],
        visa_sponsorship=True,
    )

    assert len(req.required_skills) == 1
    assert req.required_skills[0].name == "PyTorch"
    assert req.required_degree == "Master's"
    assert req.experience_years == 3
    assert req.programming_languages == ["Python", "C++"]
    assert req.visa_sponsorship is True


def test_job_requirement_type_coercion():
    """Verify string coercion for experience years and boolean coercion
    for visa_sponsorship."""
    req = JobRequirement(experience_years="5", visa_sponsorship="True")
    assert req.experience_years == 5
    assert req.visa_sponsorship is True


def test_job_requirement_invalid_types():
    """Verify validation errors for invalid data types."""
    with pytest.raises(ValidationError):
        JobRequirement(experience_years="three")


# ==============================================================================
# JobPosting Tests
# ==============================================================================


def test_job_posting_minimal():
    """Verify JobPosting with only required fields."""
    posting = JobPosting(
        id="job_123",
        title="AI Researcher",
        organization="OpenLab",
    )

    assert posting.id == "job_123"
    assert posting.title == "AI Researcher"
    assert posting.organization == "OpenLab"
    assert posting.department is None
    assert posting.country is None
    assert posting.employment_type is None
    assert posting.job_type is None
    assert posting.url == ""
    assert posting.description == ""
    assert posting.source == ""
    assert isinstance(posting.requirements, JobRequirement)


def test_job_posting_missing_required_fields():
    """Verify that omitting required fields raises a ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        JobPosting(title="AI Researcher", organization="OpenLab")
    assert "id" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        JobPosting(id="job_123", organization="OpenLab")
    assert "title" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        JobPosting(id="job_123", title="AI Researcher")
    assert "organization" in str(exc_info.value)


def test_job_posting_enum_str_assignment():
    """Verify string assignment automatically maps to Enum fields."""
    posting = JobPosting(
        id="job_101",
        title="Postdoc Fellow",
        organization="Stanford",
        employment_type="Full Time",
        job_type="Postdoc",
    )

    assert posting.employment_type == EmploymentType.FULL_TIME
    assert posting.job_type == JobType.POSTDOC


def test_job_posting_invalid_enum_value():
    """Verify invalid Enum string values raise a ValidationError."""
    with pytest.raises(ValidationError):
        JobPosting(
            id="job_101",
            title="Dev",
            organization="TechCo",
            job_type="InvalidJobType",
        )


def test_job_posting_date_parsing():
    """Verify ISO date string parsing for deadline and posted_date."""
    posting = JobPosting(
        id="job_102",
        title="Engineer",
        organization="TechCo",
        deadline="2026-12-31",
        posted_date="2026-08-01",
    )

    assert posting.deadline == date(2026, 12, 31)
    assert posting.posted_date == date(2026, 8, 1)


def test_job_posting_nested_requirements_from_dict():
    """Verify nested JobRequirement instantiated directly from a dict."""
    data = {
        "id": "job_103",
        "title": "ML Engineer",
        "organization": "DeepData",
        "requirements": {
            "required_degree": "PhD",
            "experience_years": 2,
            "programming_languages": ["Python", "Rust"],
            "visa_sponsorship": False,
        },
    }

    posting = JobPosting(**data)
    assert isinstance(posting.requirements, JobRequirement)
    assert posting.requirements.required_degree == "PhD"
    assert posting.requirements.experience_years == 2
    assert posting.requirements.programming_languages == ["Python", "Rust"]
    assert posting.requirements.visa_sponsorship is False


def test_job_posting_serialization():
    """Verify model_dump and model_dump_json properly format enums and dates."""
    posting = JobPosting(
        id="job_104",
        title="Faculty",
        organization="MIT",
        job_type=JobType.FACULTY,
        employment_type=EmploymentType.FULL_TIME,
        posted_date=date(2026, 5, 10),
    )

    dumped = posting.model_dump()
    assert dumped["id"] == "job_104"
    assert dumped["job_type"] == "Faculty"
    assert dumped["employment_type"] == "Full Time"
    assert dumped["posted_date"] == date(2026, 5, 10)

    json_data = posting.model_dump_json()
    assert '"job_type":"Faculty"' in json_data
    assert '"posted_date":"2026-05-10"' in json_data
