from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class Education(BaseModel):
    degree: str
    institution: str
    start_year: int | None = None
    end_year: int | None = None
    grade: str | None = None
    specialization: str | None = None


class Experience(BaseModel):
    title: str
    organization: str
    start_date: date | None = None
    end_date: date | None = None
    location: str | None = None
    description: list[str] = Field(default_factory=list)


class Publication(BaseModel):
    title: str
    authors: list[str]
    venue: str | None = None
    year: int | None = None
    doi: str | None = None
    url: str | None = None


class Project(BaseModel):
    title: str
    description: str
    technologies: list[str] = Field(default_factory=list)
    url: str | None = None


class Skill(BaseModel):
    name: str
    category: str | None = (
        None  # programming, framework, research, tool, language, database, cloud
    )
    confidence: float = 1.0


class CandidateProfile(BaseModel):
    name: str
    email: str | None = None
    phone: str | None = None
    location: str | None = None

    education: list[Education] = Field(default_factory=list)
    experience: list[Experience] = Field(default_factory=list)
    publications: list[Publication] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)

    technical_skills: list[Skill] = Field(default_factory=list)
    programming_languages: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    research_interests: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)


class ParsedDocument(BaseModel):
    text: str
    page_count: int


class ParsedResult(BaseModel):
    profile: CandidateProfile
    warnings: list[str] = Field(default_factory=list)
    is_successful: bool = True
