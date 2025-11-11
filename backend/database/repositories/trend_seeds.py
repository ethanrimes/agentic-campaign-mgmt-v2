# backend/database/repositories/trend_seeds.py

"""Repository for trend seeds."""

from typing import List
from backend.models import TrendSeed
from .base import BaseRepository


class TrendSeedsRepository(BaseRepository[TrendSeed]):
    """Repository for managing trend seeds."""

    def __init__(self):
        super().__init__("trend_seeds", TrendSeed)

    async def get_recent(self, limit: int = 10) -> List[TrendSeed]:
        """Get most recent trend seeds."""
        try:
            result = (
                await self.client.table(self.table_name)
                .select("*")
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return [self.model_class(**item) for item in result.data]
        except Exception as e:
            return []
