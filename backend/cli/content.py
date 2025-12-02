# backend/cli/content.py

"""CLI commands for content creation agent.

Uses unified format where each image/video post creates both an Instagram
and Facebook post, optionally sharing the same media across platforms.
"""

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
@click.option(
    '--skip-verify',
    is_flag=True,
    default=False,
    help='Skip automatic verification of created posts'
)
@click.option(
    '--share-media/--no-share-media',
    default=None,
    help='Override share_media_across_platforms setting. --share-media reuses media across FB+IG, --no-share-media generates separate media.'
)
def create_all(business_asset_id: str, skip_verify: bool, share_media: bool | None):
    """Create content for all pending tasks using unified format"""
    import asyncio
    from backend.agents.content_creation.runner import ContentCreationRunner
    from backend.config.settings import settings

    # Determine effective share_media setting
    effective_share_media = share_media if share_media is not None else settings.share_media_across_platforms

    logger.info(
        "Running content creation for all tasks",
        business_asset_id=business_asset_id,
        share_media=effective_share_media
    )
    click.echo(f"🎨 Creating content for all pending tasks (unified format)...")
    click.echo(f"   Media sharing: {'enabled' if effective_share_media else 'disabled'}")

    async def _run():
        runner = ContentCreationRunner(
            business_asset_id,
            auto_verify=not skip_verify,
            share_media=share_media
        )
        return await runner.run_all()

    result = asyncio.run(_run())

    click.echo(f"✅ Content creation complete")
    click.echo(f"   Tasks processed: {result['tasks_processed']}")
    click.echo(f"   Posts created: {result['posts_created']}")

    if 'verification' in result and result['verification']['verified'] > 0:
        v = result['verification']
        click.echo(f"\n🔍 Verification Results:")
        click.echo(f"   Verified: {v['verified']}")
        click.echo(f"   Approved: {v['approved']}")
        click.echo(f"   Rejected: {v['rejected']}")


@content.command()
@click.option(
    '--business-asset-id',
    required=True,
    type=str,
    help='Business asset ID (e.g., penndailybuzz, eaglesnationfanhuddle)'
)
@click.option("--task-id", required=True, help="Task ID")
@click.option(
    '--skip-verify',
    is_flag=True,
    default=False,
    help='Skip automatic verification of created posts'
)
@click.option(
    '--share-media/--no-share-media',
    default=None,
    help='Override share_media_across_platforms setting. --share-media reuses media across FB+IG, --no-share-media generates separate media.'
)
def create(business_asset_id: str, task_id: str, skip_verify: bool, share_media: bool | None):
    """Create content for a specific task using unified format"""
    import asyncio
    from backend.agents.content_creation.runner import ContentCreationRunner
    from backend.config.settings import settings

    # Determine effective share_media setting
    effective_share_media = share_media if share_media is not None else settings.share_media_across_platforms

    logger.info(
        "Creating content for task",
        business_asset_id=business_asset_id,
        task_id=task_id,
        share_media=effective_share_media
    )
    click.echo(f"🎨 Creating content for task: {task_id} (unified format)")
    click.echo(f"   Media sharing: {'enabled' if effective_share_media else 'disabled'}")

    async def _run():
        runner = ContentCreationRunner(
            business_asset_id,
            auto_verify=not skip_verify,
            share_media=share_media
        )
        return await runner.run_single(task_id)

    result = asyncio.run(_run())

    if result['success']:
        click.echo(f"✅ Content created - {result['posts_created']} posts")

        if 'verification' in result and result['verification']['verified'] > 0:
            v = result['verification']
            click.echo(f"\n🔍 Verification Results:")
            click.echo(f"   Verified: {v['verified']}")
            click.echo(f"   Approved: {v['approved']}")
            click.echo(f"   Rejected: {v['rejected']}")
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
