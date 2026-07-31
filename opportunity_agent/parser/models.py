from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass(slots=True)
class Education:
    degree: str
    institution: str
    start_year: int | None = None
    end_year: int | None = None
    grade: str | None = None
    specialization: str | None = None


@dataclass(slots=True)
class Experience:
    title: str
    organization: str
    start_date: date | None = None
    end_date: date | None = None
    location: str | None = None
    description: list[str] = field(default_factory=list)


@dataclass(slots=True)
class Publication:
    title: str
    authors: list[str]
    venue: str | None = None
    year: int | None = None
    doi: str | None = None
    url: str | None = None


@dataclass(slots=True)
class Project:
    title: str
    description: str
    technologies: list[str] = field(default_factory=list)
    url: str | None = None


@dataclass(slots=True)
class Skill:
    name: str
    category: str | None = None  # programming, framework, research, tool, language
    confidence: float = 1.0


@dataclass(slots=True)
class CandidateProfile:
    name: str
    email: str | None = None
    phone: str | None = None
    location: str | None = None

    education: list[Education] = field(default_factory=list)
    experience: list[Experience] = field(default_factory=list)
    publications: list[Publication] = field(default_factory=list)
    projects: list[Project] = field(default_factory=list)

    technical_skills: list[Skill] = field(default_factory=list)
    programming_languages: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    research_interests: list[str] = field(default_factory=list)
    certifications: list[str] = field(default_factory=list)
