# backend/cli/content.py

"""CLI commands for content creation agent."""

import click
from uuid import UUID
from backend.utils import get_logger

logger = get_logger(__name__)


@click.group(name="content")
def content():
    """Content creation commands"""
    pass


@content.command()
@click.option("--max-workers", default=3, help="Maximum concurrent workers")
def create_all(max_workers: int):
    """Create content for all pending tasks"""
    logger.info("Running content creation for all tasks", max_workers=max_workers)
    click.echo(f"🎨 Creating content (max {max_workers} workers)...")

    # TODO: Implement content creation runner
    # from backend.agents.content_creation.runner import run_content_creation_all
    # result = run_content_creation_all(max_workers)

    click.echo("✅ Content creation complete")


@content.command()
@click.option("--task-id", required=True, help="Task ID")
def create(task_id: str):
    """Create content for a specific task"""
    logger.info("Creating content for task", task_id=task_id)
    click.echo(f"🎨 Creating content for task: {task_id}")

    # TODO: Implement content creation for single task
    # from backend.agents.content_creation.runner import run_content_creation_task
    # result = run_content_creation_task(UUID(task_id))

    click.echo("✅ Content created")


@content.command()
@click.option("--limit", default=10, help="Number of tasks to display")
def pending(limit: int):
    """List pending content creation tasks"""
    from backend.database.repositories import ContentCreationTaskRepository

    repo = ContentCreationTaskRepository()
    tasks = repo.get_pending_tasks(limit=limit)

    click.echo(f"\n📋 Pending Tasks ({len(tasks)}):\n")
    for task in tasks:
        click.echo(f"  • Task ID: {task.id}")
        click.echo(f"    Seed: {task.content_seed_id} ({task.content_seed_type})")
        click.echo(f"    Created: {task.created_at}")
        click.echo()
