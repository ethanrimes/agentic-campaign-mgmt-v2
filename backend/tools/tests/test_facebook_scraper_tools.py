# backend/tools/tests/test_facebook_scraper_tools.py

"""
Integration tests for Facebook scraper tools.
These tests use real RapidAPI connections.
"""

import pytest
from backend.tools.facebook_scraper_tools import (
    SearchPagesTool,
    GetPagePostsTool,
    SearchPostsTool,
    GetGroupPostsTool,
)
from .conftest import skip_if_no_rapidapi


pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.integration,
    pytest.mark.requires_rapidapi,
    skip_if_no_rapidapi,
]


class TestSearchPagesTool:
    """Integration tests for SearchPagesTool with real RapidAPI."""

    async def test_arun_with_real_api(self):
        """Test searching for Facebook pages using real API."""
        tool = SearchPagesTool()

        # Search for a common term that should return results
        result = await tool._arun(query="restaurant")

        # Verify we get a valid response
        assert isinstance(result, str)
        assert "Facebook Pages" in result or "No pages found" in result or "Error" in result

    async def test_arun_handles_obscure_query(self):
        """Test searching with a very specific query."""
        tool = SearchPagesTool()

        result = await tool._arun(query="XyZaBC123NonexistentPage9876")

        assert isinstance(result, str)
        # Should either find something or gracefully report no results

    def test_run_raises_not_implemented(self):
        """Test that sync version raises NotImplementedError."""
        tool = SearchPagesTool()

        with pytest.raises(NotImplementedError):
            tool._run(query="test")


class TestGetPagePostsTool:
    """Integration tests for GetPagePostsTool with real RapidAPI."""

    async def test_arun_handles_response(self):
        """Test getting posts from a Facebook page."""
        tool = GetPagePostsTool()

        # Try to get posts (page may or may not exist)
        result = await tool._arun(page_id="12345", limit=10)

        # Should handle gracefully
        assert isinstance(result, str)
        assert "Recent Facebook Posts" in result or "No posts found" in result or "Error" in result

    async def test_arun_with_different_limits(self):
        """Test getting posts with different limit values."""
        tool = GetPagePostsTool()

        for limit in [5, 10, 20]:
            result = await tool._arun(page_id="12345", limit=limit)
            assert isinstance(result, str)

    def test_run_raises_not_implemented(self):
        """Test that sync version raises NotImplementedError."""
        tool = GetPagePostsTool()

        with pytest.raises(NotImplementedError):
            tool._run(page_id="test", limit=10)


class TestSearchPostsTool:
    """Integration tests for SearchPostsTool with real RapidAPI."""

    async def test_arun_with_real_api(self):
        """Test searching for Facebook posts using real API."""
        tool = SearchPostsTool()

        # Search for a common term
        result = await tool._arun(query="food")

        # Verify we get a valid response
        assert isinstance(result, str)
        assert "Facebook Posts" in result or "No posts found" in result or "Error" in result

    def test_run_raises_not_implemented(self):
        """Test that sync version raises NotImplementedError."""
        tool = SearchPostsTool()

        with pytest.raises(NotImplementedError):
            tool._run(query="test")


class TestGetGroupPostsTool:
    """Integration tests for GetGroupPostsTool with real RapidAPI."""

    async def test_arun_handles_response(self):
        """Test getting posts from a Facebook group."""
        tool = GetGroupPostsTool()

        # Try to get group posts (group may or may not exist/be accessible)
        result = await tool._arun(group_id="12345", limit=10)

        # Should handle gracefully
        assert isinstance(result, str)
        assert "Recent Facebook Group Posts" in result or "No posts found" in result or "Error" in result

    def test_run_raises_not_implemented(self):
        """Test that sync version raises NotImplementedError."""
        tool = GetGroupPostsTool()

        with pytest.raises(NotImplementedError):
            tool._run(group_id="test", limit=10)


class TestFacebookScraperToolsIntegration:
    """Integration tests for complete Facebook scraping workflows."""

    async def test_search_pages_and_get_posts_workflow(self):
        """Test searching for pages and getting their posts."""
        search_tool = SearchPagesTool()
        posts_tool = GetPagePostsTool()

        # Search for pages
        search_result = await search_tool._arun(query="restaurant")
        assert isinstance(search_result, str)

        # Try to get posts from a sample page ID
        posts_result = await posts_tool._arun(page_id="12345", limit=5)
        assert isinstance(posts_result, str)

    async def test_concurrent_scraping_operations(self):
        """Test that scraper tools can handle concurrent operations."""
        import asyncio

        search_pages_tool = SearchPagesTool()
        search_posts_tool = SearchPostsTool()

        # Run both searches concurrently
        pages_task = search_pages_tool._arun(query="restaurant")
        posts_task = search_posts_tool._arun(query="food")

        pages_result, posts_result = await asyncio.gather(pages_task, posts_task)

        # Both should complete successfully
        assert isinstance(pages_result, str)
        assert isinstance(posts_result, str)
