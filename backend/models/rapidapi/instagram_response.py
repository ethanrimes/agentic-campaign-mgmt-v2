# backend/models/rapidapi/instagram_response.py

"""
Pydantic models for Instagram RapidAPI responses.
Based on instagram-looter2 API v1.
"""

from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime


# ============================================================================
# BASE RESPONSE MODELS
# ============================================================================

class BaseResponse(BaseModel):
    """Base response with status and attempts."""
    status: bool | str = Field(..., description="Response status")
    attempts: Optional[str] = Field(None, description="Number of retry attempts")


# ============================================================================
# COMMON/SHARED MODELS
# ============================================================================

class InstagramUser(BaseModel):
    """Basic Instagram user information."""
    model_config = {"populate_by_name": True}

    pk: str = Field(..., alias="id", description="Primary key / user ID")
    username: str = Field(..., description="Username")
    full_name: str = Field("", description="Full display name")
    is_private: bool = Field(False, description="Is account private")
    is_verified: bool = Field(False, description="Is account verified")
    profile_pic_url: str = Field("", description="Profile picture URL")
    follower_count: Optional[int] = Field(None, description="Number of followers")


class Location(BaseModel):
    """Location information."""
    pk: str | int = Field(..., description="Location ID")
    name: str = Field(..., description="Location name")
    short_name: Optional[str] = Field(None, description="Short name")
    lat: Optional[float] = Field(None, description="Latitude")
    lng: Optional[float] = Field(None, description="Longitude")
    address: Optional[str] = Field(None, description="Street address")
    city: Optional[str] = Field(None, description="City name")
    facebook_places_id: Optional[str | int] = Field(None, description="Facebook Places ID")


class ImageCandidate(BaseModel):
    """Image version with different resolution."""
    url: str = Field(..., description="Image URL")
    width: int = Field(..., description="Image width")
    height: int = Field(..., description="Image height")


class VideoVersion(BaseModel):
    """Video version with different format/resolution."""
    type: int = Field(..., description="Video type code")
    url: str = Field(..., description="Video URL")
    width: int = Field(..., description="Video width")
    height: int = Field(..., description="Video height")


# ============================================================================
# IDENTITY UTILITY MODELS
# ============================================================================

class UsernameFromIdResponse(BaseResponse):
    """Response for username lookup from user ID."""
    username: str = Field(..., description="Username")
    user_id: str = Field(..., description="User ID")


class UserIdFromUsernameResponse(BaseResponse):
    """Response for user ID lookup from username."""
    username: str = Field(..., description="Username")
    user_id: str = Field(..., description="User ID")


class MediaShortcodeResponse(BaseResponse):
    """Response for media shortcode lookup."""
    shortcode: str = Field(..., description="Media shortcode")
    media_id: str = Field(..., description="Media ID")


# ============================================================================
# USER PROFILE MODELS
# ============================================================================

class BioLink(BaseModel):
    """Link in user bio."""
    link_type: str = Field(..., description="Type of link")
    lynx_url: str = Field("", description="Lynx URL for tracking")
    title: str = Field("", description="Link title")
    url: str = Field(..., description="Actual URL")


class HdProfilePicInfo(BaseModel):
    """HD profile picture information."""
    url: str = Field(..., description="HD profile picture URL")


class EdgeFollowedBy(BaseModel):
    """Follower count edge."""
    count: int = Field(0, description="Number of followers")


class EdgeFollow(BaseModel):
    """Following count edge."""
    count: int = Field(0, description="Number of accounts following")


class UserProfile(BaseResponse):
    """Detailed user profile information."""
    full_name: str = Field(..., description="Full name")
    is_memorialized: bool = Field(False)
    is_private: bool = Field(False)
    username: str = Field(..., description="Username")
    pk: str = Field(..., description="User ID")
    profile_pic_url: str = Field(..., description="Profile picture URL")
    hd_profile_pic_url_info: Optional[HdProfilePicInfo] = Field(None)
    is_verified: bool = Field(False)
    follower_count: int = Field(0)
    following_count: int = Field(0)
    media_count: int = Field(0)
    biography: str = Field("", description="Bio text")
    bio_links: List[BioLink] = Field(default_factory=list)
    external_url: Optional[str] = Field(None)
    category: Optional[str] = Field(None, description="Professional category")
    is_business: bool = Field(False)
    account_type: Optional[int] = Field(None)


