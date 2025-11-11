# backend/models/social_media.py

"""
Social media entities for scraped content.
Used by trend seed agent to store posts and users from Facebook/Instagram.
"""

from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field, HttpUrl
from uuid import UUID, uuid4


class User(BaseModel):
    """
    A social media user/account from scraped data.
    """

    id: Optional[str] = Field(None, description="Platform user ID (if available)")
    username: Optional[str] = Field(None, description="Username/handle")
    display_name: Optional[str] = Field(None, description="Display name")
    profile_url: Optional[HttpUrl] = Field(None, description="Profile URL")
    follower_count: Optional[int] = Field(
        None, description="Number of followers (if available)"
    )
    platform: str = Field(..., description="Platform: 'facebook' or 'instagram'")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata from scraper"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "12345678",
                "username": "pennstudentlife",
                "display_name": "Penn Student Life",
                "profile_url": "https://www.instagram.com/pennstudentlife/",
                "follower_count": 15234,
                "platform": "instagram",
                "metadata": {},
            }
        }


class ScraperPost(BaseModel):
    """
    A post from social media scraped by RapidAPI tools.
    Stored with trend seeds to provide context.
    """

    id: Optional[str] = Field(None, description="Platform post ID (if available)")
    link: HttpUrl = Field(
        ...,
        description="URL to the post (critical for content creation agents to reference)",
    )
    text: Optional[str] = Field(None, description="Post caption/text")
    author: Optional[User] = Field(None, description="Post author")
    likes: Optional[int] = Field(None, description="Like count")
    comments: Optional[int] = Field(None, description="Comment count")
    shares: Optional[int] = Field(None, description="Share count")
    hashtags: List[str] = Field(default_factory=list, description="Hashtags used")
    media_urls: List[str] = Field(
        default_factory=list, description="URLs to images/videos in post"
    )
    posted_at: Optional[datetime] = Field(
        None, description="When post was published"
    )
    platform: str = Field(..., description="Platform: 'facebook' or 'instagram'")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional scraped data"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "C1234567890",
                "link": "https://www.instagram.com/p/ABC123/",
                "text": "Beautiful snowy morning at Penn! ❄️ #UPenn #WinterVibes #CampusLife",
                "author": None,
                "likes": 342,
                "comments": 28,
                "shares": None,
                "hashtags": ["UPenn", "WinterVibes", "CampusLife"],
                "media_urls": [
                    "https://instagram.com/media/image1.jpg",
                ],
                "posted_at": "2025-01-16T08:30:00Z",
                "platform": "instagram",
                "metadata": {},
            }
        }


# Alias for backward compatibility with the main models
Post = ScraperPost
