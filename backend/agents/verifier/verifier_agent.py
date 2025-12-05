# backend/agents/verifier/verifier_agent.py

"""
Content safety verifier agent using Gemini 2.5 Flash.
Verifies posts against a safety checklist before publishing.
"""

import os
import tempfile
import httpx
from pathlib import Path
from typing import Dict, Any, List, Optional
from uuid import UUID

from google import genai
from google.genai import types

from backend.config.settings import settings
from backend.database.repositories.completed_posts import CompletedPostRepository
from backend.database.repositories.verifier_responses import VerifierResponseRepository
from backend.database.repositories.news_event_seeds import NewsEventSeedRepository
from backend.database.repositories.media import MediaRepository
from backend.models import CompletedPost, VerifierResponse, VerifierChecklistInput
from backend.utils import get_logger

logger = get_logger(__name__)


class VerifierAgent:
    """
    Content safety verifier agent.

    Uses Gemini 2.5 Flash to verify posts against a safety checklist:
    - Offensive content detection
    - Misinformation detection (for news events)

    Note: Source links are now deterministically appended by the content agent,
    so we no longer need to verify their presence.
    """

    MODEL = "models/gemini-2.5-flash"

    def __init__(self, business_asset_id: str):
        self.business_asset_id = business_asset_id
        self.posts_repo = CompletedPostRepository()
        self.verifier_repo = VerifierResponseRepository()
        self.news_repo = NewsEventSeedRepository()
        self.media_repo = MediaRepository()

        # Load prompt
        prompt_path = Path(__file__).parent / "prompts" / "verifier.txt"
        self.system_prompt = prompt_path.read_text()

        # Initialize Gemini client
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not set - required for verifier agent")
        self.client = genai.Client(api_key=settings.gemini_api_key)

    async def _download_media(self, url: str, temp_dir: str) -> tuple[str, str]:
        """
        Download media from URL to temporary file.

        Args:
            url: Public URL to media
            temp_dir: Temporary directory path

        Returns:
            Tuple of (local_path, mime_type)
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()

            # Determine mime type and extension
            content_type = response.headers.get("content-type", "")
            if "video" in content_type or url.endswith(".mp4"):
                mime_type = "video/mp4"
                ext = ".mp4"
            elif "png" in content_type or url.endswith(".png"):
                mime_type = "image/png"
                ext = ".png"
            elif "jpeg" in content_type or "jpg" in content_type or url.endswith((".jpg", ".jpeg")):
                mime_type = "image/jpeg"
                ext = ".jpg"
            elif "webp" in content_type or url.endswith(".webp"):
                mime_type = "image/webp"
                ext = ".webp"
            else:
                # Default to png for images
                mime_type = "image/png"
                ext = ".png"

            # Save to temp file
            filename = f"media_{hash(url)}{ext}"
            filepath = os.path.join(temp_dir, filename)
            with open(filepath, "wb") as f:
                f.write(response.content)

            return filepath, mime_type

    async def _get_media_for_post(self, post: CompletedPost) -> List[Dict[str, Any]]:
        """
        Get media information for a post.

        Args:
            post: The completed post

        Returns:
            List of dicts with 'url' and 'type' keys
        """
        media_list = []
        for media_id in post.media_ids:
            try:
                media = await self.media_repo.get_by_id(self.business_asset_id, media_id)
                if media and "public_url" in media:
                    media_type = media.get("media_type", "image")
                    media_list.append({
                        "url": str(media["public_url"]),
                        "type": media_type
                    })
            except Exception as e:
                logger.warning("Failed to fetch media", media_id=str(media_id), error=str(e))
        return media_list

    def _build_context(
        self,
        post: CompletedPost,
        news_seed: Optional[Any] = None
    ) -> str:
        """Build context string for the verifier."""
        context = f"""## Post to Verify

**Platform:** {post.platform}
**Post Type:** {post.post_type}

**Post Text:**
{post.text}

**Content Seed Type:** {post.content_seed_type}
"""

        if news_seed:
            context += f"""
## News Event Context (for verification)

**Event Name:** {news_seed.name}
**Description:** {news_seed.description}
**Location:** {news_seed.location}

