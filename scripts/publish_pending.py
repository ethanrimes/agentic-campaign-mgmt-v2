#!/usr/bin/env python3
# scripts/publish_pending.py

"""
Script to publish all pending posts.

Usage:
    python scripts/publish_pending.py --all
    python scripts/publish_pending.py --business-asset-id penndailybuzz
    python scripts/publish_pending.py --all --before 2025-12-15
    python scripts/publish_pending.py --business-asset-id penndailybuzz --before 2025-12-15T12:00:00
"""

import asyncio
import sys
from datetime import datetime, timezone
from typing import Optional, List
from uuid import UUID

import click

# Add the parent directory to the path so we can import backend
sys.path.insert(0, str(__file__).rsplit("/scripts", 1)[0])

from backend.utils import setup_logging, get_logger
from backend.database.repositories.completed_posts import CompletedPostRepository
from backend.database.repositories.media import MediaRepository
from backend.database.repositories.business_assets import BusinessAssetRepository
from backend.services.meta.facebook_publisher import FacebookPublisher
from backend.services.meta.instagram_publisher import InstagramPublisher
from backend.models import CompletedPost

setup_logging()
logger = get_logger(__name__)


async def get_media_urls(business_asset_id: str, media_ids: List[UUID]) -> List[str]:
    """Fetch media URLs from media IDs."""
    if not media_ids:
        return []

    media_repo = MediaRepository()
    urls = []
    for media_id in media_ids:
        try:
            media = await media_repo.get_by_id(business_asset_id, media_id)
            if media and "public_url" in media:
                urls.append(str(media["public_url"]))
        except Exception as e:
            logger.error("Failed to fetch media", media_id=str(media_id), error=str(e))
    return urls


async def publish_facebook_post(
    business_asset_id: str,
    post: CompletedPost,
    publisher: FacebookPublisher,
    repo: CompletedPostRepository
) -> bool:
    """Publish a single Facebook post."""
    try:
        post_type = post.post_type
        media_urls = await get_media_urls(business_asset_id, post.media_ids)
        text = post.text or ""

        # Determine publishing method based on post type and media
        if post_type == "facebook_video" or (media_urls and len(media_urls) == 1 and ".mp4" in media_urls[0]):
            # Video post
            platform_post_id = await publisher.post_video(media_urls[0], text)
        elif len(media_urls) > 1:
            # Carousel post
            platform_post_id = await publisher.post_carousel(media_urls, text)
        elif len(media_urls) == 1:
            # Single image post
            platform_post_id = await publisher.post_image(media_urls[0], text)
        else:
            # Text/link post
            platform_post_id = await publisher.post_text(text, None)

        # Mark as published
        await repo.mark_published(
            business_asset_id,
            post.id,
            platform_post_id,
            f"https://www.facebook.com/{platform_post_id}"
        )

        logger.info("Published Facebook post", post_id=str(post.id), platform_post_id=platform_post_id)
        return True

    except Exception as e:
        logger.error("Failed to publish Facebook post", post_id=str(post.id), error=str(e))
        await repo.mark_failed(business_asset_id, post.id, str(e))
        return False


async def publish_instagram_post(
    business_asset_id: str,
    post: CompletedPost,
    publisher: InstagramPublisher,
    repo: CompletedPostRepository
) -> bool:
    """Publish a single Instagram post."""
    try:
        post_type = post.post_type
        media_urls = await get_media_urls(business_asset_id, post.media_ids)
        caption = post.text or ""

        # Determine publishing method based on post type
        if post_type == "instagram_reel" or (media_urls and ".mp4" in media_urls[0]):
            # Reel post
            platform_post_id = await publisher.post_reel(media_urls[0], caption)
        elif len(media_urls) > 1:
            # Carousel post
            platform_post_id = await publisher.post_carousel(media_urls, caption)
        elif len(media_urls) == 1:
            # Single image post
            platform_post_id = await publisher.post_image(media_urls[0], caption)
        else:
            logger.error("Instagram post requires media", post_id=str(post.id))
            await repo.mark_failed(business_asset_id, post.id, "Instagram posts require media")
            return False

        # Mark as published
        await repo.mark_published(
            business_asset_id,
            post.id,
            platform_post_id,
            f"https://www.instagram.com/p/{platform_post_id}/"
        )

        logger.info("Published Instagram post", post_id=str(post.id), platform_post_id=platform_post_id)
        return True

    except Exception as e:
        logger.error("Failed to publish Instagram post", post_id=str(post.id), error=str(e))
        await repo.mark_failed(business_asset_id, post.id, str(e))
        return False


