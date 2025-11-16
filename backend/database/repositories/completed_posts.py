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
        self, platform: Literal["facebook", "instagram"], limit: int = 10
    ) -> List[CompletedPost]:
        """
        Get pending posts for a specific platform.

        DEPRECATED: Use get_posts_ready_to_publish() instead for scheduled posting.
        This method is kept for backward compatibility.
        """
        try:
            from backend.database import get_supabase_client
            client = await get_supabase_client()
            result = (
                await client.table(self.table_name)
                .select("*")
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
                platform=platform,
                error=str(e),
            )
            return []

    async def get_posts_ready_to_publish(
        self, platform: Literal["facebook", "instagram"], limit: int = 10
    ) -> List[CompletedPost]:
        """
        Get posts that are ready to be published based on scheduled_posting_time.

        Returns posts where:
        - status = 'pending'
        - platform matches
        - scheduled_posting_time <= NOW() (or is NULL for immediate publishing)

        Ordered by scheduled_posting_time (earliest first).
        """
        try:
            from backend.database import get_supabase_client
            client = await get_supabase_client()

            now = datetime.now(timezone.utc).isoformat()

            # Get posts where scheduled_posting_time is NULL or <= now
            result = (
                await client.table(self.table_name)
                .select("*")
                .eq("platform", platform)
                .eq("status", "pending")
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
                platform=platform,
                error=str(e),
            )
            return []

    async def get_all_pending_posts(
        self, platform: Optional[Literal["facebook", "instagram"]] = None
    ) -> List[CompletedPost]:
        """
        Get all pending posts, optionally filtered by platform.

        Useful for the schedule update script.
        """
        try:
            from backend.database import get_supabase_client
            client = await get_supabase_client()

            query = (
                client.table(self.table_name)
                .select("*")
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
                platform=platform,
                error=str(e),
            )
            return []

    async def update_scheduled_time(
        self, post_id: UUID, scheduled_posting_time: datetime
    ) -> CompletedPost | None:
        """Update the scheduled posting time for a post."""
        return await self.update(
            post_id,
            {"scheduled_posting_time": scheduled_posting_time.isoformat()}
        )

    async def get_by_task_id(self, task_id: UUID) -> List[CompletedPost]:
        """Get all posts for a specific task."""
        try:
            from backend.database import get_supabase_client
            client = await get_supabase_client()
            result = (
                await client.table(self.table_name)
                .select("*")
                .eq("task_id", str(task_id))
                .execute()
            )
            return [self.model_class(**item) for item in result.data]
        except Exception as e:
            from backend.utils import get_logger
            logger = get_logger(__name__)
            logger.error(
                "Failed to get posts by task ID",
                task_id=str(task_id),
                error=str(e),
            )
            return []

    async def mark_published(
        self, post_id: UUID, platform_post_id: str, platform_post_url: str | None = None
    ) -> CompletedPost | None:
        """Mark a post as published."""
        from datetime import datetime, timezone
        updates = {
            "status": "published",
            "published_at": datetime.now(timezone.utc).isoformat(),
            "platform_post_id": platform_post_id,
        }
        if platform_post_url:
            updates["platform_post_url"] = platform_post_url
        return await self.update(post_id, updates)

    async def mark_failed(self, post_id: UUID, error_message: str) -> CompletedPost | None:
        """Mark a post as failed."""
        return await self.update(post_id, {"status": "failed", "error_message": error_message})

    async def get_recent_by_platform(
        self, platform: Literal["facebook", "instagram"], limit: int = 20
    ) -> List[CompletedPost]:
        """Get recent posts for a platform (for UI)."""
        try:
            from backend.database import get_supabase_client
            client = await get_supabase_client()
            result = (
                await client.table(self.table_name)
                .select("*")
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
                platform=platform,
                error=str(e),
            )
            return []

    async def get_posts_since(self, cutoff_date) -> List[CompletedPost]:
        """Get all posts created since a specific datetime (for insights analysis)."""
        try:
            from backend.database import get_supabase_client
            client = await get_supabase_client()

            # Convert datetime to ISO format for Supabase
            cutoff_iso = cutoff_date.isoformat()

            result = (
                await client.table(self.table_name)
                .select("*")
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
                cutoff_date=str(cutoff_date),
                error=str(e),
            )
            return []
