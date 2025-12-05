# backend/models/posts.py

"""
Completed post entity.
Created by the content creation agent, published by the publishers.
"""

from datetime import datetime, timezone
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from uuid import UUID, uuid4


class CompletedPost(BaseModel):
    """
    A completed social media post ready for or already published.

    Created by the content creation agent and consumed by publishers.
    Includes all media, text, and metadata needed for posting.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique post ID")
    business_asset_id: str = Field(..., description="Business asset ID for multi-tenancy")

    # Task reference
    task_id: UUID = Field(
        ..., description="ID of the content creation task that produced this post"
    )

    # Content seed references (exactly one must be set)
    news_event_seed_id: Optional[UUID] = Field(
        None, description="Foreign key to news_event_seeds table (mutually exclusive)"
    )
    trend_seed_id: Optional[UUID] = Field(
        None, description="Foreign key to trend_seeds table (mutually exclusive)"
    )
    ungrounded_seed_id: Optional[UUID] = Field(
        None, description="Foreign key to ungrounded_seeds table (mutually exclusive)"
    )

    # Platform and type
    platform: Literal["facebook", "instagram"] = Field(
        ..., description="Target platform"
    )
    post_type: Literal[
        "instagram_image",
        "instagram_carousel",
        "instagram_reel",
        "instagram_story",
        "facebook_feed",
        "facebook_video",
    ] = Field(..., description="Specific post type")

    # Content
    text: str = Field(..., description="Post caption/text (may include embedded links)")
    media_ids: List[UUID] = Field(
        default_factory=list,
        description="List of media IDs referencing the media table (empty for text-only posts)",
    )

    # Optional metadata
    location: Optional[str] = Field(
        None, description="Location tag (if applicable)"
    )
    music: Optional[str] = Field(
        None, description="Music/audio for reels/stories (if applicable)"
    )
    hashtags: List[str] = Field(
        default_factory=list, description="Hashtags to include"
    )

    # Publishing status
    status: Literal["pending", "published", "failed"] = Field(
        default="pending", description="Publishing status"
    )
    verification_status: Literal["unverified", "verified", "rejected", "manually_overridden"] = Field(
        default="unverified",
        description="Content verification status: unverified (not yet checked), verified (approved), rejected (failed verification), manually_overridden (rejected but manually approved)"
    )
    scheduled_posting_time: Optional[datetime] = Field(
        None, description="When this post should be published (NULL means publish immediately)"
    )

    # Verification group support (for cross-platform media sharing)
    verification_group_id: Optional[UUID] = Field(
        None,
        description="Groups posts that share media for unified verification. NULL means standalone post."
    )
    is_verification_primary: bool = Field(
        default=True,
        description="TRUE = this post will be verified. FALSE = inherits verification from primary post in group."
    )
    published_at: Optional[datetime] = Field(
        None, description="When the post was published to the platform"
    )
    platform_post_id: Optional[str] = Field(
        None, description="Post ID from Facebook/Instagram (after publishing)"
    )
    platform_video_id: Optional[str] = Field(
        None, description="Video ID from Facebook/Instagram for video posts (reels, videos). Used to fetch video-specific insights."
    )
    platform_post_url: Optional[HttpUrl] = Field(
        None, description="URL to the published post (if available)"
    )
    error_message: Optional[str] = Field(
        None, description="Error message if publishing failed"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the post was created by content creation agent",
    )

    @property
    def content_seed_id(self) -> UUID:
        """Get the content seed ID (for backwards compatibility)."""
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
        """Get the content seed type (for backwards compatibility)."""
        if self.news_event_seed_id:
            return "news_event"
        elif self.trend_seed_id:
            return "trend"
        elif self.ungrounded_seed_id:
            return "ungrounded"
        else:
            raise ValueError("No content seed type set")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "c9d0e1f2-a3b4-1c2d-6e7f-8a9b0c1d2e3f",
                "business_asset_id": "penndailybuzz",
                "task_id": "b8c9d0e1-f2a3-0b1c-5d6e-7f8a9b0c1d2e",
                "news_event_seed_id": "b2c3d4e5-f6a7-5b6c-9d0e-1f2a3b4c5d6e",
                "trend_seed_id": None,
                "ungrounded_seed_id": None,
                "platform": "instagram",
                "post_type": "instagram_image",
                "text": "SEPTA fare increase coming in March 🚊💰 What does this mean for Penn students? Check out our breakdown. #SEPTA #UPenn #Philadelphia #Transit",
                "media_ids": [
                    "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d"
                ],
                "location": "Philadelphia, Pennsylvania",
                "music": None,
                "hashtags": ["SEPTA", "UPenn", "Philadelphia", "Transit"],
                "status": "pending",
                "scheduled_posting_time": "2025-01-19T10:00:00Z",
                "published_at": None,
                "platform_post_id": None,
                "platform_post_url": None,
                "error_message": None,
                "created_at": "2025-01-18T18:30:00Z",
            }
        }
    )
