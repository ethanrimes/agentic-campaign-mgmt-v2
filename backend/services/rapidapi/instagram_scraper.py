# backend/services/rapidapi/instagram_scraper.py

"""
Instagram scraper using RapidAPI (instagram-looter2).
Comprehensive implementation with Pydantic model validation.
"""

from typing import List, Optional, Literal
from backend.utils import get_logger
from backend.models.rapidapi.instagram_response import (
    # Identity
    UsernameFromIdResponse,
    UserIdFromUsernameResponse,
    MediaShortcodeResponse,
    # User profiles
    UserProfile,
    WebProfileResponse,
    UserTimelineResponse,
    UserReelsResponse,
    UserRepostsResponse,
    RelatedProfilesResponse,
    # Media
    MediaDetailResponse,
    TimelineMedia,
    # Search
    SearchUsersResponse,
    SearchHashtagsResponse,
    SearchLocationsResponse,
    GlobalSearchResponse,
    # Hashtags
    HashtagMediaResponse,
    # Locations
    LocationInfoResponse,
    LocationMediaResponse,
    CitiesResponse,
    LocationsResponse,
    # Music
    MusicResponse,
    # Explore
    ExploreSectionsResponse,
    SectionMediaResponse,
)
from .base import RapidAPIBaseClient

logger = get_logger(__name__)


