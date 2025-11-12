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

    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.agent = PlannerAgent()
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
                # Create ContentCreationTask model instance
                task = ContentCreationTask(
                    content_seed_id=allocation["seed_id"],
                    content_seed_type=allocation["seed_type"],
                    instagram_image_posts=allocation["instagram_image_posts"],
                    instagram_reel_posts=allocation["instagram_reel_posts"],
                    facebook_feed_posts=allocation["facebook_feed_posts"],
                    facebook_video_posts=allocation["facebook_video_posts"],
                    image_budget=allocation["image_budget"],
                    video_budget=allocation["video_budget"],
                    status="pending"
                    # Note: week_start_date not included as column doesn't exist in DB yet
                )

                # Create in database - returns the created task
                created_task = await self.tasks_repo.create(task)

                tasks.append(created_task.model_dump(mode="json"))

                logger.info(
                    "Content task created",
                    task_id=str(created_task.id),
                    seed_id=allocation["seed_id"]
                )

            except Exception as e:
                logger.error(
                    "Error creating content task",
                    error=str(e),
                    seed_id=allocation.get("seed_id")
                )

        logger.info("Content tasks created", count=len(tasks))
        return tasks


async def run_planner(max_retries: int = 3) -> Dict[str, Any]:
    """
    CLI entry point for running the planner.

    Args:
        max_retries: Maximum number of attempts

    Returns:
        Dictionary with results
    """
    runner = PlannerRunner(max_retries)
    return await runner.run()
