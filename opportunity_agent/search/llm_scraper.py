from __future__ import annotations

import asyncio
from urllib.parse import quote_plus

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from pydantic import BaseModel, Field

import opportunity_agent.prompts.prompts as prompts
from opportunity_agent.llm.client import LLMClient
from opportunity_agent.models.job import JobPosting
from opportunity_agent.models.profile import SearchProfile
from opportunity_agent.search.base import BaseSearchProvider


class JobPostingList(BaseModel):
    jobs: list[JobPosting] = Field(
        default_factory=list, description="List of job postings"
    )


class LLMWebScraperProvider(BaseSearchProvider):
    """
    Generic search provider that uses a Playwright for JS execution.
    BeautifulSoup for HTML parsing, and an LLM for extracting job postings from
    the HTML content.
    """

    source_name: str = "LLM Web Scraper"

    def __init__(
        self,
        llm: LLMClient,
        base_url: str,
        query_param_name: str = "q",
        max_concurrent_queries: int = 3,
    ) -> None:
        self.llm = llm
        self.base_url = base_url
        self.query_param_name = query_param_name
        self.max_concurrent_queries = max_concurrent_queries

    async def search(self, profile: SearchProfile, limit: int = 10) -> list[JobPosting]:
        """
        Perform a search for job postings based on the provided search profile.

        Args:
            profile (SearchProfile): The search profile containing search criteria.
            limit (int): The maximum number of job postings to return.
        """
        search_queries = self._build_search_queries(profile)

        # Limit total web requests to avoid rate limits
        selected_queries = search_queries[: self.max_concurrent_queries]

        # Execute web searched concurrently.
        tasks = [self._search_single_query(q, limit=limit) for q in selected_queries]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        aggregated_jobs: list[JobPosting] = []

        for query_result in results:
            if isinstance(query_result, list):
                aggregated_jobs.extend(query_result)

        return aggregated_jobs

    def _build_search_queries(self, profile: SearchProfile) -> list[str]:
        """
        Build search queries based on the provided search profile.

        Args:
            profile (SearchProfile): The search profile containing search criteria.

        Returns:
            list[str]: A list of search queries.
        """
        queries: list[str] = []

        # Primary Title + Top 2 keywords
        if profile.job_titles and profile.keywords:
            primary_title = profile.job_titles[0]
            top_keywords = " ".join(profile.keywords[:2])
            queries.append(f"{primary_title} {top_keywords}".strip())

        # Secondary Domain Keywords
        if len(profile.keywords) >= 3:
            secondary_keywords = " ".join(profile.keywords[2:5])
            queries.append(secondary_keywords.strip())

        # Job Type + Key Domain
        if profile.job_types and profile.keywords:
            queries.append(f"{profile.job_types[0]} {profile.keywords[0]}")

        return queries or ["Software Engineer"]

    async def _search_single_query(self, query: str, limit: int) -> list[JobPosting]:
        """
        Fetches page for a single search string and extracts jobs via LLM.
        """
        encoded_query = quote_plus(query)
        target_url = f"{self.base_url}?{self.query_param_name}={encoded_query}"

        raw_html = await self._fetch_rendered_html(target_url)
        if not raw_html:
            return []

        cleaned_html = self._clean_html(raw_html)
        if not cleaned_html:
            return []

        try:
            extracted_data = self.llm.generate_json(
                prompt=prompts.JOB_EXTRACTION_PROMPT,
                text=cleaned_html[:14000],
                response_schema=JobPostingList,
            )
            job_list = JobPostingList(**extracted_data)

            for job in job_list.jobs:
                job.source = self.source_name

            return job_list.jobs[:limit]
        except Exception:
            return []

    async def _fetch_rendered_html(self, url: str) -> str:
        """
        Launches headless browser and retrieves fully-rendered HTML.
        """
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                    "AppleWebKit/537.36"
                )
                page = await context.new_page()
                await page.goto(url, wait_until="networkidle", timeout=20000)
                content = await page.content()
                await browser.close()
                return content
        except Exception:
            return ""

    def _clean_html(self, raw_html: str) -> str:
        """
        Strips scripts, styles, SVGs, and unnecessary formatting.
        """
        soup = BeautifulSoup(raw_html, "html.parser")

        for tag in soup(
            ["script", "style", "nav", "footer", "header", "svg", "noscript", "iframe"]
        ):
            tag.decompose()

        text = soup.get_text(separator="\n")
        lines = (line.strip() for line in text.splitlines())
        return "\n".join(chunk for chunk in lines if chunk)
