# backend/agents/comment_responder/comment_responder_agent.py

"""Comment responder agent for generating replies to social media comments."""

from pathlib import Path
from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from backend.config.settings import settings
from backend.config.prompts import get_global_system_prompt
from backend.models import PlatformComment
from backend.services.meta import CommentOperations
from backend.utils import get_logger

logger = get_logger(__name__)


class CommentResponderAgent:
    """
    Agent for generating contextual responses to social media comments.

    Uses LangChain to generate professional, engaging responses based on:
    - The original post content
    - The specific comment
    - Other comments on the post
    - Platform-specific context
    """

    def __init__(self):
        self.comment_ops = CommentOperations()

        # Load prompts
        prompt_path = Path(__file__).parent / "prompts" / "comment_responder.txt"
        self.agent_prompt = prompt_path.read_text()
        self.global_prompt = get_global_system_prompt()

        # Initialize LLM
        self.llm = ChatOpenAI(
            model=settings.default_model_name,
            api_key=settings.get_model_api_key(),
            temperature=0.7,  # Higher temperature for more natural, varied responses
        )

        # Output parser
        self.output_parser = StrOutputParser()

    async def generate_response(
        self,
        comment: PlatformComment
    ) -> Optional[str]:
        """
        Generate a response to a comment.

        Args:
            comment: PlatformComment instance with all comment details

        Returns:
            Generated response text, or None if we should not respond

        Raises:
            Exception: If response generation fails
        """
        logger.info(
            "Generating response for comment",
            comment_id=comment.comment_id,
            platform=comment.platform
        )

        try:
            # Gather context
            context = await self._gather_context(comment)

            # Check if we should respond (e.g., filter spam)
            if not self._should_respond(comment, context):
                logger.info(
                    "Skipping response (filtered)",
                    comment_id=comment.comment_id
                )
                return None

            # Build prompt
            prompt = self._build_prompt(comment, context)

            # Generate response using LangChain
            chain = prompt | self.llm | self.output_parser
            response = await chain.ainvoke({})

            # Clean and validate response
            response = response.strip()

            if not response or len(response) < 5:
                logger.warning(
                    "Generated response too short or empty",
                    comment_id=comment.comment_id
                )
                return None

            logger.info(
                "Generated response successfully",
                comment_id=comment.comment_id,
                response_length=len(response)
            )

            return response

        except Exception as e:
            logger.error(
                "Failed to generate response",
                comment_id=comment.comment_id,
                error=str(e)
            )
            raise

    async def _gather_context(
        self,
        comment: PlatformComment
    ) -> Dict[str, Any]:
        """
        Gather all necessary context for response generation.

        Args:
            comment: The comment we're responding to

        Returns:
            Dictionary with post context, comment details, and other comments
        """
        logger.info(
            "Gathering context for comment",
            comment_id=comment.comment_id,
            post_id=comment.post_id
        )

        # Fetch post/media context
        try:
            post_context = await self.comment_ops.get_post_context(
                platform=comment.platform,
                post_id=comment.post_id
            )
        except Exception as e:
            logger.error(
                "Failed to fetch post context",
                post_id=comment.post_id,
                error=str(e)
            )
            post_context = {}

        # Fetch all comments on this post
        try:
            all_comments = await self.comment_ops.get_all_comments(
                platform=comment.platform,
                post_id=comment.post_id
            )
        except Exception as e:
            logger.error(
                "Failed to fetch other comments",
                post_id=comment.post_id,
                error=str(e)
            )
            all_comments = []

        # Verify the comment still exists
        try:
            current_comment = await self.comment_ops.get_comment_details(
                platform=comment.platform,
                comment_id=comment.comment_id
            )
        except Exception as e:
            logger.warning(
                "Could not verify comment existence",
                comment_id=comment.comment_id,
                error=str(e)
            )
            current_comment = None

        context = {
            "post_context": post_context,
            "all_comments": all_comments,
            "current_comment": current_comment or {
                "text": comment.comment_text,
                "id": comment.comment_id,
                "username": comment.commenter_username
            }
        }

        logger.info(
            "Context gathered successfully",
            comment_id=comment.comment_id,
            has_post_context=bool(post_context),
            other_comments_count=len(all_comments)
        )

        return context

    def _should_respond(
        self,
        comment: PlatformComment,
        context: Dict[str, Any]
    ) -> bool:
        """
        Determine if we should respond to this comment.

        Filters out spam, inappropriate content, etc.

        Args:
            comment: The comment to check
            context: Gathered context

        Returns:
            True if we should respond, False otherwise
        """
        # Basic spam filter (very simple for now)
        text = comment.comment_text.lower()

        # Filter obvious spam patterns
        spam_indicators = [
            "http://",
            "https://",
            "click here",
            "buy now",
            "free money",
            "www.",
        ]

        for indicator in spam_indicators:
            if indicator in text:
                logger.info(
                    "Comment marked as potential spam",
                    comment_id=comment.comment_id,
                    indicator=indicator
                )
                return False

        # Verify comment still exists
        if not context.get("current_comment"):
            logger.info(
                "Comment no longer exists",
                comment_id=comment.comment_id
            )
            return False

        return True

    def _build_prompt(
        self,
        comment: PlatformComment,
        context: Dict[str, Any]
    ) -> ChatPromptTemplate:
        """
        Build the prompt for response generation.

        Args:
            comment: The comment we're responding to
            context: Gathered context

        Returns:
            ChatPromptTemplate ready for invocation
        """
        post_context = context.get("post_context", {})
        all_comments = context.get("all_comments", [])
        current_comment = context.get("current_comment", {})

        # Extract post details
        if comment.platform == "facebook":
            post_text = post_context.get("message", "")
            post_url = post_context.get("permalink_url", "")
        else:  # Instagram
            post_text = post_context.get("caption", "")
            post_url = post_context.get("permalink", "")

        # Build context string
        context_str = f"""
## Original Post

Platform: {comment.platform.upper()}
Caption: {post_text[:500] if post_text else "N/A"}
URL: {post_url}

## Comment to Respond To

Commenter: @{comment.commenter_username}
Comment: {comment.comment_text}
Posted: {comment.created_time}
Likes: {comment.like_count}

## Other Comments on This Post

Total Comments: {len(all_comments)}
"""

        # Add sample of other comments for context (limit to avoid token overflow)
        if all_comments:
            context_str += "\nRecent Comments:\n"
            for i, other_comment in enumerate(all_comments[:5]):
                # Get comment text (field name differs by platform)
                if comment.platform == "facebook":
                    other_text = other_comment.get("message", "")
                else:
                    other_text = other_comment.get("text", "")

                other_username = other_comment.get("username", other_comment.get("from", {}).get("name", "Unknown"))
                context_str += f"{i+1}. @{other_username}: {other_text[:100]}...\n"

        # Build the full prompt
        system_message = f"{self.global_prompt}\n\n{self.agent_prompt}"

        user_message = f"""{context_str}

## Your Task

Generate an appropriate response to @{comment.commenter_username}'s comment: "{comment.comment_text}"

Remember to:
- Be professional, friendly, and authentic
- Keep it concise (1-3 sentences)
- Encourage further engagement
- Stay on-brand and contextually relevant

Generate ONLY the response text (no explanations or meta-commentary).
"""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", user_message)
        ])

        return prompt
