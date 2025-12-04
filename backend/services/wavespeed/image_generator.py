# backend/services/wavespeed/image_generator.py

"""Image generation service using Wavespeed AI."""

from typing import Optional, Union
from backend.config import settings
from backend.utils import get_logger
from .base import WavespeedBaseClient
from .model_configs import get_image_model_config, ModelConfig, ImageSize

logger = get_logger(__name__)


class ImageGenerator(WavespeedBaseClient):
    """
    Image generator using Wavespeed AI models.

    Supports multiple image models configured via settings.wavespeed_image_model:
    - stability-ai/sdxl-lora
    - bytedance/seedream-v4
    - bytedance/seedream-v4.5 (requires minimum 2048*2048)

    Example:
        ```python
        generator = ImageGenerator()

        # Using ImageSize enum (recommended)
        image_bytes = await generator.generate(
            prompt="A vibrant photo of Penn campus in winter",
            size=ImageSize.SQUARE
        )

        # Using string (for backwards compatibility)
        image_bytes = await generator.generate(
            prompt="A vibrant photo of Penn campus in winter",
            size="2048*2048"
        )
        ```
    """

    def __init__(self):
        super().__init__()
        self.model_id = settings.wavespeed_image_model
        self._config: ModelConfig = get_image_model_config(self.model_id)

    @property
    def config(self) -> ModelConfig:
        """Get the current model configuration."""
        return self._config

    async def generate(
        self,
        prompt: str,
        size: Union[ImageSize, str] = None,
        negative_prompt: str = "",
        guidance_scale: float = 3.5,
        num_inference_steps: int = 28,
    ) -> bytes:
        """
        Generate an image.

        Args:
            prompt: Text prompt for generation
            size: Image size - use ImageSize enum or "width*height" string.
                  Defaults to ImageSize.SQUARE (2048*2048) for seedream models.
                  Note: seedream-v4.5 requires minimum 2048*2048 (4,194,304 pixels).
            negative_prompt: Negative prompt (only used by sdxl-lora)
            guidance_scale: CFG scale (only used by sdxl-lora, range 1-20)
            num_inference_steps: Denoising steps (only used by sdxl-lora, range 1-50)

        Returns:
            Image bytes (PNG)

        Raises:
            MediaGenerationError: If generation fails
        """
        # Convert ImageSize enum to string if needed
        if isinstance(size, ImageSize):
            size_str = size.value
        elif size is None:
            size_str = ImageSize.get_default().value
        else:
            size_str = size

        logger.info(
            "Generating image",
            model=self.model_id,
            prompt=prompt[:50],
            size=size_str,
        )

        # Build payload using model-specific configuration
        payload = self._config.build_payload(
            prompt=prompt,
            size=size_str,
            negative_prompt=negative_prompt,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
        )

        # Submit task
        request_id = await self._submit_task(self.model_id, payload)

        # Poll for completion
        output_url = await self._poll_for_completion(request_id)

        # Download image
        image_bytes = await self._download_media(output_url)

        return image_bytes
