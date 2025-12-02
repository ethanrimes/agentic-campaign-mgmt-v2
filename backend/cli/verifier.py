# backend/cli/verifier.py

"""CLI commands for content verifier agent."""

import click
import asyncio
from backend.utils import get_logger

logger = get_logger(__name__)


@click.group(name="verifier")
def verifier():
    """Content verification commands"""
    pass


@verifier.command()
@click.option(
    '--business-asset-id',
    required=True,
    type=str,
    help='Business asset ID (e.g., penndailybuzz, eaglesnationfanhuddle)'
)
@click.option(
    '--post-id',
    required=True,
    type=str,
    help='ID of the completed post to verify'
)
def verify(business_asset_id: str, post_id: str):
    """Verify a specific completed post"""
    from backend.agents.verifier import verify_single_post

    logger.info("Verifying post", business_asset_id=business_asset_id, post_id=post_id)
    click.echo(f"🔍 Verifying post: {post_id}")

    result = asyncio.run(verify_single_post(business_asset_id, post_id))

    if result['is_approved']:
        click.echo(f"✅ Post APPROVED")
    else:
        click.echo(f"❌ Post REJECTED")

    click.echo(f"\n📋 Checklist Results:")
    click.echo(f"   - No offensive content: {result['has_no_offensive_content']}")
    click.echo(f"   - No misinformation (if news): {result.get('has_no_misinformation', 'N/A')}")

    click.echo(f"\n💬 Reasoning:")
    click.echo(f"   {result['reasoning']}")

    if result.get('issues_found'):
        click.echo(f"\n⚠️  Issues Found:")
        for issue in result['issues_found']:
            click.echo(f"   - {issue}")


@verifier.command()
@click.option(
    '--business-asset-id',
    required=True,
    type=str,
    help='Business asset ID (e.g., penndailybuzz, eaglesnationfanhuddle)'
)
def verify_all(business_asset_id: str):
    """Verify all unverified pending posts.

    Only verifies PRIMARY posts. Secondary posts in verification groups
    (created with --share-media) automatically inherit the verification result.
    """
    from backend.agents.verifier import verify_all_unverified

    logger.info("Verifying all unverified posts", business_asset_id=business_asset_id)
    click.echo(f"🔍 Verifying all unverified primary posts for {business_asset_id}...")

    result = asyncio.run(verify_all_unverified(business_asset_id))

    click.echo(f"\n✅ Verification Complete")
    click.echo(f"   Primary posts verified: {result['posts_verified']}")
    if result.get('posts_affected', 0) > result['posts_verified']:
        click.echo(f"   Total posts affected: {result['posts_affected']} (includes secondary posts in groups)")
    click.echo(f"   Approved: {result['approved']}")
    click.echo(f"   Rejected: {result['rejected']}")
    if result.get('errors', 0) > 0:
        click.echo(f"   Errors: {result['errors']}")


@verifier.command()
@click.option(
    '--business-asset-id',
    required=True,
    type=str,
    help='Business asset ID (e.g., penndailybuzz, eaglesnationfanhuddle)'
)
def stats(business_asset_id: str):
    """Show verification statistics"""
    from backend.database.repositories.verifier_responses import VerifierResponseRepository

    async def get_stats():
        repo = VerifierResponseRepository()
        return await repo.get_stats(business_asset_id)

    logger.info("Getting verification stats", business_asset_id=business_asset_id)
    click.echo(f"📊 Verification Statistics for {business_asset_id}")

    result = asyncio.run(get_stats())

    click.echo(f"\n   Total verifications: {result['total_verifications']}")
    click.echo(f"   Approved: {result['approved']}")
    click.echo(f"   Rejected: {result['rejected']}")
    click.echo(f"   Approval rate: {result['approval_rate']:.1f}%")


@verifier.command()
@click.option(
    '--business-asset-id',
    required=True,
    type=str,
    help='Business asset ID (e.g., penndailybuzz, eaglesnationfanhuddle)'
)
@click.option(
    '--limit',
    default=10,
    type=int,
    help='Maximum number of posts to show'
)
def rejected(business_asset_id: str, limit: int):
    """List recently rejected posts"""
    from backend.database.repositories.verifier_responses import VerifierResponseRepository

    async def get_rejected():
        repo = VerifierResponseRepository()
        return await repo.get_rejected_posts(business_asset_id, limit)

    logger.info("Getting rejected posts", business_asset_id=business_asset_id)
    click.echo(f"❌ Recently Rejected Posts for {business_asset_id}\n")

    results = asyncio.run(get_rejected())

    if not results:
        click.echo("   No rejected posts found")
        return

    for i, response in enumerate(results, 1):
        click.echo(f"{i}. Post ID: {response.completed_post_id}")
        click.echo(f"   Reason: {response.reasoning[:100]}...")
        if response.issues_found:
            click.echo(f"   Issues: {', '.join(response.issues_found[:3])}")
        click.echo()


@verifier.command()
@click.option(
    '--business-asset-id',
    required=True,
    type=str,
    help='Business asset ID (e.g., penndailybuzz, eaglesnationfanhuddle)'
)
@click.option(
    '--limit',
    default=20,
    type=int,
    help='Maximum number of posts to show'
)
def unverified(business_asset_id: str, limit: int):
    """List unverified pending posts"""
    from backend.database.repositories.completed_posts import CompletedPostRepository

    async def get_unverified():
        repo = CompletedPostRepository()
        return await repo.get_unverified_posts(business_asset_id, limit)

    logger.info("Getting unverified posts", business_asset_id=business_asset_id)
    click.echo(f"⏳ Unverified Pending Posts for {business_asset_id}\n")

    results = asyncio.run(get_unverified())

    if not results:
        click.echo("   No unverified posts found")
        return

    click.echo(f"Found {len(results)} unverified posts:\n")
    for i, post in enumerate(results, 1):
        click.echo(f"{i}. Post ID: {post.id}")
        click.echo(f"   Platform: {post.platform} ({post.post_type})")
        click.echo(f"   Text: {post.text[:80]}...")
        click.echo(f"   Created: {post.created_at}")
        click.echo()
