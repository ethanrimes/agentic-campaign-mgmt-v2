# backend/tools/tests/test_knowledge_base_tools.py

"""
Manual integration test for knowledge base tools.
Run this script directly to test the tools and inspect the output.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
import asyncio
from backend.tools.knowledge_base_tools import (
    SearchNewsEventsTool,
    GetRecentSeedsTool,
    GetLatestInsightsTool,
)
from backend.utils import get_logger

logger = get_logger(__name__)


async def test_search_news_events():
    """Test searching for news events."""
    logger.info("=" * 80)
    logger.info("Testing SearchNewsEventsTool")
    logger.info("=" * 80)

    tool = SearchNewsEventsTool()

    # Test 1: Search with broad query
    logger.info("\n--- Test 1: Search for 'Philadelphia' ---")
    result = await tool._arun(query="Philadelphia", limit=5)
    logger.info(f"Result:\n{result}\n")

    # Test 2: Search for something that doesn't exist
    logger.info("--- Test 2: Search for non-existent event ---")
    result = await tool._arun(query="ThisEventDefinitelyDoesNotExist12345", limit=5)
    logger.info(f"Result:\n{result}\n")

    logger.info("SearchNewsEventsTool tests completed ✓\n")


async def test_get_recent_seeds():
    """Test getting recent seeds."""
    logger.info("=" * 80)
    logger.info("Testing GetRecentSeedsTool")
    logger.info("=" * 80)

    tool = GetRecentSeedsTool()

    # Test news seeds
    logger.info("\n--- Test 1: Get recent news seeds ---")
    result = await tool._arun(seed_type="news", limit=5)
    logger.info(f"Result:\n{result}\n")

    # Test trend seeds
    logger.info("--- Test 2: Get recent trend seeds ---")
    result = await tool._arun(seed_type="trend", limit=5)
    logger.info(f"Result:\n{result}\n")

    # Test ungrounded seeds
    logger.info("--- Test 3: Get recent ungrounded seeds ---")
    result = await tool._arun(seed_type="ungrounded", limit=5)
    logger.info(f"Result:\n{result}\n")

    # Test invalid type
    logger.info("--- Test 4: Invalid seed type ---")
    result = await tool._arun(seed_type="invalid", limit=5)
    logger.info(f"Result:\n{result}\n")

    logger.info("GetRecentSeedsTool tests completed ✓\n")


async def test_get_latest_insights():
    """Test getting latest insights."""
    logger.info("=" * 80)
    logger.info("Testing GetLatestInsightsTool")
    logger.info("=" * 80)

    tool = GetLatestInsightsTool()

    logger.info("\n--- Test 1: Get latest insights ---")
    result = await tool._arun()
    logger.info(f"Result:\n{result}\n")

    logger.info("GetLatestInsightsTool tests completed ✓\n")


async def test_concurrent_execution():
    """Test concurrent tool execution."""
    logger.info("=" * 80)
    logger.info("Testing Concurrent Execution")
    logger.info("=" * 80)

    search_tool = SearchNewsEventsTool()
    seeds_tool = GetRecentSeedsTool()
    insights_tool = GetLatestInsightsTool()

    logger.info("\n--- Running all tools concurrently ---")

    results = await asyncio.gather(
        search_tool._arun(query="event", limit=3),
        seeds_tool._arun(seed_type="news", limit=3),
        insights_tool._arun(),
        return_exceptions=True
    )

    logger.info("Search result:")
    logger.info(results[0])
    logger.info("\nSeeds result:")
    logger.info(results[1])
    logger.info("\nInsights result:")
    logger.info(results[2])

    logger.info("\nConcurrent execution tests completed ✓\n")


async def main():
    """Run all tests."""
    logger.info("\n" + "=" * 80)
    logger.info("KNOWLEDGE BASE TOOLS INTEGRATION TESTS")
    logger.info("=" * 80 + "\n")

    try:
        await test_search_news_events()
        await test_get_recent_seeds()
        await test_get_latest_insights()
        await test_concurrent_execution()

        logger.info("=" * 80)
        logger.info("ALL TESTS COMPLETED SUCCESSFULLY ✓")
        logger.info("=" * 80)
    except Exception as e:
        logger.error("Test failed", error=str(e), exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
