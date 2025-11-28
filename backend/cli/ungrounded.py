# backend/cli/ungrounded.py

"""CLI commands for ungrounded seed agent."""

import click
from backend.utils import get_logger

logger = get_logger(__name__)


@click.group(name="ungrounded")
def ungrounded():
    """Ungrounded (creative) seed generation commands"""
    pass


@ungrounded.command()
@click.option(
    '--business-asset-id',
    required=True,
    type=str,
    help='Business asset ID (e.g., penndailybuzz, eaglesnationfanhuddle)'
)
@click.option("--count", default=5, help="Number of ideas to generate")
def generate(business_asset_id: str, count: int):
    """Generate creative content ideas"""
    import asyncio
    from backend.agents.ungrounded_seed import run_ungrounded_generation

    logger.info("Generating ungrounded seeds", business_asset_id=business_asset_id, count=count)
    click.echo(f"💡 Generating {count} creative content ideas...")

    result = asyncio.run(run_ungrounded_generation(business_asset_id, count))

    click.echo(f"✅ Generated {len(result)} creative ideas")


@ungrounded.command()
@click.option(
    '--business-asset-id',
    required=True,
    type=str,
    help='Business asset ID (e.g., penndailybuzz, eaglesnationfanhuddle)'
)
@click.option("--limit", default=10, help="Number of seeds to display")
def list(business_asset_id: str, limit: int):
    """List recent ungrounded seeds"""
    from backend.database.repositories import UngroundedSeedRepository

    repo = UngroundedSeedRepository()
    seeds = repo.get_recent(business_asset_id, limit=limit)

    click.echo(f"\n💭 Recent Ungrounded Seeds ({len(seeds)}):\n")
    for seed in seeds:
        click.echo(f"  • {seed.idea}")
        click.echo(f"    Format: {seed.format}")
        click.echo(f"    Created: {seed.created_at}")
        click.echo()