def get_all_business_asset_ids() -> List[str]:
    """Get all active business asset IDs."""
    repo = BusinessAssetRepository()
    assets = repo.get_all_active()
    return [asset.id for asset in assets]


async def publish_for_business_asset(
    business_asset_id: str,
    before_date: Optional[datetime],
    limit: int
) -> dict:
    """
    Publish pending posts for a single business asset.

    Args:
        business_asset_id: Business asset ID
        before_date: Only publish posts scheduled before this date
        limit: Maximum posts per platform

    Returns:
        Summary of results
    """
    repo = CompletedPostRepository()
    fb_publisher = FacebookPublisher(business_asset_id)
    ig_publisher = InstagramPublisher(business_asset_id)

    results = {
        "business_asset_id": business_asset_id,
        "facebook": {"attempted": 0, "success": 0},
        "instagram": {"attempted": 0, "success": 0},
    }

    # Get pending posts ready to publish
    fb_posts = await repo.get_posts_ready_to_publish(business_asset_id, "facebook", limit)
    ig_posts = await repo.get_posts_ready_to_publish(business_asset_id, "instagram", limit)

    # Filter by before_date if specified
    if before_date:
        fb_posts = [
            p for p in fb_posts
            if p.scheduled_posting_time and p.scheduled_posting_time < before_date
        ]
        ig_posts = [
            p for p in ig_posts
            if p.scheduled_posting_time and p.scheduled_posting_time < before_date
        ]

    # Publish Facebook posts
    for post in fb_posts:
        results["facebook"]["attempted"] += 1
        if await publish_facebook_post(business_asset_id, post, fb_publisher, repo):
            results["facebook"]["success"] += 1

    # Publish Instagram posts
    for post in ig_posts:
        results["instagram"]["attempted"] += 1
        if await publish_instagram_post(business_asset_id, post, ig_publisher, repo):
            results["instagram"]["success"] += 1

    return results


def parse_datetime(date_str: str) -> datetime:
    """Parse a datetime string in various formats."""
    formats = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            # If no timezone, assume UTC
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue

    raise ValueError(f"Unable to parse date: {date_str}. Use format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS")


