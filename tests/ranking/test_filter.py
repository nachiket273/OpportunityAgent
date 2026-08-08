from __future__ import annotations

from datetime import date, timedelta

from opportunity_agent.config.settings import FilterConfig
from opportunity_agent.models.job import JobPosting
from opportunity_agent.models.match import MatchResult
from opportunity_agent.ranking.filter import MatchFilter


def make_match_result(
    job_id: str,
    overall_score: float,
    country: str | None = None,
    deadline: date | None = None,
) -> MatchResult:
    """Helper factory to build minimalist MatchResult objects for testing."""
    return MatchResult(
        job=JobPosting(
            id=job_id,
            title=f"Job {job_id}",
            organization="Test Org",
            country=country,
            deadline=deadline,
            url=f"https://example.com/{job_id}",
        ),
        overall_score=overall_score,
        skill_score=overall_score,
        education_score=overall_score,
        experience_score=overall_score,
        research_score=overall_score,
        publication_score=overall_score,
    )


# ============================================================================
# Edge Cases & Empty Inputs
# ============================================================================


def test_filter_empty_list() -> None:
    """Verify that filtering an empty list returns an empty list."""
    match_filter = MatchFilter()
    assert match_filter.filter([]) == []


def test_filter_default_config_allows_all_valid_active_matches() -> None:
    """
    Verify default FilterConfig allows matches with scores >= 0 and future deadlines.
    """
    today = date.today()
    matches = [
        make_match_result(
            "1",
            overall_score=50.0,
            country="Germany",
            deadline=today + timedelta(days=10),
        ),
        make_match_result("2", overall_score=0.0, country="USA", deadline=None),
    ]

    match_filter = MatchFilter(config=FilterConfig())
    filtered = match_filter.filter(matches)

    assert len(filtered) == 2


# ============================================================================
# Score Threshold Filter Tests
# ============================================================================


def test_filter_min_overall_score_boundary() -> None:
    """Verify exact boundary behavior for min_overall_score."""
    matches = [
        make_match_result("low", overall_score=59.9),
        make_match_result("exact", overall_score=60.0),
        make_match_result("high", overall_score=60.1),
    ]

    config = FilterConfig(min_overall_score=60.0, exclude_expired_deadlines=False)
    match_filter = MatchFilter(config=config)
    filtered = match_filter.filter(matches)

    ids = [m.job.id for m in filtered]
    assert ids == ["exact", "high"]


# ============================================================================
# Country Filtering Tests
# ============================================================================


def test_filter_allowed_countries_case_insensitive() -> None:
    """
    Verify allowed_countries matches case-insensitively
    and rejects missing/other countries.
    """
    matches = [
        make_match_result("1", overall_score=80.0, country="germany"),
        make_match_result("2", overall_score=80.0, country="SWITZERLAND"),
        make_match_result("3", overall_score=80.0, country="France"),
        make_match_result("4", overall_score=80.0, country=None),  # Missing country
    ]

    config = FilterConfig(
        allowed_countries=["Germany", "Switzerland"],
        exclude_expired_deadlines=False,
    )
    match_filter = MatchFilter(config=config)
    filtered = match_filter.filter(matches)

    ids = [m.job.id for m in filtered]
    assert ids == ["1", "2"]


def test_filter_excluded_countries_case_insensitive() -> None:
    """Verify excluded_countries rejects matching countries regardless of case."""
    matches = [
        make_match_result("1", overall_score=80.0, country="India"),
        make_match_result("2", overall_score=80.0, country="INDIA"),
        make_match_result("3", overall_score=80.0, country="Germany"),
        make_match_result("4", overall_score=80.0, country=None),
    ]

    config = FilterConfig(
        excluded_countries=["india"],
        exclude_expired_deadlines=False,
    )
    match_filter = MatchFilter(config=config)
    filtered = match_filter.filter(matches)

    ids = [m.job.id for m in filtered]
    assert ids == ["3", "4"]


# ============================================================================
# Deadline Filter Tests
# ============================================================================


def test_filter_exclude_expired_deadlines() -> None:
    """
    Verify past deadlines are excluded while today, future, and None deadlines are kept.
    """
    today = date.today()
    matches = [
        make_match_result(
            "past", overall_score=80.0, deadline=today - timedelta(days=1)
        ),
        make_match_result("today", overall_score=80.0, deadline=today),
        make_match_result(
            "future", overall_score=80.0, deadline=today + timedelta(days=5)
        ),
        make_match_result("none", overall_score=80.0, deadline=None),
    ]

    config = FilterConfig(exclude_expired_deadlines=True)
    match_filter = MatchFilter(config=config)
    filtered = match_filter.filter(matches)

    ids = [m.job.id for m in filtered]
    assert ids == ["today", "future", "none"]


def test_filter_include_expired_deadlines_when_flag_false() -> None:
    """Verify past deadlines are retained if exclude_expired_deadlines is False."""
    today = date.today()
    matches = [
        make_match_result(
            "past", overall_score=80.0, deadline=today - timedelta(days=1)
        ),
    ]

    config = FilterConfig(exclude_expired_deadlines=False)
    match_filter = MatchFilter(config=config)
    filtered = match_filter.filter(matches)

    assert len(filtered) == 1
