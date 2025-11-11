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
@click.option("--keyword", required=True, help="Keyword to search")
@click.option("--platform", type=click.Choice(["instagram", "facebook", "both"]), default="both")
def discover(keyword: str, platform: str):
    """Discover trends from social media"""
    logger.info("Discovering trends", keyword=keyword, platform=platform)
    click.echo(f"🔎 Discovering trends for: {keyword}")
    click.echo(f"📱 Platform: {platform}")

    # TODO: Implement trend discovery
    # from backend.agents.trend_seed.trend_searcher import run_trend_discovery
    # result = run_trend_discovery(keyword, platform)

    click.echo("✅ Trend discovery complete")


@trends.command()
@click.option("--limit", default=10, help="Number of trends to display")
def list(limit: int):
    """List recent trend seeds"""
    from backend.database.repositories import TrendSeedRepository

    repo = TrendSeedRepository()
    seeds = repo.get_recent(limit=limit)

    click.echo(f"\n📈 Recent Trend Seeds ({len(seeds)}):\n")
    for seed in seeds:
        click.echo(f"  • {seed.name}")
        click.echo(f"    {seed.description[:100]}...")
        click.echo(f"    Created: {seed.created_at}")
        click.echo()
