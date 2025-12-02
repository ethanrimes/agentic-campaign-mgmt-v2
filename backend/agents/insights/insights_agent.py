# backend/agents/insights/insights_agent.py

"""
Engagement insights and learning agent.

Uses context-stuffing approach: all engagement data is gathered upfront
and provided to the LLM in a single prompt, eliminating tool calls.
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from backend.config.settings import settings
from backend.config.prompts import get_global_system_prompt
from backend.database.repositories.insights import InsightsRepository
from backend.services.insights_context_builder import (
    build_insights_context,
    format_context_for_agent,
)
from backend.models.insights import InsightReport
from backend.utils import get_logger

logger = get_logger(__name__)


class InsightReportOutput(BaseModel):
    """Structured engagement insight report."""
    summary: str = Field(..., description="High-level takeaway in 1-2 sentences")
    findings: str = Field(..., description="Detailed analysis with specific metrics, patterns, and recommendations (2-4 paragraphs in markdown)")
    key_recommendations: List[str] = Field(default_factory=list, description="Concrete, implementable recommendations")


class InsightsAgent:
    """
    Agent for analyzing engagement data and generating insights.

    Uses context-stuffing approach where all data is fetched upfront
    and provided to the LLM, eliminating the need for tool calls.
    """

    def __init__(self, business_asset_id: str):
        self.business_asset_id = business_asset_id
        self.insights_repo = InsightsRepository()

        # Load prompts
        prompt_path = Path(__file__).parent / "prompts" / "insights.txt"
        self.agent_prompt = prompt_path.read_text()
        self.global_prompt = get_global_system_prompt(self.business_asset_id)

        # Initialize LLM with structured output
        self.llm = ChatOpenAI(
            model=settings.default_model_name,
            api_key=settings.get_model_api_key(),
            temperature=0.3,  # Lower temperature for analytical work
        ).with_structured_output(InsightReportOutput)

    async def analyze_engagement(self, days: int = 14) -> Dict[str, Any]:
        """
        Analyze engagement data and generate insights.

        Args:
            days: Number of days to analyze (used for display, actual limits from settings)

        Returns:
            Created insight report
        """
        logger.info("Starting engagement analysis", days=days)

        try:
            # Step 1: Build context with all engagement data
            logger.info("Building insights context...")
            context = await build_insights_context(self.business_asset_id)

            # Check if we have any data to analyze
            if not context.facebook_posts and not context.instagram_posts:
                logger.warning("No published posts found to analyze")
                return await self._create_empty_report()

            # Step 2: Format context for the agent
            context_text = format_context_for_agent(context)

            # Step 3: Build the prompt
            system_message = f"{self.global_prompt}\n\n{self.agent_prompt}"

            user_message = f"""Analyze the engagement data below and generate a comprehensive insight report.

{context_text}

Based on this data, provide:
1. A high-level summary (1-2 sentences)
2. Detailed findings with specific metrics and patterns (formatted in markdown)
3. Key recommendations for improving engagement

Be specific and data-driven. Reference actual numbers from the posts. Identify patterns in what works and what doesn't."""

            # Step 4: Call the LLM
            logger.info("Calling LLM for analysis...")
            messages = [
                SystemMessage(content=system_message),
                HumanMessage(content=user_message)
            ]

            result: InsightReportOutput = await self.llm.ainvoke(messages)

            # Step 5: Save the report
            insight_report = InsightReport(
                business_asset_id=self.business_asset_id,
                summary=result.summary,
                findings=result.findings,
                tool_calls=[],  # No tool calls in context-stuffing approach
                created_by=settings.default_model_name
            )

            created_report = await self.insights_repo.create(insight_report)
            logger.info("Insight report saved", report_id=str(created_report.id))

            report = created_report.model_dump(mode="json")
            report["key_recommendations"] = result.key_recommendations

            logger.info("Engagement analysis complete", report_id=report["id"])
            return report

        except Exception as e:
            logger.error("Error in engagement analysis", error=str(e), exc_info=True)
            raise

    async def _create_empty_report(self) -> Dict[str, Any]:
        """Create a report when no posts are available."""
        insight_report = InsightReport(
            business_asset_id=self.business_asset_id,
            summary="No published posts available for analysis in the specified time period.",
            findings="Unable to generate insights as no posts have been published recently. "
                    "Run content creation and publishing workflows first to generate data for analysis.",
            tool_calls=[],
            created_by=settings.default_model_name
        )

        created_report = await self.insights_repo.create(insight_report)
        return created_report.model_dump(mode="json")


async def run_insights_analysis(business_asset_id: str, days: int = 14) -> Dict[str, Any]:
    """
    CLI entry point for insights analysis.

    Args:
        business_asset_id: Business asset ID for multi-tenancy
        days: Number of days to analyze (display only, actual limits from settings)

    Returns:
        Created insight report
    """
    agent = InsightsAgent(business_asset_id)
    return await agent.analyze_engagement(days)
