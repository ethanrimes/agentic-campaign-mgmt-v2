# backend/services/meta/__init__.py

"""
Meta (Facebook/Instagram) services.

This module provides services for publishing, comments, and insights
on Meta platforms (Facebook and Instagram).
"""

# Publishing services
from .publishing import FacebookPublisher, InstagramPublisher

# Comment services
from .comments import CommentOperations, InstagramCommentChecker, check_instagram_comments

# Insights services
from .insights import FacebookInsightsService, InstagramInsightsService, EngagementAPI

# Base client (for direct extension)
from .base import MetaBaseClient

__all__ = [
    # Publishing
    "FacebookPublisher",
    "InstagramPublisher",
    # Comments
    "CommentOperations",
    "InstagramCommentChecker",
    "check_instagram_comments",
    # Insights
    "FacebookInsightsService",
    "InstagramInsightsService",
    "EngagementAPI",
    # Base
    "MetaBaseClient",
]
