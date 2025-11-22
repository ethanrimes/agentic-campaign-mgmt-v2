# backend/services/meta/base.py

"""Base client for Meta Graph API."""

import aiohttp
from typing import Dict, Any
from backend.config import settings
from backend.utils import get_logger, APIError

logger = get_logger(__name__)


class MetaBaseClient:
    """Base client for Meta Graph API operations."""

    API_VERSION = "v24.0"
    BASE_URL = f"https://graph.facebook.com/{API_VERSION}"
    INSTAGRAM_BASE_URL = f"https://graph.instagram.com/{API_VERSION}"

    def __init__(self):
        self.page_id = settings.facebook_page_id
        self.ig_user_id = settings.app_users_instagram_account_id
        self.page_token = settings.facebook_page_access_token
        self.ig_token = settings.instagram_page_access_token

    async def _make_request(
        self,
        method: str,
        url: str,
        data: Dict[str, Any] = None,
        json_data: Dict[str, Any] = None,
        headers: Dict[str, str] = None,
    ) -> Dict[str, Any]:
        """
        Make HTTP request to Meta API.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Full URL
            data: For GET requests, these become query parameters. For POST, form data.
            json_data: JSON data
            headers: Request headers

        Returns:
            JSON response

        Raises:
            APIError: If request fails
        """
        # For GET requests, data should be sent as query params
        # For POST requests, data should be sent as form data
        params = None
        form_data = None

        if method.upper() == "GET":
            params = data
        else:
            form_data = data

        async with aiohttp.ClientSession() as session:
            try:
                async with session.request(
                    method, url, params=params, data=form_data, json=json_data, headers=headers
                ) as response:
                    result = await response.json()

                    if response.status != 200:
                        error = result.get("error", {})
                        error_msg = error.get("message", "Unknown error")
                        raise APIError(
                            f"Meta API error: {error_msg}",
                            status_code=response.status,
                            response_body=str(result),
                        )

                    return result

            except aiohttp.ClientError as e:
                raise APIError(f"Network error: {e}")
