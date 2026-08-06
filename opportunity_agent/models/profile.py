from __future__ import annotations

from pydantic import BaseModel, Field


class SearchProfile(BaseModel):
    keywords: list[str] = Field(
        default_factory=list,
        description="List of keywords to search for in candidate profiles.",
    )
    job_titles: list[str] = Field(
        default_factory=list,
        description="List of job titles to search for in candidate profiles.",
    )
    countries: list[str] = Field(
        default_factory=list,
        description="List of countries to filter candidate profiles by location.",
    )
    job_types: list[str] = Field(
        default_factory=list,
        description="List of job types (e.g., full-time, part-time, contract) to filter"
        "candidate profiles.",
    )
    search_queries: list[str] = Field(
        default_factory=list,
        description=(
            "3 to 5 distinct, highly-targeted search engine query strings "
            "(e.g., ['Quantum Computing Research Engineer',"
            "'PyTorch Machine Learning PhD'])."
        ),
    )
