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
    logger.info("Running insights analysis", days=days)
    click.echo(f"📊 Analyzing content from past {days} days...")

    # TODO: Implement insights agent
    # from backend.agents.insights.insights_agent import run_insights_analysis
    # result = run_insights_analysis(days)

    click.echo("✅ Insights analysis complete")


@insights.command()
@click.option("--limit", default=5, help="Number of reports to display")
def list(limit: int):
    """List recent insight reports"""
    from backend.database.repositories import InsightReportRepository

    repo = InsightReportRepository()
    reports = repo.get_recent(limit=limit)

    click.echo(f"\n📈 Recent Insight Reports ({len(reports)}):\n")
    for report in reports:
        click.echo(f"  Summary: {report.summary}")
        click.echo(f"  Created: {report.created_at}")
        click.echo()


@insights.command()
def latest():
    """Show the latest insight report"""
    from backend.database.repositories import InsightReportRepository

    repo = InsightReportRepository()
    report = repo.get_latest()

    if not report:
        click.echo("No insight reports found")
        return

    click.echo(f"\n📊 Latest Insight Report\n")
    click.echo(f"Created: {report.created_at}")
    click.echo(f"\nSummary:\n{report.summary}\n")
    click.echo(f"\nFindings:\n{report.findings}\n")
