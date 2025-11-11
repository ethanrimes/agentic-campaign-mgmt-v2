# backend/agents/planner/planner_agent.py

"""Weekly content planning agent."""

from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from backend.config.settings import settings
from backend.config.prompts import get_global_system_prompt
from backend.config.guardrails_config import guardrails
from backend.tools import create_knowledge_base_tools
from backend.database.repositories.news_event_seeds import NewsEventSeedRepository
from backend.database.repositories.trend_seeds import TrendSeedsRepository
from backend.database.repositories.ungrounded_seeds import UngroundedSeedRepository
from backend.database.repositories.insights import InsightsRepository
from backend.models.planner import PlannerOutput
from backend.utils import get_logger

logger = get_logger(__name__)


class PlannerAgent:
    """
    Agent for creating weekly content plans.

    Selects content seeds and allocates posts/media according to guardrails.
    """

    def __init__(self):
        self.news_repo = NewsEventSeedRepository()
        self.trend_repo = TrendSeedsRepository()
        self.ungrounded_repo = UngroundedSeedRepository()
        self.insights_repo = InsightsRepository()

        # Load prompts
        prompt_path = Path(__file__).parent / "prompts" / "planner.txt"
        self.agent_prompt_template = prompt_path.read_text()
        self.global_prompt = get_global_system_prompt()

        # Initialize LLM
        self.llm = ChatOpenAI(
            model=settings.default_model_name,
            api_key=settings.get_model_api_key(),
            temperature=0.5,  # Moderate temperature for strategic planning
        )

        # Create tools
        self.tools = create_knowledge_base_tools()

    async def create_weekly_plan(self) -> Dict[str, Any]:
        """
        Create a weekly content plan.

        Returns:
            Planner output with allocations
        """
        logger.info("Starting weekly planning")

        try:
            # Gather context
            context = await self._gather_planning_context()

            # Fill in guardrails in prompt
            agent_prompt = self._format_prompt_with_guardrails()

            # Create agent
            agent_executor = create_agent(
                model=self.llm,
                tools=self.tools,
                system_prompt=f"{self.global_prompt}\n\n{agent_prompt}",
                response_format=ToolStrategy(PlannerOutput)
            )

            # Build input with context
            input_text = self._format_input(context)

            # Run agent
            config = {"verbose": True, "max_iterations": 10}
            result = await agent_executor.ainvoke(
                {"messages": [("human", input_text)]},
                config=config
            )

            # The agent's structured response is here
            structured_output: PlannerOutput = result.get("structured_response")

            if not structured_output:
                logger.warning("Agent did not return a structured response")
                raise Exception("Agent did not return structured plan")

            # Convert to dict for return
            plan = structured_output.model_dump(mode="json")

            logger.info("Weekly plan created successfully")
            return plan

        except Exception as e:
            logger.error("Error creating weekly plan", error=str(e))
            raise

    async def _gather_planning_context(self) -> Dict[str, Any]:
        """Gather all context needed for planning."""
        logger.info("Gathering planning context")

        # Get available content seeds
        news_seeds = await self.news_repo.get_all()
        trend_seeds = await self.trend_repo.get_all()
        ungrounded_seeds = await self.ungrounded_repo.get_all()

        # Get latest insights
        latest_insights = await self.insights_repo.get_latest()

        context = {
            "news_seeds": news_seeds[:20],  # Limit for context size
            "trend_seeds": trend_seeds[:20],
            "ungrounded_seeds": ungrounded_seeds[:20],
            "insights": latest_insights,
            "week_start": self._get_next_monday().isoformat()
        }

        logger.info(
            "Context gathered",
            news_count=len(news_seeds),
            trend_count=len(trend_seeds),
            ungrounded_count=len(ungrounded_seeds)
        )

        return context

    def _format_prompt_with_guardrails(self) -> str:
        """Fill in guardrail values in prompt template."""
        return self.agent_prompt_template.format(
            min_posts_per_week=guardrails.min_posts_per_week,
            max_posts_per_week=guardrails.max_posts_per_week,
            min_content_seeds_per_week=guardrails.min_content_seeds_per_week,
            max_content_seeds_per_week=guardrails.max_content_seeds_per_week,
            min_videos_per_week=guardrails.min_videos_per_week,
            max_videos_per_week=guardrails.max_videos_per_week,
            min_images_per_week=guardrails.min_images_per_week,
            max_images_per_week=guardrails.max_images_per_week
        )

    def _format_input(self, context: Dict[str, Any]) -> str:
        """Format input text with context for the agent."""
        input_text = f"""Create a weekly content plan for the week starting {context['week_start']}.

Available Content Seeds:

** News Events ({len(context['news_seeds'])} available) **
"""
        for i, seed in enumerate(context['news_seeds'][:10], 1):
            input_text += f"{i}. {seed.get('name', 'Unnamed')} (ID: {seed.get('id')})\n"
            input_text += f"   {seed.get('description', '')[:150]}...\n\n"

        input_text += f"\n** Trends ({len(context['trend_seeds'])} available) **\n"
        for i, seed in enumerate(context['trend_seeds'][:10], 1):
            input_text += f"{i}. {seed.get('name', 'Unnamed')} (ID: {seed.get('id')})\n"
            input_text += f"   {seed.get('description', '')[:150]}...\n\n"

        input_text += f"\n** Creative Ideas ({len(context['ungrounded_seeds'])} available) **\n"
        for i, seed in enumerate(context['ungrounded_seeds'][:10], 1):
            input_text += f"{i}. {seed.get('idea', 'Unnamed')} (ID: {seed.get('id')})\n"
            input_text += f"   Format: {seed.get('format', 'unknown')}\n\n"

        # Add insights
        if context.get('insights'):
            insights = context['insights']
            input_text += f"\n** Latest Insights **\n"
            input_text += f"Summary: {insights.get('summary', 'No summary')}\n"
            input_text += f"Findings: {insights.get('findings', '')[:300]}...\n\n"

        input_text += """
Based on this context, create a strategic weekly content plan.

Your plan must include:
1. Selected content seeds (with IDs)
2. Post allocations for each seed (Instagram + Facebook)
3. Media budgets (images and videos)
4. Reasoning for your choices

Remember to STRICTLY follow the guardrails!
"""

        return input_text

    def _get_next_monday(self) -> datetime:
        """Get the date of the next Monday."""
        today = datetime.utcnow().date()
        days_ahead = 0 - today.weekday()  # Monday is 0
        if days_ahead <= 0:
            days_ahead += 7
        return datetime.combine(today + timedelta(days=days_ahead), datetime.min.time())