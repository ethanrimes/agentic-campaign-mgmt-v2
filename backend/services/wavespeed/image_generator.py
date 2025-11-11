# backend/services/wavespeed/image_generator.py

"""Image generation service using Wavespeed SDXL-LoRA."""

from typing import Optional
from backend.config import settings
from backend.utils import get_logger
from .base import WavespeedBaseClient

logger = get_logger(__name__)


class ImageGenerator(WavespeedBaseClient):
    """
    Image generator using Wavespeed SDXL-LoRA model.

    Example:
        ```python
        generator = ImageGenerator()
        image_bytes = await generator.generate(
            prompt="A vibrant photo of Penn campus in winter",
            size="1024*1024"
        )
        ```
    """

    def __init__(self):
        super().__init__()
        self.model = settings.wavespeed_image_model

    async def generate(
        self,
        prompt: str,
        size: str = "1024*1024",
        guidance_scale: float = 7.5,
        num_inference_steps: int = 30,
        seed: int = -1,
    ) -> bytes:
        """
        Generate an image.

        Args:
            prompt: Text prompt for generation
            size: Image size (e.g., "1024*1024", "512*512")
            guidance_scale: CFG scale (higher = more prompt adherence)
            num_inference_steps: Number of denoising steps
            seed: Random seed (-1 for random)

        Returns:
            Image bytes (PNG)

        Raises:
            MediaGenerationError: If generation fails
        """
        logger.info(
            "Generating image",
            prompt=prompt[:50],
            size=size,
            guidance_scale=guidance_scale,
        )

        payload = {
            "prompt": prompt,
            "size": size,
            "guidance_scale": guidance_scale,
            "num_inference_steps": num_inference_steps,
            "seed": seed,
            "enable_base64_output": False,
            "loras": [],
        }

        # Submit task
        request_id = await self._submit_task(self.model, payload)

        # Poll for completion
        output_url = await self._poll_for_completion(request_id)

        # Download image
        image_bytes = await self._download_media(output_url)

        return image_bytes
