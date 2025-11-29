# backend/models/comments.py

"""
Platform comment entity for Facebook and Instagram comments.
Used for AI-powered comment response generation.
"""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID, uuid4


class PlatformComment(BaseModel):
    """
    A comment from Facebook or Instagram that needs a response.

    Comments are populated either via webhook (Facebook) or periodic polling (Instagram).
    The comment responder agent processes pending comments and generates appropriate replies.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4, description="Unique comment record ID")
    business_asset_id: str = Field(..., description="Business asset ID for multi-tenancy")

    # Platform identification
    platform: Literal["facebook", "instagram"] = Field(
        ..., description="Platform this comment is from"
    )
    comment_id: str = Field(
        ..., description="Platform's unique comment ID"
    )
    post_id: str = Field(
        ..., description="Platform's post ID this comment belongs to"
    )

    # Comment content
    comment_text: str = Field(..., description="The comment text")
    commenter_username: str = Field(..., description="Username of the commenter")
    commenter_id: str = Field(..., description="Platform ID of the commenter")
    parent_comment_id: Optional[str] = Field(
        None, description="Parent comment ID if this is a reply (for threading)"
    )

    # Metadata from platform
    created_time: datetime = Field(
        ..., description="When the comment was created on the platform"
    )
    like_count: int = Field(default=0, description="Number of likes on the comment")
    permalink_url: Optional[str] = Field(
        None, description="Permanent URL to the comment"
    )

    # Response tracking
    status: Literal["pending", "responded", "failed", "ignored"] = Field(
        default="pending", description="Status of our response to this comment"
    )
    response_text: Optional[str] = Field(
        None, description="Our AI-generated response text"
    )
    response_comment_id: Optional[str] = Field(
        None, description="Platform ID of our posted reply comment"
    )
    responded_at: Optional[datetime] = Field(
        None, description="When we responded to the comment"
    )
    error_message: Optional[str] = Field(
        None, description="Error message if response failed"
    )
    retry_count: int = Field(
        default=0, description="Number of times we attempted to respond"
    )

    # Optional link to our posts
    our_post_id: Optional[UUID] = Field(
        None, description="Reference to our completed_posts table if we can match it"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(),
        description="When this record was created in our database"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(),
        description="When this record was last updated"
    )
