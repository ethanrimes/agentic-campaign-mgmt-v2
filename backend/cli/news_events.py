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
@click.option("--topic", required=True, help="Topic to search for")
@click.option("--count", default=5, help="Number of events to retrieve")
def ingest_perplexity(topic: str, count: int):
    """Ingest news events via Perplexity Sonar"""
    import asyncio
    from backend.agents.news_event import run_perplexity_ingestion

    logger.info("Ingesting news events via Perplexity", topic=topic)
    click.echo(f"🔍 Searching for news about: {topic}")

    result = asyncio.run(run_perplexity_ingestion(topic, count))

    click.echo(f"✅ Ingested {len(result)} news events successfully")
    click.echo("Run 'deduplicate' command to consolidate events")


@news_events.command()
@click.option("--query", required=True, help="Research query")
@click.option("--count", default=5, help="Number of events to extract")
def ingest_deep_research(query: str, count: int):
    """Ingest news events via ChatGPT Deep Research"""
    import asyncio
    from backend.agents.news_event import run_deep_research

    logger.info("Running deep research", query=query)
    click.echo(f"🔬 Deep research on: {query}")

    result = asyncio.run(run_deep_research(query, count))

    click.echo(f"✅ Deep research completed - ingested {len(result)} events")
    click.echo("Run 'deduplicate' command to consolidate events")


@news_events.command()
def deduplicate():
    """Run deduplication on ingested events"""
    import asyncio
    from backend.agents.news_event import run_deduplication

    logger.info("Running event deduplication")
    click.echo("🔄 Deduplicating ingested events...")

    stats = asyncio.run(run_deduplication())

    click.echo(f"✅ Deduplication complete")
    click.echo(f"   Processed: {stats['processed']}")
    click.echo(f"   Merged: {stats['merged']}")
    click.echo(f"   New: {stats['new']}")


@news_events.command()
@click.option("--limit", default=10, help="Number of events to display")
def list(limit: int):
    """List recent news event seeds"""
    from backend.database.repositories import NewsEventSeedRepository

    repo = NewsEventSeedRepository()
    seeds = repo.get_recent(limit=limit)

    click.echo(f"\n📰 Recent News Event Seeds ({len(seeds)}):\n")
    for seed in seeds:
        click.echo(f"  • {seed.name}")
        click.echo(f"    Location: {seed.location}")
        click.echo(f"    Created: {seed.created_at}")
        click.echo()
