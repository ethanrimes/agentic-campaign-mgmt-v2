# backend/tools/instagram_scraper_tools.py

"""
LangChain tools for Instagram scraping via RapidAPI.
Comprehensive implementation with Pydantic validation.
"""

from typing import Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from backend.services.rapidapi.instagram_scraper import InstagramScraper
from backend.utils import get_logger

logger = get_logger(__name__)


# ============================================================================
# USER PROFILE TOOLS
# ============================================================================

class GetUserProfileInput(BaseModel):
    """Input for GetUserProfile tool."""
    username: str = Field(..., description="Instagram username (without @ symbol)")


class GetUserProfileTool(BaseTool):
    """Tool to get detailed Instagram user profile information."""

    name: str = "get_instagram_user_profile"
    description: str = """
    Get detailed profile information for an Instagram user.
    Returns follower count, bio, links, verification status, and post count.
    Use this to research influencers, competitors, or accounts relevant to your niche.
    """
    args_schema: Type[BaseModel] = GetUserProfileInput

    def _run(self, username: str) -> str:
        """Synchronous wrapper (not implemented - use async version)."""
        raise NotImplementedError("Use async version via _arun")

    async def _arun(self, username: str) -> str:
        """Execute the tool asynchronously."""
        try:
            scraper = InstagramScraper()
            profile = await scraper.get_user_profile(username=username)

            if not profile:
                return f"Could not find profile for @{username}"

            output = f"Instagram Profile: @{username}\n\n"
            output += f"Full Name: {profile.full_name}\n"
            output += f"Bio: {profile.biography}\n"
            output += f"Followers: {profile.follower_count:,}\n"
            output += f"Following: {profile.following_count:,}\n"
            output += f"Posts: {profile.media_count:,}\n"
            output += f"Verified: {'Yes ✓' if profile.is_verified else 'No'}\n"
            output += f"Private: {'Yes' if profile.is_private else 'No'}\n"

            if profile.category:
                output += f"Category: {profile.category}\n"

            if profile.external_url:
                output += f"Website: {profile.external_url}\n"

            if profile.bio_links:
                output += f"\nBio Links ({len(profile.bio_links)}):\n"
                for link in profile.bio_links[:3]:
                    if link.url:
                        output += f"  - {link.title or link.url}\n"

            return output

        except Exception as e:
            logger.error("Error getting user profile", error=str(e))
            return f"Error getting profile for @{username}: {str(e)}"


class GetUserMediaInput(BaseModel):
    """Input for GetUserMedia tool."""
    username: str = Field(..., description="Instagram username (without @ symbol)")
    count: int = Field(12, description="Number of recent posts to fetch (max 50)")


class GetUserMediaTool(BaseTool):
    """Tool to get recent posts from an Instagram user."""

    name: str = "get_instagram_user_media"
    description: str = """
    Get recent posts from an Instagram user's profile.
    Returns post captions, likes, comments, and media types.
    Use this to analyze content from specific accounts, influencers, or competitors.
    Useful for understanding what type of content performs well.
    """
    args_schema: Type[BaseModel] = GetUserMediaInput

    def _run(self, username: str, count: int = 12) -> str:
        """Synchronous wrapper (not implemented - use async version)."""
        raise NotImplementedError("Use async version via _arun")

    async def _arun(self, username: str, count: int = 12) -> str:
        """Execute the tool asynchronously."""
        try:
            # First get user ID from username
            scraper = InstagramScraper()
            user_id_response = await scraper.user_id_from_username(username)

            if not user_id_response:
                return f"Could not find user @{username}"

            # Get user media
            media_response = await scraper.get_user_media(user_id_response.user_id, min(count, 50))

            if not media_response or not media_response.data:
                return f"No media found for @{username}"

            # Extract media from response
            timeline_media = media_response.data.user.edge_owner_to_timeline_media
            edges = timeline_media.edges

            if not edges:
                return f"No posts found for @{username}"

            output = f"Recent Posts from @{username} ({len(edges)} posts):\n\n"

            for i, edge in enumerate(edges[:count], 1):
                # Edge is Dict[str, MediaNode], so extract the node
                node = edge.get("node") if isinstance(edge, dict) else edge
                if not node:
                    continue

                # Access MediaNode attributes directly (it's a Pydantic model)
                shortcode = node.shortcode
                typename = node.typename  # We aliased __typename to typename
                likes = node.edge_liked_by.count if node.edge_liked_by else 0
                comments = node.edge_media_to_comment.count if node.edge_media_to_comment else 0

                # Get caption
                caption = ""
                if node.edge_media_to_caption:
                    caption_edges = node.edge_media_to_caption.get("edges", [])
                    if caption_edges and len(caption_edges) > 0:
                        caption_node = caption_edges[0].get("node", {})
                        if isinstance(caption_node, dict):
                            caption = caption_node.get("text", "")

                media_type = "Photo"
                if typename == "GraphVideo":
                    media_type = "Video"
                elif typename == "GraphSidecar":
                    media_type = "Carousel"

                output += f"{i}. [{media_type}] {shortcode}\n"
                output += f"   Likes: {likes:,} | Comments: {comments:,}\n"
                if caption:
                    output += f"   Caption: {caption[:150]}{'...' if len(caption) > 150 else ''}\n"
                output += f"   URL: https://www.instagram.com/p/{shortcode}/\n\n"

            return output

        except Exception as e:
            logger.error("Error getting user media", error=str(e))
            return f"Error getting media for @{username}: {str(e)}"


