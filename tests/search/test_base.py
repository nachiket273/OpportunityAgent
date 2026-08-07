from __future__ import annotations

import pytest

from opportunity_agent.models.job import JobPosting
from opportunity_agent.models.profile import SearchProfile
from opportunity_agent.search.base import BaseSearchProvider


def test_base_search_provider_cannot_be_instantiated() -> None:
    """Verify that BaseSearchProvider cannot be instantiated directly."""
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        BaseSearchProvider()  # type: ignore[abstract]


def test_subclass_without_abstract_methods_fails_instantiation() -> None:
    """Verify that a subclass missing the `search` method cannot be instantiated."""

    class IncompleteProvider(BaseSearchProvider):
        source_name = "incomplete"

    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        IncompleteProvider()  # type: ignore[abstract]


@pytest.mark.asyncio
async def test_concrete_search_provider_execution() -> None:
    """Verify that a fully implemented provider can be instantiated and executed."""

    class DummyProvider(BaseSearchProvider):
        source_name = "dummy"

        async def search(
            self, profile: SearchProfile, limit: int = 10
        ) -> list[JobPosting]:
            return [
                JobPosting(
                    id="123",
                    title="Test Software Engineer",
                    organization="Acme Corp",
                    source=self.source_name,
                )
            ]

    provider = DummyProvider()
    assert provider.source_name == "dummy"

    profile = SearchProfile(keywords=["Python"])
    results = await provider.search(profile, limit=5)

    assert len(results) == 1
    assert isinstance(results[0], JobPosting)
    assert results[0].title == "Test Software Engineer"
    assert results[0].source == "dummy"
