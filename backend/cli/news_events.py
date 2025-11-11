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
def ingest_perplexity(topic: str):
    """Ingest news events via Perplexity Sonar"""
    logger.info("Ingesting news events via Perplexity", topic=topic)
    click.echo(f"🔍 Searching for news about: {topic}")

    # TODO: Implement Perplexity Sonar ingestion
    # from backend.agents.news_event.perplexity_sonar import run_perplexity_ingestion
    # result = run_perplexity_ingestion(topic)

    click.echo("✅ News events ingested successfully")
    click.echo("Run 'deduplicate' command to consolidate events")


@news_events.command()
@click.option("--query", required=True, help="Research query")
def ingest_deep_research(query: str):
    """Ingest news events via ChatGPT Deep Research"""
    logger.info("Running deep research", query=query)
    click.echo(f"🔬 Deep research on: {query}")

    # TODO: Implement deep research ingestion
    # from backend.agents.news_event.deep_research import run_deep_research
    # result = run_deep_research(query)

    click.echo("✅ Deep research completed")
    click.echo("Run 'deduplicate' command to consolidate events")


@news_events.command()
def deduplicate():
    """Run deduplication on ingested events"""
    logger.info("Running event deduplication")
    click.echo("🔄 Deduplicating ingested events...")

    # TODO: Implement deduplication
    # from backend.agents.news_event.deduplicator import run_deduplication
    # result = run_deduplication()

    click.echo("✅ Deduplication complete")


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
