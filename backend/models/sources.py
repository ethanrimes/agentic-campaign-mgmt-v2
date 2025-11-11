# backend/models/sources.py

"""
Source entity for news event seeds.
Represents a URL source with key findings and metadata.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl
from uuid import UUID, uuid4


class Source(BaseModel):
    """
    A source URL with extracted key findings.

    Used by news event seeds to track where information came from.
    Includes the agent/tool that discovered the source.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique source ID")
    url: HttpUrl = Field(..., description="Source URL")
    key_findings: str = Field(
        ...,
        description="Natural language description of relevant information from this source",
    )
    found_by: str = Field(
        ...,
        description="Agent or tool that discovered this source (e.g., 'Perplexity Sonar', 'ChatGPT Deep Research', 'Gemini')",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when source was added",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "url": "https://www.nbcphiladelphia.com/news/local/example-article",
                "key_findings": "SEPTA announced a 15% fare increase effective January 2025, citing budget shortfalls and declining ridership post-pandemic.",
                "found_by": "Perplexity Sonar",
                "created_at": "2025-01-15T10:30:00Z",
            }
        }
