# backend/services/wavespeed/video_generator.py

"""Video generation service using Wavespeed WAN-2.2."""

from typing import Optional
from backend.config import settings
from backend.utils import get_logger
from .base import WavespeedBaseClient

logger = get_logger(__name__)


class VideoGenerator(WavespeedBaseClient):
    """
    Video generator using Wavespeed WAN-2.2 (text-to-video) model.

    Example:
        ```python
        generator = VideoGenerator()
        video_bytes = await generator.generate(
            prompt="An old man adjusts his glasses while reading a newspaper",
            size="1280*720"
        )
        ```
    """

    def __init__(self):
        super().__init__()
        self.model = settings.wavespeed_video_model
        # Videos need much longer polling time - override if env vars not set for videos
        # Default to 20 minutes (240 attempts * 5s) if not configured
        if self.max_poll_attempts < 120:  # If less than 10 minutes
            self.max_poll_attempts = 240  # Override to 20 minutes for videos

    async def generate(
        self,
        prompt: str,
        size: str = "1280*720",
        seed: int = -1,
    ) -> bytes:
        """
        Generate a video from a text prompt.

        Args:
            prompt: Text prompt describing the desired video content
            size: Video resolution (e.g., "1280*720", "1920*1080")
            seed: Random seed (-1 for random)

        Returns:
            Video bytes (MP4)

        Raises:
            MediaGenerationError: If generation fails
        """
        logger.info(
            "Generating video",
            prompt=prompt[:50],
            size=size,
        )

        payload = {
            "prompt": prompt,
            "seed": seed,
            "size": size,
        }

        # Submit task
        request_id = await self._submit_task(self.model, payload)

        # Poll for completion (videos take much longer than images)
        output_url = await self._poll_for_completion(request_id)

        # Download video
        video_bytes = await self._download_media(output_url)

        return video_bytes