class WebProfileUser(BaseModel):
    """Web profile user data (from web-profile endpoint)."""
    id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    full_name: str = Field(..., description="Full name")
    biography: str = Field("", description="Biography text")
    biography_with_entities: Optional[Dict[str, Any]] = Field(None)
    bio_links: List[BioLink] = Field(default_factory=list)
    external_url: Optional[str] = Field(None)
    external_url_linkshimmed: Optional[str] = Field(None)
    is_private: bool = Field(False)
    is_verified: bool = Field(False)
    is_professional_account: bool = Field(False)
    category_name: Optional[str] = Field(None)
    profile_pic_url: str = Field(..., description="Profile picture URL")
    profile_pic_url_hd: Optional[str] = Field(None, description="HD profile picture URL")
    edge_followed_by: EdgeFollowedBy = Field(default_factory=EdgeFollowedBy)
    edge_follow: EdgeFollow = Field(default_factory=EdgeFollow)
    edge_owner_to_timeline_media: Optional[Dict[str, Any]] = Field(None, description="Timeline media edge")
    edge_felix_video_timeline: Optional[Dict[str, Any]] = Field(None, description="Video timeline")


class WebProfileResponse(BaseResponse):
    """Web profile response from web-profile endpoint."""
    user: WebProfileUser = Field(..., description="User data")


class PageInfo(BaseModel):
    """Pagination information."""
    has_next_page: bool = Field(False)
    end_cursor: Optional[str] = Field(None)


# ============================================================================
# MEDIA MODELS
# ============================================================================

class MediaCaption(BaseModel):
    """Media caption information."""
    pk: Optional[str] = Field(None)
    text: str = Field("", description="Caption text")
    created_at: Optional[int] = Field(None, description="Unix timestamp")
    created_at_utc: Optional[int] = Field(None, description="UTC timestamp")
    user: Optional[InstagramUser] = Field(None)


class MediaDimensions(BaseModel):
    """Media dimensions."""
    height: int = Field(..., description="Height in pixels")
    width: int = Field(..., description="Width in pixels")


class MediaTaggedUser(BaseModel):
    """User tagged in media."""
    user: InstagramUser = Field(..., description="Tagged user info")
    x: float = Field(..., description="X coordinate (relative)")
    y: float = Field(..., description="Y coordinate (relative)")


class EdgeMediaToTaggedUser(BaseModel):
    """Tagged users edge."""
    edges: List[Dict[str, MediaTaggedUser]] = Field(default_factory=list)


class EdgeLikedBy(BaseModel):
    """Liked by edge."""
    count: int = Field(0, description="Number of likes")


class EdgeMediaToComment(BaseModel):
    """Comments edge."""
    count: int = Field(0, description="Number of comments")
    page_info: Optional[PageInfo] = Field(None)


class ClipsMetadata(BaseModel):
    """Clips (Reels) specific metadata."""
    audio_type: Optional[str] = Field(None, description="Audio type (original_sounds, licensed_music)")
    music_info: Optional[Dict[str, Any]] = Field(None, description="Licensed music info")
    original_sound_info: Optional[Dict[str, Any]] = Field(None, description="Original sound info")


class MediaNode(BaseModel):
    """Individual media item node."""
    model_config = {"populate_by_name": True}

    typename: str = Field(..., alias="__typename", description="GraphQL typename")
    id: str = Field(..., description="Media ID")
    shortcode: str = Field(..., description="Media shortcode")
    display_url: str = Field(..., description="Display image URL")
    is_video: bool = Field(False)
    taken_at_timestamp: int = Field(..., description="Unix timestamp")
    dimensions: MediaDimensions = Field(..., description="Media dimensions")
    edge_media_to_caption: Optional[Dict[str, List[Dict[str, MediaCaption]]]] = Field(None)
    edge_liked_by: EdgeLikedBy = Field(default_factory=EdgeLikedBy)
    edge_media_to_comment: EdgeMediaToComment = Field(default_factory=EdgeMediaToComment)
    location: Optional[Location] = Field(None)
    owner: Optional[InstagramUser] = Field(None)
    accessibility_caption: Optional[str] = Field(None)
    # For carousel posts
    edge_sidecar_to_children: Optional[Dict[str, List]] = Field(None)


