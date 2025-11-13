# backend/models/rapidapi/facebook_response.py

"""
Pydantic models for Facebook RapidAPI responses.
Based on facebook-scraper3 API.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ============================================================================
# COMMON/SHARED MODELS
# ============================================================================

class ImageInfo(BaseModel):
    """Image information with dimensions."""
    uri: str = Field(..., description="Image URL")
    width: Optional[int] = Field(None, description="Image width in pixels")
    height: Optional[int] = Field(None, description="Image height in pixels")
    scale: Optional[int] = Field(None, description="Image scale factor")
    id: Optional[str] = Field(None, description="Image ID")


class FacebookAuthor(BaseModel):
    """Facebook post/comment author information."""
    id: str = Field(..., description="Author Facebook ID")
    name: str = Field(..., description="Author name")
    url: Optional[str] = Field(None, description="Profile URL")
    profile_picture_url: Optional[str] = Field(None, description="Profile picture URL")
    gender: Optional[str] = Field(None, description="Gender (MALE, FEMALE, UNKNOWN, NEUTER)")


class Reactions(BaseModel):
    """Breakdown of Facebook reactions."""
    angry: int = Field(0, description="Angry reactions")
    care: int = Field(0, description="Care reactions")
    haha: int = Field(0, description="Haha reactions")
    like: int = Field(0, description="Like reactions")
    love: int = Field(0, description="Love reactions")
    sad: int = Field(0, description="Sad reactions")
    wow: int = Field(0, description="Wow reactions")


class VideoFile(BaseModel):
    """Video file information."""
    video_sd_file: Optional[str] = Field(None, description="SD video file URL")
    video_hd_file: Optional[str] = Field(None, description="HD video file URL")


class AlbumPhoto(BaseModel):
    """Photo in an album preview."""
    type: str = Field(..., description="Media type (usually 'photo')")
    image_file_uri: str = Field(..., description="Image file URL")
    url: str = Field(..., description="Facebook URL to photo")
    id: str = Field(..., description="Photo ID")


class LocationResult(BaseModel):
    """Location search result."""
    label: str = Field(..., description="Location label/name")
    uid: str = Field(..., description="Location UID")
    city_id: int = Field(..., description="City ID")
    timezone: str = Field(..., description="Timezone")


# ============================================================================
# SEARCH MODELS
# ============================================================================

class LocationsSearchResponse(BaseModel):
    """Response for location search."""
    results: List[LocationResult] = Field(default_factory=list)


class VideoSearchResult(BaseModel):
    """Video search result."""
    video_id: str = Field(..., description="Video ID")
    video_url: str = Field(..., description="Video URL")
    title: str = Field(..., description="Video title")
    author_name: str = Field(..., description="Author name")
    views: str = Field(..., description="View count (e.g., '1K views')")
    time_ago: str = Field(..., description="Time since posted")
    description: Optional[str] = Field(None, description="Video description")
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail URL")
    is_author_verified: Optional[bool] = Field(None, description="Is author verified")


class PostSearchResult(BaseModel):
    """Post search result."""
    post_id: str = Field(..., description="Post ID")
    type: str = Field(..., description="Content type (usually 'post')")
    url: str = Field(..., description="Post URL")
    message: Optional[str] = Field(None, description="Post message/text")
    timestamp: int = Field(..., description="Unix timestamp")
    comments_count: int = Field(0, description="Number of comments")
    reactions_count: int = Field(0, description="Total reactions")
    reshare_count: int = Field(0, description="Number of shares")
    reactions: Reactions = Field(default_factory=Reactions)
    author: FacebookAuthor = Field(..., description="Post author")
    image: Optional[ImageInfo] = Field(None, description="Attached image")
    video: Optional[str] = Field(None, description="Video URL")
    album_preview: Optional[List[AlbumPhoto]] = Field(None, description="Album preview")


class PlaceSearchResult(BaseModel):
    """Place/business search result."""
    type: str = Field(..., description="Entity type (usually 'place')")
    name: str = Field(..., description="Place name")
    facebook_id: str = Field(..., description="Facebook page ID")
    url: str = Field(..., description="Facebook page URL")
    profile_url: Optional[str] = Field(None, description="Profile URL")
    is_verified: bool = Field(False, description="Is verified")
    image: ImageInfo = Field(..., description="Profile image")


class PageSearchResult(BaseModel):
    """Page search result."""
    type: str = Field(..., description="Entity type (usually 'page')")
    name: str = Field(..., description="Page name")
    facebook_id: str = Field(..., description="Facebook page ID")
    url: str = Field(..., description="Facebook page URL")
    profile_url: Optional[str] = Field(None, description="Profile URL")
    is_verified: bool = Field(False, description="Is verified")
    image: ImageInfo = Field(..., description="Profile image")


class EventSearchResult(BaseModel):
    """Event search result."""
    type: str = Field(..., description="Entity type (usually 'search_event')")
    event_id: str = Field(..., description="Event ID")
    title: str = Field(..., description="Event title")
    url: str = Field(..., description="Event URL")
    day_time_sentence: Optional[str] = Field(None, description="Human-readable time")


class PersonSearchResult(BaseModel):
    """Person/profile search result."""
    type: str = Field(..., description="Entity type (usually 'search_profile')")
    profile_id: str = Field(..., description="Profile ID")
    name: str = Field(..., description="Profile name")
    url: str = Field(..., description="Profile URL")
    is_verified: bool = Field(False, description="Is verified")
    profile_picture: ImageInfo = Field(..., description="Profile picture")


# ============================================================================
# PAGE MODELS
# ============================================================================

class PageIdResponse(BaseModel):
    """Response for page ID lookup."""
    page_id: str = Field(..., description="Facebook page ID")


class DelegatePage(BaseModel):
    """Delegated page information."""
    is_business_page_active: bool = Field(False)
    id: str = Field(..., description="Delegate page ID")


class PageDetails(BaseModel):
    """Detailed page information."""
    name: str = Field(..., description="Page name")
    type: str = Field(..., description="Entity type (usually 'page')")
    page_id: str = Field(..., description="Page ID")
    url: str = Field(..., description="Page URL")
    image: str = Field(..., description="Profile picture URL")
    intro: Optional[str] = Field(None, description="Page intro/bio")
    likes: int = Field(0, description="Number of likes")
    followers: int = Field(0, description="Number of followers")
    categories: List[str] = Field(default_factory=list)
    phone: Optional[str] = Field(None, description="Contact phone")
    email: Optional[str] = Field(None, description="Contact email")
    address: Optional[str] = Field(None, description="Physical address")
    rating: Optional[float] = Field(None, description="Average rating")
    services: Optional[List[str]] = Field(None, description="Services offered")
    price_range: Optional[str] = Field(None, description="Price range indicator")
    website: Optional[str] = Field(None, description="External website")
    delegate_page: Optional[DelegatePage] = Field(None)
    cover_image: Optional[str] = Field(None, description="Cover photo URL")
    verified: bool = Field(False, description="Is verified")
    other_accounts: List[Any] = Field(default_factory=list)
    reels_page_id: Optional[str] = Field(None, description="Reels page ID")


class PageDetailsResponse(BaseModel):
    """Response wrapper for page details."""
    results: PageDetails = Field(..., description="Page details")


class PagePost(BaseModel):
    """Facebook page post."""
    post_id: str = Field(..., description="Post ID")
    type: str = Field(..., description="Content type")
    url: str = Field(..., description="Post URL")
    message: Optional[str] = Field(None, description="Post message")
    timestamp: int = Field(..., description="Unix timestamp")
    comments_count: int = Field(0)
    reactions_count: int = Field(0)
    reshare_count: int = Field(0)
    reactions: Reactions = Field(default_factory=Reactions)
    author: FacebookAuthor = Field(..., description="Post author")
    image: Optional[ImageInfo] = Field(None)
    video: Optional[str] = Field(None)
    album_preview: Optional[List[AlbumPhoto]] = Field(None)


class PagePhoto(BaseModel):
    """Page photo."""
    type: str = Field(..., description="Media type (usually 'page_photo')")
    id: str = Field(..., description="Photo ID")
    uri: str = Field(..., description="Photo URL")


class PagePhotosResponse(BaseModel):
    """Response for page photos."""
    results: List[PagePhoto] = Field(default_factory=list)
    cursor: Optional[str] = Field(None, description="Pagination cursor")
    collection_id: Optional[str] = Field(None, description="Collection ID")


class ReviewAuthorProfilePicture(BaseModel):
    """Review author profile picture."""
    uri: str = Field(..., description="Profile picture URL")
    width: Optional[int] = Field(None)
    height: Optional[int] = Field(None)
    scale: Optional[int] = Field(None)


class ReviewAuthor(BaseModel):
    """Review author information."""
    id: str = Field(..., description="Author ID")
    name: str = Field(..., description="Author name")
    url: Optional[str] = Field(None, description="Profile URL")
    profile_picture: ReviewAuthorProfilePicture = Field(..., description="Profile picture")


class PageReview(BaseModel):
    """Page review."""
    type: str = Field(..., description="Content type (usually 'review')")
    post_id: str = Field(..., description="Review post ID")
    recommend: bool = Field(..., description="Is recommendation (5-star)")
    message: str = Field(..., description="Review text")
    author: ReviewAuthor = Field(..., description="Review author")
    reactions_count: int = Field(0)
    share: int = Field(0, description="Number of shares")
    photos: List[Any] = Field(default_factory=list)
    tags: List[Any] = Field(default_factory=list)


class PageReel(BaseModel):
    """Page reel/video."""
    type: str = Field(..., description="Media type (usually 'reel')")
    video_id: str = Field(..., description="Video ID")
    post_id: str = Field(..., description="Post ID")
    url: str = Field(..., description="Reel URL")
    description: str = Field(..., description="Reel caption")
    timestamp: int = Field(..., description="Unix timestamp")
    length_in_seconds: float = Field(..., description="Video duration")
    browser_native_hd_url: str = Field(..., description="HD video URL")
    play_count: int = Field(0, description="Play count")
    comments_count: int = Field(0)
    reactions_count: int = Field(0)
    reshare_count: int = Field(0)
    author: FacebookAuthor = Field(..., description="Reel author")
    thumbnail_uri: str = Field(..., description="Thumbnail URL")


class EventAuthor(BaseModel):
    """Event author/host."""
    id: str = Field(..., description="Host ID")
    name: str = Field(..., description="Host name")
    url: str = Field(..., description="Host URL")


class EventPlace(BaseModel):
    """Event location/venue."""
    id: str = Field(..., description="Place ID")
    name: str = Field(..., description="Venue name and address")
    location: str = Field(..., description="City/location")


class PageEvent(BaseModel):
    """Page event (future or past)."""
    id: str = Field(..., description="Event ID or recurring series ID")
    name: str = Field(..., description="Event name")
    is_cancelled: bool = Field(False)
    event_author: EventAuthor = Field(..., description="Event host")
    event_place: EventPlace = Field(..., description="Event location")
    url: str = Field(..., description="Event URL")
    gif_cover_photo: Optional[str] = Field(None)
    cover_video: Optional[str] = Field(None)


class PageVideo(BaseModel):
    """Page video."""
    video_id: str = Field(..., description="Video ID")
    url: str = Field(..., description="Video file URL")
    description: str = Field(..., description="Video caption")
    timestamp: int = Field(..., description="Unix timestamp")
    length_in_ms: int = Field(..., description="Duration in milliseconds")
    play_count: int = Field(0)
    reactions_count: int = Field(0)
    author: Dict[str, Any] = Field(..., description="Video author")
    thumbnail_uri: str = Field(..., description="Thumbnail URL")
    type: str = Field(..., description="Media type")


# ============================================================================
# POST AND COMMENT MODELS
# ============================================================================

class Comment(BaseModel):
    """Facebook comment."""
    type: str = Field(..., description="Entity type (usually 'comment')")
    comment_id: str = Field(..., description="Comment ID")
    legacy_comment_id: str = Field(..., description="Legacy comment ID")
    depth: int = Field(0, description="Nested level (0 = top-level)")
    created_time: int = Field(..., description="Unix timestamp")
    message: str = Field(..., description="Comment text")
    author: FacebookAuthor = Field(..., description="Comment author")
    replies_count: int = Field(0)
    reactions_count: str = Field("0", description="Reaction count as string")
    is_sticker: bool = Field(False)
    is_gif: bool = Field(False)
    image: Optional[Any] = Field(None)
    video: Optional[Any] = Field(None)
    sticker: Optional[Any] = Field(None)
    gif: Optional[Any] = Field(None)


class PostDetail(BaseModel):
    """Detailed post information."""
    post_id: str = Field(..., description="Post ID")
    type: str = Field(..., description="Content type")
    url: str = Field(..., description="Post URL")
    message: str = Field(..., description="Post message")
    timestamp: int = Field(..., description="Unix timestamp")
    comments_count: int = Field(0)
    reactions_count: int = Field(0)
    reshare_count: int = Field(0)
    reactions: Reactions = Field(default_factory=Reactions)
    author: FacebookAuthor = Field(..., description="Post author")
    image: Optional[ImageInfo] = Field(None)
    video: Optional[str] = Field(None)
    album_preview: Optional[List[AlbumPhoto]] = Field(None)


class PostDetailResponse(BaseModel):
    """Response wrapper for post detail."""
    results: PostDetail = Field(..., description="Post details")


class ReshareEntity(BaseModel):
    """Entity that reshared a post."""
    id: str = Field(..., description="Entity ID")
    name: str = Field(..., description="Entity name")
    url: Optional[str] = Field(None, description="Entity URL")


# ============================================================================
# EVENT MODELS
# ============================================================================

class LocationFromDetails(BaseModel):
    """Location parsed from event details."""
    name: str = Field(..., description="Location name")
    contextual_name: str = Field(..., description="Contextual location name")


class RelatedEvent(BaseModel):
    """Related event information."""
    event_id: str = Field(..., description="Event ID")
    url: str = Field(..., description="Event URL")
    title: str = Field(..., description="Event title")


class EventDetails(BaseModel):
    """Detailed event information."""
    stats: str = Field("ok", description="API status")
    event_id: str = Field(..., description="Event ID")
    title: str = Field(..., description="Event title")
    source: str = Field("fb", description="Source platform")
    details: str = Field(..., description="Event description")
    location_text: str = Field(..., description="Full location text")
    lat: Optional[float] = Field(None, description="Latitude")
    lng: Optional[float] = Field(None, description="Longitude")
    start_date: str = Field(..., description="Start date (YYYY-MM-DD)")
    start_time: str = Field(..., description="Start time (HH:MM:SS)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")
    end_time: Optional[str] = Field(None, description="End time (HH:MM:SS)")
    local_formatted_time: str = Field(..., description="Human-readable time")
    hosts: List[str] = Field(default_factory=list)
    responded_count: int = Field(0, description="Number of responses")
    cover_image_url: Optional[str] = Field(None, description="Cover image URL")
    related_events: List[RelatedEvent] = Field(default_factory=list)
    location_from_details: Optional[LocationFromDetails] = Field(None)
    tags: List[Any] = Field(default_factory=list)
    has_tickets: Optional[bool] = Field(None)


class EventDetailsResponse(BaseModel):
    """Response wrapper for event details."""
    event: EventDetails = Field(..., description="Event details")


# ============================================================================
# GROUP MODELS
# ============================================================================

class GroupIdResponse(BaseModel):
    """Response for group ID lookup."""
    group_id: str = Field(..., description="Facebook group ID")


class GroupPost(BaseModel):
    """Facebook group post."""
    post_id: str = Field(..., description="Post ID")
    type: str = Field(..., description="Content type")
    url: str = Field(..., description="Post URL")
    message: Optional[str] = Field(None, description="Post message")
    timestamp: int = Field(..., description="Unix timestamp")
    comments_count: int = Field(0)
    reactions_count: int = Field(0)
    reshare_count: int = Field(0)
    reactions: Reactions = Field(default_factory=Reactions)
    author: FacebookAuthor = Field(..., description="Post author")
    image: Optional[ImageInfo] = Field(None)
    video: Optional[str] = Field(None)
    album_preview: Optional[List[AlbumPhoto]] = Field(None)


class AboutSection(BaseModel):
    """About section item."""
    icon: ImageInfo = Field(..., description="Section icon")
    text: str = Field(..., description="Section text")
    external_url: Optional[str] = Field(None, description="External link")


class GroupDetails(BaseModel):
    """Detailed group information."""
    name: str = Field(..., description="Group name")
    group_id: str = Field(..., description="Group ID")
    url: str = Field(..., description="Group URL")
    image: Optional[str] = Field(None, description="Group picture URL")
    intro: Optional[str] = Field(None, description="Group description")
    cover_image: Optional[str] = Field(None, description="Cover photo URL")
    member_count: Optional[int] = Field(None, description="Number of members")
    privacy: Optional[str] = Field(None, description="Privacy setting (Public/Private)")
    about_public: List[AboutSection] = Field(default_factory=list)


# ============================================================================
# PROFILE MODELS
# ============================================================================

class ProfileIdResponse(BaseModel):
    """Response for profile ID lookup."""
    profile_id: str = Field(..., description="Facebook profile ID")


class ProfilePost(BaseModel):
    """Profile post."""
    post_id: str = Field(..., description="Post ID")
    type: str = Field(..., description="Content type")
    url: str = Field(..., description="Post URL")
    message: str = Field(..., description="Post message")
    message_rich: Optional[str] = Field(None, description="Rich text message")
    timestamp: int = Field(..., description="Unix timestamp")
    comments_count: int = Field(0)
    reactions_count: int = Field(0)
    reshare_count: int = Field(0)
    reactions: Reactions = Field(default_factory=Reactions)
    author: FacebookAuthor = Field(..., description="Post author")
    author_title: Optional[str] = Field(None, description="Author title")
    image: Optional[ImageInfo] = Field(None)
    video: Optional[str] = Field(None, description="Video URL or reel URL")
    album_preview: Optional[List[AlbumPhoto]] = Field(None)
    video_files: Optional[VideoFile] = Field(None, description="Direct video file links")
    video_thumbnail: Optional[str] = Field(None, description="Video thumbnail URL")
    external_url: Optional[str] = Field(None, description="External link")
    attached_event: Optional[Any] = Field(None)
    attached_post: Optional[Any] = Field(None)
    attached_post_url: Optional[str] = Field(None)
    text_format_metadata: Optional[Any] = Field(None)
    comments_id: Optional[str] = Field(None)
    shares_id: Optional[str] = Field(None)


class ProfileReel(BaseModel):
    """Profile reel/video."""
    type: str = Field(..., description="Media type (usually 'reel')")
    video_id: str = Field(..., description="Video ID")
    post_id: str = Field(..., description="Post ID")
    url: str = Field(..., description="Reel URL")
    description: Optional[str] = Field(None, description="Reel caption")
    timestamp: int = Field(..., description="Unix timestamp")
    length_in_seconds: float = Field(..., description="Video duration")
    browser_native_hd_url: str = Field(..., description="HD video URL")
    play_count: int = Field(0)
    comments_count: int = Field(0)
    reactions_count: int = Field(0)
    reshare_count: int = Field(0)
    author: FacebookAuthor = Field(..., description="Reel author")
    thumbnail_uri: str = Field(..., description="Thumbnail URL")


class ProfileDetails(BaseModel):
    """Detailed profile information."""
    name: str = Field(..., description="Profile name")
    profile_id: str = Field(..., description="Profile ID")
    url: str = Field(..., description="Profile URL")
    image: Optional[str] = Field(None, description="Profile picture URL")
    intro: Optional[str] = Field(None, description="Profile bio")
    cover_image: Optional[str] = Field(None, description="Cover photo URL")
    gender: str = Field(..., description="Gender")
    about: Dict[str, Any] = Field(default_factory=dict, description="Internal about metadata")
    about_public: List[AboutSection] = Field(default_factory=list, description="Public about sections")
    verified: bool = Field(False, description="Is verified")
    delegate_page_id: Optional[str] = Field(None, description="Delegate page ID")
    reels_profile_id: Optional[str] = Field(None, description="Reels profile ID")
