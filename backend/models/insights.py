# backend/models/insights.py

"""
Insight report entities for the insights agent.
Tracks what content works and doesn't work with the audience.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
from uuid import UUID, uuid4


# ============================================================================
# FACEBOOK INSIGHTS MODELS
# ============================================================================

class FacebookPageInsight(BaseModel):
    """Single page-level metric value."""
    name: str = Field(..., description="Metric name")
    period: str = Field(..., description="Period (day, week, days_28, etc.)")
    title: str = Field(..., description="Human-readable title")
    description: str = Field(..., description="Metric description")
    value: int | Dict[str, Any] = Field(..., description="Metric value (number or breakdown object)")
    end_time: datetime = Field(..., description="End time of the metric period")


class FacebookPostInsight(BaseModel):
    """Post/photo-level engagement metrics."""
    post_id: str = Field(..., description="Facebook post ID")
    reactions_like: int = Field(0, description="Total like reactions")
    reactions_love: int = Field(0, description="Total love reactions")
    reactions_wow: int = Field(0, description="Total wow reactions")
    reactions_haha: int = Field(0, description="Total haha reactions")
    reactions_sorry: int = Field(0, description="Total sorry reactions")
    reactions_anger: int = Field(0, description="Total anger reactions")
    reactions_by_type: Dict[str, int] = Field(default_factory=dict, description="All reactions by type")
    media_views: Optional[int] = Field(None, description="Post media views")


class FacebookVideoInsight(BaseModel):
    """Video/Reel-level metrics."""
    video_id: str = Field(..., description="Facebook video ID")
    total_views: int = Field(0, description="Total video views")
    unique_views: int = Field(0, description="Unique video views")
    autoplayed_views: int = Field(0, description="Autoplayed views")
    clicked_to_play_views: int = Field(0, description="Clicked to play views")
    organic_views: int = Field(0, description="Organic views")
    paid_views: int = Field(0, description="Paid views")
    complete_views: int = Field(0, description="Complete views (100%)")
    complete_views_unique: int = Field(0, description="Unique complete views")
    avg_time_watched_ms: int = Field(0, description="Average watch time in milliseconds")
    total_time_watched_ms: int = Field(0, description="Total watch time in milliseconds")
    # Reels-specific
    reels_total_plays: Optional[int] = Field(None, description="FB Reels total plays")
    reels_replay_count: Optional[int] = Field(None, description="FB Reels replay count")


# ============================================================================
# INSTAGRAM INSIGHTS MODELS
# ============================================================================

class InstagramMediaInsight(BaseModel):
    """Instagram media (post/reel/story) insights."""
    media_id: str = Field(..., description="Instagram media ID")
    media_type: Literal["image", "video", "carousel", "reel", "story"] = Field(..., description="Type of media")
    reach: int = Field(0, description="Unique accounts reached")
    views: int = Field(0, description="Total views/displays")
    total_interactions: int = Field(0, description="Total interactions (likes + comments + saves + shares)")
    likes: int = Field(0, description="Likes count")
    comments: int = Field(0, description="Comments count")
    saves: int = Field(0, description="Saves count")
    shares: int = Field(0, description="Shares count")
    profile_activity: int = Field(0, description="Profile actions taken after viewing")
    # Reels-specific
    avg_watch_time_ms: Optional[int] = Field(None, description="Average watch time in milliseconds (Reels)")
    total_watch_time_ms: Optional[int] = Field(None, description="Total watch time in milliseconds (Reels)")


class InstagramAccountInsight(BaseModel):
    """Instagram account-level metrics."""
    accounts_engaged: int = Field(0, description="Accounts that engaged with content")
    total_interactions: int = Field(0, description="Total interactions across all content")
    reach: int = Field(0, description="Total unique accounts reached")
    reach_by_type: Dict[str, int] = Field(default_factory=dict, description="Reach broken down by media type")
    views: int = Field(0, description="Total views across all content")
    views_by_type: Dict[str, int] = Field(default_factory=dict, description="Views broken down by media type")
    profile_link_taps: int = Field(0, description="Profile link taps")
    follower_count: Optional[int] = Field(None, description="Current follower count")
    follows: Optional[int] = Field(None, description="New follows in period")
    unfollows: Optional[int] = Field(None, description="Unfollows in period")


# ============================================================================
# LEGACY TOOL CALL MODEL (keep for backwards compatibility)
# ============================================================================

class ToolCall(BaseModel):
    """
    Record of a tool call made by the insights agent.
    Stores both the input parameters and the result.
    """

    tool_name: str = Field(..., description="Name of the tool that was called")
    arguments: Dict[str, Any] = Field(
        ..., description="Arguments passed to the tool"
    )
    result: Any = Field(..., description="Result returned by the tool")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the tool was called",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "tool_name": "get_post_engagement",
                "arguments": {
                    "post_id": "123456789_987654321",
                    "platform": "facebook",
                },
                "result": {
                    "likes": 234,
                    "comments": 18,
                    "shares": 12,
                    "reach": 4521,
                },
                "timestamp": "2025-01-18T15:30:00Z",
            }
        }


class InsightReport(BaseModel):
    """
    A dated insight report from the insights agent.

    The agent analyzes engagement metrics and comments to determine:
    - What content resonates with the audience
    - What doesn't work
    - Patterns in successful posts
    - Recommendations for future content

    This report is used by:
    - The planner agent (to inform content strategy)
    - The trend seed agent (for context)
    - The ungrounded seed agent (for creative direction)
    """

    id: UUID = Field(default_factory=uuid4, description="Unique insight report ID")
    business_asset_id: str = Field(..., description="Business asset ID for multi-tenancy")
    summary: str = Field(
        ...,
        description="High-level summary of findings and recommendations",
    )
    findings: str = Field(
        ...,
        description="Detailed findings about what works/doesn't work with the audience",
    )
    tool_calls: List[ToolCall] = Field(
        default_factory=list,
        description="All tool calls made by the agent to gather data",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when report was generated",
    )
    created_by: str = Field(
        ...,
        description="Foundation model used (e.g., 'gpt-4o', 'claude-3-opus')",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "e5f6a7b8-c9d0-8e9f-2a3b-4c5d6e7f8a9b",
                "summary": "Campus life content (esp. winter aesthetics) and student-focused posts drive 3x higher engagement than generic university news. Video content underperforms static images.",
                "findings": """Analysis of 45 posts from the past 2 weeks reveals:

**High Performers:**
- Winter campus photos: avg 380 likes, 32 comments
- Student testimonials/features: avg 290 likes, 41 comments
- Behind-the-scenes campus life: avg 315 likes, 28 comments

**Low Performers:**
- Administrative announcements: avg 78 likes, 3 comments
- Video content (reels): avg 142 likes, 8 comments
- Generic "motivational" content: avg 91 likes, 5 comments

**Key Insights:**
1. Audience prefers authentic, student-centered content
2. Visual aesthetic (photography quality) matters more than video production
3. Comments show high interest in "hidden gems" and practical tips
4. Peak engagement times: 6-8 PM on weekdays

**Recommendations:**
- Focus on student stories and campus aesthetics
- Deprioritize video until we improve production quality
- Create more "insider tips" content (study spots, food, etc.)
- Schedule posts for evening hours""",
                "tool_calls": [],
                "created_at": "2025-01-18T16:00:00Z",
                "created_by": "gpt-4o",
            }
        }
