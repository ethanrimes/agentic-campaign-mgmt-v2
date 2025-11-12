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

    # Meta (Facebook/Instagram)
    meta_app_id: str
    meta_app_secret: str
    facebook_page_id: str
    instagram_business_account_id: str
    facebook_page_access_token: str
    instagram_page_access_token: str

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
    default_model_name: str = "gpt-4o-mini"

    # Target audience (the north star for all agents)
    target_audience: str = "College students at the University of Pennsylvania interested in campus news, events, and local culture"

    # Content generation guardrails
    min_posts_per_week: int = 3
    max_posts_per_week: int = 15
    min_content_seeds_per_week: int = 2
    max_content_seeds_per_week: int = 8
    min_videos_per_week: int = 0
    max_videos_per_week: int = 5
    min_images_per_week: int = 1
    max_images_per_week: int = 20

    # Wavespeed configuration
    wavespeed_image_model: str = "stability-ai/sdxl-lora"
    wavespeed_video_model: str = "wavespeed-ai/wan-2.2/i2v-5b-720p"
    wavespeed_api_base: str = "https://api.wavespeed.ai/api/v3"
    wavespeed_polling_interval: float = 2.0
    wavespeed_max_poll_attempts: int = 120

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


# Singleton instance
settings = Settings()
