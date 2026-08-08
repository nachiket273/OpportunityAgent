from __future__ import annotations

from datetime import date

from opportunity_agent.config.settings import FilterConfig
from opportunity_agent.models.match import MatchResult


class MatchFilter:
    """
    Filters MatchResult objects against configured rules.
    """

    def __init__(self, config: FilterConfig | None = None) -> None:
        self.config = config or FilterConfig()

    def filter(self, results: list[MatchResult]) -> list[MatchResult]:
        """
        Filters match results according to criteria in FilterConfig.
        """
        if not results:
            return []

        today = date.today()
        filtered_results: list[MatchResult] = []

        for res in results:
            if self._is_match_valid(res, today):
                filtered_results.append(res)

        return filtered_results

    def _is_match_valid(self, res: MatchResult, today: date) -> bool:
        job = res.job

        if res.overall_score < self.config.min_overall_score:
            return False

        if self.config.allowed_countries:
            allowed_upper = [c.upper() for c in self.config.allowed_countries]
            if not job.country or job.country.upper() not in allowed_upper:
                return False

        if self.config.excluded_countries:
            excluded_upper = [c.upper() for c in self.config.excluded_countries]
            if job.country and job.country.upper() in excluded_upper:
                return False

        if self.config.exclude_expired_deadlines and job.deadline:
            if job.deadline < today:
                return False

        return True
