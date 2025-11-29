# backend/agents/content_creation/runner.py

"""Content creation runner for processing tasks."""

from typing import Dict, Any, List, Optional
from uuid import UUID
from backend.agents.content_creation.content_agent import ContentCreationAgent
from backend.database.repositories.content_creation_tasks import ContentCreationTaskRepository
from backend.utils import get_logger

logger = get_logger(__name__)


class ContentCreationRunner:
    """
    Runner for content creation tasks.

    Can process all pending tasks or a specific task by ID.
    Automatically verifies posts after creation.
    """

    def __init__(self, business_asset_id: str, auto_verify: bool = True):
        """
        Initialize runner.

        Args:
            business_asset_id: Business asset ID for multi-tenancy
            auto_verify: Whether to automatically verify posts after creation (default True)
        """
        self.business_asset_id = business_asset_id
        self.agent = ContentCreationAgent(business_asset_id)
        self.tasks_repo = ContentCreationTaskRepository()
        self.auto_verify = auto_verify
        self._verifier = None

    async def _get_verifier(self):
        """Lazily initialize verifier agent."""
        if self._verifier is None:
            from backend.agents.verifier import VerifierAgent
            self._verifier = VerifierAgent(self.business_asset_id)
        return self._verifier

    async def _verify_posts(self, post_ids: List[str]) -> Dict[str, Any]:
        """
        Verify created posts.

        Args:
            post_ids: List of post IDs to verify

        Returns:
            Verification summary
        """
        if not self.auto_verify or not post_ids:
            return {"verified": 0, "approved": 0, "rejected": 0}

        verifier = await self._get_verifier()
        approved = 0
        rejected = 0

        for post_id in post_ids:
            try:
                result = await verifier.verify_post(UUID(post_id))
                if result.is_approved:
                    approved += 1
                else:
                    rejected += 1
            except Exception as e:
                logger.error("Error verifying post", post_id=post_id, error=str(e))

        return {
            "verified": len(post_ids),
            "approved": approved,
            "rejected": rejected
        }

    async def run_all(self) -> Dict[str, Any]:
        """
        Process all pending content creation tasks.

        Returns:
            Summary of results
        """
        logger.info("Starting content creation for all pending tasks")

        try:
            # Get all pending tasks
            pending_tasks = await self.tasks_repo.get_pending_tasks(self.business_asset_id)

            if not pending_tasks:
                logger.info("No pending tasks found")
                return {
                    "success": True,
                    "tasks_processed": 0,
                    "posts_created": 0,
                    "tasks": [],
                    "verification": {"verified": 0, "approved": 0, "rejected": 0}
                }

            logger.info(f"Found {len(pending_tasks)} pending tasks")

            results = []
            total_posts = 0
            all_post_ids = []

            for task in pending_tasks:
                task_id = str(task.id)

                try:
                    logger.info(f"Processing task {task_id}")

                    # Create content for task
                    posts = await self.agent.create_content_for_task(task_id)

                    post_ids = [str(p.id) if hasattr(p, 'id') else p["id"] for p in posts]
                    all_post_ids.extend(post_ids)

                    results.append({
                        "task_id": task_id,
                        "success": True,
                        "posts_created": len(posts),
                        "post_ids": post_ids
                    })

                    total_posts += len(posts)

                    logger.info(
                        f"Task {task_id} completed",
                        posts_created=len(posts)
                    )

                except Exception as e:
                    logger.error(
                        f"Error processing task {task_id}",
                        error=str(e)
                    )
                    results.append({
                        "task_id": task_id,
                        "success": False,
                        "error": str(e)
                    })

            # Verify all created posts
            verification_results = await self._verify_posts(all_post_ids)

            logger.info(
                "Content creation complete",
                tasks_processed=len(results),
                total_posts=total_posts,
                verified=verification_results["verified"],
                approved=verification_results["approved"],
                rejected=verification_results["rejected"]
            )

            return {
                "success": True,
                "tasks_processed": len(results),
                "posts_created": total_posts,
                "tasks": results,
                "verification": verification_results
            }

        except Exception as e:
            logger.error("Error in content creation runner", error=str(e))
            raise

    async def run_single(self, task_id: str) -> Dict[str, Any]:
        """
        Process a specific content creation task.

        Args:
            task_id: ID of the task to process

        Returns:
            Task results
        """
        logger.info("Starting content creation for specific task", task_id=task_id)

        try:
            # Verify task exists and is pending
            task = await self.tasks_repo.get_by_id(self.business_asset_id, task_id)

            if not task:
                raise Exception(f"Task {task_id} not found")

            if task.status == "completed":
                logger.warning(f"Task {task_id} is already completed")
                return {
                    "success": False,
                    "error": "Task is already completed",
                    "task_id": task_id
                }

            # Create content
            posts = await self.agent.create_content_for_task(task_id)

            post_ids = [str(p.id) if hasattr(p, 'id') else p["id"] for p in posts]

            # Verify created posts
            verification_results = await self._verify_posts(post_ids)

            logger.info(
                "Task completed successfully",
                task_id=task_id,
                posts_created=len(posts),
                verified=verification_results["verified"],
                approved=verification_results["approved"],
                rejected=verification_results["rejected"]
            )

            return {
                "success": True,
                "task_id": task_id,
                "posts_created": len(posts),
                "post_ids": post_ids,
                "posts": posts,
                "verification": verification_results
            }

        except Exception as e:
            logger.error(
                "Error processing task",
                task_id=task_id,
                error=str(e)
            )
            return {
                "success": False,
                "task_id": task_id,
                "error": str(e)
            }


async def run_content_creation_all(business_asset_id: str) -> Dict[str, Any]:
    """
    CLI entry point for processing all pending tasks.

    Args:
        business_asset_id: Business asset ID for multi-tenancy

    Returns:
        Summary of results
    """
    runner = ContentCreationRunner(business_asset_id)
    return await runner.run_all()


async def run_content_creation_single(business_asset_id: str, task_id: str) -> Dict[str, Any]:
    """
    CLI entry point for processing a specific task.

    Args:
        business_asset_id: Business asset ID for multi-tenancy
        task_id: ID of the task to process

    Returns:
        Task results
    """
    runner = ContentCreationRunner(business_asset_id)
    return await runner.run_single(task_id)
