# backend/cli/insights.py

"""CLI commands for insights agent."""

import click
from backend.utils import get_logger

logger = get_logger(__name__)


@click.group(name="insights")
def insights():
    """Insights agent commands"""
    pass


@insights.command()
@click.option("--days", default=14, help="Number of days to analyze")
def analyze(days: int):
    """Run insights analysis on recent content"""
    import asyncio
    from backend.agents.insights import run_insights_analysis

    logger.info("Running insights analysis", days=days)
    click.echo(f"📊 Analyzing content from past {days} days...")

    result = asyncio.run(run_insights_analysis(days))

    click.echo(f"✅ Insights analysis complete (Report ID: {result['id']})")
    click.echo(f"\nSummary: {result['summary']}")


@insights.command()
@click.option("--limit", default=5, help="Number of reports to display")
def list(limit: int):
    """List recent insight reports"""
    import asyncio
    from backend.database.repositories import InsightsRepository

    async def _list_reports():
        repo = InsightsRepository()
        return await repo.get_recent(limit=limit)

    reports = asyncio.run(_list_reports())

    click.echo(f"\n📈 Recent Insight Reports ({len(reports)}):\n")
    for report in reports:
        click.echo(f"  Summary: {report.summary}")
        click.echo(f"  Created: {report.created_at}")
        click.echo()


@insights.command()
def latest():
    """Show the latest insight report"""
    import asyncio
    from backend.database.repositories import InsightsRepository

    async def _get_latest():
        repo = InsightsRepository()
        return await repo.get_latest()

    report = asyncio.run(_get_latest())

    if not report:
        click.echo("No insight reports found")
        return

    click.echo(f"\n📊 Latest Insight Report\n")
    click.echo(f"Created: {report.created_at}")
    click.echo(f"\nSummary:\n{report.summary}\n")
    click.echo(f"\nFindings:\n{report.findings}\n")
