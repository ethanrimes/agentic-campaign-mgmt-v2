# backend/services/rapidapi/facebook_scraper.py

"""
Facebook scraper using RapidAPI (facebook-scraper3).
Comprehensive implementation with Pydantic model validation.
"""

from typing import List, Optional, Literal
from backend.utils import get_logger
from backend.models.rapidapi.facebook_response import (
    # Search
    LocationsSearchResponse,
    VideoSearchResult,
    PostSearchResult,
    PlaceSearchResult,
    PageSearchResult,
    EventSearchResult,
    PersonSearchResult,
    # Pages
    PageIdResponse,
    PageDetails,
    PageDetailsResponse,
    PagePost,
    PagePhotosResponse,
    PageReview,
    PageReel,
    PageEvent,
    PageVideo,
    # Posts and Comments
    Comment,
    PostDetail,
    PostDetailResponse,
    ReshareEntity,
    # Events
    EventDetailsResponse,
    # Groups
    GroupIdResponse,
    GroupPost,
    GroupDetails,
    # Profiles
    ProfileIdResponse,
    ProfilePost,
    ProfileReel,
    ProfileDetails,
)
from .base import RapidAPIBaseClient

logger = get_logger(__name__)


class FacebookScraper(RapidAPIBaseClient):
    """
    Facebook scraper using RapidAPI facebook-scraper3 API.
    All methods return Pydantic models for type safety.
    Size protection is automatically applied via base client.
    """

    def __init__(self):
        super().__init__("facebook-scraper3.p.rapidapi.com")

    # ========================================================================
    # SEARCH METHODS
    # ========================================================================

    async def search_locations(self, query: str) -> Optional[LocationsSearchResponse]:
        """
        Search for Facebook locations.

        Args:
            query: Location query (e.g., "philadelphia")

        Returns:
            Locations response or None on error
        """
        logger.info("Searching locations", query=query)
        try:
            result = await self._make_request("search/locations", {"query": query})
            return LocationsSearchResponse(**result)
        except Exception as e:
            logger.error("Failed to search locations", error=str(e))
            return None

    async def search_videos(
        self,
        query: str,
        cursor: Optional[str] = None,
        recent_videos: bool = False,
        location_uid: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Optional[List[VideoSearchResult]]:
        """
        Search for Facebook videos.

        Args:
            query: Video search query
            cursor: Pagination cursor
            recent_videos: Search recent videos only
            location_uid: Filter by location UID
            start_date: Start date filter (yyyy-mm-dd)
            end_date: End date filter (yyyy-mm-dd)

        Returns:
            List of video results or None on error
        """
        logger.info("Searching videos", query=query)
        try:
            params = {"query": query}
            if cursor:
                params["cursor"] = cursor
            if recent_videos:
                params["recent_videos"] = "true"
            if location_uid:
                params["location_uid"] = location_uid
            if start_date:
                params["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date

            result = await self._make_request("search/videos", params)
            # API returns {"results": [...], "cursor": "..."}
            if isinstance(result, dict) and "results" in result:
                return [VideoSearchResult(**item) for item in result["results"]]
            return []
        except Exception as e:
            logger.error("Failed to search videos", error=str(e))
            return None

    async def search_posts(
        self,
        query: str,
        cursor: Optional[str] = None,
        recent_posts: bool = False,
        location_uid: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Optional[List[PostSearchResult]]:
        """
        Search for Facebook posts.

        Args:
            query: Post search query
            cursor: Pagination cursor
            recent_posts: Search recent posts only
            location_uid: Filter by location UID
            start_date: Start date filter (yyyy-mm-dd)
            end_date: End date filter (yyyy-mm-dd)

        Returns:
            List of post results or None on error
        """
        logger.info("Searching posts", query=query)
        try:
            params = {"query": query}
            if cursor:
                params["cursor"] = cursor
            if recent_posts:
                params["recent_posts"] = "true"
            if location_uid:
                params["location_uid"] = location_uid
            if start_date:
                params["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date

            result = await self._make_request("search/posts", params)
            # API returns {"results": [...], "cursor": "..."}
            if isinstance(result, dict) and "results" in result:
                return [PostSearchResult(**item) for item in result["results"]]
            return []
        except Exception as e:
            logger.error("Failed to search posts", error=str(e))
            return None

    async def search_places(
        self,
        query: str,
        cursor: Optional[str] = None,
        location_uid: Optional[str] = None
    ) -> Optional[List[PlaceSearchResult]]:
        """
        Search for Facebook places/businesses.

        Args:
            query: Place search query
            cursor: Pagination cursor
            location_uid: Filter by location UID

        Returns:
            List of place results or None on error
        """
        logger.info("Searching places", query=query)
        try:
            params = {"query": query}
            if cursor:
                params["cursor"] = cursor
            if location_uid:
                params["location_uid"] = location_uid

            result = await self._make_request("search/places", params)
            # API returns {"results": [...], "cursor": "..."}
            if isinstance(result, dict) and "results" in result:
                return [PlaceSearchResult(**item) for item in result["results"]]
            return []
        except Exception as e:
            logger.error("Failed to search places", error=str(e))
            return None

    async def search_pages(
        self,
        query: str,
        cursor: Optional[str] = None,
        location_uid: Optional[str] = None
    ) -> Optional[List[PageSearchResult]]:
        """
        Search for Facebook pages.

        Args:
            query: Page search query
            cursor: Pagination cursor
            location_uid: Filter by location UID

        Returns:
            List of page results or None on error
        """
        logger.info("Searching pages", query=query)
        try:
            params = {"query": query}
            if cursor:
                params["cursor"] = cursor
            if location_uid:
                params["location_uid"] = location_uid

            result = await self._make_request("search/pages", params)
            # API returns {"results": [...], "cursor": "..."}
            if isinstance(result, dict) and "results" in result:
                return [PageSearchResult(**item) for item in result["results"]]
            return []
        except Exception as e:
            logger.error("Failed to search pages", error=str(e))
            return None

    async def search_events(
        self,
        query: str,
        cursor: Optional[str] = None,
        location_uid: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Optional[List[EventSearchResult]]:
        """
        Search for Facebook events.

        Args:
            query: Event search query
            cursor: Pagination cursor
            location_uid: Filter by location UID
            start_date: Start date filter (yyyy-mm-dd)
            end_date: End date filter (yyyy-mm-dd)

        Returns:
            List of event results or None on error
        """
        logger.info("Searching events", query=query)
        try:
            params = {"query": query}
            if cursor:
                params["cursor"] = cursor
            if location_uid:
                params["location_uid"] = location_uid
            if start_date:
                params["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date

            result = await self._make_request("search/events", params)
            # API returns {"results": [...], "cursor": "..."}
            if isinstance(result, dict) and "results" in result:
                return [EventSearchResult(**item) for item in result["results"]]
            return []
        except Exception as e:
            logger.error("Failed to search events", error=str(e))
            return None

    async def search_people(
        self,
        query: str,
        cursor: Optional[str] = None
    ) -> Optional[List[PersonSearchResult]]:
        """
        Search for Facebook profiles/people.

        Args:
            query: Person search query
            cursor: Pagination cursor

        Returns:
            List of person results or None on error
        """
        logger.info("Searching people", query=query)
        try:
            params = {"query": query}
            if cursor:
                params["cursor"] = cursor

            result = await self._make_request("search/people", params)
            # API returns {"results": [...], "cursor": "..."}
            if isinstance(result, dict) and "results" in result:
                return [PersonSearchResult(**item) for item in result["results"]]
            return []
        except Exception as e:
            logger.error("Failed to search people", error=str(e))
            return None

    async def search_groups_posts(
        self,
        query: str,
        group_id: Optional[str] = None,
        cursor: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Optional[List[PostSearchResult]]:
        """
        Search for posts in Facebook groups.

        Args:
            query: Search query
            group_id: Specific group ID to search in
            cursor: Pagination cursor
            start_date: Start date filter (yyyy-mm-dd)
            end_date: End date filter (yyyy-mm-dd)

        Returns:
            List of post results or None on error
        """
        logger.info("Searching groups posts", query=query, group_id=group_id)
        try:
            params = {"query": query}
            if group_id:
                params["group_id"] = group_id
            if cursor:
                params["cursor"] = cursor
            if start_date:
                params["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date

            result = await self._make_request("search/groups_posts", params)
            # API returns {"results": [...], "cursor": "..."}
            if isinstance(result, dict) and "results" in result:
                return [PostSearchResult(**item) for item in result["results"]]
            return []
        except Exception as e:
            logger.error("Failed to search groups posts", error=str(e))
            return None

    # ========================================================================
    # PAGE METHODS
    # ========================================================================

    async def get_page_id_from_url(self, url: str) -> Optional[PageIdResponse]:
        """
        Get page ID from page URL.

        Args:
            url: Facebook page URL

        Returns:
            Page ID response or None on error
        """
        logger.info("Getting page ID from URL", url=url)
        try:
            result = await self._make_request("page/page_id", {"url": url})
            return PageIdResponse(**result)
        except Exception as e:
            logger.error("Failed to get page ID", error=str(e))
            return None

    async def get_page_details(self, url: str) -> Optional[PageDetails]:
        """
        Get detailed page information.

        Args:
            url: Facebook page URL

        Returns:
            Page details or None on error
        """
        logger.info("Getting page details", url=url)
        try:
            result = await self._make_request("page/details", {"url": url})
            response = PageDetailsResponse(**result)
            return response.results
        except Exception as e:
            logger.error("Failed to get page details", error=str(e))
            return None

    async def get_page_posts(
        self,
        page_id: str,
        cursor: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Optional[List[PagePost]]:
        """
        Get posts from a Facebook page.

        Args:
            page_id: Facebook page ID
            cursor: Pagination cursor
            start_date: Start date filter (yyyy-mm-dd)
            end_date: End date filter (yyyy-mm-dd)

        Returns:
            List of page posts or None on error
        """
        logger.info("Getting page posts", page_id=page_id)
        try:
            params = {"page_id": page_id}
            if cursor:
                params["cursor"] = cursor
            if start_date:
                params["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date

            result = await self._make_request("page/posts", params)
            if isinstance(result, list):
                return [PagePost(**item) for item in result]
            return []
        except Exception as e:
            logger.error("Failed to get page posts", error=str(e))
            return None

    async def get_page_photos(
        self,
        page_id: str,
        cursor: Optional[str] = None,
        collection_id: Optional[str] = None
    ) -> Optional[PagePhotosResponse]:
        """
        Get photos from a Facebook page.

        Args:
            page_id: Facebook page ID
            cursor: Pagination cursor
            collection_id: Collection ID (required with cursor)

        Returns:
            Page photos response or None on error
        """
        logger.info("Getting page photos", page_id=page_id)
        try:
            params = {"page_id": page_id}
            if cursor:
                params["cursor"] = cursor
            if collection_id:
                params["collection_id"] = collection_id

            result = await self._make_request("page/photos", params)
            return PagePhotosResponse(**result)
        except Exception as e:
            logger.error("Failed to get page photos", error=str(e))
            return None

    async def get_page_reviews(
        self,
        page_id: str,
        cursor: Optional[str] = None
    ) -> Optional[List[PageReview]]:
        """
        Get reviews from a Facebook page.

        Args:
            page_id: Facebook page ID
            cursor: Pagination cursor

        Returns:
            List of page reviews or None on error
        """
        logger.info("Getting page reviews", page_id=page_id)
        try:
            params = {"page_id": page_id}
            if cursor:
                params["cursor"] = cursor

            result = await self._make_request("page/reviews", params)
            if isinstance(result, list):
                return [PageReview(**item) for item in result]
            return []
        except Exception as e:
            logger.error("Failed to get page reviews", error=str(e))
            return None

    async def get_page_reels(
        self,
        reels_page_id: Optional[str] = None,
        page_id: Optional[str] = None,
        cursor: Optional[str] = None
    ) -> Optional[List[PageReel]]:
        """
        Get reels from a Facebook page.

        Args:
            reels_page_id: Reels page ID (preferred, get from page details)
            page_id: Page ID (legacy parameter)
            cursor: Pagination cursor

        Returns:
            List of page reels or None on error
        """
        if not reels_page_id and not page_id:
            logger.error("Either reels_page_id or page_id must be provided")
            return None

        logger.info("Getting page reels", reels_page_id=reels_page_id, page_id=page_id)
        try:
            params = {}
            if reels_page_id:
                params["reels_page_id"] = reels_page_id
            elif page_id:
                params["page_id"] = page_id
            if cursor:
                params["cursor"] = cursor

            result = await self._make_request("page/reels", params)
            if isinstance(result, list):
                return [PageReel(**item) for item in result]
            return []
        except Exception as e:
            logger.error("Failed to get page reels", error=str(e))
            return None

    async def get_page_future_events(
        self,
        page_id: str,
        cursor: Optional[str] = None,
        collection_id: Optional[str] = None
    ) -> Optional[List[PageEvent]]:
        """
        Get future events from a Facebook page.

        Args:
            page_id: Facebook page ID
            cursor: Pagination cursor
            collection_id: Collection ID

        Returns:
            List of future events or None on error
        """
        logger.info("Getting page future events", page_id=page_id)
        try:
            params = {"page_id": page_id}
            if cursor:
                params["cursor"] = cursor
            if collection_id:
                params["collection_id"] = collection_id

            result = await self._make_request("page/events/future", params)
            if isinstance(result, list):
                return [PageEvent(**item) for item in result]
            return []
        except Exception as e:
            logger.error("Failed to get page future events", error=str(e))
            return None

    async def get_page_past_events(
        self,
        page_id: str,
        cursor: Optional[str] = None,
        collection_id: Optional[str] = None
    ) -> Optional[List[PageEvent]]:
        """
        Get past events from a Facebook page.

        Args:
            page_id: Facebook page ID
            cursor: Pagination cursor
            collection_id: Collection ID

        Returns:
            List of past events or None on error
        """
        logger.info("Getting page past events", page_id=page_id)
        try:
            params = {"page_id": page_id}
            if cursor:
                params["cursor"] = cursor
            if collection_id:
                params["collection_id"] = collection_id

            result = await self._make_request("page/events/past", params)
            if isinstance(result, list):
                return [PageEvent(**item) for item in result]
            return []
        except Exception as e:
            logger.error("Failed to get page past events", error=str(e))
            return None

    async def get_page_videos(
        self,
        delegate_page_id: str,
        cursor: Optional[str] = None
    ) -> Optional[List[PageVideo]]:
        """
        Get videos from a Facebook page.

        Args:
            delegate_page_id: Delegate page ID (get from page details)
            cursor: Pagination cursor

        Returns:
            List of page videos or None on error
        """
        logger.info("Getting page videos", delegate_page_id=delegate_page_id)
        try:
            params = {"delegate_page_id": delegate_page_id}
            if cursor:
                params["cursor"] = cursor

            result = await self._make_request("page/videos", params)
            if isinstance(result, list):
                return [PageVideo(**item) for item in result]
            return []
        except Exception as e:
            logger.error("Failed to get page videos", error=str(e))
            return None

    # ========================================================================
    # POST AND COMMENT METHODS
    # ========================================================================

    async def get_post_detail(
        self,
        post_id: Optional[str] = None,
        post_url: Optional[str] = None
    ) -> Optional[PostDetailResponse]:
        """
        Get detailed post information.

        Args:
            post_id: Facebook post ID
            post_url: Facebook post URL

        Returns:
            Post detail response or None on error
        """
        if not post_id and not post_url:
            logger.error("Either post_id or post_url must be provided")
            return None

        logger.info("Getting post detail", post_id=post_id, post_url=post_url)
        try:
            params = {}
            if post_id:
                params["post_id"] = post_id
            if post_url:
                params["post_url"] = post_url

            result = await self._make_request("post", params)
            return PostDetailResponse(**result)
        except Exception as e:
            logger.error("Failed to get post detail", error=str(e))
            return None

    async def get_post_comments(
        self,
        post_id: str,
        cursor: Optional[str] = None
    ) -> Optional[List[Comment]]:
        """
        Get comments on a Facebook post.

        Args:
            post_id: Facebook post ID
            cursor: Pagination cursor

        Returns:
            List of comments or None on error
        """
        logger.info("Getting post comments", post_id=post_id)
        try:
            params = {"post_id": post_id}
            if cursor:
                params["cursor"] = cursor

            result = await self._make_request("post/comments", params)
            if isinstance(result, list):
                return [Comment(**item) for item in result]
            return []
        except Exception as e:
            logger.error("Failed to get post comments", error=str(e))
            return None

    async def get_post_reshares(
        self,
        post_id: str,
        cursor: Optional[str] = None
    ) -> Optional[List[ReshareEntity]]:
        """
        Get entities that reshared a post.

        Args:
            post_id: Facebook post ID (use share_id from post details)
            cursor: Pagination cursor

        Returns:
            List of reshare entities or None on error
        """
        logger.info("Getting post reshares", post_id=post_id)
        try:
            params = {"post_id": post_id}
            if cursor:
                params["cursor"] = cursor

            result = await self._make_request("post/reshares", params)
            if isinstance(result, list):
                return [ReshareEntity(**item) for item in result]
            return []
        except Exception as e:
            logger.error("Failed to get post reshares", error=str(e))
            return None

    # ========================================================================
    # EVENT METHODS
    # ========================================================================

    async def get_event_details(self, event_id: str) -> Optional[EventDetailsResponse]:
        """
        Get detailed event information by ID.

        Args:
            event_id: Facebook event ID

        Returns:
            Event details response or None on error
        """
        logger.info("Getting event details", event_id=event_id)
        try:
            result = await self._make_request("event/details_id", {"event_id": event_id})
            return EventDetailsResponse(**result)
        except Exception as e:
            logger.error("Failed to get event details", error=str(e))
            return None

    # ========================================================================
    # GROUP METHODS
    # ========================================================================

    async def get_group_id_from_url(self, url: str) -> Optional[GroupIdResponse]:
        """
        Get group ID from group URL.

        Args:
            url: Facebook group URL

        Returns:
            Group ID response or None on error
        """
        logger.info("Getting group ID from URL", url=url)
        try:
            result = await self._make_request("group/id", {"url": url})
            return GroupIdResponse(**result)
        except Exception as e:
            logger.error("Failed to get group ID", error=str(e))
            return None

    async def get_group_details(self, url: str) -> Optional[GroupDetails]:
        """
        Get detailed group information.

        Args:
            url: Facebook group URL

        Returns:
            Group details or None on error
        """
        logger.info("Getting group details", url=url)
        try:
            result = await self._make_request("group/details", {"url": url})
            return GroupDetails(**result)
        except Exception as e:
            logger.error("Failed to get group details", error=str(e))
            return None

    async def get_group_posts(
        self,
        group_id: str,
        cursor: Optional[str] = None,
        sorting_order: Literal["CHRONOLOGICAL", "TOP_POSTS"] = "CHRONOLOGICAL"
    ) -> Optional[List[GroupPost]]:
        """
        Get posts from a Facebook group.

        Args:
            group_id: Facebook group ID
            cursor: Pagination cursor
            sorting_order: Sort order (CHRONOLOGICAL or TOP_POSTS)

        Returns:
            List of group posts or None on error
        """
        logger.info("Getting group posts", group_id=group_id)
        try:
            params = {"group_id": group_id, "sorting_order": sorting_order}
            if cursor:
                params["cursor"] = cursor

            result = await self._make_request("group/posts", params)
            if isinstance(result, list):
                return [GroupPost(**item) for item in result]
            return []
        except Exception as e:
            logger.error("Failed to get group posts", error=str(e))
            return None

    async def get_group_future_events(
        self,
        group_id: str,
        cursor: Optional[str] = None
    ) -> Optional[List[EventSearchResult]]:
        """
        Get future events from a Facebook group.

        Args:
            group_id: Facebook group ID
            cursor: Pagination cursor

        Returns:
            List of future events or None on error
        """
        logger.info("Getting group future events", group_id=group_id)
        try:
            params = {"group_id": group_id}
            if cursor:
                params["cursor"] = cursor

            result = await self._make_request("group/future_events", params)
            if isinstance(result, list):
                return [EventSearchResult(**item) for item in result]
            return []
        except Exception as e:
            logger.error("Failed to get group future events", error=str(e))
            return None

    # ========================================================================
    # PROFILE METHODS
    # ========================================================================

    async def get_profile_id_from_url(self, url: str) -> Optional[ProfileIdResponse]:
        """
        Get profile ID from profile URL.

        Args:
            url: Facebook profile URL

        Returns:
            Profile ID response or None on error
        """
        logger.info("Getting profile ID from URL", url=url)
        try:
            result = await self._make_request("profile/profile_id", {"url": url})
            return ProfileIdResponse(**result)
        except Exception as e:
            logger.error("Failed to get profile ID", error=str(e))
            return None

    async def get_profile_details_by_url(self, url: str) -> Optional[ProfileDetails]:
        """
        Get profile details by URL.

        Args:
            url: Facebook profile URL

        Returns:
            Profile details or None on error
        """
        logger.info("Getting profile details by URL", url=url)
        try:
            result = await self._make_request("profile/details_url", {"url": url})
            return ProfileDetails(**result)
        except Exception as e:
            logger.error("Failed to get profile details by URL", error=str(e))
            return None

    async def get_profile_details_by_id(self, profile_id: str) -> Optional[ProfileDetails]:
        """
        Get profile details by ID.

        Args:
            profile_id: Facebook profile ID

        Returns:
            Profile details or None on error
        """
        logger.info("Getting profile details by ID", profile_id=profile_id)
        try:
            result = await self._make_request("profile/details_id", {"profile_id": profile_id})
            return ProfileDetails(**result)
        except Exception as e:
            logger.error("Failed to get profile details by ID", error=str(e))
            return None

    async def get_profile_posts(
        self,
        profile_id: str,
        cursor: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Optional[List[ProfilePost]]:
        """
        Get posts from a Facebook profile.

        Args:
            profile_id: Facebook profile ID
            cursor: Pagination cursor
            start_date: Start date filter (yyyy-mm-dd)
            end_date: End date filter (yyyy-mm-dd)

        Returns:
            List of profile posts or None on error
        """
        logger.info("Getting profile posts", profile_id=profile_id)
        try:
            params = {"profile_id": profile_id}
            if cursor:
                params["cursor"] = cursor
            if start_date:
                params["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date

            result = await self._make_request("profile/posts", params)
            if isinstance(result, list):
                return [ProfilePost(**item) for item in result]
            return []
        except Exception as e:
            logger.error("Failed to get profile posts", error=str(e))
            return None

    async def get_profile_reels(
        self,
        reels_profile_id: str,
        cursor: Optional[str] = None
    ) -> Optional[List[ProfileReel]]:
        """
        Get reels from a Facebook profile.

        Args:
            reels_profile_id: Reels profile ID (get from profile details)
            cursor: Pagination cursor

        Returns:
            List of profile reels or None on error
        """
        logger.info("Getting profile reels", reels_profile_id=reels_profile_id)
        try:
            params = {"reels_profile_id": reels_profile_id}
            if cursor:
                params["cursor"] = cursor

            result = await self._make_request("profile/reels", params)
            if isinstance(result, list):
                return [ProfileReel(**item) for item in result]
            return []
        except Exception as e:
            logger.error("Failed to get profile reels", error=str(e))
            return None
