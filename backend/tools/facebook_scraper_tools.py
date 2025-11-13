# backend/tools/facebook_scraper_tools.py

"""Langchain tools for Facebook scraping via RapidAPI."""

from typing import Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from backend.services.rapidapi.facebook_scraper import FacebookScraper
from backend.utils import get_logger

logger = get_logger(__name__)


# ============================================================================
# SEARCH TOOLS
# ============================================================================

class SearchPagesInput(BaseModel):
    """Input for SearchPages tool."""
    query: str = Field(
        ...,
        description="Page search query string (e.g., 'beer', 'coffee', 'technology'). Use specific keywords or brand names."
    )
    location_uid: str = Field(
        None,
        description="Optional location UID to filter results by geographic area. Get this from search_locations tool (e.g., '101881036520836' for Philadelphia)"
    )


class SearchPagesTool(BaseTool):
    """Tool to search Facebook pages."""

    name: str = "search_facebook_pages"
    description: str = """
    Search for Facebook pages by keyword query.

    Returns: List of pages with name, facebook_id, url, verification status, and profile image.

    Arguments:
    - query (required): Search keyword string (e.g., 'beer', 'restaurants', 'news')
    - location_uid (optional): Location UID from search_locations to filter by geography

    Use this to find:
    - Brand pages and competitors
    - Local businesses
    - Community organizations
    - Media outlets

    Note: Returns facebook_id which can be used with get_facebook_page_posts and get_facebook_page_events.
    """
    args_schema: Type[BaseModel] = SearchPagesInput

    def _run(self, query: str, location_uid: str = None) -> str:
        """Sync version - not used by async agents."""
        raise NotImplementedError("Use async version (_arun) instead")

    async def _arun(self, query: str, location_uid: str = None) -> str:
        """Execute the tool asynchronously."""
        try:
            scraper = FacebookScraper()
            pages = await scraper.search_pages(query, location_uid=location_uid)

            if not pages:
                return f"No pages found for query: {query}"

            output = f"Facebook Pages for '{query}':\n\n"
            for i, page in enumerate(pages[:15], 1):
                name = page.name
                page_id = page.facebook_id
                verified = "✓ Verified" if page.is_verified else ""
                url = page.url

                output += f"{i}. {name} {verified}\n"
                output += f"   ID: {page_id}\n"
                output += f"   URL: {url}\n\n"

            return output
        except Exception as e:
            logger.error("Error searching pages", error=str(e))
            return f"Error searching pages: {str(e)}"


class SearchPostsInput(BaseModel):
    """Input for SearchPosts tool."""
    query: str = Field(
        ...,
        description="Post search query string (e.g., 'university', 'election', 'climate change')"
    )
    recent_posts: bool = Field(
        False,
        description="Set to true to filter to recent posts only (last few days)"
    )
    location_uid: str = Field(
        None,
        description="Optional location UID from search_locations to filter by geographic area"
    )


class SearchPostsTool(BaseTool):
    """Tool to search public Facebook posts."""

    name: str = "search_facebook_posts"
    description: str = """
    Search for public Facebook posts by keyword query.

    Returns: List of posts with post_id, message, url, timestamp, engagement metrics (reactions_count, comments_count, reshare_count), author info, and media (image/video).

    Arguments:
    - query (required): Search keyword string (e.g., 'university', 'protest', 'celebration')
    - recent_posts (optional): Set true to filter to recent posts only
    - location_uid (optional): Location UID to filter by geographic area

    Use this to:
    - Monitor public sentiment on topics
    - Find trending discussions
    - Discover user-generated content
    - Track mentions of keywords

    Note: Only searches public posts. Returns post_id which can be used with get_post_detail for full details.
    """
    args_schema: Type[BaseModel] = SearchPostsInput

    def _run(self, query: str, recent_posts: bool = False, location_uid: str = None) -> str:
        """Sync version - not used by async agents."""
        raise NotImplementedError("Use async version (_arun) instead")

    async def _arun(self, query: str, recent_posts: bool = False, location_uid: str = None) -> str:
        """Execute the tool asynchronously."""
        try:
            scraper = FacebookScraper()
            posts = await scraper.search_posts(
                query,
                recent_posts=recent_posts,
                location_uid=location_uid
            )

            if not posts:
                return f"No posts found for query: {query}"

            output = f"Facebook Posts for '{query}':\n\n"
            for i, post in enumerate(posts[:10], 1):
                message = post.message or "[No text]"
                reactions = post.reactions_count
                comments = post.comments_count
                shares = post.reshare_count
                author = post.author.name

                output += f"{i}. {message[:150]}...\n"
                output += f"   Author: {author}\n"
                output += f"   Engagement: {reactions} reactions, {comments} comments, {shares} shares\n"
                output += f"   URL: {post.url}\n\n"

            return output
        except Exception as e:
            logger.error("Error searching posts", error=str(e))
            return f"Error searching posts: {str(e)}"


