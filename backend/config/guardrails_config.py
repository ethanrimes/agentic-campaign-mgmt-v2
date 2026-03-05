# backend/config/guardrails_config.py

"""
Guardrails configuration for the planner agent.
Defines min/max constraints for daily content planning (24-hour window).
"""

from typing import Dict
from pydantic import BaseModel, Field
from .settings import settings


class GuardrailsConfig(BaseModel):
    """
    Defines the guardrails (constraints) for daily content planning.

    These constraints ensure:
    1. Content volume is sustainable and consistent
    2. Resource allocation (images/videos) is within budget
    3. Content diversity through minimum seed requirements

    The planner agent's output must satisfy all these constraints,
    or it will be rejected and regenerated.
    """

    min_posts_per_day: int = Field(
        default_factory=lambda: settings.min_posts_per_day,
        description="Minimum total posts across all platforms per day"
    )
    max_posts_per_day: int = Field(
        default_factory=lambda: settings.max_posts_per_day,
        description="Maximum total posts across all platforms per day"
    )

    min_content_seeds_per_day: int = Field(
        default_factory=lambda: settings.min_content_seeds_per_day,
        description="Minimum unique content seeds to use per day"
    )
    max_content_seeds_per_day: int = Field(
        default_factory=lambda: settings.max_content_seeds_per_day,
        description="Maximum unique content seeds to use per day"
    )

    min_videos_per_day: int = Field(
        default_factory=lambda: settings.min_videos_per_day,
        description="Minimum video content pieces per day"
    )
    max_videos_per_day: int = Field(
        default_factory=lambda: settings.max_videos_per_day,
        description="Maximum video content pieces per day"
    )

    min_images_per_day: int = Field(
        default_factory=lambda: settings.min_images_per_day,
        description="Minimum image content pieces per day"
    )
    max_images_per_day: int = Field(
        default_factory=lambda: settings.max_images_per_day,
        description="Maximum image content pieces per day"
    )

    def to_dict(self) -> Dict[str, int]:
        """Convert guardrails to dictionary for easy access."""
        return {
            "min_posts_per_day": self.min_posts_per_day,
            "max_posts_per_day": self.max_posts_per_day,
            "min_content_seeds_per_day": self.min_content_seeds_per_day,
            "max_content_seeds_per_day": self.max_content_seeds_per_day,
            "min_videos_per_day": self.min_videos_per_day,
            "max_videos_per_day": self.max_videos_per_day,
            "min_images_per_day": self.min_images_per_day,
            "max_images_per_day": self.max_images_per_day,
        }

    def __str__(self) -> str:
        """Human-readable representation of guardrails."""
        return f"""Content Guardrails (daily):
  Posts: {self.min_posts_per_day}-{self.max_posts_per_day} per day
  Content Seeds: {self.min_content_seeds_per_day}-{self.max_content_seeds_per_day} per day
  Videos: {self.min_videos_per_day}-{self.max_videos_per_day} per day
  Images: {self.min_images_per_day}-{self.max_images_per_day} per day"""


# Singleton instance
guardrails_config = GuardrailsConfig()
