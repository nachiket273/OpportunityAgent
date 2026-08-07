from __future__ import annotations

import asyncio

from opportunity_agent.llm.client import LLMClient
from opportunity_agent.models.candidate import CandidateProfile
from opportunity_agent.models.job import JobPosting
from opportunity_agent.models.profile import SearchProfile
from opportunity_agent.profile.search_profile import SearchProfileGenerator
from opportunity_agent.search.base import BaseSearchProvider


class OpportunitySearchOrchestrator:
    """
    Orchestrates transformation and concurrent multi-provider job searching.
    """

    def __init__(self, llm: LLMClient, providers: list[BaseSearchProvider]) -> None:
        self.profile_generator = SearchProfileGenerator(llm)
        self.providers = providers

    async def search_for_candidate(
        self, candidate: CandidateProfile, limit_per_provider: int = 5
    ) -> tuple[SearchProfile, list[JobPosting]]:
        """
        1. Generates SearchProfile from CandidateProfile.
        2. Executes searches in parallel across all registered providers.
        3. Deduplicates postings.
        """
        search_profile = self.profile_generator.generate(candidate)

        tasks = [
            provider.search(search_profile, limit=limit_per_provider)
            for provider in self.providers
        ]
        results_nested = await asyncio.gather(*tasks, return_exceptions=True)

        all_postings: list[JobPosting] = []
        for res in results_nested:
            if isinstance(res, list):
                all_postings.extend(res)

        deduped = self._deduplicate_postings(all_postings)
        return search_profile, deduped

    def _deduplicate_postings(self, postings: list[JobPosting]) -> list[JobPosting]:
        seen_keys = set()
        deduped_list = []
        for post in postings:
            key = (
                post.url.strip()
                if post.url
                else f"{post.title.lower()}-{post.organization.lower()}"
            )
            if key not in seen_keys:
                seen_keys.add(key)
                deduped_list.append(post)

        return deduped_list
