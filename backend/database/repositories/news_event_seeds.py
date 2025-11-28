# backend/database/repositories/news_event_seeds.py

"""Repository for news event seeds."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from backend.models import NewsEventSeed, IngestedEvent
from backend.utils import get_logger
from backend.database import get_supabase_admin_client
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
        from backend.models import Source

        try:
            # Extract sources from data (make a copy to avoid mutating original)
            data_copy = data.copy()
            sources_data = data_copy.pop("sources", [])

            # Create NewsEventSeed model from dict
            seed_model = NewsEventSeed(**data_copy)

            # Create the news event seed without sources
            seed = await super().create(seed_model)

            if not seed:
                return None

            # Create and link sources
            if sources_data:
                # Convert source dicts to Source objects if needed
                source_objects = []
                for src in sources_data:
                    if isinstance(src, dict):
                        source_objects.append(Source(**src))
                    else:
                        source_objects.append(src)

                source_repo = SourceRepository()
                await source_repo.create_and_link_sources_for_news_event_seed(
                    seed.id, source_objects
                )

            return seed
        except Exception as e:
            logger.error(
                "Failed to create news event seed with sources",
                error=str(e)
            )
            return None

    async def get_by_id(self, business_asset_id: str, id: UUID) -> Optional[NewsEventSeed]:
        """
        Get a news event seed by ID, including its sources.

        Args:
            business_asset_id: Business asset ID to filter by
            id: ID of the news event seed
        """
        from .sources import SourceRepository

        seed = await super().get_by_id(business_asset_id, id)
        if not seed:
            return None

        # Load sources
        source_repo = SourceRepository()
        sources = await source_repo.get_sources_for_news_event_seed(id)
        seed.sources = sources

        return seed

    async def list_all(self, business_asset_id: str, limit: Optional[int] = None) -> List[NewsEventSeed]:
        """
        List all news event seeds with their sources.

        Args:
            business_asset_id: Business asset ID to filter by
            limit: Optional maximum number of seeds to return
        """
        from .sources import SourceRepository

        seeds = await super().get_all(business_asset_id, limit)

        # Load sources for each seed
        source_repo = SourceRepository()
        for seed in seeds:
            sources = await source_repo.get_sources_for_news_event_seed(seed.id)
            seed.sources = sources

        return seeds

    async def search_by_name(self, business_asset_id: str, query: str, limit: int = 10) -> List[NewsEventSeed]:
        """
        Search news events by name with sources.

        Args:
            business_asset_id: Business asset ID to filter by
            query: Search query to match against event names
            limit: Maximum number of results to return
        """
        from .sources import SourceRepository

        try:
            from backend.database import get_supabase_admin_client
            client = await get_supabase_admin_client()
            result = (
                await client.table(self.table_name)
                .select("*")
                .eq("business_asset_id", business_asset_id)
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
                business_asset_id=business_asset_id,
                query=query,
                error=str(e),
            )
            return []

    async def get_recent(self, business_asset_id: str, limit: int = 10) -> List[NewsEventSeed]:
        """
        Get most recent news event seeds with sources.

        Args:
            business_asset_id: Business asset ID to filter by
            limit: Maximum number of seeds to return
        """
        from .sources import SourceRepository

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
                business_asset_id=business_asset_id,
                error=str(e),
            )
            return []

    async def update(self, business_asset_id: str, id: UUID, updates: Dict[str, Any]) -> Optional[NewsEventSeed]:
        """
        Update a news event seed, handling sources separately.

        Args:
            business_asset_id: Business asset ID to filter by
            id: ID of the news event seed to update
            updates: Dictionary of fields to update
        """
        from .sources import SourceRepository

        try:
            # Extract sources from updates if present
            sources = updates.pop("sources", None)

            # Update the news event seed without sources
            seed = await super().update(business_asset_id, id, updates)

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
            return await self.get_by_id(business_asset_id, id)
        except Exception as e:
            logger.error(
                "Failed to update news event seed with sources",
                business_asset_id=business_asset_id,
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
        from backend.models import Source

        try:
            # Extract sources from data (make a copy to avoid mutating original)
            data_copy = data.copy()
            sources_data = data_copy.pop("sources", [])

            # Create IngestedEvent model from dict
            event_model = IngestedEvent(**data_copy)

            # Create the ingested event without sources
            event = await super().create(event_model)

            if not event:
                return None

            # Create and link sources
            if sources_data:
                # Convert source dicts to Source objects if needed
                source_objects = []
                for src in sources_data:
                    if isinstance(src, dict):
                        source_objects.append(Source(**src))
                    else:
                        source_objects.append(src)

                source_repo = SourceRepository()
                await source_repo.create_and_link_sources_for_ingested_event(
                    event.id, source_objects
                )

            return event
        except Exception as e:
            logger.error(
                "Failed to create ingested event with sources",
                error=str(e)
            )
            return None

    async def get_by_id(self, business_asset_id: str, id: UUID) -> Optional[IngestedEvent]:
        """
        Get an ingested event by ID, including its sources.

        Args:
            business_asset_id: Business asset ID to filter by
            id: ID of the ingested event
        """
        from .sources import SourceRepository

        event = await super().get_by_id(business_asset_id, id)
        if not event:
            return None

        # Load sources
        source_repo = SourceRepository()
        sources = await source_repo.get_sources_for_ingested_event(id)
        event.sources = sources

        return event

    async def list_all(self, business_asset_id: str, limit: Optional[int] = None) -> List[IngestedEvent]:
        """
        List all ingested events with their sources.

        Args:
            business_asset_id: Business asset ID to filter by
            limit: Optional maximum number of events to return
        """
        from .sources import SourceRepository

        events = await super().get_all(business_asset_id, limit)

        # Load sources for each event
        source_repo = SourceRepository()
        for event in events:
            sources = await source_repo.get_sources_for_ingested_event(event.id)
            event.sources = sources

        return events

    async def get_by_ingested_by(self, business_asset_id: str, ingested_by: str) -> List[IngestedEvent]:
        """
        Get events by the agent that ingested them, with sources.

        Args:
            business_asset_id: Business asset ID to filter by
            ingested_by: Name of the agent that ingested the events
        """
        from .sources import SourceRepository

        try:
            from backend.database import get_supabase_admin_client
            client = await get_supabase_admin_client()
            result = (
                await client.table(self.table_name)
                .select("*")
                .eq("business_asset_id", business_asset_id)
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
                business_asset_id=business_asset_id,
                ingested_by=ingested_by,
                error=str(e),
            )
            return []

    async def get_unprocessed(self, business_asset_id: str, limit: Optional[int] = None) -> List[IngestedEvent]:
        """
        Get all unprocessed ingested events with sources.

        Args:
            business_asset_id: Business asset ID to filter by
            limit: Optional maximum number of events to return

        Returns:
            List of unprocessed ingested events, ordered by creation time (oldest first)
        """
        from .sources import SourceRepository

        try:
            from backend.database import get_supabase_admin_client
            client = await get_supabase_admin_client()
            query = (
                client.table(self.table_name)
                .select("*")
                .eq("business_asset_id", business_asset_id)
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
                business_asset_id=business_asset_id,
                error=str(e),
                table=self.table_name
            )
            return []

    async def mark_as_processed(
        self,
        business_asset_id: str,
        event_id: UUID,
        canonical_event_id: UUID
    ) -> Optional[IngestedEvent]:
        """
        Mark an ingested event as processed.

        Args:
            business_asset_id: Business asset ID to filter by
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

            client = await get_supabase_admin_client()
            result = (
                await client.table(self.table_name)
                .update(updates)
                .eq("business_asset_id", business_asset_id)
                .eq("id", str(event_id))
                .execute()
            )

            if not result.data:
                logger.warning(
                    "No event found to mark as processed",
                    business_asset_id=business_asset_id,
                    event_id=str(event_id)
                )
                return None

            return self.model_class(**result.data[0])
        except Exception as e:
            logger.error(
                "Failed to mark event as processed",
                business_asset_id=business_asset_id,
                event_id=str(event_id),
                canonical_event_id=str(canonical_event_id),
                error=str(e)
            )
            return None
