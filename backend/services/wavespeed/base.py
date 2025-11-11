# backend/services/wavespeed/base.py

"""
Base client for Wavespeed AI API.
Handles authentication, request submission, and polling.
"""

import asyncio
import aiohttp
from typing import Dict, Any, Optional
from backend.config import settings
from backend.utils import get_logger, APIError, MediaGenerationError

logger = get_logger(__name__)


class WavespeedBaseClient:
    """Base client for Wavespeed AI API operations."""

    def __init__(self):
        self.api_base = settings.wavespeed_api_base
        self.api_key = settings.wavespeed_api_key
        self.polling_interval = settings.wavespeed_polling_interval
        self.max_poll_attempts = settings.wavespeed_max_poll_attempts

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authorization."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def _submit_task(self, model_endpoint: str, payload: Dict[str, Any]) -> str:
        """
        Submit a generation task to Wavespeed.

        Args:
            model_endpoint: Model endpoint (e.g., 'sdxl-lora', 'wan-2.2')
            payload: Request payload

        Returns:
            Request ID for polling

        Raises:
            MediaGenerationError: If submission fails
        """
        url = f"{self.api_base}/{model_endpoint}"

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    url, headers=self._get_headers(), json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise MediaGenerationError(
                            f"Failed to submit task",
                            status_code=response.status,
                            response_body=error_text,
                        )

                    result = await response.json()
                    request_id = result["data"]["id"]
                    logger.info(
                        "Submitted generation task",
                        model=model_endpoint,
                        request_id=request_id,
                    )
                    return request_id

            except aiohttp.ClientError as e:
                raise MediaGenerationError(f"Network error during task submission: {e}")

    async def _poll_for_completion(self, request_id: str) -> str:
        """
        Poll for task completion and return output URL.

        Args:
            request_id: Request ID from task submission

        Returns:
            Temporary URL to the generated media

        Raises:
            MediaGenerationError: If polling fails or times out
        """
        url = f"{self.api_base}/predictions/{request_id}/result"

        async with aiohttp.ClientSession() as session:
            for attempt in range(1, self.max_poll_attempts + 1):
                try:
                    async with session.get(url, headers=self._get_headers()) as response:
                        if response.status != 200:
                            error_text = await response.text()
                            raise MediaGenerationError(
                                f"Failed to poll status",
                                status_code=response.status,
                                response_body=error_text,
                            )

                        result = await response.json()
                        status = result["data"]["status"]

                        if status == "completed":
                            output_url = result["data"]["outputs"][0]
                            logger.info(
                                "Generation completed",
                                request_id=request_id,
                                attempt=attempt,
                            )
                            return output_url

                        elif status == "failed":
                            error = result["data"].get("error", "Unknown error")
                            raise MediaGenerationError(f"Generation failed: {error}")

                        # Still processing
                        if attempt < self.max_poll_attempts:
                            await asyncio.sleep(self.polling_interval)

                except aiohttp.ClientError as e:
                    if attempt == self.max_poll_attempts:
                        raise MediaGenerationError(f"Network error during polling: {e}")
                    await asyncio.sleep(self.polling_interval)

            raise MediaGenerationError(
                f"Generation timeout after {self.max_poll_attempts} attempts"
            )

    async def _download_media(self, url: str) -> bytes:
        """
        Download generated media from temporary URL.

        Args:
            url: Temporary URL from Wavespeed

        Returns:
            Media bytes

        Raises:
            MediaGenerationError: If download fails
        """
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    if response.status != 200:
                        raise MediaGenerationError(
                            f"Failed to download media",
                            status_code=response.status,
                        )

                    media_bytes = await response.read()
                    logger.info("Downloaded media", size_bytes=len(media_bytes))
                    return media_bytes

            except aiohttp.ClientError as e:
                raise MediaGenerationError(f"Network error during media download: {e}")
