# backend/database/connection.py

"""
Supabase connection management.
Provides singleton clients for database and storage operations.
"""

from typing import Optional
from supabase import create_client, Client
from backend.config import settings
from backend.utils import get_logger

logger = get_logger(__name__)

# Singleton instances
_client: Optional[Client] = None
_admin_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """
    Get Supabase client with anon/public key.
    Used for standard operations that respect RLS policies.

    Returns:
        Configured Supabase client

    Example:
        ```python
        from backend.database import get_supabase_client

        supabase = get_supabase_client()
        result = supabase.table('news_event_seeds').select('*').execute()
        ```
    """
    global _client

    if _client is None:
        logger.info("Initializing Supabase client", url=settings.supabase_url)
        _client = create_client(settings.supabase_url, settings.supabase_key)

    return _client


def get_supabase_admin_client() -> Client:
    """
    Get Supabase client with service role key.
    Bypasses RLS policies - use with caution!

    Returns:
        Configured Supabase admin client

    Example:
        ```python
        from backend.database import get_supabase_admin_client

        supabase = get_supabase_admin_client()
        # Full access to all tables
        ```
    """
    global _admin_client

    if _admin_client is None:
        logger.info("Initializing Supabase admin client", url=settings.supabase_url)
        _admin_client = create_client(
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
