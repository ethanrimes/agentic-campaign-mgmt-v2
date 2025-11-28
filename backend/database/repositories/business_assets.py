# backend/database/repositories/business_assets.py

"""
Repository for managing business assets with encrypted credentials.

Business assets represent Facebook + Instagram page combinations,
each with their own credentials stored encrypted in the database.
"""

from typing import List, Optional
from datetime import datetime
from backend.database.connection import get_supabase_sync_client
from backend.models.business_asset import (
    BusinessAsset,
    BusinessAssetCreate,
    BusinessAssetUpdate,
    BusinessAssetCredentials
)
from backend.config.settings import settings
from backend.utils import get_logger

logger = get_logger(__name__)


class BusinessAssetRepository:
    """Repository for business asset CRUD operations with encryption support."""

    def __init__(self):
        self.client = get_supabase_sync_client()
        self.table = "business_assets"

    def get_by_id(self, business_asset_id: str) -> Optional[BusinessAsset]:
        """
        Get a business asset by ID.

        Args:
            business_asset_id: The unique identifier for the business asset

        Returns:
            BusinessAsset if found, None otherwise
        """
        response = self.client.table(self.table).select("*").eq("id", business_asset_id).execute()

        if not response.data:
            logger.warning(f"Business asset not found: {business_asset_id}")
            return None

        return BusinessAsset(**response.data[0])

    def get_all_active(self) -> List[BusinessAsset]:
        """
        Get all active business assets.

        Returns:
            List of active business assets
        """
        response = self.client.table(self.table).select("*").eq("is_active", True).execute()
        return [BusinessAsset(**row) for row in response.data]

    def get_all(self) -> List[BusinessAsset]:
        """
        Get all business assets (active and inactive).

        Returns:
            List of all business assets
        """
        response = self.client.table(self.table).select("*").execute()
        return [BusinessAsset(**row) for row in response.data]

    def create(self, business_asset: BusinessAssetCreate) -> BusinessAsset:
        """
        Create a new business asset with encrypted credentials.

        Args:
            business_asset: The business asset to create (with unencrypted tokens)

        Returns:
            Created business asset
        """
        # Encrypt the access tokens before storage
        encrypted_data = {
            "id": business_asset.id,
            "name": business_asset.name,
            "facebook_page_id": business_asset.facebook_page_id,
            "app_users_instagram_account_id": business_asset.app_users_instagram_account_id,
            "facebook_page_access_token_encrypted": settings.encrypt_token(
                business_asset.facebook_page_access_token
            ),
            "instagram_page_access_token_encrypted": settings.encrypt_token(
                business_asset.instagram_page_access_token
            ),
            "target_audience": business_asset.target_audience,
            "is_active": business_asset.is_active,
        }

        response = self.client.table(self.table).insert(encrypted_data).execute()

        logger.info(f"Created business asset: {business_asset.id}")
        return BusinessAsset(**response.data[0])

    def update(self, business_asset_id: str, update: BusinessAssetUpdate) -> Optional[BusinessAsset]:
        """
        Update a business asset.

        Args:
            business_asset_id: The ID of the business asset to update
            update: The fields to update

        Returns:
            Updated business asset if found, None otherwise
        """
        # Build update dict, encrypting tokens if provided
        update_data = {}

        if update.name is not None:
            update_data["name"] = update.name
        if update.facebook_page_id is not None:
            update_data["facebook_page_id"] = update.facebook_page_id
        if update.app_users_instagram_account_id is not None:
            update_data["app_users_instagram_account_id"] = update.app_users_instagram_account_id
        if update.facebook_page_access_token is not None:
            update_data["facebook_page_access_token_encrypted"] = settings.encrypt_token(
                update.facebook_page_access_token
            )
        if update.instagram_page_access_token is not None:
            update_data["instagram_page_access_token_encrypted"] = settings.encrypt_token(
                update.instagram_page_access_token
            )
        if update.target_audience is not None:
            update_data["target_audience"] = update.target_audience
        if update.is_active is not None:
            update_data["is_active"] = update.is_active

        if not update_data:
            logger.warning(f"No fields to update for business asset: {business_asset_id}")
            return self.get_by_id(business_asset_id)

        update_data["updated_at"] = datetime.now().isoformat()

        response = (
            self.client.table(self.table)
            .update(update_data)
            .eq("id", business_asset_id)
            .execute()
        )

        if not response.data:
            logger.warning(f"Business asset not found for update: {business_asset_id}")
            return None

        logger.info(f"Updated business asset: {business_asset_id}")
        return BusinessAsset(**response.data[0])

    def delete(self, business_asset_id: str) -> bool:
        """
        Delete a business asset.

        Args:
            business_asset_id: The ID of the business asset to delete

        Returns:
            True if deleted, False if not found
        """
        response = self.client.table(self.table).delete().eq("id", business_asset_id).execute()

        if not response.data:
            logger.warning(f"Business asset not found for deletion: {business_asset_id}")
            return False

        logger.info(f"Deleted business asset: {business_asset_id}")
        return True

    def get_credentials(self, business_asset_id: str) -> Optional[BusinessAssetCredentials]:
        """
        Get decrypted credentials for a business asset.

        Args:
            business_asset_id: The ID of the business asset

        Returns:
            Decrypted credentials if found, None otherwise
        """
        business_asset = self.get_by_id(business_asset_id)

        if not business_asset:
            return None

        # Decrypt the tokens
        return BusinessAssetCredentials(
            facebook_page_id=business_asset.facebook_page_id,
            app_users_instagram_account_id=business_asset.app_users_instagram_account_id,
            facebook_page_access_token=settings.decrypt_token(
                business_asset.facebook_page_access_token_encrypted
            ),
            instagram_page_access_token=settings.decrypt_token(
                business_asset.instagram_page_access_token_encrypted
            ),
            target_audience=business_asset.target_audience,
        )
