# backend/tools/engagement_tools.py

"""Langchain tools for accessing Meta engagement metrics."""

from typing import Type, Optional
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from backend.services.meta.engagement_api import EngagementAPI
from backend.utils import get_logger

logger = get_logger(__name__)


class GetPageInsightsInput(BaseModel):
    """Input for GetPageInsights tool."""
    page_id: str = Field(..., description="Facebook Page ID")
    metric_names: str = Field(
        ...,
        description="Comma-separated metric names (e.g., 'page_impressions,page_engaged_users')"
    )
    period: str = Field("day", description="Time period: 'day', 'week', or 'lifetime'")


class GetPageInsightsTool(BaseTool):
    """Tool to get Facebook Page insights/metrics."""

    name: str = "get_page_insights"
    description: str = """
    Get engagement metrics for a Facebook Page.
    Use this to understand page performance, impressions, reach, and engagement.
    Useful for analyzing what content is performing well.
    """
    args_schema: Type[BaseModel] = GetPageInsightsInput

    def _run(self, page_id: str, metric_names: str, period: str = "day") -> str:
        """Sync version - not used by async agents."""
        raise NotImplementedError("Use async version (_arun) instead")

    async def _arun(self, page_id: str, metric_names: str, period: str = "day") -> str:
        """Execute the tool asynchronously."""
        try:
            metrics = [m.strip() for m in metric_names.split(",")]
            api = EngagementAPI()

            result = await api.get_page_insights(page_id, metrics, period)

            if not result:
                return "No insights data available for the specified metrics."

            # Format results as readable text
            output = f"Page Insights for {page_id} (period: {period}):\n\n"
            for metric in result:
                name = metric.get("name", "unknown")
                values = metric.get("values", [])
                if values:
                    latest_value = values[0].get("value", "N/A")
                    output += f"- {name}: {latest_value}\n"

            return output
        except Exception as e:
            logger.error("Error getting page insights", error=str(e))
            return f"Error retrieving page insights: {str(e)}"


class GetPostEngagementInput(BaseModel):
    """Input for GetPostEngagement tool."""
    post_id: str = Field(..., description="Facebook post ID (format: {page_id}_{post_id})")


class GetPostEngagementTool(BaseTool):
    """Tool to get engagement metrics for a specific post."""

    name: str = "get_post_engagement"
    description: str = """
    Get detailed engagement metrics for a specific Facebook post.
    Returns likes, comments, shares, and reach data.
    Use this to analyze performance of individual posts.
    """
    args_schema: Type[BaseModel] = GetPostEngagementInput

    def _run(self, post_id: str) -> str:
        """Sync version - not used by async agents."""
        raise NotImplementedError("Use async version (_arun) instead")

    async def _arun(self, post_id: str) -> str:
        """Execute the tool asynchronously."""
        try:
            api = EngagementAPI()
            result = await api.get_post_engagement(post_id)

            if not result:
                return f"No engagement data found for post {post_id}"

            output = f"Post Engagement for {post_id}:\n\n"
            output += f"- Likes: {result.get('likes', {}).get('summary', {}).get('total_count', 0)}\n"
            output += f"- Comments: {result.get('comments', {}).get('summary', {}).get('total_count', 0)}\n"
            output += f"- Shares: {result.get('shares', {}).get('count', 0)}\n"

            return output
        except Exception as e:
            logger.error("Error getting post engagement", error=str(e))
            return f"Error retrieving post engagement: {str(e)}"


class GetPostCommentsInput(BaseModel):
    """Input for GetPostComments tool."""
    post_id: str = Field(..., description="Facebook post ID")
    limit: int = Field(25, description="Maximum number of comments to retrieve (default: 25)")


