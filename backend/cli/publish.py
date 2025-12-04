# backend/cli/publish.py

"""CLI commands for publishing content."""

import click
import asyncio
from typing import List
from uuid import UUID
from backend.utils import get_logger
from backend.models import CompletedPost
from backend.database.repositories.completed_posts import CompletedPostRepository
from backend.database.repositories.media import MediaRepository
from backend.services.meta.facebook_publisher import FacebookPublisher
from backend.services.meta.instagram_publisher import InstagramPublisher

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


@click.group(name="publish")
def publish():
    """Content publishing commands"""
    pass


async def publish_facebook_post(business_asset_id: str, post: CompletedPost, publisher: FacebookPublisher, repo: CompletedPostRepository) -> bool:
    """Publish a single Facebook post."""
    try:
        post_type = post.post_type
        media_urls = await get_media_urls(business_asset_id, post.media_ids)
        text = post.text or ""

        platform_post_id = None
        platform_video_id = None
        platform_post_url = None

        # Determine publishing method based on post type and media
        if post_type == "facebook_video" or (media_urls and len(media_urls) == 1 and ".mp4" in media_urls[0]):
            # Video post - returns video_id which can be used for insights
            platform_post_id = await publisher.post_video(media_urls[0], text)
            # For video posts, the returned ID is the video_id
            platform_video_id = platform_post_id
            platform_post_url = f"https://www.facebook.com/reel/{platform_post_id}"
        elif len(media_urls) > 1:
            # Carousel post
            platform_post_id = await publisher.post_carousel(media_urls, text)
            platform_post_url = f"https://www.facebook.com/{platform_post_id}"
        elif len(media_urls) == 1:
            # Single image post
            platform_post_id = await publisher.post_image(media_urls[0], text)
            platform_post_url = f"https://www.facebook.com/{platform_post_id}"
        else:
            # Text/link post
            platform_post_id = await publisher.post_text(text, None)
            platform_post_url = f"https://www.facebook.com/{platform_post_id}"

        # Mark as published with video_id if applicable
        await repo.mark_published(
            business_asset_id,
            post.id,
            platform_post_id,
            platform_post_url,
            platform_video_id=platform_video_id
        )

        logger.info("Published Facebook post", post_id=str(post.id), platform_post_id=platform_post_id, platform_video_id=platform_video_id)
        return True

    except Exception as e:
        logger.error("Failed to publish Facebook post", post_id=str(post.id), error=str(e))
        await repo.mark_failed(business_asset_id, post.id, str(e))
        return False


async def publish_instagram_post(business_asset_id: str, post: CompletedPost, publisher: InstagramPublisher, repo: CompletedPostRepository) -> bool:
    """Publish a single Instagram post."""
    try:
        post_type = post.post_type
        media_urls = await get_media_urls(business_asset_id, post.media_ids)
        caption = post.text or ""

        platform_post_id = None
        platform_video_id = None

        # Determine publishing method based on post type
        if post_type == "instagram_reel" or (media_urls and ".mp4" in media_urls[0]):
            # Reel post - returns media_id which can be used for video insights
            platform_post_id = await publisher.post_reel(media_urls[0], caption)
            # For reels, the returned media_id is also the video_id for insights
            platform_video_id = platform_post_id
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

        # Mark as published with video_id if applicable
        await repo.mark_published(
            business_asset_id,
            post.id,
            platform_post_id,
            f"https://www.instagram.com/p/{platform_post_id}/",
            platform_video_id=platform_video_id
        )

        logger.info("Published Instagram post", post_id=str(post.id), platform_post_id=platform_post_id, platform_video_id=platform_video_id)
        return True

    except Exception as e:
        logger.error("Failed to publish Instagram post", post_id=str(post.id), error=str(e))
        await repo.mark_failed(business_asset_id, post.id, str(e))
        return False


@publish.command()
@click.option(
    '--business-asset-id',
    required=True,
    type=str,
    help='Business asset ID (e.g., penndailybuzz, eaglesnationfanhuddle)'
)
@click.option("--limit", default=10, help="Maximum number of posts to publish")
def facebook(business_asset_id: str, limit: int):
    """Publish scheduled Facebook posts that are ready"""
    async def _publish():
        logger.info("Checking for scheduled Facebook posts", business_asset_id=business_asset_id)
        click.echo("📘 Checking for Facebook posts to publish...")

        repo = CompletedPostRepository()
        publisher = FacebookPublisher(business_asset_id)

        # Get posts ready to publish (scheduled time has arrived)
        ready_posts = await repo.get_posts_ready_to_publish(business_asset_id, "facebook", limit)

        if not ready_posts:
            click.echo("   No Facebook posts ready to publish")
            return

        click.echo(f"   Found {len(ready_posts)} posts ready to publish")

        # Publish each post
        success_count = 0
        for i, post in enumerate(ready_posts, 1):
            scheduled_time = post.scheduled_posting_time.strftime("%Y-%m-%d %H:%M:%S") if post.scheduled_posting_time else "immediately"
            click.echo(f"   Publishing post {i}/{len(ready_posts)} (scheduled: {scheduled_time})...")
            if await publish_facebook_post(business_asset_id, post, publisher, repo):
                success_count += 1

        click.echo(f"✅ Published {success_count}/{len(ready_posts)} Facebook posts")

    asyncio.run(_publish())


