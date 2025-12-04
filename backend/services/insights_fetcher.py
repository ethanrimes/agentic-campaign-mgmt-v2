# backend/services/insights_fetcher.py

"""
Insights fetching service.

Coordinates fetching insights from Meta APIs and storing them in the database.
Used by CLI commands and scheduled jobs.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from backend.utils import get_logger
from backend.config.settings import settings
from backend.config.business_asset_loader import get_business_asset_credentials

# Import insights services
from backend.services.meta.insights import (
    FacebookInsightsService,
    InstagramInsightsService,
)

# Import repositories
from backend.database.repositories.insights_metrics import (
    FacebookPageInsightsRepository,
    FacebookPostInsightsRepository,
    FacebookVideoInsightsRepository,
    InstagramAccountInsightsRepository,
    InstagramMediaInsightsRepository,
)

# Import completed posts repository
from backend.database.repositories.completed_posts import CompletedPostRepository

logger = get_logger(__name__)


# =============================================================================
# ACCOUNT-LEVEL INSIGHTS FETCHING
# =============================================================================


async def fetch_account_insights(business_asset_id: str) -> Dict[str, Any]:
    """
    Fetch and cache account-level insights for a business asset.

    Fetches:
    - Facebook page insights
    - Instagram account insights

    Args:
        business_asset_id: The business asset ID

    Returns:
        Dictionary with fetched insights data and any errors
    """
    logger.info("Fetching account insights", business_asset_id=business_asset_id)

    result = {
        "facebook": None,
        "instagram": None,
        "errors": [],
    }

    try:
        # Get credentials
        credentials = get_business_asset_credentials(business_asset_id)

        # Fetch Facebook page insights
        try:
            fb_service = FacebookInsightsService(business_asset_id)
            fb_insights = await fb_service.fetch_page_insights()

            # Save to database
            fb_repo = FacebookPageInsightsRepository()
            saved = await fb_repo.upsert(fb_insights)

            result["facebook"] = {
                "page_name": saved.page_name,
                "page_views_total": saved.page_views_total,
                "page_post_engagements": saved.page_post_engagements,
                "page_follows": saved.page_follows,
                "metrics_fetched_at": saved.metrics_fetched_at.isoformat() if saved.metrics_fetched_at else None,
            }

            logger.info(
                "Facebook page insights fetched and saved",
                business_asset_id=business_asset_id,
                page_name=saved.page_name,
            )

        except Exception as e:
            error_msg = f"Failed to fetch Facebook page insights: {e}"
            logger.error(error_msg, business_asset_id=business_asset_id)
            result["errors"].append(error_msg)

        # Fetch Instagram account insights
        try:
            ig_service = InstagramInsightsService(business_asset_id)
            ig_insights = await ig_service.fetch_account_insights()

            # Save to database
            ig_repo = InstagramAccountInsightsRepository()
            saved = await ig_repo.upsert(ig_insights)

            result["instagram"] = {
                "username": saved.username,
                "followers_count": saved.followers_count,
                "reach_day": saved.reach_day,
                "reach_week": saved.reach_week,
                "metrics_fetched_at": saved.metrics_fetched_at.isoformat() if saved.metrics_fetched_at else None,
            }

            logger.info(
                "Instagram account insights fetched and saved",
                business_asset_id=business_asset_id,
                username=saved.username,
            )

        except Exception as e:
            error_msg = f"Failed to fetch Instagram account insights: {e}"
            logger.error(error_msg, business_asset_id=business_asset_id)
            result["errors"].append(error_msg)

    except Exception as e:
        error_msg = f"Failed to get credentials: {e}"
        logger.error(error_msg, business_asset_id=business_asset_id)
        result["errors"].append(error_msg)

    return result


# =============================================================================
# POST-LEVEL INSIGHTS FETCHING
# =============================================================================


async def fetch_post_insights(
    business_asset_id: str,
    limit: int = None,
    days_back: int = None
) -> Dict[str, Any]:
    """
    Fetch and cache post-level insights for recent posts.

    Fetches insights for:
    - Facebook posts (from completed_posts table)
    - Facebook videos
    - Instagram media

    Args:
        business_asset_id: The business asset ID
        limit: Max posts to fetch per platform (default from settings)
        days_back: Only fetch posts from last N days (default from settings)

    Returns:
        Dictionary with counts and any errors
    """
    limit = limit or settings.insights_post_limit
    days_back = days_back or settings.insights_post_days_back

    logger.info(
        "Fetching post insights",
        business_asset_id=business_asset_id,
        limit=limit,
        days_back=days_back,
    )

    result = {
        "facebook_posts_fetched": 0,
        "facebook_videos_fetched": 0,
        "instagram_media_fetched": 0,
        "errors": [],
    }

    try:
        # Get completed posts from database
        posts_repo = CompletedPostRepository()
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)

        # Get Facebook posts (published with platform_post_id)
        fb_posts = await posts_repo.get_recent_published_for_insights(
            business_asset_id=business_asset_id,
            platform="facebook",
            limit=limit,
            since=cutoff_date,
        )

        # Get Instagram posts (published with platform_post_id)
        ig_posts = await posts_repo.get_recent_published_for_insights(
            business_asset_id=business_asset_id,
            platform="instagram",
            limit=limit,
            since=cutoff_date,
        )

        logger.info(
            "Found posts to fetch insights for",
            facebook_count=len(fb_posts),
            instagram_count=len(ig_posts),
        )

        # Fetch Facebook post insights
        if fb_posts:
            fb_service = FacebookInsightsService(business_asset_id)
            fb_post_repo = FacebookPostInsightsRepository()
            fb_video_repo = FacebookVideoInsightsRepository()

            for post in fb_posts:
                if not post.platform_post_id:
                    continue

                try:
                    # Determine whether to use video or post insights endpoint
                    # based on whether platform_video_id is set
                    if post.platform_video_id:
                        # Video post - use video insights endpoint
                        video_insights = await fb_service.fetch_video_insights(
                            video_id=post.platform_video_id
                        )
                        if video_insights:
                            video_insights.completed_post_id = post.id
                            await fb_video_repo.upsert(video_insights)
                            result["facebook_videos_fetched"] += 1
                    else:
                        # Feed post - use post insights endpoint
                        post_insights = await fb_service.fetch_post_insights(
                            platform_post_id=post.platform_post_id
                        )
                        if post_insights:
                            post_insights.completed_post_id = post.id
                            await fb_post_repo.upsert(post_insights)
                            result["facebook_posts_fetched"] += 1

                except Exception as e:
                    error_msg = f"Failed to fetch FB post {post.platform_post_id}: {e}"
                    logger.warning(error_msg)
                    result["errors"].append(error_msg)

        # Fetch Instagram media insights
        if ig_posts:
            ig_service = InstagramInsightsService(business_asset_id)
            ig_media_repo = InstagramMediaInsightsRepository()

            for post in ig_posts:
                if not post.platform_post_id:
                    continue

                try:
                    # Let the service determine media_type from the API
                    # (passing None since the Pydantic model uses lowercase but API returns uppercase)
                    media_insights = await ig_service.fetch_media_insights(
                        media_id=post.platform_post_id,
                        media_type=None,
                    )

                    if media_insights:
                        # Link to completed post
                        media_insights.completed_post_id = post.id
                        await ig_media_repo.upsert(media_insights)
                        result["instagram_media_fetched"] += 1

                except Exception as e:
                    error_msg = f"Failed to fetch IG media {post.platform_post_id}: {e}"
                    logger.warning(error_msg)
                    result["errors"].append(error_msg)

        logger.info(
            "Post insights fetching complete",
            business_asset_id=business_asset_id,
            facebook_posts=result["facebook_posts_fetched"],
            facebook_videos=result["facebook_videos_fetched"],
            instagram_media=result["instagram_media_fetched"],
            errors=len(result["errors"]),
        )

    except Exception as e:
        error_msg = f"Failed to fetch post insights: {e}"
        logger.error(error_msg, business_asset_id=business_asset_id)
        result["errors"].append(error_msg)

    return result


# =============================================================================
# COMBINED FETCHING
# =============================================================================


async def fetch_all_insights(business_asset_id: str) -> Dict[str, Any]:
    """
    Fetch all insights (account + posts) for a business asset.

    Args:
        business_asset_id: The business asset ID

    Returns:
        Dictionary with account and post results
    """
    logger.info("Fetching all insights", business_asset_id=business_asset_id)

    account_result = await fetch_account_insights(business_asset_id)
    posts_result = await fetch_post_insights(business_asset_id)

    return {
        "account": account_result,
        "posts": posts_result,
    }


# =============================================================================
# CACHED INSIGHTS RETRIEVAL
# =============================================================================


async def get_cached_insights(
    business_asset_id: str,
    platform: str = "all"
) -> Dict[str, Any]:
    """
    Get cached insights from the database.

    Args:
        business_asset_id: The business asset ID
        platform: "facebook", "instagram", or "all"

    Returns:
        Dictionary with cached insights data
    """
    logger.info(
        "Getting cached insights",
        business_asset_id=business_asset_id,
        platform=platform,
    )

    result = {}

    if platform in ("facebook", "all"):
        # Get Facebook page insights
        fb_page_repo = FacebookPageInsightsRepository()
        result["facebook_page"] = await fb_page_repo.get_latest(business_asset_id)

        # Get Facebook post insights
        fb_post_repo = FacebookPostInsightsRepository()
        result["facebook_posts"] = await fb_post_repo.get_all_for_business(
            business_asset_id,
            limit=settings.insights_facebook_posts_limit,
        )

        # Get Facebook video insights
        fb_video_repo = FacebookVideoInsightsRepository()
        result["facebook_videos"] = await fb_video_repo.get_recent(
            business_asset_id,
            limit=settings.insights_facebook_posts_limit,
        )

    if platform in ("instagram", "all"):
        # Get Instagram account insights
        ig_account_repo = InstagramAccountInsightsRepository()
        result["instagram_account"] = await ig_account_repo.get_latest(business_asset_id)

        # Get Instagram media insights
        ig_media_repo = InstagramMediaInsightsRepository()
        result["instagram_media"] = await ig_media_repo.get_all_for_business(
            business_asset_id,
            limit=settings.insights_instagram_posts_limit,
        )

    return result
