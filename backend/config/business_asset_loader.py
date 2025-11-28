# backend/config/business_asset_loader.py

"""
Business asset credential loader with caching.

This module provides functionality to load and cache business asset credentials
from Supabase. Credentials are decrypted on load and cached in memory for
performance.
"""

from typing import Dict, Optional
from backend.models.business_asset import BusinessAssetCredentials
from backend.utils import get_logger

logger = get_logger(__name__)

# Global cache for business asset credentials
_credentials_cache: Dict[str, BusinessAssetCredentials] = {}


def get_business_asset_credentials(business_asset_id: str) -> BusinessAssetCredentials:
    """
    Get decrypted credentials for a business asset.

    Credentials are cached in memory after first load for performance.
    To reload credentials (e.g., after token refresh), call clear_credentials_cache().

    Args:
        business_asset_id: The unique identifier for the business asset

    Returns:
        BusinessAssetCredentials with decrypted tokens

    Raises:
        ValueError: If business asset not found or credentials are invalid
    """
    # Check cache first
    if business_asset_id in _credentials_cache:
        logger.debug(f"Using cached credentials for: {business_asset_id}")
        return _credentials_cache[business_asset_id]

    # Load from database
    logger.info(f"Loading credentials from database for: {business_asset_id}")

    # Import here to avoid circular dependency
    from backend.database.repositories.business_assets import BusinessAssetRepository

    repo = BusinessAssetRepository()
    credentials = repo.get_credentials(business_asset_id)

    if not credentials:
        raise ValueError(f"Business asset not found: {business_asset_id}")

    # Cache for future use
    _credentials_cache[business_asset_id] = credentials

    logger.info(f"Loaded and cached credentials for: {business_asset_id}")
    return credentials


def clear_credentials_cache(business_asset_id: Optional[str] = None) -> None:
    """
    Clear the credentials cache.

    Args:
        business_asset_id: If provided, clear only this asset's credentials.
                          If None, clear all cached credentials.
    """
    global _credentials_cache

    if business_asset_id:
        if business_asset_id in _credentials_cache:
            del _credentials_cache[business_asset_id]
            logger.info(f"Cleared credentials cache for: {business_asset_id}")
    else:
        _credentials_cache = {}
        logger.info("Cleared all credentials cache")


def preload_all_active_credentials() -> None:
    """
    Preload credentials for all active business assets into cache.

    This can be called at application startup to avoid lazy loading delays.
    """
    from backend.database.repositories.business_assets import BusinessAssetRepository

    repo = BusinessAssetRepository()
    active_assets = repo.get_all_active()

    logger.info(f"Preloading credentials for {len(active_assets)} active business assets")

    for asset in active_assets:
        try:
            get_business_asset_credentials(asset.id)
        except Exception as e:
            logger.error(f"Failed to preload credentials for {asset.id}", error=str(e))

    logger.info(f"Preloaded {len(_credentials_cache)} business asset credentials")
