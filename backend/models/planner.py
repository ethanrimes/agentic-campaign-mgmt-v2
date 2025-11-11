# backend/models/planner.py

"""
Planner agent output schemas.
Defines the structured output for weekly content planning.
"""

from datetime import datetime
from typing import List, Literal
from pydantic import BaseModel, Field
from uuid import UUID


class ContentSeedAllocation(BaseModel):
    """
    Allocation of posts and media budget for a single content seed.
    """

    seed_id: UUID = Field(..., description="Reference to content seed (any type)")
    seed_type: Literal["news_event", "trend", "ungrounded"] = Field(
        ..., description="Type of content seed"
    )

    # Instagram allocation
    instagram_image_posts: int = Field(
        default=0,
        ge=0,
        description="Number of Instagram image/carousel posts",
    )
    instagram_reel_posts: int = Field(
        default=0,
        ge=0,
        description="Number of Instagram reel posts",
    )

    # Facebook allocation
    facebook_feed_posts: int = Field(
        default=0,
        ge=0,
        description="Number of Facebook feed posts",
    )
    facebook_video_posts: int = Field(
        default=0,
        ge=0,
        description="Number of Facebook video posts",
    )

    # Media budget
    image_budget: int = Field(
        default=0,
        ge=0,
        description="Maximum images that can be generated for this seed",
    )
    video_budget: int = Field(
        default=0,
        ge=0,
        description="Maximum videos that can be generated for this seed",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "seed_id": "b2c3d4e5-f6a7-5b6c-9d0e-1f2a3b4c5d6e",
                "seed_type": "news_event",
                "instagram_image_posts": 2,
                "instagram_reel_posts": 0,
                "facebook_feed_posts": 1,
                "facebook_video_posts": 0,
                "image_budget": 3,
                "video_budget": 0,
            }
        }

    @property
    def total_posts(self) -> int:
        """Total posts allocated for this seed."""
        return (
            self.instagram_image_posts
            + self.instagram_reel_posts
            + self.facebook_feed_posts
            + self.facebook_video_posts
        )


class PlannerOutput(BaseModel):
    """
    Complete weekly content plan from the planner agent.

    This output is validated against guardrails before being accepted.
    If valid, each seed allocation is converted into ContentCreationTasks.
    """

    allocations: List[ContentSeedAllocation] = Field(
        ..., description="List of content seed allocations"
    )
    reasoning: str = Field(
        ...,
        description="Explanation of the plan: why these seeds were chosen, how they align with insights, etc.",
    )
    week_start_date: str = Field(
        ..., description="Start date of the week (ISO 8601 format)"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when plan was created",
    )

    @property
    def total_posts(self) -> int:
        """Total posts across all allocations."""
        return sum(a.total_posts for a in self.allocations)

    @property
    def total_seeds(self) -> int:
        """Total unique content seeds used."""
        return len(self.allocations)

    @property
    def total_images(self) -> int:
        """Total image budget across all allocations."""
        return sum(a.image_budget for a in self.allocations)

    @property
    def total_videos(self) -> int:
        """Total video budget across all allocations."""
        return sum(a.video_budget for a in self.allocations)

    class Config:
        json_schema_extra = {
            "example": {
                "allocations": [],
                "reasoning": "This week's plan focuses on winter campus aesthetics (trending per insights) and SEPTA news (high local relevance). Allocating more Instagram posts due to higher engagement rates. Minimizing video due to recent underperformance.",
                "week_start_date": "2025-01-20",
                "created_at": "2025-01-18T17:00:00Z",
            }
        }