# ============================================================================
# SEARCH TOOLS
# ============================================================================

class SearchUsersInput(BaseModel):
    """Input for SearchUsers tool."""
    query: str = Field(..., description="Search query for users")


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
        """Synchronous wrapper (not implemented - use async version)."""
        raise NotImplementedError("Use async version via _arun")

    async def _arun(self, query: str) -> str:
        """Execute the tool asynchronously."""
        try:
            scraper = InstagramScraper()
            result = await scraper.search_users(query)

            if not result or not result.users:
                return f"No users found for query: {query}"

            output = f"Instagram Users for '{query}':\n\n"

            for user_result in result.users[:10]:
                user = user_result.user
                output += f"@{user.username}"
                if user.is_verified:
                    output += " ✓"
                output += "\n"

                if user.full_name:
                    output += f"  Name: {user.full_name}\n"

                if user.follower_count:
                    output += f"  Followers: {user.follower_count:,}\n"

                output += f"  Profile: https://www.instagram.com/{user.username}/\n\n"

            return output

        except Exception as e:
            logger.error("Error searching users", error=str(e))
            return f"Error searching users for '{query}': {str(e)}"


class SearchHashtagsInput(BaseModel):
    """Input for SearchHashtags tool."""
    query: str = Field(..., description="Hashtag search query (without # symbol)")


class SearchHashtagsTool(BaseTool):
    """Tool to search Instagram hashtags."""

    name: str = "search_instagram_hashtags"
    description: str = """
    Search for Instagram hashtags by keyword.
    Returns hashtag names and post counts.
    Use this to discover trending hashtags relevant to your content strategy.
    """
    args_schema: Type[BaseModel] = SearchHashtagsInput

    def _run(self, query: str) -> str:
        """Synchronous wrapper (not implemented - use async version)."""
        raise NotImplementedError("Use async version via _arun")

    async def _arun(self, query: str) -> str:
        """Execute the tool asynchronously."""
        try:
            scraper = InstagramScraper()
            result = await scraper.search_hashtags(query)

            if not result or not result.hashtags:
                return f"No hashtags found for query: {query}"

            output = f"Instagram Hashtags for '{query}':\n\n"

            for hashtag_result in result.hashtags[:10]:
                hashtag = hashtag_result.hashtag
                name = hashtag.get("name", "")
                media_count = hashtag.get("media_count", 0)

                output += f"#{name} - {media_count:,} posts\n"

            return output

        except Exception as e:
            logger.error("Error searching hashtags", error=str(e))
            return f"Error searching hashtags for '{query}': {str(e)}"


class SearchLocationsInput(BaseModel):
    """Input for SearchLocations tool."""
    query: str = Field(..., description="Location search query (e.g., 'philadelphia', 'new york')")


