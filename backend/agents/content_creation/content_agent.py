# backend/agents/content_creation/content_agent.py

"""Content creation agent for generating social media posts."""

from pathlib import Path
from typing import Dict, Any, List, Literal, Optional
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
    media_urls: List[str] = Field(default_factory=list, description="List of generated media URLs")
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
                task["content_seed_id"],
                task["content_seed_type"]
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
                    completed_post = CompletedPost(
                        task_id=task["id"],
                        content_seed_id=task["content_seed_id"],
                        content_seed_type=task["content_seed_type"],
                        platform=post_data.platform,
                        post_type=post_data.post_type,
                        text=post_data.text,
                        media_urls=post_data.media_urls if post_data.media_urls else [],
                        location=post_data.location,
                        hashtags=post_data.hashtags
                    )

                    # Save to database (note: create is synchronous, not async)
                    created_post = self.posts_repo.create(completed_post)
                    posts.append(created_post.model_dump(mode="json"))
                    logger.info("Completed post saved", post_id=str(created_post.id))
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
    ) -> Dict[str, Any]:
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
        task: Dict[str, Any],
        seed: Dict[str, Any]
    ) -> str:
        """Format task and seed information for the agent."""
        context = f"""Create social media content for the following task:

** Content Seed **
Type: {task['content_seed_type']}
"""

        # Add seed-specific information
        if task['content_seed_type'] == "news_event":
            context += f"""Name: {seed.get('name', 'Unnamed')}
Location: {seed.get('location', 'Unknown')}
Time: {seed.get('start_time')} to {seed.get('end_time', 'ongoing')}
Description: {seed.get('description', '')}

Sources:
"""
            for i, src in enumerate(seed.get('sources', []), 1):
                context += f"{i}. {src.get('url', 'No URL')}\n"
                context += f"   Key Findings: {src.get('key_findings', 'N/A')}\n"

        elif task['content_seed_type'] == "trend":
            context += f"""Name: {seed.get('name', 'Unnamed')}
Description: {seed.get('description', '')}
Hashtags: {', '.join(seed.get('hashtags', []))}
"""
            if seed.get('posts'):
                context += f"\nExample Posts:\n"
                for post in seed['posts'][:5]:
                    context += f"- {post.get('link', 'No link')}\n"

        elif task['content_seed_type'] == "ungrounded":
            context += f"""Idea: {seed.get('idea', '')}
Format: {seed.get('format', 'Unknown')}
Details: {seed.get('details', '')}
"""

        # Add allocations
        context += f"""\n
** Required Posts **
Instagram:
- Image/Carousel Posts: {task['instagram_image_posts']}
- Reel Posts: {task['instagram_reel_posts']}

Facebook:
- Feed Posts: {task['facebook_feed_posts']}
- Video Posts: {task['facebook_video_posts']}

** Media Budgets **
- Maximum Images: {task['image_budget']}
- Maximum Videos: {task['video_budget']}

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