# backend/database/repositories/content_creation_tasks.py

"""Repository for content creation tasks."""

from typing import List
from uuid import UUID
from backend.models import ContentCreationTask
from .base import BaseRepository


class ContentCreationTaskRepository(BaseRepository[ContentCreationTask]):
    """Repository for managing content creation tasks."""

    def __init__(self):
        super().__init__("content_creation_tasks", ContentCreationTask)

    async def get_pending_tasks(self, business_asset_id: str, limit: int = 10) -> List[ContentCreationTask]:
        """
        Get pending tasks.

        Args:
            business_asset_id: Business asset ID to filter by
            limit: Maximum number of tasks to return
        """
        from backend.database import get_supabase_admin_client
        try:
            client = await get_supabase_admin_client()
            result = (
                await client.table(self.table_name)
                .select("*")
                .eq("business_asset_id", business_asset_id)
                .eq("status", "pending")
                .order("created_at", desc=False)
                .limit(limit)
                .execute()
            )
            return [self.model_class(**item) for item in result.data]
        except Exception as e:
            return []

    async def get_by_seed_id(self, business_asset_id: str, seed_id: UUID) -> List[ContentCreationTask]:
        """
        Get tasks for a specific content seed.

        Args:
            business_asset_id: Business asset ID to filter by
            seed_id: ID of the content seed
        """
        from backend.database import get_supabase_admin_client
        try:
            client = await get_supabase_admin_client()
            result = (
                await client.table(self.table_name)
                .select("*")
                .eq("business_asset_id", business_asset_id)
                .eq("content_seed_id", str(seed_id))
                .order("created_at", desc=True)
                .execute()
            )
            return [self.model_class(**item) for item in result.data]
        except Exception as e:
            return []

    async def mark_in_progress(self, business_asset_id: str, task_id: UUID) -> ContentCreationTask | None:
        """
        Mark a task as in progress.

        Args:
            business_asset_id: Business asset ID to filter by
            task_id: ID of the task to mark
        """
        from datetime import datetime
        return await self.update(
            business_asset_id,
            task_id,
            {"status": "in_progress", "started_at": datetime.utcnow().isoformat()}
        )

    async def mark_completed(self, business_asset_id: str, task_id: UUID) -> ContentCreationTask | None:
        """
        Mark a task as completed.

        Args:
            business_asset_id: Business asset ID to filter by
            task_id: ID of the task to mark
        """
        from datetime import datetime
        return await self.update(
            business_asset_id,
            task_id,
            {"status": "completed", "completed_at": datetime.utcnow().isoformat()},
        )

    async def mark_failed(self, business_asset_id: str, task_id: UUID, error_message: str) -> ContentCreationTask | None:
        """
        Mark a task as failed.

        Args:
            business_asset_id: Business asset ID to filter by
            task_id: ID of the task to mark
            error_message: Error message describing the failure
        """
        return await self.update(business_asset_id, task_id, {"status": "failed", "error_message": error_message})
