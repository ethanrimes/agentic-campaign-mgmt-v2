# backend/agents/trend_seed/trend_searcher.py

"""Trend discovery agent using social media scraping."""

from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, ToolMessage

from backend.config.settings import settings
from backend.config.prompts import get_global_system_prompt
from backend.tools import (
    create_instagram_scraper_tools,
    create_facebook_scraper_tools,
    create_knowledge_base_tools
)
from backend.database.repositories.trend_seeds import TrendSeedsRepository
from backend.models.seeds import TrendSeed
from backend.utils import get_logger

logger = get_logger(__name__)


class TrendSeedOutput(BaseModel):
    """Structured social media trend seed."""
    name: str = Field(..., description="Concise trend name (5-10 words)")
    description: str = Field(..., description="Detailed analysis of why this trend matters (2-3 paragraphs)")
    hashtags: List[str] = Field(default_factory=list, description="List of relevant hashtags (without # symbol)")
    key_insights: List[str] = Field(default_factory=list, description="Key insights about the trend")


class TrendSearcherAgent:
    """
    Agent for discovering social media trends.

    Uses Instagram and Facebook scraping tools to identify trending content,
    hashtags, and patterns relevant to the target audience.
    """

    def __init__(self, business_asset_id: str):
        self.business_asset_id = business_asset_id
        self.repo = TrendSeedsRepository()

        # Load prompts
        prompt_path = Path(__file__).parent / "prompts" / "trend_searcher.txt"
        self.agent_prompt = prompt_path.read_text()
        self.global_prompt = get_global_system_prompt(self.business_asset_id)

        # Initialize LLM
        self.llm = ChatOpenAI(
            model=settings.default_model_name,
            api_key=settings.get_model_api_key(),
            temperature=0.7,  # Higher temperature for creative exploration
        )

        # Create tools
        self.tools = [
            *create_instagram_scraper_tools(),
            *create_facebook_scraper_tools(),
            *create_knowledge_base_tools(business_asset_id),
        ]

        # Create agent
        self.agent_executor = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=f"{self.global_prompt}\n\n{self.agent_prompt}",
            response_format=ToolStrategy(TrendSeedOutput)
        )

    def _extract_tool_calls(self, messages: List) -> List[Dict[str, Any]]:
        """Extract tool calls from agent execution for logging."""
        tool_calls = []
        tool_results = {}

        # First pass: collect tool results by tool_call_id
        for message in messages:
            if isinstance(message, ToolMessage):
                tool_results[message.tool_call_id] = message.content

        # Second pass: extract tool calls and match with results
        for message in messages:
            if isinstance(message, AIMessage) and message.tool_calls:
                for tool_call in message.tool_calls:
                    tool_call_id = tool_call.get("id")
                    result = tool_results.get(tool_call_id, "No result captured")

                    tool_calls.append({
                        "tool_name": tool_call.get("name", "unknown"),
                        "arguments": tool_call.get("args", {}),
                        "result": result,
                        "timestamp": datetime.utcnow()
                    })

        return tool_calls

    async def discover_trends(self, query: str = None, count: int = 1) -> List[Dict[str, Any]]:
        """
        Discover social media trends.

        Args:
            query: Search query or guidance for trend discovery. If None, discovers trends
                   relevant to target audience.
            count: Number of trends to discover

        Returns:
            List of created trend seeds
        """
        logger.info("Starting trend discovery", query=query, count=count)

        # Build query if not provided
        if not query:
            credentials = settings.get_business_asset_credentials(self.business_asset_id)
            target_audience = credentials.target_audience
            query = f"trends and viral content relevant to this target audience: {target_audience}"

        trends = []

        for i in range(count):
            try:
                logger.info(f"Discovering trend {i+1}/{count}")

                input_context = f"""Discover a new social media trend relevant to our audience.

Search Query/Theme: {query}

Use your tools to:
1. Search Instagram and Facebook for trending content
2. Check existing trends in the knowledge base to avoid duplicates
3. Review insights reports to understand what resonates with our audience
4. Synthesize your findings into a comprehensive trend analysis

Focus on trends that are:
- Currently popular and gaining traction
- Relevant to our target audience
- Actionable for content creation
- Supported by specific examples

Provide your final analysis as a structured trend insight."""
                
                # Run agent
                config = {"verbose": True, "max_iterations": 15}
                result = await self.agent_executor.ainvoke(
                    {"messages": [("human", input_context)]},
                    config=config
                )

                # The agent's structured response is here
                structured_output: TrendSeedOutput = result.get("structured_response")

                if not structured_output:
                    logger.warning("Agent did not return a structured response")
                    continue

                # Extract tool calls for logging
                messages = result.get("messages", [])
                tool_calls_history = self._extract_tool_calls(messages)

                # Extract posts and hashtags from tool calls
                posts = []
                hashtags = set(structured_output.hashtags)
                users = []

                tool_calls_map = {}  # tool_call_id -> {name: str, args: dict}
                for message in messages:
                    if isinstance(message, AIMessage) and message.tool_calls:
                        for tc in message.tool_calls:
                            tool_calls_map[tc["id"]] = {"name": tc["name"], "args": tc["args"]}

                    if isinstance(message, ToolMessage):
                        tool_call_id = message.tool_call_id
                        observation = str(message.content)

                        if tool_call_id in tool_calls_map:
                            tool_name = tool_calls_map[tool_call_id]["name"]
                            tool_input = tool_calls_map[tool_call_id]["args"]

                            # Extract relevant data from tool calls
                            if "instagram" in tool_name.lower():
                                if "hashtag" in tool_name.lower() and isinstance(tool_input, dict):
                                    query = tool_input.get("query", "")
                                    if query:
                                        hashtags.add(query)

                            # Parse observation for posts/users
                            if "instagram.com/p/" in observation:
                                import re
                                codes = re.findall(r'instagram\.com/p/([A-Za-z0-9_-]+)', observation)
                                for code in codes:
                                    if code not in [p.get("link", "").split("/")[-2] for p in posts if "link" in p]:
                                        posts.append({
                                            "link": f"https://www.instagram.com/p/{code}/",
                                            "platform": "instagram"
                                        })

                # Save to database
                trend_seed = TrendSeed(
                    business_asset_id=self.business_asset_id,
                    name=structured_output.name,
                    description=structured_output.description,
                    hashtags=list(hashtags),
                    posts=posts[:10],  # Limit to 10 example posts
                    users=users[:10],  # Limit to 10 users
                    tool_calls=tool_calls_history,
                    created_by=settings.default_model_name
                )

                # Save to database
                created_trend = await self.repo.create(trend_seed)
                logger.info("Trend seed saved", trend_id=str(created_trend.id), name=created_trend.name)
                trends.append(created_trend.model_dump(mode="json"))

            except Exception as e:
                logger.error(f"Error discovering trend {i+1}", error=str(e))

        logger.info("Trend discovery complete", trends_created=len(trends))
        return trends


async def run_trend_discovery(business_asset_id: str, query: str = None, count: int = 1) -> List[Dict[str, Any]]:
    """
    CLI entry point for trend discovery.

    Args:
        business_asset_id: Business asset ID for multi-tenancy
        query: Search query or theme for trend discovery (optional - uses target audience if not provided)
        count: Number of trends to discover

    Returns:
        List of created trend seeds
    """
    agent = TrendSearcherAgent(business_asset_id)
    return await agent.discover_trends(query, count)