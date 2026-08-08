from __future__ import annotations

from datetime import date
from enum import Enum

from opportunity_agent.models.match import MatchResult


class SortStrategy(str, Enum):
    DEADLINE = "DEADLINE"
    SCORE = "SCORE"
    HYBRID = "HYBRID"


class MatchSorter:
    """Applies deterministic sorting strategies to match results."""

    def sort(
        self,
        results: list[MatchResult],
        strategy: SortStrategy = SortStrategy.HYBRID,
    ) -> list[MatchResult]:
        if not results:
            return []

        if strategy == SortStrategy.SCORE:
            # Sort strictly by overall_score descending
            return sorted(results, key=lambda r: r.overall_score, reverse=True)

        if strategy == SortStrategy.DEADLINE:
            # Sort strictly by deadline ascending (None placed last)
            return sorted(
                results,
                key=lambda r: r.job.deadline or date.max,
            )

        if strategy == SortStrategy.HYBRID:
            # Primary: Deadline ascending (None placed last)
            # Secondary: Overall score descending (-r.overall_score)
            return sorted(
                results,
                key=lambda r: (
                    r.job.deadline or date.max,
                    -r.overall_score,
                ),
            )

        return list(results)

    def _calculate_hybrid_score(self, res: MatchResult, today: date) -> float:
        """
        Calculates a composite score (0-100+):
        Base Match Score + Urgency Boost (up to +15 points for jobs
        closing within 14 days).
        """
        base_score = res.overall_score
        d = res.job.deadline

        if d is None or d < today:
            return base_score

        days_remaining = (d - today).days

        # Add urgency bonus for positions closing soon (within 14 days)
        if days_remaining <= 14:
            urgency_boost = (14 - days_remaining) * 1.0  # +1 to +14 points
            return base_score + urgency_boost

        return base_score
