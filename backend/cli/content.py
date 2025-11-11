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
def create_all():
    """Create content for all pending tasks"""
    import asyncio
    from backend.agents.content_creation import run_content_creation_all

    logger.info("Running content creation for all tasks")
    click.echo(f"🎨 Creating content for all pending tasks...")

    result = asyncio.run(run_content_creation_all())

    click.echo(f"✅ Content creation complete")
    click.echo(f"   Tasks processed: {result['tasks_processed']}")
    click.echo(f"   Posts created: {result['posts_created']}")


@content.command()
@click.option("--task-id", required=True, help="Task ID")
def create(task_id: str):
    """Create content for a specific task"""
    import asyncio
    from backend.agents.content_creation import run_content_creation_single

    logger.info("Creating content for task", task_id=task_id)
    click.echo(f"🎨 Creating content for task: {task_id}")

    result = asyncio.run(run_content_creation_single(task_id))

    if result['success']:
        click.echo(f"✅ Content created - {result['posts_created']} posts")
    else:
        click.echo(f"❌ Failed: {result.get('error')}")


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
