# backend/models/planner.py

"""
Planner agent output schemas.
Defines the structured output for weekly content planning.

Uses unified format-based allocation (image_posts, video_posts, text_only_posts)
rather than platform-specific allocation. Each image/video post creates both
an Instagram and Facebook post using shared or separate media based on config.
"""

from datetime import datetime
from typing import List, Literal
from pydantic import BaseModel, Field
from uuid import UUID


class ContentSeedAllocation(BaseModel):
    """
    Allocation of posts and media budget for a single content seed.

    Uses unified format-based allocation:
    - image_posts: Each creates 1 IG image + 1 FB feed post (2 posts total)
    - video_posts: Each creates 1 IG reel + 1 FB video post (2 posts total)
    - carousel_posts: Each creates 1 IG carousel + 1 FB carousel (2 posts total, multiple images)
    - text_only_posts: FB-only text posts (no Instagram equivalent)

    Note: text_only_posts should only be used in allocations where
    image_posts=0, video_posts=0, and carousel_posts=0 (separate seed allocations).
    """

    seed_id: UUID = Field(..., description="Reference to content seed (any type)")
    seed_type: Literal["news_event", "trend", "ungrounded"] = Field(
        ..., description="Type of content seed"
    )

    # Format-based allocation (unified across platforms)
    image_posts: int = Field(
        default=0,
        ge=0,
        description="Number of image posts (each creates 1 IG image + 1 FB feed post)",
    )
    video_posts: int = Field(
        default=0,
        ge=0,
        description="Number of video posts (each creates 1 IG reel + 1 FB video post)",
    )
    carousel_posts: int = Field(
        default=0,
        ge=0,
        description="Number of carousel posts (each creates 1 IG carousel + 1 FB carousel with 2-10 images)",
    )
    text_only_posts: int = Field(
        default=0,
        ge=0,
        description="Number of text-only posts (FB only, no Instagram equivalent)",
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

    # Scheduled posting times (planner decides these)
    scheduled_times: List[str] = Field(
        default_factory=list,
        description="ISO datetime strings for when to post. One per post unit.",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "seed_id": "b2c3d4e5-f6a7-5b6c-9d0e-1f2a3b4c5d6e",
                "seed_type": "news_event",
                "image_posts": 2,
                "video_posts": 1,
                "carousel_posts": 1,
                "text_only_posts": 0,
                "image_budget": 6,
                "video_budget": 1,
                "scheduled_times": ["2025-01-20T10:00:00Z", "2025-01-21T14:00:00Z", "2025-01-22T18:00:00Z", "2025-01-23T12:00:00Z"],
            }
        }

    @property
    def total_posts(self) -> int:
        """Total posts allocated for this seed (counting both platforms)."""
        # Each image/video/carousel post creates 2 posts (IG + FB)
        # text_only creates 1 post (FB only)
        return (self.image_posts * 2) + (self.video_posts * 2) + (self.carousel_posts * 2) + self.text_only_posts

    @property
    def total_post_units(self) -> int:
        """Total post units (for scheduling purposes - not counting platform duplication)."""
        return self.image_posts + self.video_posts + self.carousel_posts + self.text_only_posts


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
        """Total posts across all allocations (counting both platforms)."""
        return sum(a.total_posts for a in self.allocations)

    @property
    def total_post_units(self) -> int:
        """Total post units (for scheduling - not counting platform duplication)."""
        return sum(a.total_post_units for a in self.allocations)

    @property
    def total_seeds(self) -> int:
        """Total unique content seeds used."""
        return len(self.allocations)

    @property
    def total_image_posts(self) -> int:
        """Total image post units across all allocations."""
        return sum(a.image_posts for a in self.allocations)

    @property
    def total_video_posts(self) -> int:
        """Total video post units across all allocations."""
        return sum(a.video_posts for a in self.allocations)

    @property
    def total_carousel_posts(self) -> int:
        """Total carousel post units across all allocations."""
        return sum(a.carousel_posts for a in self.allocations)

    @property
    def total_text_only_posts(self) -> int:
        """Total text-only posts across all allocations."""
        return sum(a.text_only_posts for a in self.allocations)

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
                "reasoning": "This week's plan focuses on winter campus aesthetics (trending per insights) and SEPTA news (high local relevance). Using unified format to share media across platforms for efficiency.",
                "week_start_date": "2025-01-20",
                "created_at": "2025-01-18T17:00:00Z",
            }
        }
