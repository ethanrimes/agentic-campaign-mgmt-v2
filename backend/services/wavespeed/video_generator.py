# backend/services/wavespeed/video_generator.py

"""Video generation service using Wavespeed WAN-2.2."""

from typing import Optional
from backend.config import settings
from backend.utils import get_logger
from .base import WavespeedBaseClient

logger = get_logger(__name__)


class WavespeedVideoGenerator(WavespeedBaseClient):
    """
    Video generator using Wavespeed WAN-2.2 (image-to-video) model.

    Example:
        ```python
        generator = WavespeedVideoGenerator()
        video_bytes = await generator.generate(
            input_image_url="https://...",
            prompt="Gentle camera pan with moving clouds"
        )
        ```
    """

    def __init__(self):
        super().__init__()
        self.model = settings.wavespeed_video_model

    async def generate(
        self,
        input_image_url: str,
        prompt: str,
        seed: int = -1,
    ) -> bytes:
        """
        Generate a video from an input image.

        Args:
            input_image_url: URL to input image (must be publicly accessible)
            prompt: Text prompt describing the desired motion/effect
            seed: Random seed (-1 for random)

        Returns:
            Video bytes (MP4)

        Raises:
            MediaGenerationError: If generation fails
        """
        logger.info(
            "Generating video",
            prompt=prompt[:50],
            input_image=input_image_url[:50],
        )

        payload = {
            "image": input_image_url,
            "prompt": prompt,
            "seed": seed,
        }

        # Submit task
        request_id = await self._submit_task(self.model, payload)

        # Poll for completion (videos take longer)
        output_url = await self._poll_for_completion(request_id)

        # Download video
        video_bytes = await self._download_media(output_url)

        return video_bytes
