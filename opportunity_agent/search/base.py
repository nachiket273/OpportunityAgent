from __future__ import annotations

from abc import ABC, abstractmethod

from opportunity_agent.models.job import JobPosting
from opportunity_agent.models.profile import SearchProfile


class BaseSearchProvider(ABC):
    """
    Abstract base class for search providers. All search providers should inherit from
    this class and implement the `search` method.
    """

    source_name: str

    @abstractmethod
    async def search(self, profile: SearchProfile, limit: int = 10) -> list[JobPosting]:
        """
        Perform a search based on the provided SearchProfile.

        Args:
            profile (SearchProfile): The search profile containing criteria
                                     for the search.
            limit (int): The maximum number of job postings to return.

        Returns:
            list[JobPosting]: A list of job postings matching the search criteria.
        """
        pass