class SearchLocationsTool(BaseTool):
    """Tool to search Instagram locations."""

    name: str = "search_instagram_locations"
    description: str = """
    Search for Instagram locations by keyword.
    Returns location names and IDs.
    Use this to find locations relevant to your target audience or geographic area.
    """
    args_schema: Type[BaseModel] = SearchLocationsInput

    def _run(self, query: str) -> str:
        """Synchronous wrapper (not implemented - use async version)."""
        raise NotImplementedError("Use async version via _arun")

    async def _arun(self, query: str) -> str:
        """Execute the tool asynchronously."""
        try:
            scraper = InstagramScraper()
            result = await scraper.search_locations(query)

            if not result or not result.places:
                return f"No locations found for query: {query}"

            output = f"Instagram Locations for '{query}':\n\n"

            for place_result in result.places[:10]:
                place = place_result.place
                title = place.get("title", "")
                subtitle = place.get("subtitle", "")
                location = place.get("location", {})
                loc_id = location.get("pk", "")

                output += f"{title}\n"
                if subtitle:
                    output += f"  {subtitle}\n"
                if loc_id:
                    output += f"  Location ID: {loc_id}\n"
                output += "\n"

            return output

        except Exception as e:
            logger.error("Error searching locations", error=str(e))
            return f"Error searching locations for '{query}': {str(e)}"


class GetLocationMediaInput(BaseModel):
    """Input for GetLocationMedia tool."""
    location_id: str = Field(..., description="Instagram location ID")
    count: int = Field(10, description="Number of posts to fetch (max 20)")


class GetLocationMediaTool(BaseTool):
    """Tool to get media from an Instagram location."""

    name: str = "get_instagram_location_media"
    description: str = """
    Get top or recent posts from a specific Instagram location.
    Returns posts with captions, likes, and engagement metrics.
    Use this to see what content is popular at specific venues or areas.
    Useful for understanding local trends and community interests.
    """
    args_schema: Type[BaseModel] = GetLocationMediaInput

    def _run(self, location_id: str, count: int = 10) -> str:
        """Synchronous wrapper (not implemented - use async version)."""
        raise NotImplementedError("Use async version via _arun")

    async def _arun(self, location_id: str, count: int = 10) -> str:
        """Execute the tool asynchronously."""
        try:
            scraper = InstagramScraper()
            media_list = await scraper.get_location_media(location_id, tab="ranked")

            if not media_list:
                return f"No media found for location {location_id}"

            output = f"Top Posts from Location {location_id} ({len(media_list[:count])} posts):\n\n"

            for i, media in enumerate(media_list[:count], 1):
                username = media.user.username if media.user else "unknown"
                likes = media.like_count
                comments = media.comment_count
                caption_text = ""

                if media.caption:
                    caption_text = media.caption.text

                output += f"{i}. @{username}\n"
                output += f"   Likes: {likes:,} | Comments: {comments:,}\n"
                if caption_text:
                    output += f"   Caption: {caption_text[:150]}{'...' if len(caption_text) > 150 else ''}\n"
                if media.code:
                    output += f"   URL: https://www.instagram.com/p/{media.code}/\n"
                output += "\n"

            return output

        except Exception as e:
            logger.error("Error getting location media", error=str(e))
            return f"Error getting media for location {location_id}: {str(e)}"


class GlobalSearchInput(BaseModel):
    """Input for GlobalSearch tool."""
    query: str = Field(..., description="Search query for users, hashtags, and locations")


