# backend/services/meta/instagram_publisher.py

"""Instagram posting service."""

from typing import List
from backend.utils import get_logger, PublishingError
from .base import MetaBaseClient

logger = get_logger(__name__)


class InstagramPublisher(MetaBaseClient):
    """
    Instagram publishing service.

    Uses two-step process: create container → publish container.
    Supports: images, carousels, reels, stories.
    """

    async def post_image(self, image_url: str, caption: str) -> str:
        """
        Post a single image to Instagram.

        Args:
            image_url: Public URL to image
            caption: Post caption

        Returns:
            Instagram media ID

        Raises:
            PublishingError: If posting fails
        """
        logger.info("Posting image to Instagram", caption=caption[:50])

        try:
            # Step 1: Create media container
            url = f"{self.INSTAGRAM_BASE_URL}/{self.ig_user_id}/media"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.ig_token}",
            }
            json_data = {
                "image_url": image_url,
                "caption": caption,
            }

            result = await self._make_request("POST", url, json_data=json_data, headers=headers)
            container_id = result["id"]

            # Step 2: Publish container
            publish_url = f"{self.INSTAGRAM_BASE_URL}/{self.ig_user_id}/media_publish"
            publish_data = {
                "creation_id": container_id,
            }

            result = await self._make_request("POST", publish_url, json_data=publish_data, headers=headers)
            media_id = result["id"]
            logger.info("Posted image to Instagram", media_id=media_id)
            return media_id

        except Exception as e:
            raise PublishingError(f"Failed to post image: {e}")

    async def post_carousel(self, image_urls: List[str], caption: str) -> str:
        """
        Post a carousel to Instagram.

        Args:
            image_urls: List of public URLs to images
            caption: Post caption

        Returns:
            Instagram media ID

        Raises:
            PublishingError: If posting fails
        """
        logger.info("Posting carousel to Instagram", num_images=len(image_urls))

        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.ig_token}",
            }

            # Step 1: Create containers for each image
            container_ids = []
            for image_url in image_urls:
                url = f"{self.INSTAGRAM_BASE_URL}/{self.ig_user_id}/media"
                json_data = {
                    "image_url": image_url,
                    "is_carousel_item": True,
                }
                result = await self._make_request("POST", url, json_data=json_data, headers=headers)
                container_ids.append(result["id"])

            # Step 2: Create carousel container
            url = f"{self.INSTAGRAM_BASE_URL}/{self.ig_user_id}/media"
            json_data = {
                "media_type": "CAROUSEL",
                "children": ",".join(container_ids),
                "caption": caption,
            }
            result = await self._make_request("POST", url, json_data=json_data, headers=headers)
            carousel_id = result["id"]

            # Step 3: Publish carousel
            publish_url = f"{self.INSTAGRAM_BASE_URL}/{self.ig_user_id}/media_publish"
            publish_data = {
                "creation_id": carousel_id,
            }
            result = await self._make_request("POST", publish_url, json_data=publish_data, headers=headers)
            media_id = result["id"]
            logger.info("Posted carousel to Instagram", media_id=media_id)
            return media_id

        except Exception as e:
            raise PublishingError(f"Failed to post carousel: {e}")

    async def post_reel(self, video_url: str, caption: str) -> str:
        """
        Post a reel to Instagram.

        Args:
            video_url: Public URL to video
            caption: Reel caption

        Returns:
            Instagram media ID

        Raises:
            PublishingError: If posting fails
        """
        logger.info("Posting reel to Instagram", caption=caption[:50])

        try:
            # Step 1: Create reel container
            url = f"{self.INSTAGRAM_BASE_URL}/{self.ig_user_id}/media"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.ig_token}",
            }
            json_data = {
                "video_url": video_url,
                "media_type": "REELS",
                "caption": caption,
            }

            result = await self._make_request("POST", url, json_data=json_data, headers=headers)
            container_id = result["id"]

            # Step 2: Publish reel
            publish_url = f"{self.INSTAGRAM_BASE_URL}/{self.ig_user_id}/media_publish"
            publish_data = {
                "creation_id": container_id,
            }

            result = await self._make_request("POST", publish_url, json_data=publish_data, headers=headers)
            media_id = result["id"]
            logger.info("Posted reel to Instagram", media_id=media_id)
            return media_id

        except Exception as e:
            raise PublishingError(f"Failed to post reel: {e}")
