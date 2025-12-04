# backend/cli/news_events.py

"""CLI commands for news event seed agents."""

import click
from backend.utils import get_logger

logger = get_logger(__name__)


@click.group(name="news-events")
def news_events():
    """News event seed management commands"""
    pass


@news_events.command()
@click.option(
    '--business-asset-id',
    required=True,
    type=str,
    help='Business asset ID (e.g., penndailybuzz, eaglesnationfanhuddle)'
)
@click.option("--topic", default=None, help="Topic to search for (optional - uses target audience if not provided)")
@click.option("--count", default=5, help="Number of events to retrieve")
def ingest_perplexity(business_asset_id: str, topic: str, count: int):
    """Ingest news events via Perplexity Sonar"""
    import asyncio
    from backend.agents.news_event import run_perplexity_ingestion

    logger.info("Ingesting news events via Perplexity", business_asset_id=business_asset_id, topic=topic)
    if topic:
        click.echo(f"🔍 Searching for news about: {topic}")
    else:
        click.echo(f"🔍 Searching for news relevant to target audience...")

    result = asyncio.run(run_perplexity_ingestion(business_asset_id, topic, count))

    click.echo(f"✅ Ingested {len(result)} news events successfully")
    click.echo("Run 'deduplicate' command to consolidate events")


@news_events.command()
@click.option(
    '--business-asset-id',
    required=True,
    type=str,
    help='Business asset ID (e.g., penndailybuzz, eaglesnationfanhuddle)'
)
@click.option("--query", default=None, help="Research query (optional - uses target audience if not provided)")
@click.option("--count", default=5, help="Number of events to extract")
def ingest_deep_research(business_asset_id: str, query: str, count: int):
    """Ingest news events via ChatGPT Deep Research"""
    import asyncio
    from backend.agents.news_event import run_deep_research

    logger.info("Running deep research", business_asset_id=business_asset_id, query=query)
    if query:
        click.echo(f"🔬 Deep research on: {query}")
    else:
        click.echo(f"🔬 Deep research on content relevant to target audience...")

    result = asyncio.run(run_deep_research(business_asset_id, query, count))

    click.echo(f"✅ Deep research completed - ingested {len(result)} events")
    click.echo("Run 'deduplicate' command to consolidate events")


@news_events.command()
@click.option(
    '--business-asset-id',
    required=True,
    type=str,
    help='Business asset ID (e.g., penndailybuzz, eaglesnationfanhuddle)'
)
def deduplicate(business_asset_id: str):
    """Run deduplication on ingested events"""
    import asyncio
    from backend.agents.news_event import run_deduplication

    logger.info("Running event deduplication", business_asset_id=business_asset_id)
    click.echo("🔄 Deduplicating ingested events...")

    stats = asyncio.run(run_deduplication(business_asset_id))

    click.echo(f"✅ Deduplication complete")
    click.echo(f"   Processed: {stats['processed']}")
    click.echo(f"   Merged: {stats['merged']}")
    click.echo(f"   New: {stats['new']}")


@news_events.command()
@click.option(
    '--business-asset-id',
    required=True,
    type=str,
    help='Business asset ID (e.g., penndailybuzz, eaglesnationfanhuddle)'
)
@click.option("--limit", default=10, help="Number of events to display")
def list(business_asset_id: str, limit: int):
    """List recent news event seeds"""
    import asyncio
    from backend.database.repositories import NewsEventSeedRepository

    async def _list():
        repo = NewsEventSeedRepository()
        return await repo.get_recent(business_asset_id, limit=limit)

    seeds = asyncio.run(_list())

    click.echo(f"\n📰 Recent News Event Seeds ({len(seeds)}):\n")
    for seed in seeds:
        click.echo(f"  • {seed.name}")
        click.echo(f"    Location: {seed.location}")
        click.echo(f"    Created: {seed.created_at}")
        click.echo()
