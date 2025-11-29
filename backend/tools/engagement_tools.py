# backend/tools/engagement_tools.py

"""
Langchain tools for accessing Meta (Facebook & Instagram) engagement metrics.
Integrates with Graph API v24.0 to fetch real-time insights data.
"""

import aiohttp
from typing import Type, List, Optional
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, Field
from langchain.tools import BaseTool

from backend.models.insights import (
    FacebookPageInsight,
    FacebookPostInsight,
    FacebookVideoInsight,
    InstagramMediaInsight,
    InstagramAccountInsight,
)
from backend.utils import get_logger

logger = get_logger(__name__)

# ============================================================================
# FACEBOOK PAGE INSIGHTS TOOLS
# ============================================================================

class GetFacebookPageInsightsInput(BaseModel):
    """Input for Facebook Page insights."""
    business_asset_id: str = Field(..., description="Business asset ID for multi-tenancy support")
    metrics: str = Field(
        "page_post_engagements,page_media_view",
        description="Comma-separated metrics (e.g., 'page_post_engagements,page_media_view,page_follows')"
    )
    period: str = Field("day", description="Period: day, week, or days_28")
    days_back: int = Field(7, description="Number of days to look back (max 90)")


class GetFacebookPageInsightsTool(BaseTool):
    """Get Facebook Page-level insights."""

    name: str = "get_facebook_page_insights"
    description: str = """
    Get page-level engagement metrics for your Facebook Page.
    Returns metrics like engagements, media views, follows, etc.
    Use this to understand overall page performance.
    """
    args_schema: Type[BaseModel] = GetFacebookPageInsightsInput
    business_asset_id: str

    def __init__(self, business_asset_id: str, **kwargs):
        """Initialize with business_asset_id."""
        super().__init__(business_asset_id=business_asset_id, **kwargs)

    def _run(self, query: str) -> str:
        """Sync version - not used by async agents."""
        raise NotImplementedError("Use async version (_arun) instead")

    async def _arun(self, business_asset_id: str, metrics: str, period: str = "day", days_back: int = 7) -> List[FacebookPageInsight]:
        """Fetch page insights from Facebook Graph API."""
        try:
            from backend.config.business_asset_loader import get_business_asset_credentials
            credentials = get_business_asset_credentials(self.business_asset_id)
            page_id = credentials.facebook_page_id
            access_token = credentials.facebook_page_access_token

            # Calculate date range
            until = datetime.now(timezone.utc)
            since = until - timedelta(days=min(days_back, 90))

            url = f"https://graph.facebook.com/v24.0/{page_id}/insights"
            params = {
                "metric": metrics,
                "period": period,
                "since": int(since.timestamp()),
                "until": int(until.timestamp()),
                "access_token": access_token,
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error("Facebook Page insights error", status=response.status, error=error_text)
                        return []

                    data = await response.json()
                    insights = []

                    for metric_data in data.get("data", []):
                        name = metric_data.get("name")
                        period_val = metric_data.get("period")
                        title = metric_data.get("title", "")
                        description = metric_data.get("description", "")
                        values = metric_data.get("values", [])

                        for value_entry in values:
                            insights.append(FacebookPageInsight(
                                name=name,
                                period=period_val,
                                title=title,
                                description=description,
                                value=value_entry.get("value", 0),
                                end_time=datetime.fromisoformat(value_entry["end_time"].replace("Z", "+00:00"))
                            ))

                    logger.info("Fetched Facebook page insights", count=len(insights))
                    return insights

        except Exception as e:
            logger.error("Error fetching Facebook page insights", error=str(e), exc_info=True)
            return []


# ============================================================================
# FACEBOOK POST INSIGHTS TOOLS
# ============================================================================

class GetFacebookPostInsightsInput(BaseModel):
    """Input for Facebook Post insights."""
    business_asset_id: str = Field(..., description="Business asset ID for multi-tenancy support")
    post_id: str = Field(..., description="Facebook post ID (format: page_id_post_id)")


class GetFacebookPostInsightsTool(BaseTool):
    """Get insights for a specific Facebook post."""

    name: str = "get_facebook_post_insights"
    description: str = """
    Get detailed engagement metrics for a specific Facebook post.
    Returns reactions (likes, loves, wows, etc.) and media views.
    Use this to analyze individual post performance.
    """
    args_schema: Type[BaseModel] = GetFacebookPostInsightsInput
    business_asset_id: str

    def __init__(self, business_asset_id: str, **kwargs):
        """Initialize with business_asset_id."""
        super().__init__(business_asset_id=business_asset_id, **kwargs)

    def _run(self, query: str) -> str:
        """Sync version - not used by async agents."""
        raise NotImplementedError("Use async version (_arun) instead")

    async def _arun(self, business_asset_id: str, post_id: str) -> Optional[FacebookPostInsight]:
        """Fetch post insights from Facebook Graph API."""
        try:
            from backend.config.business_asset_loader import get_business_asset_credentials
            credentials = get_business_asset_credentials(self.business_asset_id)
            access_token = credentials.facebook_page_access_token

            # Fetch reaction metrics
            url = f"https://graph.facebook.com/v24.0/{post_id}/insights"
            params = {
                "metric": "post_reactions_like_total,post_reactions_love_total,post_reactions_wow_total,post_reactions_haha_total,post_reactions_sorry_total,post_reactions_anger_total,post_reactions_by_type_total,post_media_view",
                "access_token": access_token,
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error("Facebook post insights error", status=response.status, error=error_text)
                        return None

                    data = await response.json()

                    # Parse metrics
                    insight = FacebookPostInsight(post_id=post_id)

                    for metric in data.get("data", []):
                        name = metric.get("name")
                        values = metric.get("values", [])
                        if not values:
                            continue

                        value = values[0].get("value", 0)

                        if name == "post_reactions_like_total":
                            insight.reactions_like = value
                        elif name == "post_reactions_love_total":
                            insight.reactions_love = value
                        elif name == "post_reactions_wow_total":
                            insight.reactions_wow = value
                        elif name == "post_reactions_haha_total":
                            insight.reactions_haha = value
                        elif name == "post_reactions_sorry_total":
                            insight.reactions_sorry = value
                        elif name == "post_reactions_anger_total":
                            insight.reactions_anger = value
                        elif name == "post_reactions_by_type_total":
                            if isinstance(value, dict):
                                insight.reactions_by_type = value
                        elif name == "post_media_view":
                            insight.media_views = value

                    logger.info("Fetched Facebook post insights", post_id=post_id)
                    return insight

        except Exception as e:
            logger.error("Error fetching Facebook post insights", error=str(e), exc_info=True)
            return None


# ============================================================================
# FACEBOOK VIDEO INSIGHTS TOOLS
# ============================================================================

class GetFacebookVideoInsightsInput(BaseModel):
    """Input for Facebook Video insights."""
    business_asset_id: str = Field(..., description="Business asset ID for multi-tenancy support")
    video_id: str = Field(..., description="Facebook video ID")


class GetFacebookVideoInsightsTool(BaseTool):
    """Get insights for a Facebook video or reel."""

    name: str = "get_facebook_video_insights"
    description: str = """
    Get detailed video metrics for a Facebook video or reel.
    Returns views, watch time, completions, and reel-specific metrics.
    Use this to analyze video performance.
    """
    args_schema: Type[BaseModel] = GetFacebookVideoInsightsInput
    business_asset_id: str

    def __init__(self, business_asset_id: str, **kwargs):
        """Initialize with business_asset_id."""
        super().__init__(business_asset_id=business_asset_id, **kwargs)

    def _run(self, query: str) -> str:
        """Sync version - not used by async agents."""
        raise NotImplementedError("Use async version (_arun) instead")

    async def _arun(self, business_asset_id: str, video_id: str) -> Optional[FacebookVideoInsight]:
        """Fetch video insights from Facebook Graph API."""
        try:
            from backend.config.business_asset_loader import get_business_asset_credentials
            credentials = get_business_asset_credentials(self.business_asset_id)
            access_token = credentials.facebook_page_access_token

            url = f"https://graph.facebook.com/v24.0/{video_id}/video_insights"
            params = {
                "metric": "total_video_views,total_video_views_unique,total_video_views_autoplayed,total_video_views_clicked_to_play,total_video_views_organic,total_video_views_paid,total_video_complete_views,total_video_complete_views_unique,total_video_avg_time_watched,total_video_view_total_time,fb_reels_total_plays,fb_reels_replay_count",
                "period": "lifetime",
                "access_token": access_token,
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error("Facebook video insights error", status=response.status, error=error_text)
                        return None

                    data = await response.json()

                    # Parse metrics
                    insight = FacebookVideoInsight(video_id=video_id)

                    for metric in data.get("data", []):
                        name = metric.get("name")
                        values = metric.get("values", [])
                        if not values:
                            continue

                        value = values[0].get("value", 0)

                        if name == "total_video_views":
                            insight.total_views = value
                        elif name == "total_video_views_unique":
                            insight.unique_views = value
                        elif name == "total_video_views_autoplayed":
                            insight.autoplayed_views = value
                        elif name == "total_video_views_clicked_to_play":
                            insight.clicked_to_play_views = value
                        elif name == "total_video_views_organic":
                            insight.organic_views = value
                        elif name == "total_video_views_paid":
                            insight.paid_views = value
                        elif name == "total_video_complete_views":
                            insight.complete_views = value
                        elif name == "total_video_complete_views_unique":
                            insight.complete_views_unique = value
                        elif name == "total_video_avg_time_watched":
                            insight.avg_time_watched_ms = int(value * 1000) if isinstance(value, (int, float)) else 0
                        elif name == "total_video_view_total_time":
                            insight.total_time_watched_ms = int(value * 1000) if isinstance(value, (int, float)) else 0
                        elif name == "fb_reels_total_plays":
                            insight.reels_total_plays = value
                        elif name == "fb_reels_replay_count":
                            insight.reels_replay_count = value

                    logger.info("Fetched Facebook video insights", video_id=video_id)
                    return insight

        except Exception as e:
            logger.error("Error fetching Facebook video insights", error=str(e), exc_info=True)
            return None


# ============================================================================
# INSTAGRAM MEDIA INSIGHTS TOOLS
# ============================================================================

class GetInstagramMediaInsightsInput(BaseModel):
    """Input for Instagram media insights."""
    business_asset_id: str = Field(..., description="Business asset ID for multi-tenancy support")
    media_id: str = Field(..., description="Instagram media ID")
    media_type: str = Field("image", description="Media type: image, video, carousel, reel, story")


class GetInstagramMediaInsightsTool(BaseTool):
    """Get insights for Instagram media."""

    name: str = "get_instagram_media_insights"
    description: str = """
    Get engagement metrics for a specific Instagram post, reel, or story.
    Returns reach, views, interactions, likes, comments, saves, shares, and watch time.
    Use this to analyze individual content performance on Instagram.
    """
    args_schema: Type[BaseModel] = GetInstagramMediaInsightsInput
    business_asset_id: str

    def __init__(self, business_asset_id: str, **kwargs):
        """Initialize with business_asset_id."""
        super().__init__(business_asset_id=business_asset_id, **kwargs)

    def _run(self, query: str) -> str:
        """Sync version - not used by async agents."""
        raise NotImplementedError("Use async version (_arun) instead")

    async def _arun(self, business_asset_id: str, media_id: str, media_type: str = "image") -> Optional[InstagramMediaInsight]:
        """Fetch media insights from Instagram Graph API."""
        try:
            from backend.config.business_asset_loader import get_business_asset_credentials
            credentials = get_business_asset_credentials(self.business_asset_id)
            access_token = credentials.instagram_page_access_token

            # Build metric list based on media type
            if media_type == "reel":
                metrics = "reach,views,total_interactions,likes,comments,saved,shares,profile_activity,ig_reels_avg_watch_time,ig_reels_video_view_total_time"
            else:
                metrics = "reach,views,total_interactions,likes,comments,saved,shares,profile_activity"

            url = f"https://graph.instagram.com/v24.0/{media_id}/insights"
            params = {
                "metric": metrics,
                "access_token": access_token,
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error("Instagram media insights error", status=response.status, error=error_text)
                        return None

                    data = await response.json()

                    # Parse metrics
                    insight = InstagramMediaInsight(media_id=media_id, media_type=media_type)

                    for metric in data.get("data", []):
                        name = metric.get("name")
                        values = metric.get("values", [])
                        if not values:
                            continue

                        value = values[0].get("value", 0)

                        if name == "reach":
                            insight.reach = value
                        elif name == "views":
                            insight.views = value
                        elif name == "total_interactions":
                            insight.total_interactions = value
                        elif name == "likes":
                            insight.likes = value
                        elif name == "comments":
                            insight.comments = value
                        elif name == "saved":
                            insight.saves = value
                        elif name == "shares":
                            insight.shares = value
                        elif name == "profile_activity":
                            insight.profile_activity = value
                        elif name == "ig_reels_avg_watch_time":
                            insight.avg_watch_time_ms = value
                        elif name == "ig_reels_video_view_total_time":
                            insight.total_watch_time_ms = value

                    logger.info("Fetched Instagram media insights", media_id=media_id)
                    return insight

        except Exception as e:
            logger.error("Error fetching Instagram media insights", error=str(e), exc_info=True)
            return None


# ============================================================================
# INSTAGRAM ACCOUNT INSIGHTS TOOLS
# ============================================================================

class GetInstagramAccountInsightsInput(BaseModel):
    """Input for Instagram account insights."""
    business_asset_id: str = Field(..., description="Business asset ID for multi-tenancy support")
    period: str = Field("day", description="Period: day, week, or days_28")
    days_back: int = Field(7, description="Number of days to look back")


class GetInstagramAccountInsightsTool(BaseTool):
    """Get Instagram account-level insights."""

    name: str = "get_instagram_account_insights"
    description: str = """
    Get account-level engagement metrics for your Instagram Business Account.
    Returns reach, views, engaged accounts, interactions, and profile metrics.
    Use this to understand overall Instagram performance.
    """
    args_schema: Type[BaseModel] = GetInstagramAccountInsightsInput
    business_asset_id: str

    def __init__(self, business_asset_id: str, **kwargs):
        """Initialize with business_asset_id."""
        super().__init__(business_asset_id=business_asset_id, **kwargs)

    def _run(self, query: str) -> str:
        """Sync version - not used by async agents."""
        raise NotImplementedError("Use async version (_arun) instead")

    async def _arun(self, business_asset_id: str, period: str = "day", days_back: int = 7) -> Optional[InstagramAccountInsight]:
        """Fetch account insights from Instagram Graph API."""
        try:
            from backend.config.business_asset_loader import get_business_asset_credentials
            credentials = get_business_asset_credentials(self.business_asset_id)
            ig_account_id = credentials.app_users_instagram_account_id
            access_token = credentials.instagram_page_access_token

            # Calculate date range
            until = int(datetime.now(timezone.utc).timestamp())
            since = int((datetime.now(timezone.utc) - timedelta(days=days_back)).timestamp())

            url = f"https://graph.instagram.com/v24.0/{ig_account_id}/insights"
            params = {
                "metric": "accounts_engaged,total_interactions,reach,views,profile_links_taps",
                "period": period,
                "metric_type": "total_value",
                "since": since,
                "until": until,
                "access_token": access_token,
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error("Instagram account insights error", status=response.status, error=error_text)
                        return None

                    data = await response.json()

                    # Parse metrics
                    insight = InstagramAccountInsight()

                    for metric in data.get("data", []):
                        name = metric.get("name")
                        values = metric.get("values", [])
                        if not values:
                            continue

                        # Sum up values across the period
                        total = sum(v.get("value", 0) for v in values)

                        if name == "accounts_engaged":
                            insight.accounts_engaged = total
                        elif name == "total_interactions":
                            insight.total_interactions = total
                        elif name == "reach":
                            insight.reach = total
                        elif name == "views":
                            insight.views = total
                        elif name == "profile_links_taps":
                            insight.profile_link_taps = total

                    logger.info("Fetched Instagram account insights")
                    return insight

        except Exception as e:
            logger.error("Error fetching Instagram account insights", error=str(e), exc_info=True)
            return None


# ============================================================================
# TOOL FACTORY
# ============================================================================

def create_engagement_tools(business_asset_id: str):
    """Create all engagement tools for use with Langchain agents.

    Args:
        business_asset_id: The business asset ID for multi-tenancy support.

    Returns:
        List of engagement tools configured with the provided business_asset_id.
    """
    return [
        GetFacebookPageInsightsTool(business_asset_id=business_asset_id),
        GetFacebookPostInsightsTool(business_asset_id=business_asset_id),
        GetFacebookVideoInsightsTool(business_asset_id=business_asset_id),
        GetInstagramMediaInsightsTool(business_asset_id=business_asset_id),
        GetInstagramAccountInsightsTool(business_asset_id=business_asset_id),
    ]
