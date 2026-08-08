from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from opportunity_agent.ranking.sorter import SortStrategy


class LLMConfig(BaseModel):
    """
    Configuration settings for LLM client.
    """

    model: str = Field(default="gemini-2.5-flash")
    temperature: float = Field(default=0.0, ge=0.0, le=1.0)


class FilterConfig(BaseModel):
    """
    User-defined filtering criteria.
    """

    min_overall_score: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Minimum overall score required to pass filter.",
    )

    allowed_countries: list[str] = Field(
        default_factory=list,
        description="If set, only positions in these countries are kept.",
    )

    excluded_countries: list[str] = Field(
        default_factory=list,
        description="Positions in these countries are rejected.",
    )

    exclude_expired_deadlines: bool = Field(
        default=True,
        description="If True, positions with past deadlines are excluded.",
    )


class RankingConfig(BaseModel):
    """
    Configuration settings for the ranking pipeline.
    """

    sort_strategy: SortStrategy = Field(
        default=SortStrategy.HYBRID,
        description="Default sorting strategy for match results.",
    )
    filter: FilterConfig = Field(
        default_factory=FilterConfig,
        description="Filter criteria.",
    )


class AppConfig(BaseModel):
    """
    Master application configuration model.
    """

    llm: LLMConfig = Field(default_factory=LLMConfig)
    ranking: RankingConfig = Field(default_factory=RankingConfig)

    @classmethod
    def load_from_yaml(
        cls, config_path: str | Path = "config/config.yaml"
    ) -> AppConfig:
        """
        Loads configuration settings from a YAML file.
        Falls back to default settings if the file is missing or invalid.
        """
        path = Path(config_path)

        if not path.exists():
            return cls()

        try:
            with path.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}

            return cls(**data)

        except Exception as exc:
            raise exc
