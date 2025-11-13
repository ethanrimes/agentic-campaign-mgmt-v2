# backend/services/rapidapi/base.py

"""Base client for RapidAPI requests."""

import aiohttp
import json
from typing import Dict, Any
from backend.config import settings
from backend.utils import get_logger, APIError

logger = get_logger(__name__)

# Maximum allowed response size in characters (500KB worth of JSON text)
MAX_RESPONSE_SIZE = 500_000


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
        Make request to RapidAPI endpoint with size validation.

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            JSON response

        Raises:
            APIError: If request fails or response is too large
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

                    # Read response text first to check size
                    response_text = await response.text()
                    response_size = len(response_text)

                    # Check if response exceeds size limit
                    if response_size > MAX_RESPONSE_SIZE:
                        logger.error(
                            "Response size exceeds limit",
                            endpoint=endpoint,
                            size=response_size,
                            limit=MAX_RESPONSE_SIZE,
                            params=params
                        )
                        raise APIError(
                            f"Response size ({response_size:,} chars) exceeds maximum allowed size ({MAX_RESPONSE_SIZE:,} chars). "
                            f"Consider using pagination parameters like 'count' or 'limit' to reduce the query size. "
                            f"For endpoints that support pagination, use 'max_id' or 'end_cursor' to fetch data in smaller batches."
                        )

                    # Parse JSON
                    return json.loads(response_text)

            except aiohttp.ClientError as e:
                raise APIError(f"Network error: {e}")
            except json.JSONDecodeError as e:
                raise APIError(f"Failed to parse JSON response: {e}")
