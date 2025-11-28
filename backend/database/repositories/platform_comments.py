# backend/database/repositories/platform_comments.py

"""Repository for platform comments."""

from typing import List, Literal, Optional
from uuid import UUID
from backend.models import PlatformComment
from .base import BaseRepository
from backend.utils import get_logger

logger = get_logger(__name__)


class PlatformCommentRepository(BaseRepository[PlatformComment]):
    """Repository for managing platform comments from Facebook and Instagram."""

    def __init__(self):
        super().__init__("platform_comments", PlatformComment)

    async def get_pending_comments(
        self,
        business_asset_id: str,
        platform: Optional[Literal["facebook", "instagram"]] = None,
        limit: int = 50
    ) -> List[PlatformComment]:
        """
        Get pending comments that need responses.

        Args:
            business_asset_id: Business asset ID to filter by
            platform: Optional platform filter ("facebook" or "instagram")
            limit: Maximum number of comments to return

        Returns:
            List of pending comments, ordered by creation time
        """
        try:
            from backend.database import get_supabase_admin_client
            client = await get_supabase_admin_client()

            query = (
                client.table(self.table_name)
                .select("*")
                .eq("business_asset_id", business_asset_id)
                .eq("status", "pending")
                .order("created_time", desc=False)
                .limit(limit)
            )

            if platform:
                query = query.eq("platform", platform)

            result = await query.execute()

            logger.info(
                "Retrieved pending comments",
                business_asset_id=business_asset_id,
                platform=platform or "all",
                count=len(result.data)
            )

            return [self.model_class(**item) for item in result.data]
        except Exception as e:
            logger.error(
                "Failed to get pending comments",
                business_asset_id=business_asset_id,
                platform=platform,
                error=str(e)
            )
            return []

    async def get_by_comment_id(
        self,
        business_asset_id: str,
        platform: Literal["facebook", "instagram"],
        comment_id: str
    ) -> Optional[PlatformComment]:
        """
        Get a comment by its platform-specific comment ID.

        Args:
            business_asset_id: Business asset ID to filter by
            platform: Platform ("facebook" or "instagram")
            comment_id: Platform's unique comment ID

        Returns:
            Comment if found, None otherwise
        """
        try:
            from backend.database import get_supabase_admin_client
            client = await get_supabase_admin_client()

            result = (
                await client.table(self.table_name)
                .select("*")
                .eq("business_asset_id", business_asset_id)
                .eq("platform", platform)
                .eq("comment_id", comment_id)
                .execute()
            )

            if not result.data:
                return None

            return self.model_class(**result.data[0])
        except Exception as e:
            logger.error(
                "Failed to get comment by comment_id",
                business_asset_id=business_asset_id,
                platform=platform,
                comment_id=comment_id,
                error=str(e)
            )
            return None

    async def mark_as_responded(
        self,
        business_asset_id: str,
        comment_record_id: UUID,
        response_text: str,
        response_comment_id: str
    ) -> Optional[PlatformComment]:
        """
        Mark a comment as responded.

        Args:
            business_asset_id: Business asset ID to filter by
            comment_record_id: UUID of the comment record in our database
            response_text: The text we responded with
            response_comment_id: Platform ID of our reply comment

        Returns:
            Updated comment record if successful, None otherwise
        """
        from datetime import datetime

        try:
            updates = {
                "status": "responded",
                "response_text": response_text,
                "response_comment_id": response_comment_id,
                "responded_at": datetime.utcnow().isoformat()
            }

            result = await self.update(business_asset_id, comment_record_id, updates)

            if result:
                logger.info(
                    "Marked comment as responded",
                    business_asset_id=business_asset_id,
                    comment_id=str(comment_record_id),
                    response_comment_id=response_comment_id
                )

            return result
        except Exception as e:
            logger.error(
                "Failed to mark comment as responded",
                business_asset_id=business_asset_id,
                comment_id=str(comment_record_id),
                error=str(e)
            )
            return None

    async def mark_as_failed(
        self,
        business_asset_id: str,
        comment_record_id: UUID,
        error_message: str,
        increment_retry: bool = True
    ) -> Optional[PlatformComment]:
        """
        Mark a comment response as failed.

        Args:
            business_asset_id: Business asset ID to filter by
            comment_record_id: UUID of the comment record
            error_message: Error message describing the failure
            increment_retry: Whether to increment the retry_count

        Returns:
            Updated comment record if successful, None otherwise
        """
        try:
            # Get current comment to access retry_count if needed
            current = await self.get_by_id(business_asset_id, comment_record_id)
            if not current:
                logger.error(
                    "Comment not found",
                    business_asset_id=business_asset_id,
                    comment_id=str(comment_record_id)
                )
                return None

            updates = {
                "status": "failed",
                "error_message": error_message
            }

            if increment_retry:
                updates["retry_count"] = current.retry_count + 1

            result = await self.update(business_asset_id, comment_record_id, updates)

            if result:
                logger.info(
                    "Marked comment as failed",
                    business_asset_id=business_asset_id,
                    comment_id=str(comment_record_id),
                    retry_count=result.retry_count
                )

            return result
        except Exception as e:
            logger.error(
                "Failed to mark comment as failed",
                business_asset_id=business_asset_id,
                comment_id=str(comment_record_id),
                error=str(e)
            )
            return None

    async def mark_as_ignored(self, business_asset_id: str, comment_record_id: UUID) -> Optional[PlatformComment]:
        """
        Mark a comment as ignored (won't respond).

        Args:
            business_asset_id: Business asset ID to filter by
            comment_record_id: UUID of the comment record

        Returns:
            Updated comment record if successful, None otherwise
        """
        try:
            updates = {"status": "ignored"}
            result = await self.update(business_asset_id, comment_record_id, updates)

            if result:
                logger.info(
                    "Marked comment as ignored",
                    business_asset_id=business_asset_id,
                    comment_id=str(comment_record_id)
                )

            return result
        except Exception as e:
            logger.error(
                "Failed to mark comment as ignored",
                business_asset_id=business_asset_id,
                comment_id=str(comment_record_id),
                error=str(e)
            )
            return None

    async def get_comments_by_post(
        self,
        business_asset_id: str,
        platform: Literal["facebook", "instagram"],
        post_id: str,
        status: Optional[Literal["pending", "responded", "failed", "ignored"]] = None
    ) -> List[PlatformComment]:
        """
        Get all comments for a specific post.

        Args:
            business_asset_id: Business asset ID to filter by
            platform: Platform ("facebook" or "instagram")
            post_id: Platform's post ID
            status: Optional status filter

        Returns:
            List of comments for the post
        """
        try:
            from backend.database import get_supabase_admin_client
            client = await get_supabase_admin_client()

            query = (
                client.table(self.table_name)
                .select("*")
                .eq("business_asset_id", business_asset_id)
                .eq("platform", platform)
                .eq("post_id", post_id)
                .order("created_time", desc=False)
            )

            if status:
                query = query.eq("status", status)

            result = await query.execute()
            return [self.model_class(**item) for item in result.data]
        except Exception as e:
            logger.error(
                "Failed to get comments by post",
                business_asset_id=business_asset_id,
                platform=platform,
                post_id=post_id,
                error=str(e)
            )
            return []
