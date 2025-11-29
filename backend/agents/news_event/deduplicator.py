# backend/agents/news_event/deduplicator.py

"""Event deduplication and consolidation agent."""

from datetime import datetime
from typing import List, Dict, Any, Optional
from uuid import UUID
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from backend.config.settings import settings
from backend.database.repositories.news_event_seeds import NewsEventSeedRepository, IngestedEventRepository
from backend.models.seeds import NewsEventSeed, IngestedEvent, Source
from backend.utils import get_logger

logger = get_logger(__name__)


class DeduplicatorAgent:
    """
    Agent for deduplicating and consolidating ingested news events.

    Compares new ingested events against existing canonical news event seeds
    and either merges them or creates new seeds.
    """

    def __init__(self, business_asset_id: str):
        self.business_asset_id = business_asset_id
        self.ingested_repo = IngestedEventRepository()
        self.canonical_repo = NewsEventSeedRepository()

        # Initialize LLM
        self.llm = ChatOpenAI(
            model=settings.default_model_name,
            api_key=settings.get_model_api_key(),
            temperature=0.3,  # Low temperature for consistent deduplication
        )

        self.dedup_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at identifying duplicate news events.

You will be given a new ingested event and a list of existing canonical events.
Your job is to determine if the ingested event is a duplicate of any existing event.

Two events are duplicates if they refer to the same underlying occurrence, even if described differently.

Consider:
- Time overlap (events happening at similar times)
- Location similarity (same or nearby locations)
- Topic/subject matter (same underlying story or occurrence)
- Source overlap (citing the same original sources)

Return your analysis as JSON:
{{
  "is_duplicate": true/false,
  "matching_event_id": "uuid of matching event if match or null",
  "confidence": "high/medium/low",
  "reasoning": "explanation of your decision"
}}"""),
            ("user", """Ingested Event:
Name: {ingested_name}
Location: {ingested_location}
Time: {ingested_start} to {ingested_end}
Description: {ingested_description}

Existing Canonical Events:
{existing_events}

