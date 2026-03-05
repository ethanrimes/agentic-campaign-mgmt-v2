# backend/agents/planner/runner.py

"""Planner agent runner with retry logic."""

from typing import Dict, Any, List, Optional
from uuid import UUID
from backend.agents.planner.planner_agent import PlannerAgent
from backend.agents.planner.validator import validate_plan
from backend.database.repositories.content_creation_tasks import ContentCreationTaskRepository
from backend.database.repositories.news_event_seeds import NewsEventSeedRepository
from backend.database.repositories.trend_seeds import TrendSeedsRepository
from backend.database.repositories.ungrounded_seeds import UngroundedSeedRepository
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
        self.news_repo = NewsEventSeedRepository()
        self.trend_repo = TrendSeedsRepository()
        self.ungrounded_repo = UngroundedSeedRepository()

    async def run(self) -> Dict[str, Any]:
        """
        Run the planner agent with retries.

        Returns:
            Dictionary with plan and created tasks info
        """
        logger.info("Starting planner runner", max_retries=self.max_retries)

        feedback: Optional[str] = None

        for attempt in range(1, self.max_retries + 1):
            logger.info(f"Planner attempt {attempt}/{self.max_retries}")

            try:
                # Create plan (with optional feedback from previous failed attempt)
                plan = await self.agent.create_weekly_plan(feedback=feedback)

                # Validate plan structure against guardrails
                is_valid, errors = validate_plan(plan)

                if is_valid:
                    # Validate that all selected seed IDs actually exist in the DB
                    seed_errors = await self._validate_seed_ids(plan)

                    if seed_errors:
                        logger.warning(
                            f"Seed ID validation failed (attempt {attempt})",
                            errors=seed_errors
                        )
                        errors = seed_errors
                        is_valid = False

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
                        feedback = "Your previous plan was rejected for the following reasons:\n" + \
                                   "\n".join(f"- {e}" for e in errors) + \
                                   "\n\nPlease fix these issues and resubmit the plan."
                        logger.info("Retrying plan creation with feedback...")
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

    async def _validate_seed_ids(self, plan: Dict[str, Any]) -> List[str]:
        """
        Verify that all seed IDs in the plan actually exist in the database.

        Returns:
            List of error strings (empty if all seeds are valid)
        """
        errors = []
        repo_map = {
            "news_event": self.news_repo,
            "trend": self.trend_repo,
            "ungrounded": self.ungrounded_repo,
        }

        for allocation in plan.get("allocations", []):
            seed_id_str = allocation.get("seed_id")
            seed_type = allocation.get("seed_type")
            repo = repo_map.get(seed_type)

            if not repo or not seed_id_str:
                continue

            try:
                seed_uuid = UUID(str(seed_id_str))
                existing = await repo.get_by_id(self.business_asset_id, seed_uuid)
                if existing is None:
                    errors.append(
                        f"Seed ID {seed_id_str} (type: {seed_type}) does not exist. "
                        f"You must only use seed IDs from the list provided to you."
                    )
            except (ValueError, Exception) as e:
                errors.append(
                    f"Seed ID {seed_id_str} (type: {seed_type}) is invalid: {e}"
                )

        return errors

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
