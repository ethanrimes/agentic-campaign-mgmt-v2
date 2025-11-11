# backend/database/connection.py

"""
Supabase connection management.
Provides singleton async clients for database and storage operations.
"""

from typing import Optional
from supabase import acreate_client, AsyncClient
from backend.config import settings
from backend.utils import get_logger

logger = get_logger(__name__)

# Singleton instances
_client: Optional[AsyncClient] = None
_admin_client: Optional[AsyncClient] = None


async def get_supabase_client() -> AsyncClient:
    """
    Get async Supabase client with anon/public key.
    Used for standard operations that respect RLS policies.

    Returns:
        Configured async Supabase client

    Example:
        ```python
        from backend.database import get_supabase_client

        supabase = await get_supabase_client()
        result = await supabase.table('news_event_seeds').select('*').execute()
        ```
    """
    global _client

    if _client is None:
        logger.info("Initializing async Supabase client", url=settings.supabase_url)
        _client = await acreate_client(settings.supabase_url, settings.supabase_key)

    return _client


async def get_supabase_admin_client() -> AsyncClient:
    """
    Get async Supabase client with service role key.
    Bypasses RLS policies - use with caution!

    Returns:
        Configured async Supabase admin client

    Example:
        ```python
        from backend.database import get_supabase_admin_client

        supabase = await get_supabase_admin_client()
        # Full access to all tables
        ```
    """
    global _admin_client

    if _admin_client is None:
        logger.info("Initializing async Supabase admin client", url=settings.supabase_url)
        _admin_client = await acreate_client(
            settings.supabase_url, settings.supabase_service_key
        )

    return _admin_client


def reset_connections():
    """
    Reset connection singletons.
    Useful for testing or when credentials change.
    """
    global _client, _admin_client
    _client = None
    _admin_client = None
    logger.info("Reset Supabase connections")
