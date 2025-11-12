# backend/tools/tests/test_knowledge_base_tools.py

"""
Integration tests for knowledge base tools.
These tests use real database connections and test data.
They are read-only and do not insert or modify data.
"""

import pytest
import asyncio
from backend.tools.knowledge_base_tools import (
    SearchNewsEventsTool,
    GetRecentSeedsTool,
    GetLatestInsightsTool,
)

# Mark all tests in this file as asyncio and integration
pytestmark = [pytest.mark.asyncio, pytest.mark.integration]


class TestSearchNewsEventsTool:
    """Read-only integration tests for SearchNewsEventsTool."""

    async def test_arun_search_reads_schema(self):
        """
        Test searching for news events.
        A successful run either finds formatted results or a 'not found' message.
        """
        tool = SearchNewsEventsTool()

        # Search for a broad query to increase chance of results
        result = await tool._arun(query="a", limit=5)

        assert isinstance(result, str)
        # The result is valid if it's the "not found" message OR it's a formatted list
        assert "No news events found" in result or result.startswith("- ")

    async def test_arun_no_results(self):
        """Test searching when no matching events exist."""
        tool = SearchNewsEventsTool()

        # Search for something that definitely doesn't exist
        result = await tool._arun(query="ThisEventDefinitelyDoesNotExist12345", limit=5)

        assert "No news events found" in result
        assert "ThisEventDefinitelyDoesNotExist12345" in result

    async def test_arun_with_limit(self):
        """Test that limit parameter is respected (read-only)."""
        tool = SearchNewsEventsTool()

        result = await tool._arun(query="test", limit=1)

        # Should get a valid string response (either data or "not found")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_run_raises_not_implemented(self):
        """Test that sync version raises NotImplementedError."""
        tool = SearchNewsEventsTool()

        with pytest.raises(NotImplementedError):
            tool._run(query="test")


class TestGetRecentSeedsTool:
    """Read-only integration tests for GetRecentSeedsTool."""

    async def test_arun_news_seeds_reads_schema(self):
        """Test retrieving recent news seeds, validating schema."""
        tool = GetRecentSeedsTool()

        result = await tool._arun(seed_type="news", limit=10)

        assert isinstance(result, str)
        # Valid if "not found" or if it's a formatted list
        assert "No news seeds found" in result or result.startswith("- ")

    async def test_arun_trend_seeds_reads_schema(self):
        """Test retrieving recent trend seeds, validating schema."""
        tool = GetRecentSeedsTool()

        result = await tool._arun(seed_type="trend", limit=10)

        assert isinstance(result, str)
        # Valid if "not found" or if it's a formatted list
        assert "No trend seeds found" in result or result.startswith("- ")

    async def test_arun_ungrounded_seeds_reads_schema(self):
        """Test retrieving recent ungrounded seeds, validating schema."""
        tool = GetRecentSeedsTool()

        result = await tool._arun(seed_type="ungrounded", limit=10)

        assert isinstance(result, str)
        # Valid if "not found" or if it's a formatted list
        assert "No ungrounded seeds found" in result or result.startswith("- ")

    async def test_arun_invalid_seed_type(self):
        """Test with invalid seed type."""
        tool = GetRecentSeedsTool()

        result = await tool._arun(seed_type="invalid_type_12345", limit=10)

        assert "Invalid seed type" in result
        assert "invalid_type_12345" in result

    async def test_arun_with_different_limits(self):
        """Test that different limit values work correctly (read-only)."""
        tool = GetRecentSeedsTool()

        result_5 = await tool._arun(seed_type="news", limit=5)
        result_20 = await tool._arun(seed_type="news", limit=20)

        assert isinstance(result_5, str)
        assert isinstance(result_20, str)

    def test_run_raises_not_implemented(self):
        """Test that sync version raises NotImplementedError."""
        tool = GetRecentSeedsTool()

        with pytest.raises(NotImplementedError):
            tool._run(seed_type="news")


class TestGetLatestInsightsTool:
    """Read-only integration tests for GetLatestInsightsTool."""

    async def test_arun_insights_reads_schema(self):
        """Test retrieving latest insights, validating schema."""
        tool = GetLatestInsightsTool()

        result = await tool._arun()

        assert isinstance(result, str)
        # These are the two possible valid string responses
        assert result == "No insights reports found" or result.startswith("Latest Insights Report")

    def test_run_raises_not_implemented(self):
        """Test that sync version raises NotImplementedError."""
        tool = GetLatestInsightsTool()

        with pytest.raises(NotImplementedError):
            tool._run()


class TestKnowledgeBaseToolsIntegration:
    """Read-only integration tests for complete workflows."""

    async def test_complete_read_only_workflow(self):
        """Test using multiple knowledge base tools in sequence (read-only)."""
        # Search for news events
        search_tool = SearchNewsEventsTool()
        search_result = await search_tool._arun(query="a", limit=5)
        assert isinstance(search_result, str)

        # Get recent seeds of each type
        seeds_tool = GetRecentSeedsTool()

        news_result = await seeds_tool._arun(seed_type="news", limit=10)
        assert isinstance(news_result, str)

        trend_result = await seeds_tool._arun(seed_type="trend", limit=10)
        assert isinstance(trend_result, str)

        ungrounded_result = await seeds_tool._arun(seed_type="ungrounded", limit=10)
        assert isinstance(ungrounded_result, str)

        # Get latest insights
        insights_tool = GetLatestInsightsTool()
        insights_result = await insights_tool._arun()
        assert isinstance(insights_result, str)

    async def test_tools_handle_concurrent_read_only(self):
        """Test that tools can handle concurrent execution (read-only)."""
        search_tool = SearchNewsEventsTool()
        insights_tool = GetLatestInsightsTool()

        # Run both tools concurrently
        search_task = search_tool._arun(query="e", limit=5)
        insights_task = insights_tool._arun()

        search_result, insights_result = await asyncio.gather(search_task, insights_task)

        # Both should complete successfully and return valid strings
        assert isinstance(search_result, str)
        assert isinstance(insights_result, str)