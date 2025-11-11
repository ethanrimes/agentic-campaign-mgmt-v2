# backend/services/meta/facebook_publisher.py

"""Facebook posting service."""

import json
from typing import List
from backend.utils import get_logger, PublishingError
from .base import MetaBaseClient

logger = get_logger(__name__)


class FacebookPublisher(MetaBaseClient):
    """
    Facebook publishing service.

    Supports:
    - Single image posts
    - Carousel posts (multiple images)
    - Video posts
    - Text/link posts
    """

    async def post_image(self, image_url: str, caption: str) -> str:
        """
        Post a single image to Facebook page.

        Args:
            image_url: Public URL to image
            caption: Post caption

        Returns:
            Facebook post ID

        Raises:
            PublishingError: If posting fails
        """
        logger.info("Posting image to Facebook", caption=caption[:50])

        url = f"{self.BASE_URL}/{self.page_id}/photos"
        data = {
            "url": image_url,
            "caption": caption,
            "access_token": self.page_token,
        }

        try:
            result = await self._make_request("POST", url, data=data)
            post_id = result["id"]
            logger.info("Posted image to Facebook", post_id=post_id)
            return post_id
        except Exception as e:
            raise PublishingError(f"Failed to post image: {e}")

    async def post_carousel(self, image_urls: List[str], caption: str) -> str:
        """
        Post a carousel (multiple images) to Facebook page.

        Args:
            image_urls: List of public URLs to images
            caption: Post caption

        Returns:
            Facebook post ID

        Raises:
            PublishingError: If posting fails
        """
        logger.info("Posting carousel to Facebook", num_images=len(image_urls))

        try:
            # Step 1: Upload images without publishing
            photo_ids = []
            for image_url in image_urls:
                url = f"{self.BASE_URL}/{self.page_id}/photos"
                data = {
                    "url": image_url,
                    "published": False,
                    "caption": "",
                    "access_token": self.page_token,
                }
                result = await self._make_request("POST", url, data=data)
                photo_ids.append(result["id"])

            # Step 2: Create carousel post
            url = f"{self.BASE_URL}/{self.page_id}/feed"
            attached_media = [{"media_fbid": pid} for pid in photo_ids]
            data = {
                "message": caption,
                "attached_media": json.dumps(attached_media),
                "access_token": self.page_token,
            }

            result = await self._make_request("POST", url, data=data)
            post_id = result["id"]
            logger.info("Posted carousel to Facebook", post_id=post_id)
            return post_id

        except Exception as e:
            raise PublishingError(f"Failed to post carousel: {e}")

    async def post_video(self, video_url: str, description: str) -> str:
        """
        Post a video to Facebook page.

        Args:
            video_url: Public URL to video
            description: Video description

        Returns:
            Facebook post ID

        Raises:
            PublishingError: If posting fails
        """
        logger.info("Posting video to Facebook", description=description[:50])

        url = f"{self.BASE_URL}/{self.page_id}/videos"
        data = {
            "file_url": video_url,
            "description": description,
            "access_token": self.page_token,
        }

        try:
            result = await self._make_request("POST", url, data=data)
            post_id = result["id"]
            logger.info("Posted video to Facebook", post_id=post_id)
            return post_id
        except Exception as e:
            raise PublishingError(f"Failed to post video: {e}")

    async def post_text(self, message: str, link: str = None) -> str:
        """
        Post text (with optional link) to Facebook page.

        Args:
            message: Post message
            link: Optional URL to include

        Returns:
            Facebook post ID

        Raises:
            PublishingError: If posting fails
        """
        logger.info("Posting text to Facebook", message=message[:50])

        url = f"{self.BASE_URL}/{self.page_id}/feed"
        data = {
            "message": message,
            "access_token": self.page_token,
        }
        if link:
            data["link"] = link

        try:
            result = await self._make_request("POST", url, data=data)
            post_id = result["id"]
            logger.info("Posted text to Facebook", post_id=post_id)
            return post_id
        except Exception as e:
            raise PublishingError(f"Failed to post text: {e}")
