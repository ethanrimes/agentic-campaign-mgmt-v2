# backend/agents/planner/planner_agent.py

"""Weekly content planning agent."""

from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

from backend.config.settings import settings
from backend.config.prompts import get_global_system_prompt
from backend.config.guardrails_config import guardrails
from backend.tools import create_knowledge_base_tools
from backend.database.repositories.news_event_seeds import NewsEventSeedsRepository
from backend.database.repositories.trend_seeds import TrendSeedsRepository
from backend.database.repositories.ungrounded_seeds import UngroundedSeedsRepository
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
        self.news_repo = NewsEventSeedsRepository()
        self.trend_repo = TrendSeedsRepository()
        self.ungrounded_repo = UngroundedSeedsRepository()
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

            # Create agent prompt template
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", f"{self.global_prompt}\n\n{agent_prompt}"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])

            # Create agent
            agent = create_openai_functions_agent(
                llm=self.llm,
                tools=self.tools,
                prompt=prompt_template
            )

            agent_executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                verbose=True,
                max_iterations=10,
                return_intermediate_steps=True
            )

            # Build input with context
            input_text = self._format_input(context)

            # Run agent
            result = await agent_executor.ainvoke({"input": input_text})

            # Parse output into structured plan
            plan = await self._parse_plan(result["output"], context)

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

    async def _parse_plan(self, agent_output: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Parse agent output into structured plan."""
        # Use LLM to extract structured plan
        structured_plan = await self._extract_structured_plan(agent_output, context)

        return structured_plan

    async def _extract_structured_plan(
        self,
        agent_output: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Use LLM to extract structured plan from agent output."""
        extraction_prompt = f"""Extract a structured weekly content plan from the following planning output.

Planning Output:
{agent_output}

Week Start Date: {context['week_start']}

Provide a JSON response with this exact structure:
{{
  "allocations": [
    {{
      "seed_id": "uuid-here",
      "seed_type": "news_event" | "trend" | "ungrounded",
      "instagram_image_posts": 0,
      "instagram_reel_posts": 0,
      "facebook_feed_posts": 0,
      "facebook_video_posts": 0,
      "image_budget": 0,
      "video_budget": 0
    }}
  ],
  "reasoning": "Explanation of the planning strategy",
  "week_start_date": "{context['week_start']}"
}}

IMPORTANT:
- All counts must be non-negative integers
- seed_id must be a valid UUID from the provided context
- seed_type must be exactly one of: "news_event", "trend", "ungrounded"
- Extract ALL allocations mentioned in the output
"""

        extraction_llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=settings.openai_api_key,
            temperature=0.1  # Very low for consistent extraction
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
        except json.JSONDecodeError as e:
            logger.error("Failed to parse plan extraction", error=str(e))
            raise Exception(f"Failed to parse plan: {str(e)}")

    def _get_next_monday(self) -> datetime:
        """Get the date of the next Monday."""
        today = datetime.utcnow().date()
        days_ahead = 0 - today.weekday()  # Monday is 0
        if days_ahead <= 0:
            days_ahead += 7
        return datetime.combine(today + timedelta(days=days_ahead), datetime.min.time())
