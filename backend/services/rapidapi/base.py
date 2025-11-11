# backend/services/rapidapi/base.py

"""Base client for RapidAPI requests."""

import aiohttp
from typing import Dict, Any
from backend.config import settings
from backend.utils import get_logger, APIError

logger = get_logger(__name__)


class RapidAPIBaseClient:
    """Base client for RapidAPI social media scraping."""

    def __init__(self, api_host: str):
        self.api_key = settings.rapidapi_key
        self.api_host = api_host

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with RapidAPI authentication."""
        return {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": self.api_host,
        }

    async def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make request to RapidAPI endpoint.

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            JSON response

        Raises:
            APIError: If request fails
        """
        url = f"https://{self.api_host}/{endpoint}"

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=self._get_headers(), params=params) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise APIError(
                            f"RapidAPI error",
                            status_code=response.status,
                            response_body=error_text,
                        )

                    return await response.json()

            except aiohttp.ClientError as e:
                raise APIError(f"Network error: {e}")
