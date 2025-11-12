# backend/tools/instagram_scraper_tools.py

"""Langchain tools for Instagram scraping via RapidAPI."""

from typing import Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from backend.services.rapidapi.instagram_scraper import InstagramScraper
from backend.utils import get_logger

logger = get_logger(__name__)


class SearchLocationsInput(BaseModel):
    """Input for SearchLocations tool."""
    query: str = Field(..., description="Location search query (e.g., 'philadelphia', 'new york')")


class SearchLocationsTool(BaseTool):
    """Tool to search Instagram locations by keyword."""

    name: str = "search_instagram_locations"
    description: str = """
    Search for Instagram locations by keyword.
    Returns location IDs, names, and metadata.
    Use this to find locations relevant to your target audience or geographic area.
    """
    args_schema: Type[BaseModel] = SearchLocationsInput

    def _run(self, query: str) -> str:
        """Sync version - not used by async agents."""
        raise NotImplementedError("Use async version (_arun) instead")

    async def _arun(self, query: str) -> str:
        """Execute the tool asynchronously."""
        try:
            scraper = InstagramScraper()
            locations = await scraper.search_locations(query)

            if not locations:
                return f"No locations found for query: {query}"

            output = f"Instagram Locations for '{query}':\n\n"
            for i, loc in enumerate(locations[:10], 1):  # Limit to 10
                name = loc.get("name", "Unknown")
                loc_id = loc.get("pk", "N/A")
                address = loc.get("address", "")
                output += f"{i}. {name} (ID: {loc_id})\n"
                if address:
                    output += f"   Address: {address}\n"
                output += "\n"

            return output
        except Exception as e:
            logger.error("Error searching locations", error=str(e))
            return f"Error searching locations: {str(e)}"


class GetLocationMediaInput(BaseModel):
    """Input for GetLocationMedia tool."""
    location_id: str = Field(..., description="Instagram location ID")
    tab: str = Field("ranked", description="Media tab: 'ranked' or 'recent'")


class GetLocationMediaTool(BaseTool):
    """Tool to get media posts from an Instagram location."""

    name: str = "get_instagram_location_media"
    description: str = """
    Get media posts from a specific Instagram location.
    Returns recent or top-ranked posts from that location.
    Use this to see what content is popular at specific venues or areas.
    """
    args_schema: Type[BaseModel] = GetLocationMediaInput

    def _run(self, location_id: str, tab: str = "ranked") -> str:
        """Sync version - not used by async agents."""
        raise NotImplementedError("Use async version (_arun) instead")

    async def _arun(self, location_id: str, tab: str = "ranked") -> str:
        """Execute the tool asynchronously."""
        try:
            scraper = InstagramScraper()
            media = await scraper.get_location_media(location_id, tab)

            if not media:
                return f"No media found for location {location_id}"

            output = f"Instagram Media from Location {location_id} ({tab}):\n\n"
            for i, post in enumerate(media[:10], 1):  # Limit to 10
                code = post.get("code", "N/A")
                caption = post.get("caption", {}).get("text", "[No caption]")
                likes = post.get("like_count", 0)
                comments = post.get("comment_count", 0)

                output += f"{i}. Post: {code}\n"
                output += f"   Likes: {likes}, Comments: {comments}\n"
                output += f"   Caption: {caption[:100]}...\n"
                output += f"   Link: https://www.instagram.com/p/{code}/\n\n"

            return output
        except Exception as e:
            logger.error("Error getting location media", error=str(e))
            return f"Error getting location media: {str(e)}"


class SearchHashtagsInput(BaseModel):
    """Input for SearchHashtags tool."""
    query: str = Field(..., description="Hashtag search query (without # symbol)")


class SearchHashtagsTool(BaseTool):
    """Tool to search Instagram hashtags."""

    name: str = "search_instagram_hashtags"
    description: str = """
    Search for Instagram hashtags by keyword.
    Returns hashtag names, post counts, and metadata.
    Use this to discover trending hashtags relevant to your content.
    """
    args_schema: Type[BaseModel] = SearchHashtagsInput

    def _run(self, query: str) -> str:
        """Sync version - not used by async agents."""
        raise NotImplementedError("Use async version (_arun) instead")

    async def _arun(self, query: str) -> str:
        """Execute the tool asynchronously."""
        try:
            scraper = InstagramScraper()
            hashtags = await scraper.search_hashtags(query)

            if not hashtags:
                return f"No hashtags found for query: {query}"

            output = f"Instagram Hashtags for '{query}':\n\n"
            for i, tag in enumerate(hashtags[:10], 1):
                name = tag.get("name", "unknown")
                post_count = tag.get("media_count", 0)
                output += f"{i}. #{name} ({post_count:,} posts)\n"

            return output
        except Exception as e:
            logger.error("Error searching hashtags", error=str(e))
            return f"Error searching hashtags: {str(e)}"


class SearchUsersInput(BaseModel):
    """Input for SearchUsers tool."""
    query: str = Field(..., description="Username or name search query")


