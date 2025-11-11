# backend/agents/content_creation/runner.py

"""Content creation runner for processing tasks."""

from typing import Dict, Any, List, Optional
from backend.agents.content_creation.content_agent import ContentCreationAgent
from backend.database.repositories.content_creation_tasks import ContentCreationTaskRepository
from backend.utils import get_logger

logger = get_logger(__name__)


class ContentCreationRunner:
    """
    Runner for content creation tasks.

    Can process all pending tasks or a specific task by ID.
    """

    def __init__(self):
        self.agent = ContentCreationAgent()
        self.tasks_repo = ContentCreationTaskRepository()

    async def run_all(self) -> Dict[str, Any]:
        """
        Process all pending content creation tasks.

        Returns:
            Summary of results
        """
        logger.info("Starting content creation for all pending tasks")

        try:
            # Get all pending tasks
            pending_tasks = await self.tasks_repo.get_pending_tasks()

            if not pending_tasks:
                logger.info("No pending tasks found")
                return {
                    "success": True,
                    "tasks_processed": 0,
                    "posts_created": 0,
                    "tasks": []
                }

            logger.info(f"Found {len(pending_tasks)} pending tasks")

            results = []
            total_posts = 0

            for task in pending_tasks:
                task_id = task["id"]

                try:
                    logger.info(f"Processing task {task_id}")

                    # Create content for task
                    posts = await self.agent.create_content_for_task(task_id)

                    results.append({
                        "task_id": task_id,
                        "success": True,
                        "posts_created": len(posts),
                        "post_ids": [p["id"] for p in posts]
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

            logger.info(
                "Content creation complete",
                tasks_processed=len(results),
                total_posts=total_posts
            )

            return {
                "success": True,
                "tasks_processed": len(results),
                "posts_created": total_posts,
                "tasks": results
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
            task = await self.tasks_repo.get_by_id(task_id)

            if not task:
                raise Exception(f"Task {task_id} not found")

            if task.get("status") == "completed":
                logger.warning(f"Task {task_id} is already completed")
                return {
                    "success": False,
                    "error": "Task is already completed",
                    "task_id": task_id
                }

            # Create content
            posts = await self.agent.create_content_for_task(task_id)

            logger.info(
                "Task completed successfully",
                task_id=task_id,
                posts_created=len(posts)
            )

            return {
                "success": True,
                "task_id": task_id,
                "posts_created": len(posts),
                "post_ids": [p["id"] for p in posts],
                "posts": posts
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


async def run_content_creation_all() -> Dict[str, Any]:
    """
    CLI entry point for processing all pending tasks.

    Returns:
        Summary of results
    """
    runner = ContentCreationRunner()
    return await runner.run_all()


async def run_content_creation_single(task_id: str) -> Dict[str, Any]:
    """
    CLI entry point for processing a specific task.

    Args:
        task_id: ID of the task to process

    Returns:
        Task results
    """
    runner = ContentCreationRunner()
    return await runner.run_single(task_id)
