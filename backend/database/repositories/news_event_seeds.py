# backend/database/repositories/news_event_seeds.py

"""Repository for news event seeds."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from backend.models import NewsEventSeed, IngestedEvent
from backend.utils import get_logger
from backend.database import get_supabase_client
from .base import BaseRepository

logger = get_logger(__name__)


class NewsEventSeedRepository(BaseRepository[NewsEventSeed]):
    """Repository for managing news event seeds."""

    def __init__(self):
        super().__init__("news_event_seeds", NewsEventSeed)

    async def create(self, data: Dict[str, Any]) -> Optional[NewsEventSeed]:
        """
        Create a news event seed with sources.

        Handles the sources separately using the SourceRepository.
        """
        from .sources import SourceRepository

        try:
            # Extract sources from data
            sources = data.pop("sources", [])

            # Create the news event seed without sources
            seed = await super().create(data)

            if not seed:
                return None

            # Create and link sources
            if sources:
                source_repo = SourceRepository()
                await source_repo.create_and_link_sources_for_news_event_seed(
                    seed.id, sources
                )

            return seed
        except Exception as e:
            logger.error(
                "Failed to create news event seed with sources",
                error=str(e)
            )
            return None

    async def get_by_id(self, id: UUID) -> Optional[NewsEventSeed]:
        """
        Get a news event seed by ID, including its sources.
        """
        from .sources import SourceRepository

        seed = await super().get_by_id(id)
        if not seed:
            return None

        # Load sources
        source_repo = SourceRepository()
        sources = await source_repo.get_sources_for_news_event_seed(id)
        seed.sources = sources

        return seed

    async def list_all(self, limit: Optional[int] = None) -> List[NewsEventSeed]:
        """
        List all news event seeds with their sources.
        """
        from .sources import SourceRepository

        seeds = await super().list_all(limit)

        # Load sources for each seed
        source_repo = SourceRepository()
        for seed in seeds:
            sources = await source_repo.get_sources_for_news_event_seed(seed.id)
            seed.sources = sources

        return seeds

    async def search_by_name(self, query: str, limit: int = 10) -> List[NewsEventSeed]:
        """Search news events by name with sources."""
        from .sources import SourceRepository

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
            seeds = [self.model_class(**item) for item in result.data]

            # Load sources for each seed
            source_repo = SourceRepository()
            for seed in seeds:
                sources = await source_repo.get_sources_for_news_event_seed(seed.id)
                seed.sources = sources

            return seeds
        except Exception as e:
            logger.error(
                "Failed to search news events by name",
                query=query,
                error=str(e),
            )
            return []

    async def get_recent(self, limit: int = 10) -> List[NewsEventSeed]:
        """Get most recent news event seeds with sources."""
        from .sources import SourceRepository

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
            seeds = [self.model_class(**item) for item in result.data]

            # Load sources for each seed
            source_repo = SourceRepository()
            for seed in seeds:
                sources = await source_repo.get_sources_for_news_event_seed(seed.id)
                seed.sources = sources

            return seeds
        except Exception as e:
            logger.error(
                "Failed to get recent news event seeds",
                error=str(e),
            )
            return []

    async def update(self, id: UUID, updates: Dict[str, Any]) -> Optional[NewsEventSeed]:
        """
        Update a news event seed, handling sources separately.
        """
        from .sources import SourceRepository

        try:
            # Extract sources from updates if present
            sources = updates.pop("sources", None)

            # Update the news event seed without sources
            seed = await super().update(id, updates)

            if not seed:
                return None

            # Update sources if provided
            if sources is not None:
                source_repo = SourceRepository()

                # First, get existing sources for this seed
                existing_sources = await source_repo.get_sources_for_news_event_seed(id)
                existing_urls = {str(src.url) for src in existing_sources}

                # Add new sources that don't already exist
                for source_dict in sources:
                    from backend.models import Source

                    # Convert dict to Source model if needed
                    if isinstance(source_dict, dict):
                        source = Source(**source_dict)
                    else:
                        source = source_dict

                    # Only add if URL doesn't already exist
                    if str(source.url) not in existing_urls:
                        # Check if source with this URL exists in sources table
                        existing_source = await source_repo.get_by_url(str(source.url))

                        if existing_source:
                            # Link existing source to this seed
                            await source_repo.link_source_to_news_event_seed(
                                existing_source.id, id
                            )
                        else:
                            # Create new source and link it
                            source_data = source.model_dump(mode="json", exclude={"id"})
                            created_source = await source_repo.create(source_data)
                            if created_source:
                                await source_repo.link_source_to_news_event_seed(
                                    created_source.id, id
                                )

            # Reload with sources
            return await self.get_by_id(id)
        except Exception as e:
            logger.error(
                "Failed to update news event seed with sources",
                id=str(id),
                error=str(e)
            )
            return None


class IngestedEventRepository(BaseRepository[IngestedEvent]):
    """Repository for ingested events (pre-deduplication)."""

    def __init__(self):
        super().__init__("ingested_events", IngestedEvent)

    async def create(self, data: Dict[str, Any]) -> Optional[IngestedEvent]:
        """
        Create an ingested event with sources.

        Handles the sources separately using the SourceRepository.
        """
        from .sources import SourceRepository

        try:
            # Extract sources from data
            sources = data.pop("sources", [])

            # Create the ingested event without sources
            event = await super().create(data)

            if not event:
                return None

            # Create and link sources
            if sources:
                source_repo = SourceRepository()
                await source_repo.create_and_link_sources_for_ingested_event(
                    event.id, sources
                )

            return event
        except Exception as e:
            logger.error(
                "Failed to create ingested event with sources",
                error=str(e)
            )
            return None

    async def get_by_id(self, id: UUID) -> Optional[IngestedEvent]:
        """
        Get an ingested event by ID, including its sources.
        """
        from .sources import SourceRepository

        event = await super().get_by_id(id)
        if not event:
            return None

        # Load sources
        source_repo = SourceRepository()
        sources = await source_repo.get_sources_for_ingested_event(id)
        event.sources = sources

        return event

    async def list_all(self, limit: Optional[int] = None) -> List[IngestedEvent]:
        """
        List all ingested events with their sources.
        """
        from .sources import SourceRepository

        events = await super().list_all(limit)

        # Load sources for each event
        source_repo = SourceRepository()
        for event in events:
            sources = await source_repo.get_sources_for_ingested_event(event.id)
            event.sources = sources

        return events

    async def get_by_ingested_by(self, ingested_by: str) -> List[IngestedEvent]:
        """Get events by the agent that ingested them, with sources."""
        from .sources import SourceRepository

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
            events = [self.model_class(**item) for item in result.data]

            # Load sources for each event
            source_repo = SourceRepository()
            for event in events:
                sources = await source_repo.get_sources_for_ingested_event(event.id)
                event.sources = sources

            return events
        except Exception as e:
            logger.error(
                "Failed to get events by ingested_by",
                ingested_by=ingested_by,
                error=str(e),
            )
            return []

    async def get_unprocessed(self, limit: Optional[int] = None) -> List[IngestedEvent]:
        """
        Get all unprocessed ingested events with sources.

        Args:
            limit: Optional maximum number of events to return

        Returns:
            List of unprocessed ingested events, ordered by creation time (oldest first)
        """
        from .sources import SourceRepository

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
            events = [self.model_class(**item) for item in result.data]

            # Load sources for each event
            source_repo = SourceRepository()
            for event in events:
                sources = await source_repo.get_sources_for_ingested_event(event.id)
                event.sources = sources

            return events
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

            client = await get_supabase_client()
            result = (
                await client.table(self.table_name)
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
