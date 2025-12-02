# backend/tools/tests/test_engagement_tools.py

"""
Integration tests for engagement tools.
Tests the new direct API fetch functions for the context-stuffing approach.

Run: python -m backend.tools.tests.test_engagement_tools
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import asyncio
from backend.tools.engagement_tools import (
    fetch_facebook_page_insights,
    fetch_facebook_post_insights,
    fetch_facebook_video_insights,
    fetch_instagram_media_insights,
    fetch_instagram_account_insights,
    fetch_platform_comments,
)
from backend.database.repositories.completed_posts import CompletedPostRepository
from backend.utils import get_logger

logger = get_logger(__name__)


async def test_facebook_page_insights(business_asset_id: str):
    """Test Facebook Page insights."""
    logger.info("=" * 80)
    logger.info("TESTING: Facebook Page Insights")
    logger.info("=" * 80)

    # Test 1: Basic page metrics
    logger.info("\n--- Test 1: Page insights (last 14 days) ---")
    result = await fetch_facebook_page_insights(
        business_asset_id=business_asset_id,
        period="day",
        days_back=14
    )
    if result:
        logger.info(f"✓ Got {len(result)} data points")
        for insight in result[:5]:  # Show first 5
            logger.info(f"  {insight.name}: {insight.value} (end: {insight.end_time})")
    else:
        logger.warning("✗ No data returned")

    logger.info("\n✓ Facebook Page insights tests complete\n")


async def test_facebook_post_insights(business_asset_id: str):
    """Test Facebook Post insights (feed posts)."""
    logger.info("=" * 80)
    logger.info("TESTING: Facebook Post Insights (Feed Posts)")
    logger.info("=" * 80)

    repo = CompletedPostRepository()

    # Get recent published Facebook posts
    logger.info("\n--- Fetching recent published Facebook posts from database ---")
    posts = await repo.get_recent_published_by_platform(business_asset_id, "facebook", limit=10)

    # Filter for feed posts (not videos)
    feed_posts = [p for p in posts if p.post_type == "facebook_feed"]

    if not feed_posts:
        logger.warning("✗ No published Facebook feed posts found")
        logger.info("\n✓ Facebook Post insights tests complete (skipped)\n")
        return

    logger.info(f"✓ Found {len(feed_posts)} published Facebook feed posts")

    # Test first post
    post = feed_posts[0]
    logger.info(f"\n--- Testing post: {post.platform_post_id} ---")
    logger.info(f"  Text: {post.text[:80]}...")

    result = await fetch_facebook_post_insights(
        business_asset_id=business_asset_id,
        platform_post_id=post.platform_post_id
    )

    if result:
        logger.info("✓ Post insights retrieved:")
        logger.info(f"  Total Reactions: {result.reactions_like}")
        logger.info(f"  Likes: {result.reactions_like}")
        logger.info(f"  Loves: {result.reactions_love}")
        logger.info(f"  Wows: {result.reactions_wow}")
        logger.info(f"  Hahas: {result.reactions_haha}")
        logger.info(f"  Reactions by type: {result.reactions_by_type}")
    else:
        logger.warning("✗ No insights data returned")

    logger.info("\n✓ Facebook Post insights tests complete\n")


async def test_facebook_video_insights(business_asset_id: str):
    """Test Facebook Video insights."""
    logger.info("=" * 80)
    logger.info("TESTING: Facebook Video Insights")
    logger.info("=" * 80)

    # Test 1: Direct video ID test (from Meta API directly)
    # This video ID is known to exist for flyeaglesflycommunity
    direct_video_id = "1375731680607892"
    logger.info(f"\n--- Test 1: Direct video ID test: {direct_video_id} ---")

    result = await fetch_facebook_video_insights(
        business_asset_id=business_asset_id,
        video_id=direct_video_id
    )

    if result:
        logger.info("✓ Video insights retrieved:")
        logger.info(f"  Total Views (blue_reels_play_count): {result.total_views}")
        logger.info(f"  Unique Reach (post_impressions_unique): {result.unique_views}")
        logger.info(f"  Avg Watch Time: {result.avg_time_watched_ms}ms")
        logger.info(f"  Total Watch Time: {result.total_time_watched_ms}ms")
        if result.reels_total_plays:
            logger.info(f"  Reels Plays (includes replays): {result.reels_total_plays}")
        if result.reels_replay_count:
            logger.info(f"  Replay Count: {result.reels_replay_count}")
        if result.reactions_by_type:
            logger.info(f"  Social Actions: {result.reactions_by_type}")
    else:
        logger.warning("✗ No video insights data returned for direct video ID")

    # Test 2: Videos from database (if any exist)
    repo = CompletedPostRepository()
    logger.info("\n--- Test 2: Fetching Facebook video posts from database ---")
    posts = await repo.get_recent_published_by_platform(business_asset_id, "facebook", limit=20)

    video_posts = [p for p in posts if p.post_type == "facebook_video"]

    if not video_posts:
        logger.info("  No published Facebook video posts found in database (skipping database test)")
    else:
        logger.info(f"✓ Found {len(video_posts)} published Facebook video posts")

        # Test first video from database
        post = video_posts[0]
        logger.info(f"\n--- Testing video from database: {post.platform_post_id} ---")
        logger.info(f"  Text: {post.text[:80]}...")

        result = await fetch_facebook_video_insights(
            business_asset_id=business_asset_id,
            video_id=post.platform_post_id
        )

        if result:
            logger.info("✓ Video insights retrieved:")
            logger.info(f"  Total Views: {result.total_views}")
            logger.info(f"  Unique Reach: {result.unique_views}")
        else:
            logger.warning("✗ No video insights data returned")

    logger.info("\n✓ Facebook Video insights tests complete\n")


async def test_instagram_media_insights(business_asset_id: str):
    """Test Instagram Media insights."""
    logger.info("=" * 80)
    logger.info("TESTING: Instagram Media Insights")
    logger.info("=" * 80)

    repo = CompletedPostRepository()

    # Get recent published Instagram posts
    logger.info("\n--- Fetching published Instagram posts from database ---")
    published_posts = await repo.get_recent_published_by_platform(business_asset_id, "instagram", limit=10)

    if not published_posts:
        logger.warning("✗ No published Instagram posts found")
        logger.info("\n✓ Instagram Media insights tests complete (skipped)\n")
        return

    logger.info(f"✓ Found {len(published_posts)} published Instagram posts")

    # Test different media types
    for post in published_posts[:3]:  # Test up to 3 posts
        media_type = "reel" if "reel" in post.post_type.lower() else "image"

        logger.info(f"\n--- Testing {media_type}: {post.platform_post_id} ---")
        logger.info(f"  Post type: {post.post_type}")
        logger.info(f"  Text: {post.text[:80]}...")

        result = await fetch_instagram_media_insights(
            business_asset_id=business_asset_id,
            media_id=post.platform_post_id,
            media_type=media_type
        )

        if result:
            logger.info(f"✓ {media_type.title()} insights retrieved:")
            logger.info(f"  Reach: {result.reach}")
            logger.info(f"  Views: {result.views}")
            logger.info(f"  Total Interactions: {result.total_interactions}")
            logger.info(f"  Likes: {result.likes}")
            logger.info(f"  Comments: {result.comments}")
            logger.info(f"  Saves: {result.saves}")
            logger.info(f"  Shares: {result.shares}")
            if result.avg_watch_time_ms:
                logger.info(f"  Avg Watch Time: {result.avg_watch_time_ms}ms")
        else:
            logger.warning("✗ No insights data returned")

    logger.info("\n✓ Instagram Media insights tests complete\n")


async def test_instagram_account_insights(business_asset_id: str):
    """Test Instagram Account insights."""
    logger.info("=" * 80)
    logger.info("TESTING: Instagram Account Insights")
    logger.info("=" * 80)

    # Test 1: Last 14 days
    logger.info("\n--- Test 1: Account metrics (last 14 days) ---")
    result = await fetch_instagram_account_insights(
        business_asset_id=business_asset_id,
        days_back=14
    )

    if result:
        logger.info("✓ Account insights retrieved:")
        logger.info(f"  Accounts Engaged: {result.accounts_engaged}")
        logger.info(f"  Total Interactions: {result.total_interactions}")
        logger.info(f"  Reach: {result.reach}")
        logger.info(f"  Views: {result.views}")
        logger.info(f"  Profile Link Taps: {result.profile_link_taps}")
        if result.follows is not None:
            logger.info(f"  Follows: {result.follows}")
        if result.unfollows is not None:
            logger.info(f"  Unfollows: {result.unfollows}")
    else:
        logger.warning("✗ No account insights data returned")

    logger.info("\n✓ Instagram Account insights tests complete\n")


async def test_platform_comments(business_asset_id: str):
    """Test Platform Comments (database)."""
    logger.info("=" * 80)
    logger.info("TESTING: Platform Comments (Database)")
    logger.info("=" * 80)

    # Test 1: Get all comments
    logger.info("\n--- Test 1: Get all comments (limit 10) ---")
    result = await fetch_platform_comments(
        business_asset_id=business_asset_id,
        limit=10
    )
    if result:
        logger.info(f"✓ Got {len(result)} comments")
        for comment in result[:3]:
            text = comment.get('comment_text', '')[:50]
            logger.info(f"  [{comment['platform']}] @{comment['commenter_username']}: {text}...")
            logger.info(f"    Status: {comment['status']}, Likes: {comment['like_count']}")
    else:
        logger.warning("✗ No comments found in database")

    # Test 2: Filter by platform (Facebook)
    logger.info("\n--- Test 2: Filter by platform (Facebook) ---")
    result = await fetch_platform_comments(
        business_asset_id=business_asset_id,
        platform="facebook",
        limit=5
    )
    if result:
        logger.info(f"✓ Got {len(result)} Facebook comments")
        for comment in result[:2]:
            text = comment.get('comment_text', '')[:50]
            logger.info(f"  @{comment['commenter_username']}: {text}...")
    else:
        logger.info("  No Facebook comments found")

    # Test 3: Filter by platform (Instagram)
    logger.info("\n--- Test 3: Filter by platform (Instagram) ---")
    result = await fetch_platform_comments(
        business_asset_id=business_asset_id,
        platform="instagram",
        limit=5
    )
    if result:
        logger.info(f"✓ Got {len(result)} Instagram comments")
        for comment in result[:2]:
            text = comment.get('comment_text', '')[:50]
            logger.info(f"  @{comment['commenter_username']}: {text}...")
    else:
        logger.info("  No Instagram comments found")

    logger.info("\n✓ Platform Comments tests complete\n")


async def test_context_builder(business_asset_id: str):
    """Test the full context builder."""
    logger.info("=" * 80)
    logger.info("TESTING: Insights Context Builder")
    logger.info("=" * 80)

    from backend.services.insights_context_builder import (
        build_insights_context,
        format_context_for_agent,
    )

    logger.info("\n--- Building full insights context ---")
    context = await build_insights_context(business_asset_id)

    logger.info(f"✓ Context built:")
    logger.info(f"  Facebook page insights: {len(context.facebook_page_insights)}")
    logger.info(f"  Instagram account insights: {'Yes' if context.instagram_account_insights else 'No'}")
    logger.info(f"  Facebook posts with metrics: {len(context.facebook_posts)}")
    logger.info(f"  Instagram posts with metrics: {len(context.instagram_posts)}")

    # Format for agent
    formatted = format_context_for_agent(context)
    logger.info(f"\n--- Formatted context preview (first 1000 chars) ---")
    logger.info(formatted[:1000])
    logger.info(f"...\n(Total length: {len(formatted)} characters)")

    logger.info("\n✓ Context Builder tests complete\n")


async def test_error_handling(business_asset_id: str):
    """Test error handling with invalid inputs."""
    logger.info("=" * 80)
    logger.info("TESTING: Error Handling")
    logger.info("=" * 80)

    # Test 1: Invalid Facebook post ID
    logger.info("\n--- Test 1: Invalid Facebook post ID ---")
    result = await fetch_facebook_post_insights(
        business_asset_id=business_asset_id,
        platform_post_id="invalid_post_id_123"
    )
    if result is None:
        logger.info("✓ Correctly returned None for invalid post ID")
    else:
        logger.warning("✗ Expected None but got data")

    # Test 2: Invalid Instagram media ID
    logger.info("\n--- Test 2: Invalid Instagram media ID ---")
    result = await fetch_instagram_media_insights(
        business_asset_id=business_asset_id,
        media_id="invalid_media_123",
        media_type="image"
    )
    if result is None:
        logger.info("✓ Correctly returned None for invalid media ID")
    else:
        logger.warning("✗ Expected None but got data")

    # Test 3: Invalid video ID
    logger.info("\n--- Test 3: Invalid Facebook video ID ---")
    result = await fetch_facebook_video_insights(
        business_asset_id=business_asset_id,
        video_id="invalid_video_123"
    )
    if result is None:
        logger.info("✓ Correctly returned None for invalid video ID")
    else:
        logger.warning("✗ Expected None but got data")

    logger.info("\n✓ Error handling tests complete\n")


async def main():
    """Run all engagement tool tests."""
    import argparse

    parser = argparse.ArgumentParser(description="Test engagement tools")
    parser.add_argument(
        "--business-asset-id",
        default="penndailybuzz",
        help="Business asset ID to test (default: penndailybuzz)"
    )
    parser.add_argument(
        "--test",
        choices=["all", "fb-page", "fb-post", "fb-video", "ig-media", "ig-account", "comments", "context", "errors"],
        default="all",
        help="Which test to run (default: all)"
    )
    args = parser.parse_args()

    business_asset_id = args.business_asset_id

    logger.info("\n" + "=" * 80)
    logger.info("ENGAGEMENT TOOLS INTEGRATION TESTS")
    logger.info("=" * 80)
    logger.info(f"\nConfiguration:")
    logger.info(f"  Business Asset ID: {business_asset_id}")
    logger.info(f"  Test: {args.test}")
    logger.info("\n")

    try:
        if args.test in ["all", "fb-page"]:
            await test_facebook_page_insights(business_asset_id)

        if args.test in ["all", "fb-post"]:
            await test_facebook_post_insights(business_asset_id)

        if args.test in ["all", "fb-video"]:
            await test_facebook_video_insights(business_asset_id)

        if args.test in ["all", "ig-media"]:
            await test_instagram_media_insights(business_asset_id)

        if args.test in ["all", "ig-account"]:
            await test_instagram_account_insights(business_asset_id)

        if args.test in ["all", "comments"]:
            await test_platform_comments(business_asset_id)

        if args.test in ["all", "context"]:
            await test_context_builder(business_asset_id)

        if args.test in ["all", "errors"]:
            await test_error_handling(business_asset_id)

        logger.info("=" * 80)
        logger.info("ALL TESTS COMPLETED ✓")
        logger.info("=" * 80)
        logger.info("\nReview the logs above to verify:")
        logger.info("  - API calls are successful")
        logger.info("  - Data is being parsed correctly")
        logger.info("  - Pydantic models are populated properly")
        logger.info("  - Error handling works as expected")
        logger.info("\n")

    except Exception as e:
        logger.error("Test suite failed", error=str(e), exc_info=True)
        raise


if __name__ == "__main__":
    print('RUNNING ENGAGEMENT TOOLS TESTS')
    asyncio.run(main())
    print("FINISHED")
