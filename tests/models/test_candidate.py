from datetime import date

import pytest
from pydantic import ValidationError

from opportunity_agent.models.candidate import (
    CandidateProfile,
    Education,
    Experience,
    ParsedDocument,
    ParsedResult,
    Project,
    Publication,
    Skill,
)


def test_create_empty_candidate_profile():
    profile = CandidateProfile(name="John Doe")

    assert profile.name == "John Doe"
    assert profile.email is None
    assert profile.education == []
    assert profile.publications == []
    assert profile.projects == []
    assert profile.technical_skills == []
    assert profile.programming_languages == []
    assert profile.tools == []
    assert profile.research_interests == []
    assert profile.certifications == []


def test_add_education():
    profile = CandidateProfile(name="John Doe")

    profile.education.append(
        Education(
            degree="MS",
            institution="MIT",
            start_year=2022,
            end_year=2024,
            grade="A",
            specialization="Physics",
        )
    )

    assert len(profile.education) == 1
    assert profile.education[0].degree == "MS"
    assert profile.education[0].institution == "MIT"
    assert profile.education[0].start_year == 2022
    assert profile.education[0].end_year == 2024
    assert profile.education[0].grade == "A"
    assert profile.education[0].specialization == "Physics"


def test_add_experience():
    profile = CandidateProfile(name="John Doe")

    profile.experience.append(
        Experience(
            title="Software Engineer",
            organization="Dummy Inc",
            start_date=date(2024, 10, 1),
            end_date=date(2026, 2, 1),
        )
    )

    assert profile.experience[0].title == "Software Engineer"
    assert profile.experience[0].organization == "Dummy Inc"
    assert profile.experience[0].start_date == date(2024, 10, 1)
    assert profile.experience[0].end_date == date(2026, 2, 1)
    assert profile.experience[0].location is None


def test_add_publication():
    publication = Publication(
        title="AI for Science",
        authors=["John Doe", "Jane Doe"],
        venue="Nature",
        year=2025,
    )

    assert publication.year == 2025
    assert len(publication.authors) == 2
    assert publication.title == "AI for Science"
    assert publication.venue == "Nature"


def test_add_project():
    project = Project(
        title="OpportunityAgent",
        description="Autonomous job discovery",
        technologies=["Python", "LLM"],
    )

    assert "Python" in project.technologies
    assert "LLM" in project.technologies
    assert project.title == "OpportunityAgent"
    assert project.description == "Autonomous job discovery"


def test_lists_are_not_shared_between_instances():
    p1 = CandidateProfile(name="Alice")
    p2 = CandidateProfile(name="Bob")

    py_skill = Skill(name="Python", confidence=7)

    p1.technical_skills.append(py_skill)

    assert p2.technical_skills == []
    assert len(p1.technical_skills) == 1
    assert p1.technical_skills[0].name == "Python"
    assert p1.technical_skills[0].confidence == 7


def test_parsed_document():
    doc = ParsedDocument(text="Sample text", page_count=5)

    assert doc.text == "Sample text"
    assert doc.page_count == 5


def test_parsed_result():
    profile = CandidateProfile(name="John Doe")
    result = ParsedResult(profile=profile, warnings=["Warning 1"], is_successful=True)

    assert result.profile.name == "John Doe"
    assert result.warnings == ["Warning 1"]
    assert result.is_successful is True


def test_education_minimal():
    edu = Education(degree="BS", institution="MIT")
    assert edu.degree == "BS"
    assert edu.institution == "MIT"
    assert edu.start_year is None
    assert edu.end_year is None
    assert edu.grade is None
    assert edu.specialization is None


def test_education_missing_required_fields():
    with pytest.raises(ValidationError) as exc_info:
        Education(degree="BS")  # missing institution
    assert "institution" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        Education(institution="MIT")  # missing degree
    assert "degree" in str(exc_info.value)


def test_education_type_coercion():
    # Pydantic automatically coerces compatible string numbers to int
    edu = Education(degree="BS", institution="MIT", start_year="2018", end_year="2022")
    assert edu.start_year == 2018
    assert edu.end_year == 2022


def test_education_invalid_type():
    with pytest.raises(ValidationError):
        Education(degree="BS", institution="MIT", start_year="not-a-year")


