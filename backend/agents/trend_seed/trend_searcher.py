# backend/agents/trend_seed/trend_searcher.py

"""Trend discovery agent using social media scraping."""

from pathlib import Path
from typing import Dict, Any, List
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

from backend.config.settings import settings
from backend.config.prompts import get_global_system_prompt
from backend.tools import (
    create_instagram_scraper_tools,
    create_facebook_scraper_tools,
    create_knowledge_base_tools
)
from backend.database.repositories.trend_seeds import TrendSeedsRepository
from backend.utils import get_logger

logger = get_logger(__name__)


class TrendSearcherAgent:
    """
    Agent for discovering social media trends.

    Uses Instagram and Facebook scraping tools to identify trending content,
    hashtags, and patterns relevant to the target audience.
    """

    def __init__(self):
        self.repo = TrendSeedsRepository()

        # Load prompts
        prompt_path = Path(__file__).parent / "prompts" / "trend_searcher.txt"
        self.agent_prompt = prompt_path.read_text()
        self.global_prompt = get_global_system_prompt()

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
            *create_knowledge_base_tools(),
        ]

        # Create agent prompt template
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", f"{self.global_prompt}\n\n{self.agent_prompt}"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        # Create agent
        self.agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt_template
        )

        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            max_iterations=15,  # Allow multiple tool calls
            return_intermediate_steps=True
        )

    async def discover_trends(self, query: str, count: int = 1) -> List[Dict[str, Any]]:
        """
        Discover social media trends.

        Args:
            query: Search query or guidance for trend discovery
            count: Number of trends to discover

        Returns:
            List of created trend seeds
        """
        logger.info("Starting trend discovery", query=query, count=count)

        trends = []

        for i in range(count):
            try:
                logger.info(f"Discovering trend {i+1}/{count}")

                # Run agent
                result = await self.agent_executor.ainvoke({
                    "input": f"""Discover a new social media trend relevant to our audience.

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
                })

                # Extract the output
                output = result["output"]

                # Parse and save trend seed
                trend_seed = await self._parse_and_save_trend(output, result)

                if trend_seed:
                    trends.append(trend_seed)
                    logger.info("Trend seed created", trend_id=trend_seed["id"])

            except Exception as e:
                logger.error(f"Error discovering trend {i+1}", error=str(e))

        logger.info("Trend discovery complete", trends_created=len(trends))
        return trends

    async def _parse_and_save_trend(
        self,
        agent_output: str,
        full_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse agent output and save trend seed."""
        # Extract tool calls from intermediate steps
        intermediate_steps = full_result.get("intermediate_steps", [])

        # Collect posts, hashtags, and users mentioned in tool calls
        posts = []
        hashtags = set()
        users = []

        for action, observation in intermediate_steps:
            tool_name = action.tool
            tool_input = action.tool_input

            # Extract relevant data from tool calls
            if "instagram" in tool_name.lower():
                if "hashtag" in tool_name.lower() and isinstance(tool_input, dict):
                    query = tool_input.get("query", "")
                    if query:
                        hashtags.add(query)

            # Parse observation for posts/users (simplified - could be more sophisticated)
            if "instagram.com/p/" in str(observation):
                # Extract Instagram post codes
                import re
                codes = re.findall(r'instagram\.com/p/([A-Za-z0-9_-]+)', str(observation))
                for code in codes:
                    if code not in [p.get("link", "").split("/")[-2] for p in posts]:
                        posts.append({
                            "link": f"https://www.instagram.com/p/{code}/",
                            "platform": "instagram"
                        })

        # Use LLM to extract structured data from agent output
        structured_data = await self._extract_structured_trend(agent_output, list(hashtags), posts)

        # Save to database
        trend_data = {
            "name": structured_data.get("name", "Unnamed Trend"),
            "description": structured_data.get("description", agent_output[:500]),
            "hashtags": structured_data.get("hashtags", list(hashtags)),
            "posts": posts[:10],  # Limit to 10 example posts
            "users": users[:10],  # Limit to 10 users
            "created_by": settings.default_model_name
        }

        trend_id = await self.repo.create(trend_data)

        logger.info("Trend seed saved", trend_id=trend_id, name=trend_data["name"])

        return {
            "id": trend_id,
            **trend_data
        }

    async def _extract_structured_trend(
        self,
        agent_output: str,
        hashtags: List[str],
        posts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Use LLM to extract structured trend data from agent output."""
        extraction_prompt = f"""Extract structured trend information from the following trend analysis.

Trend Analysis:
{agent_output}

Extracted Hashtags: {', '.join(hashtags) if hashtags else 'None'}
Example Posts Found: {len(posts)}

Provide a JSON response with:
{{
  "name": "Concise trend name (5-10 words)",
  "description": "Detailed analysis of why this trend matters (2-3 paragraphs)",
  "hashtags": ["list", "of", "relevant", "hashtags"],
  "key_insights": ["insight 1", "insight 2", "insight 3"]
}}

Focus on creating a clear, actionable trend description that explains:
- What the trend is
- Why it's relevant to the target audience
- How it could be leveraged for content creation
- Supporting evidence from the analysis
"""

        extraction_llm = ChatOpenAI(
            model="gpt-4o-mini",  # Use faster model for extraction
            api_key=settings.openai_api_key,
            temperature=0.3
        )

        messages = [
            {"role": "system", "content": "You are a data extraction assistant. Extract structured information from text."},
            {"role": "user", "content": extraction_prompt}
        ]

        response = await extraction_llm.ainvoke(messages)

        # Parse JSON
        import json
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            logger.warning("Failed to parse extraction response")
            return {
                "name": "Trend Analysis",
                "description": agent_output[:500],
                "hashtags": hashtags,
                "key_insights": []
            }


async def run_trend_discovery(query: str = "", count: int = 1) -> List[Dict[str, Any]]:
    """
    CLI entry point for trend discovery.

    Args:
        query: Search query or theme for trend discovery
        count: Number of trends to discover

    Returns:
        List of created trend seeds
    """
    agent = TrendSearcherAgent()
    return await agent.discover_trends(query or "social media trends", count)