class InstagramScraper(RapidAPIBaseClient):
    """
    Instagram scraper using RapidAPI instagram-looter2 API.
    All methods return Pydantic models for type safety.
    """

    def __init__(self):
        super().__init__("instagram-looter2.p.rapidapi.com")

    # ========================================================================
    # IDENTITY UTILITIES
    # ========================================================================

    async def username_from_id(self, user_id: str) -> Optional[UsernameFromIdResponse]:
        """
        Get username from user ID.

        Args:
            user_id: Instagram user ID

        Returns:
            Username response or None on error
        """
        logger.info("Getting username from ID", user_id=user_id)
        try:
            result = await self._make_request("id", {"id": user_id})
            return UsernameFromIdResponse(**result)
        except Exception as e:
            logger.error("Failed to get username", error=str(e))
            return None

    async def user_id_from_username(self, username: str) -> Optional[UserIdFromUsernameResponse]:
        """
        Get user ID from username.

        Args:
            username: Instagram username

        Returns:
            User ID response or None on error
        """
        logger.info("Getting user ID from username", username=username)
        try:
            result = await self._make_request("id", {"username": username})
            return UserIdFromUsernameResponse(**result)
        except Exception as e:
            logger.error("Failed to get user ID", error=str(e))
            return None

    async def shortcode_from_media_id(self, media_id: str) -> Optional[MediaShortcodeResponse]:
        """
        Get media shortcode from media ID.

        Args:
            media_id: Instagram media ID

        Returns:
            Shortcode response or None on error
        """
        logger.info("Getting shortcode from media ID", media_id=media_id)
        try:
            result = await self._make_request("id-media", {"id": media_id})
            return MediaShortcodeResponse(**result)
        except Exception as e:
            logger.error("Failed to get shortcode", error=str(e))
            return None

    async def media_id_from_url(self, url: str) -> Optional[MediaShortcodeResponse]:
        """
        Get media ID from media URL.

        Args:
            url: Instagram post URL

        Returns:
            Media ID response or None on error
        """
        logger.info("Getting media ID from URL", url=url)
        try:
            result = await self._make_request("id-media", {"url": url})
            return MediaShortcodeResponse(**result)
        except Exception as e:
            logger.error("Failed to get media ID", error=str(e))
            return None

    # ========================================================================
    # USER PROFILE METHODS
    # ========================================================================

    async def get_user_profile(
        self,
        username: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Optional[UserProfile]:
        """
        Get detailed user profile information.

        Args:
            username: Instagram username (either username or user_id required)
            user_id: Instagram user ID (either username or user_id required)

        Returns:
            User profile or None on error
        """
        if not username and not user_id:
            logger.error("Either username or user_id must be provided")
            return None

        params = {"username": username} if username else {"id": user_id}
        logger.info("Getting user profile", params=params)

        try:
            result = await self._make_request("profile2", params)
            return UserProfile(**result)
        except Exception as e:
            logger.error("Failed to get user profile", error=str(e))
            return None

    async def get_web_profile(self, username: str) -> Optional[WebProfileResponse]:
        """
        Get web profile information (includes recent posts).

        Args:
            username: Instagram username

        Returns:
            Web profile response or None on error
        """
        logger.info("Getting web profile", username=username)
        try:
            result = await self._make_request("web-profile", {"username": username})
            return WebProfileResponse(**result)
        except Exception as e:
            logger.error("Failed to get web profile", error=str(e))
            return None

    async def get_user_media(
        self,
        user_id: str,
        count: int = 12
    ) -> Optional[UserTimelineResponse]:
        """
        Get user's timeline media (posts).

        Args:
            user_id: Instagram user ID
            count: Number of posts to fetch (default: 12)

        Returns:
            Timeline response or None on error
        """
        logger.info("Getting user media", user_id=user_id, count=count)
        try:
            result = await self._make_request("user-feeds2", {"id": user_id, "count": count})
            return UserTimelineResponse(**result)
        except Exception as e:
            logger.error("Failed to get user media", error=str(e))
            return None

    async def get_user_reels(
        self,
        user_id: str,
        count: int = 12
    ) -> Optional[List[TimelineMedia]]:
        """
        Get user's reels.

        Args:
            user_id: Instagram user ID
            count: Number of reels to fetch (default: 12)

        Returns:
            List of reels or empty list on error
        """
        logger.info("Getting user reels", user_id=user_id, count=count)
        try:
            result = await self._make_request("reels", {"id": user_id, "count": count})
            # Result is an array of media objects
            if isinstance(result, list):
                return [TimelineMedia(**item.get("media", {})) for item in result if "media" in item]
            return []
        except Exception as e:
            logger.error("Failed to get user reels", error=str(e))
            return []

    async def get_user_reposts(self, user_id: str) -> Optional[UserRepostsResponse]:
        """
        Get user's reposts.

        Args:
            user_id: Instagram user ID

        Returns:
            Reposts response or None on error
        """
        logger.info("Getting user reposts", user_id=user_id)
        try:
            result = await self._make_request("user-reposts", {"id": user_id})
            return UserRepostsResponse(**result)
        except Exception as e:
            logger.error("Failed to get user reposts", error=str(e))
            return None

    async def get_user_tagged_media(
        self,
        user_id: str,
        count: int = 12
    ) -> Optional[dict]:
        """
        Get media where user is tagged.

        Args:
            user_id: Instagram user ID
            count: Number of posts to fetch

        Returns:
            Tagged media data or None on error
        """
        logger.info("Getting user tagged media", user_id=user_id, count=count)
        try:
            result = await self._make_request("user-tags", {"id": user_id, "count": count})
            return result
        except Exception as e:
            logger.error("Failed to get tagged media", error=str(e))
            return None

    async def get_related_profiles(self, user_id: str) -> Optional[RelatedProfilesResponse]:
        """
        Get profiles related to this user.

        Args:
            user_id: Instagram user ID

        Returns:
            Related profiles response or None on error
        """
        logger.info("Getting related profiles", user_id=user_id)
        try:
            result = await self._make_request("related-profiles", {"id": user_id})
            return RelatedProfilesResponse(**result)
        except Exception as e:
            logger.error("Failed to get related profiles", error=str(e))
            return None

    # ========================================================================
    # MEDIA DETAIL METHODS
    # ========================================================================

    async def get_media_detail(
        self,
        post_url: Optional[str] = None,
        media_id: Optional[str] = None
    ) -> Optional[MediaDetailResponse]:
        """
        Get detailed media information.

        Args:
            post_url: Instagram post URL (either post_url or media_id required)
            media_id: Instagram media ID (either post_url or media_id required)

        Returns:
            Media detail response or None on error
        """
        if not post_url and not media_id:
            logger.error("Either post_url or media_id must be provided")
            return None

        params = {"url": post_url} if post_url else {"id": media_id}
        logger.info("Getting media detail", params=params)

        try:
            result = await self._make_request("post", params)
            return MediaDetailResponse(**result)
        except Exception as e:
            logger.error("Failed to get media detail", error=str(e))
            return None

    # ========================================================================
    # SEARCH METHODS
    # ========================================================================

    async def search_users(self, query: str) -> Optional[SearchUsersResponse]:
        """
        Search for users by username or name.

        Args:
            query: Search query

        Returns:
            Search users response or None on error
        """
        logger.info("Searching users", query=query)
        try:
            result = await self._make_request("search", {"query": query, "select": "users"})
            return SearchUsersResponse(**result)
        except Exception as e:
            logger.error("Failed to search users", error=str(e))
            return None

    async def search_hashtags(self, query: str) -> Optional[SearchHashtagsResponse]:
        """
        Search for hashtags by keyword.

        Args:
            query: Search query (without # symbol)

        Returns:
            Search hashtags response or None on error
        """
        logger.info("Searching hashtags", query=query)
        try:
            result = await self._make_request("search", {"query": query, "select": "hashtags"})
            return SearchHashtagsResponse(**result)
        except Exception as e:
            logger.error("Failed to search hashtags", error=str(e))
            return None

    async def search_locations(self, query: str) -> Optional[SearchLocationsResponse]:
        """
        Search for locations by keyword.

        Args:
            query: Search query

        Returns:
            Search locations response or None on error
        """
        logger.info("Searching locations", query=query)
        try:
            result = await self._make_request("search", {"query": query, "select": "locations"})
            return SearchLocationsResponse(**result)
        except Exception as e:
            logger.error("Failed to search locations", error=str(e))
            return None

    async def global_search(self, query: str) -> Optional[GlobalSearchResponse]:
        """
        Perform global search across users, hashtags, and locations.

        Args:
            query: Search query

        Returns:
            Global search response or None on error
        """
        logger.info("Global search", query=query)
        try:
            result = await self._make_request("search", {"query": query})
            return GlobalSearchResponse(**result)
        except Exception as e:
            logger.error("Failed global search", error=str(e))
            return None

    # ========================================================================
    # HASHTAG METHODS
    # ========================================================================

    async def get_hashtag_media(self, hashtag: str) -> Optional[HashtagMediaResponse]:
        """
        Get media posts by hashtag.

        Args:
            hashtag: Hashtag to query (without # symbol)

        Returns:
            Hashtag media response or None on error
        """
        logger.info("Getting hashtag media", hashtag=hashtag)
        try:
            result = await self._make_request("tag-feeds", {"query": hashtag})
            return HashtagMediaResponse(**result)
        except Exception as e:
            logger.error("Failed to get hashtag media", error=str(e))
            return None

    # ========================================================================
    # LOCATION METHODS
    # ========================================================================

    async def get_location_info(self, location_id: str) -> Optional[LocationInfoResponse]:
        """
        Get location information by ID.

        Args:
            location_id: Instagram location ID

        Returns:
            Location info response or None on error
        """
        logger.info("Getting location info", location_id=location_id)
        try:
            result = await self._make_request("location-info", {"id": location_id})
            return LocationInfoResponse(**result)
        except Exception as e:
            logger.error("Failed to get location info", error=str(e))
            return None

    async def get_location_media(
        self,
        location_id: str,
        tab: Literal["ranked", "recent"] = "ranked"
    ) -> Optional[List[TimelineMedia]]:
        """
        Get media posts from a location.

        Args:
            location_id: Instagram location ID
            tab: Media tab - "ranked" or "recent" (default: "ranked")

        Returns:
            List of timeline media or empty list on error
        """
        logger.info("Getting location media", location_id=location_id, tab=tab)
        try:
            result = await self._make_request("location-feeds", {"id": location_id, "tab": tab})
            if isinstance(result, list):
                return [TimelineMedia(**item) for item in result]
            return []
        except Exception as e:
            logger.error("Failed to get location media", error=str(e))
            return []

    async def get_cities(
        self,
        country_code: str,
        page: int = 1
    ) -> Optional[CitiesResponse]:
        """
        Get cities by country code.

        Args:
            country_code: Country code (e.g., "US")
            page: Page number for pagination (default: 1)

        Returns:
            Cities response or None on error
        """
        logger.info("Getting cities", country_code=country_code, page=page)
        try:
            result = await self._make_request("cities", {"country_code": country_code, "page": page})
            return CitiesResponse(**result)
        except Exception as e:
            logger.error("Failed to get cities", error=str(e))
            return None

    async def get_locations_by_city(
        self,
        city_id: str,
        page: int = 1
    ) -> Optional[LocationsResponse]:
        """
        Get locations by city ID.

        Args:
            city_id: City ID
            page: Page number for pagination (default: 1)

        Returns:
            Locations response or None on error
        """
        logger.info("Getting locations by city", city_id=city_id, page=page)
        try:
            result = await self._make_request("locations", {"city_id": city_id, "page": page})
            return LocationsResponse(**result)
        except Exception as e:
            logger.error("Failed to get locations", error=str(e))
            return None

    # ========================================================================
    # MUSIC METHODS
    # ========================================================================

    async def get_music_info(self, music_id: str) -> Optional[MusicResponse]:
        """
        Get music/audio information by ID.

        Args:
            music_id: Music asset ID

        Returns:
            Music response or None on error
        """
        logger.info("Getting music info", music_id=music_id)
        try:
            result = await self._make_request("music", {"id": music_id})
            return MusicResponse(**result)
        except Exception as e:
            logger.error("Failed to get music info", error=str(e))
            return None

    # ========================================================================
    # EXPLORE SECTION METHODS
    # ========================================================================

    async def get_explore_sections(self) -> Optional[List[dict]]:
        """
        Get list of all explore sections.

        Returns:
            List of explore sections or empty list on error
        """
        logger.info("Getting explore sections")
        try:
            result = await self._make_request("sections", {})
            if isinstance(result, list):
                return result
            return []
        except Exception as e:
            logger.error("Failed to get explore sections", error=str(e))
            return []

    async def get_section_media(
        self,
        section_id: str,
        count: int = 20
    ) -> Optional[SectionMediaResponse]:
        """
        Get media from a specific explore section.

        Args:
            section_id: Section ID
            count: Number of items to fetch (default: 20)

        Returns:
            Section media response or None on error
        """
        logger.info("Getting section media", section_id=section_id, count=count)
        try:
            result = await self._make_request("section", {"id": section_id, "count": count})
            return SectionMediaResponse(**result)
        except Exception as e:
            logger.error("Failed to get section media", error=str(e))
            return None
