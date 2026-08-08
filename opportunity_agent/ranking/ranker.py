from __future__ import annotations

from opportunity_agent.config.settings import RankingConfig
from opportunity_agent.models.match import MatchResult
from opportunity_agent.ranking.filter import MatchFilter
from opportunity_agent.ranking.sorter import MatchSorter


class MatchRanker:
    """Orchestrates filtering and sorting of job match results."""

    def __init__(self, config: RankingConfig | None = None) -> None:
        self.config = config or RankingConfig()
        self.filter_engine = MatchFilter(config=self.config.filter)
        self.sorter_engine = MatchSorter()

    def rank(self, results: list[MatchResult]) -> list[MatchResult]:
        """
        Executes the ranking pipeline: Filter -> Sort.

        Args:
            results: Raw list of MatchResult objects.

        Returns:
            list[MatchResult]: Filtered and deterministically sorted results.
        """
        # 1. Filter results based on config criteria
        filtered_results = self.filter_engine.filter(results)

        # 2. Sort filtered results using chosen strategy
        ranked_results = self.sorter_engine.sort(
            filtered_results, strategy=self.config.sort_strategy
        )

        return ranked_results
