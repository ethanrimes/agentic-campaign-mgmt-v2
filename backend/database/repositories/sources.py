# backend/database/repositories/sources.py

"""Repository for managing sources and their relationships with events."""

from typing import List, Optional
from uuid import UUID
from backend.models import Source
from backend.utils import get_logger
from backend.database import get_supabase_admin_client
from .base import BaseRepository

logger = get_logger(__name__)


class SourceRepository(BaseRepository[Source]):
    """Repository for managing sources."""

    def __init__(self):
        super().__init__("sources", Source)

    async def get_by_url(self, url: str) -> Optional[Source]:
        """Get a source by its URL."""
        try:
            client = await get_supabase_admin_client()
            result = (
                await client.table(self.table_name)
                .select("*")
                .eq("url", url)
                .limit(1)
                .execute()
            )
            if result.data:
                return self.model_class(**result.data[0])
            return None
        except Exception as e:
            logger.error(
                "Failed to get source by URL",
                url=url,
                error=str(e),
            )
            return None

    async def get_sources_for_ingested_event(
        self, ingested_event_id: UUID
    ) -> List[Source]:
        """Get all sources associated with an ingested event."""
        try:
            client = await get_supabase_admin_client()

            # Query junction table to get source IDs
            junction_result = (
                await client.table("ingested_event_sources")
                .select("source_id")
                .eq("ingested_event_id", str(ingested_event_id))
                .execute()
            )

            if not junction_result.data:
                return []

            # Extract source IDs
            source_ids = [row["source_id"] for row in junction_result.data]

            # Fetch all sources
            sources_result = (
                await client.table(self.table_name)
                .select("*")
                .in_("id", source_ids)
                .execute()
            )

            return [self.model_class(**item) for item in sources_result.data]
        except Exception as e:
            logger.error(
                "Failed to get sources for ingested event",
                ingested_event_id=str(ingested_event_id),
                error=str(e),
            )
            return []

    async def get_sources_for_news_event_seed(
        self, news_event_seed_id: UUID
    ) -> List[Source]:
        """Get all sources associated with a news event seed."""
        try:
            client = await get_supabase_admin_client()

            # Query junction table to get source IDs
            junction_result = (
                await client.table("news_event_seed_sources")
                .select("source_id")
                .eq("news_event_seed_id", str(news_event_seed_id))
                .execute()
            )

            if not junction_result.data:
                return []

            # Extract source IDs
            source_ids = [row["source_id"] for row in junction_result.data]

            # Fetch all sources
            sources_result = (
                await client.table(self.table_name)
                .select("*")
                .in_("id", source_ids)
                .execute()
            )

            return [self.model_class(**item) for item in sources_result.data]
        except Exception as e:
            logger.error(
                "Failed to get sources for news event seed",
                news_event_seed_id=str(news_event_seed_id),
                error=str(e),
            )
            return []

    async def link_source_to_ingested_event(
        self, source_id: UUID, ingested_event_id: UUID
    ) -> bool:
        """Create a link between a source and an ingested event."""
        try:
            client = await get_supabase_admin_client()
            await client.table("ingested_event_sources").insert({
                "source_id": str(source_id),
                "ingested_event_id": str(ingested_event_id)
            }).execute()

            logger.info(
                "Linked source to ingested event",
                source_id=str(source_id),
                ingested_event_id=str(ingested_event_id)
            )
            return True
        except Exception as e:
            logger.error(
                "Failed to link source to ingested event",
                source_id=str(source_id),
                ingested_event_id=str(ingested_event_id),
                error=str(e),
            )
            return False

    async def link_source_to_news_event_seed(
        self, source_id: UUID, news_event_seed_id: UUID
    ) -> bool:
        """Create a link between a source and a news event seed."""
        try:
            client = await get_supabase_admin_client()
            await client.table("news_event_seed_sources").insert({
                "source_id": str(source_id),
                "news_event_seed_id": str(news_event_seed_id)
            }).execute()

            logger.info(
                "Linked source to news event seed",
                source_id=str(source_id),
                news_event_seed_id=str(news_event_seed_id)
            )
            return True
        except Exception as e:
            logger.error(
                "Failed to link source to news event seed",
                source_id=str(source_id),
                news_event_seed_id=str(news_event_seed_id),
                error=str(e),
            )
            return False

    async def create_and_link_sources_for_ingested_event(
        self, ingested_event_id: UUID, sources: List[Source]
    ) -> List[Source]:
        """
        Create sources and link them to an ingested event.

        Returns the list of created sources with their IDs.
        """
        created_sources = []
        for source in sources:
            try:
                # Check if source with this URL already exists
                existing_source = await self.get_by_url(str(source.url))

                if existing_source:
                    # Use existing source
                    source_to_link = existing_source
                else:
                    # Create new source
                    source_to_link = await super().create(source)

                if source_to_link:
                    # Link to ingested event
                    await self.link_source_to_ingested_event(
                        source_to_link.id, ingested_event_id
                    )
                    created_sources.append(source_to_link)
            except Exception as e:
                logger.error(
                    "Failed to create and link source",
                    url=str(source.url),
                    error=str(e)
                )

        return created_sources

    async def create_and_link_sources_for_news_event_seed(
        self, news_event_seed_id: UUID, sources: List[Source]
    ) -> List[Source]:
        """
        Create sources and link them to a news event seed.

        Returns the list of created sources with their IDs.
        """
        created_sources = []
        for source in sources:
            try:
                # Check if source with this URL already exists
                existing_source = await self.get_by_url(str(source.url))

                if existing_source:
                    # Use existing source
                    source_to_link = existing_source
                else:
                    # Create new source
                    source_to_link = await super().create(source)

                if source_to_link:
                    # Link to news event seed
                    await self.link_source_to_news_event_seed(
                        source_to_link.id, news_event_seed_id
                    )
                    created_sources.append(source_to_link)
            except Exception as e:
                logger.error(
                    "Failed to create and link source",
                    url=str(source.url),
                    error=str(e)
                )

        return created_sources
