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

    def get_pending_tasks(self, limit: int = 10) -> List[ContentCreationTask]:
        """Get pending tasks."""
        try:
            result = (
                self.client.table(self.table_name)
                .select("*")
                .eq("status", "pending")
                .order("created_at", desc=False)
                .limit(limit)
                .execute()
            )
            return [self.model_class(**item) for item in result.data]
        except Exception as e:
            return []

    def get_by_seed_id(self, seed_id: UUID) -> List[ContentCreationTask]:
        """Get tasks for a specific content seed."""
        try:
            result = (
                self.client.table(self.table_name)
                .select("*")
                .eq("content_seed_id", str(seed_id))
                .order("created_at", desc=True)
                .execute()
            )
            return [self.model_class(**item) for item in result.data]
        except Exception as e:
            return []

    def mark_in_progress(self, task_id: UUID) -> ContentCreationTask | None:
        """Mark a task as in progress."""
        from datetime import datetime
        return self.update(
            task_id, {"status": "in_progress", "started_at": datetime.utcnow().isoformat()}
        )

    def mark_completed(self, task_id: UUID) -> ContentCreationTask | None:
        """Mark a task as completed."""
        from datetime import datetime
        return self.update(
            task_id,
            {"status": "completed", "completed_at": datetime.utcnow().isoformat()},
        )

    def mark_failed(self, task_id: UUID, error_message: str) -> ContentCreationTask | None:
        """Mark a task as failed."""
        return self.update(task_id, {"status": "failed", "error_message": error_message})
