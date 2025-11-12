# backend/database/repositories/news_event_seeds.py

"""Repository for news event seeds."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID
from backend.models import NewsEventSeed, IngestedEvent
from backend.utils import get_logger
from .base import BaseRepository

logger = get_logger(__name__)


class NewsEventSeedRepository(BaseRepository[NewsEventSeed]):
    """Repository for managing news event seeds."""

    def __init__(self):
        super().__init__("news_event_seeds", NewsEventSeed)

    async def search_by_name(self, query: str, limit: int = 10) -> List[NewsEventSeed]:
        """Search news events by name."""
        try:
            from backend.database import get_supabase_client
            client = await get_supabase_client()
            result = (
                await client.table(self.table_name)
                .select("*")
                .ilike("name", f"%{query}%")
                .limit(limit)
                .execute()
            )
            return [self.model_class(**item) for item in result.data]
        except Exception as e:
            logger.error(
                "Failed to search news events by name",
                query=query,
                error=str(e),
            )
            return []

    async def get_recent(self, limit: int = 10) -> List[NewsEventSeed]:
        """Get most recent news event seeds."""
        try:
            from backend.database import get_supabase_client
            client = await get_supabase_client()
            result = (
                await client.table(self.table_name)
                .select("*")
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return [self.model_class(**item) for item in result.data]
        except Exception as e:
            logger.error(
                "Failed to get recent news event seeds",
                error=str(e),
            )
            return []


class IngestedEventRepository(BaseRepository[IngestedEvent]):
    """Repository for ingested events (pre-deduplication)."""

    def __init__(self):
        super().__init__("ingested_events", IngestedEvent)

    async def get_by_ingested_by(self, ingested_by: str) -> List[IngestedEvent]:
        """Get events by the agent that ingested them."""
        try:
            from backend.database import get_supabase_client
            client = await get_supabase_client()
            result = (
                await client.table(self.table_name)
                .select("*")
                .eq("ingested_by", ingested_by)
                .order("created_at", desc=True)
                .execute()
            )
            return [self.model_class(**item) for item in result.data]
        except Exception as e:
            logger.error(
                "Failed to get events by ingested_by",
                ingested_by=ingested_by,
                error=str(e),
            )
            return []

    async def get_unprocessed(self, limit: Optional[int] = None) -> List[IngestedEvent]:
        """
        Get all unprocessed ingested events.

        Args:
            limit: Optional maximum number of events to return

        Returns:
            List of unprocessed ingested events, ordered by creation time (oldest first)
        """
        try:
            from backend.database import get_supabase_client
            client = await get_supabase_client()
            query = (
                client.table(self.table_name)
                .select("*")
                .eq("processed", False)
                .order("created_at", desc=False)  # Process oldest first
            )

            if limit:
                query = query.limit(limit)

            result = await query.execute()
            return [self.model_class(**item) for item in result.data]
        except Exception as e:
            logger.error(
                "Failed to get unprocessed events",
                error=str(e),
                table=self.table_name
            )
            return []

    async def mark_as_processed(
        self,
        event_id: UUID,
        canonical_event_id: UUID
    ) -> Optional[IngestedEvent]:
        """
        Mark an ingested event as processed.

        Args:
            event_id: ID of the ingested event to mark as processed
            canonical_event_id: ID of the canonical news event seed it was deduplicated into

        Returns:
            Updated ingested event if successful, None otherwise
        """
        try:
            updates = {
                "processed": True,
                "processed_at": datetime.utcnow().isoformat(),
                "canonical_event_id": str(canonical_event_id)
            }

            result = (
                await self.client.table(self.table_name)
                .update(updates)
                .eq("id", str(event_id))
                .execute()
            )

            if not result.data:
                logger.warning(
                    "No event found to mark as processed",
                    event_id=str(event_id)
                )
                return None

            return self.model_class(**result.data[0])
        except Exception as e:
            logger.error(
                "Failed to mark event as processed",
                event_id=str(event_id),
                canonical_event_id=str(canonical_event_id),
                error=str(e)
            )
            return None
