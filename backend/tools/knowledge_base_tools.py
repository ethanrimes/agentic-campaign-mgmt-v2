# backend/tools/knowledge_base_tools.py

"""
Langchain tools for reading the knowledge database.
Shared by trend seed agent, ungrounded seed agent, and others.
"""

from langchain.tools import BaseTool
from typing import Optional, Type
from pydantic import BaseModel, Field
from backend.database.repositories import (
    NewsEventSeedRepository,
    TrendSeedsRepository,
    UngroundedSeedRepository,
    InsightsRepository,
)


class SearchNewsEventsInput(BaseModel):
    """Input for searching news events."""
    query: str = Field(description="Search query for news event names")
    limit: int = Field(default=5, description="Maximum results")


class SearchNewsEventsTool(BaseTool):
    """Tool to search news event seeds."""

    name: str = "search_news_events"
    description: str = "Search for news event seeds by name/description"
    args_schema: Type[BaseModel] = SearchNewsEventsInput

    def _run(self, query: str, limit: int = 5) -> str:
        """Search news events."""
        repo = NewsEventSeedRepository()
        seeds = repo.search_by_name(query, limit=limit)

        if not seeds:
            return f"No news events found matching '{query}'"

        results = []
        for seed in seeds:
            results.append(
                f"- {seed.name} ({seed.location}): {seed.description[:100]}..."
            )

        return "\n".join(results)


class GetRecentSeedsInput(BaseModel):
    """Input for getting recent seeds."""
    seed_type: str = Field(description="Type: 'news', 'trend', or 'ungrounded'")
    limit: int = Field(default=10, description="Maximum results")


class GetRecentSeedsTool(BaseTool):
    """Tool to get recent content seeds."""

    name: str = "get_recent_seeds"
    description: str = "Get recent content seeds of a specific type"
    args_schema: Type[BaseModel] = GetRecentSeedsInput

    def _run(self, seed_type: str, limit: int = 10) -> str:
        """Get recent seeds."""
        if seed_type == "news":
            repo = NewsEventSeedRepository()
        elif seed_type == "trend":
            repo = TrendSeedsRepository()
        elif seed_type == "ungrounded":
            repo = UngroundedSeedRepository()
        else:
            return f"Invalid seed type: {seed_type}"

        seeds = repo.get_recent(limit=limit)

        if not seeds:
            return f"No {seed_type} seeds found"

        results = []
        for seed in seeds:
            if hasattr(seed, 'name'):
                results.append(f"- {seed.name}")
            elif hasattr(seed, 'idea'):
                results.append(f"- {seed.idea}")

        return "\n".join(results)


class GetLatestInsightsInput(BaseModel):
    """Input for getting latest insights."""
    pass


class GetLatestInsightsTool(BaseTool):
    """Tool to get the latest insights report."""

    name: str = "get_latest_insights"
    description: str = "Get the most recent insights report about content performance"
    args_schema: Type[BaseModel] = GetLatestInsightsInput

    def _run(self) -> str:
        """Get latest insights."""
        repo = InsightsRepository()
        report = repo.get_latest()

        if not report:
            return "No insights reports found"

        return f"""Latest Insights Report (from {report.created_at}):

Summary: {report.summary}

Findings:
{report.findings}
"""


def create_knowledge_base_tools():
    """Create all knowledge base tools for use with Langchain agents."""
    return [
        SearchNewsEventsTool(),
        GetRecentSeedsTool(),
        GetLatestInsightsTool(),
    ]
