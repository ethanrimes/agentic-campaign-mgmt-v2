# backend/services/meta/insights/instagram_insights.py

"""
Instagram Insights fetching service.

Fetches account-level and media-level metrics from the
Instagram Graph API and stores them in the database cache.
"""

import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone

from backend.services.meta.base import MetaBaseClient
from backend.models.insights import (
    InstagramAccountInsights,
    InstagramMediaInsights,
)
from backend.utils import get_logger

logger = get_logger(__name__)


class InstagramInsightsService(MetaBaseClient):
    """
    Service for fetching and caching Instagram insights.

    Provides methods to fetch:
    - Account-level metrics (reach, followers, profile info)
    - Media-level metrics (likes, comments, saves, shares, views, watch time)
    """

    # =========================================================================
    # ACCOUNT-LEVEL INSIGHTS
    # =========================================================================

    async def fetch_account_insights(self, days_back: int = 28) -> InstagramAccountInsights:
        """
        Fetch account-level insights from Instagram Graph API.

        Args:
            days_back: Number of days to look back for reach metrics

        Returns:
            InstagramAccountInsights object with all metrics
        """
        logger.info("Fetching Instagram account insights", ig_user_id=self.ig_user_id, days_back=days_back)

        # Initialize insights object
        insights = InstagramAccountInsights(
            business_asset_id=self.business_asset_id,
            ig_user_id=self.ig_user_id,
        )

        # Fetch account metadata
        await self._fetch_account_metadata(insights)

        # Fetch account insights metrics
        await self._fetch_account_metrics(insights, days_back)

        insights.metrics_fetched_at = datetime.now(timezone.utc)

        logger.info(
            "Fetched Instagram account insights",
            username=insights.username,
            followers=insights.followers_count,
            reach_day=insights.reach_day,
        )

        return insights

    async def _fetch_account_metadata(self, insights: InstagramAccountInsights) -> None:
        """Fetch account metadata (username, name, bio, followers, etc.)."""
        try:
            url = f"{self.INSTAGRAM_BASE_URL}/{self.ig_user_id}"
            params = {
                "fields": "username,name,biography,followers_count,follows_count,media_count,profile_picture_url",
                "access_token": self.ig_token,
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        insights.username = data.get("username")
                        insights.name = data.get("name")
                        insights.biography = data.get("biography")
                        insights.followers_count = data.get("followers_count", 0)
                        insights.follows_count = data.get("follows_count", 0)
                        insights.media_count = data.get("media_count", 0)
                        insights.profile_picture_url = data.get("profile_picture_url")
                        logger.debug("Fetched account metadata", username=insights.username)
                    else:
                        error_text = await response.text()
                        logger.warning("Failed to fetch account metadata", error=error_text)
        except Exception as e:
            logger.warning("Error fetching account metadata", error=str(e))

    async def _fetch_account_metrics(self, insights: InstagramAccountInsights, days_back: int) -> None:
        """Fetch account-level insights metrics."""
        until = int(datetime.now(timezone.utc).timestamp())
        since = int((datetime.now(timezone.utc) - timedelta(days=days_back)).timestamp())

        raw_metrics = {}

        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.INSTAGRAM_BASE_URL}/{self.ig_user_id}/insights"

                # Fetch daily reach
                params = {
                    "metric": "reach",
                    "period": "day",
                    "since": since,
                    "until": until,
                    "access_token": self.ig_token,
                }

                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        raw_metrics["reach_day"] = data.get("data", [])

                        for metric in data.get("data", []):
                            if metric.get("name") == "reach":
                                # Sum up daily reach values
                                for v in metric.get("values", []):
                                    val = v.get("value", 0)
                                    if isinstance(val, int):
                                        insights.reach_day += val

                # Fetch weekly reach
                params["period"] = "week"
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        raw_metrics["reach_week"] = data.get("data", [])

                        for metric in data.get("data", []):
                            if metric.get("name") == "reach":
                                # Get the most recent week value
                                values = metric.get("values", [])
                                if values:
                                    val = values[-1].get("value", 0)
                                    insights.reach_week = val if isinstance(val, int) else 0

                # Fetch 28-day reach
                params["period"] = "days_28"
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        raw_metrics["reach_days_28"] = data.get("data", [])

                        for metric in data.get("data", []):
                            if metric.get("name") == "reach":
                                values = metric.get("values", [])
                                if values:
                                    val = values[-1].get("value", 0)
                                    insights.reach_days_28 = val if isinstance(val, int) else 0

        except Exception as e:
            logger.error("Error fetching account metrics", error=str(e), exc_info=True)

        insights.raw_metrics = raw_metrics

    # =========================================================================
    # MEDIA-LEVEL INSIGHTS
    # =========================================================================

    async def fetch_media_insights(
        self,
        media_id: str,
        media_type: str = None
    ) -> Optional[InstagramMediaInsights]:
        """
        Fetch media-level insights for an Instagram post or reel.

        Args:
            media_id: The Instagram media ID
            media_type: Optional hint about media type ('image', 'video', 'carousel', 'reel')

        Returns:
            InstagramMediaInsights object or None if error
        """
        logger.info("Fetching Instagram media insights", media_id=media_id, media_type=media_type)

        insights = InstagramMediaInsights(
            business_asset_id=self.business_asset_id,
            platform_media_id=media_id,
            media_type=media_type,
        )

        raw_metrics = {}

        try:
            async with aiohttp.ClientSession() as session:
                # First, fetch basic media fields
                media_url = f"{self.INSTAGRAM_BASE_URL}/{media_id}"
                media_params = {
                    "fields": "id,media_type,like_count,comments_count,permalink",
                    "access_token": self.ig_token,
                }

                async with session.get(media_url, params=media_params) as response:
                    if response.status == 200:
                        data = await response.json()
                        raw_metrics["media_fields"] = data

                        insights.likes = data.get("like_count", 0)
                        insights.comments = data.get("comments_count", 0)
                        insights.permalink = data.get("permalink")

                        # Determine media type from API
                        api_media_type = data.get("media_type", "").upper()
                        if api_media_type == "VIDEO":
                            insights.media_type = "reel"
                        elif api_media_type == "CAROUSEL_ALBUM":
                            insights.media_type = "carousel"
                        elif api_media_type == "IMAGE":
                            insights.media_type = "image"

                # Determine which insights metrics to request based on media type
                # Note: 'impressions' is deprecated for media created after July 2024 (API v22.0+)
                if insights.media_type in ("reel", "video"):
                    # Reel metrics
                    metrics = "comments,likes,saved,shares,views,reach,ig_reels_avg_watch_time,ig_reels_video_view_total_time"
                else:
                    # Feed post metrics (no reel-specific metrics)
                    metrics = "comments,likes,saved,shares,views,reach"

                # Fetch insights metrics
                insights_url = f"{self.INSTAGRAM_BASE_URL}/{media_id}/insights"
                insights_params = {
                    "metric": metrics,
                    "access_token": self.ig_token,
                }

                async with session.get(insights_url, params=insights_params) as response:
                    if response.status == 200:
                        data = await response.json()
                        raw_metrics["insights"] = data.get("data", [])

                        for metric in data.get("data", []):
                            name = metric.get("name")
                            values = metric.get("values", [])
                            if not values:
                                continue

                            value = values[0].get("value", 0)

                            if name == "comments":
                                insights.comments = value if isinstance(value, int) else 0
                            elif name == "likes":
                                insights.likes = value if isinstance(value, int) else 0
                            elif name == "saved":
                                insights.saved = value if isinstance(value, int) else 0
                            elif name == "shares":
                                insights.shares = value if isinstance(value, int) else 0
                            elif name == "views":
                                insights.views = value if isinstance(value, int) else 0
                            elif name == "reach":
                                insights.reach = value if isinstance(value, int) else 0
                            elif name == "ig_reels_avg_watch_time":
                                insights.ig_reels_avg_watch_time_ms = value if isinstance(value, int) else 0
                            elif name == "ig_reels_video_view_total_time":
                                insights.ig_reels_video_view_total_time_ms = value if isinstance(value, int) else 0
                    else:
                        error_text = await response.text()
                        logger.warning(
                            "Failed to fetch media insights",
                            media_id=media_id,
                            error=error_text
                        )
                        # Return partial data if we have some fields
                        if insights.likes > 0 or insights.comments > 0 or insights.permalink:
                            insights.raw_metrics = raw_metrics
                            insights.metrics_fetched_at = datetime.now(timezone.utc)
                            return insights
                        return None

        except Exception as e:
            logger.error("Error fetching media insights", media_id=media_id, error=str(e))
            return None

        insights.raw_metrics = raw_metrics
        insights.metrics_fetched_at = datetime.now(timezone.utc)

        logger.info(
            "Fetched Instagram media insights",
            media_id=media_id,
            likes=insights.likes,
            comments=insights.comments,
            views=insights.views,
            reach=insights.reach,
        )

        return insights

    async def fetch_recent_media_list(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch list of recent media from the Instagram account.

        Args:
            limit: Maximum number of media to return

        Returns:
            List of media dictionaries with id and basic info
        """
        logger.info("Fetching Instagram media list", limit=limit)

        media_list = []

        try:
            url = f"{self.INSTAGRAM_BASE_URL}/{self.ig_user_id}/media"
            params = {
                "fields": "id,media_type,timestamp,permalink",
                "limit": min(limit, 100),  # API max is 100
                "access_token": self.ig_token,
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        media_list = data.get("data", [])

                        # Handle pagination if we need more
                        while len(media_list) < limit:
                            paging = data.get("paging", {})
                            next_url = paging.get("next")
                            if not next_url:
                                break

                            async with session.get(next_url) as next_response:
                                if next_response.status == 200:
                                    data = await next_response.json()
                                    media_list.extend(data.get("data", []))
                                else:
                                    break

                        # Trim to limit
                        media_list = media_list[:limit]

                    else:
                        error_text = await response.text()
                        logger.warning("Failed to fetch media list", error=error_text)

        except Exception as e:
            logger.error("Error fetching media list", error=str(e))

        logger.info("Fetched Instagram media list", count=len(media_list))
        return media_list
