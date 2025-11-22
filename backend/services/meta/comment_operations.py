# backend/services/meta/comment_operations.py

"""Comment operations service for Facebook and Instagram."""

from typing import Dict, Any, List, Optional
from backend.utils import get_logger, APIError
from .base import MetaBaseClient

logger = get_logger(__name__)


class CommentOperations(MetaBaseClient):
    """
    Service for fetching and responding to comments on Facebook and Instagram.

    Supports:
    - Fetching post details
    - Fetching comment details
    - Fetching all comments on a post
    - Posting replies to comments
    """

    # =========================================================================
    # FACEBOOK OPERATIONS
    # =========================================================================

    async def get_facebook_post_context(self, post_id: str) -> Dict[str, Any]:
        """
        Fetch full context for a Facebook post.

        Args:
            post_id: Facebook post ID

        Returns:
            Dictionary with post details including message, attachments, etc.

        Raises:
            APIError: If request fails
        """
        logger.info("Fetching Facebook post context", post_id=post_id)

        url = f"{self.BASE_URL}/{post_id}"
        params = {
            "fields": (
                "message,from,created_time,permalink_url,"
                "attachments{description,media_type,media,url,subattachments},"
                "shares,privacy,updated_time"
            ),
            "access_token": self.page_token
        }

        try:
            result = await self._make_request(
                "GET",
                url,
                data=params
            )
            logger.info("Successfully fetched Facebook post context", post_id=post_id)
            return result
        except Exception as e:
            raise APIError(f"Failed to fetch Facebook post context: {e}")

    async def get_facebook_comment_details(self, comment_id: str) -> Dict[str, Any]:
        """
        Fetch details for a specific Facebook comment.

        Args:
            comment_id: Facebook comment ID

        Returns:
            Dictionary with comment details

        Raises:
            APIError: If request fails
        """
        logger.info("Fetching Facebook comment details", comment_id=comment_id)

        url = f"{self.BASE_URL}/{comment_id}"
        params = {
            "fields": (
                "message,from,created_time,parent,permalink_url,"
                "comment_count,like_count,attachment"
            ),
            "access_token": self.page_token
        }

        try:
            result = await self._make_request(
                "GET",
                url,
                data=params
            )
            logger.info("Successfully fetched Facebook comment", comment_id=comment_id)
            return result
        except Exception as e:
            raise APIError(f"Failed to fetch Facebook comment: {e}")

    async def get_facebook_post_comments(self, post_id: str) -> List[Dict[str, Any]]:
        """
        Fetch all comments on a Facebook post.

        Args:
            post_id: Facebook post ID

        Returns:
            List of comment dictionaries

        Raises:
            APIError: If request fails
        """
        logger.info("Fetching Facebook post comments", post_id=post_id)

        url = f"{self.BASE_URL}/{post_id}/comments"
        params = {
            "fields": (
                "message,from,created_time,parent,permalink_url,"
                "comment_count,like_count"
            ),
            "filter": "stream",  # Include all comments and replies
            "access_token": self.page_token
        }

        try:
            result = await self._make_request(
                "GET",
                url,
                data=params
            )
            comments = result.get("data", [])
            logger.info(
                "Successfully fetched Facebook post comments",
                post_id=post_id,
                count=len(comments)
            )
            return comments
        except Exception as e:
            raise APIError(f"Failed to fetch Facebook post comments: {e}")

    async def reply_to_facebook_comment(
        self,
        comment_id: str,
        message: str
    ) -> str:
        """
        Reply to a Facebook comment.

        Args:
            comment_id: Facebook comment ID to reply to
            message: Reply message text

        Returns:
            ID of the posted reply comment

        Raises:
            APIError: If posting fails
        """
        logger.info(
            "Posting reply to Facebook comment",
            comment_id=comment_id,
            message_preview=message[:50]
        )

        url = f"{self.BASE_URL}/{comment_id}/comments"
        data = {
            "message": message,
            "access_token": self.page_token
        }

        try:
            result = await self._make_request(
                "POST",
                url,
                data=data
            )
            reply_id = result.get("id")
            logger.info(
                "Successfully posted Facebook reply",
                comment_id=comment_id,
                reply_id=reply_id
            )
            return reply_id
        except Exception as e:
            raise APIError(f"Failed to reply to Facebook comment: {e}")

    # =========================================================================
    # INSTAGRAM OPERATIONS
    # =========================================================================

    async def get_instagram_media_list(self) -> List[Dict[str, Any]]:
        """
        Fetch list of all Instagram media for the account.

        Returns:
            List of media dictionaries with IDs

        Raises:
            APIError: If request fails
        """
        logger.info("Fetching Instagram media list")

        url = f"{self.INSTAGRAM_BASE_URL}/me/media"
        params = {
            "fields": "id",
            "access_token": self.ig_token
        }

        try:
            result = await self._make_request(
                "GET",
                url,
                data=params
            )
            media_list = result.get("data", [])
            logger.info(
                "Successfully fetched Instagram media list",
                count=len(media_list)
            )
            return media_list
        except Exception as e:
            raise APIError(f"Failed to fetch Instagram media list: {e}")

    async def get_instagram_media_context(self, media_id: str) -> Dict[str, Any]:
        """
        Fetch full context for an Instagram media post.

        Args:
            media_id: Instagram media ID

        Returns:
            Dictionary with media details including caption, type, URL, etc.

        Raises:
            APIError: If request fails
        """
        logger.info("Fetching Instagram media context", media_id=media_id)

        url = f"{self.INSTAGRAM_BASE_URL}/{media_id}"
        params = {
            "fields": (
                "id,caption,media_type,media_url,thumbnail_url,permalink,"
                "timestamp,username,owner,children{media_type,media_url,thumbnail_url}"
            ),
            "access_token": self.ig_token
        }

        try:
            result = await self._make_request(
                "GET",
                url,
                data=params
            )
            logger.info("Successfully fetched Instagram media context", media_id=media_id)
            return result
        except Exception as e:
            raise APIError(f"Failed to fetch Instagram media context: {e}")

    async def get_instagram_media_comments(self, media_id: str) -> List[Dict[str, Any]]:
        """
        Fetch all comments on an Instagram media post.

        Args:
            media_id: Instagram media ID

        Returns:
            List of comment dictionaries with replies nested

        Raises:
            APIError: If request fails
        """
        logger.info("Fetching Instagram media comments", media_id=media_id)

        url = f"{self.INSTAGRAM_BASE_URL}/{media_id}/comments"
        params = {
            "fields": (
                "id,text,username,timestamp,from,like_count,"
                "replies{id,text,username,timestamp,from,like_count}"
            ),
            "access_token": self.ig_token
        }

        try:
            result = await self._make_request(
                "GET",
                url,
                data=params
            )
            comments = result.get("data", [])
            logger.info(
                "Successfully fetched Instagram media comments",
                media_id=media_id,
                count=len(comments)
            )
            return comments
        except Exception as e:
            raise APIError(f"Failed to fetch Instagram media comments: {e}")

    async def get_instagram_comment_details(self, comment_id: str) -> Dict[str, Any]:
        """
        Fetch details for a specific Instagram comment.

        Args:
            comment_id: Instagram comment ID

        Returns:
            Dictionary with comment details

        Raises:
            APIError: If request fails
        """
        logger.info("Fetching Instagram comment details", comment_id=comment_id)

        url = f"{self.INSTAGRAM_BASE_URL}/{comment_id}"
        params = {
            "fields": (
                "id,text,username,timestamp,from,hidden,like_count,"
                "media,parent_id"
            ),
            "access_token": self.ig_token
        }

        try:
            result = await self._make_request(
                "GET",
                url,
                data=params
            )
            logger.info("Successfully fetched Instagram comment", comment_id=comment_id)
            return result
        except Exception as e:
            raise APIError(f"Failed to fetch Instagram comment: {e}")

    async def reply_to_instagram_comment(
        self,
        comment_id: str,
        message: str
    ) -> str:
        """
        Reply to an Instagram comment.

        Args:
            comment_id: Instagram comment ID to reply to
            message: Reply message text

        Returns:
            ID of the posted reply comment

        Raises:
            APIError: If posting fails
        """
        logger.info(
            "Posting reply to Instagram comment",
            comment_id=comment_id,
            message_preview=message[:50]
        )

        url = f"{self.INSTAGRAM_BASE_URL}/{comment_id}/replies"
        data = {
            "message": message,
            "access_token": self.ig_token
        }

        try:
            result = await self._make_request(
                "POST",
                url,
                data=data
            )
            reply_id = result.get("id")
            logger.info(
                "Successfully posted Instagram reply",
                comment_id=comment_id,
                reply_id=reply_id
            )
            return reply_id
        except Exception as e:
            raise APIError(f"Failed to reply to Instagram comment: {e}")

    # =========================================================================
    # UNIFIED OPERATIONS (works for both platforms)
    # =========================================================================

    async def get_post_context(
        self,
        platform: str,
        post_id: str
    ) -> Dict[str, Any]:
        """
        Unified method to get post context for either platform.

        Args:
            platform: "facebook" or "instagram"
            post_id: Platform-specific post/media ID

        Returns:
            Dictionary with post/media details

        Raises:
            ValueError: If platform is invalid
            APIError: If request fails
        """
        if platform == "facebook":
            return await self.get_facebook_post_context(post_id)
        elif platform == "instagram":
            return await self.get_instagram_media_context(post_id)
        else:
            raise ValueError(f"Invalid platform: {platform}. Must be 'facebook' or 'instagram'")

    async def get_comment_details(
        self,
        platform: str,
        comment_id: str
    ) -> Dict[str, Any]:
        """
        Unified method to get comment details for either platform.

        Args:
            platform: "facebook" or "instagram"
            comment_id: Platform-specific comment ID

        Returns:
            Dictionary with comment details

        Raises:
            ValueError: If platform is invalid
            APIError: If request fails
        """
        if platform == "facebook":
            return await self.get_facebook_comment_details(comment_id)
        elif platform == "instagram":
            return await self.get_instagram_comment_details(comment_id)
        else:
            raise ValueError(f"Invalid platform: {platform}. Must be 'facebook' or 'instagram'")

    async def get_all_comments(
        self,
        platform: str,
        post_id: str
    ) -> List[Dict[str, Any]]:
        """
        Unified method to get all comments for either platform.

        Args:
            platform: "facebook" or "instagram"
            post_id: Platform-specific post/media ID

        Returns:
            List of comment dictionaries

        Raises:
            ValueError: If platform is invalid
            APIError: If request fails
        """
        if platform == "facebook":
            return await self.get_facebook_post_comments(post_id)
        elif platform == "instagram":
            return await self.get_instagram_media_comments(post_id)
        else:
            raise ValueError(f"Invalid platform: {platform}. Must be 'facebook' or 'instagram'")

    async def reply_to_comment(
        self,
        platform: str,
        comment_id: str,
        message: str
    ) -> str:
        """
        Unified method to reply to a comment on either platform.

        Args:
            platform: "facebook" or "instagram"
            comment_id: Platform-specific comment ID
            message: Reply message text

        Returns:
            ID of the posted reply

        Raises:
            ValueError: If platform is invalid
            APIError: If posting fails
        """
        if platform == "facebook":
            return await self.reply_to_facebook_comment(comment_id, message)
        elif platform == "instagram":
            return await self.reply_to_instagram_comment(comment_id, message)
        else:
            raise ValueError(f"Invalid platform: {platform}. Must be 'facebook' or 'instagram'")
