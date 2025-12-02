# backend/agents/insights/insights_agent.py

"""Engagement insights and learning agent."""

from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage

from backend.config.settings import settings
from backend.config.prompts import get_global_system_prompt
from backend.tools import create_engagement_tools
from backend.database.repositories.insights import InsightsRepository
from backend.database.repositories.completed_posts import CompletedPostRepository
from backend.models.insights import InsightReport
from backend.utils import get_logger

logger = get_logger(__name__)


class InsightReportOutput(BaseModel):
    """Structured engagement insight report."""
    summary: str = Field(..., description="High-level takeaway in 1-2 sentences")
    findings: str = Field(..., description="Detailed analysis with specific metrics, patterns, and recommendations (2-4 paragraphs)")
    key_recommendations: List[str] = Field(default_factory=list, description="Concrete, implementable recommendations")


class InsightsAgent:
    """
    Agent for analyzing engagement data and generating insights.

    Uses Meta API engagement tools to understand what content works
    with the target audience.
    """

    def __init__(self, business_asset_id: str):
        self.business_asset_id = business_asset_id
        self.insights_repo = InsightsRepository()
        self.posts_repo = CompletedPostRepository()

        # Load prompts
        prompt_path = Path(__file__).parent / "prompts" / "insights.txt"
        self.agent_prompt = prompt_path.read_text()
        self.global_prompt = get_global_system_prompt(self.business_asset_id)

        # Initialize LLM
        self.llm = ChatOpenAI(
            model=settings.default_model_name,
            api_key=settings.get_model_api_key(),
            temperature=0.3,  # Lower temperature for analytical work
        )

        # Create tools
        self.tools = create_engagement_tools(business_asset_id)

        # Create agent
        self.agent_executor = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=f"{self.global_prompt}\n\n{self.agent_prompt}",
            response_format=ToolStrategy(InsightReportOutput)
        )

    async def analyze_engagement(self, days: int = 14) -> Dict[str, Any]:
        """
        Analyze engagement data and generate insights.

        Args:
            days: Number of days to analyze (default: 14)

        Returns:
            Created insight report
        """
        logger.info("Starting engagement analysis", days=days)

        try:
            # Get recent posts to analyze
            recent_posts = await self._get_recent_posts(days)

            if not recent_posts:
                logger.warning("No recent posts found to analyze")
                return await self._create_empty_report()

            # Build context about posts for the agent
            posts_context = self._format_posts_context(recent_posts)

            # Run agent
            input_context = f"""Analyze engagement data for our social media content from the past {days} days.

Recent Posts Context:
{posts_context}

Instructions:
1. Use your Meta Graph API tools to gather comprehensive engagement metrics:
   - Page-level and account-level insights for the time period
   - Post-specific metrics for individual content (use platform_post_id from context)
   - Video/reel insights for visual content (check if posts have media_ids)
2. Analyze the data to identify patterns in performance:
   - Compare different content types, formats, and platforms
   - Look at engagement quality (saves/shares vs. just likes)
   - Examine reach and view metrics alongside interactions
3. Generate comprehensive insights about:
   - What content types and formats drive the best engagement
   - Which metrics indicate high-quality audience engagement
   - Patterns in underperforming content
   - Platform-specific trends (Facebook vs. Instagram)
4. Provide specific, data-driven, actionable recommendations

Your analysis should be thorough, metrics-based, and honest about what's working and what isn't.
Include specific numbers from your tool calls to support your conclusions.
"""
            config = {"verbose": True, "max_iterations": 20}
            result = await self.agent_executor.ainvoke(
                {"messages": [("human", input_context)]},
                config=config
            )

            # Extract structured output and tool calls
            structured_output: InsightReportOutput = result.get("structured_response")
            tool_calls = self._extract_tool_calls(result.get("messages", []))

            if not structured_output:
                logger.warning("Agent did not return a structured response")
                return await self._create_empty_report()

            # Save insight report
            insight_report = InsightReport(
                business_asset_id=self.business_asset_id,
                summary=structured_output.summary,
                findings=structured_output.findings,
                tool_calls=tool_calls,
                created_by=settings.default_model_name
            )

            # Save to database
            created_report = await self.insights_repo.create(insight_report)
            logger.info("Insight report saved", report_id=str(created_report.id))
            report = created_report.model_dump(mode="json")

            logger.info("Engagement analysis complete", report_id=report["id"])
            return report

        except Exception as e:
            logger.error("Error in engagement analysis", error=str(e))
            raise

    async def _get_recent_posts(self, days: int) -> List[Dict[str, Any]]:
        """Get recent completed posts from database."""
        # Calculate cutoff date
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(days=days)

        # Get posts (this would need to be implemented in the repository)
        # For now, return a simplified query
        return await self.posts_repo.get_posts_since(self.business_asset_id, cutoff)

    def _format_posts_context(self, posts: List[Dict[str, Any]]) -> str:
        """Format posts information for agent context."""
        if not posts:
            return "No recent posts found."

        context = f"Total Posts: {len(posts)}\n\n"

        limit = settings.insights_posts_limit
        for i, post in enumerate(posts[:limit], 1):
            platform = post.get("platform", "unknown")
            platform_post_id = post.get("platform_post_id")
            post_type = post.get("post_type", "unknown")
            text = post.get("text", "[No text]")[:100]
            published_at = post.get("published_at", "Unknown")

            context += f"{i}. Platform: {platform}\n"
            context += f"   Post Type: {post_type}\n"
            if platform_post_id:
                context += f"   Platform Post ID: {platform_post_id}\n"
            context += f"   Published: {published_at}\n"
            context += f"   Text: {text}...\n\n"

        if len(posts) > limit:
            context += f"... and {len(posts) - limit} more posts\n"

        return context

    def _extract_tool_calls(self, messages: List) -> List[Dict[str, Any]]:
        """Extract tool calls from agent execution for logging."""
        from langchain_core.messages import ToolMessage

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

    async def _create_empty_report(self) -> Dict[str, Any]:
        """Create a report when no posts are available."""
        insight_report = InsightReport(
            business_asset_id=self.business_asset_id,
            summary="No posts available for analysis in the specified time period.",
            findings="Unable to generate insights as no posts have been published recently. "
                    "Run content creation and publishing workflows first.",
            tool_calls=[],
            created_by=settings.default_model_name
        )

        # Save to database
        created_report = await self.insights_repo.create(insight_report)

        return created_report.model_dump(mode="json")


async def run_insights_analysis(business_asset_id: str, days: int = 14) -> Dict[str, Any]:
    """
    CLI entry point for insights analysis.

    Args:
        business_asset_id: Business asset ID for multi-tenancy
        days: Number of days to analyze

    Returns:
        Created insight report
    """
    agent = InsightsAgent(business_asset_id)
    return await agent.analyze_engagement(days)