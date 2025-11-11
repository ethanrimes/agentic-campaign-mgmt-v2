# backend/config/guardrails_config.py

"""
Guardrails configuration for the planner agent.
Defines min/max constraints for weekly content planning.
"""

from typing import Dict
from pydantic import BaseModel, Field
from .settings import settings


class GuardrailsConfig(BaseModel):
    """
    Defines the guardrails (constraints) for weekly content planning.

    These constraints ensure:
    1. Content volume is sustainable and consistent
    2. Resource allocation (images/videos) is within budget
    3. Content diversity through minimum seed requirements

    The planner agent's output must satisfy all these constraints,
    or it will be rejected and regenerated.
    """

    min_posts_per_week: int = Field(
        default_factory=lambda: settings.min_posts_per_week,
        description="Minimum total posts across all platforms"
    )
    max_posts_per_week: int = Field(
        default_factory=lambda: settings.max_posts_per_week,
        description="Maximum total posts across all platforms"
    )

    min_content_seeds_per_week: int = Field(
        default_factory=lambda: settings.min_content_seeds_per_week,
        description="Minimum unique content seeds to use"
    )
    max_content_seeds_per_week: int = Field(
        default_factory=lambda: settings.max_content_seeds_per_week,
        description="Maximum unique content seeds to use"
    )

    min_videos_per_week: int = Field(
        default_factory=lambda: settings.min_videos_per_week,
        description="Minimum video content pieces"
    )
    max_videos_per_week: int = Field(
        default_factory=lambda: settings.max_videos_per_week,
        description="Maximum video content pieces"
    )

    min_images_per_week: int = Field(
        default_factory=lambda: settings.min_images_per_week,
        description="Minimum image content pieces"
    )
    max_images_per_week: int = Field(
        default_factory=lambda: settings.max_images_per_week,
        description="Maximum image content pieces"
    )

    def to_dict(self) -> Dict[str, int]:
        """Convert guardrails to dictionary for easy access."""
        return {
            "min_posts_per_week": self.min_posts_per_week,
            "max_posts_per_week": self.max_posts_per_week,
            "min_content_seeds_per_week": self.min_content_seeds_per_week,
            "max_content_seeds_per_week": self.max_content_seeds_per_week,
            "min_videos_per_week": self.min_videos_per_week,
            "max_videos_per_week": self.max_videos_per_week,
            "min_images_per_week": self.min_images_per_week,
            "max_images_per_week": self.max_images_per_week,
        }

    def __str__(self) -> str:
        """Human-readable representation of guardrails."""
        return f"""Content Guardrails:
  Posts: {self.min_posts_per_week}-{self.max_posts_per_week} per week
  Content Seeds: {self.min_content_seeds_per_week}-{self.max_content_seeds_per_week} per week
  Videos: {self.min_videos_per_week}-{self.max_videos_per_week} per week
  Images: {self.min_images_per_week}-{self.max_images_per_week} per week"""


# Singleton instance
guardrails_config = GuardrailsConfig()
