# backend/cli/publish.py

"""CLI commands for publishing content."""

import click
import asyncio
from typing import Dict, Any
from backend.utils import get_logger
from backend.database.repositories.completed_posts import CompletedPostsRepository
from backend.services.meta.facebook_publisher import FacebookPublisher
from backend.services.meta.instagram_publisher import InstagramPublisher

logger = get_logger(__name__)


@click.group(name="publish")
def publish():
    """Content publishing commands"""
    pass


async def publish_facebook_post(post: Dict[str, Any], publisher: FacebookPublisher, repo: CompletedPostsRepository) -> bool:
    """Publish a single Facebook post."""
    try:
        post_type = post.get("post_type", "")
        media_urls = post.get("media_urls", [])
        text = post.get("text", "")

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
            platform_post_id = await publisher.post_text(text, post.get("link"))

        # Mark as published
        await repo.mark_published(
            post["id"],
            platform_post_id,
            f"https://www.facebook.com/{platform_post_id}"
        )

        logger.info("Published Facebook post", post_id=post["id"], platform_post_id=platform_post_id)
        return True

    except Exception as e:
        logger.error("Failed to publish Facebook post", post_id=post["id"], error=str(e))
        await repo.mark_failed(post["id"], str(e))
        return False


async def publish_instagram_post(post: Dict[str, Any], publisher: InstagramPublisher, repo: CompletedPostsRepository) -> bool:
    """Publish a single Instagram post."""
    try:
        post_type = post.get("post_type", "")
        media_urls = post.get("media_urls", [])
        caption = post.get("text", "")

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
            logger.error("Instagram post requires media", post_id=post["id"])
            await repo.mark_failed(post["id"], "Instagram posts require media")
            return False

        # Mark as published
        await repo.mark_published(
            post["id"],
            platform_post_id,
            f"https://www.instagram.com/p/{platform_post_id}/"
        )

        logger.info("Published Instagram post", post_id=post["id"], platform_post_id=platform_post_id)
        return True

    except Exception as e:
        logger.error("Failed to publish Instagram post", post_id=post["id"], error=str(e))
        await repo.mark_failed(post["id"], str(e))
        return False


@publish.command()
@click.option("--limit", default=10, help="Maximum number of posts to publish")
def facebook(limit: int):
    """Publish pending Facebook posts"""
    async def _publish():
        logger.info("Publishing Facebook posts")
        click.echo("📘 Publishing to Facebook...")

        repo = CompletedPostsRepository()
        publisher = FacebookPublisher()

        # Get pending posts
        pending_posts = await repo.get_pending_for_platform("facebook", limit)

        if not pending_posts:
            click.echo("   No pending Facebook posts")
            return

        click.echo(f"   Found {len(pending_posts)} pending posts")

        # Publish each post
        success_count = 0
        for i, post in enumerate(pending_posts, 1):
            click.echo(f"   Publishing post {i}/{len(pending_posts)}...")
            if await publish_facebook_post(post, publisher, repo):
                success_count += 1

        click.echo(f"✅ Published {success_count}/{len(pending_posts)} Facebook posts")

    asyncio.run(_publish())


@publish.command()
@click.option("--limit", default=10, help="Maximum number of posts to publish")
def instagram(limit: int):
    """Publish pending Instagram posts"""
    async def _publish():
        logger.info("Publishing Instagram posts")
        click.echo("📷 Publishing to Instagram...")

        repo = CompletedPostsRepository()
        publisher = InstagramPublisher()

        # Get pending posts
        pending_posts = await repo.get_pending_for_platform("instagram", limit)

        if not pending_posts:
            click.echo("   No pending Instagram posts")
            return

        click.echo(f"   Found {len(pending_posts)} pending posts")

        # Publish each post
        success_count = 0
        for i, post in enumerate(pending_posts, 1):
            click.echo(f"   Publishing post {i}/{len(pending_posts)}...")
            if await publish_instagram_post(post, publisher, repo):
                success_count += 1

        click.echo(f"✅ Published {success_count}/{len(pending_posts)} Instagram posts")

    asyncio.run(_publish())


@publish.command()
@click.option("--limit", default=10, help="Maximum posts per platform")
def all(limit: int):
    """Publish all pending posts"""
    async def _publish():
        logger.info("Publishing all posts")
        click.echo("📱 Publishing to all platforms...")

        repo = CompletedPostsRepository()
        fb_publisher = FacebookPublisher()
        ig_publisher = InstagramPublisher()

        total_success = 0
        total_attempted = 0

        # Publish Facebook posts
        click.echo("\n📘 Facebook:")
        fb_posts = await repo.get_pending_for_platform("facebook", limit)
        if fb_posts:
            click.echo(f"   Found {len(fb_posts)} pending posts")
            for i, post in enumerate(fb_posts, 1):
                click.echo(f"   Publishing post {i}/{len(fb_posts)}...")
                total_attempted += 1
                if await publish_facebook_post(post, fb_publisher, repo):
                    total_success += 1
        else:
            click.echo("   No pending posts")

        # Publish Instagram posts
        click.echo("\n📷 Instagram:")
        ig_posts = await repo.get_pending_for_platform("instagram", limit)
        if ig_posts:
            click.echo(f"   Found {len(ig_posts)} pending posts")
            for i, post in enumerate(ig_posts, 1):
                click.echo(f"   Publishing post {i}/{len(ig_posts)}...")
                total_attempted += 1
                if await publish_instagram_post(post, ig_publisher, repo):
                    total_success += 1
        else:
            click.echo("   No pending posts")

        click.echo(f"\n✅ Published {total_success}/{total_attempted} total posts")

    asyncio.run(_publish())
