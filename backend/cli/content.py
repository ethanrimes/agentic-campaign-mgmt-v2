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
@click.option(
    '--business-asset-id',
    required=True,
    type=str,
    help='Business asset ID (e.g., penndailybuzz, eaglesnationfanhuddle)'
)
def create_all(business_asset_id: str):
    """Create content for all pending tasks"""
    import asyncio
    from backend.agents.content_creation import run_content_creation_all

    logger.info("Running content creation for all tasks", business_asset_id=business_asset_id)
    click.echo(f"🎨 Creating content for all pending tasks...")

    result = asyncio.run(run_content_creation_all(business_asset_id))

    click.echo(f"✅ Content creation complete")
    click.echo(f"   Tasks processed: {result['tasks_processed']}")
    click.echo(f"   Posts created: {result['posts_created']}")


@content.command()
@click.option(
    '--business-asset-id',
    required=True,
    type=str,
    help='Business asset ID (e.g., penndailybuzz, eaglesnationfanhuddle)'
)
@click.option("--task-id", required=True, help="Task ID")
def create(business_asset_id: str, task_id: str):
    """Create content for a specific task"""
    import asyncio
    from backend.agents.content_creation import run_content_creation_single

    logger.info("Creating content for task", business_asset_id=business_asset_id, task_id=task_id)
    click.echo(f"🎨 Creating content for task: {task_id}")

    result = asyncio.run(run_content_creation_single(business_asset_id, task_id))

    if result['success']:
        click.echo(f"✅ Content created - {result['posts_created']} posts")
    else:
        click.echo(f"❌ Failed: {result.get('error')}")


@content.command()
@click.option(
    '--business-asset-id',
    required=True,
    type=str,
    help='Business asset ID (e.g., penndailybuzz, eaglesnationfanhuddle)'
)
@click.option("--limit", default=10, help="Number of tasks to display")
def pending(business_asset_id: str, limit: int):
    """List pending content creation tasks"""
    from backend.database.repositories import ContentCreationTaskRepository

    repo = ContentCreationTaskRepository()
    tasks = repo.get_pending_tasks(business_asset_id, limit=limit)

    click.echo(f"\n📋 Pending Tasks ({len(tasks)}):\n")
    for task in tasks:
        click.echo(f"  • Task ID: {task.id}")
        click.echo(f"    Seed: {task.content_seed_id} ({task.content_seed_type})")
        click.echo(f"    Created: {task.created_at}")
        click.echo()
