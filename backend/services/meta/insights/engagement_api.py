# backend/services/meta/insights/engagement_api.py

"""
Engagement metrics API for Facebook and Instagram.
Used by the insights agent to analyze what content works.
"""

from typing import Dict, Any, List
from backend.utils import get_logger
from backend.services.meta.base import MetaBaseClient

logger = get_logger(__name__)


class EngagementAPI(MetaBaseClient):
    """
    API for retrieving engagement metrics and comments.

    Used by the insights agent to understand what content resonates
    with the audience.
    """

    async def get_facebook_post_metrics(self, post_id: str) -> Dict[str, Any]:
        """
        Get engagement metrics for a Facebook post.

        Args:
            post_id: Facebook post ID

        Returns:
            Dictionary with likes, comments, shares, reach, etc.
        """
        logger.info("Fetching Facebook post metrics", post_id=post_id)

        url = f"{self.BASE_URL}/{post_id}"
        params = f"?fields=likes.summary(true),comments.summary(true),shares,insights.metric(post_impressions,post_engaged_users)&access_token={self.page_token}"

        try:
            result = await self._make_request("GET", url + params)

            metrics = {
                "post_id": post_id,
                "likes": result.get("likes", {}).get("summary", {}).get("total_count", 0),
                "comments": result.get("comments", {}).get("summary", {}).get("total_count", 0),
                "shares": result.get("shares", {}).get("count", 0),
                "reach": 0,  # From insights
                "engagement": 0,  # From insights
            }

            # Extract insights if available
            insights = result.get("insights", {}).get("data", [])
            for insight in insights:
                if insight["name"] == "post_impressions":
                    metrics["reach"] = insight["values"][0]["value"]
                elif insight["name"] == "post_engaged_users":
                    metrics["engagement"] = insight["values"][0]["value"]

            logger.info("Fetched Facebook metrics", metrics=metrics)
            return metrics

        except Exception as e:
            logger.error("Failed to fetch Facebook metrics", error=str(e))
            return {"error": str(e)}

    async def get_instagram_post_metrics(self, media_id: str) -> Dict[str, Any]:
        """
        Get engagement metrics for an Instagram post.

        Args:
            media_id: Instagram media ID

        Returns:
            Dictionary with likes, comments, reach, etc.
        """
        logger.info("Fetching Instagram post metrics", media_id=media_id)

        url = f"{self.BASE_URL}/{media_id}"
        params = f"?fields=like_count,comments_count,insights.metric(impressions,reach,engagement)&access_token={self.ig_token}"

        try:
            result = await self._make_request("GET", url + params)

            metrics = {
                "media_id": media_id,
                "likes": result.get("like_count", 0),
                "comments": result.get("comments_count", 0),
                "impressions": 0,
                "reach": 0,
                "engagement": 0,
            }

            # Extract insights
            insights = result.get("insights", {}).get("data", [])
            for insight in insights:
                name = insight["name"]
                value = insight["values"][0]["value"]
                if name in metrics:
                    metrics[name] = value

            logger.info("Fetched Instagram metrics", metrics=metrics)
            return metrics

        except Exception as e:
            logger.error("Failed to fetch Instagram metrics", error=str(e))
            return {"error": str(e)}

    async def get_facebook_post_comments(self, post_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get comments on a Facebook post.

        Args:
            post_id: Facebook post ID
            limit: Maximum comments to retrieve

        Returns:
            List of comment dictionaries
        """
        url = f"{self.BASE_URL}/{post_id}/comments"
        params = f"?fields=id,message,from,created_time,like_count&limit={limit}&access_token={self.page_token}"

        try:
            result = await self._make_request("GET", url + params)
            comments = result.get("data", [])
            logger.info("Fetched Facebook comments", count=len(comments))
            return comments
        except Exception as e:
            logger.error("Failed to fetch Facebook comments", error=str(e))
            return []

    async def get_instagram_post_comments(self, media_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get comments on an Instagram post.

        Args:
            media_id: Instagram media ID
            limit: Maximum comments to retrieve

        Returns:
            List of comment dictionaries
        """
        url = f"{self.BASE_URL}/{media_id}/comments"
        params = f"?fields=id,text,username,timestamp,like_count&limit={limit}&access_token={self.ig_token}"

        try:
            result = await self._make_request("GET", url + params)
            comments = result.get("data", [])
            logger.info("Fetched Instagram comments", count=len(comments))
            return comments
        except Exception as e:
            logger.error("Failed to fetch Instagram comments", error=str(e))
            return []
