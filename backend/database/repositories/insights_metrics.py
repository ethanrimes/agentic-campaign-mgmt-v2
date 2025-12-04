# backend/database/repositories/insights_metrics.py

"""
Repository classes for cached insights metrics.

Provides database operations for storing and retrieving
Facebook and Instagram insights data.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timezone, timedelta
from backend.database import get_supabase_admin_client
from backend.models.insights import (
    FacebookPageInsights,
    FacebookPostInsights,
    FacebookVideoInsights,
    InstagramAccountInsights,
    InstagramMediaInsights,
)
from backend.utils import get_logger, DatabaseError

logger = get_logger(__name__)


# =============================================================================
# FACEBOOK PAGE INSIGHTS REPOSITORY
# =============================================================================


class FacebookPageInsightsRepository:
    """Repository for Facebook page-level insights."""

    TABLE_NAME = "facebook_page_insights"

    async def upsert(self, insights: FacebookPageInsights) -> FacebookPageInsights:
        """
        Insert or update page insights.

        Uses ON CONFLICT to update existing row for the same business_asset_id and page_id.

        Args:
            insights: FacebookPageInsights instance

        Returns:
            Upserted insights instance
        """
        try:
            client = await get_supabase_admin_client()
            data = insights.model_dump(mode="json", exclude_unset=True, exclude={"id", "created_at", "updated_at"})

            result = await client.table(self.TABLE_NAME).upsert(
                data,
                on_conflict="business_asset_id"
            ).execute()

            if not result.data:
                raise DatabaseError("Failed to upsert Facebook page insights")

            return FacebookPageInsights(**result.data[0])
        except Exception as e:
            logger.error(
                "Failed to upsert Facebook page insights",
                business_asset_id=insights.business_asset_id,
                page_id=insights.page_id,
                error=str(e),
            )
            raise DatabaseError(f"Failed to upsert page insights: {e}")

    async def get_by_page_id(
        self,
        business_asset_id: str,
        page_id: str
    ) -> Optional[FacebookPageInsights]:
        """
        Get page insights by page ID.

        Args:
            business_asset_id: Business asset ID
            page_id: Facebook page ID

        Returns:
            FacebookPageInsights if found, None otherwise
        """
        try:
            client = await get_supabase_admin_client()
            result = (
                await client.table(self.TABLE_NAME)
                .select("*")
                .eq("business_asset_id", business_asset_id)
                .eq("page_id", page_id)
                .execute()
            )

            if not result.data:
                return None

            return FacebookPageInsights(**result.data[0])
        except Exception as e:
            logger.error(
                "Failed to get Facebook page insights",
                business_asset_id=business_asset_id,
                page_id=page_id,
                error=str(e),
            )
            raise DatabaseError(f"Failed to get page insights: {e}")

    async def get_latest(self, business_asset_id: str) -> Optional[FacebookPageInsights]:
        """
        Get the most recently updated page insights for a business asset.

        Args:
            business_asset_id: Business asset ID

        Returns:
            Most recent FacebookPageInsights if found, None otherwise
        """
        try:
            client = await get_supabase_admin_client()
            result = (
                await client.table(self.TABLE_NAME)
                .select("*")
                .eq("business_asset_id", business_asset_id)
                .order("metrics_fetched_at", desc=True)
                .limit(1)
                .execute()
            )

            if not result.data:
                return None

            return FacebookPageInsights(**result.data[0])
        except Exception as e:
            logger.error(
                "Failed to get latest Facebook page insights",
                business_asset_id=business_asset_id,
                error=str(e),
            )
            raise DatabaseError(f"Failed to get latest page insights: {e}")


# =============================================================================
# FACEBOOK POST INSIGHTS REPOSITORY
# =============================================================================


class FacebookPostInsightsRepository:
    """Repository for Facebook post-level insights."""

    TABLE_NAME = "facebook_post_insights"

    async def upsert(self, insights: FacebookPostInsights) -> FacebookPostInsights:
        """
        Insert or update post insights.

        Args:
            insights: FacebookPostInsights instance

        Returns:
            Upserted insights instance
        """
        try:
            client = await get_supabase_admin_client()
            data = insights.model_dump(mode="json", exclude_unset=True, exclude={"id", "created_at", "updated_at"})

            result = await client.table(self.TABLE_NAME).upsert(
                data,
                on_conflict="business_asset_id,platform_post_id"
            ).execute()

            if not result.data:
                raise DatabaseError("Failed to upsert Facebook post insights")

            return FacebookPostInsights(**result.data[0])
        except Exception as e:
            logger.error(
                "Failed to upsert Facebook post insights",
                business_asset_id=insights.business_asset_id,
                post_id=insights.platform_post_id,
                error=str(e),
            )
            raise DatabaseError(f"Failed to upsert post insights: {e}")

    async def get_by_post_id(
        self,
        business_asset_id: str,
        platform_post_id: str
    ) -> Optional[FacebookPostInsights]:
        """
        Get post insights by post ID.

        Args:
            business_asset_id: Business asset ID
            platform_post_id: Facebook post ID

        Returns:
            FacebookPostInsights if found, None otherwise
        """
        try:
            client = await get_supabase_admin_client()
            result = (
                await client.table(self.TABLE_NAME)
                .select("*")
                .eq("business_asset_id", business_asset_id)
                .eq("platform_post_id", platform_post_id)
                .execute()
            )

            if not result.data:
                return None

            return FacebookPostInsights(**result.data[0])
        except Exception as e:
            logger.error(
                "Failed to get Facebook post insights",
                business_asset_id=business_asset_id,
                post_id=platform_post_id,
                error=str(e),
            )
            raise DatabaseError(f"Failed to get post insights: {e}")

    async def get_recent(
        self,
        business_asset_id: str,
        limit: int = 50,
        days_back: int = 30
    ) -> List[FacebookPostInsights]:
        """
        Get recent post insights.

        Args:
            business_asset_id: Business asset ID
            limit: Maximum posts to return
            days_back: Only include posts from the last N days

        Returns:
            List of FacebookPostInsights
        """
        try:
            client = await get_supabase_admin_client()
            cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)

            result = (
                await client.table(self.TABLE_NAME)
                .select("*")
                .eq("business_asset_id", business_asset_id)
                .gte("post_created_time", cutoff.isoformat())
                .order("post_created_time", desc=True)
                .limit(limit)
                .execute()
            )

            return [FacebookPostInsights(**item) for item in result.data]
        except Exception as e:
            logger.error(
                "Failed to get recent Facebook post insights",
                business_asset_id=business_asset_id,
                error=str(e),
            )
            raise DatabaseError(f"Failed to get recent post insights: {e}")

    async def get_all_for_business(
        self,
        business_asset_id: str,
        limit: int = 100
    ) -> List[FacebookPostInsights]:
        """
        Get all post insights for a business asset.

        Args:
            business_asset_id: Business asset ID
            limit: Maximum posts to return

        Returns:
            List of FacebookPostInsights
        """
        try:
            client = await get_supabase_admin_client()
            result = (
                await client.table(self.TABLE_NAME)
                .select("*")
                .eq("business_asset_id", business_asset_id)
                .order("post_created_time", desc=True)
                .limit(limit)
                .execute()
            )

            return [FacebookPostInsights(**item) for item in result.data]
        except Exception as e:
            logger.error(
                "Failed to get all Facebook post insights",
                business_asset_id=business_asset_id,
                error=str(e),
            )
            raise DatabaseError(f"Failed to get all post insights: {e}")


# =============================================================================
# FACEBOOK VIDEO INSIGHTS REPOSITORY
# =============================================================================


class FacebookVideoInsightsRepository:
    """Repository for Facebook video-level insights."""

    TABLE_NAME = "facebook_video_insights"

    async def upsert(self, insights: FacebookVideoInsights) -> FacebookVideoInsights:
        """
        Insert or update video insights.

        Args:
            insights: FacebookVideoInsights instance

        Returns:
            Upserted insights instance
        """
        try:
            client = await get_supabase_admin_client()
            data = insights.model_dump(mode="json", exclude_unset=True, exclude={"id", "created_at", "updated_at"})

            result = await client.table(self.TABLE_NAME).upsert(
                data,
                on_conflict="business_asset_id,platform_video_id"
            ).execute()

            if not result.data:
                raise DatabaseError("Failed to upsert Facebook video insights")

            return FacebookVideoInsights(**result.data[0])
        except Exception as e:
            logger.error(
                "Failed to upsert Facebook video insights",
                business_asset_id=insights.business_asset_id,
                video_id=insights.platform_video_id,
                error=str(e),
            )
            raise DatabaseError(f"Failed to upsert video insights: {e}")

    async def get_by_video_id(
        self,
        business_asset_id: str,
        platform_video_id: str
    ) -> Optional[FacebookVideoInsights]:
        """
        Get video insights by video ID.

        Args:
            business_asset_id: Business asset ID
            platform_video_id: Facebook video ID

        Returns:
            FacebookVideoInsights if found, None otherwise
        """
        try:
            client = await get_supabase_admin_client()
            result = (
                await client.table(self.TABLE_NAME)
                .select("*")
                .eq("business_asset_id", business_asset_id)
                .eq("platform_video_id", platform_video_id)
                .execute()
            )

            if not result.data:
                return None

            return FacebookVideoInsights(**result.data[0])
        except Exception as e:
            logger.error(
                "Failed to get Facebook video insights",
                business_asset_id=business_asset_id,
                video_id=platform_video_id,
                error=str(e),
            )
            raise DatabaseError(f"Failed to get video insights: {e}")

    async def get_recent(
        self,
        business_asset_id: str,
        limit: int = 50
    ) -> List[FacebookVideoInsights]:
        """
        Get recent video insights.

        Args:
            business_asset_id: Business asset ID
            limit: Maximum videos to return

        Returns:
            List of FacebookVideoInsights
        """
        try:
            client = await get_supabase_admin_client()
            result = (
                await client.table(self.TABLE_NAME)
                .select("*")
                .eq("business_asset_id", business_asset_id)
                .order("metrics_fetched_at", desc=True)
                .limit(limit)
                .execute()
            )

            return [FacebookVideoInsights(**item) for item in result.data]
        except Exception as e:
            logger.error(
                "Failed to get recent Facebook video insights",
                business_asset_id=business_asset_id,
                error=str(e),
            )
            raise DatabaseError(f"Failed to get recent video insights: {e}")


# =============================================================================
# INSTAGRAM ACCOUNT INSIGHTS REPOSITORY
# =============================================================================


class InstagramAccountInsightsRepository:
    """Repository for Instagram account-level insights."""

    TABLE_NAME = "instagram_account_insights"

    async def upsert(self, insights: InstagramAccountInsights) -> InstagramAccountInsights:
        """
        Insert or update account insights.

        Args:
            insights: InstagramAccountInsights instance

        Returns:
            Upserted insights instance
        """
        try:
            client = await get_supabase_admin_client()
            data = insights.model_dump(mode="json", exclude_unset=True, exclude={"id", "created_at", "updated_at"})

            result = await client.table(self.TABLE_NAME).upsert(
                data,
                on_conflict="business_asset_id"
            ).execute()

            if not result.data:
                raise DatabaseError("Failed to upsert Instagram account insights")

            return InstagramAccountInsights(**result.data[0])
        except Exception as e:
            logger.error(
                "Failed to upsert Instagram account insights",
                business_asset_id=insights.business_asset_id,
                ig_user_id=insights.ig_user_id,
                error=str(e),
            )
            raise DatabaseError(f"Failed to upsert account insights: {e}")

    async def get_by_user_id(
        self,
        business_asset_id: str,
        ig_user_id: str
    ) -> Optional[InstagramAccountInsights]:
        """
        Get account insights by Instagram user ID.

        Args:
            business_asset_id: Business asset ID
            ig_user_id: Instagram user ID

        Returns:
            InstagramAccountInsights if found, None otherwise
        """
        try:
            client = await get_supabase_admin_client()
            result = (
                await client.table(self.TABLE_NAME)
                .select("*")
                .eq("business_asset_id", business_asset_id)
                .eq("ig_user_id", ig_user_id)
                .execute()
            )

            if not result.data:
                return None

            return InstagramAccountInsights(**result.data[0])
        except Exception as e:
            logger.error(
                "Failed to get Instagram account insights",
                business_asset_id=business_asset_id,
                ig_user_id=ig_user_id,
                error=str(e),
            )
            raise DatabaseError(f"Failed to get account insights: {e}")

    async def get_latest(self, business_asset_id: str) -> Optional[InstagramAccountInsights]:
        """
        Get the most recently updated account insights for a business asset.

        Args:
            business_asset_id: Business asset ID

        Returns:
            Most recent InstagramAccountInsights if found, None otherwise
        """
        try:
            client = await get_supabase_admin_client()
            result = (
                await client.table(self.TABLE_NAME)
                .select("*")
                .eq("business_asset_id", business_asset_id)
                .order("metrics_fetched_at", desc=True)
                .limit(1)
                .execute()
            )

            if not result.data:
                return None

            return InstagramAccountInsights(**result.data[0])
        except Exception as e:
            logger.error(
                "Failed to get latest Instagram account insights",
                business_asset_id=business_asset_id,
                error=str(e),
            )
            raise DatabaseError(f"Failed to get latest account insights: {e}")


# =============================================================================
# INSTAGRAM MEDIA INSIGHTS REPOSITORY
# =============================================================================


class InstagramMediaInsightsRepository:
    """Repository for Instagram media-level insights."""

    TABLE_NAME = "instagram_media_insights"

    async def upsert(self, insights: InstagramMediaInsights) -> InstagramMediaInsights:
        """
        Insert or update media insights.

        Args:
            insights: InstagramMediaInsights instance

        Returns:
            Upserted insights instance
        """
        try:
            client = await get_supabase_admin_client()
            data = insights.model_dump(mode="json", exclude_unset=True, exclude={"id", "created_at", "updated_at"})

            result = await client.table(self.TABLE_NAME).upsert(
                data,
                on_conflict="business_asset_id,platform_media_id"
            ).execute()

            if not result.data:
                raise DatabaseError("Failed to upsert Instagram media insights")

            return InstagramMediaInsights(**result.data[0])
        except Exception as e:
            logger.error(
                "Failed to upsert Instagram media insights",
                business_asset_id=insights.business_asset_id,
                media_id=insights.platform_media_id,
                error=str(e),
            )
            raise DatabaseError(f"Failed to upsert media insights: {e}")

    async def get_by_media_id(
        self,
        business_asset_id: str,
        platform_media_id: str
    ) -> Optional[InstagramMediaInsights]:
        """
        Get media insights by media ID.

        Args:
            business_asset_id: Business asset ID
            platform_media_id: Instagram media ID

        Returns:
            InstagramMediaInsights if found, None otherwise
        """
        try:
            client = await get_supabase_admin_client()
            result = (
                await client.table(self.TABLE_NAME)
                .select("*")
                .eq("business_asset_id", business_asset_id)
                .eq("platform_media_id", platform_media_id)
                .execute()
            )

            if not result.data:
                return None

            return InstagramMediaInsights(**result.data[0])
        except Exception as e:
            logger.error(
                "Failed to get Instagram media insights",
                business_asset_id=business_asset_id,
                media_id=platform_media_id,
                error=str(e),
            )
            raise DatabaseError(f"Failed to get media insights: {e}")

    async def get_recent(
        self,
        business_asset_id: str,
        limit: int = 50,
        media_type: Optional[str] = None
    ) -> List[InstagramMediaInsights]:
        """
        Get recent media insights.

        Args:
            business_asset_id: Business asset ID
            limit: Maximum media to return
            media_type: Optional filter by media type ('image', 'video', 'carousel', 'reel')

        Returns:
            List of InstagramMediaInsights
        """
        try:
            client = await get_supabase_admin_client()
            query = (
                client.table(self.TABLE_NAME)
                .select("*")
                .eq("business_asset_id", business_asset_id)
            )

            if media_type:
                query = query.eq("media_type", media_type)

            result = (
                await query
                .order("metrics_fetched_at", desc=True)
                .limit(limit)
                .execute()
            )

            return [InstagramMediaInsights(**item) for item in result.data]
        except Exception as e:
            logger.error(
                "Failed to get recent Instagram media insights",
                business_asset_id=business_asset_id,
                error=str(e),
            )
            raise DatabaseError(f"Failed to get recent media insights: {e}")

    async def get_all_for_business(
        self,
        business_asset_id: str,
        limit: int = 100
    ) -> List[InstagramMediaInsights]:
        """
        Get all media insights for a business asset.

        Args:
            business_asset_id: Business asset ID
            limit: Maximum media to return

        Returns:
            List of InstagramMediaInsights
        """
        try:
            client = await get_supabase_admin_client()
            result = (
                await client.table(self.TABLE_NAME)
                .select("*")
                .eq("business_asset_id", business_asset_id)
                .order("metrics_fetched_at", desc=True)
                .limit(limit)
                .execute()
            )

            return [InstagramMediaInsights(**item) for item in result.data]
        except Exception as e:
            logger.error(
                "Failed to get all Instagram media insights",
                business_asset_id=business_asset_id,
                error=str(e),
            )
            raise DatabaseError(f"Failed to get all media insights: {e}")
