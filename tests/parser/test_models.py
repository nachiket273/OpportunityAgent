from datetime import date

from opportunity_agent.parser.models import (
    CandidateProfile,
    Education,
    Experience,
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