class SearchEventsInput(BaseModel):
    """Input for SearchEvents tool."""
    query: str = Field(
        ...,
        description="Event search query string (e.g., 'beer', 'concert', 'festival', 'conference')"
    )
    location_uid: str = Field(
        None,
        description="Optional location UID from search_locations to filter by geographic area"
    )


class SearchEventsTool(BaseTool):
    """Tool to search Facebook events."""

    name: str = "search_facebook_events"
    description: str = """
    Search for public Facebook events by keyword query.

    Returns: List of events with event_id, title, url, and day_time_sentence.

    Arguments:
    - query (required): Event search query string (e.g., 'beer', 'concert', 'meetup')
    - location_uid (optional): Location UID to filter by geographic area

    Use this to:
    - Discover upcoming events
    - Find festivals and gatherings
    - Locate community meetups
    - Research event trends

    Note: Returns event_id which can be used with get_facebook_event_details for full event information.
    """
    args_schema: Type[BaseModel] = SearchEventsInput

    def _run(self, query: str, location_uid: str = None) -> str:
        """Sync version - not used by async agents."""
        raise NotImplementedError("Use async version (_arun) instead")

    async def _arun(self, query: str, location_uid: str = None) -> str:
        """Execute the tool asynchronously."""
        try:
            scraper = FacebookScraper()
            events = await scraper.search_events(query, location_uid=location_uid)

            if not events:
                return f"No events found for query: {query}"

            output = f"Facebook Events for '{query}':\n\n"
            for i, event in enumerate(events[:15], 1):
                title = event.title
                event_id = event.event_id
                url = event.url

                output += f"{i}. {title}\n"
                output += f"   Event ID: {event_id}\n"
                output += f"   URL: {url}\n\n"

            return output
        except Exception as e:
            logger.error("Error searching events", error=str(e))
            return f"Error searching events: {str(e)}"


class SearchPlacesInput(BaseModel):
    """Input for SearchPlaces tool."""
    query: str = Field(
        ...,
        description="Place/business search query string (e.g., 'pizza', 'bookstore', 'gym')"
    )
    location_uid: str = Field(
        None,
        description="Optional location UID from search_locations to filter by geographic area"
    )


class SearchPlacesTool(BaseTool):
    """Tool to search Facebook places/businesses."""

    name: str = "search_facebook_places"
    description: str = """
    Search for Facebook business pages and physical places by keyword query.

    Returns: List of places with name, facebook_id, url, verification status, and profile image.

    Arguments:
    - query (required): Place/business type search string (e.g., 'pizza', 'bookstore', 'hotel')
    - location_uid (optional): Location UID to filter by geographic area

    Use this to:
    - Find local businesses
    - Discover restaurants and cafes
    - Locate service providers
    - Research retail locations

    Note: Similar to search_pages but specifically for businesses with physical locations.
    """
    args_schema: Type[BaseModel] = SearchPlacesInput

    def _run(self, query: str, location_uid: str = None) -> str:
        """Sync version - not used by async agents."""
        raise NotImplementedError("Use async version (_arun) instead")

    async def _arun(self, query: str, location_uid: str = None) -> str:
        """Execute the tool asynchronously."""
        try:
            scraper = FacebookScraper()
            places = await scraper.search_places(query, location_uid=location_uid)

            if not places:
                return f"No places found for query: {query}"

            output = f"Facebook Places for '{query}':\n\n"
            for i, place in enumerate(places[:15], 1):
                name = place.name
                place_id = place.facebook_id
                verified = "✓ Verified" if place.is_verified else ""

                output += f"{i}. {name} {verified}\n"
                output += f"   Place ID: {place_id}\n"
                output += f"   URL: {place.url}\n\n"

            return output
        except Exception as e:
            logger.error("Error searching places", error=str(e))
            return f"Error searching places: {str(e)}"


# ============================================================================
# PAGE TOOLS
# ============================================================================

