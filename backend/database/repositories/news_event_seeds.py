# backend/database/repositories/news_event_seeds.py

"""Repository for news event seeds."""

from typing import List, Optional
from backend.models import NewsEventSeed, IngestedEvent
from .base import BaseRepository


class NewsEventSeedRepository(BaseRepository[NewsEventSeed]):
    """Repository for managing news event seeds."""

    def __init__(self):
        super().__init__("news_event_seeds", NewsEventSeed)

    def search_by_name(self, query: str, limit: int = 10) -> List[NewsEventSeed]:
        """Search news events by name."""
        try:
            result = (
                self.client.table(self.table_name)
                .select("*")
                .ilike("name", f"%{query}%")
                .limit(limit)
                .execute()
            )
            return [self.model_class(**item) for item in result.data]
        except Exception as e:
            return []

    def get_recent(self, limit: int = 10) -> List[NewsEventSeed]:
        """Get most recent news event seeds."""
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


class IngestedEventRepository(BaseRepository[IngestedEvent]):
    """Repository for ingested events (pre-deduplication)."""

    def __init__(self):
        super().__init__("ingested_events", IngestedEvent)

    def get_by_ingested_by(self, ingested_by: str) -> List[IngestedEvent]:
        """Get events by the agent that ingested them."""
        try:
            result = (
                self.client.table(self.table_name)
                .select("*")
                .eq("ingested_by", ingested_by)
                .order("created_at", desc=True)
                .execute()
            )
            return [self.model_class(**item) for item in result.data]
        except Exception as e:
            return []
