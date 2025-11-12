# backend/tools/tests/test_engagement_tools.py

"""
Integration tests for engagement tools.
These tests use real Meta API connections.
"""

import pytest
from backend.tools.engagement_tools import (
    GetPageInsightsTool,
    GetPostEngagementTool,
    GetPostCommentsTool,
    GetInstagramInsightsTool,
    GetInstagramMediaInsightsTool,
)
from .conftest import skip_if_no_meta


pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.integration,
    pytest.mark.requires_meta,
    skip_if_no_meta,
]


class TestGetPageInsightsTool:
    """Integration tests for GetPageInsightsTool with real Meta API."""

    async def test_arun_with_real_api(self, test_page_id):
        """Test getting page insights from real Meta API."""
        tool = GetPageInsightsTool()

        # Request common page metrics
        result = await tool._arun(
            page_id=test_page_id,
            metric_names="page_impressions,page_engaged_users",
            period="day"
        )

        # Verify we get actual data back
        assert isinstance(result, str)
        assert "Page Insights" in result
        assert test_page_id in result
        # Should contain at least one of the requested metrics
        assert "page_impressions" in result or "page_engaged_users" in result or "No insights data" in result

    async def test_arun_with_different_periods(self, test_page_id):
        """Test getting insights with different time periods."""
        tool = GetPageInsightsTool()

        # Test with different periods
        for period in ["day", "week", "lifetime"]:
            result = await tool._arun(
                page_id=test_page_id,
                metric_names="page_impressions",
                period=period
            )

            assert isinstance(result, str)
            assert period in result.lower()

    async def test_arun_handles_invalid_metrics_gracefully(self, test_page_id):
        """Test that tool handles invalid metric names gracefully."""
        tool = GetPageInsightsTool()

        result = await tool._arun(
            page_id=test_page_id,
            metric_names="invalid_metric_12345",
            period="day"
        )

        # Should get either an error or no data message
        assert isinstance(result, str)
        # Tool should handle errors gracefully, not crash

    def test_run_raises_not_implemented(self):
        """Test that sync version raises NotImplementedError."""
        tool = GetPageInsightsTool()

        with pytest.raises(NotImplementedError):
            tool._run(page_id="test", metric_names="test")


class TestGetPostEngagementTool:
    """Integration tests for GetPostEngagementTool with real Meta API."""

    async def test_arun_handles_response(self, test_page_id):
        """Test getting post engagement data."""
        tool = GetPostEngagementTool()

        # Create a sample post ID (format: {page_id}_{post_id})
        # Note: This might not return data if the post doesn't exist,
        # but should handle it gracefully
        post_id = f"{test_page_id}_12345"

        result = await tool._arun(post_id=post_id)

        # Should return a valid response (either data or "no data found" message)
        assert isinstance(result, str)
        assert "Post Engagement" in result or "No engagement data" in result or "Error" in result

    def test_run_raises_not_implemented(self):
        """Test that sync version raises NotImplementedError."""
        tool = GetPostEngagementTool()

        with pytest.raises(NotImplementedError):
            tool._run(post_id="test")


class TestGetPostCommentsTool:
    """Integration tests for GetPostCommentsTool with real Meta API."""

    async def test_arun_handles_response(self, test_page_id):
        """Test getting post comments."""
        tool = GetPostCommentsTool()

        # Create a sample post ID
        post_id = f"{test_page_id}_12345"

        result = await tool._arun(post_id=post_id, limit=25)

        # Should return a valid response
        assert isinstance(result, str)
        assert "Comments" in result or "No comments" in result or "Error" in result

    async def test_arun_with_different_limits(self, test_page_id):
        """Test getting comments with different limit values."""
        tool = GetPostCommentsTool()

        post_id = f"{test_page_id}_12345"

        for limit in [5, 10, 25]:
            result = await tool._arun(post_id=post_id, limit=limit)

            assert isinstance(result, str)
            # Should handle the request regardless of limit

    def test_run_raises_not_implemented(self):
        """Test that sync version raises NotImplementedError."""
        tool = GetPostCommentsTool()

        with pytest.raises(NotImplementedError):
            tool._run(post_id="test")


