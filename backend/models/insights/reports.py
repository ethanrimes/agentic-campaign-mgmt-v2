# backend/models/insights/reports.py

"""
Insight report models for the insights agent.

These models are used by the insights agent to generate
analytical reports about content performance.
"""

from datetime import datetime, timezone
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID, uuid4


def utc_now() -> datetime:
    """Get current UTC time in a timezone-aware manner."""
    return datetime.now(timezone.utc)


class ToolCall(BaseModel):
    """
    Record of a tool call made by the insights agent.
    Stores both the input parameters and the result.
    """

    tool_name: str = Field(..., description="Name of the tool that was called")
    arguments: Dict[str, Any] = Field(
        ..., description="Arguments passed to the tool"
    )
    result: Any = Field(..., description="Result returned by the tool")
    timestamp: datetime = Field(
        default_factory=utc_now,
        description="When the tool was called",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "tool_name": "get_post_engagement",
                "arguments": {
                    "post_id": "123456789_987654321",
                    "platform": "facebook",
                },
                "result": {
                    "likes": 234,
                    "comments": 18,
                    "shares": 12,
                    "reach": 4521,
                },
                "timestamp": "2025-01-18T15:30:00Z",
            }
        }


class InsightReport(BaseModel):
    """
    A dated insight report from the insights agent.

    The agent analyzes engagement metrics and comments to determine:
    - What content resonates with the audience
    - What doesn't work
    - Patterns in successful posts
    - Recommendations for future content

    This report is used by:
    - The planner agent (to inform content strategy)
    - The trend seed agent (for context)
    - The ungrounded seed agent (for creative direction)
    """

    id: UUID = Field(default_factory=uuid4, description="Unique insight report ID")
    business_asset_id: str = Field(..., description="Business asset ID for multi-tenancy")
    summary: str = Field(
        ...,
        description="High-level summary of findings and recommendations",
    )
    findings: str = Field(
        ...,
        description="Detailed findings about what works/doesn't work with the audience",
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Actionable recommendations for maximizing engagement",
    )
    tool_calls: List[ToolCall] = Field(
        default_factory=list,
        description="All tool calls made by the agent to gather data",
    )
    created_at: datetime = Field(
        default_factory=utc_now,
        description="Timestamp when report was generated",
    )
    created_by: str = Field(
        ...,
        description="Foundation model used (e.g., 'gpt-4o', 'claude-3-opus')",
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "e5f6a7b8-c9d0-8e9f-2a3b-4c5d6e7f8a9b",
                "summary": "Campus life content (esp. winter aesthetics) and student-focused posts drive 3x higher engagement than generic university news. Video content underperforms static images.",
                "findings": """Analysis of 45 posts from the past 2 weeks reveals:

**High Performers:**
- Winter campus photos: avg 380 likes, 32 comments
- Student testimonials/features: avg 290 likes, 41 comments
- Behind-the-scenes campus life: avg 315 likes, 28 comments

**Low Performers:**
- Administrative announcements: avg 78 likes, 3 comments
- Video content (reels): avg 142 likes, 8 comments
- Generic "motivational" content: avg 91 likes, 5 comments

**Key Insights:**
1. Audience prefers authentic, student-centered content
2. Visual aesthetic (photography quality) matters more than video production
3. Comments show high interest in "hidden gems" and practical tips
4. Peak engagement times: 6-8 PM on weekdays

**Recommendations:**
- Focus on student stories and campus aesthetics
- Deprioritize video until we improve production quality
- Create more "insider tips" content (study spots, food, etc.)
- Schedule posts for evening hours""",
                "recommendations": [
                    "Focus on student stories and campus aesthetics - these drive 3x more engagement",
                    "Schedule posts for 6-8 PM on weekdays when engagement peaks",
                    "Create more 'insider tips' content about study spots, food, and hidden gems",
                    "Deprioritize video content until production quality improves",
                    "Feature more behind-the-scenes campus life to capitalize on authenticity preference"
                ],
                "tool_calls": [],
                "created_at": "2025-01-18T16:00:00Z",
                "created_by": "gpt-4o",
            }
        }
