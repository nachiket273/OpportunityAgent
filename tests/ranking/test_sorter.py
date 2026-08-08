from __future__ import annotations

from datetime import date, timedelta

from opportunity_agent.models.job import JobPosting
from opportunity_agent.models.match import MatchResult
from opportunity_agent.ranking.sorter import MatchSorter, SortStrategy


def make_match_result(
    job_id: str,
    overall_score: float,
    deadline: date | None = None,
) -> MatchResult:
    return MatchResult(
        job=JobPosting(
            id=job_id,
            title=f"Job {job_id}",
            organization="Test Org",
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
# Sorter Edge Cases
# ============================================================================


def test_sorter_empty_list() -> None:
    """Verify sorting an empty list returns an empty list."""
    sorter = MatchSorter()
    assert sorter.sort([], strategy=SortStrategy.HYBRID) == []


# ============================================================================
# SCORE Strategy Tests
# ============================================================================


def test_sorter_score_strategy_descending() -> None:
    """Verify SCORE strategy sorts strictly by overall_score descending."""
    matches = [
        make_match_result("low", overall_score=50.0),
        make_match_result("high", overall_score=95.0),
        make_match_result("mid", overall_score=75.0),
    ]

    sorter = MatchSorter()
    sorted_matches = sorter.sort(matches, strategy=SortStrategy.SCORE)

    ids = [m.job.id for m in sorted_matches]
    assert ids == ["high", "mid", "low"]


# ============================================================================
# DEADLINE Strategy Tests
# ============================================================================


def test_sorter_deadline_strategy_ascending_with_nones_last() -> None:
    """
    Verify DEADLINE strategy places soonest deadlines first and None deadlines last.
    """
    today = date.today()
    matches = [
        make_match_result("none_1", overall_score=99.0, deadline=None),
        make_match_result(
            "far", overall_score=90.0, deadline=today + timedelta(days=30)
        ),
        make_match_result(
            "soon", overall_score=70.0, deadline=today + timedelta(days=2)
        ),
        make_match_result("none_2", overall_score=80.0, deadline=None),
    ]

    sorter = MatchSorter()
    sorted_matches = sorter.sort(matches, strategy=SortStrategy.DEADLINE)

    ids = [m.job.id for m in sorted_matches]
    assert ids[:2] == ["soon", "far"]
    assert set(ids[2:]) == {"none_1", "none_2"}


# ============================================================================
# HYBRID Strategy Tests
# ============================================================================


def test_sorter_hybrid_strategy_deadline_then_score() -> None:
    """
    Verify HYBRID strategy sorts primarily by deadline (ascending, None last)
    and secondarily by score (descending).
    """
    today = date.today()
    matches = [
        make_match_result(
            "same_date_low_score",
            overall_score=60.0,
            deadline=today + timedelta(days=5),
        ),
        make_match_result(
            "same_date_high_score",
            overall_score=90.0,
            deadline=today + timedelta(days=5),
        ),
        make_match_result(
            "sooner_date", overall_score=70.0, deadline=today + timedelta(days=2)
        ),
        make_match_result("no_deadline_high", overall_score=95.0, deadline=None),
        make_match_result("no_deadline_low", overall_score=40.0, deadline=None),
    ]

    sorter = MatchSorter()
    sorted_matches = sorter.sort(matches, strategy=SortStrategy.HYBRID)

    ids = [m.job.id for m in sorted_matches]
    expected_order = [
        "sooner_date",  # Deadline: +2 days
        "same_date_high_score",  # Deadline: +5 days, Score: 90.0
        "same_date_low_score",  # Deadline: +5 days, Score: 60.0
        "no_deadline_high",  # Deadline: None, Score: 95.0
        "no_deadline_low",  # Deadline: None, Score: 40.0
    ]
    assert ids == expected_order
