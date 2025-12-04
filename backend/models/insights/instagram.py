# backend/models/insights/instagram.py

"""
Instagram insights models for cached metrics.

These models correspond to the database tables and represent
cached engagement data from the Instagram Graph API.
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
from uuid import UUID, uuid4


def utc_now() -> datetime:
    """Get current UTC time in a timezone-aware manner."""
    return datetime.now(timezone.utc)


class InstagramAccountInsights(BaseModel):
    """
    Instagram Account-level insights (cached in database).

    Corresponds to the instagram_account_insights table.
    One row per business asset, updated periodically.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique record ID")
    business_asset_id: str = Field(..., description="Business asset ID")

    # Account metadata
    ig_user_id: str = Field(..., description="Instagram User ID")
    username: Optional[str] = Field(None, description="Instagram username")
    name: Optional[str] = Field(None, description="Display name")
    biography: Optional[str] = Field(None, description="Profile bio")
    profile_picture_url: Optional[str] = Field(None, description="Profile picture URL")

    # Basic counts
    followers_count: int = Field(0, description="Total followers")
    follows_count: int = Field(0, description="Total following")
    media_count: int = Field(0, description="Total media posts")

    # Reach metrics (day, week, days_28)
    reach_day: int = Field(0, description="Daily reach")
    reach_week: int = Field(0, description="Weekly reach")
    reach_days_28: int = Field(0, description="28-day reach")

    # Raw API response
    raw_metrics: Dict[str, Any] = Field(default_factory=dict, description="Full API response")

    # Timestamps
    metrics_fetched_at: datetime = Field(default_factory=utc_now)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    class Config:
        from_attributes = True


class InstagramMediaInsights(BaseModel):
    """
    Instagram Media insights for posts/reels.

    Corresponds to the instagram_media_insights table.
    One row per media, updated when metrics are refreshed.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique record ID")
    business_asset_id: str = Field(..., description="Business asset ID")

    # Media identification
    platform_media_id: str = Field(..., description="Instagram media ID")
    completed_post_id: Optional[UUID] = Field(None, description="Link to completed_posts table")
    media_type: Optional[Literal["image", "video", "carousel", "reel"]] = Field(
        None, description="Type of media"
    )
    permalink: Optional[str] = Field(None, description="Direct link to the post")

    # Feed post metrics (all media types)
    comments: int = Field(0, description="Number of comments")
    likes: int = Field(0, description="Number of likes")
    saved: int = Field(0, description="Number of saves")
    shares: int = Field(0, description="Number of shares")
    views: int = Field(0, description="Times displayed/played")

    # Reel-specific metrics
    ig_reels_avg_watch_time_ms: int = Field(0, description="Average watch time in ms (reels)")
    ig_reels_video_view_total_time_ms: int = Field(0, description="Total watch time in ms (reels)")

    # Raw API response
    raw_metrics: Dict[str, Any] = Field(default_factory=dict, description="Full API response")

    # Timestamps
    metrics_fetched_at: datetime = Field(default_factory=utc_now)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    class Config:
        from_attributes = True

    @property
    def total_interactions(self) -> int:
        """Total interactions (likes + comments + saves + shares)."""
        return self.likes + self.comments + self.saved + self.shares

    @property
    def avg_watch_time_seconds(self) -> float:
        """Average watch time in seconds (for reels)."""
        return self.ig_reels_avg_watch_time_ms / 1000.0

    @property
    def total_watch_time_seconds(self) -> float:
        """Total watch time in seconds (for reels)."""
        return self.ig_reels_video_view_total_time_ms / 1000.0

    @property
    def is_reel(self) -> bool:
        """Check if this is a reel."""
        return self.media_type == "reel" or self.media_type == "video"
