# backend/models/insights/facebook.py

"""
Facebook insights models for cached metrics.

These models correspond to the database tables and represent
cached engagement data from the Facebook Graph API.
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from uuid import UUID, uuid4


def utc_now() -> datetime:
    """Get current UTC time in a timezone-aware manner."""
    return datetime.now(timezone.utc)


class FacebookPageInsights(BaseModel):
    """
    Facebook Page-level insights (cached in database).

    Corresponds to the facebook_page_insights table.
    One row per business asset, updated periodically.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique record ID")
    business_asset_id: str = Field(..., description="Business asset ID")

    # Page metadata
    page_id: str = Field(..., description="Facebook Page ID")
    page_name: Optional[str] = Field(None, description="Page display name")
    page_picture_url: Optional[str] = Field(None, description="Page profile picture URL")

    # Page views (period: day, week, days_28)
    page_views_total: int = Field(0, description="Daily page views")
    page_views_total_week: int = Field(0, description="Weekly page views")
    page_views_total_days_28: int = Field(0, description="28-day page views")

    # Actions & engagement
    page_total_actions: int = Field(0, description="Daily CTA clicks")
    page_total_actions_days_28: int = Field(0, description="28-day CTA clicks")
    page_post_engagements: int = Field(0, description="Daily post engagements")
    page_post_engagements_week: int = Field(0, description="Weekly post engagements")
    page_post_engagements_days_28: int = Field(0, description="28-day post engagements")

    # Follows
    page_follows: int = Field(0, description="Total page followers")

    # Media views (with optional breakdown)
    page_media_view: int = Field(0, description="Daily media views")
    page_media_view_week: int = Field(0, description="Weekly media views")
    page_media_view_days_28: int = Field(0, description="28-day media views")
    page_media_view_from_followers: int = Field(0, description="Media views from followers")
    page_media_view_from_non_followers: int = Field(0, description="Media views from non-followers")

    # Reactions (daily totals)
    reactions_like_total: int = Field(0, description="Daily like reactions")
    reactions_love_total: int = Field(0, description="Daily love reactions")
    reactions_wow_total: int = Field(0, description="Daily wow reactions")
    reactions_haha_total: int = Field(0, description="Daily haha reactions")
    reactions_sorry_total: int = Field(0, description="Daily sorry/sad reactions")
    reactions_anger_total: int = Field(0, description="Daily anger reactions")

    # Reactions (week)
    reactions_like_week: int = Field(0, description="Weekly like reactions")
    reactions_love_week: int = Field(0, description="Weekly love reactions")
    reactions_wow_week: int = Field(0, description="Weekly wow reactions")
    reactions_haha_week: int = Field(0, description="Weekly haha reactions")
    reactions_sorry_week: int = Field(0, description="Weekly sorry/sad reactions")
    reactions_anger_week: int = Field(0, description="Weekly anger reactions")

    # Video views
    page_video_views: int = Field(0, description="Daily video views")
    page_video_views_week: int = Field(0, description="Weekly video views")
    page_video_views_days_28: int = Field(0, description="28-day video views")

    # Raw API response
    raw_metrics: Dict[str, Any] = Field(default_factory=dict, description="Full API response")

    # Timestamps
    metrics_fetched_at: datetime = Field(default_factory=utc_now)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    class Config:
        from_attributes = True


class FacebookPostInsights(BaseModel):
    """
    Facebook Post-level insights for feed posts/photos.

    Corresponds to the facebook_post_insights table.
    One row per post, updated when metrics are refreshed.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique record ID")
    business_asset_id: str = Field(..., description="Business asset ID")

    # Post identification
    platform_post_id: str = Field(..., description="Facebook post ID")
    completed_post_id: Optional[UUID] = Field(None, description="Link to completed_posts table")

    # Post-level metrics
    post_media_view: int = Field(0, description="Times content was displayed")
    post_media_view_from_followers: int = Field(0, description="Views from followers")
    post_media_view_from_non_followers: int = Field(0, description="Views from non-followers")

    post_impressions_unique: int = Field(0, description="Unique accounts reached")
    post_impressions_organic_unique: int = Field(0, description="Organic reach")

    # Reactions
    reactions_like: int = Field(0, description="Like reactions")
    reactions_love: int = Field(0, description="Love reactions")
    reactions_wow: int = Field(0, description="Wow reactions")
    reactions_haha: int = Field(0, description="Haha reactions")
    reactions_sorry: int = Field(0, description="Sorry/sad reactions")
    reactions_anger: int = Field(0, description="Anger reactions")
    reactions_by_type: Dict[str, int] = Field(default_factory=dict, description="All reactions by type")

    # Raw API response
    raw_metrics: Dict[str, Any] = Field(default_factory=dict, description="Full API response")

    # Timestamps
    metrics_fetched_at: datetime = Field(default_factory=utc_now)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    class Config:
        from_attributes = True

    @property
    def total_reactions(self) -> int:
        """Total reaction count."""
        return (
            self.reactions_like
            + self.reactions_love
            + self.reactions_wow
            + self.reactions_haha
            + self.reactions_sorry
            + self.reactions_anger
        )


class FacebookVideoInsights(BaseModel):
    """
    Facebook Video/Reel insights.

    Corresponds to the facebook_video_insights table.
    One row per video, updated when metrics are refreshed.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique record ID")
    business_asset_id: str = Field(..., description="Business asset ID")

    # Video identification
    platform_video_id: str = Field(..., description="Facebook video ID")
    completed_post_id: Optional[UUID] = Field(None, description="Link to completed_posts table")

    # Video metrics
    post_video_views: int = Field(0, description="3s+ video views")
    post_video_views_unique: int = Field(0, description="Unique viewers (3s+)")
    post_video_view_time_ms: int = Field(0, description="Total watch time in ms")
    post_video_avg_time_watched_ms: int = Field(0, description="Average watch time in ms")
    post_video_length_ms: int = Field(0, description="Video duration in ms")

    # Raw API response
    raw_metrics: Dict[str, Any] = Field(default_factory=dict, description="Full API response")

    # Timestamps
    metrics_fetched_at: datetime = Field(default_factory=utc_now)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    class Config:
        from_attributes = True

    @property
    def avg_watch_time_seconds(self) -> float:
        """Average watch time in seconds."""
        return self.post_video_avg_time_watched_ms / 1000.0

    @property
    def total_watch_time_seconds(self) -> float:
        """Total watch time in seconds."""
        return self.post_video_view_time_ms / 1000.0

    @property
    def video_length_seconds(self) -> float:
        """Video length in seconds."""
        return self.post_video_length_ms / 1000.0
