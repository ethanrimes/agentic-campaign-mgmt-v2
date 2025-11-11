# backend/services/rapidapi/instagram_scraper.py

"""Instagram scraping via RapidAPI."""

from typing import List, Dict, Any
from backend.utils import get_logger
from .base import RapidAPIBaseClient

logger = get_logger(__name__)


class InstagramScraper(RapidAPIBaseClient):
    """
    Instagram scraper using RapidAPI.

    Provides methods to search locations, users, hashtags, and posts.
    """

    def __init__(self):
        # Using instagram-looter2 as example (replace with your actual RapidAPI service)
        super().__init__("instagram-looter2.p.rapidapi.com")

    async def search_locations(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for locations by keyword.

        Args:
            query: Search query (e.g., "newyork", "philadelphia")

        Returns:
            List of location objects
        """
        logger.info("Searching Instagram locations", query=query)

        try:
            result = await self._make_request("search", {"query": query, "select": "locations"})
            return result.get("data", [])
        except Exception as e:
            logger.error("Failed to search locations", error=str(e))
            return []

    async def get_location_media(self, location_id: str, tab: str = "ranked") -> List[Dict[str, Any]]:
        """
        Get media posts for a location.

        Args:
            location_id: Instagram location ID
            tab: "ranked" or "recent"

        Returns:
            List of post objects
        """
        logger.info("Fetching location media", location_id=location_id)

        try:
            result = await self._make_request("location-feeds", {"id": location_id, "tab": tab})
            return result.get("data", [])
        except Exception as e:
            logger.error("Failed to get location media", error=str(e))
            return []

    async def search_hashtag(self, hashtag: str) -> List[Dict[str, Any]]:
        """
        Search for posts by hashtag.

        Args:
            hashtag: Hashtag to search (without #)

        Returns:
            List of post objects
        """
        logger.info("Searching Instagram hashtag", hashtag=hashtag)

        try:
            result = await self._make_request("search", {"query": hashtag, "select": "hashtags"})
            return result.get("data", [])
        except Exception as e:
            logger.error("Failed to search hashtag", error=str(e))
            return []

    async def search_users(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for users.

        Args:
            query: Username or name to search

        Returns:
            List of user objects
        """
        logger.info("Searching Instagram users", query=query)

        try:
            result = await self._make_request("search", {"query": query, "select": "users"})
            return result.get("data", [])
        except Exception as e:
            logger.error("Failed to search users", error=str(e))
            return []

    async def global_search(self, query: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Perform global search (users, hashtags, locations).

        Args:
            query: Search query

        Returns:
            Dictionary with "users", "hashtags", "locations" keys
        """
        logger.info("Instagram global search", query=query)

        try:
            result = await self._make_request("search", {"query": query})
            return {
                "users": result.get("users", []),
                "hashtags": result.get("hashtags", []),
                "locations": result.get("locations", []),
                "posts": result.get("posts", []),
            }
        except Exception as e:
            logger.error("Failed global search", error=str(e))
            return {"users": [], "hashtags": [], "locations": [], "posts": []}
