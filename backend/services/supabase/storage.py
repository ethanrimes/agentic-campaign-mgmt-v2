# backend/services/supabase/storage.py

"""
Supabase storage operations for generated media.
"""

from datetime import datetime
from uuid import uuid4
from pathlib import Path
from backend.database import get_supabase_admin_client
from backend.utils import get_logger
from backend.models import Image, Video

logger = get_logger(__name__)


class StorageService:
    """
    Helper for uploading and managing media in Supabase storage.
    """

    BUCKET_NAME = "generated-media"

    def __init__(self):
        self.client = get_supabase_admin_client()

    def upload_image(
        self,
        image_bytes: bytes,
        task_id: str,
        prompt: str = None,
        model: str = None,
        mime_type: str = "image/png",
    ) -> Image:
        """
        Upload generated image to Supabase storage.

        Args:
            image_bytes: Image data
            task_id: Content creation task ID
            prompt: Generation prompt
            model: Model used
            mime_type: Image MIME type

        Returns:
            Image model with public URL
        """
        # Generate unique filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        file_id = uuid4().hex[:8]
        filename = f"{timestamp}_{file_id}.png"

        # Build storage path
        storage_path = f"{task_id}/images/{filename}"

        logger.info("Uploading image to Supabase", path=storage_path, size=len(image_bytes))

        try:
            # Upload to storage
            self.client.storage.from_(self.BUCKET_NAME).upload(
                storage_path,
                image_bytes,
                file_options={"content-type": mime_type},
            )

            # Get public URL
            public_url = self.client.storage.from_(self.BUCKET_NAME).get_public_url(storage_path)

            # Create Image model
            image = Image(
                storage_path=storage_path,
                public_url=public_url,
                prompt=prompt,
                model=model,
                file_size=len(image_bytes),
                mime_type=mime_type,
            )

            logger.info("Image uploaded successfully", url=public_url)
            return image

        except Exception as e:
            logger.error("Failed to upload image", error=str(e))
            raise

    def upload_video(
        self,
        video_bytes: bytes,
        task_id: str,
        prompt: str = None,
        input_image_url: str = None,
        model: str = None,
        mime_type: str = "video/mp4",
    ) -> Video:
        """
        Upload generated video to Supabase storage.

        Args:
            video_bytes: Video data
            task_id: Content creation task ID
            prompt: Generation prompt
            input_image_url: Input image for I2V
            model: Model used
            mime_type: Video MIME type

        Returns:
            Video model with public URL
        """
        # Generate unique filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        file_id = uuid4().hex[:8]
        filename = f"{timestamp}_{file_id}.mp4"

        # Build storage path
        storage_path = f"{task_id}/videos/{filename}"

        logger.info("Uploading video to Supabase", path=storage_path, size=len(video_bytes))

        try:
            # Upload to storage
            self.client.storage.from_(self.BUCKET_NAME).upload(
                storage_path,
                video_bytes,
                file_options={"content-type": mime_type},
            )

            # Get public URL
            public_url = self.client.storage.from_(self.BUCKET_NAME).get_public_url(storage_path)

            # Create Video model
            video = Video(
                storage_path=storage_path,
                public_url=public_url,
                prompt=prompt,
                input_image_url=input_image_url,
                model=model,
                file_size=len(video_bytes),
                mime_type=mime_type,
            )

            logger.info("Video uploaded successfully", url=public_url)
            return video

        except Exception as e:
            logger.error("Failed to upload video", error=str(e))
            raise

    def delete_file(self, storage_path: str) -> bool:
        """
        Delete a file from storage.

        Args:
            storage_path: Path in storage bucket

        Returns:
            True if successful
        """
        try:
            self.client.storage.from_(self.BUCKET_NAME).remove([storage_path])
            logger.info("File deleted", path=storage_path)
            return True
        except Exception as e:
            logger.error("Failed to delete file", path=storage_path, error=str(e))
            return False