class SearchUsersTool(BaseTool):
    """Tool to search Instagram users."""

    name: str = "search_instagram_users"
    description: str = """
    Search for Instagram users by username or name.
    Returns user profiles with follower counts and verification status.
    Use this to find influencers, competitors, or relevant accounts in your niche.
    """
    args_schema: Type[BaseModel] = SearchUsersInput

    def _run(self, query: str) -> str:
        """Sync version - not used by async agents."""
        raise NotImplementedError("Use async version (_arun) instead")

    async def _arun(self, query: str) -> str:
        """Execute the tool asynchronously."""
        try:
            scraper = InstagramScraper()
            users = await scraper.search_users(query)

            if not users:
                return f"No users found for query: {query}"

            output = f"Instagram Users for '{query}':\n\n"
            for i, user in enumerate(users[:10], 1):
                username = user.get("username", "unknown")
                full_name = user.get("full_name", "")
                follower_count = user.get("follower_count", 0)
                is_verified = user.get("is_verified", False)

                output += f"{i}. @{username}"
                if is_verified:
                    output += " ✓"
                output += "\n"
                if full_name:
                    output += f"   Name: {full_name}\n"
                output += f"   Followers: {follower_count:,}\n"
                output += f"   Profile: https://www.instagram.com/{username}/\n\n"

            return output
        except Exception as e:
            logger.error("Error searching users", error=str(e))
            return f"Error searching users: {str(e)}"


class GetUserMediaInput(BaseModel):
    """Input for GetUserMedia tool."""
    username: str = Field(..., description="Instagram username (without @ symbol)")


class GetUserMediaTool(BaseTool):
    """Tool to get recent media from an Instagram user."""

    name: str = "get_instagram_user_media"
    description: str = """
    Get recent media posts from an Instagram user's profile.
    Returns their latest posts with captions, likes, and comments.
    Use this to analyze content from specific accounts or influencers.
    """
    args_schema: Type[BaseModel] = GetUserMediaInput

    def _run(self, username: str) -> str:
        """Sync version - not used by async agents."""
        raise NotImplementedError("Use async version (_arun) instead")

    async def _arun(self, username: str) -> str:
        """Execute the tool asynchronously."""
        try:
            scraper = InstagramScraper()
            media = await scraper.get_user_media(username)

            if not media:
                return f"No media found for user @{username}"

            output = f"Recent Instagram Posts from @{username}:\n\n"
            for i, post in enumerate(media[:10], 1):
                code = post.get("code", "N/A")
                caption = post.get("caption", {}).get("text", "[No caption]")
                likes = post.get("like_count", 0)
                comments = post.get("comment_count", 0)

                output += f"{i}. Post: {code}\n"
                output += f"   Likes: {likes}, Comments: {comments}\n"
                output += f"   Caption: {caption[:100]}...\n"
                output += f"   Link: https://www.instagram.com/p/{code}/\n\n"

            return output
        except Exception as e:
            logger.error("Error getting user media", error=str(e))
            return f"Error getting user media: {str(e)}"


class GlobalSearchInput(BaseModel):
    """Input for GlobalSearch tool."""
    query: str = Field(..., description="Search query for users, hashtags, and locations")


class GlobalSearchTool(BaseTool):
    """Tool to perform global search across Instagram."""

    name: str = "search_instagram_global"
    description: str = """
    Perform a global search across Instagram for users, hashtags, and locations.
    Returns mixed results from all categories.
    Use this for broad exploration of topics or themes.
    """
    args_schema: Type[BaseModel] = GlobalSearchInput

    def _run(self, query: str) -> str:
        """Sync version - not used by async agents."""
        raise NotImplementedError("Use async version (_arun) instead")

    async def _arun(self, query: str) -> str:
        """Execute the tool asynchronously."""
        try:
            scraper = InstagramScraper()
            results = await scraper.global_search(query)

            if not results:
                return f"No results found for query: {query}"

            output = f"Instagram Global Search for '{query}':\n\n"

            # Users
            users = results.get("users", [])
            if users:
                output += "👤 Users:\n"
                for user in users[:5]:
                    username = user.get("username", "unknown")
                    followers = user.get("follower_count", 0)
                    output += f"  - @{username} ({followers:,} followers)\n"
                output += "\n"

            # Hashtags
            hashtags = results.get("hashtags", [])
            if hashtags:
                output += "# Hashtags:\n"
                for tag in hashtags[:5]:
                    name = tag.get("name", "unknown")
                    posts = tag.get("media_count", 0)
                    output += f"  - #{name} ({posts:,} posts)\n"
                output += "\n"

            # Locations
            locations = results.get("places", [])
            if locations:
                output += "📍 Locations:\n"
                for loc in locations[:5]:
                    name = loc.get("name", "unknown")
                    loc_id = loc.get("pk", "")
                    output += f"  - {name} (ID: {loc_id})\n"
                output += "\n"

            return output
        except Exception as e:
            logger.error("Error in global search", error=str(e))
            return f"Error in global search: {str(e)}"


def create_instagram_scraper_tools():
    """Create all Instagram scraper tools for use with Langchain agents."""
    return [
        SearchLocationsTool(),
        GetLocationMediaTool(),
        SearchHashtagsTool(),
        SearchUsersTool(),
        GetUserMediaTool(),
        GlobalSearchTool(),
    ]
