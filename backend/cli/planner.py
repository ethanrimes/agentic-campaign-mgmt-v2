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
    import asyncio
    from backend.agents.planner import run_planner

    logger.info("Running planner agent", max_retries=max_retries)
    click.echo("📅 Planning weekly content...")

    result = asyncio.run(run_planner(max_retries))

    if result['success']:
        click.echo(f"✅ Content plan created (attempt {result['attempt']})")
        click.echo(f"   Tasks created: {result['tasks_created']}")
    else:
        click.echo(f"❌ Plan creation failed after {result['attempt']} attempts")
        click.echo(f"   Errors: {result.get('errors', [])}")
