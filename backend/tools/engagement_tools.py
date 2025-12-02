# backend/tools/engagement_tools.py

"""
Engagement metrics fetchers for Facebook and Instagram.
Used by the insights agent to gather post-level and account-level metrics.

This module provides direct API calls (not LangChain tools) for the
context-stuffing approach where all metrics are gathered upfront.
"""

import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, Field

from backend.models.insights import (
    FacebookPageInsight,
    FacebookPostInsight,
    FacebookVideoInsight,
    InstagramMediaInsight,
    InstagramAccountInsight,
)
from backend.config.business_asset_loader import get_business_asset_credentials
from backend.utils import get_logger

logger = get_logger(__name__)


# ============================================================================
# FACEBOOK PAGE-LEVEL METRICS
# ============================================================================

async def fetch_facebook_page_insights(
    business_asset_id: str,
    period: str = "day",
    days_back: int = 14
) -> List[FacebookPageInsight]:
    """
    Fetch Facebook Page-level insights.

    Note: Page insights may not be available for all pages depending on
    page type and permissions. Returns empty list if unavailable.

    Args:
        business_asset_id: Business asset ID for credentials
        period: Period for metrics (day, week, days_28)
        days_back: Number of days to look back (max 90)

    Returns:
        List of FacebookPageInsight objects
    """
    try:
        credentials = get_business_asset_credentials(business_asset_id)
        page_id = credentials.facebook_page_id
        access_token = credentials.facebook_page_access_token

        until = datetime.now(timezone.utc)
        since = until - timedelta(days=min(days_back, 90))

        # Default metrics for page insights
        # These metrics are commonly available across page types
        default_metrics = "page_views_total,page_daily_follows,page_daily_unfollows,page_follows,page_posts_impressions,page_daily_follows_unique"

        url = f"https://graph.facebook.com/v24.0/{page_id}/insights"
        params = {
            "metric": default_metrics,
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
# FACEBOOK POST-LEVEL METRICS (Feed Posts / Photos)
# ============================================================================

async def fetch_facebook_post_insights(
    business_asset_id: str,
    platform_post_id: str
) -> Optional[FacebookPostInsight]:
    """
    Fetch engagement metrics for a Facebook feed post or photo.

    IMPORTANT: For feed posts, platform_post_id should be just the post ID.
    This function constructs the full ID as {page_id}_{post_id} for the API call.

    Args:
        business_asset_id: Business asset ID for credentials
        platform_post_id: The platform post ID (without page_id prefix)

    Returns:
        FacebookPostInsight or None if error
    """
    try:
        credentials = get_business_asset_credentials(business_asset_id)
        page_id = credentials.facebook_page_id
        access_token = credentials.facebook_page_access_token

        # Construct full post ID: page_id_post_id
        # Check if post_id already contains an underscore (already has page_id)
        if "_" in platform_post_id:
            full_post_id = platform_post_id
        else:
            full_post_id = f"{page_id}_{platform_post_id}"

        # Fetch basic engagement counts via the post object
        url = f"https://graph.facebook.com/v24.0/{full_post_id}"
        params = {
            "fields": "likes.summary(true),comments.summary(true),shares,reactions.summary(true)",
            "access_token": access_token,
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error("Facebook post insights error", status=response.status, error=error_text, post_id=full_post_id)
                    return None

                data = await response.json()

                insight = FacebookPostInsight(
                    post_id=platform_post_id,
                    reactions_like=data.get("reactions", {}).get("summary", {}).get("total_count", 0),
                    media_views=None  # Not available for basic feed posts
                )

                # Fetch detailed metrics from insights endpoint
                # Metrics: post_clicks, post_reactions_like_total, post_reactions_love_total, etc.
                insights_url = f"https://graph.facebook.com/v24.0/{full_post_id}/insights"
                insights_params = {
                    "metric": "post_clicks,post_reactions_like_total,post_reactions_love_total,post_reactions_wow_total,post_reactions_haha_total,post_reactions_sorry_total,post_reactions_anger_total,post_reactions_by_type_total",
                    "access_token": access_token,
                }

                async with session.get(insights_url, params=insights_params) as insights_response:
                    if insights_response.status == 200:
                        insights_data = await insights_response.json()
                        for metric in insights_data.get("data", []):
                            name = metric.get("name")
                            values = metric.get("values", [])
                            if not values:
                                continue
                            value = values[0].get("value", 0)

                            if name == "post_clicks":
                                insight.clicks = value if isinstance(value, int) else 0
                            elif name == "post_reactions_like_total":
                                insight.reactions_like = value if isinstance(value, int) else 0
                            elif name == "post_reactions_love_total":
                                insight.reactions_love = value if isinstance(value, int) else 0
                            elif name == "post_reactions_wow_total":
                                insight.reactions_wow = value if isinstance(value, int) else 0
                            elif name == "post_reactions_haha_total":
                                insight.reactions_haha = value if isinstance(value, int) else 0
                            elif name == "post_reactions_sorry_total":
                                insight.reactions_sorry = value if isinstance(value, int) else 0
                            elif name == "post_reactions_anger_total":
                                insight.reactions_anger = value if isinstance(value, int) else 0
                            elif name == "post_reactions_by_type_total":
                                if isinstance(value, dict):
                                    insight.reactions_by_type = value

                logger.info("Fetched Facebook post insights", post_id=platform_post_id)
                return insight

    except Exception as e:
        logger.error("Error fetching Facebook post insights", error=str(e), exc_info=True)
        return None


# ============================================================================
# FACEBOOK VIDEO METRICS (Videos / Reels)
# ============================================================================

async def fetch_facebook_video_insights(
    business_asset_id: str,
    video_id: str
) -> Optional[FacebookVideoInsight]:
    """
    Fetch metrics for a Facebook video or reel.

    Uses the /{video_id}/video_insights endpoint.
    Valid metrics from API:
    - post_video_likes_by_reaction_type
    - post_video_avg_time_watched
    - post_video_social_actions
    - post_video_view_time
    - post_impressions_unique (reach)
    - blue_reels_play_count
    - fb_reels_total_plays
    - fb_reels_replay_count
    - post_video_retention_graph
    - post_video_followers

    Args:
        business_asset_id: Business asset ID for credentials
        video_id: The Facebook video ID (platform_post_id for video posts)

    Returns:
        FacebookVideoInsight or None if error
    """
    try:
        credentials = get_business_asset_credentials(business_asset_id)
        access_token = credentials.facebook_page_access_token

        url = f"https://graph.facebook.com/v24.0/{video_id}/video_insights"
        # No metric parameter = get all available metrics
        params = {
            "access_token": access_token,
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error("Facebook video insights error", status=response.status, error=error_text, video_id=video_id)
                    return None

                data = await response.json()
                insight = FacebookVideoInsight(video_id=video_id)

                for metric in data.get("data", []):
                    name = metric.get("name")
                    values = metric.get("values", [])
                    if not values:
                        continue

                    value = values[0].get("value", 0)

                    if name == "post_impressions_unique":
                        insight.unique_views = value
                    elif name == "post_video_avg_time_watched":
                        insight.avg_time_watched_ms = value if isinstance(value, int) else 0
                    elif name == "post_video_view_time":
                        insight.total_time_watched_ms = value if isinstance(value, int) else 0
                    elif name == "blue_reels_play_count":
                        insight.total_views = value
                    elif name == "fb_reels_total_plays":
                        insight.reels_total_plays = value
                    elif name == "fb_reels_replay_count":
                        insight.reels_replay_count = value
                    elif name == "post_video_social_actions":
                        # This is a dict with comments, shares, reactions
                        if isinstance(value, dict):
                            insight.reactions_by_type = value

                logger.info("Fetched Facebook video insights", video_id=video_id)
                return insight

    except Exception as e:
        logger.error("Error fetching Facebook video insights", error=str(e), exc_info=True)
        return None


# ============================================================================
# INSTAGRAM MEDIA METRICS
# ============================================================================

async def fetch_instagram_media_insights(
    business_asset_id: str,
    media_id: str,
    media_type: str = "image"
) -> Optional[InstagramMediaInsight]:
    """
    Fetch engagement metrics for an Instagram post, reel, or carousel.

    Args:
        business_asset_id: Business asset ID for credentials
        media_id: Instagram media ID (platform_post_id)
        media_type: Type of media (image, video, carousel, reel)

    Returns:
        InstagramMediaInsight or None if error
    """
    try:
        credentials = get_business_asset_credentials(business_asset_id)
        access_token = credentials.instagram_page_access_token

        async with aiohttp.ClientSession() as session:
            # First, fetch basic media fields (permalink, like_count, comments_count)
            media_url = f"https://graph.instagram.com/v24.0/{media_id}"
            media_params = {
                "fields": "id,caption,media_type,like_count,comments_count,permalink",
                "access_token": access_token,
            }

            insight = InstagramMediaInsight(media_id=media_id, media_type=media_type)

            async with session.get(media_url, params=media_params) as media_response:
                if media_response.status == 200:
                    media_data = await media_response.json()
                    # Populate from basic fields
                    insight.likes = media_data.get("like_count", 0)
                    insight.comments = media_data.get("comments_count", 0)
                    insight.permalink = media_data.get("permalink")
                    # Update media_type from API if available
                    api_media_type = media_data.get("media_type", "").lower()
                    if api_media_type == "video":
                        insight.media_type = "reel"
                    elif api_media_type == "carousel_album":
                        insight.media_type = "carousel"
                    elif api_media_type == "image":
                        insight.media_type = "image"

            # Then fetch insights metrics
            # Build metric list based on media type
            # Note: "impressions" is NOT supported for image posts, only for reels/videos
            # For reels: reach, total_interactions, likes, comments, saved, shares, ig_reels_avg_watch_time, ig_reels_video_view_total_time
            # For images: only reach, total_interactions, likes, comments, saved, shares (NO impressions)
            if insight.media_type == "reel" or insight.media_type == "video":
                metrics = "reach,total_interactions,likes,comments,saved,shares,ig_reels_avg_watch_time,ig_reels_video_view_total_time"
            else:
                # Images don't support impressions metric
                metrics = "reach,total_interactions,likes,comments,saved,shares"

            insights_url = f"https://graph.instagram.com/v24.0/{media_id}/insights"
            insights_params = {
                "metric": metrics,
                "access_token": access_token,
            }

            async with session.get(insights_url, params=insights_params) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error("Instagram media insights error", status=response.status, error=error_text, media_id=media_id)
                    # Return partial data from basic fields if insights fail
                    if insight.likes > 0 or insight.comments > 0 or insight.permalink:
                        logger.info("Returning partial Instagram media data", media_id=media_id)
                        return insight
                    return None

                data = await response.json()

                for metric in data.get("data", []):
                    name = metric.get("name")
                    values = metric.get("values", [])
                    if not values:
                        continue

                    value = values[0].get("value", 0)

                    if name == "reach":
                        insight.reach = value
                    elif name == "impressions" or name == "plays":
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
# INSTAGRAM ACCOUNT-LEVEL METRICS
# ============================================================================

async def fetch_instagram_account_insights(
    business_asset_id: str,
    days_back: int = 14
) -> Optional[InstagramAccountInsight]:
    """
    Fetch Instagram account-level insights.

    Args:
        business_asset_id: Business asset ID for credentials
        days_back: Number of days to look back

    Returns:
        InstagramAccountInsight or None if error
    """
    try:
        credentials = get_business_asset_credentials(business_asset_id)
        ig_account_id = credentials.app_users_instagram_account_id
        access_token = credentials.instagram_page_access_token

        until = int(datetime.now(timezone.utc).timestamp())
        since = int((datetime.now(timezone.utc) - timedelta(days=days_back)).timestamp())

        url = f"https://graph.instagram.com/v24.0/{ig_account_id}/insights"
        # Valid metrics per API error: reach, follower_count, accounts_engaged, total_interactions,
        # likes, comments, shares, saves, profile_links_taps, follows_and_unfollows
        params = {
            "metric": "accounts_engaged,total_interactions,reach,profile_links_taps,follows_and_unfollows",
            "period": "day",
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
                insight = InstagramAccountInsight()

                for metric in data.get("data", []):
                    name = metric.get("name")
                    # For total_value metrics, we get a single total
                    total_value = metric.get("total_value", {}).get("value", 0)

                    # Also check values array for compatibility
                    values = metric.get("values", [])
                    if values and not total_value:
                        total_value = sum(v.get("value", 0) for v in values)

                    if name == "accounts_engaged":
                        insight.accounts_engaged = total_value
                    elif name == "total_interactions":
                        insight.total_interactions = total_value
                    elif name == "reach":
                        insight.reach = total_value
                    elif name == "impressions":
                        insight.views = total_value
                    elif name == "profile_links_taps":
                        insight.profile_link_taps = total_value
                    elif name == "follows_and_unfollows":
                        if isinstance(total_value, dict):
                            insight.follows = total_value.get("follows", 0)
                            insight.unfollows = total_value.get("unfollows", 0)

                logger.info("Fetched Instagram account insights", days_back=days_back)
                return insight

    except Exception as e:
        logger.error("Error fetching Instagram account insights", error=str(e), exc_info=True)
        return None


# ============================================================================
# COMMENTS FROM DATABASE (unchanged - still useful)
# ============================================================================

async def fetch_platform_comments(
    business_asset_id: str,
    platform: Optional[str] = None,
    post_id: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Fetch comments from the database for analysis.

    Args:
        business_asset_id: Business asset ID
        platform: Filter by platform (facebook, instagram)
        post_id: Filter by specific post ID
        limit: Maximum comments to return

    Returns:
        List of comment dictionaries
    """
    try:
        from backend.database import get_supabase_admin_client
        client = await get_supabase_admin_client()

        query = (
            client.table("platform_comments")
            .select("*")
            .eq("business_asset_id", business_asset_id)
            .order("created_time", desc=True)
            .limit(limit)
        )

        if platform:
            query = query.eq("platform", platform)
        if post_id:
            query = query.eq("post_id", post_id)

        result = await query.execute()

        comments = []
        for item in result.data:
            comments.append({
                "comment_id": item.get("comment_id"),
                "platform": item.get("platform"),
                "post_id": item.get("post_id"),
                "comment_text": item.get("comment_text"),
                "commenter_username": item.get("commenter_username"),
                "created_time": item.get("created_time"),
                "like_count": item.get("like_count", 0),
                "status": item.get("status"),
                "response_text": item.get("response_text"),
            })

        logger.info("Fetched platform comments", count=len(comments))
        return comments

    except Exception as e:
        logger.error("Error fetching platform comments", error=str(e), exc_info=True)
        return []
