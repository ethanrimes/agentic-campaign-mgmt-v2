#!/usr/bin/env python3
# scripts/full_pipeline.py

"""
Script to run the full content pipeline for a business asset:
1. Research: News events (Perplexity), trends, ungrounded ideas
2. Insights: Fetch metrics + AI analysis
3. Planner: Create content plan from seeds
4. Content: Generate content for all pending tasks

Usage:
    python scripts/full_pipeline.py --business-asset-id flyeaglesflycommunity --skip-research --skip-insights
    python scripts/full_pipeline.py --business-asset-id oceankindnesscollective  --skip-research --skip-insights
    python scripts/full_pipeline.py --business-asset-id airesearchinsightslab  --skip-research --skip-insights


    python scripts/full_pipeline.py --business-asset-id penndailybuzz --skip-research
    python scripts/full_pipeline.py --business-asset-id penndailybuzz --skip-insights
    python scripts/full_pipeline.py --business-asset-id penndailybuzz --news-count 5 --trends-count 3
"""

import subprocess
import sys
from typing import Optional

import click


def run_command(description: str, command: list[str], continue_on_error: bool = False) -> bool:
    """
    Run a CLI command and display output.

    Args:
        description: Human-readable description of the command
        command: Command and arguments as list
        continue_on_error: If True, don't exit on failure

    Returns:
        True if command succeeded, False otherwise
    """
    click.echo(f"\n{'='*60}")
    click.echo(f"🚀 {description}")
    click.echo(f"{'='*60}")
    click.echo(f"$ {' '.join(command)}\n")

    result = subprocess.run(command, cwd=str(__file__).rsplit("/scripts", 1)[0])

    if result.returncode != 0:
        click.echo(f"\n❌ Failed: {description}")
        if not continue_on_error:
            sys.exit(result.returncode)
        return False

    click.echo(f"\n✅ Completed: {description}")
    return True


