# backend/tools/tests/test_instagram_scraper_tools.py

"""
Integration tests for Instagram scraper tools.
These tests use real RapidAPI connections.
"""

import pytest
from backend.tools.instagram_scraper_tools import (
    SearchLocationsTool,
    GetLocationMediaTool,
    SearchHashtagsTool,
    SearchUsersTool,
    GetUserMediaTool,
    GlobalSearchTool,
)
from .conftest import skip_if_no_rapidapi


pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.integration,
    pytest.mark.requires_rapidapi,
    skip_if_no_rapidapi,
]


class TestSearchLocationsTool:
    """Integration tests for SearchLocationsTool with real RapidAPI."""

    async def test_arun_with_real_api(self):
        """Test searching for Instagram locations using real API."""
        tool = SearchLocationsTool()

        result = await tool._arun(query="new york")

        assert isinstance(result, str)
        assert "Instagram Locations" in result or "No locations found" in result or "Error" in result

    def test_run_raises_not_implemented(self):
        """Test that sync version raises NotImplementedError."""
        tool = SearchLocationsTool()

        with pytest.raises(NotImplementedError):
            tool._run(query="test")


class TestGetLocationMediaTool:
    """Integration tests for GetLocationMediaTool with real RapidAPI."""

    async def test_arun_handles_response(self):
        """Test getting media from an Instagram location."""
        tool = GetLocationMediaTool()

        result = await tool._arun(location_id="12345", tab="ranked")

        assert isinstance(result, str)
        assert "Instagram Media" in result or "No media found" in result or "Error" in result

    def test_run_raises_not_implemented(self):
        """Test that sync version raises NotImplementedError."""
        tool = GetLocationMediaTool()

        with pytest.raises(NotImplementedError):
            tool._run(location_id="test")


class TestSearchHashtagsTool:
    """Integration tests for SearchHashtagsTool with real RapidAPI."""

    async def test_arun_with_real_api(self):
        """Test searching for Instagram hashtags using real API."""
        tool = SearchHashtagsTool()

        result = await tool._arun(query="food")

        assert isinstance(result, str)
        assert "Instagram Hashtags" in result or "No hashtags found" in result or "Error" in result

    def test_run_raises_not_implemented(self):
        """Test that sync version raises NotImplementedError."""
        tool = SearchHashtagsTool()

        with pytest.raises(NotImplementedError):
            tool._run(query="test")


class TestSearchUsersTool:
    """Integration tests for SearchUsersTool with real RapidAPI."""

    async def test_arun_with_real_api(self):
        """Test searching for Instagram users using real API."""
        tool = SearchUsersTool()

        result = await tool._arun(query="instagram")

        assert isinstance(result, str)
        assert "Instagram Users" in result or "No users found" in result or "Error" in result

    def test_run_raises_not_implemented(self):
        """Test that sync version raises NotImplementedError."""
        tool = SearchUsersTool()

        with pytest.raises(NotImplementedError):
            tool._run(query="test")


class TestGetUserMediaTool:
    """Integration tests for GetUserMediaTool with real RapidAPI."""

    async def test_arun_handles_response(self):
        """Test getting media from an Instagram user."""
        tool = GetUserMediaTool()

        result = await tool._arun(username="instagram")

        assert isinstance(result, str)
        assert "Recent Instagram Posts" in result or "No media found" in result or "Error" in result

    def test_run_raises_not_implemented(self):
        """Test that sync version raises NotImplementedError."""
        tool = GetUserMediaTool()

        with pytest.raises(NotImplementedError):
            tool._run(username="test")


class TestGlobalSearchTool:
    """Integration tests for GlobalSearchTool with real RapidAPI."""

    async def test_arun_with_real_api(self):
        """Test global Instagram search using real API."""
        tool = GlobalSearchTool()

        result = await tool._arun(query="food")

        assert isinstance(result, str)
        assert "Instagram Global Search" in result or "No results found" in result or "Error" in result

    def test_run_raises_not_implemented(self):
        """Test that sync version raises NotImplementedError."""
        tool = GlobalSearchTool()

        with pytest.raises(NotImplementedError):
            tool._run(query="test")


class TestInstagramScraperToolsIntegration:
    """Integration tests for complete Instagram scraping workflows."""

    async def test_search_workflow(self):
        """Test searching across different Instagram entities."""
        locations_tool = SearchLocationsTool()
        hashtags_tool = SearchHashtagsTool()
        users_tool = SearchUsersTool()

        # Search for locations
        locations_result = await locations_tool._arun(query="philadelphia")
        assert isinstance(locations_result, str)

        # Search for hashtags
        hashtags_result = await hashtags_tool._arun(query="food")
        assert isinstance(hashtags_result, str)

        # Search for users
        users_result = await users_tool._arun(query="chef")
        assert isinstance(users_result, str)

    async def test_concurrent_scraping(self):
        """Test that Instagram tools can handle concurrent operations."""
        import asyncio

        global_search_tool = GlobalSearchTool()
        hashtags_tool = SearchHashtagsTool()

        # Run both searches concurrently
        global_task = global_search_tool._arun(query="travel")
        hashtags_task = hashtags_tool._arun(query="travel")

        global_result, hashtags_result = await asyncio.gather(global_task, hashtags_task)

        assert isinstance(global_result, str)
        assert isinstance(hashtags_result, str)
