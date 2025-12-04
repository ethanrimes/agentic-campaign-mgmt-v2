#!/usr/bin/env python3
# scripts/move_schedule.py

"""
Script to move up the scheduled posting date of verified pending posts.

Usage:
    python scripts/move_schedule.py --days 2 --all
    python scripts/move_schedule.py --days 3 --business-asset-id penndailybuzz
    python scripts/move_schedule.py --days 1 --all --dry-run
"""

import asyncio
import sys
from datetime import timedelta
from typing import List, Optional

import click

# Add the parent directory to the path so we can import backend
sys.path.insert(0, str(__file__).rsplit("/scripts", 1)[0])

from backend.utils import setup_logging, get_logger
from backend.database.repositories.completed_posts import CompletedPostRepository
from backend.database.repositories.business_assets import BusinessAssetRepository
from backend.models import CompletedPost

setup_logging()
logger = get_logger(__name__)


def get_all_business_asset_ids() -> List[str]:
    """Get all active business asset IDs."""
    repo = BusinessAssetRepository()
    assets = repo.get_all_active()
    return [asset.id for asset in assets]


async def move_schedule_for_business_asset(
    business_asset_id: str,
    days: int,
    dry_run: bool
) -> dict:
    """
    Move up the scheduled posting time for verified pending posts.

    Args:
        business_asset_id: Business asset ID
        days: Number of days to move up (subtract from scheduled time)
        dry_run: If True, don't actually update

    Returns:
        Summary of results
    """
    repo = CompletedPostRepository()

    results = {
        "business_asset_id": business_asset_id,
        "updated": 0,
        "skipped_no_schedule": 0,
        "errors": 0,
    }

    # Get all pending verified posts
    posts = await repo.get_scheduled_pending_posts(business_asset_id, limit=500)

    for post in posts:
        if not post.scheduled_posting_time:
            results["skipped_no_schedule"] += 1
            continue

        old_time = post.scheduled_posting_time
        new_time = old_time - timedelta(days=days)

        if dry_run:
            click.echo(
                f"  [DRY RUN] {post.id} ({post.platform}): "
                f"{old_time.strftime('%Y-%m-%d %H:%M')} -> {new_time.strftime('%Y-%m-%d %H:%M')}"
            )
            results["updated"] += 1
        else:
            try:
                await repo.update_scheduled_time(business_asset_id, post.id, new_time)
                logger.info(
                    "Updated scheduled time",
                    post_id=str(post.id),
                    old_time=old_time.isoformat(),
                    new_time=new_time.isoformat(),
                )
                results["updated"] += 1
            except Exception as e:
                logger.error(
                    "Failed to update scheduled time",
                    post_id=str(post.id),
                    error=str(e),
                )
                results["errors"] += 1

    return results


@click.command()
@click.option(
    "--days",
    type=int,
    required=True,
    help="Number of days to move up the scheduled posting time (positive = earlier)"
)
@click.option(
    "--all", "update_all",
    is_flag=True,
    help="Update scheduled times for all active business assets"
)
@click.option(
    "--business-asset-id",
    type=str,
    help="Business asset ID to update (e.g., penndailybuzz)"
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be updated without actually updating"
)
def main(
    days: int,
    update_all: bool,
    business_asset_id: Optional[str],
    dry_run: bool
):
    """
    Move up the scheduled posting date of verified pending posts.

    This script subtracts the specified number of days from the scheduled_posting_time
    of all verified pending posts.

    Examples:

        # Move all posts 2 days earlier for all business assets
        python scripts/move_schedule.py --days 2 --all

        # Move posts 3 days earlier for a specific business asset
        python scripts/move_schedule.py --days 3 --business-asset-id penndailybuzz

        # Preview changes without applying them
        python scripts/move_schedule.py --days 1 --all --dry-run
    """
    if not update_all and not business_asset_id:
        click.echo("Error: Either --all or --business-asset-id must be specified", err=True)
        sys.exit(1)

    if update_all and business_asset_id:
        click.echo("Error: Cannot specify both --all and --business-asset-id", err=True)
        sys.exit(1)

    if days <= 0:
        click.echo("Error: --days must be a positive number", err=True)
        sys.exit(1)

    async def _update():
        # Get business asset IDs to process
        if update_all:
            asset_ids = get_all_business_asset_ids()
            if not asset_ids:
                click.echo("No active business assets found")
                return
            click.echo(f"Processing {len(asset_ids)} business assets")
        else:
            asset_ids = [business_asset_id]
            click.echo(f"Processing business asset: {business_asset_id}")

        click.echo(f"Moving scheduled times {days} day(s) earlier")

        if dry_run:
            click.echo("\n[DRY RUN MODE - No changes will be made]\n")

        total_updated = 0
        total_skipped = 0
        total_errors = 0

        for asset_id in asset_ids:
            click.echo(f"\n{'='*50}")
            click.echo(f"Business Asset: {asset_id}")
            click.echo(f"{'='*50}")

            results = await move_schedule_for_business_asset(asset_id, days, dry_run)

            click.echo(f"\n  Updated: {results['updated']}")
            click.echo(f"  Skipped (no schedule): {results['skipped_no_schedule']}")
            if results['errors'] > 0:
                click.echo(f"  Errors: {results['errors']}")

            total_updated += results["updated"]
            total_skipped += results["skipped_no_schedule"]
            total_errors += results["errors"]

        # Print summary
        click.echo(f"\n{'='*50}")
        click.echo("SUMMARY")
        click.echo(f"{'='*50}")

        if dry_run:
            click.echo(f"\n[DRY RUN] Would update {total_updated} posts")
        else:
            click.echo(f"\nTotal updated: {total_updated}")

        click.echo(f"Total skipped (no schedule): {total_skipped}")
        if total_errors > 0:
            click.echo(f"Total errors: {total_errors}")

    asyncio.run(_update())


if __name__ == "__main__":
    main()
