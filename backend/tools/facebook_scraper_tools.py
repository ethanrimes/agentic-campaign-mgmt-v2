# backend/tools/facebook_scraper_tools.py

"""Langchain tools for Facebook scraping via RapidAPI."""

from typing import Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from backend.services.rapidapi.facebook_scraper import FacebookScraper
from backend.utils import get_logger

logger = get_logger(__name__)


class SearchPagesInput(BaseModel):
    """Input for SearchPages tool."""
    query: str = Field(..., description="Page search query (e.g., 'Philadelphia restaurants')")


class SearchPagesTool(BaseTool):
    """Tool to search Facebook pages."""

    name: str = "search_facebook_pages"
    description: str = """
    Search for Facebook pages by keyword.
    Returns page names, IDs, and follower counts.
    Use this to find relevant pages, competitors, or community groups.
    """
    args_schema: Type[BaseModel] = SearchPagesInput

    def _run(self, query: str) -> str:
        """Execute the tool."""
        try:
            scraper = FacebookScraper()
            import asyncio
            pages = asyncio.run(scraper.search_pages(query))

            if not pages:
                return f"No pages found for query: {query}"

            output = f"Facebook Pages for '{query}':\n\n"
            for i, page in enumerate(pages[:10], 1):
                name = page.get("name", "Unknown")
                page_id = page.get("id", "N/A")
                category = page.get("category", "")
                likes = page.get("fan_count", 0)

                output += f"{i}. {name}\n"
                output += f"   ID: {page_id}\n"
                if category:
                    output += f"   Category: {category}\n"
                output += f"   Likes: {likes:,}\n\n"

            return output
        except Exception as e:
            logger.error("Error searching pages", error=str(e))
            return f"Error searching pages: {str(e)}"


class GetPagePostsInput(BaseModel):
    """Input for GetPagePosts tool."""
    page_id: str = Field(..., description="Facebook page ID")
    limit: int = Field(10, description="Number of posts to retrieve (default: 10)")


class GetPagePostsTool(BaseTool):
    """Tool to get posts from a Facebook page."""

    name: str = "get_facebook_page_posts"
    description: str = """
    Get recent posts from a Facebook page.
    Returns post content, engagement metrics, and links.
    Use this to analyze what content is being shared by specific pages.
    """
    args_schema: Type[BaseModel] = GetPagePostsInput

    def _run(self, page_id: str, limit: int = 10) -> str:
        """Execute the tool."""
        try:
            scraper = FacebookScraper()
            import asyncio
            posts = asyncio.run(scraper.get_page_posts(page_id, limit))

            if not posts:
                return f"No posts found for page {page_id}"

            output = f"Recent Facebook Posts from Page {page_id}:\n\n"
            for i, post in enumerate(posts[:limit], 1):
                post_id = post.get("id", "N/A")
                message = post.get("message", "[No text]")
                likes = post.get("reactions", {}).get("summary", {}).get("total_count", 0)
                comments = post.get("comments", {}).get("summary", {}).get("total_count", 0)
                shares = post.get("shares", {}).get("count", 0)

                output += f"{i}. Post ID: {post_id}\n"
                output += f"   Likes: {likes}, Comments: {comments}, Shares: {shares}\n"
                output += f"   Message: {message[:100]}...\n\n"

            return output
        except Exception as e:
            logger.error("Error getting page posts", error=str(e))
            return f"Error getting page posts: {str(e)}"


class SearchPostsInput(BaseModel):
    """Input for SearchPosts tool."""
    query: str = Field(..., description="Search query for posts")


class SearchPostsTool(BaseTool):
    """Tool to search public Facebook posts."""

    name: str = "search_facebook_posts"
    description: str = """
    Search for public Facebook posts by keyword.
    Returns posts matching the search query with engagement data.
    Use this to discover trending topics or conversations.
    """
    args_schema: Type[BaseModel] = SearchPostsInput

    def _run(self, query: str) -> str:
        """Execute the tool."""
        try:
            scraper = FacebookScraper()
            import asyncio
            posts = asyncio.run(scraper.search_posts(query))

            if not posts:
                return f"No posts found for query: {query}"

            output = f"Facebook Posts for '{query}':\n\n"
            for i, post in enumerate(posts[:10], 1):
                post_id = post.get("id", "N/A")
                message = post.get("message", "[No text]")
                likes = post.get("reactions", {}).get("summary", {}).get("total_count", 0)

                output += f"{i}. {message[:100]}...\n"
                output += f"   Post ID: {post_id}\n"
                output += f"   Reactions: {likes}\n\n"

            return output
        except Exception as e:
            logger.error("Error searching posts", error=str(e))
            return f"Error searching posts: {str(e)}"


class GetGroupPostsInput(BaseModel):
    """Input for GetGroupPosts tool."""
    group_id: str = Field(..., description="Facebook group ID")
    limit: int = Field(10, description="Number of posts to retrieve (default: 10)")


class GetGroupPostsTool(BaseTool):
    """Tool to get posts from a Facebook group."""

    name: str = "get_facebook_group_posts"
    description: str = """
    Get recent posts from a Facebook group.
    Returns posts with engagement metrics.
    Use this to understand community discussions and trending topics in groups.
    Note: Only works with public groups or groups you have access to.
    """
    args_schema: Type[BaseModel] = GetGroupPostsInput

    def _run(self, group_id: str, limit: int = 10) -> str:
        """Execute the tool."""
        try:
            scraper = FacebookScraper()
            import asyncio
            posts = asyncio.run(scraper.get_group_posts(group_id, limit))

            if not posts:
                return f"No posts found for group {group_id}"

            output = f"Recent Facebook Group Posts from {group_id}:\n\n"
            for i, post in enumerate(posts[:limit], 1):
                post_id = post.get("id", "N/A")
                message = post.get("message", "[No text]")
                likes = post.get("reactions", {}).get("summary", {}).get("total_count", 0)
                comments = post.get("comments", {}).get("summary", {}).get("total_count", 0)

                output += f"{i}. {message[:100]}...\n"
                output += f"   Post ID: {post_id}\n"
                output += f"   Reactions: {likes}, Comments: {comments}\n\n"

            return output
        except Exception as e:
            logger.error("Error getting group posts", error=str(e))
            return f"Error getting group posts: {str(e)}"


def create_facebook_scraper_tools():
    """Create all Facebook scraper tools for use with Langchain agents."""
    return [
        SearchPagesTool(),
        GetPagePostsTool(),
        SearchPostsTool(),
        GetGroupPostsTool(),
    ]
