# backend/services/meta/insights/facebook_insights.py

"""
Facebook Insights fetching service.

Fetches page-level, post-level, and video-level metrics from the
Facebook Graph API and stores them in the database cache.
"""

import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone

from backend.services.meta.base import MetaBaseClient
from backend.config.business_asset_loader import get_business_asset_credentials
from backend.models.insights import (
    FacebookPageInsights,
    FacebookPostInsights,
    FacebookVideoInsights,
)
from backend.utils import get_logger

logger = get_logger(__name__)


class FacebookInsightsService(MetaBaseClient):
    """
    Service for fetching and caching Facebook insights.

    Provides methods to fetch:
    - Page-level metrics (views, engagement, reactions, video views)
    - Post-level metrics (media views, impressions, reactions)
    - Video-level metrics (views, watch time, retention)
    """

    # =========================================================================
    # PAGE-LEVEL INSIGHTS
    # =========================================================================

    async def fetch_page_insights(self, days_back: int = 28) -> FacebookPageInsights:
        """
        Fetch page-level insights from Facebook Graph API.

        Args:
            days_back: Number of days to look back for time-series metrics

        Returns:
            FacebookPageInsights object with all metrics
        """
        logger.info("Fetching Facebook page insights", page_id=self.page_id, days_back=days_back)

        until = datetime.now(timezone.utc)
        since = until - timedelta(days=min(days_back, 90))

        # Initialize insights object
        insights = FacebookPageInsights(
            business_asset_id=self.business_asset_id,
            page_id=self.page_id,
        )

        # Fetch page metadata (name and picture)
        await self._fetch_page_metadata(insights)

        # Fetch page insights metrics
        await self._fetch_page_metrics(insights, since, until)

        insights.metrics_fetched_at = datetime.now(timezone.utc)

        logger.info(
            "Fetched Facebook page insights",
            page_views=insights.page_views_total,
            page_follows=insights.page_follows,
            engagements=insights.page_post_engagements,
        )

        return insights

    async def _fetch_page_metadata(self, insights: FacebookPageInsights) -> None:
        """Fetch page name and profile picture."""
        try:
            url = f"{self.BASE_URL}/{self.page_id}"
            params = {
                "fields": "name,picture{url}",
                "access_token": self.page_token,
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        insights.page_name = data.get("name")
                        picture_data = data.get("picture", {}).get("data", {})
                        insights.page_picture_url = picture_data.get("url")
                        logger.debug("Fetched page metadata", name=insights.page_name)
        except Exception as e:
            logger.warning("Failed to fetch page metadata", error=str(e))

    async def _fetch_page_metrics(
        self,
        insights: FacebookPageInsights,
        since: datetime,
        until: datetime
    ) -> None:
        """Fetch page-level metrics from the insights endpoint."""

        # Define metrics to fetch for each period
        day_metrics = [
            "page_views_total",
            "page_total_actions",
            "page_post_engagements",
            "page_follows",
            "page_media_view",
            "page_actions_post_reactions_like_total",
            "page_actions_post_reactions_love_total",
            "page_actions_post_reactions_wow_total",
            "page_actions_post_reactions_haha_total",
            "page_actions_post_reactions_sorry_total",
            "page_actions_post_reactions_anger_total",
            "page_video_views",
        ]

        raw_metrics = {}

        try:
            async with aiohttp.ClientSession() as session:
                # Fetch day period metrics
                url = f"{self.BASE_URL}/{self.page_id}/insights"
                params = {
                    "metric": ",".join(day_metrics),
                    "period": "day",
                    "since": int(since.timestamp()),
                    "until": int(until.timestamp()),
                    "access_token": self.page_token,
                }

                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        self._process_page_metrics(insights, data.get("data", []), "day")
                        raw_metrics["day"] = data.get("data", [])
                    else:
                        error_text = await response.text()
                        logger.warning("Failed to fetch day metrics", error=error_text)

                # Fetch week period metrics
                week_metrics = [
                    "page_views_total",
                    "page_post_engagements",
                    "page_media_view",
                    "page_video_views",
                ]
                params["metric"] = ",".join(week_metrics)
                params["period"] = "week"

                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        self._process_page_metrics(insights, data.get("data", []), "week")
                        raw_metrics["week"] = data.get("data", [])

                # Fetch days_28 period metrics
                days28_metrics = [
                    "page_views_total",
                    "page_total_actions",
                    "page_post_engagements",
                    "page_media_view",
                    "page_video_views",
                ]
                params["metric"] = ",".join(days28_metrics)
                params["period"] = "days_28"

                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        self._process_page_metrics(insights, data.get("data", []), "days_28")
                        raw_metrics["days_28"] = data.get("data", [])

                # Fetch page_media_view with breakdown
                breakdown_url = f"{self.BASE_URL}/{self.page_id}/insights"
                breakdown_params = {
                    "metric": "page_media_view",
                    "period": "day",
                    "breakdown": "is_from_followers",
                    "since": int(since.timestamp()),
                    "until": int(until.timestamp()),
                    "access_token": self.page_token,
                }

                async with session.get(breakdown_url, params=breakdown_params) as response:
                    if response.status == 200:
                        data = await response.json()
                        self._process_media_view_breakdown(insights, data.get("data", []))
                        raw_metrics["media_view_breakdown"] = data.get("data", [])

        except Exception as e:
            logger.error("Error fetching page metrics", error=str(e), exc_info=True)

        insights.raw_metrics = raw_metrics

    def _process_page_metrics(
        self,
        insights: FacebookPageInsights,
        metrics_data: List[Dict[str, Any]],
        period: str
    ) -> None:
        """Process page metrics from API response.

        For 'day' period: Sum all daily values to get the total over the time range.
        For 'week' and 'days_28' periods: Take only the most recent value, since
        each value already represents a rolling total (7-day or 28-day respectively).
        """
        for metric in metrics_data:
            name = metric.get("name")
            values = metric.get("values", [])

            if period == "day":
                # Sum up all daily values for the period
                total = 0
                for v in values:
                    val = v.get("value", 0)
                    if isinstance(val, (int, float)):
                        total += val
            else:
                # For week and days_28: each value is already a rolling total,
                # so we only need the most recent value
                total = 0
                if values:
                    # Get the most recent value (last in the array)
                    val = values[-1].get("value", 0)
                    if isinstance(val, (int, float)):
                        total = val

            # Map to insights fields
            if period == "day":
                if name == "page_views_total":
                    insights.page_views_total = total
                elif name == "page_total_actions":
                    insights.page_total_actions = total
                elif name == "page_post_engagements":
                    insights.page_post_engagements = total
                elif name == "page_follows":
                    insights.page_follows = total
                elif name == "page_media_view":
                    insights.page_media_view = total
                elif name == "page_actions_post_reactions_like_total":
                    insights.reactions_like_total = total
                elif name == "page_actions_post_reactions_love_total":
                    insights.reactions_love_total = total
                elif name == "page_actions_post_reactions_wow_total":
                    insights.reactions_wow_total = total
                elif name == "page_actions_post_reactions_haha_total":
                    insights.reactions_haha_total = total
                elif name == "page_actions_post_reactions_sorry_total":
                    insights.reactions_sorry_total = total
                elif name == "page_actions_post_reactions_anger_total":
                    insights.reactions_anger_total = total
                elif name == "page_video_views":
                    insights.page_video_views = total

            elif period == "week":
                if name == "page_views_total":
                    insights.page_views_total_week = total
                elif name == "page_post_engagements":
                    insights.page_post_engagements_week = total
                elif name == "page_media_view":
                    insights.page_media_view_week = total
                elif name == "page_video_views":
                    insights.page_video_views_week = total

            elif period == "days_28":
                if name == "page_views_total":
                    insights.page_views_total_days_28 = total
                elif name == "page_total_actions":
                    insights.page_total_actions_days_28 = total
                elif name == "page_post_engagements":
                    insights.page_post_engagements_days_28 = total
                elif name == "page_media_view":
                    insights.page_media_view_days_28 = total
                elif name == "page_video_views":
                    insights.page_video_views_days_28 = total

    def _process_media_view_breakdown(
        self,
        insights: FacebookPageInsights,
        metrics_data: List[Dict[str, Any]]
    ) -> None:
        """Process page_media_view with is_from_followers breakdown."""
        for metric in metrics_data:
            if metric.get("name") != "page_media_view":
                continue

            for v in metric.get("values", []):
                val = v.get("value", {})
                if isinstance(val, dict):
                    insights.page_media_view_from_followers += val.get("followers", 0)
                    insights.page_media_view_from_non_followers += val.get("non_followers", 0)

    # =========================================================================
    # POST-LEVEL INSIGHTS
    # =========================================================================

    async def fetch_post_insights(self, platform_post_id: str) -> Optional[FacebookPostInsights]:
        """
        Fetch post-level insights for a Facebook feed post or photo.

        Args:
            platform_post_id: The Facebook post ID

        Returns:
            FacebookPostInsights object or None if error
        """
        logger.info("Fetching Facebook post insights", post_id=platform_post_id)

        # Construct full post ID if needed
        if "_" in platform_post_id:
            full_post_id = platform_post_id
        else:
            full_post_id = f"{self.page_id}_{platform_post_id}"

        insights = FacebookPostInsights(
            business_asset_id=self.business_asset_id,
            platform_post_id=platform_post_id,
        )

        raw_metrics = {}

        try:
            async with aiohttp.ClientSession() as session:
                # Fetch post insights metrics
                url = f"{self.BASE_URL}/{full_post_id}/insights"
                metrics = [
                    "post_media_view",
                    "post_impressions_unique",
                    "post_impressions_organic_unique",
                    "post_reactions_like_total",
                    "post_reactions_love_total",
                    "post_reactions_wow_total",
                    "post_reactions_haha_total",
                    "post_reactions_sorry_total",
                    "post_reactions_anger_total",
                    "post_reactions_by_type_total",
                ]
                params = {
                    "metric": ",".join(metrics),
                    "access_token": self.page_token,
                }

                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.warning(
                            "Failed to fetch post insights",
                            post_id=platform_post_id,
                            error=error_text
                        )
                        return None

                    data = await response.json()
                    raw_metrics["insights"] = data.get("data", [])

                    for metric in data.get("data", []):
                        name = metric.get("name")
                        values = metric.get("values", [])
                        if not values:
                            continue

                        value = values[0].get("value", 0)

                        if name == "post_media_view":
                            insights.post_media_view = value if isinstance(value, int) else 0
                        elif name == "post_impressions_unique":
                            insights.post_impressions_unique = value if isinstance(value, int) else 0
                        elif name == "post_impressions_organic_unique":
                            insights.post_impressions_organic_unique = value if isinstance(value, int) else 0
                        elif name == "post_reactions_like_total":
                            insights.reactions_like = value if isinstance(value, int) else 0
                        elif name == "post_reactions_love_total":
                            insights.reactions_love = value if isinstance(value, int) else 0
                        elif name == "post_reactions_wow_total":
                            insights.reactions_wow = value if isinstance(value, int) else 0
                        elif name == "post_reactions_haha_total":
                            insights.reactions_haha = value if isinstance(value, int) else 0
                        elif name == "post_reactions_sorry_total":
                            insights.reactions_sorry = value if isinstance(value, int) else 0
                        elif name == "post_reactions_anger_total":
                            insights.reactions_anger = value if isinstance(value, int) else 0
                        elif name == "post_reactions_by_type_total":
                            if isinstance(value, dict):
                                insights.reactions_by_type = value

                # Try to fetch post_media_view with breakdown
                breakdown_params = {
                    "metric": "post_media_view",
                    "breakdown": "is_from_followers",
                    "access_token": self.page_token,
                }

                async with session.get(url, params=breakdown_params) as response:
                    if response.status == 200:
                        data = await response.json()
                        raw_metrics["media_view_breakdown"] = data.get("data", [])

                        for metric in data.get("data", []):
                            if metric.get("name") != "post_media_view":
                                continue
                            for v in metric.get("values", []):
                                val = v.get("value", {})
                                if isinstance(val, dict):
                                    insights.post_media_view_from_followers = val.get("followers", 0)
                                    insights.post_media_view_from_non_followers = val.get("non_followers", 0)

        except Exception as e:
            logger.error("Error fetching post insights", post_id=platform_post_id, error=str(e))
            return None

        insights.raw_metrics = raw_metrics
        insights.metrics_fetched_at = datetime.now(timezone.utc)

        logger.info(
            "Fetched Facebook post insights",
            post_id=platform_post_id,
            impressions=insights.post_impressions_unique,
            reactions=insights.total_reactions,
        )

        return insights

    # =========================================================================
    # VIDEO-LEVEL INSIGHTS
    # =========================================================================

    async def fetch_video_insights(self, video_id: str) -> Optional[FacebookVideoInsights]:
        """
        Fetch video-level insights for a Facebook video or reel.

        Uses the video node's fields approach rather than the /video_insights edge,
        which can be unreliable for certain video types (especially reels).

        Args:
            video_id: The Facebook video ID

        Returns:
            FacebookVideoInsights object or None if error
        """
        logger.info("Fetching Facebook video insights", video_id=video_id)

        insights = FacebookVideoInsights(
            business_asset_id=self.business_asset_id,
            platform_video_id=video_id,
        )

        raw_metrics = {}

        try:
            async with aiohttp.ClientSession() as session:
                # Use the video node with video_insights as a field
                # This approach is more reliable than the /video_insights edge
                url = f"{self.BASE_URL}/{video_id}"
                params = {
                    "fields": "id,video_insights,length",
                    "access_token": self.page_token,
                }

                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.warning(
                            "Failed to fetch video insights",
                            video_id=video_id,
                            error=error_text
                        )
                        return None

                    data = await response.json()
                    raw_metrics["video_data"] = data

                    # Get video length from the video object itself
                    if "length" in data:
                        # length is in seconds, convert to ms
                        insights.post_video_length_ms = int(data["length"] * 1000)

                    # Process video_insights
                    video_insights_data = data.get("video_insights", {}).get("data", [])
                    raw_metrics["video_insights"] = video_insights_data

                    for metric in video_insights_data:
                        name = metric.get("name")
                        values = metric.get("values", [])
                        if not values:
                            continue

                        value = values[0].get("value", 0)

                        # Map the metric names to our model fields
                        if name == "post_video_views":
                            insights.post_video_views = value if isinstance(value, int) else 0
                        elif name == "post_video_views_unique":
                            insights.post_video_views_unique = value if isinstance(value, int) else 0
                        elif name == "post_video_view_time":
                            insights.post_video_view_time_ms = value if isinstance(value, int) else 0
                        elif name == "post_video_avg_time_watched":
                            insights.post_video_avg_time_watched_ms = value if isinstance(value, int) else 0
                        elif name == "post_video_length":
                            insights.post_video_length_ms = value if isinstance(value, int) else 0
                        # Reel-specific metrics
                        elif name == "blue_reels_play_count":
                            insights.post_video_views = value if isinstance(value, int) else 0
                        elif name == "fb_reels_total_plays":
                            # Use total plays if views not available
                            if not insights.post_video_views:
                                insights.post_video_views = value if isinstance(value, int) else 0
                        elif name == "post_impressions_unique":
                            insights.post_video_views_unique = value if isinstance(value, int) else 0

        except Exception as e:
            logger.error("Error fetching video insights", video_id=video_id, error=str(e))
            return None

        insights.raw_metrics = raw_metrics
        insights.metrics_fetched_at = datetime.now(timezone.utc)

        logger.info(
            "Fetched Facebook video insights",
            video_id=video_id,
            views=insights.post_video_views,
            avg_watch_time_ms=insights.post_video_avg_time_watched_ms,
        )

        return insights
