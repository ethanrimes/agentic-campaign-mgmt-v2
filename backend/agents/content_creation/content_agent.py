# backend/agents/content_creation/content_agent.py

"""Content creation agent for generating social media posts.

Uses unified format (image_posts, video_posts, text_only_posts) where each
image/video post creates both an Instagram and Facebook post using shared
or separate media based on the share_media_across_platforms config setting.
"""

from pathlib import Path
from typing import Dict, Any, List, Literal, Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel, Field
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from backend.config.settings import settings
from backend.config.prompts import get_global_system_prompt
from backend.tools import create_media_generation_tools
from backend.database.repositories.content_creation_tasks import ContentCreationTaskRepository
from backend.database.repositories.completed_posts import CompletedPostRepository
from backend.database.repositories.news_event_seeds import NewsEventSeedRepository
from backend.database.repositories.trend_seeds import TrendSeedsRepository
from backend.database.repositories.ungrounded_seeds import UngroundedSeedRepository
from backend.models.posts import CompletedPost
from backend.utils import get_logger

logger = get_logger(__name__)

# AI disclosure footnote - appended to all posts deterministically
AI_DISCLOSURE_FOOTNOTE = "\n\n✨ AI-assisted"

# Source link format - appended to news event posts deterministically
NEWS_SOURCE_LINK_FORMAT = "\n\n🔗 Read more: {url}"


class UnifiedPostOutput(BaseModel):
    """
    A unified post output that will be used to create posts on both platforms.

    Each UnifiedPostOutput creates:
    - For image/video formats: 1 Instagram post + 1 Facebook post (2 total)
    - For text_only format: 1 Facebook post only
    """
    format_type: Literal["image", "video", "text_only"] = Field(
        ..., description="Type of content format"
    )
    text: str = Field(..., description="The full caption/text for the post")
    media_ids: List[str] = Field(
        default_factory=list,
        description="List of Media IDs (UUIDs) from the media generation tools. Extract 'Media ID' values from tool responses, NOT URLs."
    )
    location: Optional[str] = Field(None, description="Optional location tag")
    hashtags: List[str] = Field(default_factory=list, description="List of hashtags (without # symbol)")


class AgentResponse(BaseModel):
    """Complete response from content creation agent using unified format."""
    posts: List[UnifiedPostOutput] = Field(..., description="List of unified post outputs")


