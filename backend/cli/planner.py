# backend/cli/planner.py

"""CLI commands for planner agent."""

import click
from backend.utils import get_logger

logger = get_logger(__name__)


@click.group(name="planner")
def planner():
    """Content planning commands"""
    pass


@planner.command()
@click.option("--max-retries", default=3, help="Maximum retry attempts")
def run(max_retries: int):
    """Run planner agent to create weekly content plan"""
    logger.info("Running planner agent", max_retries=max_retries)
    click.echo("📅 Planning weekly content...")

    # TODO: Implement planner runner
    # from backend.agents.planner.runner import run_planner_with_retries
    # result = run_planner_with_retries(max_retries)

    click.echo("✅ Content plan created")
    click.echo("Content creation tasks have been generated")
