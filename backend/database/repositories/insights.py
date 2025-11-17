# backend/database/repositories/insights.py

"""Repository for insight reports."""

from typing import List
from backend.models import InsightReport
from .base import BaseRepository


class InsightsRepository(BaseRepository[InsightReport]):
    """Repository for managing insight reports."""

    def __init__(self):
        super().__init__("insight_reports", InsightReport)

    async def get_recent(self, limit: int = 5) -> List[InsightReport]:
        """Get most recent insight reports."""
        try:
            from backend.database import get_supabase_admin_client
            client = await get_supabase_admin_client()
            result = (
                await client.table(self.table_name)
                .select("*")
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return [self.model_class(**item) for item in result.data]
        except Exception as e:
            from backend.utils import get_logger
            logger = get_logger(__name__)
            logger.error(
                "Failed to get recent insight reports",
                error=str(e),
            )
            return []

    async def get_latest(self) -> InsightReport | None:
        """Get the most recent insight report."""
        reports = await self.get_recent(limit=1)
        return reports[0] if reports else None
