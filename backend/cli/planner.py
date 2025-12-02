# backend/cli/planner.py

"""CLI commands for planner agent.

Uses unified format (image_posts, video_posts, text_only_posts) where each
image/video post creates both an Instagram and Facebook post.
"""

import click
from backend.utils import get_logger

logger = get_logger(__name__)


@click.group(name="planner")
def planner():
    """Content planning commands"""
    pass


@planner.command()
@click.option(
    '--business-asset-id',
    required=True,
    type=str,
    help='Business asset ID (e.g., penndailybuzz, eaglesnationfanhuddle)'
)
@click.option("--max-retries", default=3, help="Maximum retry attempts")
@click.option(
    '--share-media/--no-share-media',
    default=None,
    help='Override share_media_across_platforms setting. --share-media reuses media across FB+IG, --no-share-media generates separate media.'
)
def run(business_asset_id: str, max_retries: int, share_media: bool | None):
    """Run planner agent to create weekly content plan using unified format"""
    import asyncio
    from backend.agents.planner import run_planner
    from backend.config.settings import settings

    # Determine effective share_media setting
    effective_share_media = share_media if share_media is not None else settings.share_media_across_platforms

    logger.info(
        "Running planner agent",
        business_asset_id=business_asset_id,
        max_retries=max_retries,
        share_media=effective_share_media
    )

    click.echo("📅 Planning weekly content (unified format)...")
    click.echo(f"   Media sharing: {'enabled' if effective_share_media else 'disabled'}")

    result = asyncio.run(run_planner(business_asset_id, max_retries))

    if result['success']:
        click.echo(f"✅ Content plan created (attempt {result['attempt']})")
        click.echo(f"   Tasks created: {result['tasks_created']}")
    else:
        click.echo(f"❌ Plan creation failed after {result['attempt']} attempts")
        click.echo(f"   Errors: {result.get('errors', [])}")
