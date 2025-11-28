# backend/agents/news_event/deep_research.py

"""OpenAI o1-mini deep research agent for news ingestion."""

import aiohttp
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

from backend.config.settings import settings
from backend.database.repositories.news_event_seeds import IngestedEventRepository
from backend.models.seeds import IngestedEvent, Source
from backend.utils import get_logger

logger = get_logger(__name__)


class DeepResearchAgent:
    """
    Agent for deep research using OpenAI o4-mini.

    Uses the OpenAI Responses API to perform comprehensive research with o4-mini-deep-research,
    then parses results into structured news events with gpt-4o-mini.
    """

    def __init__(self, business_asset_id: str):
        self.business_asset_id = business_asset_id
        self.api_key = settings.openai_api_key
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not configured")

        self.responses_api_base = "https://api.openai.com/v1/responses"
        self.chat_api_base = "https://api.openai.com/v1/chat/completions"
        self.research_model = "o4-mini-deep-research-2025-06-26"
        self.parser_model = "gpt-4o-mini"
        self.repo = IngestedEventRepository()

        # Load system prompt for parser
        prompt_path = Path(__file__).parent / "prompts" / "deep_research_parser.txt"
        if prompt_path.exists():
            self.parser_system_prompt = prompt_path.read_text()
        else:
            self.parser_system_prompt = "You are a research analyst who extracts structured information from reports."

    async def research_and_ingest(
        self,
        query: str,
        num_events: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Perform deep research and ingest news events.

        Args:
            query: Research query/topic
            num_events: Number of events to extract

        Returns:
            List of ingested events
        """
        logger.info("Starting deep research", query=query, num_events=num_events)

        try:
            # Step 1: Perform deep research
            research_report = await self._perform_deep_research(query)

            # Step 2: Parse research into structured events
            events_data = await self._parse_research_to_events(research_report, num_events)

            # Step 3: Save to database as ingested events
            saved_events = []
            for event_data in events_data:
                ingested_event = await self._save_ingested_event(event_data)
                if ingested_event:
                    saved_events.append(ingested_event)

            logger.info(
                "Deep research complete",
                query=query,
                events_ingested=len(saved_events)
            )

            return saved_events

        except Exception as e:
            logger.error("Error in deep research", error=str(e))
            raise

    async def _perform_deep_research(self, query: str) -> str:
        """Perform deep research using o4-mini via the Responses API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        research_prompt = f"""Produce a comprehensive, citation-rich research report on: {query}

Focus on:
- Recent events (within the past 30 days)
- Significant developments, announcements, or changes
- Events with local or community impact
- Verified information from credible sources

For each event, include:
- What happened
- When it occurred (provide specific dates)
- Where it took place
- Why it matters
- Credible source citations with URLs

Format the report clearly with sections for each major event. Include as many relevant source URLs as possible."""

        payload = {
            "model": self.research_model,
            "reasoning": {"effort": "medium"},
            "tools": [{"type": "web_search_preview"}],
            "input": [
                {"role": "system", "content": "You are an expert research assistant specializing in news and current events."},
                {"role": "user", "content": research_prompt}
            ]
        }

        logger.info("Submitting deep research request", model=self.research_model, query=query)

        # Deep research can take several minutes, so set a long timeout
        timeout = aiohttp.ClientTimeout(total=600)  # 10 minutes
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(self.responses_api_base, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Deep research API error ({response.status}): {error_text}")

                result = await response.json()

                # Extract response content from Responses API format
                # The Responses API returns choices[0].message.content similar to chat completions
                content = result["choices"][0]["message"]["content"]

                if not content:
                    raise Exception("No research output generated")

                logger.info("Deep research completed", length=len(content))
                return content

    async def _parse_research_to_events(
        self,
        research_report: str,
        num_events: int
    ) -> List[Dict[str, Any]]:
        """Parse research report into structured events using GPT-4o-mini."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        current_time = datetime.now(timezone.utc).isoformat()

        parser_prompt = f"""Parse the following research report and extract the top {num_events} news events.

For each event, provide:
- name: Concise event title
- start_time: Event start date/time in ISO 8601 format (estimate if not exact)
- end_time: Event end date/time in ISO 8601 format or null for single-day/ongoing
- location: Geographic location (city, region, or "Global")
- description: 2-3 sentence summary of what happened and why it matters
- sources: Array of sources with:
  - url: Source URL from the report
  - key_findings: What this source contributed
  - found_by: "OpenAI Deep Research"
  - created_at: Current timestamp

Return as JSON with this structure:
{{
  "events": [
    {{
      "name": "Event Name",
      "start_time": "2025-01-01T00:00:00Z",
      "end_time": "2025-01-02T00:00:00Z",
      "location": "City, State",
      "description": "Description here",
      "sources": [
        {{
          "url": "https://...",
          "key_findings": "What was learned",
          "found_by": "OpenAI Deep Research",
          "created_at": "{current_time}"
        }}
      ]
    }}
  ]
}}

Research Report:
{research_report}
"""

        payload = {
            "model": self.parser_model,
            "messages": [
                {"role": "system", "content": self.parser_system_prompt},
                {"role": "user", "content": parser_prompt}
            ],
            "response_format": {"type": "json_object"}
        }

        logger.info("Parsing research report", parser_model=self.parser_model)

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.chat_api_base,
                headers=headers,
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Parser API error ({response.status}): {error_text}")

                result = await response.json()
                content = result["choices"][0]["message"]["content"]

                # Parse JSON
                parsed = json.loads(content)
                return parsed.get("events", [])

    async def _save_ingested_event(self, event_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Save an ingested event to the database."""
        try:
            # Convert sources to Source objects
            sources = []
            for src in event_data.get("sources", []):
                sources.append(Source(
                    url=src["url"],
                    key_findings=src["key_findings"],
                    found_by="OpenAI Deep Research"
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
                ingested_by="OpenAI Deep Research"
            )

            # Convert to dict for repository
            event_dict = ingested_event.model_dump(mode="json", exclude={"id"})

            # Save to database
            created_event = await self.repo.create(event_dict)

            logger.info("Ingested event saved", event_id=str(created_event.id), name=event_data["name"])

            return created_event.model_dump(mode="json")

        except Exception as e:
            logger.error("Error saving ingested event", error=str(e), event_name=event_data.get("name"))
            return None


async def run_deep_research(business_asset_id: str, query: str, num_events: int = 5) -> List[Dict[str, Any]]:
    """
    CLI entry point for running deep research.

    Args:
        business_asset_id: Business asset ID for multi-tenancy
        query: Research query/topic
        num_events: Number of events to extract

    Returns:
        List of ingested events
    """
    agent = DeepResearchAgent(business_asset_id)
    return await agent.research_and_ingest(query, num_events)