@click.command()
@click.option(
    "--business-asset-id",
    required=True,
    type=str,
    help="Business asset ID (e.g., penndailybuzz)"
)
@click.option(
    "--skip-research",
    is_flag=True,
    help="Skip research phase (news events, trends, ungrounded)"
)
@click.option(
    "--skip-insights",
    is_flag=True,
    help="Skip insights fetch and analysis"
)
@click.option(
    "--skip-planner",
    is_flag=True,
    help="Skip planner (content plan creation)"
)
@click.option(
    "--skip-content",
    is_flag=True,
    help="Skip content creation"
)
@click.option(
    "--skip-verify",
    is_flag=True,
    help="Skip verification during content creation"
)
@click.option(
    "--news-count",
    default=5,
    type=int,
    help="Number of news events to ingest (default: 5)"
)
@click.option(
    "--trends-count",
    default=3,
    type=int,
    help="Number of trends to discover (default: 3)"
)
@click.option(
    "--ungrounded-count",
    default=3,
    type=int,
    help="Number of ungrounded ideas to generate (default: 3)"
)
@click.option(
    "--insights-days",
    default=14,
    type=int,
    help="Number of days for insights analysis (default: 14)"
)
@click.option(
    "--share-media/--no-share-media",
    default=None,
    help="Share media between Instagram and Facebook (uses default if not specified)"
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be run without executing"
)
def main(
    business_asset_id: str,
    skip_research: bool,
    skip_insights: bool,
    skip_planner: bool,
    skip_content: bool,
    skip_verify: bool,
    news_count: int,
    trends_count: int,
    ungrounded_count: int,
    insights_days: int,
    share_media: Optional[bool],
    dry_run: bool
):
    """
    Run the full content pipeline for a business asset.

    Pipeline stages:
    1. RESEARCH: Ingest news events, discover trends, generate creative ideas
    2. INSIGHTS: Fetch metrics from Meta APIs and run AI analysis
    3. PLANNER: Create content plan from available seeds
    4. CONTENT: Generate content for all pending tasks

    Examples:

        # Run full pipeline
        python scripts/full_pipeline.py --business-asset-id penndailybuzz

        # Skip research (use existing seeds)
        python scripts/full_pipeline.py --business-asset-id penndailybuzz --skip-research

        # Custom counts
        python scripts/full_pipeline.py --business-asset-id penndailybuzz --news-count 10 --trends-count 5

        # Dry run to see commands
        python scripts/full_pipeline.py --business-asset-id penndailybuzz --dry-run
    """
    click.echo("\n" + "="*60)
    click.echo("📱 FULL CONTENT PIPELINE")
    click.echo("="*60)
    click.echo(f"\nBusiness Asset: {business_asset_id}")
    click.echo(f"Skip Research: {skip_research}")
    click.echo(f"Skip Insights: {skip_insights}")
    click.echo(f"Skip Planner: {skip_planner}")
    click.echo(f"Skip Content: {skip_content}")

    if dry_run:
        click.echo("\n🔍 DRY RUN MODE - Commands will be shown but not executed\n")

    base_cmd = ["python", "-m", "backend.cli.main"]

    # Build media sharing args
    media_args = []
    if share_media is True:
        media_args = ["--share-media"]
    elif share_media is False:
        media_args = ["--no-share-media"]

    # =========================================================================
    # PHASE 1: RESEARCH
    # =========================================================================
    if not skip_research:
        click.echo("\n" + "="*60)
        click.echo("📚 PHASE 1: RESEARCH")
        click.echo("="*60)

        # News events via Perplexity
        news_cmd = base_cmd + [
            "news-events", "ingest-perplexity",
            "--business-asset-id", business_asset_id,
            "--count", str(news_count)
        ]
        if dry_run:
            click.echo(f"Would run: {' '.join(news_cmd)}")
        else:
            run_command(
                f"Ingesting {news_count} news events via Perplexity",
                news_cmd,
                continue_on_error=True
            )

        # Deduplicate news events
        dedup_cmd = base_cmd + [
            "news-events", "deduplicate",
            "--business-asset-id", business_asset_id
        ]
        if dry_run:
            click.echo(f"Would run: {' '.join(dedup_cmd)}")
        else:
            run_command(
                "Deduplicating news events",
                dedup_cmd,
                continue_on_error=True
            )

        # Discover trends
        trends_cmd = base_cmd + [
            "trends", "discover",
            "--business-asset-id", business_asset_id,
            "--count", str(trends_count)
        ]
        if dry_run:
            click.echo(f"Would run: {' '.join(trends_cmd)}")
        else:
            run_command(
                f"Discovering {trends_count} trends",
                trends_cmd,
                continue_on_error=True
            )

        # Generate ungrounded ideas
        ungrounded_cmd = base_cmd + [
            "ungrounded", "generate",
            "--business-asset-id", business_asset_id,
            "--count", str(ungrounded_count)
        ]
        if dry_run:
            click.echo(f"Would run: {' '.join(ungrounded_cmd)}")
        else:
            run_command(
                f"Generating {ungrounded_count} creative ideas",
                ungrounded_cmd,
                continue_on_error=True
            )
    else:
        click.echo("\n⏭️  Skipping research phase")

    # =========================================================================
    # PHASE 2: INSIGHTS
    # =========================================================================
    if not skip_insights:
        click.echo("\n" + "="*60)
        click.echo("📊 PHASE 2: INSIGHTS")
        click.echo("="*60)

        # Fetch all insights from Meta APIs
        fetch_cmd = base_cmd + [
            "insights", "fetch-all",
            "--business-asset-id", business_asset_id
        ]
        if dry_run:
            click.echo(f"Would run: {' '.join(fetch_cmd)}")
        else:
            run_command(
                "Fetching insights from Meta APIs",
                fetch_cmd,
                continue_on_error=True
            )

        # Run AI analysis
        analyze_cmd = base_cmd + [
            "insights", "analyze",
            "--business-asset-id", business_asset_id,
            "--days", str(insights_days)
        ]
        if dry_run:
            click.echo(f"Would run: {' '.join(analyze_cmd)}")
        else:
            run_command(
                f"Running AI insights analysis ({insights_days} days)",
                analyze_cmd,
                continue_on_error=True
            )
    else:
        click.echo("\n⏭️  Skipping insights phase")

    # =========================================================================
    # PHASE 3: PLANNER
    # =========================================================================
    if not skip_planner:
        click.echo("\n" + "="*60)
        click.echo("📋 PHASE 3: PLANNER")
        click.echo("="*60)

        planner_cmd = base_cmd + [
            "planner", "run",
            "--business-asset-id", business_asset_id,
            "--max-retries", "3"
        ] + media_args

        if dry_run:
            click.echo(f"Would run: {' '.join(planner_cmd)}")
        else:
            run_command(
                "Creating content plan",
                planner_cmd
            )
    else:
        click.echo("\n⏭️  Skipping planner phase")

    # =========================================================================
    # PHASE 4: CONTENT CREATION
    # =========================================================================
    if not skip_content:
        click.echo("\n" + "="*60)
        click.echo("🎨 PHASE 4: CONTENT CREATION")
        click.echo("="*60)

        content_cmd = base_cmd + [
            "content", "create-all",
            "--business-asset-id", business_asset_id
        ] + media_args

        if skip_verify:
            content_cmd.append("--skip-verify")

        if dry_run:
            click.echo(f"Would run: {' '.join(content_cmd)}")
        else:
            run_command(
                "Creating content for all pending tasks",
                content_cmd
            )
    else:
        click.echo("\n⏭️  Skipping content creation phase")

    # =========================================================================
    # SUMMARY
    # =========================================================================
    click.echo("\n" + "="*60)
    click.echo("✅ PIPELINE COMPLETE")
    click.echo("="*60)

    if dry_run:
        click.echo("\n🔍 Dry run complete - no commands were executed")
    else:
        click.echo(f"\nBusiness Asset: {business_asset_id}")
        click.echo("\nNext steps:")
        click.echo(f"  1. Review pending posts: python -m backend.cli.main content pending --business-asset-id {business_asset_id}")
        click.echo(f"  2. Check verification: python -m backend.cli.main verifier stats --business-asset-id {business_asset_id}")
        click.echo(f"  3. Publish when ready: python -m backend.cli.main publish all --business-asset-id {business_asset_id}")


if __name__ == "__main__":
    main()