class TimelineMedia(BaseModel):
    """Timeline media with full details."""
    pk: str = Field(..., description="Primary key")
    id: str = Field(..., description="Media ID with user ID")
    code: str = Field(..., description="Shortcode")
    media_type: int = Field(..., description="1=photo, 2=video, 8=carousel")
    taken_at: int = Field(..., description="Unix timestamp")
    device_timestamp: Optional[int] = Field(None)
    original_width: int = Field(..., description="Original width")
    original_height: int = Field(..., description="Original height")
    display_uri: Optional[str] = Field(None, description="Display URL")
    like_count: int = Field(0)
    comment_count: int = Field(0)
    play_count: Optional[int] = Field(None, description="Video play count")
    video_duration: Optional[float] = Field(None, description="Video duration in seconds")
    caption: Optional[MediaCaption] = Field(None)
    user: InstagramUser = Field(..., description="Post owner")
    location: Optional[Location] = Field(None)
    image_versions2: Optional[Dict[str, List[ImageCandidate]]] = Field(None)
    video_versions: Optional[List[VideoVersion]] = Field(None)
    clips_metadata: Optional[ClipsMetadata] = Field(None)
    carousel_media: Optional[List[Dict[str, Any]]] = Field(None, description="Carousel items")
    is_paid_partnership: bool = Field(False)
    media_repost_count: Optional[int] = Field(None)


class EdgeOwnerToTimelineMedia(BaseModel):
    """Edge containing timeline media."""
    count: int = Field(0, description="Total count of media")
    page_info: PageInfo = Field(default_factory=PageInfo)
    edges: List[Dict[str, MediaNode]] = Field(default_factory=list, description="Media nodes")


class TimelineUser(BaseModel):
    """User object in timeline response."""
    edge_owner_to_timeline_media: EdgeOwnerToTimelineMedia = Field(..., description="Timeline media edge")


class UserTimelineData(BaseModel):
    """Timeline data wrapper."""
    user: TimelineUser = Field(..., description="User with timeline data")


class UserTimelineResponse(BaseResponse):
    """User timeline media response."""
    data: UserTimelineData = Field(..., description="Timeline data with edges")


class UserReelsResponse(BaseModel):
    """User reels response (array of media)."""
    root: List[Dict[str, TimelineMedia]] = Field(default_factory=list)


class UserRepostsResponse(BaseModel):
    """User reposts response."""
    more_available: bool = Field(False)
    items: List[TimelineMedia] = Field(default_factory=list)


# ============================================================================
# MEDIA DETAIL MODELS
# ============================================================================

class MediaDetailResponse(BaseResponse):
    """Detailed media information response."""
    model_config = {"populate_by_name": True}

    typename: str = Field(..., alias="__typename", description="GraphQL typename")
    id: str = Field(..., description="Media ID")
    shortcode: str = Field(..., description="Shortcode")
    thumbnail_src: str = Field(..., description="Thumbnail URL")
    display_url: str = Field(..., description="Display URL")
    display_resources: List[ImageCandidate] = Field(default_factory=list)
    is_video: bool = Field(False)
    dimensions: MediaDimensions = Field(..., description="Dimensions")
    owner: InstagramUser = Field(..., description="Post owner")
    edge_media_to_caption: Optional[Dict[str, List]] = Field(None)
    edge_media_preview_like: EdgeLikedBy = Field(default_factory=EdgeLikedBy)
    edge_media_to_comment: EdgeMediaToComment = Field(default_factory=EdgeMediaToComment)
    edge_sidecar_to_children: Optional[Dict[str, List]] = Field(None, description="Carousel children")
    taken_at_timestamp: int = Field(..., description="Unix timestamp")
    location: Optional[Location] = Field(None)


# ============================================================================
# SEARCH MODELS
# ============================================================================

class SearchUser(BaseModel):
    """User search result."""
    position: int = Field(..., description="Ranking position")
    user: InstagramUser = Field(..., description="User details")


class SearchUsersResponse(BaseResponse):
    """Search users response."""
    users: List[SearchUser] = Field(default_factory=list)


class SearchHashtag(BaseModel):
    """Hashtag search result."""
    position: int = Field(..., description="Ranking position")
    hashtag: Dict[str, Any] = Field(..., description="Hashtag details with name, media_count, id")


class SearchHashtagsResponse(BaseResponse):
    """Search hashtags response."""
    hashtags: List[SearchHashtag] = Field(default_factory=list)


class SearchPlace(BaseModel):
    """Place/location search result."""
    position: int = Field(..., description="Ranking position")
    place: Dict[str, Any] = Field(..., description="Place details with location, title, subtitle")


