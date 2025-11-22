# backend/agents/comment_responder/runner.py

"""Runner for the comment responder agent with retry logic."""

from typing import Dict, Any, List
from backend.agents.comment_responder.comment_responder_agent import CommentResponderAgent
from backend.database.repositories.platform_comments import PlatformCommentRepository
from backend.services.meta import CommentOperations
from backend.utils import get_logger

logger = get_logger(__name__)


class CommentResponderRunner:
    """
    Runner for the comment responder agent.

    Processes pending comments and generates/posts responses.
    """

    def __init__(self, max_comments_per_run: int = 10):
        """
        Initialize the runner.

        Args:
            max_comments_per_run: Maximum number of comments to process in one run
        """
        self.max_comments_per_run = max_comments_per_run
        self.agent = CommentResponderAgent()
        self.comment_repo = PlatformCommentRepository()
        self.comment_ops = CommentOperations()

    async def run(
        self,
        platform: str = None,
        limit: int = None
    ) -> Dict[str, Any]:
        """
        Run the comment responder for pending comments.

        Args:
            platform: Optional platform filter ("facebook" or "instagram")
            limit: Optional limit override

        Returns:
            Dictionary with results summary
        """
        limit = limit or self.max_comments_per_run

        logger.info(
            "Starting comment responder run",
            platform=platform or "all",
            limit=limit
        )

        # Get pending comments
        pending_comments = await self.comment_repo.get_pending_comments(
            platform=platform,
            limit=limit
        )

        if not pending_comments:
            logger.info("No pending comments to process")
            return {
                "success": True,
                "processed": 0,
                "responded": 0,
                "failed": 0,
                "ignored": 0
            }

        logger.info(f"Found {len(pending_comments)} pending comments")

        results = {
            "processed": 0,
            "responded": 0,
            "failed": 0,
            "ignored": 0,
            "errors": []
        }

        # Process each comment
        for comment in pending_comments:
            try:
                await self._process_comment(comment, results)
                results["processed"] += 1
            except Exception as e:
                logger.error(
                    "Error processing comment",
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
            **{k: v for k, v in results.items() if k != "errors"}
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
            comment_id=str(comment.id),
            platform=comment.platform,
            commenter=comment.commenter_username
        )

        try:
            # Generate response
            response_text = await self.agent.generate_response(comment)

            # If no response (e.g., spam filtered), mark as ignored
            if not response_text:
                await self.comment_repo.mark_as_ignored(comment.id)
                results["ignored"] += 1
                logger.info(
                    "Comment ignored",
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
                    comment_record_id=comment.id,
                    response_text=response_text,
                    response_comment_id=response_comment_id
                )

                results["responded"] += 1

                logger.info(
                    "Successfully responded to comment",
                    comment_id=str(comment.id),
                    response_id=response_comment_id
                )

            except Exception as e:
                # Failed to post response
                error_msg = f"Failed to post response: {str(e)}"
                await self.comment_repo.mark_as_failed(
                    comment_record_id=comment.id,
                    error_message=error_msg,
                    increment_retry=True
                )

                results["failed"] += 1

                logger.error(
                    "Failed to post comment response",
                    comment_id=str(comment.id),
                    error=str(e)
                )

        except Exception as e:
            # Failed to generate response
            error_msg = f"Failed to generate response: {str(e)}"
            await self.comment_repo.mark_as_failed(
                comment_record_id=comment.id,
                error_message=error_msg,
                increment_retry=True
            )

            results["failed"] += 1

            logger.error(
                "Failed to generate comment response",
                comment_id=str(comment.id),
                error=str(e)
            )


async def run_comment_responder(
    platform: str = None,
    limit: int = 10
) -> Dict[str, Any]:
    """
    CLI entry point for running the comment responder.

    Args:
        platform: Optional platform filter ("facebook" or "instagram")
        limit: Maximum number of comments to process

    Returns:
        Dictionary with results
    """
    runner = CommentResponderRunner(max_comments_per_run=limit)
    return await runner.run(platform=platform, limit=limit)
