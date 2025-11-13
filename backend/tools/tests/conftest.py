# backend/tools/tests/conftest.py

"""
Pytest configuration and shared fixtures for integration tests.
These tests use real APIs and database connections.
"""

import pytest
import os
from datetime import datetime, timezone
from uuid import uuid4

from backend.database import get_supabase_client
from backend.database.repositories.news_event_seeds import NewsEventSeedRepository
from backend.database.repositories.trend_seeds import TrendSeedsRepository
from backend.database.repositories.ungrounded_seeds import UngroundedSeedRepository
from backend.database.repositories.insights import InsightsRepository
from backend.database.repositories.media import MediaRepository
from backend.config import settings


# Skip markers for tests requiring specific credentials
pytestmark = pytest.mark.asyncio


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test (requires real APIs)"
    )
    config.addinivalue_line(
        "markers", "requires_meta: mark test as requiring Meta API credentials"
    )
    config.addinivalue_line(
        "markers", "requires_rapidapi: mark test as requiring RapidAPI credentials"
    )
    config.addinivalue_line(
        "markers", "requires_wavespeed: mark test as requiring Wavespeed API credentials"
    )


def has_meta_credentials():
    """Check if Meta API credentials are available."""
    return all([
        settings.meta_app_id,
        settings.meta_app_secret,
        settings.facebook_page_id,
        settings.facebook_page_access_token,
    ])


def has_rapidapi_credentials():
    """Check if RapidAPI credentials are available."""
    return bool(settings.rapidapi_key)


def has_wavespeed_credentials():
    """Check if Wavespeed credentials are available."""
    return bool(settings.wavespeed_api_key)


# Skip decorators for conditional test execution
skip_if_no_meta = pytest.mark.skipif(
    not has_meta_credentials(),
    reason="Meta API credentials not configured"
)

skip_if_no_rapidapi = pytest.mark.skipif(
    not has_rapidapi_credentials(),
    reason="RapidAPI credentials not configured"
)

skip_if_no_wavespeed = pytest.mark.skipif(
    not has_wavespeed_credentials(),
    reason="Wavespeed API credentials not configured"
)


@pytest.fixture
async def db_client():
    """
    Provide Supabase database client.

    Yields:
        AsyncClient: Configured Supabase client
    """
    client = await get_supabase_client()
    yield client


@pytest.fixture
async def test_news_seed(db_client):
    """
    Create a test news event seed and clean up after test.

    Yields:
        NewsEventSeed: Created test seed
    """
    # Create test seed with correct schema
    seed_data = {
        "id": str(uuid4()),
        "name": "Integration Test Event",
        "location": "Philadelphia",
        "description": "This is a test event created for integration testing purposes",
        "sources": [],  # Empty list of sources
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    # Insert directly using client
    result = await db_client.table("news_event_seeds").insert(seed_data).execute()
    seed_id = result.data[0]["id"]

    yield result.data[0]

    # Cleanup
    await db_client.table("news_event_seeds").delete().eq("id", seed_id).execute()


@pytest.fixture
async def test_trend_seed(db_client):
    """
    Create a test trend seed and clean up after test.

    Yields:
        TrendSeed: Created test seed
    """
    seed_data = {
        "id": str(uuid4()),
        "name": "Integration Test Trend",
        "description": "Test trend for integration testing",
        "hashtags": [],
        "posts": [],
        "users": [],
        "created_by": "pytest",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    result = await db_client.table("trend_seeds").insert(seed_data).execute()
    seed_id = result.data[0]["id"]

    yield result.data[0]

    # Cleanup
    await db_client.table("trend_seeds").delete().eq("id", seed_id).execute()


@pytest.fixture
async def test_ungrounded_seed(db_client):
    """
    Create a test ungrounded seed and clean up after test.

    Yields:
        UngroundedSeed: Created test seed
    """
    seed_data = {
        "id": str(uuid4()),
        "idea": "Integration Test Ungrounded Idea",
        "format": "text",
        "created_by": "pytest",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    result = await db_client.table("ungrounded_seeds").insert(seed_data).execute()
    seed_id = result.data[0]["id"]

    yield result.data[0]

    # Cleanup
    await db_client.table("ungrounded_seeds").delete().eq("id", seed_id).execute()


@pytest.fixture
async def test_insight_report(db_client):
    """
    Create a test insights report and clean up after test.

    Yields:
        InsightReport: Created test report
    """
    report_data = {
        "id": str(uuid4()),
        "summary": "Integration Test Insights Summary",
        "findings": "Test findings for integration testing purposes",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    result = await db_client.table("insight_reports").insert(report_data).execute()
    report_id = result.data[0]["id"]

    yield result.data[0]

    # Cleanup
    await db_client.table("insight_reports").delete().eq("id", report_id).execute()


@pytest.fixture
async def cleanup_generated_media(db_client):
    """
    Fixture to clean up any media generated during tests.
    Use this as a finalizer for tests that generate media.

    Usage:
        async def test_generate_image(cleanup_generated_media):
            media_ids = cleanup_generated_media
            # ... test code that generates media ...
            media_ids.append(created_media_id)
    """
    media_ids_to_cleanup = []

    yield media_ids_to_cleanup

    # Cleanup after test
    if media_ids_to_cleanup:
        for media_id in media_ids_to_cleanup:
            try:
                await db_client.table("media").delete().eq("id", media_id).execute()
            except Exception:
                pass  # Ignore cleanup errors


@pytest.fixture(scope="session")
def test_page_id():
    """Provide Facebook Page ID for testing."""
    return settings.facebook_page_id


@pytest.fixture(scope="session")
def test_instagram_id():
    """Provide Instagram Business Account ID for testing."""
    return settings.app_users_instagram_account_id