def test_experience_minimal():
    exp = Experience(title="Dev", organization="TechCorp")
    assert exp.title == "Dev"
    assert exp.organization == "TechCorp"
    assert exp.start_date is None
    assert exp.end_date is None
    assert exp.location is None
    assert exp.description == []


def test_experience_date_string_parsing():
    # Pydantic parses valid ISO date strings into datetime.date objects
    exp = Experience(
        title="Dev",
        organization="TechCorp",
        start_date="2022-01-15",
        end_date="2023-12-31",
    )
    assert exp.start_date == date(2022, 1, 15)
    assert exp.end_date == date(2023, 12, 31)


def test_experience_invalid_date_format():
    with pytest.raises(ValidationError):
        Experience(title="Dev", organization="TechCorp", start_date="15/01/2022")


def test_experience_missing_required():
    with pytest.raises(ValidationError):
        Experience(title="Dev")


def test_publication_minimal():
    pub = Publication(title="Paper", authors=["Author A"])
    assert pub.title == "Paper"
    assert pub.authors == ["Author A"]
    assert pub.venue is None
    assert pub.year is None
    assert pub.doi is None
    assert pub.url is None


def test_publication_missing_authors():
    with pytest.raises(ValidationError):
        Publication(title="Paper")


def test_project_minimal():
    proj = Project(title="App", description="A cool app")
    assert proj.title == "App"
    assert proj.description == "A cool app"
    assert proj.technologies == []
    assert proj.url is None


def test_project_missing_description():
    with pytest.raises(ValidationError):
        Project(title="App")


def test_skill_defaults():
    skill = Skill(name="Python")
    assert skill.name == "Python"
    assert skill.category is None
    assert skill.confidence == 1.0


def test_skill_type_coercion():
    skill = Skill(name="Python", confidence="0.85")
    assert skill.confidence == 0.85
    assert isinstance(skill.confidence, float)


def test_skill_invalid_confidence():
    with pytest.raises(ValidationError):
        Skill(name="Python", confidence="high")


def test_candidate_profile_from_dict():
    raw_data = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "education": [{"degree": "BSc", "institution": "Oxford"}],
        "technical_skills": [{"name": "Python", "confidence": 0.9}],
        "programming_languages": ["Python", "Rust"],
    }
    profile = CandidateProfile(**raw_data)
    assert profile.name == "Jane Doe"
    assert profile.email == "jane@example.com"
    assert len(profile.education) == 1
    assert profile.education[0].degree == "BSc"
    assert profile.technical_skills[0].confidence == 0.9
    assert "Rust" in profile.programming_languages


def test_candidate_profile_nested_validation_error():
    # Passing invalid nested object inside education list
    raw_data = {
        "name": "Jane Doe",
        "education": [{"degree": "BSc"}],  # Missing required 'institution'
    }
    with pytest.raises(ValidationError) as exc_info:
        CandidateProfile(**raw_data)
    assert "education.0.institution" in str(exc_info.value) or "institution" in str(
        exc_info.value
    )


def test_candidate_profile_serialization():
    profile = CandidateProfile(
        name="John",
        programming_languages=["Python", "C++"],
    )
    dumped = profile.model_dump()
    assert dumped["name"] == "John"
    assert dumped["programming_languages"] == ["Python", "C++"]
    assert dumped["email"] is None


def test_parsed_document_validation():
    doc = ParsedDocument(text="Hello", page_count=2)
    assert doc.text == "Hello"
    assert doc.page_count == 2

    with pytest.raises(ValidationError):
        ParsedDocument(text="Hello", page_count="invalid_int")


def test_parsed_result_defaults():
    profile = CandidateProfile(name="John Doe")
    result = ParsedResult(profile=profile)

    assert result.is_successful is True
    assert result.warnings == []
    assert result.profile.name == "John Doe"


def test_parsed_result_from_nested_dict():
    data = {
        "profile": {"name": "Alice Smith"},
        "warnings": ["Low confidence on experience extraction"],
        "is_successful": True,
    }
    result = ParsedResult(**data)
    assert isinstance(result.profile, CandidateProfile)
    assert result.profile.name == "Alice Smith"
    assert len(result.warnings) == 1
