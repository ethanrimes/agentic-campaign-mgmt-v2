# backend/tools/tests/test_instagram_scraper_manual.py

"""
Manual integration tests for Instagram scraper tools.
Run this directly to test all Instagram scraping endpoints via RapidAPI.
Results are logged to console for manual verification.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import asyncio
from backend.tools.instagram_scraper_tools import (
    GetUserProfileTool,
    GetUserMediaTool,
    SearchUsersTool,
    SearchHashtagsTool,
    SearchLocationsTool,
    GetLocationMediaTool,
    GlobalSearchTool,
    GetHashtagMediaTool,
)
from backend.config.settings import settings
from backend.utils import get_logger

logger = get_logger(__name__)


async def test_get_user_profile():
    """Test getting user profile."""
    logger.info("=" * 80)
    logger.info("TESTING: Get User Profile")
    logger.info("=" * 80)

    tool = GetUserProfileTool()

    # Test with a known Instagram account
    logger.info("\n--- Test 1: Get profile for 'instagram' ---")
    result = await tool._arun(username="instagram")

    if result and "Could not find" not in result:
        logger.info("✓ Successfully retrieved profile")
        logger.info(f"\n{result}\n")
    else:
        logger.warning(f"✗ Failed to retrieve profile: {result}")

    logger.info("\n✓ Get user profile tests complete\n")


async def test_get_user_media():
    """Test getting user media."""
    logger.info("=" * 80)
    logger.info("TESTING: Get User Media")
    logger.info("=" * 80)

    tool = GetUserMediaTool()

    # Test with a known Instagram account
    logger.info("\n--- Test 1: Get recent posts from 'instagram' ---")
    result = await tool._arun(username="instagram", count=5)

    if result and "No posts found" not in result:
        logger.info("✓ Successfully retrieved user media")
        logger.info(f"\n{result}\n")
    else:
        logger.warning(f"✗ Failed to retrieve media: {result}")

    logger.info("\n✓ Get user media tests complete\n")


async def test_search_users():
    """Test searching users."""
    logger.info("=" * 80)
    logger.info("TESTING: Search Users")
    logger.info("=" * 80)

    tool = SearchUsersTool()

    # Test 1: Search for photographers
    logger.info("\n--- Test 1: Search for 'photographer' ---")
    result = await tool._arun(query="photographer")

    if result and "No users found" not in result:
        logger.info("✓ Successfully found users")
        logger.info(f"\n{result}\n")
    else:
        logger.warning(f"✗ No users found: {result}")

    # Test 2: Search for a specific niche
    logger.info("\n--- Test 2: Search for 'coffee' ---")
    result = await tool._arun(query="coffee")

    if result and "No users found" not in result:
        logger.info("✓ Successfully found users")
        logger.info(f"\n{result}\n")
    else:
        logger.warning(f"✗ No users found: {result}")

    logger.info("\n✓ Search users tests complete\n")


async def test_search_hashtags():
    """Test searching hashtags."""
    logger.info("=" * 80)
    logger.info("TESTING: Search Hashtags")
    logger.info("=" * 80)

    tool = SearchHashtagsTool()

    # Test 1: Search for popular hashtag
    logger.info("\n--- Test 1: Search for 'travel' ---")
    result = await tool._arun(query="travel")

    if result and "No hashtags found" not in result:
        logger.info("✓ Successfully found hashtags")
        logger.info(f"\n{result}\n")
    else:
        logger.warning(f"✗ No hashtags found: {result}")

    # Test 2: Search for niche hashtag
    logger.info("\n--- Test 2: Search for 'college' ---")
    result = await tool._arun(query="college")

    if result and "No hashtags found" not in result:
        logger.info("✓ Successfully found hashtags")
        logger.info(f"\n{result}\n")
    else:
        logger.warning(f"✗ No hashtags found: {result}")

    logger.info("\n✓ Search hashtags tests complete\n")


async def test_search_locations():
    """Test searching locations."""
    logger.info("=" * 80)
    logger.info("TESTING: Search Locations")
    logger.info("=" * 80)

    tool = SearchLocationsTool()

    # Test 1: Search for major city
    logger.info("\n--- Test 1: Search for 'new york' ---")
    result = await tool._arun(query="new york")

    if result and "No locations found" not in result:
        logger.info("✓ Successfully found locations")
        logger.info(f"\n{result}\n")
    else:
        logger.warning(f"✗ No locations found: {result}")

    # Test 2: Search for Philadelphia (target audience location)
    logger.info("\n--- Test 2: Search for 'philadelphia' ---")
    result = await tool._arun(query="philadelphia")

    if result and "No locations found" not in result:
        logger.info("✓ Successfully found locations")
        logger.info(f"\n{result}\n")
    else:
        logger.warning(f"✗ No locations found: {result}")

    logger.info("\n✓ Search locations tests complete\n")


async def test_get_location_media():
    """Test getting location media."""
    logger.info("=" * 80)
    logger.info("TESTING: Get Location Media")
    logger.info("=" * 80)

    tool = GetLocationMediaTool()

    # Test with a known location ID (Times Square, New York)
    logger.info("\n--- Test 1: Get media from Times Square (213385402) ---")
    result = await tool._arun(location_id="213385402", count=5)

    if result and "No media found" not in result:
        logger.info("✓ Successfully retrieved location media")
        logger.info(f"\n{result}\n")
    else:
        logger.warning(f"✗ Failed to retrieve media: {result}")

    logger.info("\n✓ Get location media tests complete\n")


async def test_global_search():
    """Test global search."""
    logger.info("=" * 80)
    logger.info("TESTING: Global Search")
    logger.info("=" * 80)

    tool = GlobalSearchTool()

    # Test 1: Search for a popular topic
    logger.info("\n--- Test 1: Global search for 'fitness' ---")
    result = await tool._arun(query="fitness")

    if result and "No results found" not in result:
        logger.info("✓ Successfully performed global search")
        logger.info(f"\n{result}\n")
    else:
        logger.warning(f"✗ No results found: {result}")

    # Test 2: Search for college-related content
    logger.info("\n--- Test 2: Global search for 'university' ---")
    result = await tool._arun(query="university")

    if result and "No results found" not in result:
        logger.info("✓ Successfully performed global search")
        logger.info(f"\n{result}\n")
    else:
        logger.warning(f"✗ No results found: {result}")

    logger.info("\n✓ Global search tests complete\n")


async def test_get_hashtag_media():
    """Test getting hashtag media."""
    logger.info("=" * 80)
    logger.info("TESTING: Get Hashtag Media")
    logger.info("=" * 80)

    tool = GetHashtagMediaTool()

    # Test 1: Get media for popular hashtag
    logger.info("\n--- Test 1: Get media for #travel ---")
    result = await tool._arun(hashtag="travel")

    if result and "No media found" not in result:
        logger.info("✓ Successfully retrieved hashtag media")
        logger.info(f"\n{result}\n")
    else:
        logger.warning(f"✗ Failed to retrieve media: {result}")

    # Test 2: Get media for college hashtag
    logger.info("\n--- Test 2: Get media for #collegelife ---")
    result = await tool._arun(hashtag="collegelife")

    if result and "No media found" not in result:
        logger.info("✓ Successfully retrieved hashtag media")
        logger.info(f"\n{result}\n")
    else:
        logger.warning(f"✗ Failed to retrieve media: {result}")

    logger.info("\n✓ Get hashtag media tests complete\n")


async def test_error_handling():
    """Test error handling with invalid inputs."""
    logger.info("=" * 80)
    logger.info("TESTING: Error Handling")
    logger.info("=" * 80)

    # Test 1: Invalid username
    logger.info("\n--- Test 1: Invalid username ---")
    tool = GetUserProfileTool()
    result = await tool._arun(username="this_username_definitely_does_not_exist_12345")
    if "Could not find" in result or "Error" in result:
        logger.info("✓ Correctly handled invalid username")
    else:
        logger.warning("✗ Did not handle invalid username properly")

    # Test 2: Invalid location ID
    logger.info("\n--- Test 2: Invalid location ID ---")
    tool = GetLocationMediaTool()
    result = await tool._arun(location_id="invalid_location_99999", count=5)
    if "No media found" in result or "Error" in result:
        logger.info("✓ Correctly handled invalid location ID")
    else:
        logger.warning("✗ Did not handle invalid location ID properly")

    logger.info("\n✓ Error handling tests complete\n")


async def main():
    """Run all Instagram scraper tool tests."""
    logger.info("\n" + "=" * 80)
    logger.info("INSTAGRAM SCRAPER TOOLS INTEGRATION TESTS")
    logger.info("=" * 80)
    logger.info(f"\nConfiguration:")
    logger.info(f"  RapidAPI Key: {settings.rapidapi_key[:20]}...")
    logger.info(f"  API Host: instagram-looter2.p.rapidapi.com")
    logger.info("\n")

    try:
        # Run all tests
        await test_get_user_profile()
        await test_get_user_media()
        await test_search_users()
        await test_search_hashtags()
        await test_search_locations()
        await test_get_location_media()
        await test_global_search()
        await test_get_hashtag_media()
        await test_error_handling()

        logger.info("=" * 80)
        logger.info("ALL TESTS COMPLETED SUCCESSFULLY ✓")
        logger.info("=" * 80)
        logger.info("\nReview the logs above to verify:")
        logger.info("  - API calls are successful")
        logger.info("  - Data is being parsed correctly")
        logger.info("  - Pydantic models are populated properly")
        logger.info("  - Error handling works as expected")
        logger.info("  - Response size limits are respected")
        logger.info("\n")

    except Exception as e:
        logger.error("Test suite failed", error=str(e), exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