class SearchLocationsResponse(BaseResponse):
    """Search locations response."""
    places: List[SearchPlace] = Field(default_factory=list)


class GlobalSearchResponse(BaseResponse):
    """Global search response with all types."""
    users: List[SearchUser] = Field(default_factory=list)
    hashtags: List[SearchHashtag] = Field(default_factory=list)
    places: List[SearchPlace] = Field(default_factory=list)


# ============================================================================
# HASHTAG MODELS
# ============================================================================

class HashtagInfo(BaseModel):
    """Hashtag information."""
    id: str = Field(..., description="Hashtag ID")
    name: str = Field(..., description="Hashtag name")
    media_count: int = Field(0, description="Number of posts with this hashtag")


class HashtagMediaResponse(BaseModel):
    """Media by hashtag response."""
    hashtag_info: HashtagInfo = Field(..., description="Hashtag details")
    media_data: List[TimelineMedia] = Field(default_factory=list)


# ============================================================================
# LOCATION MODELS
# ============================================================================

class LocationInfoResponse(BaseResponse):
    """Location information response."""
    location: Location = Field(..., description="Location details")


class LocationMediaResponse(BaseModel):
    """Media by location response."""
    root: List[TimelineMedia] = Field(default_factory=list)


class CityInfo(BaseModel):
    """City information."""
    id: str = Field(..., description="City ID")
    name: str = Field(..., description="City name")
    slug: str = Field(..., description="URL slug")


class CountryInfo(BaseModel):
    """Country information."""
    id: str = Field(..., description="Country ID")
    name: str = Field(..., description="Country name")
    slug: str = Field(..., description="URL slug")


class CitiesResponse(BaseModel):
    """Cities by country response."""
    country_info: CountryInfo = Field(..., description="Country details")
    city_list: List[CityInfo] = Field(default_factory=list)


class LocationsResponse(BaseModel):
    """Locations by city response."""
    country_info: CountryInfo = Field(..., description="Country details")
    city_info: CityInfo = Field(..., description="City details")
    location_list: List[Dict[str, Any]] = Field(default_factory=list)


# ============================================================================
# MUSIC MODELS
# ============================================================================

class MusicInfo(BaseModel):
    """Music/audio information."""
    audio_asset_id: str = Field(..., description="Audio asset ID")
    duration_in_ms: int = Field(0, description="Duration in milliseconds")
    progressive_download_url: Optional[str] = Field(None, description="Download URL")
    ig_artist: Optional[InstagramUser] = Field(None, description="Artist info")
    original_audio_title: Optional[str] = Field(None)


class MusicResponse(BaseModel):
    """Music info response."""
    items: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    status: str = Field("ok")
    attempts: Optional[str] = Field(None)


# ============================================================================
# EXPLORE SECTION MODELS
# ============================================================================

class SubSection(BaseModel):
    """Explore subsection."""
    section_id: int | str = Field(..., description="Section ID")
    name: str = Field(..., description="Section name")


class ExploreSection(BaseModel):
    """Explore section with media."""
    section_id: str = Field(..., description="Section ID")
    name: str = Field(..., description="Section name")
    subsections: List[SubSection] = Field(default_factory=list)
    medias: List[TimelineMedia] = Field(default_factory=list)


class ExploreSectionsResponse(BaseModel):
    """List of explore sections."""
    root: List[ExploreSection] = Field(default_factory=list)


class SectionMediaResponse(BaseResponse):
    """Media by section response."""
    section_name: str = Field(..., description="Section name")
    max_id: Optional[str] = Field(None, description="Pagination cursor")
    more_available: bool = Field(False)
    items: List[TimelineMedia] = Field(default_factory=list)
    subsections: List[SubSection] = Field(default_factory=list)


# ============================================================================
# RELATED PROFILES MODEL
# ============================================================================

class RelatedProfileNode(BaseModel):
    """Related profile information."""
    id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    full_name: str = Field(..., description="Full name")
    is_private: bool = Field(False)
    is_verified: bool = Field(False)
    profile_pic_url: str = Field(..., description="Profile picture URL")
    followed_by_viewer: bool = Field(False)
    follows_viewer: bool = Field(False)


class RelatedProfilesResponse(BaseModel):
    """Related profiles response."""
    data: Dict[str, Any] = Field(default_factory=dict, description="Data with user edge")
