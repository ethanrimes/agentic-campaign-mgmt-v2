# backend/models/verifier.py

"""
Verifier response entity.
Stores the result of content verification by the verifier LLM.
"""

from datetime import datetime, timezone
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID, uuid4


class VerifierResponse(BaseModel):
    """
    A verification response from the content safety verifier LLM.

    Stores the result of verifying a completed post for:
    - Offensive content detection
    - Misinformation detection (for news events)

    Note: Source link verification was removed as links are now deterministically
    appended by the content agent.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique verifier response ID")
    business_asset_id: str = Field(..., description="Business asset ID for multi-tenancy")

    # Foreign key to the post being verified
    completed_post_id: UUID = Field(
        ..., description="ID of the completed post being verified (primary post)"
    )

    # Verification group support (for cross-platform media sharing)
    verification_group_id: Optional[UUID] = Field(
        None,
        description="Links to verification group. When set, result applies to all posts in the group."
    )

    # Overall verification result
    is_approved: bool = Field(
        ..., description="Whether the post passed all verification checks"
    )

    # Individual checklist results
    has_no_offensive_content: bool = Field(
        ..., description="Whether the content passes offensive content check"
    )
    has_no_misinformation: Optional[bool] = Field(
        None,
        description="Whether news content passes misinformation check (NULL for non-news content)"
    )

    # Detailed explanation
    reasoning: str = Field(
        ..., description="Detailed reasoning from the verifier LLM explaining the decision"
    )

    # Specific issues found
    issues_found: List[str] = Field(
        default_factory=list,
        description="Array of specific issues found during verification"
    )

    # Model used
    model: str = Field(
        default="gemini-2.5-flash",
        description="Model used for verification"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the verification was performed"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "e1f2a3b4-c5d6-7e8f-9a0b-1c2d3e4f5a6b",
                "business_asset_id": "penndailybuzz",
                "completed_post_id": "c9d0e1f2-a3b4-1c2d-6e7f-8a9b0c1d2e3f",
                "is_approved": True,
                "has_no_offensive_content": True,
                "has_no_misinformation": True,
                "reasoning": "The post accurately reports the SEPTA fare increase. No offensive content detected. Information matches the provided sources.",
                "issues_found": [],
                "model": "gemini-2.5-flash",
                "created_at": "2025-01-18T19:00:00Z"
            }
        }
    )


class VerifierChecklistInput(BaseModel):
    """
    Input structure for the verifier LLM's structured output.
    Used to parse the LLM's response.

    Note: has_source_link_if_news was removed as links are now deterministically
    appended by the content agent.
    """

    has_no_offensive_content: bool = Field(
        ...,
        description="Does the content (text, images, videos) contain any hateful, offensive, or inappropriate material? True means NO offensive content found."
    )
    has_no_misinformation: Optional[bool] = Field(
        None,
        description="For news events: does the content accurately represent the source material without misinformation? Set to null if not a news event. True means NO misinformation found. Note: misspellings do NOT count as misinformation."
    )
    is_approved: bool = Field(
        ...,
        description="Overall approval: should this post be published? True only if all applicable checks pass."
    )
    reasoning: str = Field(
        ...,
        description="Detailed explanation of the verification decision, including any concerns or issues found."
    )
    issues_found: List[str] = Field(
        default_factory=list,
        description="List of specific issues found during verification. Empty if no issues."
    )
