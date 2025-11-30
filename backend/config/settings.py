# backend/config/settings.py

"""
Central configuration management for the social media agent framework.
Loads all settings from environment variables and provides typed access.
"""

import os
from typing import Literal, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from cryptography.fernet import Fernet


class Settings(BaseSettings):
    """
    Main settings class for the application.
    All settings are loaded from environment variables.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # =============================================================================
    # REQUIRED SETTINGS
    # =============================================================================

    # Supabase
    supabase_url: str
    supabase_key: str
    supabase_service_key: str
    supabase_db_url: Optional[str] = None

    # Encryption
    encryption_key: str

    # OpenAI (default provider)
    openai_api_key: str

    # Meta (Facebook/Instagram) - Shared app credentials
    # Note: Per-asset credentials (page IDs, access tokens) are stored in Supabase
    meta_app_id: str
    meta_app_secret: str

    # Wavespeed AI
    wavespeed_api_key: str

    # RapidAPI
    rapidapi_key: str

    # =============================================================================
    # OPTIONAL SETTINGS (with defaults)
    # =============================================================================

    # Additional AI providers
    gemini_api_key: Optional[str] = None
    perplexity_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None

    # Model configuration
    default_model_provider: Literal["openai", "gemini", "anthropic"] = "openai"
    default_model_name: str = "gpt-5-mini"

    # Content generation guardrails
    min_posts_per_week: int = 10
    max_posts_per_week: int = 20
    min_content_seeds_per_week: int = 8
    max_content_seeds_per_week: int = 15
    min_videos_per_week: int = 2
    max_videos_per_week: int = 10
    min_images_per_week: int = 10
    max_images_per_week: int = 30

    # Wavespeed configuration
    wavespeed_image_model: str = "bytedance/seedream-v4"
    wavespeed_video_model: str = "bytedance/seedance-v1-pro-t2v-480p"
    wavespeed_api_base: str = "https://api.wavespeed.ai/api/v3"
    wavespeed_polling_interval: float = 2.0
    wavespeed_max_poll_attempts: int = 120

    # Planner context limits (how many recent seeds to fetch for planning)
    planner_news_seeds_limit: int = 10
    planner_trend_seeds_limit: int = 10
    planner_ungrounded_seeds_limit: int = 10

    # Deduplicator configuration (how many recent canonical seeds to compare against)
    deduplicator_canonical_seeds_limit: int = 10

    # Publishing
    publishing_check_interval: int = 6  # hours

    # Logging
    log_level: str = "INFO"

    # =============================================================================
    # COMPUTED PROPERTIES
    # =============================================================================

    @property
    def fernet(self) -> Fernet:
        """Get Fernet cipher for encryption/decryption."""
        return Fernet(self.encryption_key.encode())

    def decrypt_token(self, encrypted_token: str) -> str:
        """Decrypt an encrypted token."""
        return self.fernet.decrypt(encrypted_token.encode()).decode()

    def encrypt_token(self, token: str) -> str:
        """Encrypt a token."""
        return self.fernet.encrypt(token.encode()).decode()

    def get_model_api_key(self, provider: Optional[str] = None) -> str:
        """
        Get API key for the specified provider.
        Falls back to default_model_provider if provider is None.
        """
        provider = provider or self.default_model_provider

        if provider == "openai":
            return self.openai_api_key
        elif provider == "gemini":
            if not self.gemini_api_key:
                raise ValueError("GEMINI_API_KEY not set")
            return self.gemini_api_key
        elif provider == "anthropic":
            if not self.anthropic_api_key:
                raise ValueError("ANTHROPIC_API_KEY not set")
            return self.anthropic_api_key
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def get_business_asset_credentials(self, business_asset_id: str):
        """
        Get decrypted credentials for a business asset.

        Args:
            business_asset_id: The unique identifier for the business asset

        Returns:
            BusinessAssetCredentials with decrypted tokens

        Raises:
            ValueError: If business asset not found
        """
        from backend.config.business_asset_loader import get_business_asset_credentials
        return get_business_asset_credentials(business_asset_id)


# Singleton instance
settings = Settings()
