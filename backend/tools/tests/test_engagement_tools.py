# backend/tools/tests/test_engagement_tools.py

"""
Manual integration tests for engagement tools.
Run this directly to test all Facebook and Instagram insights endpoints.
Results are logged to console for manual verification.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import asyncio
from backend.tools.engagement_tools import (
    GetFacebookPageInsightsTool,
    GetFacebookPostInsightsTool,
    GetFacebookVideoInsightsTool,
    GetInstagramMediaInsightsTool,
    GetInstagramAccountInsightsTool,
)
from backend.database.repositories.completed_posts import CompletedPostRepository
from backend.utils import get_logger

logger = get_logger(__name__)


async def test_facebook_page_insights(business_asset_id: str):
    """Test Facebook Page insights."""
    logger.info("=" * 80)
    logger.info("TESTING: Facebook Page Insights")
    logger.info("=" * 80)

    tool = GetFacebookPageInsightsTool(business_asset_id=business_asset_id)

    # Test 1: Basic page metrics
    logger.info("\n--- Test 1: Page engagements and media views (last 7 days) ---")
    result = await tool._arun(
        business_asset_id=business_asset_id,
        metrics="page_post_engagements,page_media_view",
        period="day",
        days_back=7
    )
    if result:
        logger.info(f"✓ Got {len(result)} data points")
        for insight in result[:3]:  # Show first 3
            logger.info(f"  {insight.name}: {insight.value} (end: {insight.end_time})")
    else:
        logger.warning("✗ No data returned")

    # Test 2: Follows metrics
    logger.info("\n--- Test 2: Page follows (last 7 days) ---")
    result = await tool._arun(
        business_asset_id=business_asset_id,
        metrics="page_daily_follows,page_daily_follows_unique",
        period="day",
        days_back=7
    )
    if result:
        logger.info(f"✓ Got {len(result)} data points")
        for insight in result[:3]:
            logger.info(f"  {insight.name}: {insight.value}")
    else:
        logger.warning("✗ No data returned")

    logger.info("\n✓ Facebook Page insights tests complete\n")


async def test_facebook_post_insights(business_asset_id: str):
    """Test Facebook Post insights."""
    logger.info("=" * 80)
    logger.info("TESTING: Facebook Post Insights")
    logger.info("=" * 80)

    tool = GetFacebookPostInsightsTool(business_asset_id=business_asset_id)
    repo = CompletedPostRepository()

    # Get recent Facebook posts
    logger.info("\n--- Fetching recent Facebook posts from database ---")
    posts = await repo.get_recent_by_platform("facebook", limit=5)

    if not posts:
        logger.warning("✗ No Facebook posts found in database")
        return

    logger.info(f"✓ Found {len(posts)} Facebook posts")

    # Test insights for first published post
    for post in posts:
        if post.status == "published" and post.platform_post_id:
            logger.info(f"\n--- Testing post: {post.platform_post_id} ---")
            logger.info(f"  Text: {post.text[:80]}...")

            result = await tool._arun(business_asset_id=business_asset_id, post_id=post.platform_post_id)

            if result:
                logger.info("✓ Post insights retrieved:")
                logger.info(f"  Likes: {result.reactions_like}")
                logger.info(f"  Loves: {result.reactions_love}")
                logger.info(f"  Wows: {result.reactions_wow}")
                logger.info(f"  Hahas: {result.reactions_haha}")
                logger.info(f"  Media views: {result.media_views}")
                logger.info(f"  All reactions: {result.reactions_by_type}")
            else:
                logger.warning("✗ No insights data returned")

            break  # Only test first post

    logger.info("\n✓ Facebook Post insights tests complete\n")


async def test_facebook_video_insights(business_asset_id: str):
    """Test Facebook Video insights."""
    logger.info("=" * 80)
    logger.info("TESTING: Facebook Video Insights")
    logger.info("=" * 80)

    tool = GetFacebookVideoInsightsTool(business_asset_id=business_asset_id)
    repo = CompletedPostRepository()

    # Get recent Facebook posts with media
    logger.info("\n--- Fetching Facebook posts with media ---")
    posts = await repo.get_recent_by_platform("facebook", limit=20)

    video_posts = [p for p in posts if p.media_ids and p.status == "published"]

    if not video_posts:
        logger.warning("✗ No Facebook video posts found")
        return

    logger.info(f"✓ Found {len(video_posts)} posts with media")

    # Test first video
    for post in video_posts[:1]:
        if post.media_ids:
            video_id = post.media_ids[0]
            logger.info(f"\n--- Testing video: {video_id} ---")

            result = await tool._arun(business_asset_id=business_asset_id, video_id=video_id)

            if result:
                logger.info("✓ Video insights retrieved:")
                logger.info(f"  Total views: {result.total_views}")
                logger.info(f"  Unique views: {result.unique_views}")
                logger.info(f"  Complete views: {result.complete_views}")
                logger.info(f"  Avg watch time: {result.avg_time_watched_ms}ms")
                logger.info(f"  Total watch time: {result.total_time_watched_ms}ms")
                if result.reels_total_plays:
                    logger.info(f"  Reels plays: {result.reels_total_plays}")
            else:
                logger.warning("✗ No video insights data returned")

    logger.info("\n✓ Facebook Video insights tests complete\n")


async def test_instagram_media_insights(business_asset_id: str):
    """Test Instagram Media insights."""
    logger.info("=" * 80)
    logger.info("TESTING: Instagram Media Insights")
    logger.info("=" * 80)

    tool = GetInstagramMediaInsightsTool(business_asset_id=business_asset_id)
    repo = CompletedPostRepository()

    # Get recent Instagram posts
    logger.info("\n--- Fetching Instagram posts from database ---")
    posts = await repo.get_recent_by_platform("instagram", limit=10)

    if not posts:
        logger.warning("✗ No Instagram posts found")
        return

    logger.info(f"✓ Found {len(posts)} Instagram posts")

    # Test different media types
    for post in posts:
        if post.status == "published" and post.platform_post_id:
            media_type = "reel" if "reel" in post.post_type.lower() else "image"

            logger.info(f"\n--- Testing {media_type}: {post.platform_post_id} ---")
            logger.info(f"  Text: {post.text[:80]}...")

            result = await tool._arun(
                business_asset_id=business_asset_id,
                media_id=post.platform_post_id,
                media_type=media_type
            )

            if result:
                logger.info(f"✓ {media_type.title()} insights retrieved:")
                logger.info(f"  Reach: {result.reach}")
                logger.info(f"  Views: {result.views}")
                logger.info(f"  Total interactions: {result.total_interactions}")
                logger.info(f"  Likes: {result.likes}")
                logger.info(f"  Comments: {result.comments}")
                logger.info(f"  Saves: {result.saves}")
                logger.info(f"  Shares: {result.shares}")
                if media_type == "reel":
                    logger.info(f"  Avg watch time: {result.avg_watch_time_ms}ms")
                    logger.info(f"  Total watch time: {result.total_watch_time_ms}ms")
            else:
                logger.warning("✗ No insights data returned")

            # Test 2 posts maximum
            if posts.index(post) >= 1:
                break

    logger.info("\n✓ Instagram Media insights tests complete\n")


async def test_instagram_account_insights(business_asset_id: str):
    """Test Instagram Account insights."""
    logger.info("=" * 80)
    logger.info("TESTING: Instagram Account Insights")
    logger.info("=" * 80)

    tool = GetInstagramAccountInsightsTool(business_asset_id=business_asset_id)

    # Test 1: Last 7 days
    logger.info("\n--- Test 1: Account metrics (last 7 days) ---")
    result = await tool._arun(business_asset_id=business_asset_id, period="day", days_back=7)

    if result:
        logger.info("✓ Account insights retrieved:")
        logger.info(f"  Accounts engaged: {result.accounts_engaged}")
        logger.info(f"  Total interactions: {result.total_interactions}")
        logger.info(f"  Reach: {result.reach}")
        logger.info(f"  Views: {result.views}")
        logger.info(f"  Profile link taps: {result.profile_link_taps}")
    else:
        logger.warning("✗ No account insights data returned")

    # Test 2: Last 28 days
    logger.info("\n--- Test 2: Account metrics (last 28 days) ---")
    result = await tool._arun(business_asset_id=business_asset_id, period="days_28", days_back=28)

    if result:
        logger.info("✓ Account insights retrieved (28-day period):")
        logger.info(f"  Total reach: {result.reach}")
        logger.info(f"  Total views: {result.views}")
    else:
        logger.warning("✗ No account insights data returned")

    logger.info("\n✓ Instagram Account insights tests complete\n")


async def test_error_handling(business_asset_id: str):
    """Test error handling with invalid inputs."""
    logger.info("=" * 80)
    logger.info("TESTING: Error Handling")
    logger.info("=" * 80)

    # Test 1: Invalid post ID
    logger.info("\n--- Test 1: Invalid Facebook post ID ---")
    tool = GetFacebookPostInsightsTool(business_asset_id=business_asset_id)
    result = await tool._arun(business_asset_id=business_asset_id, post_id="invalid_post_id_123")
    if result is None:
        logger.info("✓ Correctly returned None for invalid post ID")
    else:
        logger.warning("✗ Expected None but got data")

    # Test 2: Invalid Instagram media ID
    logger.info("\n--- Test 2: Invalid Instagram media ID ---")
    tool = GetInstagramMediaInsightsTool(business_asset_id=business_asset_id)
    result = await tool._arun(business_asset_id=business_asset_id, media_id="invalid_media_123", media_type="image")
    if result is None:
        logger.info("✓ Correctly returned None for invalid media ID")
    else:
        logger.warning("✗ Expected None but got data")

    logger.info("\n✓ Error handling tests complete\n")


async def main():
    """Run all engagement tool tests."""
    # Default to penndailybuzz for testing
    business_asset_id = "penndailybuzz"

    logger.info("\n" + "=" * 80)
    logger.info("ENGAGEMENT TOOLS INTEGRATION TESTS")
    logger.info("=" * 80)
    logger.info(f"\nConfiguration:")
    logger.info(f"  Business Asset ID: {business_asset_id}")
    logger.info("\n")

    try:
        # Run all tests
        await test_facebook_page_insights(business_asset_id)
        await test_facebook_post_insights(business_asset_id)
        await test_facebook_video_insights(business_asset_id)
        await test_instagram_media_insights(business_asset_id)
        await test_instagram_account_insights(business_asset_id)
        await test_error_handling(business_asset_id)

        logger.info("=" * 80)
        logger.info("ALL TESTS COMPLETED SUCCESSFULLY ✓")
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
    print('RUNNING')
    asyncio.run(main())
    print("FINISHED")
