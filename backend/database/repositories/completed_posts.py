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
            result = (
                await self.client.table(self.table_name)
                .select("*")
                .eq("platform", platform)
                .eq("status", "pending")
                .order("created_at", desc=False)
                .limit(limit)
                .execute()
            )
            return [self.model_class(**item) for item in result.data]
        except Exception as e:
            return []

    async def get_by_task_id(self, task_id: UUID) -> List[CompletedPost]:
        """Get all posts for a specific task."""
        try:
            result = (
                await self.client.table(self.table_name)
                .select("*")
                .eq("task_id", str(task_id))
                .execute()
            )
            return [self.model_class(**item) for item in result.data]
        except Exception as e:
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
            result = (
                await self.client.table(self.table_name)
                .select("*")
                .eq("platform", platform)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return [self.model_class(**item) for item in result.data]
        except Exception as e:
            return []