class GetPageDetailsInput(BaseModel):
    """Input for GetPageDetails tool."""
    page_url: str = Field(
        ...,
        description="Full Facebook page URL (e.g., 'https://www.facebook.com/facebook' or 'https://www.facebook.com/YourPageName')"
    )


class GetPageDetailsTool(BaseTool):
    """Tool to get detailed Facebook page information."""

    name: str = "get_facebook_page_details"
    description: str = """
    Get comprehensive details about a specific Facebook page by URL.

    Returns: Page details including name, page_id, verified status, likes, followers, categories, bio (intro), contact info (phone, email, address), website, rating, cover_image, and reels_page_id.

    Arguments:
    - page_url (required): Full Facebook page URL (e.g., 'https://www.facebook.com/facebook')

    Use this to:
    - Analyze page profiles
    - Get audience size metrics
    - Extract contact information
    - Verify page authenticity

    Note: The returned page_id can be used with get_facebook_page_posts and get_facebook_page_events. The reels_page_id can be used to fetch reels.
    """
    args_schema: Type[BaseModel] = GetPageDetailsInput

    def _run(self, page_url: str) -> str:
        """Sync version - not used by async agents."""
        raise NotImplementedError("Use async version (_arun) instead")

    async def _arun(self, page_url: str) -> str:
        """Execute the tool asynchronously."""
        try:
            scraper = FacebookScraper()
            page = await scraper.get_page_details(page_url)

            if not page:
                return f"Could not retrieve page details for: {page_url}"

            output = f"Facebook Page Details:\n\n"
            output += f"Name: {page.name}\n"
            output += f"Page ID: {page.page_id}\n"
            output += f"Verified: {'Yes ✓' if page.verified else 'No'}\n"
            output += f"Likes: {page.likes:,}\n"
            output += f"Followers: {page.followers:,}\n"

            if page.categories:
                output += f"Categories: {', '.join(page.categories)}\n"

            if page.intro:
                output += f"\nBio: {page.intro}\n"

            if page.phone:
                output += f"Phone: {page.phone}\n"

            if page.email:
                output += f"Email: {page.email}\n"

            if page.address:
                output += f"Address: {page.address}\n"

            if page.website:
                output += f"Website: {page.website}\n"

            if page.rating:
                output += f"Rating: {page.rating} stars\n"

            output += f"\nURL: {page.url}\n"

            return output
        except Exception as e:
            logger.error("Error getting page details", error=str(e))
            return f"Error getting page details: {str(e)}"


class GetPagePostsInput(BaseModel):
    """Input for GetPagePosts tool."""
    page_id: str = Field(
        ...,
        description="Facebook page ID (numeric string like '100064860875397'). Get this from get_facebook_page_details or search_facebook_pages."
    )
    limit: int = Field(
        10,
        description="Number of posts to retrieve (default: 10, max: 25)"
    )


class GetPagePostsTool(BaseTool):
    """Tool to get posts from a Facebook page."""

    name: str = "get_facebook_page_posts"
    description: str = """
    Get recent posts from a specific Facebook page by page_id.

    Returns: List of posts with post_id, message, url, timestamp, engagement metrics (reactions_count, comments_count, reshare_count), author info, and media (image/video).

    Arguments:
    - page_id (required): Numeric Facebook page ID (e.g., '100064860875397'). Must first get this from get_facebook_page_details or search_facebook_pages.
    - limit (optional): Number of posts to retrieve (default: 10, max: 25)

    Use this to:
    - Analyze page content strategy
    - Monitor posting frequency
    - Track engagement patterns
    - Research competitor content

    Important: This requires a page_id (numeric), NOT a page URL. First call get_facebook_page_details with the page URL to get the page_id.
    """
    args_schema: Type[BaseModel] = GetPagePostsInput

    def _run(self, page_id: str, limit: int = 10) -> str:
        """Sync version - not used by async agents."""
        raise NotImplementedError("Use async version (_arun) instead")

    async def _arun(self, page_id: str, limit: int = 10) -> str:
        """Execute the tool asynchronously."""
        try:
            scraper = FacebookScraper()
            posts = await scraper.get_page_posts(page_id)

            if not posts:
                return f"No posts found for page {page_id}"

            # Limit the number of posts
            posts = posts[:min(limit, 25)]

            output = f"Recent Posts from Page {page_id}:\n\n"
            for i, post in enumerate(posts, 1):
                message = post.message or "[No text]"
                reactions = post.reactions_count
                comments = post.comments_count
                shares = post.reshare_count
                author = post.author.name

                output += f"{i}. {message[:200]}...\n"
                output += f"   Posted by: {author}\n"
                output += f"   Engagement: {reactions} reactions, {comments} comments, {shares} shares\n"

                if post.image:
                    output += f"   📷 Has image\n"
                if post.video:
                    output += f"   🎥 Has video\n"

                output += f"   URL: {post.url}\n\n"

            return output
        except Exception as e:
            logger.error("Error getting page posts", error=str(e))
            return f"Error getting page posts: {str(e)}"


