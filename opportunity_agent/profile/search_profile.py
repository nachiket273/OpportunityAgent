from __future__ import annotations

import opportunity_agent.prompts.prompts as prompts
from opportunity_agent.llm.client import LLMClient
from opportunity_agent.models.candidate import CandidateProfile
from opportunity_agent.models.profile import SearchProfile


class SearchProfileGenerator:
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def generate(self, search_criteria: CandidateProfile) -> SearchProfile:
        """
        Generate a search profile based on the provided search criteria.

        Args:
            search_criteria (CandidateProfile): The criteria for generating
                                                the search profile.

        Returns:
            SearchProfile: The generated search profile.
        """
        profile_json = search_criteria.model_dump_json(exclude_none=True)

        try:
            raw_dict = self.llm.generate_json(
                prompt=prompts.SEARCH_PROFILE_PROMPT,
                text=profile_json,
                response_schema=SearchProfile,
            )

            return SearchProfile(**raw_dict)
        except Exception:

            fallback_keywords = (
                search_criteria.programming_languages + search_criteria.tools
            )
            primary_title = (
                search_criteria.experience[0].title
                if search_criteria.experience
                else "Researcher"
            )

            return SearchProfile(
                keywords=fallback_keywords,
                job_titles=[primary_title],
                job_types=[],
                countries=(
                    [search_criteria.location] if search_criteria.location else []
                ),
                search_queries=[
                    f"{primary_title} {' '.join(fallback_keywords[:2])}".strip(),
                    " ".join(fallback_keywords[:4]).strip(),
                ],
            )
