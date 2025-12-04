# backend/services/meta/insights/__init__.py

"""
Insights fetching services for Facebook and Instagram.

This module provides functionality for fetching and caching engagement
metrics from Meta platforms.
"""

from .facebook_insights import FacebookInsightsService
from .instagram_insights import InstagramInsightsService
from .engagement_api import EngagementAPI

__all__ = [
    "FacebookInsightsService",
    "InstagramInsightsService",
    "EngagementAPI",
]