class GetPageEventsInput(BaseModel):
    """Input for GetPageEvents tool."""
    page_id: str = Field(
        ...,
        description="Facebook page ID (numeric string). Get this from get_facebook_page_details or search_facebook_pages."
    )
    past_events: bool = Field(
        False,
        description="If True, get past events; if False (default), get future/upcoming events"
    )


class GetPageEventsTool(BaseTool):
    """Tool to get events from a Facebook page."""

    name: str = "get_facebook_page_events"
    description: str = """
    Get upcoming or past events hosted by a specific Facebook page.

    Returns: List of events with id, name, is_cancelled, event_author, event_place (location info), url, and cover media.

    Arguments:
    - page_id (required): Numeric Facebook page ID. Must first get this from get_facebook_page_details or search_facebook_pages.
    - past_events (optional): Set true to get past events, false (default) for upcoming events

    Use this to:
    - Discover events hosted by a page
    - Track event schedules
    - Research venue event history
    - Monitor cancellations

    Important: Requires a page_id (numeric), NOT a URL. Get the page_id first using get_facebook_page_details.
    """
    args_schema: Type[BaseModel] = GetPageEventsInput

    def _run(self, page_id: str, past_events: bool = False) -> str:
        """Sync version - not used by async agents."""
        raise NotImplementedError("Use async version (_arun) instead")

    async def _arun(self, page_id: str, past_events: bool = False) -> str:
        """Execute the tool asynchronously."""
        try:
            scraper = FacebookScraper()

            if past_events:
                events = await scraper.get_page_past_events(page_id)
                time_label = "Past"
            else:
                events = await scraper.get_page_future_events(page_id)
                time_label = "Upcoming"

            if not events:
                return f"No {time_label.lower()} events found for page {page_id}"

            output = f"{time_label} Events for Page {page_id}:\n\n"
            for i, event in enumerate(events[:15], 1):
                name = event.name
                location = event.event_place.location if event.event_place else "N/A"
                venue = event.event_place.name if event.event_place else "N/A"
                cancelled = " [CANCELLED]" if event.is_cancelled else ""

                output += f"{i}. {name}{cancelled}\n"
                output += f"   Location: {location}\n"
                output += f"   Venue: {venue}\n"
                output += f"   URL: {event.url}\n\n"

            return output
        except Exception as e:
            logger.error("Error getting page events", error=str(e))
            return f"Error getting page events: {str(e)}"


# ============================================================================
# EVENT TOOLS
# ============================================================================

class GetEventDetailsInput(BaseModel):
    """Input for GetEventDetails tool."""
    event_id: str = Field(
        ...,
        description="Facebook event ID (numeric string like '1259800548576578'). Get this from search_facebook_events or get_facebook_page_events."
    )


