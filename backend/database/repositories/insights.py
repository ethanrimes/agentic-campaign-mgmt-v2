# backend/database/repositories/insights.py

"""Repository for insight reports."""

from typing import List
from backend.models import InsightReport
from .base import BaseRepository


class InsightsRepository(BaseRepository[InsightReport]):
    """Repository for managing insight reports."""

    def __init__(self):
        super().__init__("insight_reports", InsightReport)

    async def get_recent(self, business_asset_id: str, limit: int = 5) -> List[InsightReport]:
        """
        Get most recent insight reports.

        Args:
            business_asset_id: Business asset ID to filter by
            limit: Maximum number of reports to return
        """
        try:
            from backend.database import get_supabase_admin_client
            client = await get_supabase_admin_client()
            result = (
                await client.table(self.table_name)
                .select("*")
                .eq("business_asset_id", business_asset_id)
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
                business_asset_id=business_asset_id,
                error=str(e),
            )
            return []

    async def get_latest(self, business_asset_id: str) -> InsightReport | None:
        """
        Get the most recent insight report.

        Args:
            business_asset_id: Business asset ID to filter by
        """
        reports = await self.get_recent(business_asset_id, limit=1)
        return reports[0] if reports else None
