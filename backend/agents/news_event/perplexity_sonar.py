# backend/agents/news_event/perplexity_sonar.py

"""Perplexity Sonar news ingestion agent."""

import aiohttp
from typing import List, Dict, Any
from pathlib import Path
import json

from backend.config.settings import settings
from backend.database.repositories import IngestedEventRepository
from backend.models.seeds import IngestedEvent, Source
from backend.utils import get_logger

logger = get_logger(__name__)


class PerplexitySonarAgent:
    """
    Agent for ingesting news events using Perplexity Sonar API.

    Uses structured output to get news events in standardized format.
    """

    def __init__(self, business_asset_id: str):
        self.business_asset_id = business_asset_id
        self.api_key = settings.perplexity_api_key
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY not configured")

        self.api_base = "https://api.perplexity.ai/chat/completions"
        self.model = "sonar-pro"
        self.repo = IngestedEventRepository()

        # Load system prompt
        prompt_path = Path(__file__).parent / "prompts" / "perplexity_sonar.txt"
        self.system_prompt = prompt_path.read_text()

    async def ingest_news(self, topic: str, num_events: int = 5) -> List[Dict[str, Any]]:
        """
        Ingest news events for a given topic.

        Args:
            topic: Topic to search for (e.g., "Philadelphia", "AI technology")
            num_events: Number of events to retrieve (default: 5)

        Returns:
            List of ingested event dictionaries
        """
        logger.info("Starting Perplexity Sonar news ingestion", topic=topic, num_events=num_events)

        try:
            # Build user query
            user_query = f"Summarize the top {num_events} recent news events about {topic}. "
            user_query += "Include name, timing, location, a 2–3 sentence description, and credible sources."

            # Call Perplexity API
            events_data = await self._call_perplexity_api(user_query)

            # Save to database as ingested events
            saved_events = []
            for event_data in events_data:
                ingested_event = await self._save_ingested_event(event_data)
                if ingested_event:
                    saved_events.append(ingested_event)

            logger.info(
                "Perplexity Sonar ingestion complete",
                topic=topic,
                events_ingested=len(saved_events)
            )

            return saved_events

        except Exception as e:
            logger.error("Error in Perplexity Sonar ingestion", error=str(e))
            raise

    async def _call_perplexity_api(self, query: str) -> List[Dict[str, Any]]:
        """Call Perplexity API with structured output."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Define JSON schema for structured output
        json_schema = {
            "name": "NewsEventsResponse",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "news_events": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {
                                    "type": "string",
                                    "description": "A unique summary identifier or key sentence"
                                },
                                "name": {
                                    "type": "string",
                                    "description": "Concise event title"
                                },
                                "start_time": {
                                    "type": "string",
                                    "description": "Event start date/time in ISO 8601 format"
                                },
                                "end_time": {
                                    "type": ["string", "null"],
                                    "description": "Event end date/time in ISO 8601 format or null"
                                },
                                "location": {
                                    "type": "string",
                                    "description": "Where the event took place"
                                },
                                "description": {
                                    "type": "string",
                                    "description": "2–3 sentence summary"
                                },
                                "sources": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "url": {"type": "string", "format": "uri"},
                                            "key_findings": {"type": "string"},
                                            "found_by": {
                                                "type": "string",
                                                "description": "Agent or source that discovered this link"
                                            },
                                            "created_at": {"type": "string"}
                                        },
                                        "required": ["url", "key_findings", "found_by", "created_at"],
                                        "additionalProperties": False
                                    }
                                },
                                "created_at": {
                                    "type": "string",
                                    "description": "Timestamp for when the event object was created"
                                }
                            },
                            "required": [
                                "id", "name", "start_time", "end_time",
                                "location", "description", "sources", "created_at"
                            ],
                            "additionalProperties": False
                        }
                    }
                },
                "required": ["news_events"],
                "additionalProperties": False
            }
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": query}
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": json_schema
            }
        }

        # Assuming self.api_base = "https://api.perplexity.ai/chat/completions"
        async with aiohttp.ClientSession() as session:
            async with session.post(self.api_base, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Perplexity API error ({response.status}): {error_text}")

                result = await response.json()

                # Extract content from response
                content = result["choices"][0]["message"]["content"]

                # Parse JSON content (Perplexity returns a JSON string in the 'content' field)
                parsed = json.loads(content)
                return parsed["news_events"]

    async def _save_ingested_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save an ingested event to the database."""
        try:
            # Convert sources to Source objects
            sources = []
            for src in event_data.get("sources", []):
                sources.append(Source(
                    url=src["url"],
                    key_findings=src["key_findings"],
                    found_by="Perplexity Sonar"
                ))

            # Create IngestedEvent model instance
            ingested_event = IngestedEvent(
                business_asset_id=self.business_asset_id,
                name=event_data["name"],
                start_time=event_data["start_time"],
                end_time=event_data.get("end_time"),
                location=event_data["location"],
                description=event_data["description"],
                sources=sources,
                ingested_by="Perplexity Sonar"
            )

            # Convert to dict for repository (repository expects Dict[str, Any])
            event_dict = ingested_event.model_dump(mode="json", exclude={"id"})

            # Save to database
            created_event = await self.repo.create(event_dict)

            logger.info("Ingested event saved", event_id=str(created_event.id), name=event_data["name"])

            return created_event.model_dump(mode="json")

        except Exception as e:
            logger.error("Error saving ingested event", error=str(e), event_name=event_data.get("name"))
            return None


async def run_perplexity_ingestion(business_asset_id: str, topic: str, num_events: int = 5) -> List[Dict[str, Any]]:
    """
    CLI entry point for running Perplexity Sonar ingestion.

    Args:
        business_asset_id: Business asset ID for multi-tenancy
        topic: Topic to search for
        num_events: Number of events to retrieve

    Returns:
        List of ingested events
    """
    agent = PerplexitySonarAgent(business_asset_id)
    return await agent.ingest_news(topic, num_events)
