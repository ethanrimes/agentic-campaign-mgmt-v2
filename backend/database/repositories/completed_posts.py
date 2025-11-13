# backend/database/repositories/completed_posts.py

"""Repository for completed posts."""

from typing import List, Literal
from uuid import UUID
from backend.models import CompletedPost
from .base import BaseRepository


class CompletedPostRepository(BaseRepository[CompletedPost]):
    """Repository for managing completed posts."""

    def __init__(self):
        super().__init__("completed_posts", CompletedPost)

    async def get_pending_for_platform(
        self, platform: Literal["facebook", "instagram"], limit: int = 10
    ) -> List[CompletedPost]:
        """Get pending posts for a specific platform."""
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
