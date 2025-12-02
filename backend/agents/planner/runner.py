# backend/agents/planner/runner.py

"""Planner agent runner with retry logic."""

from typing import Dict, Any
from backend.agents.planner.planner_agent import PlannerAgent
from backend.agents.planner.validator import validate_plan
from backend.database.repositories.content_creation_tasks import ContentCreationTaskRepository
from backend.models.tasks import ContentCreationTask
from backend.utils import get_logger

logger = get_logger(__name__)


class PlannerRunner:
    """
    Runner for the planner agent with validation and retry logic.

    Attempts to create a valid plan, retrying if validation fails.
    On success, converts the plan into content creation tasks.
    """

    def __init__(self, business_asset_id: str, max_retries: int = 3):
        self.business_asset_id = business_asset_id
        self.max_retries = max_retries
        self.agent = PlannerAgent(business_asset_id)
        self.tasks_repo = ContentCreationTaskRepository()

    async def run(self) -> Dict[str, Any]:
        """
        Run the planner agent with retries.

        Returns:
            Dictionary with plan and created tasks info
        """
        logger.info("Starting planner runner", max_retries=self.max_retries)

        for attempt in range(1, self.max_retries + 1):
            logger.info(f"Planner attempt {attempt}/{self.max_retries}")

            try:
                # Create plan
                plan = await self.agent.create_weekly_plan()

                # Validate plan
                is_valid, errors = validate_plan(plan)

                if is_valid:
                    logger.info("Plan validation successful", attempt=attempt)

                    # Convert to content creation tasks
                    tasks = await self._create_content_creation_tasks(plan)

                    return {
                        "success": True,
                        "attempt": attempt,
                        "plan": plan,
                        "tasks_created": len(tasks),
                        "task_ids": [str(t["id"]) for t in tasks]
                    }
                else:
                    logger.warning(
                        f"Plan validation failed (attempt {attempt})",
                        errors=errors
                    )

                    if attempt < self.max_retries:
                        logger.info("Retrying plan creation...")
                    else:
                        logger.error("Max retries reached, plan creation failed")
                        return {
                            "success": False,
                            "attempt": attempt,
                            "errors": errors,
                            "plan": plan
                        }

            except Exception as e:
                logger.error(f"Error in planner attempt {attempt}", error=str(e))

                if attempt >= self.max_retries:
                    raise

        return {
            "success": False,
            "attempt": self.max_retries,
            "errors": ["Max retries reached without producing valid plan"]
        }

    async def _create_content_creation_tasks(self, plan: Dict[str, Any]) -> list:
        """
        Convert plan allocations into content creation tasks.

        Uses unified format (image_posts, video_posts, text_only_posts).

        Args:
            plan: Validated plan dictionary

        Returns:
            List of created task records
        """
        logger.info("Converting plan to content creation tasks")

        allocations = plan.get("allocations", [])
        tasks = []

        for allocation in allocations:
            try:
                # Map seed_id to the correct foreign key column based on seed_type
                seed_type = allocation["seed_type"]
                seed_id = allocation["seed_id"]

                seed_kwargs = {}
                if seed_type == "news_event":
                    seed_kwargs["news_event_seed_id"] = seed_id
                elif seed_type == "trend":
                    seed_kwargs["trend_seed_id"] = seed_id
                elif seed_type == "ungrounded":
                    seed_kwargs["ungrounded_seed_id"] = seed_id

                # Create ContentCreationTask model instance with unified format
                task = ContentCreationTask(
                    business_asset_id=self.business_asset_id,
                    **seed_kwargs,
                    # Unified format allocations
                    image_posts=allocation.get("image_posts", 0),
                    video_posts=allocation.get("video_posts", 0),
                    text_only_posts=allocation.get("text_only_posts", 0),
                    # Media budgets
                    image_budget=allocation.get("image_budget", 0),
                    video_budget=allocation.get("video_budget", 0),
                    # Scheduled times from planner
                    scheduled_times=allocation.get("scheduled_times", []),
                    status="pending"
                )

                # Create in database - returns the created task
                created_task = await self.tasks_repo.create(task)

                tasks.append(created_task.model_dump(mode="json"))

                logger.info(
                    "Content task created",
                    task_id=str(created_task.id),
                    seed_id=allocation["seed_id"],
                    image_posts=allocation.get("image_posts", 0),
                    video_posts=allocation.get("video_posts", 0),
                    text_only_posts=allocation.get("text_only_posts", 0)
                )

            except Exception as e:
                logger.error(
                    "Error creating content task",
                    error=str(e),
                    seed_id=allocation.get("seed_id")
                )

        logger.info("Content tasks created", count=len(tasks))
        return tasks


async def run_planner(business_asset_id: str, max_retries: int = 3) -> Dict[str, Any]:
    """
    CLI entry point for running the planner.

    Args:
        business_asset_id: Business asset ID for multi-tenancy
        max_retries: Maximum number of attempts

    Returns:
        Dictionary with results
    """
    runner = PlannerRunner(business_asset_id, max_retries)
    return await runner.run()