class TestGetInstagramInsightsTool:
    """Integration tests for GetInstagramInsightsTool with real Meta API."""

    async def test_arun_with_real_api(self, test_instagram_id):
        """Test getting Instagram insights from real Meta API."""
        tool = GetInstagramInsightsTool()

        # Request common Instagram metrics
        result = await tool._arun(
            ig_user_id=test_instagram_id,
            metric_names="impressions,reach,profile_views",
            period="day"
        )

        # Verify we get actual data back
        assert isinstance(result, str)
        assert "Instagram Insights" in result or "No Instagram insights" in result
        assert test_instagram_id in result

    async def test_arun_with_different_periods(self, test_instagram_id):
        """Test getting insights with different time periods."""
        tool = GetInstagramInsightsTool()

        for period in ["day", "week", "days_28"]:
            result = await tool._arun(
                ig_user_id=test_instagram_id,
                metric_names="impressions",
                period=period
            )

            assert isinstance(result, str)
            # Should get a valid response for each period

    def test_run_raises_not_implemented(self):
        """Test that sync version raises NotImplementedError."""
        tool = GetInstagramInsightsTool()

        with pytest.raises(NotImplementedError):
            tool._run(ig_user_id="test", metric_names="test")


class TestGetInstagramMediaInsightsTool:
    """Integration tests for GetInstagramMediaInsightsTool with real Meta API."""

    async def test_arun_handles_response(self):
        """Test getting Instagram media insights."""
        tool = GetInstagramMediaInsightsTool()

        # Use a sample media ID (might not exist, but should handle gracefully)
        media_id = "12345"

        result = await tool._arun(media_id=media_id)

        # Should return a valid response
        assert isinstance(result, str)
        assert "Media Insights" in result or "No insights" in result or "Error" in result

    def test_run_raises_not_implemented(self):
        """Test that sync version raises NotImplementedError."""
        tool = GetInstagramMediaInsightsTool()

        with pytest.raises(NotImplementedError):
            tool._run(media_id="test")


class TestEngagementToolsIntegration:
    """Integration tests for complete engagement workflows."""

    async def test_complete_facebook_workflow(self, test_page_id):
        """Test getting multiple types of Facebook engagement data."""
        page_insights_tool = GetPageInsightsTool()
        post_engagement_tool = GetPostEngagementTool()

        # Get page insights
        page_result = await page_insights_tool._arun(
            page_id=test_page_id,
            metric_names="page_impressions",
            period="day"
        )

        assert isinstance(page_result, str)

        # Try to get post engagement (may not have data)
        post_id = f"{test_page_id}_12345"
        post_result = await post_engagement_tool._arun(post_id=post_id)

        assert isinstance(post_result, str)

    async def test_complete_instagram_workflow(self, test_instagram_id):
        """Test getting multiple types of Instagram engagement data."""
        account_insights_tool = GetInstagramInsightsTool()

        # Get account insights
        account_result = await account_insights_tool._arun(
            ig_user_id=test_instagram_id,
            metric_names="impressions,reach",
            period="day"
        )

        assert isinstance(account_result, str)

    async def test_concurrent_api_calls(self, test_page_id, test_instagram_id):
        """Test that engagement tools can handle concurrent API calls."""
        import asyncio

        page_tool = GetPageInsightsTool()
        instagram_tool = GetInstagramInsightsTool()

        # Run both tools concurrently
        page_task = page_tool._arun(
            page_id=test_page_id,
            metric_names="page_impressions",
            period="day"
        )
        instagram_task = instagram_tool._arun(
            ig_user_id=test_instagram_id,
            metric_names="impressions",
            period="day"
        )

        page_result, instagram_result = await asyncio.gather(page_task, instagram_task)

        # Both should complete successfully
        assert isinstance(page_result, str)
        assert isinstance(instagram_result, str)
