# backend/models/posts.py

"""
Completed post entity.
Created by the content creation agent, published by the publishers.
"""

from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, HttpUrl
from uuid import UUID, uuid4


class CompletedPost(BaseModel):
    """
    A completed social media post ready for or already published.

    Created by the content creation agent and consumed by publishers.
    Includes all media, text, and metadata needed for posting.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique post ID")

    # Task reference
    task_id: UUID = Field(
        ..., description="ID of the content creation task that produced this post"
    )
    content_seed_id: UUID = Field(
        ..., description="ID of the content seed this post is based on"
    )
    content_seed_type: Literal["news_event", "trend", "ungrounded"] = Field(
        ..., description="Type of content seed"
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
    media_urls: List[HttpUrl] = Field(
        default_factory=list,
        description="List of Supabase URLs for images/videos (empty for text-only posts)",
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
    published_at: Optional[datetime] = Field(
        None, description="When the post was published to the platform"
    )
    platform_post_id: Optional[str] = Field(
        None, description="Post ID from Facebook/Instagram (after publishing)"
    )
    platform_post_url: Optional[HttpUrl] = Field(
        None, description="URL to the published post (if available)"
    )
    error_message: Optional[str] = Field(
        None, description="Error message if publishing failed"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the post was created by content creation agent",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "c9d0e1f2-a3b4-1c2d-6e7f-8a9b0c1d2e3f",
                "task_id": "b8c9d0e1-f2a3-0b1c-5d6e-7f8a9b0c1d2e",
                "content_seed_id": "b2c3d4e5-f6a7-5b6c-9d0e-1f2a3b4c5d6e",
                "content_seed_type": "news_event",
                "platform": "instagram",
                "post_type": "instagram_image",
                "text": "SEPTA fare increase coming in March 🚊💰 What does this mean for Penn students? Check out our breakdown. #SEPTA #UPenn #Philadelphia #Transit",
                "media_urls": [
                    "https://your-project.supabase.co/storage/v1/object/public/generated-media/task_abc/img_001.png"
                ],
                "location": "Philadelphia, Pennsylvania",
                "music": None,
                "hashtags": ["SEPTA", "UPenn", "Philadelphia", "Transit"],
                "status": "pending",
                "published_at": None,
                "platform_post_id": None,
                "platform_post_url": None,
                "error_message": None,
                "created_at": "2025-01-18T18:30:00Z",
            }
        }
