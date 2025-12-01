# backend/models/seeds.py

"""
Content seed entities: News Events, Trends, and Ungrounded seeds.
These are the foundation for all content creation.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from uuid import UUID, uuid4

from .sources import Source
from .social_media import ScraperPost, User


# =============================================================================
# NEWS EVENT SEEDS
# =============================================================================


class IngestedEvent(BaseModel):
    """
    Raw event ingested from research agents (Perplexity/Deep Research).
    These are processed by the deduplicator to create NewsEventSeeds.

    Note: The 'sources' field is populated by the repository layer from the
    normalized sources table via the ingested_event_sources junction table,
    not from a database column.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique ingested event ID")
    business_asset_id: str = Field(..., description="Business asset ID for multi-tenancy")
    name: str = Field(..., description="Concise event title")
    start_time: Optional[str] = Field(
        None, description="Event start date/time in ISO 8601 format"
    )
    end_time: Optional[str] = Field(
        None, description="Event end date/time in ISO 8601 format"
    )
    location: str = Field(
        ..., description="Where the event took place (city, country, or global)"
    )
    description: str = Field(
        ..., description="2-3 sentence summary of what happened and why it matters"
    )
    sources: List[Source] = Field(
        default_factory=list, description="Source URLs with key findings"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when event was ingested",
    )
    ingested_by: str = Field(
        ...,
        description="Agent that ingested this event (e.g., 'Perplexity Sonar', 'ChatGPT Deep Research')",
    )
    processed: bool = Field(
        default=False,
        description="Whether this event has been processed by the deduplicator",
    )
    processed_at: Optional[datetime] = Field(
        None,
        description="Timestamp when event was processed by the deduplicator",
    )
    canonical_event_id: Optional[UUID] = Field(
        None,
        description="ID of the canonical news event seed this was deduplicated into",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
                "name": "SEPTA Fare Increase Announced",
                "start_time": "2025-01-15T00:00:00Z",
                "end_time": None,
                "location": "Philadelphia, PA",
                "description": "SEPTA announced a 15% fare increase effective March 2025, the first increase in five years. The transit authority cites rising operational costs and declining ridership as primary reasons.",
                "sources": [],
                "created_at": "2025-01-15T10:30:00Z",
                "ingested_by": "Perplexity Sonar",
            }
        }


class NewsEventSeed(BaseModel):
    """
    Canonical news event seed in the knowledge database.
    Created by deduplicating and consolidating IngestedEvents.

    Note: The 'sources' field is populated by the repository layer from the
    normalized sources table via the news_event_seed_sources junction table,
    not from a database column.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique news event seed ID")
    business_asset_id: str = Field(..., description="Business asset ID for multi-tenancy")
    name: str = Field(..., description="Canonical event title")
    start_time: Optional[str] = Field(
        None, description="Event start date/time in ISO 8601 format"
    )
    end_time: Optional[str] = Field(
        None, description="Event end date/time in ISO 8601 format"
    )
    location: str = Field(..., description="Event location")
    description: str = Field(
        ...,
        description="Consolidated 2-3 sentence description (may combine multiple ingested events)",
    )
    sources: List[Source] = Field(
        default_factory=list,
        description="All sources from consolidated ingested events",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when seed was created",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "b2c3d4e5-f6a7-5b6c-9d0e-1f2a3b4c5d6e",
                "name": "SEPTA Fare Increase",
                "start_time": "2025-01-15T00:00:00Z",
                "end_time": None,
                "location": "Philadelphia, PA",
                "description": "SEPTA announced a 15% fare increase effective March 2025, the first in five years. The transit authority cites rising costs, declining ridership, and reduced state funding as key drivers.",
                "sources": [],
                "created_at": "2025-01-15T11:00:00Z",
            }
        }


# =============================================================================
# TREND SEEDS
# =============================================================================


class TrendSeed(BaseModel):
    """
    Social media trend discovered by the trend searcher agent.
    Based on scraped data from Facebook/Instagram.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique trend seed ID")
    business_asset_id: str = Field(..., description="Business asset ID for multi-tenancy")
    name: str = Field(..., description="Concise trend name/title")
    description: str = Field(
        ...,
        description="Analysis of the trend: why it's important, what makes it engaging, relevance to audience",
    )
    hashtags: List[str] = Field(
        default_factory=list, description="Relevant hashtags (optional)"
    )
    posts: List[ScraperPost] = Field(
        default_factory=list,
        description="Relevant posts from social media (optional)",
    )
    users: List[User] = Field(
        default_factory=list,
        description="Relevant users/accounts (optional)",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when trend was discovered",
    )
    created_by: str = Field(
        ...,
        description="Foundation model used (e.g., 'gpt-4o-mini', 'gemini-1.5-flash')",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "c3d4e5f6-a7b8-6c7d-0e1f-2a3b4c5d6e7f",
                "name": "Penn Campus Winter Aesthetic",
                "description": "Students are sharing photos of campus covered in snow, focusing on historic buildings and the Quad. Posts emphasize the 'Dark Academia' aesthetic popular with Gen Z. High engagement on posts with warm lighting and architectural details.",
                "hashtags": [
                    "#PennWinter",
                    "#DarkAcademia",
                    "#UPenn",
                    "#CampusBeauty",
                ],
                "posts": [],
                "users": [],
                "created_at": "2025-01-16T14:22:00Z",
                "created_by": "gpt-4o-mini",
            }
        }


# =============================================================================
# UNGROUNDED SEEDS
# =============================================================================


class UngroundedSeed(BaseModel):
    """
    Creative content idea not grounded in news or social media trends.
    Generated by the ungrounded seed agent for diverse content.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique ungrounded seed ID")
    business_asset_id: str = Field(..., description="Business asset ID for multi-tenancy")
    idea: str = Field(
        ..., description="Natural language description of the content idea"
    )
    format: str = Field(
        ...,
        description="Intended medium: image, video, text, reel, carousel, pure text, etc.",
    )
    details: str = Field(
        ..., description="Additional details, context, or creative direction"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when seed was created",
    )
    created_by: str = Field(
        ...,
        description="Foundation model used (e.g., 'gpt-4o-mini', 'claude-3-sonnet')",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "d4e5f6a7-b8c9-7d8e-1f2a-3b4c5d6e7f8a",
                "idea": "Study spot recommendations from current students",
                "format": "carousel",
                "details": "A multi-image carousel showcasing 5 underrated study spots on campus. Each image shows the location with a student testimonial overlay. Focus on diverse spaces: coffee shops, library nooks, outdoor spots, etc. Emphasizes productivity and ambiance.",
                "created_at": "2025-01-17T09:15:00Z",
                "created_by": "gpt-4o-mini",
            }
        }
