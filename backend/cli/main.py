# backend/cli/main.py

"""
Main CLI entry point for the social media agent framework.

Usage:
    python -m backend.cli.main <command> <subcommand> [options]

Example:
    python -m backend.cli.main news-events ingest-perplexity --topic "Philadelphia"
    python -m backend.cli.main planner run --max-retries 3
    python -m backend.cli.main content create-all
    python -m backend.cli.main publish facebook
"""

import click
from backend.utils import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)


@click.group()
def cli():
    """Social Media Agent Framework CLI"""
    pass


# Import subcommand groups
from .news_events import news_events
from .trends import trends
from .ungrounded import ungrounded
from .insights import insights
from .planner import planner
from .content import content
from .publish import publish
from .comments import comments
from .verifier import verifier

# Register subcommands
cli.add_command(news_events)
cli.add_command(trends)
cli.add_command(ungrounded)
cli.add_command(insights)
cli.add_command(planner)
cli.add_command(content)
cli.add_command(publish)
cli.add_command(comments)
cli.add_command(verifier)


if __name__ == "__main__":
    cli()
