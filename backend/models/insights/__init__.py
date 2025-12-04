# backend/models/insights/__init__.py

"""
Insights models for cached engagement metrics.

This module provides Pydantic models for:
- Facebook page-level insights
- Facebook post/video insights
- Instagram account-level insights
- Instagram media insights
- Legacy insight reports (for the insights agent)
"""

from .facebook import (
    FacebookPageInsights,
    FacebookPostInsights,
    FacebookVideoInsights,
)

from .instagram import (
    InstagramAccountInsights,
    InstagramMediaInsights,
)

from .reports import (
    InsightReport,
    ToolCall,
)

__all__ = [
    # Facebook
    "FacebookPageInsights",
    "FacebookPostInsights",
    "FacebookVideoInsights",
    # Instagram
    "InstagramAccountInsights",
    "InstagramMediaInsights",
    # Reports
    "InsightReport",
    "ToolCall",
]
