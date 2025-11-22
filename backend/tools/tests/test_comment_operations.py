# backend/tools/tests/test_comment_operations.py

"""
Manual integration tests for comment operations.
Run this directly to test Facebook and Instagram comment operations.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import asyncio
from backend.services.meta.comment_operations import CommentOperations
from backend.config.settings import settings
from backend.utils import get_logger

logger = get_logger(__name__)


async def test_facebook_operations():
    """Test Facebook comment operations."""
    logger.info("=" * 80)
    logger.info("TESTING: Facebook Comment Operations")
    logger.info("=" * 80)

    ops = CommentOperations()

    # You'll need to replace these with actual IDs from your Facebook page
    # Get these from running: python -m backend.cli.main publish facebook --limit 1
    test_post_id = input("\nEnter a Facebook post ID to test (or press Enter to skip): ").strip()

    if not test_post_id:
        logger.info("Skipping Facebook tests (no post ID provided)")
        return

    # Test 1: Get post context
    logger.info("\n--- Test 1: Get Facebook Post Context ---")
    try:
        post_context = await ops.get_facebook_post_context(test_post_id)
        logger.info(f"✓ Retrieved post context")
        logger.info(f"  Message: {post_context.get('message', 'N/A')[:100]}...")
        logger.info(f"  Created: {post_context.get('created_time', 'N/A')}")
    except Exception as e:
        logger.error(f"✗ Failed to get post context: {e}")

    # Test 2: Get post comments
    logger.info("\n--- Test 2: Get Facebook Post Comments ---")
    try:
        comments = await ops.get_facebook_post_comments(test_post_id)
        logger.info(f"✓ Retrieved {len(comments)} comments")
        for i, comment in enumerate(comments[:3], 1):
            logger.info(f"  Comment {i}:")
            logger.info(f"    From: {comment.get('from', {}).get('name', 'Unknown')}")
            logger.info(f"    Text: {comment.get('message', 'N/A')[:60]}...")
            logger.info(f"    ID: {comment.get('id')}")
    except Exception as e:
        logger.error(f"✗ Failed to get comments: {e}")

    # Test 3: Get specific comment details
    if comments and len(comments) > 0:
        logger.info("\n--- Test 3: Get Facebook Comment Details ---")
        test_comment_id = comments[0].get('id')
        try:
            comment_details = await ops.get_facebook_comment_details(test_comment_id)
            logger.info(f"✓ Retrieved comment details")
            logger.info(f"  Comment ID: {comment_details.get('id')}")
            logger.info(f"  Text: {comment_details.get('message', 'N/A')}")
            logger.info(f"  Like count: {comment_details.get('like_count', 0)}")
        except Exception as e:
            logger.error(f"✗ Failed to get comment details: {e}")


async def test_instagram_operations():
    """Test Instagram comment operations."""
    logger.info("\n" + "=" * 80)
    logger.info("TESTING: Instagram Comment Operations")
    logger.info("=" * 80)

    ops = CommentOperations()

    # Test 1: Get media list
    logger.info("\n--- Test 1: Get Instagram Media List ---")
    try:
        media_list = await ops.get_instagram_media_list()
        logger.info(f"✓ Retrieved {len(media_list)} media items")
        if media_list:
            test_media_id = media_list[0].get('id')
            logger.info(f"  Using media ID for tests: {test_media_id}")
        else:
            logger.warning("  No media found")
            return
    except Exception as e:
        logger.error(f"✗ Failed to get media list: {e}")
        return

    # Test 2: Get media context
    logger.info("\n--- Test 2: Get Instagram Media Context ---")
    try:
        media_context = await ops.get_instagram_media_context(test_media_id)
        logger.info(f"✓ Retrieved media context")
        logger.info(f"  Caption: {media_context.get('caption', 'N/A')[:100]}...")
        logger.info(f"  Media type: {media_context.get('media_type', 'N/A')}")
        logger.info(f"  Permalink: {media_context.get('permalink', 'N/A')}")
    except Exception as e:
        logger.error(f"✗ Failed to get media context: {e}")

    # Test 3: Get media comments
    logger.info("\n--- Test 3: Get Instagram Media Comments ---")
    try:
        comments = await ops.get_instagram_media_comments(test_media_id)
        logger.info(f"✓ Retrieved {len(comments)} comments")
        for i, comment in enumerate(comments[:3], 1):
            logger.info(f"  Comment {i}:")
            logger.info(f"    From: @{comment.get('username', 'Unknown')}")
            logger.info(f"    Text: {comment.get('text', 'N/A')[:60]}...")
            logger.info(f"    ID: {comment.get('id')}")
            replies = comment.get('replies', {}).get('data', [])
            if replies:
                logger.info(f"    Replies: {len(replies)}")
    except Exception as e:
        logger.error(f"✗ Failed to get comments: {e}")

    # Test 4: Get specific comment details
    if comments and len(comments) > 0:
        logger.info("\n--- Test 4: Get Instagram Comment Details ---")
        test_comment_id = comments[0].get('id')
        try:
            comment_details = await ops.get_instagram_comment_details(test_comment_id)
            logger.info(f"✓ Retrieved comment details")
            logger.info(f"  Comment ID: {comment_details.get('id')}")
            logger.info(f"  Text: {comment_details.get('text', 'N/A')}")
            logger.info(f"  Like count: {comment_details.get('like_count', 0)}")
            logger.info(f"  Hidden: {comment_details.get('hidden', False)}")
        except Exception as e:
            logger.error(f"✗ Failed to get comment details: {e}")


async def test_instagram_comment_checker():
    """Test the Instagram comment checker service."""
    logger.info("\n" + "=" * 80)
    logger.info("TESTING: Instagram Comment Checker Service")
    logger.info("=" * 80)

    from backend.services.meta.instagram_comment_checker import check_instagram_comments

    logger.info("\n--- Running Instagram comment check (max 5 media) ---")
    try:
        result = await check_instagram_comments(max_media=5)
        logger.info(f"✓ Comment check completed")
        logger.info(f"  Success: {result.get('success')}")
        logger.info(f"  Media checked: {result.get('media_checked', 0)}")
        logger.info(f"  Comments found: {result.get('comments_found', 0)}")
        logger.info(f"  New comments added: {result.get('new_comments_added', 0)}")
        if result.get('errors'):
            logger.warning(f"  Errors: {len(result['errors'])}")
    except Exception as e:
        logger.error(f"✗ Failed to check comments: {e}")


async def test_comment_responder():
    """Test the comment responder agent."""
    logger.info("\n" + "=" * 80)
    logger.info("TESTING: Comment Responder Agent")
    logger.info("=" * 80)

    from backend.database.repositories.platform_comments import PlatformCommentRepository
    from backend.agents.comment_responder import CommentResponderAgent

    repo = PlatformCommentRepository()

    # Get a pending comment to test with
    logger.info("\n--- Getting pending comments ---")
    try:
        pending = await repo.get_pending_comments(limit=1)
        if not pending:
            logger.info("  No pending comments found. Run comment check first.")
            return

        test_comment = pending[0]
        logger.info(f"✓ Found pending comment")
        logger.info(f"  Platform: {test_comment.platform}")
        logger.info(f"  Commenter: @{test_comment.commenter_username}")
        logger.info(f"  Text: {test_comment.comment_text}")

        # Generate response
        logger.info("\n--- Generating response ---")
        agent = CommentResponderAgent()
        response = await agent.generate_response(test_comment)

        if response:
            logger.info(f"✓ Generated response:")
            logger.info(f"\n{'=' * 60}")
            logger.info(response)
            logger.info(f"{'=' * 60}\n")
            logger.info(f"  Response length: {len(response)} characters")
        else:
            logger.info("  No response generated (comment may be filtered)")

    except Exception as e:
        logger.error(f"✗ Failed to test comment responder: {e}")


async def main():
    """Run all tests."""
    logger.info("\n" + "#" * 80)
    logger.info("COMMENT OPERATIONS TEST SUITE")
    logger.info("#" * 80)

    # Test Facebook operations
    await test_facebook_operations()

    # Test Instagram operations
    await test_instagram_operations()

    # Test Instagram comment checker
    await test_instagram_comment_checker()

    # Test comment responder
    await test_comment_responder()

    logger.info("\n" + "#" * 80)
    logger.info("ALL TESTS COMPLETED")
    logger.info("#" * 80)


if __name__ == "__main__":
    asyncio.run(main())
