#!/usr/bin/env python3
# backend/update_schedule.py

"""
Script to update posting schedules for all pending posts.

This script recalculates the scheduled_posting_time for all pending posts
based on the current scheduling configuration in backend/scheduler.py.

Usage:
    python backend/update_schedule.py [--platform facebook|instagram|all]

When run:
- The first post for each platform will be scheduled with the initial delay from now
- Subsequent posts will be scheduled at the configured interval after the previous post
- Posts are processed in creation order (oldest first)
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Literal, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import click
from backend.database.repositories.completed_posts import CompletedPostRepository
from backend.scheduler import SCHEDULING_CONFIG
from backend.utils import get_logger

logger = get_logger(__name__)


async def update_schedule_for_platform(
    platform: Literal["facebook", "instagram"],
    dry_run: bool = False
) -> dict:
    """
    Update posting schedule for a specific platform.

    Args:
        platform: Platform to update
        dry_run: If True, don't actually update the database

    Returns:
        Summary of changes
    """
    logger.info(f"Updating schedule for {platform}", dry_run=dry_run)

    repo = CompletedPostRepository()

    # Get all pending posts for this platform (ordered by creation time)
    pending_posts = await repo.get_all_pending_posts(platform)

    if not pending_posts:
        logger.info(f"No pending posts found for {platform}")
        return {
            "platform": platform,
            "posts_updated": 0,
            "posts": []
        }

    logger.info(f"Found {len(pending_posts)} pending posts for {platform}")

    # Get configuration for this platform
    if platform == "facebook":
        interval_hours = SCHEDULING_CONFIG.FACEBOOK_POST_INTERVAL_HOURS
        initial_delay_hours = SCHEDULING_CONFIG.FACEBOOK_INITIAL_DELAY_HOURS
    else:  # instagram
        interval_hours = SCHEDULING_CONFIG.INSTAGRAM_POST_INTERVAL_HOURS
        initial_delay_hours = SCHEDULING_CONFIG.INSTAGRAM_INITIAL_DELAY_HOURS

    # Calculate scheduled times
    now = datetime.now(timezone.utc)
    current_scheduled_time = now + timedelta(hours=initial_delay_hours)

    updates = []
    for post in pending_posts:
        old_time = post.scheduled_posting_time
        new_time = current_scheduled_time

        updates.append({
            "post_id": str(post.id),
            "old_scheduled_time": old_time.isoformat() if old_time else None,
            "new_scheduled_time": new_time.isoformat(),
            "platform": platform
        })

        # Update in database
        if not dry_run:
            await repo.update_scheduled_time(post.id, new_time)

        # Increment for next post
        current_scheduled_time += timedelta(hours=interval_hours)

    logger.info(
        f"Updated {len(updates)} posts for {platform}",
        first_scheduled=updates[0]["new_scheduled_time"] if updates else None,
        last_scheduled=updates[-1]["new_scheduled_time"] if updates else None
    )

    return {
        "platform": platform,
        "posts_updated": len(updates),
        "posts": updates
    }


async def update_all_schedules(dry_run: bool = False) -> dict:
    """
    Update posting schedules for all platforms.

    Args:
        dry_run: If True, don't actually update the database

    Returns:
        Summary of all changes
    """
    logger.info("Updating schedules for all platforms", dry_run=dry_run)

    facebook_results = await update_schedule_for_platform("facebook", dry_run)
    instagram_results = await update_schedule_for_platform("instagram", dry_run)

    total_updated = facebook_results["posts_updated"] + instagram_results["posts_updated"]

    logger.info(
        "Schedule update complete",
        total_posts_updated=total_updated,
        facebook_posts=facebook_results["posts_updated"],
        instagram_posts=instagram_results["posts_updated"]
    )

    return {
        "total_posts_updated": total_updated,
        "facebook": facebook_results,
        "instagram": instagram_results
    }


@click.command()
@click.option(
    "--platform",
    type=click.Choice(["facebook", "instagram", "all"]),
    default="all",
    help="Platform to update (default: all)"
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Preview changes without updating the database"
)
def main(platform: str, dry_run: bool):
    """
    Update posting schedules for pending posts.

    This recalculates scheduled_posting_time for all pending posts based on
    the current scheduling configuration.
    """
    click.echo("=" * 80)
    click.echo("Post Schedule Update Script")
    click.echo("=" * 80)
    click.echo()

    if dry_run:
        click.echo("🔍 DRY RUN MODE - No changes will be made")
        click.echo()

    click.echo(f"Scheduling Configuration:")
    click.echo(f"  Facebook: Every {SCHEDULING_CONFIG.FACEBOOK_POST_INTERVAL_HOURS}h (initial delay: {SCHEDULING_CONFIG.FACEBOOK_INITIAL_DELAY_HOURS}h)")
    click.echo(f"  Instagram: Every {SCHEDULING_CONFIG.INSTAGRAM_POST_INTERVAL_HOURS}h (initial delay: {SCHEDULING_CONFIG.INSTAGRAM_INITIAL_DELAY_HOURS}h)")
    click.echo()

    async def _run():
        if platform == "all":
            results = await update_all_schedules(dry_run)

            click.echo(f"\n📊 Summary:")
            click.echo(f"  Total posts updated: {results['total_posts_updated']}")
            click.echo(f"  Facebook posts: {results['facebook']['posts_updated']}")
            click.echo(f"  Instagram posts: {results['instagram']['posts_updated']}")

            if dry_run:
                click.echo("\n⚠️  This was a dry run. Run without --dry-run to apply changes.")
            else:
                click.echo("\n✅ Schedule updated successfully!")

        else:
            results = await update_schedule_for_platform(platform, dry_run)

            click.echo(f"\n📊 Summary:")
            click.echo(f"  {platform.capitalize()} posts updated: {results['posts_updated']}")

            if results["posts"]:
                click.echo(f"\n📅 New Schedule:")
                for i, update in enumerate(results["posts"][:5], 1):  # Show first 5
                    scheduled_time = datetime.fromisoformat(update["new_scheduled_time"])
                    click.echo(f"  {i}. {scheduled_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")

                if len(results["posts"]) > 5:
                    click.echo(f"  ... and {len(results['posts']) - 5} more")

            if dry_run:
                click.echo("\n⚠️  This was a dry run. Run without --dry-run to apply changes.")
            else:
                click.echo("\n✅ Schedule updated successfully!")

    asyncio.run(_run())


if __name__ == "__main__":
    main()
