from __future__ import annotations

from pathlib import Path
from textwrap import dedent

from opportunity_agent.config.settings import AppConfig, FilterConfig
from opportunity_agent.ranking.sorter import SortStrategy


def test_app_config_defaults() -> None:
    """Verify default config instantiation when no YAML file is provided."""
    config = AppConfig()

    assert config.llm.model == "gemini-2.5-flash"
    assert config.ranking.sort_strategy == SortStrategy.HYBRID
    assert config.ranking.filter.min_overall_score == 0.0
    assert config.ranking.filter.exclude_expired_deadlines is True


def test_load_from_yaml_file(tmp_path: Path) -> None:
    """Verify loading settings correctly from a temporary YAML file."""
    yaml_content = dedent("""
        llm:
          model: "gemini-1.5-pro"
          temperature: 0.2

        ranking:
          sort_strategy: "SCORE"
          filter:
            min_overall_score: 75.0
            allowed_countries:
              - "Germany"
              - "Switzerland"
            excluded_countries:
              - "India"
            exclude_expired_deadlines: false
    """).strip()
    config_file = tmp_path / "config.yaml"
    config_file.write_text(yaml_content, encoding="utf-8")

    config = AppConfig.load_from_yaml(config_file)

    assert config.llm.model == "gemini-1.5-pro"
    assert config.llm.temperature == 0.2
    assert config.ranking.sort_strategy == SortStrategy.SCORE
    assert config.ranking.filter.min_overall_score == 75.0
    assert config.ranking.filter.allowed_countries == ["Germany", "Switzerland"]
    assert config.ranking.filter.excluded_countries == ["India"]
    assert config.ranking.filter.exclude_expired_deadlines is False


def test_load_from_nonexistent_file() -> None:
    """Verify fallback to defaults if config file does not exist."""
    config = AppConfig.load_from_yaml("nonexistent_path/config.yaml")

    assert config.llm.model == "gemini-2.5-flash"
    assert isinstance(config.ranking.filter, FilterConfig)