@click.command()
@click.option(
    "--all", "publish_all",
    is_flag=True,
    help="Publish pending posts for all active business assets"
)
@click.option(
    "--business-asset-id",
    type=str,
    help="Business asset ID to publish for (e.g., penndailybuzz)"
)
@click.option(
    "--before",
    type=str,
    help="Only publish posts scheduled before this date (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"
)
@click.option(
    "--limit",
    default=100,
    type=int,
    help="Maximum posts per platform per business asset (default: 100)"
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be published without actually publishing"
)
def main(
    publish_all: bool,
    business_asset_id: Optional[str],
    before: Optional[str],
    limit: int,
    dry_run: bool
):
    """
    Publish all pending posts.

    Either --all or --business-asset-id must be specified.

    Examples:

        # Publish all pending posts for all business assets
        python scripts/publish_pending.py --all

        # Publish pending posts for a specific business asset
        python scripts/publish_pending.py --business-asset-id penndailybuzz

        # Publish posts scheduled before a specific date
        python scripts/publish_pending.py --all --before 2025-12-15

        # Dry run to see what would be published
        python scripts/publish_pending.py --all --dry-run
    """
    if not publish_all and not business_asset_id:
        click.echo("Error: Either --all or --business-asset-id must be specified", err=True)
        sys.exit(1)

    if publish_all and business_asset_id:
        click.echo("Error: Cannot specify both --all and --business-asset-id", err=True)
        sys.exit(1)

    # Parse before date if specified
    before_date = None
    if before:
        try:
            before_date = parse_datetime(before)
            click.echo(f"📅 Filtering posts scheduled before: {before_date.isoformat()}")
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)

    async def _publish():
        # Get business asset IDs to process
        if publish_all:
            asset_ids = get_all_business_asset_ids()
            if not asset_ids:
                click.echo("No active business assets found")
                return
            click.echo(f"📱 Publishing for {len(asset_ids)} business assets")
        else:
            asset_ids = [business_asset_id]
            click.echo(f"📱 Publishing for business asset: {business_asset_id}")

        if dry_run:
            click.echo("\n🔍 DRY RUN MODE - No posts will be published\n")

        total_results = {
            "facebook": {"attempted": 0, "success": 0},
            "instagram": {"attempted": 0, "success": 0},
        }

        for asset_id in asset_ids:
            click.echo(f"\n{'='*50}")
            click.echo(f"📊 Processing: {asset_id}")
            click.echo(f"{'='*50}")

            if dry_run:
                # In dry run mode, just show what would be published
                repo = CompletedPostRepository()
                fb_posts = await repo.get_posts_ready_to_publish(asset_id, "facebook", limit)
                ig_posts = await repo.get_posts_ready_to_publish(asset_id, "instagram", limit)

                if before_date:
                    fb_posts = [
                        p for p in fb_posts
                        if p.scheduled_posting_time and p.scheduled_posting_time < before_date
                    ]
                    ig_posts = [
                        p for p in ig_posts
                        if p.scheduled_posting_time and p.scheduled_posting_time < before_date
                    ]

                click.echo(f"\n📘 Facebook: {len(fb_posts)} posts would be published")
                for post in fb_posts[:5]:
                    scheduled = post.scheduled_posting_time.strftime("%Y-%m-%d %H:%M") if post.scheduled_posting_time else "N/A"
                    click.echo(f"   - {post.id} (scheduled: {scheduled})")
                if len(fb_posts) > 5:
                    click.echo(f"   ... and {len(fb_posts) - 5} more")

                click.echo(f"\n📷 Instagram: {len(ig_posts)} posts would be published")
                for post in ig_posts[:5]:
                    scheduled = post.scheduled_posting_time.strftime("%Y-%m-%d %H:%M") if post.scheduled_posting_time else "N/A"
                    click.echo(f"   - {post.id} (scheduled: {scheduled})")
                if len(ig_posts) > 5:
                    click.echo(f"   ... and {len(ig_posts) - 5} more")
            else:
                # Actually publish
                results = await publish_for_business_asset(asset_id, before_date, limit)

                click.echo(f"\n📘 Facebook: {results['facebook']['success']}/{results['facebook']['attempted']} published")
                click.echo(f"📷 Instagram: {results['instagram']['success']}/{results['instagram']['attempted']} published")

                # Accumulate totals
                total_results["facebook"]["attempted"] += results["facebook"]["attempted"]
                total_results["facebook"]["success"] += results["facebook"]["success"]
                total_results["instagram"]["attempted"] += results["instagram"]["attempted"]
                total_results["instagram"]["success"] += results["instagram"]["success"]

        # Print summary
        click.echo(f"\n{'='*50}")
        click.echo("📊 SUMMARY")
        click.echo(f"{'='*50}")

        if dry_run:
            click.echo("\n🔍 DRY RUN - No posts were actually published")
        else:
            total_attempted = total_results["facebook"]["attempted"] + total_results["instagram"]["attempted"]
            total_success = total_results["facebook"]["success"] + total_results["instagram"]["success"]
            click.echo(f"\n✅ Total: {total_success}/{total_attempted} posts published")
            click.echo(f"   📘 Facebook: {total_results['facebook']['success']}/{total_results['facebook']['attempted']}")
            click.echo(f"   📷 Instagram: {total_results['instagram']['success']}/{total_results['instagram']['attempted']}")

    asyncio.run(_publish())


if __name__ == "__main__":
    main()
