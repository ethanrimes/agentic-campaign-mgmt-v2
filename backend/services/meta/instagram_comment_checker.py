# backend/services/meta/instagram_comment_checker.py

"""
Instagram comment checker service.

Since Instagram doesn't provide webhooks for comments, this service
periodically checks for new comments on Instagram posts and adds them
to the database for processing by the comment responder agent.
"""

from typing import Dict, Any, List
from datetime import datetime
from backend.services.meta.comment_operations import CommentOperations
from backend.database.repositories.platform_comments import PlatformCommentRepository
from backend.utils import get_logger

logger = get_logger(__name__)


class InstagramCommentChecker:
    """
    Service to check for new Instagram comments and add them to the database.

    Since Instagram doesn't support webhooks for comments, we need to poll
    periodically to discover new comments.
    """

    def __init__(self, business_asset_id: str):
        """
        Initialize Instagram comment checker for a specific business asset.

        Args:
            business_asset_id: The unique identifier for the business asset
        """
        self.business_asset_id = business_asset_id
        self.comment_ops = CommentOperations(business_asset_id)
        self.comment_repo = PlatformCommentRepository()

    async def check_for_new_comments(
        self,
        max_media_to_check: int = 20
    ) -> Dict[str, Any]:
        """
        Check for new comments on recent Instagram media.

        Args:
            max_media_to_check: Maximum number of recent media posts to check

        Returns:
            Dictionary with results summary
        """
        logger.info(
            "Starting Instagram comment check",
            max_media=max_media_to_check
        )

        results = {
            "success": True,
            "media_checked": 0,
            "comments_found": 0,
            "new_comments_added": 0,
            "errors": []
        }

        try:
            # Fetch all Instagram media
            media_list = await self.comment_ops.get_instagram_media_list()

            if not media_list:
                logger.info("No Instagram media found")
                return results

            # Limit to recent media
            media_to_check = media_list[:max_media_to_check]

            logger.info(
                f"Found {len(media_list)} total media, checking {len(media_to_check)} most recent"
            )

            # Check each media for comments
            for media in media_to_check:
                media_id = media.get("id")
                if not media_id:
                    continue

                try:
                    await self._check_media_comments(media_id, results)
                    results["media_checked"] += 1
                except Exception as e:
                    logger.error(
                        "Error checking media comments",
                        media_id=media_id,
                        error=str(e)
                    )
                    results["errors"].append({
                        "media_id": media_id,
                        "error": str(e)
                    })

            logger.info(
                "Instagram comment check completed",
                media_checked=results["media_checked"],
                comments_found=results["comments_found"],
                new_comments_added=results["new_comments_added"],
                errors=len(results["errors"])
            )

            return results

        except Exception as e:
            logger.error(
                "Failed to check Instagram comments",
                error=str(e)
            )
            results["success"] = False
            results["errors"].append({"general": str(e)})
            return results

    async def _check_media_comments(
        self,
        media_id: str,
        results: Dict[str, Any]
    ) -> None:
        """
        Check comments for a specific media post.

        Args:
            media_id: Instagram media ID
            results: Results dictionary to update
        """
        logger.info(f"Checking comments for media {media_id}")

        try:
            # Fetch all comments for this media
            comments = await self.comment_ops.get_instagram_media_comments(media_id)

            if not comments:
                logger.info(f"No comments found for media {media_id}")
                return

            logger.info(
                f"Found {len(comments)} comments on media {media_id}"
            )
            results["comments_found"] += len(comments)

            # Process each comment
            for comment in comments:
                await self._process_comment(comment, media_id, results)

                # Also process replies if they exist
                replies = comment.get("replies", {}).get("data", [])
                for reply in replies:
                    # Add parent_id to reply
                    reply["parent_id"] = comment.get("id")
                    reply["media"] = {"id": media_id}  # Add media reference
                    await self._process_comment(reply, media_id, results)

        except Exception as e:
            logger.error(
                "Error fetching comments for media",
                media_id=media_id,
                error=str(e)
            )
            raise

    async def _process_comment(
        self,
        comment: Dict[str, Any],
        media_id: str,
        results: Dict[str, Any]
    ) -> None:
        """
        Process a single comment and add to database if new.

        Args:
            comment: Comment data from Instagram API
            media_id: Instagram media ID
            results: Results dictionary to update
        """
        comment_id = comment.get("id")
        if not comment_id:
            logger.warning("Comment missing ID", comment=comment)
            return

        try:
            # Check if comment already exists in database
            existing = await self.comment_repo.get_by_comment_id(
                business_asset_id=self.business_asset_id,
                platform="instagram",
                comment_id=comment_id
            )

            if existing:
                # Comment already in database, skip
                return

            # Extract comment details
            comment_text = comment.get("text", "")
            username = comment.get("username", "")

            # Extract commenter ID
            from_data = comment.get("from", {})
            commenter_id = from_data.get("id", "") or from_data.get("self_ig_scoped_id", "")

            # Parse timestamp
            timestamp_str = comment.get("timestamp", "")
            try:
                created_time = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            except:
                created_time = datetime.utcnow()

            # Get like count
            like_count = comment.get("like_count", 0)

            # Get parent comment ID if this is a reply
            parent_id = comment.get("parent_id")

            # Prepare comment data
            from backend.models import PlatformComment

            new_comment = PlatformComment(
                platform="instagram",
                comment_id=comment_id,
                post_id=media_id,
                comment_text=comment_text,
                commenter_username=username or "unknown",
                commenter_id=commenter_id or "unknown",
                parent_comment_id=parent_id,
                created_time=created_time,
                like_count=like_count,
                permalink_url=None,  # Instagram doesn't provide this in API
                status="pending",
                business_asset_id=self.business_asset_id
            )

            # Insert into database
            await self.comment_repo.create(new_comment)

            results["new_comments_added"] += 1

            logger.info(
                "Added new Instagram comment to database",
                comment_id=comment_id,
                media_id=media_id,
                username=username
            )

        except Exception as e:
            logger.error(
                "Error processing comment",
                comment_id=comment_id,
                error=str(e)
            )
            raise


async def check_instagram_comments(
    business_asset_id: str,
    max_media: int = 20
) -> Dict[str, Any]:
    """
    CLI/Scheduler entry point for checking Instagram comments.

    Args:
        business_asset_id: The unique identifier for the business asset
        max_media: Maximum number of recent media to check

    Returns:
        Dictionary with results
    """
    checker = InstagramCommentChecker(business_asset_id)
    return await checker.check_for_new_comments(max_media_to_check=max_media)
