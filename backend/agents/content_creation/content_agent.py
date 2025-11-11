# backend/agents/content_creation/content_agent.py

"""Content creation agent for generating social media posts."""

from pathlib import Path
from typing import Dict, Any, List
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from backend.config.settings import settings
from backend.config.prompts import get_global_system_prompt
from backend.tools import create_media_generation_tools
from backend.database.repositories.content_creation_tasks import ContentTasksRepository
from backend.database.repositories.completed_posts import CompletedPostRepository
from backend.database.repositories.news_event_seeds import NewsEventSeedRepository
from backend.database.repositories.trend_seeds import TrendSeedsRepository
from backend.database.repositories.ungrounded_seeds import UngroundedSeedsRepository
from backend.models.posts import CompletedPost
from backend.utils import get_logger

logger = get_logger(__name__)


class ContentCreationAgent:
    """
    Agent for creating social media posts from content tasks.

    Uses Wavespeed AI to generate media and creates structured posts.
    """

    def __init__(self):
        self.tasks_repo = ContentTasksRepository()
        self.posts_repo = CompletedPostRepository()
        self.news_repo = NewsEventSeedRepository()
        self.trend_repo = TrendSeedsRepository()
        self.ungrounded_repo = UngroundedSeedsRepository()

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

        # Create agent prompt template
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", f"{self.global_prompt}\n\n{self.agent_prompt}"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        # Create agent
        self.agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt_template
        )

        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            max_iterations=20,  # Allow multiple media generations
            return_intermediate_steps=True
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
            result = await self.agent_executor.ainvoke({"input": context})

            # Parse outputs into completed posts
            posts = await self._parse_and_save_posts(
                result["output"],
                task,
                result.get("intermediate_steps", [])
            )

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
        context += f"""

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

    async def _parse_and_save_posts(
        self,
        agent_output: str,
        task: Dict[str, Any],
        intermediate_steps: List
    ) -> List[Dict[str, Any]]:
        """Parse agent output and save completed posts."""
        # Extract media URLs from tool calls
        media_urls = self._extract_media_urls(intermediate_steps)

        # Use LLM to extract structured posts
        posts_data = await self._extract_structured_posts(
            agent_output,
            task,
            media_urls
        )

        # Save posts to database
        saved_posts = []
        for post_data in posts_data:
            try:
                # Create CompletedPost model instance
                completed_post = CompletedPost(
                    task_id=post_data["task_id"],
                    content_seed_id=post_data["content_seed_id"],
                    content_seed_type=post_data["content_seed_type"],
                    platform=post_data["platform"],
                    post_type=post_data["post_type"],
                    text=post_data["text"],
                    media_urls=post_data.get("media_urls", []),
                    location=post_data.get("location"),
                    hashtags=post_data.get("hashtags", [])
                )

                # Save to database (note: create is synchronous, not async)
                created_post = self.posts_repo.create(completed_post)
                saved_posts.append(created_post.model_dump(mode="json"))
                logger.info("Completed post saved", post_id=str(created_post.id))
            except Exception as e:
                logger.error("Error saving post", error=str(e))

        return saved_posts

    def _extract_media_urls(self, intermediate_steps: List) -> List[str]:
        """Extract generated media URLs from tool calls."""
        media_urls = []

        for action, observation in intermediate_steps:
            tool_name = action.tool

            if "generate" in tool_name.lower():
                # Extract URL from observation
                obs_str = str(observation)
                if "URL:" in obs_str:
                    # Parse URL from observation
                    import re
                    urls = re.findall(r'URL: (https?://[^\s]+)', obs_str)
                    media_urls.extend(urls)

        logger.info("Extracted media URLs", count=len(media_urls))
        return media_urls

    async def _extract_structured_posts(
        self,
        agent_output: str,
        task: Dict[str, Any],
        media_urls: List[str]
    ) -> List[Dict[str, Any]]:
        """Extract structured post data from agent output."""
        extraction_prompt = f"""Extract structured social media posts from the following content creation output.

Content Output:
{agent_output}

Task Context:
- Task ID: {task['id']}
- Content Seed ID: {task['content_seed_id']}
- Content Seed Type: {task['content_seed_type']}

Available Media URLs:
{', '.join(media_urls) if media_urls else 'None'}

Expected Posts:
- Instagram Image/Carousel: {task['instagram_image_posts']}
- Instagram Reels: {task['instagram_reel_posts']}
- Facebook Feed: {task['facebook_feed_posts']}
- Facebook Video: {task['facebook_video_posts']}

Provide a JSON response with an array of posts:
{{
  "posts": [
    {{
      "task_id": "{task['id']}",
      "content_seed_id": "{task['content_seed_id']}",
      "content_seed_type": "{task['content_seed_type']}",
      "platform": "instagram" | "facebook",
      "post_type": "instagram_image" | "instagram_reel" | "facebook_feed" | "facebook_video",
      "text": "The full caption/text",
      "media_urls": ["url1", "url2"],
      "location": "Optional location",
      "hashtags": ["tag1", "tag2"]
    }}
  ]
}}

IMPORTANT:
- Extract ALL posts mentioned in the output
- Match media URLs to appropriate posts
- Ensure post_type matches the platform
- Include all hashtags from the text
"""

        extraction_llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=settings.openai_api_key,
            temperature=0.1
        )

        messages = [
            {"role": "system", "content": "You are a data extraction assistant. Extract structured information from text."},
            {"role": "user", "content": extraction_prompt}
        ]

        response = await extraction_llm.ainvoke(messages)

        # Parse JSON
        import json
        try:
            result = json.loads(response.content)
            return result.get("posts", [])
        except json.JSONDecodeError as e:
            logger.error("Failed to parse posts extraction", error=str(e))
            return []
