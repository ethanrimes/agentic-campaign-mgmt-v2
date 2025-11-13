# backend/tools/tests/test_facebook_scraper_manual.py

"""
Manual test script for Facebook scraper tools.
Run this to test the Facebook scraper implementation.

Usage:
    python -m backend.tools.tests.test_facebook_scraper_manual
"""

import asyncio
from backend.tools.facebook_scraper_tools import create_facebook_scraper_tools
from backend.utils import get_logger

logger = get_logger(__name__)


async def test_search_pages():
    """Test searching for Facebook pages."""
    logger.info("Testing search_facebook_pages")
    tools = create_facebook_scraper_tools()
    search_pages_tool = next(t for t in tools if t.name == "search_facebook_pages")

    result = await search_pages_tool._arun(query="beer")
    print("\n" + "="*80)
    print("SEARCH PAGES TEST")
    print("="*80)
    print(result)
    print("="*80 + "\n")


async def test_search_posts():
    """Test searching for Facebook posts."""
    logger.info("Testing search_facebook_posts")
    tools = create_facebook_scraper_tools()
    search_posts_tool = next(t for t in tools if t.name == "search_facebook_posts")

    result = await search_posts_tool._arun(query="facebook")
    print("\n" + "="*80)
    print("SEARCH POSTS TEST")
    print("="*80)
    print(result)
    print("="*80 + "\n")


async def test_search_events():
    """Test searching for Facebook events."""
    logger.info("Testing search_facebook_events")
    tools = create_facebook_scraper_tools()
    search_events_tool = next(t for t in tools if t.name == "search_facebook_events")

    result = await search_events_tool._arun(query="beer")
    print("\n" + "="*80)
    print("SEARCH EVENTS TEST")
    print("="*80)
    print(result)
    print("="*80 + "\n")


async def test_search_places():
    """Test searching for Facebook places."""
    logger.info("Testing search_facebook_places")
    tools = create_facebook_scraper_tools()
    search_places_tool = next(t for t in tools if t.name == "search_facebook_places")

    result = await search_places_tool._arun(query="pizza")
    print("\n" + "="*80)
    print("SEARCH PLACES TEST")
    print("="*80)
    print(result)
    print("="*80 + "\n")


async def test_page_details():
    """Test getting Facebook page details."""
    logger.info("Testing get_facebook_page_details")
    tools = create_facebook_scraper_tools()
    page_details_tool = next(t for t in tools if t.name == "get_facebook_page_details")

    # Test with Facebook's official page
    result = await page_details_tool._arun(page_url="https://www.facebook.com/facebook")
    print("\n" + "="*80)
    print("PAGE DETAILS TEST")
    print("="*80)
    print(result)
    print("="*80 + "\n")


async def test_page_posts():
    """Test getting posts from a Facebook page."""
    logger.info("Testing get_facebook_page_posts")
    tools = create_facebook_scraper_tools()
    page_posts_tool = next(t for t in tools if t.name == "get_facebook_page_posts")

    # Using Facebook's official page ID
    result = await page_posts_tool._arun(page_id="100064860875397", limit=5)
    print("\n" + "="*80)
    print("PAGE POSTS TEST")
    print("="*80)
    print(result)
    print("="*80 + "\n")


async def test_event_details():
    """Test getting Facebook event details."""
    logger.info("Testing get_facebook_event_details")
    tools = create_facebook_scraper_tools()
    event_details_tool = next(t for t in tools if t.name == "get_facebook_event_details")

    # Note: You'll need to find a valid event ID to test this
    # This is a placeholder - replace with an actual event ID
    result = await event_details_tool._arun(event_id="1259800548576578")
    print("\n" + "="*80)
    print("EVENT DETAILS TEST")
    print("="*80)
    print(result)
    print("="*80 + "\n")


async def run_all_tests():
    """Run all Facebook scraper tests."""
    print("\n" + "="*80)
    print("FACEBOOK SCRAPER TOOLS TEST SUITE")
    print("="*80 + "\n")

    tests = [
        ("Search Pages", test_search_pages),
        ("Search Posts", test_search_posts),
        ("Search Events", test_search_events),
        ("Search Places", test_search_places),
        ("Page Details", test_page_details),
        ("Page Posts", test_page_posts),
        ("Event Details", test_event_details),
    ]

    for test_name, test_func in tests:
        try:
            logger.info(f"Running test: {test_name}")
            await test_func()
            logger.info(f"✓ Test passed: {test_name}")
        except Exception as e:
            logger.error(f"✗ Test failed: {test_name}", error=str(e))
            print(f"\nError in {test_name}: {str(e)}\n")

    print("\n" + "="*80)
    print("TEST SUITE COMPLETED")
    print("="*80 + "\n")


async def test_quick():
    """Quick test with just one API call."""
    logger.info("Running quick test")
    tools = create_facebook_scraper_tools()
    page_details_tool = next(t for t in tools if t.name == "get_facebook_page_details")

    result = await page_details_tool._arun(page_url="https://www.facebook.com/facebook")
    print("\n" + "="*80)
    print("QUICK TEST: Page Details")
    print("="*80)
    print(result)
    print("="*80 + "\n")


if __name__ == "__main__":
    # Uncomment the test you want to run:

    # Run all tests (will make multiple API calls)
    asyncio.run(run_all_tests())

    # Run individual tests
    # asyncio.run(test_search_pages())
    # asyncio.run(test_search_posts())
    # asyncio.run(test_search_events())
    # asyncio.run(test_search_places())
    # asyncio.run(test_page_details())
    # asyncio.run(test_page_posts())
    # asyncio.run(test_event_details())

    # Quick single test
    # asyncio.run(test_quick())
