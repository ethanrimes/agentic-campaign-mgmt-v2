# backend/services/meta/publishing/instagram_publisher.py

"""Instagram posting service."""

import asyncio
from typing import List, Optional
from backend.utils import get_logger, PublishingError
from backend.services.meta.base import MetaBaseClient

logger = get_logger(__name__)


class InstagramPublisher(MetaBaseClient):
    """
    Instagram publishing service.

    Uses two-step process: create container → publish container.
    Supports: images, carousels, reels, stories.
    """

    async def _wait_for_container(self, container_id: str, max_polls: int = 60, poll_interval: int = 5) -> None:
        """
        Poll container status until ready.

        Args:
            container_id: The container ID to check
            max_polls: Maximum number of polls (default 60 = 5 minutes for reels)
            poll_interval: Seconds between polls

        Raises:
            PublishingError: If container fails or times out
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.ig_token}",
        }

        for _ in range(max_polls):
            status_url = f"{self.INSTAGRAM_BASE_URL}/{container_id}?fields=status_code"
            result = await self._make_request("GET", status_url, headers=headers)
            status_code = result.get("status_code")

            if status_code == "FINISHED":
                logger.info("Container ready", container_id=container_id)
                return
            elif status_code == "ERROR":
                raise PublishingError("Media container processing failed")
            elif status_code == "IN_PROGRESS":
                logger.debug("Container processing", container_id=container_id, status=status_code)
                await asyncio.sleep(poll_interval)
            else:
                # For images, status_code might not be present - treat as ready
                if status_code is None:
                    logger.info("Container ready (no status)", container_id=container_id)
                    return
                logger.debug("Container status", container_id=container_id, status=status_code)
                await asyncio.sleep(poll_interval)

        raise PublishingError(f"Container processing timed out after {max_polls * poll_interval} seconds")

    async def post_image(self, image_url: str, caption: str) -> Optional[str]:
        """
        Post a single image to Instagram.

        Args:
            image_url: Public URL to image
            caption: Post caption

        Returns:
            Instagram media ID, or None if no image URL provided

        Raises:
            PublishingError: If posting fails
        """
        if not image_url:
            logger.info("Skipping image post - no image URL provided")
            return None

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

            # Step 2: Wait for container to be ready
            await self._wait_for_container(container_id, max_polls=12, poll_interval=5)

            # Step 3: Publish container
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

    async def post_carousel(self, image_urls: List[str], caption: str) -> Optional[str]:
        """
        Post a carousel to Instagram.

        Args:
            image_urls: List of public URLs to images
            caption: Post caption

        Returns:
            Instagram media ID, or None if no image URLs provided

        Raises:
            PublishingError: If posting fails
        """
        if not image_urls:
            logger.info("Skipping carousel post - no image URLs provided")
            return None

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

            # Step 3: Wait for carousel container to be ready
            await self._wait_for_container(carousel_id, max_polls=12, poll_interval=5)

            # Step 4: Publish carousel
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

    async def post_reel(self, video_url: str, caption: str) -> Optional[str]:
        """
        Post a reel to Instagram.

        Args:
            video_url: Public URL to video
            caption: Reel caption

        Returns:
            Instagram media ID, or None if no video URL provided

        Raises:
            PublishingError: If posting fails
        """
        if not video_url:
            logger.info("Skipping reel post - no video URL provided")
            return None

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

            # Step 2: Wait for reel to be processed (videos take longer)
            await self._wait_for_container(container_id, max_polls=60, poll_interval=5)

            # Step 3: Publish reel
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