@publish.command()
@click.option(
    '--business-asset-id',
    required=True,
    type=str,
    help='Business asset ID (e.g., penndailybuzz, eaglesnationfanhuddle)'
)
@click.option("--limit", default=10, help="Maximum number of posts to publish")
def instagram(business_asset_id: str, limit: int):
    """Publish scheduled Instagram posts that are ready"""
    async def _publish():
        logger.info("Checking for scheduled Instagram posts", business_asset_id=business_asset_id)
        click.echo("📷 Checking for Instagram posts to publish...")

        repo = CompletedPostRepository()
        publisher = InstagramPublisher(business_asset_id)

        # Get posts ready to publish (scheduled time has arrived)
        ready_posts = await repo.get_posts_ready_to_publish(business_asset_id, "instagram", limit)

        if not ready_posts:
            click.echo("   No Instagram posts ready to publish")
            return

        click.echo(f"   Found {len(ready_posts)} posts ready to publish")

        # Publish each post
        success_count = 0
        for i, post in enumerate(ready_posts, 1):
            scheduled_time = post.scheduled_posting_time.strftime("%Y-%m-%d %H:%M:%S") if post.scheduled_posting_time else "immediately"
            click.echo(f"   Publishing post {i}/{len(ready_posts)} (scheduled: {scheduled_time})...")
            if await publish_instagram_post(business_asset_id, post, publisher, repo):
                success_count += 1

        click.echo(f"✅ Published {success_count}/{len(ready_posts)} Instagram posts")

    asyncio.run(_publish())


@publish.command()
@click.option(
    '--business-asset-id',
    required=True,
    type=str,
    help='Business asset ID (e.g., penndailybuzz, eaglesnationfanhuddle)'
)
@click.option("--limit", default=10, help="Maximum posts per platform")
def all(business_asset_id: str, limit: int):
    """Publish all scheduled posts that are ready"""
    async def _publish():
        logger.info("Checking for scheduled posts on all platforms", business_asset_id=business_asset_id)
        click.echo("📱 Checking for posts to publish on all platforms...")

        repo = CompletedPostRepository()
        fb_publisher = FacebookPublisher(business_asset_id)
        ig_publisher = InstagramPublisher(business_asset_id)

        total_success = 0
        total_attempted = 0

        # Publish Facebook posts
        click.echo("\n📘 Facebook:")
        fb_posts = await repo.get_posts_ready_to_publish(business_asset_id, "facebook", limit)
        if fb_posts:
            click.echo(f"   Found {len(fb_posts)} posts ready to publish")
            for i, post in enumerate(fb_posts, 1):
                scheduled_time = post.scheduled_posting_time.strftime("%Y-%m-%d %H:%M:%S") if post.scheduled_posting_time else "immediately"
                click.echo(f"   Publishing post {i}/{len(fb_posts)} (scheduled: {scheduled_time})...")
                total_attempted += 1
                if await publish_facebook_post(business_asset_id, post, fb_publisher, repo):
                    total_success += 1
        else:
            click.echo("   No posts ready to publish")

        # Publish Instagram posts
        click.echo("\n📷 Instagram:")
        ig_posts = await repo.get_posts_ready_to_publish(business_asset_id, "instagram", limit)
        if ig_posts:
            click.echo(f"   Found {len(ig_posts)} posts ready to publish")
            for i, post in enumerate(ig_posts, 1):
                scheduled_time = post.scheduled_posting_time.strftime("%Y-%m-%d %H:%M:%S") if post.scheduled_posting_time else "immediately"
                click.echo(f"   Publishing post {i}/{len(ig_posts)} (scheduled: {scheduled_time})...")
                total_attempted += 1
                if await publish_instagram_post(business_asset_id, post, ig_publisher, repo):
                    total_success += 1
        else:
            click.echo("   No posts ready to publish")

        click.echo(f"\n✅ Published {total_success}/{total_attempted} total posts")

    asyncio.run(_publish())
