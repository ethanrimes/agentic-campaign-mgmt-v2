# backend/cli/trends.py

"""CLI commands for trend seed agent."""

import click
from backend.utils import get_logger

logger = get_logger(__name__)


@click.group(name="trends")
def trends():
    """Trend seed discovery commands"""
    pass


@trends.command()
@click.option(
    '--business-asset-id',
    required=True,
    type=str,
    help='Business asset ID (e.g., penndailybuzz, eaglesnationfanhuddle)'
)
@click.option("--query", required=True, help="Search query or theme")
@click.option("--count", default=1, help="Number of trends to discover")
def discover(business_asset_id: str, query: str, count: int):
    """Discover trends from social media"""
    import asyncio
    from backend.agents.trend_seed import run_trend_discovery

    logger.info("Discovering trends", business_asset_id=business_asset_id, query=query, count=count)
    click.echo(f"🔎 Discovering trends for: {query}")

    result = asyncio.run(run_trend_discovery(business_asset_id, query, count))

    click.echo(f"✅ Trend discovery complete - discovered {len(result)} trends")


@trends.command()
@click.option(
    '--business-asset-id',
    required=True,
    type=str,
    help='Business asset ID (e.g., penndailybuzz, eaglesnationfanhuddle)'
)
@click.option("--limit", default=10, help="Number of trends to display")
def list(business_asset_id: str, limit: int):
    """List recent trend seeds"""
    from backend.database.repositories import TrendSeedsRepository

    repo = TrendSeedsRepository()
    seeds = repo.get_recent(business_asset_id, limit=limit)

    click.echo(f"\n📈 Recent Trend Seeds ({len(seeds)}):\n")
    for seed in seeds:
        click.echo(f"  • {seed.name}")
        click.echo(f"    {seed.description[:100]}...")
        click.echo(f"    Created: {seed.created_at}")
        click.echo()
