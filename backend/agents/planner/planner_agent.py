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
from backend.config.guardrails_config import guardrails_config
from backend.database.repositories.news_event_seeds import NewsEventSeedRepository
from backend.database.repositories.trend_seeds import TrendSeedsRepository
from backend.database.repositories.ungrounded_seeds import UngroundedSeedRepository
from backend.database.repositories.insights import InsightsRepository
from backend.database.repositories.completed_posts import CompletedPostRepository
from backend.models.planner import PlannerOutput
from backend.utils import get_logger

logger = get_logger(__name__)


class PlannerAgent:
    """
    Agent for creating weekly content plans.

    Selects content seeds and allocates posts/media according to guardrails.
    """

    def __init__(self, business_asset_id: str):
        self.business_asset_id = business_asset_id
        self.news_repo = NewsEventSeedRepository()
        self.trend_repo = TrendSeedsRepository()
        self.ungrounded_repo = UngroundedSeedRepository()
        self.insights_repo = InsightsRepository()
        self.posts_repo = CompletedPostRepository()

        # Load prompts
        prompt_path = Path(__file__).parent / "prompts" / "planner.txt"
        self.agent_prompt_template = prompt_path.read_text()
        self.global_prompt = get_global_system_prompt(self.business_asset_id)

        # Initialize LLM
        self.llm = ChatOpenAI(
            model=settings.default_model_name,
            api_key=settings.get_model_api_key(),
            temperature=0.5,  # Moderate temperature for strategic planning
        )

        # Create tools - empty list as context is provided in the prompt
        self.tools = []

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

        # Get most recent content seeds using configurable limits
        news_seeds = await self.news_repo.get_recent(
            self.business_asset_id,
            limit=settings.planner_news_seeds_limit
        )
        trend_seeds = await self.trend_repo.get_recent(
            self.business_asset_id,
            limit=settings.planner_trend_seeds_limit
        )
        ungrounded_seeds = await self.ungrounded_repo.get_recent(
            self.business_asset_id,
            limit=settings.planner_ungrounded_seeds_limit
        )

        # Get recent insights (configurable limit, handles fewer available gracefully)
        recent_insights = await self.insights_repo.get_recent(
            self.business_asset_id,
            limit=settings.planner_insights_limit
        )

        # Get scheduled pending posts to understand current schedule and covered content
        scheduled_posts = await self.posts_repo.get_scheduled_pending_posts(
            self.business_asset_id,
            limit=50
        )

        context = {
            "news_seeds": news_seeds,
            "trend_seeds": trend_seeds,
            "ungrounded_seeds": ungrounded_seeds,
            "insights": recent_insights,  # Now a list of reports
            "scheduled_posts": scheduled_posts,  # Pending posts in the pipeline
            "week_start": self._get_next_monday().isoformat()
        }

        logger.info(
            "Context gathered",
            news_count=len(news_seeds),
            trend_count=len(trend_seeds),
            ungrounded_count=len(ungrounded_seeds),
            scheduled_posts_count=len(scheduled_posts)
        )

        return context

    def _format_prompt_with_guardrails(self) -> str:
        """Fill in guardrail values in prompt template."""
        return self.agent_prompt_template.format(
            min_posts_per_week=guardrails_config.min_posts_per_week,
            max_posts_per_week=guardrails_config.max_posts_per_week,
            min_content_seeds_per_week=guardrails_config.min_content_seeds_per_week,
            max_content_seeds_per_week=guardrails_config.max_content_seeds_per_week,
            min_videos_per_week=guardrails_config.min_videos_per_week,
            max_videos_per_week=guardrails_config.max_videos_per_week,
            min_images_per_week=guardrails_config.min_images_per_week,
            max_images_per_week=guardrails_config.max_images_per_week
        )

    def _format_input(self, context: Dict[str, Any]) -> str:
        """Format input text with context for the agent."""
        input_text = f"""Create a weekly content plan for the week starting {context['week_start']}.

Available Content Seeds:

** News Events ({len(context['news_seeds'])} available) **
"""
        for i, seed in enumerate(context['news_seeds'][:10], 1):
            input_text += f"{i}. {getattr(seed, 'name', 'Unnamed')} (ID: {seed.id})\n"
            description = getattr(seed, 'description', '')
            input_text += f"   {description[:150] if description else 'No description'}...\n\n"

        input_text += f"\n** Trends ({len(context['trend_seeds'])} available) **\n"
        for i, seed in enumerate(context['trend_seeds'][:10], 1):
            input_text += f"{i}. {getattr(seed, 'name', 'Unnamed')} (ID: {seed.id})\n"
            description = getattr(seed, 'description', '')
            input_text += f"   {description[:150] if description else 'No description'}...\n\n"

        input_text += f"\n** Creative Ideas ({len(context['ungrounded_seeds'])} available) **\n"
        for i, seed in enumerate(context['ungrounded_seeds'][:10], 1):
            input_text += f"{i}. {getattr(seed, 'idea', 'Unnamed')} (ID: {seed.id})\n"
            input_text += f"   Format: {getattr(seed, 'format', 'unknown')}\n\n"

        # Add insights (now supports multiple reports)
        insights_list = context.get('insights', [])
        if insights_list:
            input_text += f"\n** Recent Insights ({len(insights_list)} report{'s' if len(insights_list) != 1 else ''}) **\n"
            for i, insights in enumerate(insights_list, 1):
                created_at = getattr(insights, 'created_at', 'Unknown date')
                input_text += f"\n--- Report {i} (from {created_at}) ---\n"
                input_text += f"Summary: {getattr(insights, 'summary', 'No summary')}\n"
                findings = getattr(insights, 'findings', '')
                input_text += f"Findings: {findings[:300] if findings else 'No findings'}...\n"
        else:
            input_text += f"\n** Recent Insights **\nNo insights reports available yet.\n"

        # Add scheduled posts (verified pending posts in the pipeline)
        scheduled_posts = context.get('scheduled_posts', [])
        if scheduled_posts:
            input_text += f"\n** Scheduled Posts ({len(scheduled_posts)} pending verified posts) **\n"
            input_text += "These posts are already verified and waiting to be published. Consider:\n"
            input_text += "1. Schedule gaps - avoid overlapping times\n"
            input_text += "2. Content already covered - avoid duplicate topics\n\n"
            for i, post in enumerate(scheduled_posts[:20], 1):
                platform = getattr(post, 'platform', 'unknown')
                post_type = getattr(post, 'post_type', 'unknown')
                scheduled_time = getattr(post, 'scheduled_posting_time', None)
                text_preview = getattr(post, 'text', '')[:100]
                input_text += f"{i}. [{platform.upper()}] {post_type}\n"
                input_text += f"   Scheduled: {scheduled_time or 'Immediate'}\n"
                input_text += f"   Content: {text_preview}...\n\n"
        else:
            input_text += f"\n** Scheduled Posts **\nNo pending verified posts in the pipeline.\n"

        input_text += f"""
Based on this context, create a strategic weekly content plan using UNIFIED FORMAT allocation.

REMINDER - UNIFIED FORMAT:
- image_posts: Each creates 1 IG image + 1 FB feed post (2 posts total)
- video_posts: Each creates 1 IG reel + 1 FB video post (2 posts total)
- text_only_posts: Creates only 1 FB feed post (must be in SEPARATE allocations)

Your plan must include:
1. Selected content seeds (with IDs)
2. Unified format allocations (image_posts, video_posts, text_only_posts)
3. Media budgets (image_budget, video_budget)
4. Scheduled posting times for each post unit
5. Reasoning for your choices

⚠️ CRITICAL REMINDER - YOUR PLAN MUST STAY WITHIN THESE LIMITS:
- Maximum {guardrails_config.max_posts_per_week} total posts (counting BOTH platforms)
- Maximum {guardrails_config.max_images_per_week} image_posts (each creates 2 platform posts)
- Maximum {guardrails_config.max_videos_per_week} video_posts (each creates 2 platform posts)
- Between {guardrails_config.min_content_seeds_per_week} and {guardrails_config.max_content_seeds_per_week} content seeds

Before you finalize your plan:
1. Count total posts: (image_posts × 2) + (video_posts × 2) + text_only_posts
2. Count total image_posts across ALL seeds
3. Count total video_posts across ALL seeds
4. Verify you have not exceeded ANY maximum limit
5. Ensure scheduled_times matches post unit count for each allocation

DO NOT submit a plan that exceeds these limits - it will be automatically rejected!
"""

        return input_text

    def _get_next_monday(self) -> datetime:
        """Get the date of the next Monday."""
        today = datetime.utcnow().date()
        days_ahead = 0 - today.weekday()  # Monday is 0
        if days_ahead <= 0:
            days_ahead += 7
        return datetime.combine(today + timedelta(days=days_ahead), datetime.min.time())