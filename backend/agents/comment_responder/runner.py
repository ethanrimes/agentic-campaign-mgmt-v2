# backend/agents/comment_responder/runner.py

"""Runner for the comment responder agent with multi-page support and Instagram comment fetching."""

from typing import Dict, Any, List, Optional
from backend.agents.comment_responder.comment_responder_agent import CommentResponderAgent
from backend.database.repositories.platform_comments import PlatformCommentRepository
from backend.database.repositories.business_assets import BusinessAssetRepository
from backend.services.meta import CommentOperations, check_instagram_comments
from backend.utils import get_logger

logger = get_logger(__name__)


class CommentResponderRunner:
    """
    Runner for the comment responder agent.

    Processes pending comments and generates/posts responses.
    Supports multi-page operation for both Facebook (via webhooks) and
    Instagram (via periodic polling).
    """

    def __init__(self, business_asset_id: str, max_comments_per_run: int = 10):
        """
        Initialize the runner.

        Args:
            business_asset_id: Business asset ID for multi-tenancy
            max_comments_per_run: Maximum number of comments to process in one run
        """
        self.business_asset_id = business_asset_id
        self.max_comments_per_run = max_comments_per_run
        self.agent = CommentResponderAgent(business_asset_id)
        self.comment_repo = PlatformCommentRepository()
        self.comment_ops = CommentOperations(business_asset_id)

    async def run(
        self,
        platform: str = None,
        limit: int = None,
        fetch_instagram_first: bool = True
    ) -> Dict[str, Any]:
        """
        Run the comment responder for pending comments.

        Args:
            platform: Optional platform filter ("facebook" or "instagram")
            limit: Optional limit override
            fetch_instagram_first: Whether to fetch new Instagram comments before processing

        Returns:
            Dictionary with results summary
        """
        limit = limit or self.max_comments_per_run

        logger.info(
            "Starting comment responder run",
            business_asset_id=self.business_asset_id,
            platform=platform or "all",
            limit=limit
        )

        results = {
            "success": True,
            "business_asset_id": self.business_asset_id,
            "processed": 0,
            "responded": 0,
            "failed": 0,
            "ignored": 0,
            "instagram_fetch": None,
            "errors": []
        }

        # Fetch new Instagram comments if requested and not filtering to Facebook only
        if fetch_instagram_first and platform != "facebook":
            try:
                instagram_results = await check_instagram_comments(
                    business_asset_id=self.business_asset_id,
                    max_media=20
                )
                results["instagram_fetch"] = {
                    "success": instagram_results.get("success", False),
                    "new_comments": instagram_results.get("new_comments_added", 0),
                    "media_checked": instagram_results.get("media_checked", 0)
                }
                logger.info(
                    "Instagram comment fetch completed",
                    business_asset_id=self.business_asset_id,
                    new_comments=results["instagram_fetch"]["new_comments"]
                )
            except Exception as e:
                logger.error(
                    "Failed to fetch Instagram comments",
                    business_asset_id=self.business_asset_id,
                    error=str(e)
                )
                results["instagram_fetch"] = {
                    "success": False,
                    "error": str(e)
                }

        # Get pending comments
        pending_comments = await self.comment_repo.get_pending_comments(
            business_asset_id=self.business_asset_id,
            platform=platform,
            limit=limit
        )

        if not pending_comments:
            logger.info(
                "No pending comments to process",
                business_asset_id=self.business_asset_id
            )
            return results

        logger.info(
            f"Found {len(pending_comments)} pending comments",
            business_asset_id=self.business_asset_id
        )

        # Process each comment
        for comment in pending_comments:
            try:
                await self._process_comment(comment, results)
                results["processed"] += 1
            except Exception as e:
                logger.error(
                    "Error processing comment",
                    business_asset_id=self.business_asset_id,
                    comment_id=str(comment.id),
                    error=str(e)
                )
                results["errors"].append({
                    "comment_id": str(comment.id),
                    "error": str(e)
                })

        results["success"] = results["processed"] > 0

        logger.info(
            "Comment responder run completed",
            **{k: v for k, v in results.items() if k not in ["errors", "instagram_fetch"]}
        )

        return results

    async def _process_comment(
        self,
        comment,
        results: Dict[str, Any]
    ) -> None:
        """
        Process a single comment.

        Args:
            comment: PlatformComment instance
            results: Results dictionary to update
        """
        logger.info(
            "Processing comment",
            business_asset_id=self.business_asset_id,
            comment_id=str(comment.id),
            platform=comment.platform,
            commenter=comment.commenter_username
        )

        try:
            # Generate response
            response_text = await self.agent.generate_response(comment)

            # If no response (e.g., spam filtered), mark as ignored
            if not response_text:
                await self.comment_repo.mark_as_ignored(
                    self.business_asset_id,
                    comment.id
                )
                results["ignored"] += 1
                logger.info(
                    "Comment ignored",
                    business_asset_id=self.business_asset_id,
                    comment_id=str(comment.id)
                )
                return

            # Post the response
            try:
                response_comment_id = await self.comment_ops.reply_to_comment(
                    platform=comment.platform,
                    comment_id=comment.comment_id,
                    message=response_text
                )

                # Mark as responded
                await self.comment_repo.mark_as_responded(
                    business_asset_id=self.business_asset_id,
                    comment_record_id=comment.id,
                    response_text=response_text,
                    response_comment_id=response_comment_id
                )

                results["responded"] += 1

                logger.info(
                    "Successfully responded to comment",
                    business_asset_id=self.business_asset_id,
                    comment_id=str(comment.id),
                    response_id=response_comment_id
                )

            except Exception as e:
                # Failed to post response
                error_msg = f"Failed to post response: {str(e)}"
                await self.comment_repo.mark_as_failed(
                    business_asset_id=self.business_asset_id,
                    comment_record_id=comment.id,
                    error_message=error_msg,
                    increment_retry=True
                )

                results["failed"] += 1

                logger.error(
                    "Failed to post comment response",
                    business_asset_id=self.business_asset_id,
                    comment_id=str(comment.id),
                    error=str(e)
                )

        except Exception as e:
            # Failed to generate response
            error_msg = f"Failed to generate response: {str(e)}"
            await self.comment_repo.mark_as_failed(
                business_asset_id=self.business_asset_id,
                comment_record_id=comment.id,
                error_message=error_msg,
                increment_retry=True
            )

            results["failed"] += 1

            logger.error(
                "Failed to generate comment response",
                business_asset_id=self.business_asset_id,
                comment_id=str(comment.id),
                error=str(e)
            )


