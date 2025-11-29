# backend/models/media.py

"""
Media entities for generated images and videos.
Stored in Supabase storage bucket.
"""

from datetime import datetime, timezone
from typing import Optional, Literal
from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from uuid import UUID, uuid4
from enum import Enum


class MediaType(str, Enum):
    """Media type enumeration."""

    IMAGE = "image"
    VIDEO = "video"


class Image(BaseModel):
    """
    Generated image stored in Supabase storage.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique image ID")
    business_asset_id: str = Field(
        ...,
        description="Business asset ID this media belongs to"
    )
    storage_path: str = Field(
        ...,
        description="Path in Supabase storage bucket (e.g., 'task_123/images/img_001.png')",
    )
    public_url: HttpUrl = Field(
        ..., description="Public URL for accessing the image"
    )
    prompt: Optional[str] = Field(
        None, description="Generation prompt used (if applicable)"
    )
    model: Optional[str] = Field(
        None, description="Model used for generation (e.g., 'sdxl-lora')"
    )
    width: Optional[int] = Field(None, description="Image width in pixels")
    height: Optional[int] = Field(None, description="Image height in pixels")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    mime_type: str = Field(default="image/png", description="MIME type")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when image was generated",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "f6a7b8c9-d0e1-9f0a-3b4c-5d6e7f8a9b0c",
                "storage_path": "task_abc123/images/20250118_143022_a1b2c3d4.png",
                "public_url": "https://your-project.supabase.co/storage/v1/object/public/generated-media/task_abc123/images/20250118_143022_a1b2c3d4.png",
                "prompt": "A vibrant photo of Penn campus in winter, snow-covered quad with historic buildings",
                "model": "sdxl-lora",
                "width": 1024,
                "height": 1024,
                "file_size": 2458624,
                "mime_type": "image/png",
                "created_at": "2025-01-18T14:30:22Z",
            }
        }
    )


class Video(BaseModel):
    """
    Generated video stored in Supabase storage.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique video ID")
    business_asset_id: str = Field(
        ...,
        description="Business asset ID this media belongs to"
    )
    storage_path: str = Field(
        ...,
        description="Path in Supabase storage bucket (e.g., 'task_123/videos/vid_001.mp4')",
    )
    public_url: HttpUrl = Field(
        ..., description="Public URL for accessing the video"
    )
    prompt: Optional[str] = Field(
        None, description="Generation prompt used (if applicable)"
    )
    input_image_url: Optional[HttpUrl] = Field(
        None, description="Input image URL for I2V models"
    )
    model: Optional[str] = Field(
        None, description="Model used for generation (e.g., 'wan-2.2')"
    )
    width: Optional[int] = Field(None, description="Video width in pixels")
    height: Optional[int] = Field(None, description="Video height in pixels")
    duration: Optional[float] = Field(None, description="Duration in seconds")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    mime_type: str = Field(default="video/mp4", description="MIME type")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when video was generated",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "a7b8c9d0-e1f2-0a1b-4c5d-6e7f8a9b0c1d",
                "storage_path": "task_abc123/videos/20250118_144530_e5f6g7h8.mp4",
                "public_url": "https://your-project.supabase.co/storage/v1/object/public/generated-media/task_abc123/videos/20250118_144530_e5f6g7h8.mp4",
                "prompt": "Gentle camera pan across snowy Penn campus",
                "input_image_url": "https://your-project.supabase.co/storage/v1/object/public/generated-media/task_abc123/images/input.png",
                "model": "wan-2.2",
                "width": 1280,
                "height": 720,
                "duration": 5.0,
                "file_size": 8945120,
                "mime_type": "video/mp4",
                "created_at": "2025-01-18T14:45:30Z",
            }
        }
    )
