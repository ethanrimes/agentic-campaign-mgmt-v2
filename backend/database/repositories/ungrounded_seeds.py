# backend/database/repositories/ungrounded_seeds.py

"""Repository for ungrounded seeds."""

from typing import List
from backend.models import UngroundedSeed
from .base import BaseRepository


class UngroundedSeedRepository(BaseRepository[UngroundedSeed]):
    """Repository for managing ungrounded seeds."""

    def __init__(self):
        super().__init__("ungrounded_seeds", UngroundedSeed)

    def get_recent(self, limit: int = 10) -> List[UngroundedSeed]:
        """Get most recent ungrounded seeds."""
        try:
            result = (
                self.client.table(self.table_name)
                .select("*")
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return [self.model_class(**item) for item in result.data]
        except Exception as e:
            return []
