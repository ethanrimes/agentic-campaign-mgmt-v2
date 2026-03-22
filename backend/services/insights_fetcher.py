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

# Import completed posts repository and model
from backend.database.repositories.completed_posts import CompletedPostRepository
from backend.database.repositories.media import MediaRepository
from backend.models.posts import CompletedPost
from backend.models.media import Image, Video
from backend.services.supabase.storage import StorageService

logger = get_logger(__name__)


# =============================================================================
# MEDIA TYPE MAPPING
# =============================================================================

# Maps Instagram API media_type values to our post_type enum
_IG_MEDIA_TYPE_TO_POST_TYPE = {
    "IMAGE": "instagram_image",
    "VIDEO": "instagram_reel",
    "CAROUSEL_ALBUM": "instagram_carousel",
}


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

        publish_platforms = settings.publish_platforms_set

        # Fetch Facebook page insights (only if facebook is in publish_platforms)
        if "facebook" in publish_platforms:
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
        else:
            logger.info(
                "Skipping Facebook page insights (not in publish_platforms)",
                business_asset_id=business_asset_id,
            )

        # Fetch Instagram account insights (only if instagram is in publish_platforms)
        if "instagram" in publish_platforms:
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
        else:
            logger.info(
                "Skipping Instagram account insights (not in publish_platforms)",
                business_asset_id=business_asset_id,
            )

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
        publish_platforms = settings.publish_platforms_set

        # Get completed posts from database
        posts_repo = CompletedPostRepository()
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)

        # Get Facebook posts (only if facebook is in publish_platforms)
        fb_posts = []
        if "facebook" in publish_platforms:
            fb_posts = await posts_repo.get_recent_published_for_insights(
                business_asset_id=business_asset_id,
                platform="facebook",
                limit=limit,
                since=cutoff_date,
            )
        else:
            logger.info(
                "Skipping Facebook post insights (not in publish_platforms)",
                business_asset_id=business_asset_id,
            )

        # Get Instagram posts (only if instagram is in publish_platforms)
        ig_posts = []
        if "instagram" in publish_platforms:
            ig_posts = await posts_repo.get_recent_published_for_insights(
                business_asset_id=business_asset_id,
                platform="instagram",
                limit=limit,
                since=cutoff_date,
            )
        else:
            logger.info(
                "Skipping Instagram post insights (not in publish_platforms)",
                business_asset_id=business_asset_id,
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
# EXTERNAL MEDIA DISCOVERY (for human-managed accounts)
# =============================================================================


async def discover_and_ingest_external_media(
    business_asset_id: str,
    limit: int = 50,
) -> Dict[str, Any]:
    """
    Discover media posted externally (by humans) on Instagram and ingest
    into completed_posts so the metrics pipeline can track them.

    For each media found on the account:
    - Checks if a completed_post with that platform_post_id already exists
    - If not, creates a new completed_post row (task_id=NULL, no seed)
    - Skips already-known posts

    Args:
        business_asset_id: The business asset ID
        limit: Max media items to fetch from Instagram API

    Returns:
        Dictionary with counts of discovered/ingested/skipped media
    """
    logger.info(
        "Discovering external media",
        business_asset_id=business_asset_id,
        limit=limit,
    )

    result = {
        "discovered": 0,
        "ingested": 0,
        "skipped": 0,
        "errors": [],
    }

    try:
        # Fetch recent media from Instagram API
        ig_service = InstagramInsightsService(business_asset_id)
        media_list = await ig_service.fetch_recent_media_list(limit=limit)
        result["discovered"] = len(media_list)

        if not media_list:
            logger.info("No media found on account", business_asset_id=business_asset_id)
            return result

        # Get existing platform_post_ids to avoid duplicates
        posts_repo = CompletedPostRepository()
        existing_posts = await posts_repo.get_recent_published_for_insights(
            business_asset_id=business_asset_id,
            platform="instagram",
            limit=500,
            since=datetime.now(timezone.utc) - timedelta(days=365),
        )
        existing_ids = {post.platform_post_id for post in existing_posts if post.platform_post_id}

        for media in media_list:
            media_id = media.get("id")
            if not media_id:
                continue

            # Skip if already ingested
            if media_id in existing_ids:
                result["skipped"] += 1
                continue

            try:
                # Map Instagram media_type to our post_type
                api_media_type = media.get("media_type", "IMAGE")
                post_type = _IG_MEDIA_TYPE_TO_POST_TYPE.get(api_media_type, "instagram_image")

                # Parse timestamp
                timestamp_str = media.get("timestamp")
                published_at = datetime.now(timezone.utc)
                if timestamp_str:
                    published_at = datetime.fromisoformat(timestamp_str.replace("+0000", "+00:00"))

                # Download media from Instagram and upload to Supabase storage
                media_ids = []
                media_url = media.get("media_url")
                thumbnail_url = media.get("thumbnail_url")
                # For videos: download the thumbnail for display, media_url for the video
                download_url = media_url or thumbnail_url

                if download_url:
                    try:
                        import aiohttp
                        async with aiohttp.ClientSession() as session:
                            async with session.get(download_url) as resp:
                                if resp.status == 200:
                                    media_bytes = await resp.read()

                                    storage = StorageService()
                                    media_repo = MediaRepository()
                                    storage_prefix = f"external/{business_asset_id}"

                                    if api_media_type == "VIDEO":
                                        # Upload thumbnail for display
                                        thumb_url = thumbnail_url or media_url
                                        thumb_bytes = media_bytes
                                        if thumbnail_url and thumbnail_url != download_url:
                                            async with session.get(thumbnail_url) as thumb_resp:
                                                if thumb_resp.status == 200:
                                                    thumb_bytes = await thumb_resp.read()

                                        storage_path = f"{storage_prefix}/{media_id}.jpg"
                                        public_url = await storage.upload_media(
                                            storage_path, thumb_bytes, "image/jpeg"
                                        )
                                        video_obj = Video(
                                            business_asset_id=business_asset_id,
                                            storage_path=storage_path,
                                            public_url=public_url,
                                            mime_type="image/jpeg",
                                            created_at=published_at,
                                        )
                                        saved_media = await media_repo.create_video(video_obj)
                                    else:
                                        storage_path = f"{storage_prefix}/{media_id}.jpg"
                                        public_url = await storage.upload_media(
                                            storage_path, media_bytes, "image/jpeg"
                                        )
                                        image_obj = Image(
                                            business_asset_id=business_asset_id,
                                            storage_path=storage_path,
                                            public_url=public_url,
                                            mime_type="image/jpeg",
                                            created_at=published_at,
                                        )
                                        saved_media = await media_repo.create_image(image_obj)

                                    media_ids = [saved_media.id]
                                else:
                                    logger.warning(
                                        "Failed to download media from Instagram",
                                        media_id=media_id,
                                        status=resp.status,
                                    )
                    except Exception as e:
                        logger.warning("Failed to upload media to storage", media_id=media_id, error=str(e))

                # Create completed_post for this external media
                post = CompletedPost(
                    business_asset_id=business_asset_id,
                    task_id=None,
                    platform="instagram",
                    post_type=post_type,
                    text=media.get("caption") or "(external post)",
                    media_ids=media_ids,
                    status="published",
                    verification_status="verified",
                    published_at=published_at,
                    platform_post_id=media_id,
                    platform_post_url=media.get("permalink"),
                    created_at=published_at,
                )

                await posts_repo.create(post)
                result["ingested"] += 1

                logger.debug(
                    "Ingested external media",
                    media_id=media_id,
                    post_type=post_type,
                )

            except Exception as e:
                error_msg = f"Failed to ingest media {media_id}: {e}"
                logger.warning(error_msg)
                result["errors"].append(error_msg)

        logger.info(
            "External media discovery complete",
            business_asset_id=business_asset_id,
            discovered=result["discovered"],
            ingested=result["ingested"],
            skipped=result["skipped"],
            errors=len(result["errors"]),
        )

    except Exception as e:
        error_msg = f"Failed to discover external media: {e}"
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
