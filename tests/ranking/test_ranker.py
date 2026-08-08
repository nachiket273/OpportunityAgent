from __future__ import annotations

from datetime import date, timedelta

from opportunity_agent.config.settings import FilterConfig, RankingConfig
from opportunity_agent.models.job import JobPosting
from opportunity_agent.models.match import MatchResult
from opportunity_agent.ranking.ranker import MatchRanker
from opportunity_agent.ranking.sorter import SortStrategy


def make_match_result(
    job_id: str,
    overall_score: float,
    country: str = "Germany",
    deadline: date | None = None,
) -> MatchResult:
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


def test_ranker_empty_input() -> None:
    """Verify MatchRanker handles empty lists cleanly."""
    ranker = MatchRanker()
    assert ranker.rank([]) == []


def test_ranker_end_to_end_pipeline() -> None:
    """Verify MatchRanker executes filtering followed by deterministic sorting."""
    today = date.today()

    matches = [
        # Job 1: Low score -> Filtered out
        make_match_result(
            "1",
            overall_score=40.0,
            country="Germany",
            deadline=today + timedelta(days=2),
        ),
        # Job 2: Wrong country -> Filtered out
        make_match_result(
            "2", overall_score=90.0, country="India", deadline=today + timedelta(days=2)
        ),
        # Job 3: Expired deadline -> Filtered out
        make_match_result(
            "3",
            overall_score=95.0,
            country="Germany",
            deadline=today - timedelta(days=1),
        ),
        # Job 4: Valid, closing in 5 days
        make_match_result(
            "4",
            overall_score=80.0,
            country="Germany",
            deadline=today + timedelta(days=5),
        ),
        # Job 5: Valid, closing in 2 days (Higher priority under HYBRID sort)
        make_match_result(
            "5",
            overall_score=85.0,
            country="Germany",
            deadline=today + timedelta(days=2),
        ),
    ]

    ranking_config = RankingConfig(
        sort_strategy=SortStrategy.HYBRID,
        filter=FilterConfig(
            min_overall_score=60.0,
            allowed_countries=["Germany"],
            exclude_expired_deadlines=True,
        ),
    )

    ranker = MatchRanker(config=ranking_config)
    ranked_results = ranker.rank(matches)

    # Asserts
    assert len(ranked_results) == 2
    ids = [res.job.id for res in ranked_results]
    assert ids == ["5", "4"]  # Job 5 (+2 days) sorted before Job 4 (+5 days)