async def run_comment_responder(
    business_asset_id: str,
    platform: str = None,
    limit: int = 10,
    fetch_instagram_first: bool = True
) -> Dict[str, Any]:
    """
    CLI entry point for running the comment responder for a single business asset.

    Args:
        business_asset_id: Business asset ID for multi-tenancy
        platform: Optional platform filter ("facebook" or "instagram")
        limit: Maximum number of comments to process
        fetch_instagram_first: Whether to fetch new Instagram comments before processing

    Returns:
        Dictionary with results
    """
    runner = CommentResponderRunner(business_asset_id, max_comments_per_run=limit)
    return await runner.run(
        platform=platform,
        limit=limit,
        fetch_instagram_first=fetch_instagram_first
    )


async def run_comment_responder_all_assets(
    platform: str = None,
    limit_per_asset: int = 10,
    fetch_instagram_first: bool = True
) -> Dict[str, Any]:
    """
    Run the comment responder for all active business assets.

    This is the main entry point for scheduled/periodic comment response processing.
    It iterates through all active business assets and processes pending comments
    for each.

    Args:
        platform: Optional platform filter ("facebook" or "instagram")
        limit_per_asset: Maximum number of comments to process per asset
        fetch_instagram_first: Whether to fetch new Instagram comments before processing

    Returns:
        Dictionary with aggregated results from all assets
    """
    logger.info(
        "Starting comment responder for all assets",
        platform=platform or "all",
        limit_per_asset=limit_per_asset
    )

    # Get all active business assets
    asset_repo = BusinessAssetRepository()
    active_assets = asset_repo.get_all_active()

    if not active_assets:
        logger.warning("No active business assets found")
        return {
            "success": True,
            "assets_processed": 0,
            "total_responded": 0,
            "total_failed": 0,
            "results": []
        }

    logger.info(f"Found {len(active_assets)} active business assets")

    aggregated_results = {
        "success": True,
        "assets_processed": 0,
        "total_responded": 0,
        "total_failed": 0,
        "total_ignored": 0,
        "total_instagram_comments_fetched": 0,
        "results": []
    }

    # Process each business asset
    for asset in active_assets:
        try:
            logger.info(
                f"Processing business asset: {asset.name} ({asset.id})"
            )

            result = await run_comment_responder(
                business_asset_id=asset.id,
                platform=platform,
                limit=limit_per_asset,
                fetch_instagram_first=fetch_instagram_first
            )

            aggregated_results["assets_processed"] += 1
            aggregated_results["total_responded"] += result.get("responded", 0)
            aggregated_results["total_failed"] += result.get("failed", 0)
            aggregated_results["total_ignored"] += result.get("ignored", 0)

            # Track Instagram fetches
            ig_fetch = result.get("instagram_fetch", {})
            if ig_fetch and ig_fetch.get("success"):
                aggregated_results["total_instagram_comments_fetched"] += ig_fetch.get("new_comments", 0)

            aggregated_results["results"].append({
                "business_asset_id": asset.id,
                "business_asset_name": asset.name,
                **result
            })

        except Exception as e:
            logger.error(
                f"Failed to process business asset: {asset.id}",
                error=str(e)
            )
            aggregated_results["results"].append({
                "business_asset_id": asset.id,
                "business_asset_name": asset.name,
                "success": False,
                "error": str(e)
            })

    logger.info(
        "Comment responder completed for all assets",
        assets_processed=aggregated_results["assets_processed"],
        total_responded=aggregated_results["total_responded"],
        total_failed=aggregated_results["total_failed"]
    )

    return aggregated_results
