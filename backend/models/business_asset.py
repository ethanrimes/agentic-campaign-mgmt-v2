# backend/models/business_asset.py

"""
Business Asset model for multi-tenant support.

A business asset represents a Facebook + Instagram page combination,
with associated credentials and metadata.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class BusinessAssetCredentials(BaseModel):
    """Decrypted credentials for a business asset."""
    facebook_page_id: str
    app_users_instagram_account_id: str
    facebook_page_access_token: str
    instagram_page_access_token: str
    target_audience: str


class BusinessAsset(BaseModel):
    """
    Business asset with encrypted credentials.

    This model represents a business asset as stored in the database,
    with encrypted access tokens.
    """
    id: str = Field(..., description="Unique identifier (e.g., 'penndailybuzz')")
    name: str = Field(..., description="Display name for the business asset")

    # Platform identifiers (not sensitive)
    facebook_page_id: str
    app_users_instagram_account_id: str

    # Encrypted access tokens
    facebook_page_access_token_encrypted: str
    instagram_page_access_token_encrypted: str

    # Target audience (plain text)
    target_audience: str = Field(..., description="Description of the target audience for content creation")

    # Status
    is_active: bool = True

    # Timestamps
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BusinessAssetCreate(BaseModel):
    """Model for creating a new business asset (with unencrypted tokens)."""
    id: str = Field(..., description="Unique identifier (e.g., 'penndailybuzz')")
    name: str = Field(..., description="Display name for the business asset")

    # Platform identifiers
    facebook_page_id: str
    app_users_instagram_account_id: str

    # Unencrypted access tokens (will be encrypted before storage)
    facebook_page_access_token: str
    instagram_page_access_token: str

    # Target audience (plain text)
    target_audience: str = Field(..., description="Description of the target audience for content creation")

    # Status
    is_active: bool = True


class BusinessAssetUpdate(BaseModel):
    """Model for updating a business asset."""
    name: Optional[str] = None
    facebook_page_id: Optional[str] = None
    app_users_instagram_account_id: Optional[str] = None
    facebook_page_access_token: Optional[str] = None  # Will be encrypted if provided
    instagram_page_access_token: Optional[str] = None  # Will be encrypted if provided
    target_audience: Optional[str] = None
    is_active: Optional[bool] = None
