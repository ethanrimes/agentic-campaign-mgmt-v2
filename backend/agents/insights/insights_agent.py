# backend/agents/insights/insights_agent.py

"""Engagement insights and learning agent."""

from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from backend.config.settings import settings
from backend.config.prompts import get_global_system_prompt
from backend.tools import create_engagement_tools
from backend.database.repositories.insights import InsightsRepository
from backend.database.repositories.completed_posts import CompletedPostRepository
from backend.models.insights import InsightReport, ToolCall
from backend.utils import get_logger

logger = get_logger(__name__)


class InsightsAgent:
    """
    Agent for analyzing engagement data and generating insights.

    Uses Meta API engagement tools to understand what content works
    with the target audience.
    """

    def __init__(self):
        self.insights_repo = InsightsRepository()
        self.posts_repo = CompletedPostRepository()

        # Load prompts
        prompt_path = Path(__file__).parent / "prompts" / "insights.txt"
        self.agent_prompt = prompt_path.read_text()
        self.global_prompt = get_global_system_prompt()

        # Initialize LLM
        self.llm = ChatOpenAI(
            model=settings.default_model_name,
            api_key=settings.get_model_api_key(),
            temperature=0.3,  # Lower temperature for analytical work
        )

        # Create tools
        self.tools = create_engagement_tools()

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
            max_iterations=20,  # Allow many tool calls for thorough analysis
            return_intermediate_steps=True
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
            result = await self.agent_executor.ainvoke({
                "input": f"""Analyze engagement data for our social media content from the past {days} days.

Recent Posts Context:
{posts_context}

Instructions:
1. Use your tools to gather engagement metrics for these posts
2. Fetch and analyze comments to understand audience sentiment
3. Identify patterns in high-performing vs. low-performing content
4. Generate comprehensive insights about:
   - What content types drive engagement
   - What visual styles work best
   - What the audience wants more of
   - What isn't working
5. Provide specific, actionable recommendations

Your analysis should be thorough, data-driven, and honest about what's working and what isn't.
"""
            })

            # Extract output and tool calls
            output = result["output"]
            tool_calls = self._extract_tool_calls(result.get("intermediate_steps", []))

            # Save insight report
            report = await self._save_insight_report(output, tool_calls)

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
        return await self.posts_repo.get_posts_since(cutoff)

    def _format_posts_context(self, posts: List[Dict[str, Any]]) -> str:
        """Format posts information for agent context."""
        if not posts:
            return "No recent posts found."

        context = f"Total Posts: {len(posts)}\n\n"

        for i, post in enumerate(posts[:20], 1):  # Limit to 20 for context size
            platform = post.get("platform", "unknown")
            post_id = post.get("external_id", post.get("id", "unknown"))
            text = post.get("text", "[No text]")[:100]
            posted_at = post.get("posted_at", "Unknown")

            context += f"{i}. Platform: {platform}\n"
            context += f"   Post ID: {post_id}\n"
            context += f"   Posted: {posted_at}\n"
            context += f"   Text: {text}...\n\n"

        if len(posts) > 20:
            context += f"... and {len(posts) - 20} more posts\n"

        return context

    def _extract_tool_calls(self, intermediate_steps: List) -> List[Dict[str, Any]]:
        """Extract tool calls from agent execution for logging."""
        tool_calls = []

        for action, observation in intermediate_steps:
            tool_calls.append({
                "tool": action.tool,
                "input": str(action.tool_input)[:200],  # Truncate long inputs
                "timestamp": datetime.utcnow().isoformat()
            })

        return tool_calls

    async def _save_insight_report(
        self,
        agent_output: str,
        tool_calls: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Parse agent output and save insight report."""
        # Use LLM to extract structured insights
        structured_data = await self._extract_structured_insights(agent_output)

        # Save to database
        insight_report = InsightReport(
            summary=structured_data.get("summary", agent_output[:200]),
            findings=structured_data.get("findings", agent_output),
            tool_calls=tool_calls,
            created_by=settings.default_model_name
        )

        # Save to database (note: create is synchronous, not async)
        created_report = self.insights_repo.create(insight_report)

        logger.info("Insight report saved", report_id=str(created_report.id))

        return created_report.model_dump(mode="json")

    async def _extract_structured_insights(self, agent_output: str) -> Dict[str, Any]:
        """Use LLM to extract structured insights from agent output."""
        extraction_prompt = f"""Extract structured insights from the following engagement analysis.

Analysis:
{agent_output}

Provide a JSON response with:
{{
  "summary": "High-level takeaway in 1-2 sentences",
  "findings": "Detailed analysis with specific metrics, patterns, and recommendations (2-4 paragraphs)",
  "key_recommendations": ["rec 1", "rec 2", "rec 3"]
}}

Ensure:
- Summary is concise and actionable
- Findings include specific examples and data points
- Recommendations are concrete and implementable
"""

        extraction_llm = ChatOpenAI(
            model="gpt-4o-mini",
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
                "summary": agent_output[:200],
                "findings": agent_output
            }

    async def _create_empty_report(self) -> Dict[str, Any]:
        """Create a report when no posts are available."""
        insight_report = InsightReport(
            summary="No posts available for analysis in the specified time period.",
            findings="Unable to generate insights as no posts have been published recently. "
                    "Run content creation and publishing workflows first.",
            tool_calls=[],
            created_by=settings.default_model_name
        )

        # Save to database (note: create is synchronous, not async)
        created_report = self.insights_repo.create(insight_report)

        return created_report.model_dump(mode="json")


async def run_insights_analysis(days: int = 14) -> Dict[str, Any]:
    """
    CLI entry point for insights analysis.

    Args:
        days: Number of days to analyze

    Returns:
        Created insight report
    """
    agent = InsightsAgent()
    return await agent.analyze_engagement(days)
