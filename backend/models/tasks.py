# backend/models/tasks.py

"""
Content creation task entity.
Created by the planner agent, consumed by the content creation agent.

Uses unified format-based allocation (image_posts, video_posts, text_only_posts)
rather than platform-specific allocation. Each image/video post creates both
an Instagram and Facebook post using shared or separate media based on config.
"""

from datetime import datetime
from typing import Optional, Literal, List
from pydantic import BaseModel, Field
from uuid import UUID, uuid4


class ContentCreationTask(BaseModel):
    """
    A task for the content creation agent.

    Contains all context needed to create content:
    - Reference to the content seed
    - Format-based post allocations (unified across platforms)
    - Media generation budgets
    - Scheduled posting times
    """

    id: UUID = Field(default_factory=uuid4, description="Unique task ID")
    business_asset_id: str = Field(..., description="Business asset ID for multi-tenancy")

    # Seed references (exactly one must be set for non-failed tasks)
    news_event_seed_id: Optional[UUID] = Field(
        None, description="Foreign key to news_event_seeds table (mutually exclusive)"
    )
    trend_seed_id: Optional[UUID] = Field(
        None, description="Foreign key to trend_seeds table (mutually exclusive)"
    )
    ungrounded_seed_id: Optional[UUID] = Field(
        None, description="Foreign key to ungrounded_seeds table (mutually exclusive)"
    )

    # Format-based post allocations (unified across platforms)
    image_posts: int = Field(
        default=0, ge=0,
        description="Number of image posts (each creates 1 IG image + 1 FB feed post)"
    )
    video_posts: int = Field(
        default=0, ge=0,
        description="Number of video posts (each creates 1 IG reel + 1 FB video post)"
    )
    text_only_posts: int = Field(
        default=0, ge=0,
        description="Number of text-only posts (FB only, no Instagram equivalent)"
    )

    # DEPRECATED: Platform-specific allocations (kept for backwards compatibility)
    instagram_image_posts: Optional[int] = Field(
        None, ge=0, description="DEPRECATED: Use image_posts instead"
    )
    instagram_reel_posts: Optional[int] = Field(
        None, ge=0, description="DEPRECATED: Use video_posts instead"
    )
    facebook_feed_posts: Optional[int] = Field(
        None, ge=0, description="DEPRECATED: Use image_posts instead"
    )
    facebook_video_posts: Optional[int] = Field(
        None, ge=0, description="DEPRECATED: Use video_posts instead"
    )

    # Media budgets
    image_budget: int = Field(default=0, ge=0, description="Max images to generate")
    video_budget: int = Field(default=0, ge=0, description="Max videos to generate")

    # Scheduled posting times (from planner)
    scheduled_times: List[str] = Field(
        default_factory=list,
        description="ISO datetime strings for when to post. One per post unit."
    )

    # Planning context
    week_start_date: Optional[str] = Field(
        None, description="ISO date for the start of the week this task belongs to"
    )

    # Status tracking
    status: Literal["pending", "in_progress", "completed", "failed"] = Field(
        default="pending", description="Current task status"
    )
    error_message: Optional[str] = Field(
        None, description="Error message if status is 'failed'"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When task was created",
    )
    started_at: Optional[datetime] = Field(
        None, description="When content creation started"
    )
    completed_at: Optional[datetime] = Field(
        None, description="When content creation finished"
    )

    @property
    def content_seed_id(self) -> UUID:
        """Get the content seed ID."""
        if self.news_event_seed_id:
            return self.news_event_seed_id
        elif self.trend_seed_id:
            return self.trend_seed_id
        elif self.ungrounded_seed_id:
            return self.ungrounded_seed_id
        else:
            raise ValueError("No content seed ID set")

    @property
    def content_seed_type(self) -> Literal["news_event", "trend", "ungrounded"]:
        """Get the content seed type."""
        if self.news_event_seed_id:
            return "news_event"
        elif self.trend_seed_id:
            return "trend"
        elif self.ungrounded_seed_id:
            return "ungrounded"
        else:
            raise ValueError("No content seed type set")

    @property
    def total_post_units(self) -> int:
        """Total post units (for scheduling - not counting platform duplication)."""
        return self.image_posts + self.video_posts + self.text_only_posts

    @property
    def is_legacy_format(self) -> bool:
        """Check if this task uses the deprecated platform-specific format."""
        return (
            self.instagram_image_posts is not None or
            self.instagram_reel_posts is not None or
            self.facebook_feed_posts is not None or
            self.facebook_video_posts is not None
        )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "b8c9d0e1-f2a3-0b1c-5d6e-7f8a9b0c1d2e",
                "business_asset_id": "penndailybuzz",
                "news_event_seed_id": "b2c3d4e5-f6a7-5b6c-9d0e-1f2a3b4c5d6e",
                "trend_seed_id": None,
                "ungrounded_seed_id": None,
                "image_posts": 2,
                "video_posts": 1,
                "text_only_posts": 0,
                "image_budget": 2,
                "video_budget": 1,
                "scheduled_times": ["2025-01-20T10:00:00Z", "2025-01-21T14:00:00Z", "2025-01-22T18:00:00Z"],
                "status": "pending",
                "error_message": None,
                "created_at": "2025-01-18T17:15:00Z",
                "started_at": None,
                "completed_at": None,
            }
        }
