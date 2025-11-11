# backend/agents/news_event/deduplicator.py

"""Event deduplication and consolidation agent."""

from datetime import datetime
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from backend.config.settings import settings
from backend.database.repositories.news_event_seeds import NewsEventSeedRepository
from backend.models.seeds import NewsEventSeed, Source
from backend.utils import get_logger

logger = get_logger(__name__)


class DeduplicatorAgent:
    """
    Agent for deduplicating and consolidating ingested news events.

    Compares new ingested events against existing canonical news event seeds
    and either merges them or creates new seeds.
    """

    def __init__(self):
        self.repo = NewsEventSeedRepository()

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
  "matching_event_id": "uuid or null",
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
        ingested_events = await self.repo.get_unprocessed_ingested_events()

        if not ingested_events:
            logger.info("No ingested events to process")
            return {"processed": 0, "merged": 0, "new": 0}

        # Get all existing canonical events
        canonical_events = await self.repo.get_all()

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
                    canonical_events.append(result["canonical_event"])

                stats["processed"] += 1

            except Exception as e:
                logger.error(
                    "Error processing ingested event",
                    ingested_id=ingested.get("id"),
                    error=str(e)
                )

        logger.info("Deduplication complete", stats=stats)
        return stats

    async def _process_ingested_event(
        self,
        ingested: Dict[str, Any],
        canonical_events: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Process a single ingested event."""
        logger.info("Processing ingested event", ingested_id=ingested.get("id"))

        # If no canonical events exist, create first one
        if not canonical_events:
            canonical = await self._create_canonical_event(ingested)
            return {"action": "new", "canonical_event": canonical}

        # Check for duplicates using LLM
        duplicate_result = await self._find_duplicate(ingested, canonical_events)

        if duplicate_result["is_duplicate"]:
            # Merge with existing event
            canonical_id = duplicate_result["matching_event_id"]
            await self._merge_with_canonical(ingested, canonical_id)
            return {"action": "merged", "canonical_id": canonical_id}
        else:
            # Create new canonical event
            canonical = await self._create_canonical_event(ingested)
            return {"action": "new", "canonical_event": canonical}

    async def _find_duplicate(
        self,
        ingested: Dict[str, Any],
        canonical_events: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Use LLM to find if ingested event is duplicate of existing event."""
        # Format existing events for prompt
        existing_text = ""
        for i, event in enumerate(canonical_events, 1):
            existing_text += f"\n{i}. ID: {event.get('id')}\n"
            existing_text += f"   Name: {event.get('name')}\n"
            existing_text += f"   Location: {event.get('location')}\n"
            existing_text += f"   Time: {event.get('start_time')} to {event.get('end_time')}\n"
            existing_text += f"   Description: {event.get('description')[:200]}...\n"

        # Prepare prompt variables
        prompt_vars = {
            "ingested_name": "New Event",  # Ingested events don't have names
            "ingested_location": ingested.get("location", "Unknown"),
            "ingested_start": ingested.get("start_time", "Unknown"),
            "ingested_end": ingested.get("end_time", "Unknown"),
            "ingested_description": ingested.get("description", ""),
            "existing_events": existing_text or "No existing events"
        }

        # Call LLM
        chain = self.dedup_prompt | self.llm
        response = await chain.ainvoke(prompt_vars)

        # Parse JSON response
        import json
        try:
            result = json.loads(response.content)
        except json.JSONDecodeError:
            logger.warning("Failed to parse LLM response, assuming not duplicate")
            result = {
                "is_duplicate": False,
                "matching_event_id": None,
                "confidence": "low",
                "reasoning": "Failed to parse LLM response"
            }

        logger.info(
            "Duplicate check result",
            ingested_id=ingested.get("id"),
            is_duplicate=result["is_duplicate"],
            confidence=result.get("confidence")
        )

        return result

    async def _create_canonical_event(self, ingested: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new canonical news event seed from ingested event."""
        # Generate a name from description (first sentence or truncated description)
        description = ingested.get("description", "")
        name = description.split(".")[0] if "." in description else description[:100]

        # Convert sources to Source objects if they're dictionaries
        sources = []
        for src in ingested.get("sources", []):
            if isinstance(src, dict):
                sources.append(Source(
                    url=src["url"],
                    key_findings=src["key_findings"],
                    found_by=src.get("found_by", "Unknown")
                ))
            else:
                sources.append(src)

        # Create NewsEventSeed model instance
        canonical_event = NewsEventSeed(
            name=name,
            start_time=ingested.get("start_time"),
            end_time=ingested.get("end_time"),
            location=ingested.get("location"),
            description=ingested.get("description"),
            sources=sources
        )

        # Save to database (note: create is synchronous, not async)
        created_event = self.repo.create(canonical_event)

        logger.info("Created new canonical event", canonical_id=str(created_event.id), name=name)

        return created_event.model_dump(mode="json")

    async def _merge_with_canonical(self, ingested: Dict[str, Any], canonical_id: str):
        """Merge ingested event with existing canonical event."""
        # Get existing canonical event
        canonical = await self.repo.get_by_id(canonical_id)
        if not canonical:
            raise Exception(f"Canonical event {canonical_id} not found")

        # Merge descriptions (append ingested to canonical)
        existing_desc = canonical.get("description", "")
        new_desc = ingested.get("description", "")
        merged_description = f"{existing_desc}\n\nAdditional information: {new_desc}"

        # Merge sources (deduplicate by URL)
        existing_sources = canonical.get("sources", [])
        new_sources = ingested.get("sources", [])

        existing_urls = {src.get("url") for src in existing_sources}
        merged_sources = existing_sources.copy()

        for src in new_sources:
            if src.get("url") not in existing_urls:
                merged_sources.append(src)

        # Update canonical event
        updates = {
            "description": merged_description,
            "sources": merged_sources
        }

        await self.repo.update(canonical_id, updates)

        logger.info(
            "Merged ingested event with canonical",
            canonical_id=canonical_id,
            new_sources_added=len(merged_sources) - len(existing_sources)
        )


async def run_deduplication() -> Dict[str, int]:
    """
    CLI entry point for running deduplication.

    Returns:
        Statistics about the deduplication process
    """
    agent = DeduplicatorAgent()
    return await agent.deduplicate_all()
