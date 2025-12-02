# backend/tools/__init__.py

"""
Langchain tool wrappers for the agent framework.

These tools wrap external services and database operations to make them
accessible to Langchain agents.

Engagement tools are now direct functions (not LangChain tools) for the
context-stuffing approach in the insights agent.
"""

from .engagement_tools import (
    fetch_facebook_page_insights,
    fetch_facebook_post_insights,
    fetch_facebook_video_insights,
    fetch_instagram_media_insights,
    fetch_instagram_account_insights,
    fetch_platform_comments,
)
from .instagram_scraper_tools import create_instagram_scraper_tools
from .facebook_scraper_tools import create_facebook_scraper_tools
from .media_generation_tools import create_media_generation_tools
from .knowledge_base_tools import create_knowledge_base_tools

__all__ = [
    # Engagement tools (direct functions)
    "fetch_facebook_page_insights",
    "fetch_facebook_post_insights",
    "fetch_facebook_video_insights",
    "fetch_instagram_media_insights",
    "fetch_instagram_account_insights",
    "fetch_platform_comments",
    # Scraper tools (LangChain tools)
    "create_instagram_scraper_tools",
    "create_facebook_scraper_tools",
    "create_media_generation_tools",
    "create_knowledge_base_tools",
]
