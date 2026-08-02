from pydantic import BaseModel, Field

from opportunity_agent.models.job import JobPosting


class MatchResult(BaseModel):
    job: JobPosting
    overall_score: float
    skill_score: float
    education_score: float
    experience_score: float
    research_score: float
    publication_score: float

    # Default to an empty list without needing field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    missing_requirements: list[str] = Field(default_factory=list)
    reasoning: str = ""