class GlobalSearchTool(BaseTool):
    """Tool to perform global Instagram search."""

    name: str = "search_instagram_global"
    description: str = """
    Perform a global search across Instagram for users, hashtags, and locations.
    Returns mixed results from all categories.
    Use this for broad exploration of topics, themes, or communities.
    Great for initial research when you're not sure what you're looking for.
    """
    args_schema: Type[BaseModel] = GlobalSearchInput

    def _run(self, query: str) -> str:
        """Synchronous wrapper (not implemented - use async version)."""
        raise NotImplementedError("Use async version via _arun")

    async def _arun(self, query: str) -> str:
        """Execute the tool asynchronously."""
        try:
            scraper = InstagramScraper()
            result = await scraper.global_search(query)

            if not result:
                return f"No results found for query: {query}"

            output = f"Instagram Global Search for '{query}':\n\n"

            # Users
            if result.users:
                output += "👤 USERS:\n"
                for user_result in result.users[:5]:
                    user = user_result.user
                    output += f"  @{user.username}"
                    if user.is_verified:
                        output += " ✓"
                    if user.follower_count:
                        output += f" ({user.follower_count:,} followers)"
                    output += "\n"
                output += "\n"

            # Hashtags
            if result.hashtags:
                output += "# HASHTAGS:\n"
                for hashtag_result in result.hashtags[:5]:
                    hashtag = hashtag_result.hashtag
                    name = hashtag.get("name", "")
                    media_count = hashtag.get("media_count", 0)
                    output += f"  #{name} ({media_count:,} posts)\n"
                output += "\n"

            # Locations
            if result.places:
                output += "📍 LOCATIONS:\n"
                for place_result in result.places[:5]:
                    place = place_result.place
                    title = place.get("title", "")
                    subtitle = place.get("subtitle", "")
                    output += f"  {title}"
                    if subtitle:
                        output += f" - {subtitle}"
                    output += "\n"
                output += "\n"

            return output

        except Exception as e:
            logger.error("Error in global search", error=str(e))
            return f"Error in global search for '{query}': {str(e)}"


# ============================================================================
# HASHTAG TOOLS
# ============================================================================

class GetHashtagMediaInput(BaseModel):
    """Input for GetHashtagMedia tool."""
    hashtag: str = Field(..., description="Hashtag to query (without # symbol)")


class GetHashtagMediaTool(BaseTool):
    """Tool to get posts by hashtag."""

    name: str = "get_instagram_hashtag_media"
    description: str = """
    Get top posts using a specific hashtag.
    Returns recent posts with engagement metrics.
    Use this to see what content is trending with specific hashtags.
    Useful for hashtag research and understanding what resonates with audiences.
    """
    args_schema: Type[BaseModel] = GetHashtagMediaInput

    def _run(self, hashtag: str) -> str:
        """Synchronous wrapper (not implemented - use async version)."""
        raise NotImplementedError("Use async version via _arun")

    async def _arun(self, hashtag: str) -> str:
        """Execute the tool asynchronously."""
        try:
            # Remove # if present
            hashtag = hashtag.lstrip('#')

            scraper = InstagramScraper()
            result = await scraper.get_hashtag_media(hashtag)

            if not result or not result.media_data:
                return f"No media found for #{hashtag}"

            output = f"Posts with #{hashtag}:\n"
            output += f"Total posts: {result.hashtag_info.media_count:,}\n\n"

            for i, media in enumerate(result.media_data[:10], 1):
                username = media.user.username if media.user else "unknown"
                likes = media.like_count
                comments = media.comment_count
                caption_text = ""

                if media.caption:
                    caption_text = media.caption.text

                output += f"{i}. @{username}\n"
                output += f"   Likes: {likes:,} | Comments: {comments:,}\n"
                if caption_text:
                    output += f"   Caption: {caption_text[:150]}{'...' if len(caption_text) > 150 else ''}\n"
                if media.code:
                    output += f"   URL: https://www.instagram.com/p/{media.code}/\n"
                output += "\n"

            return output

        except Exception as e:
            logger.error("Error getting hashtag media", error=str(e))
            return f"Error getting media for #{hashtag}: {str(e)}"


# ============================================================================
# TOOL FACTORY
# ============================================================================

def create_instagram_scraper_tools():
    """Create all Instagram scraper tools for use with Langchain agents."""
    return [
        GetUserProfileTool(),
        GetUserMediaTool(),
        SearchUsersTool(),
        SearchHashtagsTool(),
        SearchLocationsTool(),
        GetLocationMediaTool(),
        GlobalSearchTool(),
        GetHashtagMediaTool(),
    ]
