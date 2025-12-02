# backend/database/repositories/verifier_responses.py

"""Repository for verifier responses."""

from typing import List, Optional
from uuid import UUID
from backend.models import VerifierResponse
from backend.database import get_supabase_admin_client
from backend.utils import get_logger, DatabaseError
from .base import BaseRepository

logger = get_logger(__name__)


class VerifierResponseRepository(BaseRepository[VerifierResponse]):
    """Repository for managing verifier responses."""

    def __init__(self):
        super().__init__("verifier_responses", VerifierResponse)

    async def get_by_completed_post_id(
        self, business_asset_id: str, completed_post_id: UUID
    ) -> Optional[VerifierResponse]:
        """
        Get the most recent verification response for a completed post.

        Args:
            business_asset_id: Business asset ID to filter by
            completed_post_id: ID of the completed post

        Returns:
            Most recent VerifierResponse for the post, or None if not verified
        """
        try:
            client = await get_supabase_admin_client()
            result = (
                await client.table(self.table_name)
                .select("*")
                .eq("business_asset_id", business_asset_id)
                .eq("completed_post_id", str(completed_post_id))
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )

            if not result.data:
                return None

            return self.model_class(**result.data[0])
        except Exception as e:
            logger.error(
                "Failed to get verifier response by completed post ID",
                business_asset_id=business_asset_id,
                completed_post_id=str(completed_post_id),
                error=str(e),
            )
            return None

    async def get_all_for_post(
        self, business_asset_id: str, completed_post_id: UUID
    ) -> List[VerifierResponse]:
        """
        Get all verification responses for a completed post (audit trail).

        Args:
            business_asset_id: Business asset ID to filter by
            completed_post_id: ID of the completed post

        Returns:
            List of all VerifierResponses for the post, ordered by created_at desc
        """
        try:
            client = await get_supabase_admin_client()
            result = (
                await client.table(self.table_name)
                .select("*")
                .eq("business_asset_id", business_asset_id)
                .eq("completed_post_id", str(completed_post_id))
                .order("created_at", desc=True)
                .execute()
            )

            return [self.model_class(**item) for item in result.data]
        except Exception as e:
            logger.error(
                "Failed to get all verifier responses for post",
                business_asset_id=business_asset_id,
                completed_post_id=str(completed_post_id),
                error=str(e),
            )
            return []

    async def get_rejected_posts(
        self, business_asset_id: str, limit: int = 50
    ) -> List[VerifierResponse]:
        """
        Get recent rejected verification responses.

        Args:
            business_asset_id: Business asset ID to filter by
            limit: Maximum number of responses to return

        Returns:
            List of rejected VerifierResponses
        """
        try:
            client = await get_supabase_admin_client()
            result = (
                await client.table(self.table_name)
                .select("*")
                .eq("business_asset_id", business_asset_id)
                .eq("is_approved", False)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )

            return [self.model_class(**item) for item in result.data]
        except Exception as e:
            logger.error(
                "Failed to get rejected verifier responses",
                business_asset_id=business_asset_id,
                error=str(e),
            )
            return []

    async def get_stats(self, business_asset_id: str) -> dict:
        """
        Get verification statistics.

        Args:
            business_asset_id: Business asset ID to filter by

        Returns:
            Dictionary with verification stats
        """
        try:
            client = await get_supabase_admin_client()

            # Get total count
            total_result = (
                await client.table(self.table_name)
                .select("id", count="exact")
                .eq("business_asset_id", business_asset_id)
                .execute()
            )

            # Get approved count
            approved_result = (
                await client.table(self.table_name)
                .select("id", count="exact")
                .eq("business_asset_id", business_asset_id)
                .eq("is_approved", True)
                .execute()
            )

            # Get rejected count
            rejected_result = (
                await client.table(self.table_name)
                .select("id", count="exact")
                .eq("business_asset_id", business_asset_id)
                .eq("is_approved", False)
                .execute()
            )

            total = total_result.count or 0
            approved = approved_result.count or 0
            rejected = rejected_result.count or 0

            return {
                "total_verifications": total,
                "approved": approved,
                "rejected": rejected,
                "approval_rate": (approved / total * 100) if total > 0 else 0,
            }
        except Exception as e:
            logger.error(
                "Failed to get verification stats",
                business_asset_id=business_asset_id,
                error=str(e),
            )
            return {
                "total_verifications": 0,
                "approved": 0,
                "rejected": 0,
                "approval_rate": 0,
            }

    async def get_by_verification_group(
        self, business_asset_id: str, verification_group_id: UUID
    ) -> Optional[VerifierResponse]:
        """
        Get the most recent verification response for a verification group.

        Args:
            business_asset_id: Business asset ID to filter by
            verification_group_id: Verification group ID

        Returns:
            Most recent VerifierResponse for the group, or None if not verified
        """
        try:
            client = await get_supabase_admin_client()
            result = (
                await client.table(self.table_name)
                .select("*")
                .eq("business_asset_id", business_asset_id)
                .eq("verification_group_id", str(verification_group_id))
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )

            if not result.data:
                return None

            return self.model_class(**result.data[0])
        except Exception as e:
            logger.error(
                "Failed to get verifier response by verification group",
                business_asset_id=business_asset_id,
                verification_group_id=str(verification_group_id),
                error=str(e),
            )
            return None
