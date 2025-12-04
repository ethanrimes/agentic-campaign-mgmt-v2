# backend/database/repositories/completed_posts.py

"""Repository for completed posts."""

from typing import List, Literal, Optional
from uuid import UUID
from backend.models import CompletedPost
from .base import BaseRepository
from datetime import datetime, timezone

class CompletedPostRepository(BaseRepository[CompletedPost]):
    """Repository for managing completed posts."""

    def __init__(self):
        super().__init__("completed_posts", CompletedPost)

    async def get_pending_for_platform(
        self, business_asset_id: str, platform: Literal["facebook", "instagram"], limit: int = 10
    ) -> List[CompletedPost]:
        """
        Get pending posts for a specific platform.

        DEPRECATED: Use get_posts_ready_to_publish() instead for scheduled posting.
        This method is kept for backward compatibility.

        Args:
            business_asset_id: Business asset ID to filter by
            platform: Platform to filter by
            limit: Maximum number of posts to return
        """
        try:
            from backend.database import get_supabase_admin_client
            client = await get_supabase_admin_client()
            result = (
                await client.table(self.table_name)
                .select("*")
                .eq("business_asset_id", business_asset_id)
                .eq("platform", platform)
                .eq("status", "pending")
                .order("created_at", desc=False)
                .limit(limit)
                .execute()
            )
            return [self.model_class(**item) for item in result.data]
        except Exception as e:
            from backend.utils import get_logger
            logger = get_logger(__name__)
            logger.error(
                "Failed to get pending posts for platform",
                business_asset_id=business_asset_id,
                platform=platform,
                error=str(e),
            )
            return []

    async def get_posts_ready_to_publish(
        self, business_asset_id: str, platform: Literal["facebook", "instagram"], limit: int = 10
    ) -> List[CompletedPost]:
        """
        Get posts that are ready to be published based on scheduled_posting_time.

        Returns posts where:
        - business_asset_id matches
        - status = 'pending'
        - verification_status = 'verified' (must pass content verification)
        - platform matches
        - scheduled_posting_time <= NOW() (or is NULL for immediate publishing)

        Ordered by scheduled_posting_time (earliest first).

        Args:
            business_asset_id: Business asset ID to filter by
            platform: Platform to filter by
            limit: Maximum number of posts to return
        """
        try:
            from backend.database import get_supabase_admin_client
            client = await get_supabase_admin_client()

            now = datetime.now(timezone.utc).isoformat()

            # Get posts where scheduled_posting_time is NULL or <= now
            # AND verification_status is 'verified'
            result = (
                await client.table(self.table_name)
                .select("*")
                .eq("business_asset_id", business_asset_id)
                .eq("platform", platform)
                .eq("status", "pending")
                .eq("verification_status", "verified")
                .or_(f"scheduled_posting_time.is.null,scheduled_posting_time.lte.{now}")
                .order("scheduled_posting_time", desc=False)
                .limit(limit)
                .execute()
            )
            return [self.model_class(**item) for item in result.data]
        except Exception as e:
            from backend.utils import get_logger
            logger = get_logger(__name__)
            logger.error(
                "Failed to get posts ready to publish",
                business_asset_id=business_asset_id,
                platform=platform,
                error=str(e),
            )
            return []

    async def get_pending_verified_posts(
        self, business_asset_id: str, platform: Literal["facebook", "instagram"], limit: int = 100
    ) -> List[CompletedPost]:
        """
        Get all pending verified posts, ignoring scheduled_posting_time.

        Used by publish_pending.py script to force-publish posts regardless of schedule.

        Returns posts where:
        - business_asset_id matches
        - status = 'pending'
        - verification_status = 'verified'
        - platform matches

        Ordered by scheduled_posting_time (earliest first).

        Args:
            business_asset_id: Business asset ID to filter by
            platform: Platform to filter by
            limit: Maximum number of posts to return
        """
        try:
            from backend.database import get_supabase_admin_client
            client = await get_supabase_admin_client()

            result = (
                await client.table(self.table_name)
                .select("*")
                .eq("business_asset_id", business_asset_id)
                .eq("platform", platform)
                .eq("status", "pending")
                .eq("verification_status", "verified")
                .order("scheduled_posting_time", desc=False)
                .limit(limit)
                .execute()
            )
            return [self.model_class(**item) for item in result.data]
        except Exception as e:
            from backend.utils import get_logger
            logger = get_logger(__name__)
            logger.error(
                "Failed to get pending verified posts",
                business_asset_id=business_asset_id,
                platform=platform,
                error=str(e),
            )
            return []

    async def get_all_pending_posts(
        self, business_asset_id: str, platform: Optional[Literal["facebook", "instagram"]] = None
    ) -> List[CompletedPost]:
        """
        Get all pending posts, optionally filtered by platform.

        Useful for the schedule update script.

        Args:
            business_asset_id: Business asset ID to filter by
            platform: Optional platform to filter by
        """
        try:
            from backend.database import get_supabase_admin_client
            client = await get_supabase_admin_client()

            query = (
                client.table(self.table_name)
                .select("*")
                .eq("business_asset_id", business_asset_id)
                .eq("status", "pending")
                .order("created_at", desc=False)
            )

            if platform:
                query = query.eq("platform", platform)

            result = await query.execute()
            return [self.model_class(**item) for item in result.data]
        except Exception as e:
            from backend.utils import get_logger
            logger = get_logger(__name__)
            logger.error(
                "Failed to get all pending posts",
                business_asset_id=business_asset_id,
                platform=platform,
                error=str(e),
            )
            return []

    async def update_scheduled_time(
        self, business_asset_id: str, post_id: UUID, scheduled_posting_time: datetime
    ) -> CompletedPost | None:
        """
        Update the scheduled posting time for a post.

        Args:
            business_asset_id: Business asset ID to filter by
            post_id: ID of the post to update
            scheduled_posting_time: New scheduled posting time
        """
        return await self.update(
            business_asset_id,
            post_id,
            {"scheduled_posting_time": scheduled_posting_time.isoformat()}
        )

    async def get_by_task_id(self, business_asset_id: str, task_id: UUID) -> List[CompletedPost]:
        """
        Get all posts for a specific task.

        Args:
            business_asset_id: Business asset ID to filter by
            task_id: ID of the task to get posts for
        """
        try:
            from backend.database import get_supabase_admin_client
            client = await get_supabase_admin_client()
            result = (
                await client.table(self.table_name)
                .select("*")
                .eq("business_asset_id", business_asset_id)
                .eq("task_id", str(task_id))
                .execute()
            )
            return [self.model_class(**item) for item in result.data]
        except Exception as e:
            from backend.utils import get_logger
            logger = get_logger(__name__)
            logger.error(
                "Failed to get posts by task ID",
                business_asset_id=business_asset_id,
                task_id=str(task_id),
                error=str(e),
            )
            return []

    async def mark_published(
        self,
        business_asset_id: str,
        post_id: UUID,
        platform_post_id: str,
        platform_post_url: str | None = None,
        platform_video_id: str | None = None
    ) -> CompletedPost | None:
        """
        Mark a post as published.

        Args:
            business_asset_id: Business asset ID to filter by
            post_id: ID of the post to mark as published
            platform_post_id: Platform's post ID
            platform_post_url: Optional platform URL for the post
            platform_video_id: Optional video ID for video posts (used for fetching video insights)
        """
        from datetime import datetime, timezone
        updates = {
            "status": "published",
            "published_at": datetime.now(timezone.utc).isoformat(),
            "platform_post_id": platform_post_id,
        }
        if platform_post_url:
            updates["platform_post_url"] = platform_post_url
        if platform_video_id:
            updates["platform_video_id"] = platform_video_id
        return await self.update(business_asset_id, post_id, updates)

    async def mark_failed(self, business_asset_id: str, post_id: UUID, error_message: str) -> CompletedPost | None:
        """
        Mark a post as failed.

        Args:
            business_asset_id: Business asset ID to filter by
            post_id: ID of the post to mark as failed
            error_message: Error message describing the failure
        """
        return await self.update(business_asset_id, post_id, {"status": "failed", "error_message": error_message})

    async def get_recent_by_platform(
        self, business_asset_id: str, platform: Literal["facebook", "instagram"], limit: int = 20
    ) -> List[CompletedPost]:
        """
        Get recent posts for a platform (for UI).

        Args:
            business_asset_id: Business asset ID to filter by
            platform: Platform to filter by
            limit: Maximum number of posts to return
        """
        try:
            from backend.database import get_supabase_admin_client
            client = await get_supabase_admin_client()
            result = (
                await client.table(self.table_name)
                .select("*")
                .eq("business_asset_id", business_asset_id)
                .eq("platform", platform)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return [self.model_class(**item) for item in result.data]
        except Exception as e:
            from backend.utils import get_logger
            logger = get_logger(__name__)
            logger.error(
                "Failed to get recent posts for platform",
                business_asset_id=business_asset_id,
                platform=platform,
                error=str(e),
            )
            return []

    async def get_unverified_posts(
        self, business_asset_id: str, limit: int = 50
    ) -> List[CompletedPost]:
        """
        Get all unverified pending posts.

        Args:
            business_asset_id: Business asset ID to filter by
            limit: Maximum number of posts to return
        """
        try:
            from backend.database import get_supabase_admin_client
            client = await get_supabase_admin_client()
            result = (
                await client.table(self.table_name)
                .select("*")
                .eq("business_asset_id", business_asset_id)
                .eq("status", "pending")
                .eq("verification_status", "unverified")
                .order("created_at", desc=False)
                .limit(limit)
                .execute()
            )
            return [self.model_class(**item) for item in result.data]
        except Exception as e:
            from backend.utils import get_logger
            logger = get_logger(__name__)
            logger.error(
                "Failed to get unverified posts",
                business_asset_id=business_asset_id,
                error=str(e),
            )
            return []

    async def get_unverified_primary_posts(
        self, business_asset_id: str, limit: int = 50
    ) -> List[CompletedPost]:
        """
        Get all unverified PRIMARY pending posts (for verification groups optimization).

        Only returns posts where is_verification_primary = TRUE.
        These are the posts that should actually be verified - secondary posts
        in a verification group will inherit the result.

        Args:
            business_asset_id: Business asset ID to filter by
            limit: Maximum number of posts to return
        """
        try:
            from backend.database import get_supabase_admin_client
            client = await get_supabase_admin_client()
            result = (
                await client.table(self.table_name)
                .select("*")
                .eq("business_asset_id", business_asset_id)
                .eq("status", "pending")
                .eq("verification_status", "unverified")
                .eq("is_verification_primary", True)
                .order("created_at", desc=False)
                .limit(limit)
                .execute()
            )
            return [self.model_class(**item) for item in result.data]
        except Exception as e:
            from backend.utils import get_logger
            logger = get_logger(__name__)
            logger.error(
                "Failed to get unverified primary posts",
                business_asset_id=business_asset_id,
                error=str(e),
            )
            return []

    async def get_posts_by_verification_group(
        self, business_asset_id: str, verification_group_id: UUID
    ) -> List[CompletedPost]:
        """
        Get all posts in a verification group.

        Args:
            business_asset_id: Business asset ID to filter by
            verification_group_id: Verification group ID

        Returns:
            List of all posts in the verification group
        """
        try:
            from backend.database import get_supabase_admin_client
            client = await get_supabase_admin_client()
            result = (
                await client.table(self.table_name)
                .select("*")
                .eq("business_asset_id", business_asset_id)
                .eq("verification_group_id", str(verification_group_id))
                .execute()
            )
            return [self.model_class(**item) for item in result.data]
        except Exception as e:
            from backend.utils import get_logger
            logger = get_logger(__name__)
            logger.error(
                "Failed to get posts by verification group",
                business_asset_id=business_asset_id,
                verification_group_id=str(verification_group_id),
                error=str(e),
            )
            return []

    async def update_verification_status_by_group(
        self, business_asset_id: str, verification_group_id: UUID, verification_status: str
    ) -> int:
        """
        Update verification status for ALL posts in a verification group.

        Args:
            business_asset_id: Business asset ID to filter by
            verification_group_id: Verification group ID
            verification_status: New verification status ('unverified', 'verified', 'rejected')

        Returns:
            Number of posts updated
        """
        try:
            from backend.database import get_supabase_admin_client
            client = await get_supabase_admin_client()
            result = (
                await client.table(self.table_name)
                .update({"verification_status": verification_status})
                .eq("business_asset_id", business_asset_id)
                .eq("verification_group_id", str(verification_group_id))
                .execute()
            )
            return len(result.data) if result.data else 0
        except Exception as e:
            from backend.utils import get_logger
            logger = get_logger(__name__)
            logger.error(
                "Failed to update verification status by group",
                business_asset_id=business_asset_id,
                verification_group_id=str(verification_group_id),
                error=str(e),
            )
            return 0

    async def update_verification_status(
        self, business_asset_id: str, post_id: UUID, verification_status: str
    ) -> CompletedPost | None:
        """
        Update the verification status for a post.

        Args:
            business_asset_id: Business asset ID to filter by
            post_id: ID of the post to update
            verification_status: New verification status ('unverified', 'verified', 'rejected')
        """
        return await self.update(
            business_asset_id,
            post_id,
            {"verification_status": verification_status}
        )

    async def get_recent_published_by_platform(
        self, business_asset_id: str, platform: Literal["facebook", "instagram"], limit: int = 10
    ) -> List[CompletedPost]:
        """
        Get recent PUBLISHED posts for a platform (for insights analysis).

        Args:
            business_asset_id: Business asset ID to filter by
            platform: Platform to filter by
            limit: Maximum number of posts to return
        """
        try:
            from backend.database import get_supabase_admin_client
            client = await get_supabase_admin_client()
            result = (
                await client.table(self.table_name)
                .select("*")
                .eq("business_asset_id", business_asset_id)
                .eq("platform", platform)
                .eq("status", "published")
                .not_.is_("platform_post_id", "null")
                .order("published_at", desc=True)
                .limit(limit)
                .execute()
            )
            return [self.model_class(**item) for item in result.data]
        except Exception as e:
            from backend.utils import get_logger
            logger = get_logger(__name__)
            logger.error(
                "Failed to get recent published posts for platform",
                business_asset_id=business_asset_id,
                platform=platform,
                error=str(e),
            )
            return []

    async def get_scheduled_pending_posts(
        self, business_asset_id: str, limit: int = 50
    ) -> List[CompletedPost]:
        """
        Get all pending verified posts that are scheduled for future publishing.

        Used by the planner to understand:
        1. When posts are scheduled (gaps in the schedule)
        2. What content is already covered (avoid duplicates)

        Returns posts where:
        - business_asset_id matches
        - status = 'pending'
        - verification_status = 'verified'
        - Ordered by scheduled_posting_time (earliest first)

        Args:
            business_asset_id: Business asset ID to filter by
            limit: Maximum number of posts to return
        """
        try:
            from backend.database import get_supabase_admin_client
            client = await get_supabase_admin_client()

            result = (
                await client.table(self.table_name)
                .select("*")
                .eq("business_asset_id", business_asset_id)
                .eq("status", "pending")
                .eq("verification_status", "verified")
                .order("scheduled_posting_time", desc=False)
                .limit(limit)
                .execute()
            )
            return [self.model_class(**item) for item in result.data]
        except Exception as e:
            from backend.utils import get_logger
            logger = get_logger(__name__)
            logger.error(
                "Failed to get scheduled pending posts",
                business_asset_id=business_asset_id,
                error=str(e),
            )
            return []

    async def get_posts_since(self, business_asset_id: str, cutoff_date) -> List[CompletedPost]:
        """
        Get all posts created since a specific datetime (for insights analysis).

        Args:
            business_asset_id: Business asset ID to filter by
            cutoff_date: Get posts created after this datetime
        """
        try:
            from backend.database import get_supabase_admin_client
            client = await get_supabase_admin_client()

            # Convert datetime to ISO format for Supabase
            cutoff_iso = cutoff_date.isoformat()

            result = (
                await client.table(self.table_name)
                .select("*")
                .eq("business_asset_id", business_asset_id)
                .gte("created_at", cutoff_iso)
                .eq("status", "published")
                .order("created_at", desc=True)
                .execute()
            )

            # Convert to CompletedPost models
            posts = [self.model_class(**item) for item in result.data]

            # Return as list of dicts for agent compatibility
            return [post.model_dump(mode="json") for post in posts]

        except Exception as e:
            from backend.utils import get_logger
            logger = get_logger(__name__)
            logger.error(
                "Failed to get posts since cutoff",
                business_asset_id=business_asset_id,
                cutoff_date=str(cutoff_date),
                error=str(e),
            )
            return []
