# backend/database/repositories/media.py

"""Repository for media (images and videos)."""

from typing import List, Literal
from backend.models import Image, Video
from backend.database import get_supabase_admin_client
from backend.utils import DatabaseError
from .base import BaseRepository


class MediaRepository(BaseRepository):
    """Repository for managing media."""

    def __init__(self):
        # Using dict as base type since we have two model types
        super().__init__("media", dict)

    async def create_image(self, image: Image) -> Image:
        """Create image record."""
        try:
            client = await get_supabase_admin_client()
            data = image.model_dump(mode="json", exclude_unset=True)
            data["media_type"] = "image"
            result = await client.table(self.table_name).insert(data).execute()
            if result.data:
                return Image(**result.data[0])
            raise DatabaseError("No data returned from create_image")
        except Exception as e:
            raise DatabaseError(f"Failed to create image: {e}")

    async def create_video(self, video: Video) -> Video:
        """Create video record."""
        try:
            client = await get_supabase_admin_client()
            data = video.model_dump(mode="json", exclude_unset=True)
            data["media_type"] = "video"
            result = await client.table(self.table_name).insert(data).execute()
            if result.data:
                return Video(**result.data[0])
            raise DatabaseError("No data returned from create_video")
        except Exception as e:
            raise DatabaseError(f"Failed to create video: {e}")

    async def get_recent_media(
        self, media_type: Literal["image", "video"] | None = None, limit: int = 20
    ) -> List:
        """Get recent media."""
        try:
            client = await get_supabase_admin_client()
            query = client.table(self.table_name).select("*")
            if media_type:
                query = query.eq("media_type", media_type)
            result = await query.order("created_at", desc=True).limit(limit).execute()

            # Return as appropriate type
            items = []
            for item in result.data:
                if item["media_type"] == "image":
                    items.append(Image(**item))
                else:
                    items.append(Video(**item))
            return items
        except Exception as e:
            return []