Is this a duplicate? Which event does it match (if any)?""")
        ])

    async def deduplicate_all(self) -> Dict[str, int]:
        """
        Process all pending ingested events and deduplicate them.

        Returns:
            Statistics about the deduplication process
        """
        logger.info("Starting deduplication process")

        # Get all ingested events that haven't been processed
        ingested_events = await self.ingested_repo.get_unprocessed(self.business_asset_id)

        if not ingested_events:
            logger.info("No ingested events to process")
            return {"processed": 0, "merged": 0, "new": 0}

        # Get most recent canonical events for comparison using configurable limit
        canonical_events = await self.canonical_repo.get_recent(
            self.business_asset_id,
            limit=settings.deduplicator_canonical_seeds_limit
        )

        stats = {
            "processed": 0,
            "merged": 0,
            "new": 0
        }

        for ingested in ingested_events:
            try:
                result = await self._process_ingested_event(ingested, canonical_events)

                if result["action"] == "merged":
                    stats["merged"] += 1
                elif result["action"] == "new":
                    stats["new"] += 1
                    # Add to canonical list for subsequent comparisons
                    # Convert dict back to NewsEventSeed for type consistency
                    canonical_events.append(NewsEventSeed(**result["canonical_event"]))

                stats["processed"] += 1

            except Exception as e:
                logger.error(
                    "Error processing ingested event",
                    ingested_id=str(ingested.id),
                    error=str(e)
                )

        logger.info("Deduplication complete", stats=stats)
        return stats

    async def _process_ingested_event(
        self,
        ingested: IngestedEvent,
        canonical_events: List[NewsEventSeed]
    ) -> Dict[str, Any]:
        """Process a single ingested event."""
        logger.info("Processing ingested event", ingested_id=str(ingested.id))

        # If no canonical events exist, create first one
        if not canonical_events:
            canonical = await self._create_canonical_event(ingested)
            # Mark ingested event as processed
            await self.ingested_repo.mark_as_processed(self.business_asset_id, ingested.id, UUID(canonical["id"]))
            return {"action": "new", "canonical_event": canonical}

        # Check for duplicates using LLM
        duplicate_result = await self._find_duplicate(ingested, canonical_events)

        if duplicate_result["is_duplicate"]:
            # Merge with existing event
            canonical_id_str = duplicate_result["matching_event_id"]

            # Validate and clean UUID string
            if not canonical_id_str:
                logger.warning("LLM returned is_duplicate=True but no matching_event_id, creating new event")
                canonical = await self._create_canonical_event(ingested)
                await self.ingested_repo.mark_as_processed(self.business_asset_id, ingested.id, UUID(canonical["id"]))
                return {"action": "new", "canonical_event": canonical}

            # Clean up UUID string (strip whitespace, remove quotes)
            canonical_id_str = str(canonical_id_str).strip().strip('"').strip("'")

            # Validate it's a proper UUID
            try:
                canonical_id = UUID(canonical_id_str)
            except (ValueError, AttributeError) as e:
                logger.warning(
                    "Invalid UUID from LLM, creating new event",
                    raw_id=canonical_id_str,
                    error=str(e)
                )
                canonical = await self._create_canonical_event(ingested)
                await self.ingested_repo.mark_as_processed(self.business_asset_id, ingested.id, UUID(canonical["id"]))
                return {"action": "new", "canonical_event": canonical}

            await self._merge_with_canonical(ingested, str(canonical_id))
            # Mark ingested event as processed
            await self.ingested_repo.mark_as_processed(self.business_asset_id, ingested.id, canonical_id)
            return {"action": "merged", "canonical_id": str(canonical_id)}
        else:
            # Create new canonical event
            canonical = await self._create_canonical_event(ingested)
            # Mark ingested event as processed
            await self.ingested_repo.mark_as_processed(self.business_asset_id, ingested.id, UUID(canonical["id"]))
            return {"action": "new", "canonical_event": canonical}

    async def _find_duplicate(
        self,
        ingested: IngestedEvent,
        canonical_events: List[NewsEventSeed]
    ) -> Dict[str, Any]:
        """Use LLM to find if ingested event is duplicate of existing event."""
        # Format existing events for prompt
        existing_text = ""
        for i, event in enumerate(canonical_events, 1):
            existing_text += f"\n{i}. ID: {event.id}\n"
            existing_text += f"   Name: {event.name}\n"
            existing_text += f"   Location: {event.location}\n"
            existing_text += f"   Time: {event.start_time} to {event.end_time}\n"
            existing_text += f"   Description: {event.description[:200]}...\n"

        # Prepare prompt variables
        prompt_vars = {
            "ingested_name": ingested.name,
            "ingested_location": ingested.location,
            "ingested_start": ingested.start_time or "Unknown",
            "ingested_end": ingested.end_time or "Unknown",
            "ingested_description": ingested.description,
            "existing_events": existing_text or "No existing events"
        }

        # Call LLM
        chain = self.dedup_prompt | self.llm
        response = await chain.ainvoke(prompt_vars)

        # Parse JSON response (handle markdown-wrapped JSON)
        import json
        import re
        try:
            content = response.content
            # Strip markdown code fences if present
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
            if json_match:
                content = json_match.group(1)
            result = json.loads(content)
        except (json.JSONDecodeError, AttributeError) as e:
            logger.warning("Failed to parse LLM response, assuming not duplicate", error=str(e), content=response.content[:200])
            result = {
                "is_duplicate": False,
                "matching_event_id": None,
                "confidence": "low",
                "reasoning": "Failed to parse LLM response"
            }

        logger.info(
            "Duplicate check result",
            ingested_id=str(ingested.id),
            is_duplicate=result["is_duplicate"],
            confidence=result.get("confidence")
        )

        return result

    async def _create_canonical_event(self, ingested: IngestedEvent) -> Dict[str, Any]:
        """Create a new canonical news event seed from ingested event."""
        # Use the name from the ingested event
        name = ingested.name

        # Create NewsEventSeed model instance (sources are already Source objects)
        canonical_event = NewsEventSeed(
            business_asset_id=self.business_asset_id,
            name=name,
            start_time=ingested.start_time,
            end_time=ingested.end_time,
            location=ingested.location,
            description=ingested.description,
            sources=ingested.sources
        )

        # Save to database - convert model to dict
        created_event = await self.canonical_repo.create(
            canonical_event.model_dump(mode="json", exclude={"id"})
        )

        logger.info("Created new canonical event", canonical_id=str(created_event.id), name=name)

        return created_event.model_dump(mode="json")

    async def _merge_with_canonical(self, ingested: IngestedEvent, canonical_id: str):
        """Merge ingested event with existing canonical event."""
        # Get existing canonical event
        canonical = await self.canonical_repo.get_by_id(self.business_asset_id, UUID(canonical_id))
        if not canonical:
            raise Exception(f"Canonical event {canonical_id} not found")

        # Merge descriptions (append ingested to canonical)
        existing_desc = canonical.description
        new_desc = ingested.description
        merged_description = f"{existing_desc}\n\nAdditional information: {new_desc}"

        # Merge sources (deduplicate by URL)
        existing_sources = canonical.sources
        new_sources = ingested.sources

        existing_urls = {str(src.url) for src in existing_sources}
        merged_sources = existing_sources.copy()

        for src in new_sources:
            if str(src.url) not in existing_urls:
                merged_sources.append(src)

        # Convert sources to dicts for database update
        sources_dict = [src.model_dump(mode="json") for src in merged_sources]

        # Update canonical event
        updates = {
            "description": merged_description,
            "sources": sources_dict
        }

        await self.canonical_repo.update(self.business_asset_id, UUID(canonical_id), updates)

        logger.info(
            "Merged ingested event with canonical",
            canonical_id=canonical_id,
            new_sources_added=len(merged_sources) - len(existing_sources)
        )


async def run_deduplication(business_asset_id: str) -> Dict[str, int]:
    """
    CLI entry point for running deduplication.

    Args:
        business_asset_id: Business asset ID for multi-tenancy

    Returns:
        Statistics about the deduplication process
    """
    agent = DeduplicatorAgent(business_asset_id)
    return await agent.deduplicate_all()