class GetPostCommentsTool(BaseTool):
    """Tool to get comments on a Facebook post."""

    name: str = "get_post_comments"
    description: str = """
    Retrieve comments from a specific Facebook post.
    Use this to understand audience sentiment and feedback on content.
    Returns comment text, author info, and engagement on comments.
    """
    args_schema: Type[BaseModel] = GetPostCommentsInput

    def _run(self, post_id: str, limit: int = 25) -> str:
        """Sync version - not used by async agents."""
        raise NotImplementedError("Use async version (_arun) instead")

    async def _arun(self, post_id: str, limit: int = 25) -> str:
        """Execute the tool asynchronously."""
        try:
            api = EngagementAPI()
            result = await api.get_post_comments(post_id, limit)

            comments = result.get("data", [])
            if not comments:
                return f"No comments found for post {post_id}"

            output = f"Comments for post {post_id} (showing {len(comments)}):\n\n"
            for i, comment in enumerate(comments[:limit], 1):
                text = comment.get("message", "[No text]")
                from_user = comment.get("from", {}).get("name", "Unknown")
                like_count = comment.get("like_count", 0)
                output += f"{i}. {from_user}: {text}\n"
                output += f"   Likes: {like_count}\n\n"

            return output
        except Exception as e:
            logger.error("Error getting post comments", error=str(e))
            return f"Error retrieving comments: {str(e)}"


class GetInstagramInsightsInput(BaseModel):
    """Input for GetInstagramInsights tool."""
    ig_user_id: str = Field(..., description="Instagram Business Account ID")
    metric_names: str = Field(
        ...,
        description="Comma-separated metric names (e.g., 'impressions,reach,profile_views')"
    )
    period: str = Field("day", description="Time period: 'day', 'week', or 'days_28'")


class GetInstagramInsightsTool(BaseTool):
    """Tool to get Instagram account insights."""

    name: str = "get_instagram_insights"
    description: str = """
    Get engagement metrics for an Instagram Business Account.
    Returns impressions, reach, profile views, and other account-level metrics.
    Use this to understand overall Instagram performance.
    """
    args_schema: Type[BaseModel] = GetInstagramInsightsInput

    def _run(self, ig_user_id: str, metric_names: str, period: str = "day") -> str:
        """Sync version - not used by async agents."""
        raise NotImplementedError("Use async version (_arun) instead")

    async def _arun(self, ig_user_id: str, metric_names: str, period: str = "day") -> str:
        """Execute the tool asynchronously."""
        try:
            metrics = [m.strip() for m in metric_names.split(",")]
            api = EngagementAPI()
            result = await api.get_instagram_insights(ig_user_id, metrics, period)

            if not result:
                return "No Instagram insights data available."

            output = f"Instagram Insights for {ig_user_id} (period: {period}):\n\n"
            for metric in result:
                name = metric.get("name", "unknown")
                values = metric.get("values", [])
                if values:
                    latest_value = values[0].get("value", "N/A")
                    output += f"- {name}: {latest_value}\n"

            return output
        except Exception as e:
            logger.error("Error getting Instagram insights", error=str(e))
            return f"Error retrieving Instagram insights: {str(e)}"


class GetInstagramMediaInsightsInput(BaseModel):
    """Input for GetInstagramMediaInsights tool."""
    media_id: str = Field(..., description="Instagram media ID")


class GetInstagramMediaInsightsTool(BaseTool):
    """Tool to get insights for specific Instagram media."""

    name: str = "get_instagram_media_insights"
    description: str = """
    Get engagement metrics for a specific Instagram post or reel.
    Returns impressions, reach, likes, comments, saves, and shares.
    Use this to analyze performance of individual Instagram content.
    """
    args_schema: Type[BaseModel] = GetInstagramMediaInsightsInput

    def _run(self, media_id: str) -> str:
        """Sync version - not used by async agents."""
        raise NotImplementedError("Use async version (_arun) instead")

    async def _arun(self, media_id: str) -> str:
        """Execute the tool asynchronously."""
        try:
            api = EngagementAPI()
            result = await api.get_instagram_media_insights(media_id)

            if not result:
                return f"No insights found for media {media_id}"

            output = f"Media Insights for {media_id}:\n\n"
            for metric in result:
                name = metric.get("name", "unknown")
                values = metric.get("values", [])
                if values:
                    value = values[0].get("value", "N/A")
                    output += f"- {name}: {value}\n"

            return output
        except Exception as e:
            logger.error("Error getting media insights", error=str(e))
            return f"Error retrieving media insights: {str(e)}"


def create_engagement_tools():
    """Create all engagement tools for use with Langchain agents."""
    return [
        GetPageInsightsTool(),
        GetPostEngagementTool(),
        GetPostCommentsTool(),
        GetInstagramInsightsTool(),
        GetInstagramMediaInsightsTool(),
    ]
