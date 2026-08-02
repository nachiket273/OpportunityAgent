from datetime import date
from enum import Enum

from pydantic import BaseModel, Field

from opportunity_agent.models.candidate import Skill


class JobType(str, Enum):
    PHD = "PhD"
    POSTDOC = "Postdoc"
    RESEARCH_ENGINEER = "Research Engineer"
    RESEARCH_SCIENTIST = "Research Scientist"
    ML_ENGINEER = "Machine Learning Engineer"
    SOFTWARE_ENGINEER = "Software Engineer"
    FACULTY = "Faculty"
    INTERNSHIP = "Internship"
    FELLOWSHIP = "Fellowship"
    OTHER = "Other"


class EmploymentType(str, Enum):
    FULL_TIME = "Full Time"
    PART_TIME = "Part Time"
    CONTRACT = "Contract"
    TEMPORARY = "Temporary"
    INTERNSHIP = "Internship"


class JobRequirement(BaseModel):
    required_skills: list[Skill] = Field(default_factory=list)
    preferred_skills: list[Skill] = Field(default_factory=list)
    required_degree: str | None = None
    experience_years: int | None = None
    programming_languages: list[str] = Field(default_factory=list)
    research_domains: list[str] = Field(default_factory=list)
    documents_required: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    visa_sponsorship: bool | None = None


class JobPosting(BaseModel):
    id: str
    title: str
    organization: str
    department: str | None = None
    location: str | None = None
    country: str | None = None
    employment_type: EmploymentType | None = None
    job_type: JobType | None = None
    salary: str | None = None
    deadline: date | None = None
    posted_date: date | None = None
    url: str = ""
    description: str = ""
    source: str = ""
    requirements: JobRequirement = Field(default_factory=JobRequirement)