class ContentCreationAgent:
    """
    Agent for creating social media posts from content tasks.
    Uses Wavespeed AI to generate media and creates structured posts.

    With unified format, each image/video post creates both an Instagram
    and Facebook post, optionally sharing the same media across platforms.
    """

    def __init__(self, business_asset_id: str, share_media: Optional[bool] = None):
        """
        Initialize content creation agent.

        Args:
            business_asset_id: Business asset ID for multi-tenancy
            share_media: Override for share_media_across_platforms setting.
                         If None, uses the config setting.
        """
        self.business_asset_id = business_asset_id
        self.tasks_repo = ContentCreationTaskRepository()
        self.posts_repo = CompletedPostRepository()
        self.news_repo = NewsEventSeedRepository()
        self.trend_repo = TrendSeedsRepository()
        self.ungrounded_repo = UngroundedSeedRepository()

        # Determine media sharing mode
        self.share_media = share_media if share_media is not None else settings.share_media_across_platforms

        # Load prompts
        prompt_path = Path(__file__).parent / "prompts" / "content_creation.txt"
        self.agent_prompt = prompt_path.read_text()
        self.global_prompt = get_global_system_prompt(self.business_asset_id)

        # Initialize LLM
        self.llm = ChatOpenAI(
            model=settings.default_model_name,
            api_key=settings.get_model_api_key(),
            temperature=0.7,  # Moderate-high for creative content
        )

        # Create tools
        self.tools = create_media_generation_tools(self.business_asset_id)

        self.agent_executor = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=f"{self.global_prompt}\n\n{self.agent_prompt}",
            response_format=ToolStrategy(AgentResponse)
        )

        logger.info(
            "ContentCreationAgent initialized",
            share_media=self.share_media
        )

    async def _calculate_scheduled_time(self, platform: Literal["facebook", "instagram"]) -> datetime:
        """
        Calculate the next scheduled posting time for a platform.

        Based on the scheduling config and existing pending posts.
        """
        from backend.scheduler import SCHEDULING_CONFIG

        # Get all pending posts for this platform, ordered by scheduled_posting_time
        all_pending = await self.posts_repo.get_all_pending_posts(self.business_asset_id, platform)

        # Filter for posts with scheduled times
        scheduled_posts = [p for p in all_pending if p.scheduled_posting_time is not None]

        # Get the interval for this platform
        if platform == "facebook":
            interval_hours = SCHEDULING_CONFIG.FACEBOOK_POST_INTERVAL_HOURS
            initial_delay_hours = SCHEDULING_CONFIG.FACEBOOK_INITIAL_DELAY_HOURS
        else:  # instagram
            interval_hours = SCHEDULING_CONFIG.INSTAGRAM_POST_INTERVAL_HOURS
            initial_delay_hours = SCHEDULING_CONFIG.INSTAGRAM_INITIAL_DELAY_HOURS

        now = datetime.now(timezone.utc)

        if not scheduled_posts:
            # No scheduled posts yet, schedule first post with initial delay
            return now + timedelta(hours=initial_delay_hours)

        # Find the latest scheduled time
        latest_scheduled = max(
            scheduled_posts,
            key=lambda p: p.scheduled_posting_time
        ).scheduled_posting_time

        # Schedule this post at interval after the latest
        next_time = latest_scheduled + timedelta(hours=interval_hours)

        # If the calculated time is in the past, use initial delay from now
        if next_time < now:
            return now + timedelta(hours=initial_delay_hours)

        return next_time

    async def create_content_for_task(self, task_id: str) -> List[Dict[str, Any]]:
        """
        Create all content for a specific task using unified format.

        With unified format, each image/video post creates both an Instagram
        and Facebook post, optionally sharing the same media across platforms.

        Args:
            task_id: Content creation task ID

        Returns:
            List of created completed posts
        """
        logger.info("Starting content creation for task", task_id=task_id, share_media=self.share_media)

        try:
            # Get task
            task = await self.tasks_repo.get_by_id(self.business_asset_id, task_id)
            if not task:
                raise Exception(f"Task {task_id} not found")

            # Get content seed
            seed = await self._get_content_seed(
                str(task.content_seed_id),
                task.content_seed_type
            )

            # Check if seed exists (handle orphaned tasks)
            if not seed:
                error_msg = f"Content seed {task.content_seed_id} ({task.content_seed_type}) no longer exists"
                logger.error("Orphaned task detected", task_id=task_id, error=error_msg)
                await self.tasks_repo.update(
                    self.business_asset_id,
                    task_id,
                    {"status": "failed", "error_message": error_msg}
                )
                raise Exception(error_msg)

            # Build task context with unified format
            context = self._format_task_context(task, seed)

            # Run agent
            config = {"verbose": True}
            result = await self.agent_executor.ainvoke(
                {"messages": [("human", context)]},
                config=config
            )

            # The agent's structured response is here
            structured_output: AgentResponse = result.get("structured_response")

            if not structured_output:
                logger.warning("Agent did not return a structured response")
                raise Exception("Agent did not return structured posts")

            # Get source URL for news events (to append deterministically)
            source_url = None
            if task.content_seed_type == "news_event" and seed:
                if hasattr(seed, 'sources') and seed.sources:
                    # Use first source URL
                    first_source = seed.sources[0]
                    if hasattr(first_source, 'url'):
                        source_url = str(first_source.url)

            # Convert unified posts to platform-specific posts
            posts = []
            scheduled_times = task.scheduled_times or []
            post_index = 0

            for unified_post in structured_output.posts:
                try:
                    # Get scheduled time from task (if available) or calculate
                    scheduled_time_str = scheduled_times[post_index] if post_index < len(scheduled_times) else None

                    # Create platform-specific posts based on format type
                    if unified_post.format_type == "text_only":
                        # Text-only creates only Facebook post
                        fb_posts = await self._create_fb_only_post(
                            task, unified_post, source_url, scheduled_time_str
                        )
                        posts.extend(fb_posts)
                    else:
                        # Image/video creates both IG + FB posts
                        dual_posts = await self._create_dual_platform_posts(
                            task, unified_post, source_url, scheduled_time_str
                        )
                        posts.extend(dual_posts)

                    post_index += 1

                except Exception as e:
                    logger.error("Error creating posts from unified output", error=str(e))

            # Update task status
            await self.tasks_repo.update(self.business_asset_id, task_id, {"status": "completed"})

            logger.info(
                "Content creation complete",
                task_id=task_id,
                posts_created=len(posts),
                share_media=self.share_media
            )

            return posts

        except Exception as e:
            logger.error("Error in content creation", task_id=task_id, error=str(e))
            # Mark task as failed
            await self.tasks_repo.update(self.business_asset_id, task_id, {"status": "failed"})
            raise

    async def _create_dual_platform_posts(
        self,
        task,
        unified_post: UnifiedPostOutput,
        source_url: Optional[str],
        scheduled_time_str: Optional[str]
    ) -> List[Dict[str, Any]]:
        """
        Create both Instagram and Facebook posts from a unified post output.

        If share_media is True:
          - Both posts use the same media IDs
          - Both posts share a verification_group_id
          - Instagram post is primary (will be verified)
          - Facebook post is secondary (inherits verification result)

        If share_media is False:
          - Each post is standalone (no verification group)
          - Both posts are primary (both verified separately)
        """
        posts = []
        media_uuids = [UUID(media_id) for media_id in unified_post.media_ids] if unified_post.media_ids else []

        # Determine post types based on format
        if unified_post.format_type == "image":
            ig_post_type = "instagram_image"
            fb_post_type = "facebook_feed"
        else:  # video
            ig_post_type = "instagram_reel"
            fb_post_type = "facebook_video"

        # Prepare text with source link and AI disclosure
        post_text = unified_post.text
        if source_url:
            post_text += NEWS_SOURCE_LINK_FORMAT.format(url=source_url)
        post_text += AI_DISCLOSURE_FOOTNOTE

        # Calculate scheduled times if not provided
        if scheduled_time_str:
            try:
                base_scheduled_time = datetime.fromisoformat(scheduled_time_str.replace('Z', '+00:00'))
            except ValueError:
                base_scheduled_time = await self._calculate_scheduled_time("instagram")
        else:
            base_scheduled_time = await self._calculate_scheduled_time("instagram")

        # Generate verification group ID if sharing media
        # When sharing, IG is primary (verified), FB is secondary (inherits result)
        verification_group_id = uuid4() if self.share_media else None

        # Create Instagram post (always primary)
        ig_post = CompletedPost(
            business_asset_id=self.business_asset_id,
            task_id=task.id,
            news_event_seed_id=task.news_event_seed_id,
            trend_seed_id=task.trend_seed_id,
            ungrounded_seed_id=task.ungrounded_seed_id,
            platform="instagram",
            post_type=ig_post_type,
            text=post_text,
            media_ids=media_uuids,
            location=unified_post.location,
            hashtags=unified_post.hashtags,
            scheduled_posting_time=base_scheduled_time,
            verification_group_id=verification_group_id,
            is_verification_primary=True  # IG is always primary
        )
        created_ig = await self.posts_repo.create(ig_post)
        posts.append(created_ig.model_dump(mode="json"))
        logger.info(
            "Instagram post created",
            post_id=str(created_ig.id),
            post_type=ig_post_type,
            shared_media=self.share_media,
            verification_group_id=str(verification_group_id) if verification_group_id else None,
            is_primary=True
        )

        # Create Facebook post
        # For FB, schedule slightly after IG (or use separate calculation)
        fb_scheduled_time = base_scheduled_time + timedelta(minutes=30)

        # If not sharing media, we would need to generate new media here
        # For now, we use the same media IDs (actual media re-generation would require agent re-run)
        fb_media_uuids = media_uuids  # Same media if sharing

        # FB is secondary when sharing media (inherits verification), primary when not sharing
        fb_is_primary = not self.share_media

        fb_post = CompletedPost(
            business_asset_id=self.business_asset_id,
            task_id=task.id,
            news_event_seed_id=task.news_event_seed_id,
            trend_seed_id=task.trend_seed_id,
            ungrounded_seed_id=task.ungrounded_seed_id,
            platform="facebook",
            post_type=fb_post_type,
            text=post_text,
            media_ids=fb_media_uuids,
            location=unified_post.location,
            hashtags=unified_post.hashtags,
            scheduled_posting_time=fb_scheduled_time,
            verification_group_id=verification_group_id,
            is_verification_primary=fb_is_primary
        )
        created_fb = await self.posts_repo.create(fb_post)
        posts.append(created_fb.model_dump(mode="json"))
        logger.info(
            "Facebook post created",
            post_id=str(created_fb.id),
            post_type=fb_post_type,
            shared_media=self.share_media,
            verification_group_id=str(verification_group_id) if verification_group_id else None,
            is_primary=fb_is_primary
        )

        return posts

    async def _create_fb_only_post(
        self,
        task,
        unified_post: UnifiedPostOutput,
        source_url: Optional[str],
        scheduled_time_str: Optional[str]
    ) -> List[Dict[str, Any]]:
        """
        Create a Facebook-only text post (no Instagram equivalent).
        """
        posts = []

        # Prepare text with source link and AI disclosure
        post_text = unified_post.text
        if source_url:
            post_text += NEWS_SOURCE_LINK_FORMAT.format(url=source_url)
        post_text += AI_DISCLOSURE_FOOTNOTE

        # Calculate scheduled time
        if scheduled_time_str:
            try:
                scheduled_time = datetime.fromisoformat(scheduled_time_str.replace('Z', '+00:00'))
            except ValueError:
                scheduled_time = await self._calculate_scheduled_time("facebook")
        else:
            scheduled_time = await self._calculate_scheduled_time("facebook")

        fb_post = CompletedPost(
            business_asset_id=self.business_asset_id,
            task_id=task.id,
            news_event_seed_id=task.news_event_seed_id,
            trend_seed_id=task.trend_seed_id,
            ungrounded_seed_id=task.ungrounded_seed_id,
            platform="facebook",
            post_type="facebook_feed",
            text=post_text,
            media_ids=[],  # Text-only, no media
            location=unified_post.location,
            hashtags=unified_post.hashtags,
            scheduled_posting_time=scheduled_time
        )
        created_fb = await self.posts_repo.create(fb_post)
        posts.append(created_fb.model_dump(mode="json"))
        logger.info(
            "Facebook text-only post created",
            post_id=str(created_fb.id)
        )

        return posts

    async def _get_content_seed(
        self,
        seed_id: str,
        seed_type: str
    ):
        """Fetch content seed based on type."""
        if seed_type == "news_event":
            return await self.news_repo.get_by_id(self.business_asset_id, seed_id)
        elif seed_type == "trend":
            return await self.trend_repo.get_by_id(self.business_asset_id, seed_id)
        elif seed_type == "ungrounded":
            return await self.ungrounded_repo.get_by_id(self.business_asset_id, seed_id)
        else:
            raise ValueError(f"Unknown seed type: {seed_type}")

    def _format_task_context(
        self,
        task,  # ContentCreationTask model
        seed  # Pydantic model (NewsEventSeed, TrendSeed, or UngroundedSeed)
    ) -> str:
        """Format task and seed information for the agent using unified format."""
        context = f"""Create social media content for the following task:

** Content Seed **
Type: {task.content_seed_type}
"""

        # Add seed-specific information
        if task.content_seed_type == "news_event":
            context += f"""Name: {seed.name if hasattr(seed, 'name') else 'Unnamed'}
Location: {seed.location if hasattr(seed, 'location') else 'Unknown'}
Time: {seed.start_time} to {seed.end_time if hasattr(seed, 'end_time') and seed.end_time else 'ongoing'}
Description: {seed.description if hasattr(seed, 'description') else ''}

Sources:
"""
            if hasattr(seed, 'sources') and seed.sources:
                for i, src in enumerate(seed.sources, 1):
                    context += f"{i}. {src.url if hasattr(src, 'url') else 'No URL'}\n"
                    context += f"   Key Findings: {src.key_findings if hasattr(src, 'key_findings') else 'N/A'}\n"

        elif task.content_seed_type == "trend":
            context += f"""Name: {seed.name if hasattr(seed, 'name') else 'Unnamed'}
Description: {seed.description if hasattr(seed, 'description') else ''}
Hashtags: {', '.join(seed.hashtags) if hasattr(seed, 'hashtags') and seed.hashtags else 'None'}
"""
            if hasattr(seed, 'posts') and seed.posts:
                context += f"\nExample Posts:\n"
                for post in seed.posts[:5]:
                    context += f"- {post.link if hasattr(post, 'link') else 'No link'}\n"

        elif task.content_seed_type == "ungrounded":
            context += f"""Idea: {seed.idea if hasattr(seed, 'idea') else ''}
Format: {seed.format if hasattr(seed, 'format') else 'Unknown'}
Details: {seed.details if hasattr(seed, 'details') else ''}
"""

        # Add unified format allocations
        context += f"""\n
** Required Posts (Unified Format) **

IMPORTANT: Use unified format output (format_type: "image", "video", or "text_only")
Each image/video post you create will automatically be posted to BOTH Instagram and Facebook!

- Image Posts: {task.image_posts} (each creates IG image + FB feed)
- Video Posts: {task.video_posts} (each creates IG reel + FB video)
- Text-Only Posts: {task.text_only_posts} (FB only)

** Media Budgets **
- Maximum Images: {task.image_budget}
- Maximum Videos: {task.video_budget}

** Instructions **
Create unified post outputs for the requested content. Each output creates posts on both platforms!

For each post, specify:
1. format_type: "image", "video", or "text_only"
2. text: The caption (will be used for both platforms)
3. media_ids: List of media IDs from generation tools (for image/video)
4. hashtags: List of relevant hashtags
5. location: Optional location tag

Remember:
- Generate {task.image_posts} image posts (each creates 2 platform posts)
- Generate {task.video_posts} video posts (each creates 2 platform posts)
- Generate {task.text_only_posts} text-only posts (FB only)
"""

        return context