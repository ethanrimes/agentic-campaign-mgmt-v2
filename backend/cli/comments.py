# backend/cli/comments.py

"""CLI commands for comment management."""

import click
import asyncio
from backend.utils import get_logger
from backend.services.meta.instagram_comment_checker import check_instagram_comments
from backend.agents.comment_responder import run_comment_responder

logger = get_logger(__name__)


@click.group(name="comments")
def comments():
    """Comment management commands"""
    pass


@comments.command(name="check-instagram")
@click.option("--max-media", default=20, help="Maximum number of recent media to check")
def check_instagram(max_media: int):
    """Check for new Instagram comments and add to database"""
    async def _check():
        logger.info("Checking for new Instagram comments")
        click.echo("📷 Checking for new Instagram comments...")

        result = await check_instagram_comments(max_media=max_media)

        if result.get("success"):
            click.echo(f"\n✅ Instagram comment check completed:")
            click.echo(f"   Media checked: {result.get('media_checked', 0)}")
            click.echo(f"   Comments found: {result.get('comments_found', 0)}")
            click.echo(f"   New comments added: {result.get('new_comments_added', 0)}")

            if result.get("errors"):
                click.echo(f"\n⚠️  Errors encountered: {len(result['errors'])}")
        else:
            click.echo("❌ Instagram comment check failed")
            if result.get("errors"):
                for error in result.get("errors", []):
                    click.echo(f"   Error: {error}")

    asyncio.run(_check())


@comments.command(name="respond")
@click.option("--platform", type=click.Choice(["facebook", "instagram", "all"]), default="all", help="Platform to process")
@click.option("--limit", default=10, help="Maximum number of comments to process")
def respond(platform: str, limit: int):
    """Process pending comments and generate responses"""
    async def _respond():
        logger.info("Processing pending comments", platform=platform)
        click.echo(f"💬 Processing pending comments ({platform})...\n")

        platforms = ["facebook", "instagram"] if platform == "all" else [platform]

        total_processed = 0
        total_responded = 0
        total_failed = 0
        total_ignored = 0

        for plat in platforms:
            icon = "📘" if plat == "facebook" else "📷"
            click.echo(f"{icon} {plat.capitalize()}:")

            result = await run_comment_responder(platform=plat, limit=limit)

            if result.get("processed", 0) > 0:
                click.echo(f"   Processed: {result.get('processed', 0)}")
                click.echo(f"   Responded: {result.get('responded', 0)}")
                click.echo(f"   Ignored: {result.get('ignored', 0)}")
                click.echo(f"   Failed: {result.get('failed', 0)}")

                total_processed += result.get("processed", 0)
                total_responded += result.get("responded", 0)
                total_failed += result.get("failed", 0)
                total_ignored += result.get("ignored", 0)
            else:
                click.echo("   No pending comments")

            click.echo()

        if total_processed > 0:
            click.echo(f"✅ Total: {total_processed} processed | {total_responded} responded | {total_ignored} ignored | {total_failed} failed")
        else:
            click.echo("✅ No pending comments to process")

    asyncio.run(_respond())


@comments.command(name="test-responder")
@click.argument("comment_id")
@click.option("--platform", type=click.Choice(["facebook", "instagram"]), required=True, help="Platform")
def test_responder(comment_id: str, platform: str):
    """Test the comment responder on a specific comment (without posting the reply)"""
    async def _test():
        from backend.database.repositories.platform_comments import PlatformCommentRepository
        from backend.agents.comment_responder import CommentResponderAgent

        logger.info("Testing comment responder", comment_id=comment_id, platform=platform)
        click.echo(f"🧪 Testing comment responder...")
        click.echo(f"   Platform: {platform}")
        click.echo(f"   Comment ID: {comment_id}\n")

        repo = PlatformCommentRepository()

        # Try to find the comment in database
        comment = await repo.get_by_comment_id(platform=platform, comment_id=comment_id)

        if not comment:
            click.echo(f"❌ Comment not found in database")
            click.echo(f"   Platform: {platform}")
            click.echo(f"   Comment ID: {comment_id}")
            return

        click.echo(f"✓ Found comment in database")
        click.echo(f"   Commenter: @{comment.commenter_username}")
        click.echo(f"   Text: {comment.comment_text}")
        click.echo(f"   Status: {comment.status}")
        click.echo(f"   Created: {comment.created_time}\n")

        # Generate response
        click.echo("Generating response...")
        agent = CommentResponderAgent()

        try:
            response = await agent.generate_response(comment)

            if response:
                click.echo(f"\n✅ Generated response:")
                click.echo(f"\n{'-' * 60}")
                click.echo(response)
                click.echo(f"{'-' * 60}\n")
                click.echo(f"Response length: {len(response)} characters")
            else:
                click.echo("\n⚠️  No response generated (comment may be filtered as spam/inappropriate)")

        except Exception as e:
            click.echo(f"\n❌ Failed to generate response: {str(e)}")

    asyncio.run(_test())