**Sources:**
"""
            if hasattr(news_seed, 'sources') and news_seed.sources:
                for i, src in enumerate(news_seed.sources, 1):
                    url = src.url if hasattr(src, 'url') else 'No URL'
                    findings = src.key_findings if hasattr(src, 'key_findings') else 'N/A'
                    context += f"{i}. URL: {url}\n   Key Findings: {findings}\n"
            else:
                context += "No sources available.\n"

        return context

    async def verify_post(self, post_id: UUID) -> VerifierResponse:
        """
        Verify a single completed post.

        Args:
            post_id: ID of the post to verify

        Returns:
            VerifierResponse with the verification result
        """
        logger.info("Verifying post", post_id=str(post_id))

        # Get the post
        post = await self.posts_repo.get_by_id(self.business_asset_id, post_id)
        if not post:
            raise ValueError(f"Post {post_id} not found")

        # Get news event seed if applicable
        news_seed = None
        if post.news_event_seed_id:
            news_seed = await self.news_repo.get_by_id(
                self.business_asset_id, post.news_event_seed_id
            )

        # Build context
        context = self._build_context(post, news_seed)

        # Get media for the post
        media_list = await self._get_media_for_post(post)

        # Build content parts for Gemini
        content_parts = []

        # Download and add media files
        temp_files = []
        try:
            if media_list:
                with tempfile.TemporaryDirectory() as temp_dir:
                    for media_info in media_list:
                        try:
                            filepath, mime_type = await self._download_media(
                                media_info["url"], temp_dir
                            )
                            temp_files.append(filepath)

                            # Read file bytes
                            with open(filepath, "rb") as f:
                                file_bytes = f.read()

                            # Add to content parts
                            content_parts.append(
                                types.Part(
                                    inline_data=types.Blob(
                                        data=file_bytes,
                                        mime_type=mime_type
                                    )
                                )
                            )
                            logger.debug("Added media to verification",
                                        url=media_info["url"], mime_type=mime_type)
                        except Exception as e:
                            logger.warning("Failed to download media for verification",
                                         url=media_info["url"], error=str(e))

                    # Add text prompt
                    content_parts.append(
                        types.Part(text=f"{self.system_prompt}\n\n{context}")
                    )

                    # Call Gemini with structured output
                    response = await self._call_gemini(content_parts)
            else:
                # No media, just text
                content_parts.append(
                    types.Part(text=f"{self.system_prompt}\n\n{context}")
                )
                response = await self._call_gemini(content_parts)

        finally:
            # Files are automatically cleaned up by TemporaryDirectory context manager
            pass

        # Create and save verifier response
        # Include verification_group_id if the post has one
        verifier_response = VerifierResponse(
            business_asset_id=self.business_asset_id,
            completed_post_id=post_id,
            verification_group_id=post.verification_group_id,
            is_approved=response.is_approved,
            has_no_offensive_content=response.has_no_offensive_content,
            has_no_misinformation=response.has_no_misinformation,
            reasoning=response.reasoning,
            issues_found=response.issues_found,
            model=self.MODEL,
        )

        # Save to database
        saved_response = await self.verifier_repo.create(verifier_response)

        # Update verification status
        new_status = "verified" if response.is_approved else "rejected"

        # If the post belongs to a verification group, update ALL posts in the group
        if post.verification_group_id:
            updated_count = await self.posts_repo.update_verification_status_by_group(
                self.business_asset_id, post.verification_group_id, new_status
            )
            logger.info(
                "Verification group status updated",
                verification_group_id=str(post.verification_group_id),
                posts_updated=updated_count,
                verification_status=new_status
            )
        else:
            # Standalone post (no group), update just this post
            await self.posts_repo.update_verification_status(
                self.business_asset_id, post_id, new_status
            )

        logger.info(
            "Post verification complete",
            post_id=str(post_id),
            is_approved=response.is_approved,
            verification_status=new_status,
            verification_group_id=str(post.verification_group_id) if post.verification_group_id else None
        )

        return saved_response

    async def _call_gemini(self, content_parts: List[types.Part]) -> VerifierChecklistInput:
        """
        Call Gemini API with the content and get structured output.

        Args:
            content_parts: List of content parts (media + text)

        Returns:
            VerifierChecklistInput with the verification result
        """
        # Build the schema using types.Schema objects (required by Gemini SDK)
        # Note: is_approved is NOT in the schema - we compute it deterministically from the checklist results
        # Note: has_source_link_if_news is removed since links are now deterministically appended by content agent
        response_schema = types.Schema(
            type=types.Type.OBJECT,
            properties={
                "has_no_offensive_content": types.Schema(
                    type=types.Type.BOOLEAN,
                    description="True = NO offensive content found (check passes). False = offensive content found (check fails)."
                ),
                "has_no_misinformation": types.Schema(
                    type=types.Type.BOOLEAN,
                    description="True = NO misinformation found (check passes). For non-news content, always return true. Only return false if actual false facts are found in news content. Misspellings, garbled text, and illegible text do NOT count as misinformation."
                ),
                "reasoning": types.Schema(
                    type=types.Type.STRING,
                    description="Brief explanation of your evaluation for each checklist item."
                ),
                "issues_found": types.Schema(
                    type=types.Type.ARRAY,
                    items=types.Schema(type=types.Type.STRING),
                    description="List of specific issues found. Empty array if no issues."
                )
            },
            required=["has_no_offensive_content", "has_no_misinformation", "reasoning", "issues_found"]
        )

        try:
            response = self.client.models.generate_content(
                model=self.MODEL,
                contents=types.Content(parts=content_parts),
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=response_schema,
                )
            )

            # Parse response
            import json
            result_data = json.loads(response.text)

            # Extract checklist results
            has_no_offensive_content = result_data["has_no_offensive_content"]
            has_no_misinformation = result_data.get("has_no_misinformation")

            # Compute is_approved deterministically from checklist results
            # Approved if ALL applicable checks pass:
            # - has_no_offensive_content must be True
            # - has_no_misinformation must be True or None (not applicable)
            # Note: has_source_link_if_news is no longer checked since links are deterministically appended
            is_approved = (
                has_no_offensive_content == True and
                (has_no_misinformation is None or has_no_misinformation == True)
            )

            logger.debug(
                "Computed approval from checklist",
                has_no_offensive_content=has_no_offensive_content,
                has_no_misinformation=has_no_misinformation,
                is_approved=is_approved
            )

            return VerifierChecklistInput(
                has_no_offensive_content=has_no_offensive_content,
                has_no_misinformation=has_no_misinformation,
                is_approved=is_approved,
                reasoning=result_data["reasoning"],
                issues_found=result_data.get("issues_found", [])
            )

        except Exception as e:
            logger.error("Gemini API call failed", error=str(e))
            # Return a failed verification on error
            return VerifierChecklistInput(
                has_no_offensive_content=False,
                has_no_misinformation=None,
                is_approved=False,
                reasoning=f"Verification failed due to API error: {str(e)}",
                issues_found=["Verification system error - manual review required"]
            )


async def verify_single_post(business_asset_id: str, post_id: str) -> Dict[str, Any]:
    """
    CLI entry point for verifying a single post.

    Args:
        business_asset_id: Business asset ID
        post_id: ID of the post to verify

    Returns:
        Verification result
    """
    agent = VerifierAgent(business_asset_id)
    result = await agent.verify_post(UUID(post_id))
    return result.model_dump(mode="json")


async def verify_all_unverified(business_asset_id: str) -> Dict[str, Any]:
    """
    CLI entry point for verifying all unverified posts.

    Only verifies PRIMARY posts (is_verification_primary=True).
    Secondary posts in verification groups will automatically inherit
    the verification status from their primary post.

    Args:
        business_asset_id: Business asset ID

    Returns:
        Summary of verification results
    """
    agent = VerifierAgent(business_asset_id)
    posts_repo = CompletedPostRepository()

    # Get only unverified PRIMARY posts (secondary posts inherit verification)
    unverified_posts = await posts_repo.get_unverified_primary_posts(business_asset_id)

    if not unverified_posts:
        return {
            "success": True,
            "posts_verified": 0,
            "posts_affected": 0,
            "approved": 0,
            "rejected": 0,
            "message": "No unverified primary posts found"
        }

    logger.info(f"Found {len(unverified_posts)} unverified primary posts to verify")

    approved = 0
    rejected = 0
    errors = 0
    total_posts_affected = 0

    for post in unverified_posts:
        try:
            result = await agent.verify_post(post.id)
            if result.is_approved:
                approved += 1
            else:
                rejected += 1

            # Count how many posts were affected (including secondary posts in group)
            if post.verification_group_id:
                group_posts = await posts_repo.get_posts_by_verification_group(
                    business_asset_id, post.verification_group_id
                )
                total_posts_affected += len(group_posts)
            else:
                total_posts_affected += 1

        except Exception as e:
            logger.error("Error verifying post", post_id=str(post.id), error=str(e))
            errors += 1

    return {
        "success": True,
        "posts_verified": len(unverified_posts),
        "posts_affected": total_posts_affected,
        "approved": approved,
        "rejected": rejected,
        "errors": errors
    }
