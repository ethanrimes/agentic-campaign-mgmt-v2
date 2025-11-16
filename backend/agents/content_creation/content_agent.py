# backend/agents/content_creation/content_agent.py

"""Content creation agent for generating social media posts."""

from pathlib import Path
from typing import Dict, Any, List, Literal, Optional
from uuid import UUID
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


class PostOutput(BaseModel):
    """A structured social media post."""
    platform: Literal["instagram", "facebook"] = Field(..., description="Social media platform")
    post_type: Literal["instagram_image", "instagram_reel", "facebook_feed", "facebook_video"] = Field(
        ...,
        description="Type of post (must match platform)"
    )
    text: str = Field(..., description="The full caption/text for the post")
    media_ids: List[str] = Field(
        default_factory=list,
        description="List of Media IDs (UUIDs) from the media generation tools. Extract 'Media ID' values from tool responses, NOT URLs."
    )
    location: Optional[str] = Field(None, description="Optional location tag")
    hashtags: List[str] = Field(default_factory=list, description="List of hashtags (without # symbol)")


class AgentResponse(BaseModel):
    """Complete response from content creation agent."""
    posts: List[PostOutput] = Field(..., description="List of all created posts")


class ContentCreationAgent:
    """
    Agent for creating social media posts from content tasks.
    Uses Wavespeed AI to generate media and creates structured posts.
    """

    def __init__(self):
        self.tasks_repo = ContentCreationTaskRepository()
        self.posts_repo = CompletedPostRepository()
        self.news_repo = NewsEventSeedRepository()
        self.trend_repo = TrendSeedsRepository()
        self.ungrounded_repo = UngroundedSeedRepository()

        # Load prompts
        prompt_path = Path(__file__).parent / "prompts" / "content_creation.txt"
        self.agent_prompt = prompt_path.read_text()
        self.global_prompt = get_global_system_prompt()

        # Initialize LLM
        self.llm = ChatOpenAI(
            model=settings.default_model_name,
            api_key=settings.get_model_api_key(),
            temperature=0.7,  # Moderate-high for creative content
        )

        # Create tools
        self.tools = create_media_generation_tools()

        self.agent_executor = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=f"{self.global_prompt}\n\n{self.agent_prompt}",
            response_format=ToolStrategy(AgentResponse)
        )

    async def _calculate_scheduled_time(self, platform: Literal["facebook", "instagram"]) -> datetime:
        """
        Calculate the next scheduled posting time for a platform.

        Based on the scheduling config and existing pending posts.
        """
        from backend.scheduler import SCHEDULING_CONFIG

        # Get all pending posts for this platform, ordered by scheduled_posting_time
        all_pending = await self.posts_repo.get_all_pending_posts(platform)

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
        Create all content for a specific task.
        Args:
            task_id: Content creation task ID

        Returns:
            List of created completed posts
        """
        logger.info("Starting content creation for task", task_id=task_id)

        try:
            # Get task
            task = await self.tasks_repo.get_by_id(task_id)
            if not task:
                raise Exception(f"Task {task_id} not found")

            # Get content seed
            seed = await self._get_content_seed(
                str(task.content_seed_id),
                task.content_seed_type
            )

            # Build task context
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

            # Save posts to database
            posts = []
            for post_data in structured_output.posts:
                try:
                    # Create CompletedPost model instance
                    # Convert media_ids from strings to UUIDs
                    media_uuids = [UUID(media_id) for media_id in post_data.media_ids] if post_data.media_ids else []

                    # Calculate scheduled posting time
                    scheduled_time = await self._calculate_scheduled_time(post_data.platform)

                    completed_post = CompletedPost(
                        task_id=task.id,
                        content_seed_id=task.content_seed_id,
                        content_seed_type=task.content_seed_type,
                        platform=post_data.platform,
                        post_type=post_data.post_type,
                        text=post_data.text,
                        media_ids=media_uuids,
                        location=post_data.location,
                        hashtags=post_data.hashtags,
                        scheduled_posting_time=scheduled_time
                    )

                    # Save to database
                    created_post = await self.posts_repo.create(completed_post)
                    posts.append(created_post.model_dump(mode="json"))
                    logger.info(
                        "Completed post saved",
                        post_id=str(created_post.id),
                        platform=post_data.platform,
                        scheduled_time=scheduled_time.isoformat()
                    )
                except Exception as e:
                    logger.error("Error saving post", error=str(e))

            # Update task status
            await self.tasks_repo.update(task_id, {"status": "completed"})

            logger.info(
                "Content creation complete",
                task_id=task_id,
                posts_created=len(posts)
            )

            return posts

        except Exception as e:
            logger.error("Error in content creation", task_id=task_id, error=str(e))
            # Mark task as failed
            await self.tasks_repo.update(task_id, {"status": "failed"})
            raise

    async def _get_content_seed(
        self,
        seed_id: str,
        seed_type: str
    ):
        """Fetch content seed based on type."""
        if seed_type == "news_event":
            return await self.news_repo.get_by_id(seed_id)
        elif seed_type == "trend":
            return await self.trend_repo.get_by_id(seed_id)
        elif seed_type == "ungrounded":
            return await self.ungrounded_repo.get_by_id(seed_id)
        else:
            raise ValueError(f"Unknown seed type: {seed_type}")

    def _format_task_context(
        self,
        task,  # ContentCreationTask model
        seed  # Pydantic model (NewsEventSeed, TrendSeed, or UngroundedSeed)
    ) -> str:
        """Format task and seed information for the agent."""
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

        # Add allocations
        context += f"""\n
** Required Posts **
Instagram:
- Image/Carousel Posts: {task.instagram_image_posts}
- Reel Posts: {task.instagram_reel_posts}

Facebook:
- Feed Posts: {task.facebook_feed_posts}
- Video Posts: {task.facebook_video_posts}

** Media Budgets **
- Maximum Images: {task.image_budget}
- Maximum Videos: {task.video_budget}

** Instructions **
Create ALL required posts with engaging captions, relevant hashtags, and appropriate media.
Use your media generation tools to create images and videos within budget.
Ensure content is authentic, engaging, and aligned with the target audience.

For each post, specify:
1. Platform (facebook or instagram)
2. Post type (instagram_image, instagram_reel, facebook_feed, facebook_video)
3. Text/caption
4. Media (generate if needed)
5. Hashtags
6. Optional: location tag
"""

        return context