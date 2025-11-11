# backend/agents/news_event/deep_research.py

"""OpenAI o4-mini deep research agent for news ingestion."""

import aiohttp
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional

from backend.config.settings import settings
from backend.database.repositories.news_event_seeds import NewsEventSeedRepository
from backend.utils import get_logger

logger = get_logger(__name__)


class DeepResearchAgent:
    """
    Agent for deep research using OpenAI o4-mini-deep-research.

    Uses the OpenAI Responses API to perform comprehensive research,
    then parses results into news events.
    """

    def __init__(self):
        self.api_key = settings.openai_api_key
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not configured")

        self.api_base = "https://api.openai.com/v1/responses"
        self.research_model = "o4-mini-deep-research"
        self.parser_model = "gpt-4o-mini"  # Use GPT-4o-mini for parsing
        self.repo = NewsEventSeedRepository()

    async def research_and_ingest(
        self,
        topic: str,
        num_events: int = 5,
        max_tool_calls: int = 60
    ) -> List[Dict[str, Any]]:
        """
        Perform deep research and ingest news events.

        Args:
            topic: Topic to research
            num_events: Number of events to extract
            max_tool_calls: Maximum tool calls for research

        Returns:
            List of ingested events
        """
        logger.info("Starting deep research", topic=topic, num_events=num_events)

        try:
            # Step 1: Perform deep research
            research_report = await self._perform_deep_research(topic, max_tool_calls)

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
                topic=topic,
                events_ingested=len(saved_events)
            )

            return saved_events

        except Exception as e:
            logger.error("Error in deep research", error=str(e))
            raise

    async def _perform_deep_research(self, topic: str, max_tool_calls: int) -> str:
        """Perform deep research using o4-mini-deep-research."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        research_prompt = f"""Produce a comprehensive, citation-rich research report on the latest news and events about {topic}.

Focus on:
- Recent events (within the past 30 days)
- Significant developments, announcements, or changes
- Events with local or community impact
- Verified information from credible sources

For each event, include:
- What happened
- When it occurred
- Where it took place
- Why it matters
- Credible source citations with URLs

Format the report clearly with sections for each major event."""

        payload = {
            "model": self.research_model,
            "input": research_prompt,
            "tools": [{"type": "web_search_preview"}],
            "reasoning": {"summary": "auto"},
            "max_tool_calls": max_tool_calls,
            "max_output_tokens": 4000
        }

        logger.info("Submitting deep research request", model=self.research_model)

        async with aiohttp.ClientSession() as session:
            async with session.post(self.api_base, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Deep research API error ({response.status}): {error_text}")

                result = await response.json()

                # Check status
                status = result.get("status")
                if status == "failed":
                    error = result.get("error", {})
                    raise Exception(f"Research failed: {error.get('message', 'Unknown error')}")

                # Extract text output
                output = result.get("output", [])
                research_text = ""

                for item in output:
                    if item.get("type") == "text":
                        research_text += item.get("text", "")

                if not research_text:
                    raise Exception("No research output generated")

                logger.info("Deep research completed", length=len(research_text))
                return research_text

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
          "created_at": "{datetime.utcnow().isoformat()}Z"
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
                {"role": "system", "content": "You are a research analyst who extracts structured information from reports."},
                {"role": "user", "content": parser_prompt}
            ],
            "response_format": {"type": "json_object"}
        }

        logger.info("Parsing research report", parser_model=self.parser_model)

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Parser API error ({response.status}): {error_text}")

                result = await response.json()
                content = result["choices"][0]["message"]["content"]

                # Parse JSON
                import json
                parsed = json.loads(content)
                return parsed.get("events", [])

    async def _save_ingested_event(self, event_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Save an ingested event to the database."""
        try:
            ingested_event_data = {
                "start_time": event_data["start_time"],
                "end_time": event_data.get("end_time"),
                "location": event_data["location"],
                "description": event_data["description"],
                "sources": event_data.get("sources", [])
            }

            # Save to database
            event_id = await self.repo.create_ingested_event(ingested_event_data)

            logger.info("Ingested event saved", event_id=event_id, name=event_data["name"])

            return {
                "id": event_id,
                **ingested_event_data
            }

        except Exception as e:
            logger.error("Error saving ingested event", error=str(e), event_name=event_data.get("name"))
            return None


async def run_deep_research(topic: str, num_events: int = 5) -> List[Dict[str, Any]]:
    """
    CLI entry point for running deep research.

    Args:
        topic: Topic to research
        num_events: Number of events to extract

    Returns:
        List of ingested events
    """
    agent = DeepResearchAgent()
    return await agent.research_and_ingest(topic, num_events)