class GetEventDetailsTool(BaseTool):
    """Tool to get detailed Facebook event information."""

    name: str = "get_facebook_event_details"
    description: str = """
    Get comprehensive details about a specific Facebook event by event_id.

    Returns: Full event details including event_id, title, details (description), location_text, lat/lng coordinates, start_date, start_time, end_date, end_time, local_formatted_time, hosts, responded_count, cover_image_url, and related_events.

    Arguments:
    - event_id (required): Numeric Facebook event ID (e.g., '1259800548576578'). Get this from search_facebook_events or get_facebook_page_events.

    Use this to:
    - Get complete event information
    - Extract event descriptions and schedules
    - Find event locations and coordinates
    - See attendance numbers
    - Discover related events

    Important: Requires an event_id (numeric), NOT an event URL. Get the event_id from search results first.
    """
    args_schema: Type[BaseModel] = GetEventDetailsInput

    def _run(self, event_id: str) -> str:
        """Sync version - not used by async agents."""
        raise NotImplementedError("Use async version (_arun) instead")

    async def _arun(self, event_id: str) -> str:
        """Execute the tool asynchronously."""
        try:
            scraper = FacebookScraper()
            response = await scraper.get_event_details(event_id)

            if not response or not response.event:
                return f"Could not retrieve event details for: {event_id}"

            event = response.event

            output = f"Facebook Event Details:\n\n"
            output += f"Title: {event.title}\n"
            output += f"Event ID: {event.event_id}\n\n"

            output += f"📅 Date & Time:\n"
            output += f"   {event.local_formatted_time}\n"
            output += f"   Start: {event.start_date} {event.start_time}\n"
            if event.end_date and event.end_time:
                output += f"   End: {event.end_date} {event.end_time}\n"
            output += f"\n"

            output += f"📍 Location:\n"
            output += f"   {event.location_text}\n"
            if event.lat and event.lng:
                output += f"   Coordinates: {event.lat}, {event.lng}\n"
            output += f"\n"

            if event.hosts:
                output += f"🎭 Hosts: {', '.join(event.hosts)}\n\n"

            output += f"👥 Responded Count: {event.responded_count:,}\n\n"

            if event.details:
                output += f"Description:\n{event.details[:500]}...\n\n"

            if event.related_events:
                output += f"Related Events: {len(event.related_events)}\n"

            return output
        except Exception as e:
            logger.error("Error getting event details", error=str(e))
            return f"Error getting event details: {str(e)}"


# ============================================================================
# GROUP TOOLS
# ============================================================================

class GetGroupPostsInput(BaseModel):
    """Input for GetGroupPosts tool."""
    group_id: str = Field(
        ...,
        description="Facebook group ID (numeric string). Get this from a group URL or search."
    )
    limit: int = Field(
        10,
        description="Number of posts to retrieve (default: 10, max: 25)"
    )
    top_posts: bool = Field(
        False,
        description="If True, get top posts; if False (default), get chronological posts"
    )


class GetGroupPostsTool(BaseTool):
    """Tool to get posts from a Facebook group."""

    name: str = "get_facebook_group_posts"
    description: str = """
    Get recent posts from a public Facebook group by group_id.

    Returns: List of posts with post_id, message, url, timestamp, engagement metrics (reactions_count, comments_count), author info, and media (image/album_preview).

    Arguments:
    - group_id (required): Numeric Facebook group ID (e.g., '1439220986320043')
    - limit (optional): Number of posts to retrieve (default: 10, max: 25)
    - top_posts (optional): Set true for top posts, false (default) for chronological

    Use this to:
    - Monitor group discussions
    - Track trending topics
    - Analyze community engagement
    - Research group content patterns

    Important: Only works with public groups or groups you have access to. Requires group_id (numeric).
    """
    args_schema: Type[BaseModel] = GetGroupPostsInput

    def _run(self, group_id: str, limit: int = 10, top_posts: bool = False) -> str:
        """Sync version - not used by async agents."""
        raise NotImplementedError("Use async version (_arun) instead")

    async def _arun(self, group_id: str, limit: int = 10, top_posts: bool = False) -> str:
        """Execute the tool asynchronously."""
        try:
            scraper = FacebookScraper()
            sorting = "TOP_POSTS" if top_posts else "CHRONOLOGICAL"
            posts = await scraper.get_group_posts(group_id, sorting_order=sorting)

            if not posts:
                return f"No posts found for group {group_id}"

            # Limit the number of posts
            posts = posts[:min(limit, 25)]

            output = f"Group Posts from {group_id} ({sorting}):\n\n"
            for i, post in enumerate(posts, 1):
                message = post.message or "[No text]"
                reactions = post.reactions_count
                comments = post.comments_count
                author = post.author.name

                output += f"{i}. {message[:200]}...\n"
                output += f"   Author: {author}\n"
                output += f"   Engagement: {reactions} reactions, {comments} comments\n"
                output += f"   URL: {post.url}\n\n"

            return output
        except Exception as e:
            logger.error("Error getting group posts", error=str(e))
            return f"Error getting group posts: {str(e)}"


def create_facebook_scraper_tools():
    """Create all Facebook scraper tools for use with Langchain agents."""
    return [
        SearchPagesTool(),
        SearchPostsTool(),
        SearchEventsTool(),
        SearchPlacesTool(),
        GetPageDetailsTool(),
        GetPagePostsTool(),
        GetPageEventsTool(),
        GetEventDetailsTool(),
        GetGroupPostsTool(),
    ]
