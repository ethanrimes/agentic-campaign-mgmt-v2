# backend/services/wavespeed/video_generator.py

"""Video generation service using Wavespeed AI."""

from typing import Optional
from backend.config import settings
from backend.utils import get_logger
from .base import WavespeedBaseClient
from .model_configs import get_video_model_config, ModelConfig

logger = get_logger(__name__)


class VideoGenerator(WavespeedBaseClient):
    """
    Video generator using Wavespeed AI models.

    Supports multiple video models configured via settings.wavespeed_video_model:
    - wavespeed-ai/wan-2.2/i2v-5b-720p (default)
    - bytedance/seedance-v1-pro-t2v-480p

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
        self.model_id = settings.wavespeed_video_model
        self._config: ModelConfig = get_video_model_config(self.model_id)
        # Videos need much longer polling time
        if self.max_poll_attempts < 120:
            self.max_poll_attempts = 240  # 20 minutes for videos

    @property
    def config(self) -> ModelConfig:
        """Get the current model configuration."""
        return self._config

    async def generate(
        self,
        prompt: str,
        size: str = "1280*720",
        aspect_ratio: str = "16:9",
        camera_fixed: bool = False,
        seed: int = -1,
        duration: Optional[int] = None,
    ) -> bytes:
        """
        Generate a video from a text prompt.

        Args:
            prompt: Text prompt describing the desired video content
            size: Video resolution for wan-2.2 ("1280*720" or "720*1280")
            aspect_ratio: Aspect ratio for seedance ("21:9", "16:9", "4:3", "1:1", "3:4", "9:16")
            camera_fixed: Whether to fix camera (only for seedance)
            seed: Random seed (-1 for random)
            duration: Video duration in seconds — passed through to models that support it
                      (e.g. GrokVideoConfig: 6 or 10). Ignored by other models.

        Returns:
            Video bytes (MP4)

        Raises:
            MediaGenerationError: If generation fails
        """
        logger.info(
            "Generating video",
            model=self.model_id,
            prompt=prompt[:50],
            size=size,
            aspect_ratio=aspect_ratio,
            duration=duration,
        )

        # Build payload using model-specific configuration
        # duration is passed as a kwarg; models that don't support it will ignore it via **kwargs
        payload = self._config.build_payload(
            prompt=prompt,
            size=size,
            aspect_ratio=aspect_ratio,
            camera_fixed=camera_fixed,
            seed=seed,
            **({"duration": duration} if duration is not None else {}),
        )

        # Submit task and poll for completion with retry on transient errors
        output_url = await self._submit_and_poll_with_retry(self.model_id, payload)

        # Download video
        video_bytes = await self._download_media(output_url)

        return video_bytes
