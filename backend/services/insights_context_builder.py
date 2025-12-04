# backend/services/insights_context_builder.py

"""
Context builder for the insights agent.

Reads cached metrics from the database instead of making live API calls.
This provides faster context building and reduces API rate limiting.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from backend.config.settings import settings
from backend.database.repositories.completed_posts import CompletedPostRepository
from backend.database.repositories.insights_metrics import (
    FacebookPageInsightsRepository,
    FacebookPostInsightsRepository,
    FacebookVideoInsightsRepository,
    InstagramAccountInsightsRepository,
    InstagramMediaInsightsRepository,
)
from backend.database.repositories.platform_comments import PlatformCommentRepository
from backend.models.insights import (
    FacebookPageInsights,
    FacebookPostInsights,
    FacebookVideoInsights,
    InstagramAccountInsights,
    InstagramMediaInsights,
)
from backend.utils import get_logger

logger = get_logger(__name__)


@dataclass
class PostWithEngagement:
    """A post with its engagement metrics and comments."""
    # Post details
    post_id: str
    platform: str
    post_type: str
    text: str
    published_at: Optional[datetime]
    platform_post_id: Optional[str]

    # Engagement metrics (populated based on post type)
    metrics: Optional[Dict[str, Any]] = None

    # Video metrics (for video posts)
    video_metrics: Optional[Dict[str, Any]] = None

    # Comments on this post
    comments: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class InsightsContext:
    """Complete context for the insights agent."""
    business_asset_id: str

    # Account-level metrics (cached from database)
    facebook_page_insights: Optional[FacebookPageInsights] = None
    instagram_account_insights: Optional[InstagramAccountInsights] = None

    # Posts with engagement
    facebook_posts: List[PostWithEngagement] = field(default_factory=list)
    instagram_posts: List[PostWithEngagement] = field(default_factory=list)

    # Summary stats
    total_facebook_posts: int = 0
    total_instagram_posts: int = 0
    analysis_period_days: int = 14

    # Data freshness
    facebook_page_last_fetched: Optional[datetime] = None
    instagram_account_last_fetched: Optional[datetime] = None


async def build_insights_context(business_asset_id: str) -> InsightsContext:
    """
    Build the complete context for the insights agent.

    Fetches:
    - Recent Facebook posts with engagement metrics and comments
    - Recent Instagram posts with engagement metrics and comments
    - Account-level metrics for both platforms

    Args:
        business_asset_id: The business asset to analyze

    Returns:
        InsightsContext with all data populated
    """
    logger.info("Building insights context", business_asset_id=business_asset_id)

    context = InsightsContext(
        business_asset_id=business_asset_id,
        analysis_period_days=settings.insights_account_metrics_days
    )

    # Fetch account-level metrics
    await _fetch_account_metrics(context)

    # Fetch posts and their engagement
    await _fetch_posts_with_engagement(context)

    logger.info(
        "Insights context built",
        facebook_posts=len(context.facebook_posts),
        instagram_posts=len(context.instagram_posts)
    )

    return context


async def _fetch_account_metrics(context: InsightsContext) -> None:
    """Fetch account-level metrics from cached database."""
    # Facebook page insights (cached)
    try:
        fb_repo = FacebookPageInsightsRepository()
        fb_insights = await fb_repo.get_latest(context.business_asset_id)
        if fb_insights:
            context.facebook_page_insights = fb_insights
            context.facebook_page_last_fetched = fb_insights.metrics_fetched_at
            logger.debug(
                "Loaded Facebook page insights from cache",
                last_fetched=fb_insights.metrics_fetched_at
            )
    except Exception as e:
        logger.warning("Failed to load Facebook page insights from cache", error=str(e))

    # Instagram account insights (cached)
    try:
        ig_repo = InstagramAccountInsightsRepository()
        ig_insights = await ig_repo.get_latest(context.business_asset_id)
        if ig_insights:
            context.instagram_account_insights = ig_insights
            context.instagram_account_last_fetched = ig_insights.metrics_fetched_at
            logger.debug(
                "Loaded Instagram account insights from cache",
                last_fetched=ig_insights.metrics_fetched_at
            )
    except Exception as e:
        logger.warning("Failed to load Instagram account insights from cache", error=str(e))


async def _fetch_posts_with_engagement(context: InsightsContext) -> None:
    """Fetch recent published posts and their cached engagement metrics from database."""
    posts_repo = CompletedPostRepository()
    comments_repo = PlatformCommentRepository()

    # Initialize metrics repositories
    fb_post_repo = FacebookPostInsightsRepository()
    fb_video_repo = FacebookVideoInsightsRepository()
    ig_media_repo = InstagramMediaInsightsRepository()

    # Fetch published Facebook posts
    fb_posts = await posts_repo.get_recent_published_by_platform(
        business_asset_id=context.business_asset_id,
        platform="facebook",
        limit=settings.insights_facebook_posts_limit
    )
    context.total_facebook_posts = len(fb_posts)

    for post in fb_posts:
        post_with_engagement = PostWithEngagement(
            post_id=str(post.id),
            platform="facebook",
            post_type=post.post_type,
            text=post.text,
            published_at=post.published_at,
            platform_post_id=post.platform_post_id
        )

        # Fetch cached post metrics from database
        if post.platform_post_id:
            try:
                cached_metrics = await fb_post_repo.get_by_post_id(
                    context.business_asset_id,
                    post.platform_post_id
                )
                if cached_metrics:
                    post_with_engagement.metrics = cached_metrics.model_dump()
            except Exception as e:
                logger.debug(f"No cached post metrics for {post.platform_post_id}: {e}")

            # For video posts, also get video-specific metrics
            if post.post_type == "facebook_video":
                try:
                    video_id = post.platform_video_id or post.platform_post_id
                    cached_video = await fb_video_repo.get_by_video_id(
                        context.business_asset_id,
                        video_id
                    )
                    if cached_video:
                        post_with_engagement.video_metrics = cached_video.model_dump()
                except Exception as e:
                    logger.debug(f"No cached video metrics for {post.platform_post_id}: {e}")

        # Fetch comments from database
        try:
            comments = await comments_repo.get_comments_by_post(
                business_asset_id=context.business_asset_id,
                platform="facebook",
                post_id=post.platform_post_id,
            )
            post_with_engagement.comments = [c.model_dump() for c in comments[:20]]
        except Exception as e:
            logger.debug(f"No comments for FB post {post.platform_post_id}: {e}")

        context.facebook_posts.append(post_with_engagement)

    # Fetch published Instagram posts
    ig_posts = await posts_repo.get_recent_published_by_platform(
        business_asset_id=context.business_asset_id,
        platform="instagram",
        limit=settings.insights_instagram_posts_limit
    )
    context.total_instagram_posts = len(ig_posts)

    for post in ig_posts:
        post_with_engagement = PostWithEngagement(
            post_id=str(post.id),
            platform="instagram",
            post_type=post.post_type,
            text=post.text,
            published_at=post.published_at,
            platform_post_id=post.platform_post_id
        )

        # Fetch cached media metrics from database
        if post.platform_post_id:
            try:
                cached_metrics = await ig_media_repo.get_by_media_id(
                    context.business_asset_id,
                    post.platform_post_id
                )
                if cached_metrics:
                    post_with_engagement.metrics = cached_metrics.model_dump()
            except Exception as e:
                logger.debug(f"No cached media metrics for {post.platform_post_id}: {e}")

        # Fetch comments from database
        try:
            comments = await comments_repo.get_comments_by_post(
                business_asset_id=context.business_asset_id,
                platform="instagram",
                post_id=post.platform_post_id,
            )
            post_with_engagement.comments = [c.model_dump() for c in comments[:20]]
        except Exception as e:
            logger.debug(f"No comments for IG post {post.platform_post_id}: {e}")

        context.instagram_posts.append(post_with_engagement)


def format_context_for_agent(context: InsightsContext) -> str:
    """
    Format the insights context as a string for the agent prompt.

    Args:
        context: The InsightsContext to format

    Returns:
        Formatted string with all context data
    """
    lines = []

    lines.append(f"# Engagement Analysis Context for {context.business_asset_id}")
    lines.append(f"Analysis Period: {context.analysis_period_days} days")
    lines.append("")

    # Account-level metrics
    lines.append("## Account-Level Metrics")
    lines.append("")

    # Facebook page metrics
    lines.append("### Facebook Page Metrics")
    if context.facebook_page_insights:
        fb = context.facebook_page_insights
        lines.append(f"- Page Name: {fb.page_name or 'N/A'}")
        lines.append(f"- Last Updated: {context.facebook_page_last_fetched}")
        lines.append(f"- Page Views (day): {fb.page_views_total}")
        lines.append(f"- Page Views (week): {fb.page_views_total_week}")
        lines.append(f"- Page Views (28 days): {fb.page_views_total_days_28}")
        lines.append(f"- Post Engagements (day): {fb.page_post_engagements}")
        lines.append(f"- Post Engagements (week): {fb.page_post_engagements_week}")
        lines.append(f"- Post Engagements (28 days): {fb.page_post_engagements_days_28}")
        lines.append(f"- Page Follows: {fb.page_follows}")
        lines.append(f"- Video Views (day): {fb.page_video_views}")
        lines.append(f"- Media Views (day): {fb.page_media_view}")
        total_reactions = fb.reactions_like_total + fb.reactions_love_total + fb.reactions_wow_total + fb.reactions_haha_total + fb.reactions_sorry_total + fb.reactions_anger_total
        if total_reactions:
            lines.append(f"- Total Reactions (day): {total_reactions}")
    else:
        lines.append("No Facebook page metrics available (run 'insights fetch-account' to populate)")
    lines.append("")

    # Instagram account metrics
    lines.append("### Instagram Account Metrics")
    if context.instagram_account_insights:
        ig = context.instagram_account_insights
        lines.append(f"- Username: @{ig.username or 'N/A'}")
        lines.append(f"- Last Updated: {context.instagram_account_last_fetched}")
        lines.append(f"- Followers: {ig.followers_count}")
        lines.append(f"- Following: {ig.follows_count}")
        lines.append(f"- Media Count: {ig.media_count}")
        lines.append(f"- Reach (day): {ig.reach_day}")
        lines.append(f"- Reach (week): {ig.reach_week}")
        lines.append(f"- Reach (28 days): {ig.reach_days_28}")
    else:
        lines.append("No Instagram account metrics available (run 'insights fetch-account' to populate)")
    lines.append("")

    # Facebook posts
    lines.append("## Facebook Posts")
    lines.append(f"Total posts in database: {context.total_facebook_posts}")
    lines.append(f"Posts with metrics: {len([p for p in context.facebook_posts if p.metrics])}")
    lines.append("")

    for i, post in enumerate(context.facebook_posts, 1):
        lines.append(f"### Facebook Post #{i}")
        lines.append(f"- Type: {post.post_type}")
        lines.append(f"- Published: {post.published_at}")
        text = post.text or ""
        lines.append(f"- Text: {text[:200]}{'...' if len(text) > 200 else ''}")

        if post.metrics:
            lines.append("- Post Metrics:")
            lines.append(f"  - Reach (unique): {post.metrics.get('post_impressions_unique', 0)}")
            lines.append(f"  - Reach (organic): {post.metrics.get('post_impressions_organic_unique', 0)}")
            lines.append(f"  - Total Reactions: {post.metrics.get('reactions_total', 0)}")
            lines.append(f"  - Comments: {post.metrics.get('comments', 0)}")
            lines.append(f"  - Shares: {post.metrics.get('shares', 0)}")
            if post.metrics.get('reactions_like'):
                lines.append(f"  - Likes: {post.metrics.get('reactions_like', 0)}")
            if post.metrics.get('reactions_love'):
                lines.append(f"  - Loves: {post.metrics.get('reactions_love', 0)}")

        # Video-specific metrics
        if post.video_metrics:
            lines.append("- Video Metrics:")
            lines.append(f"  - Total Views: {post.video_metrics.get('post_video_views', 0)}")
            lines.append(f"  - Unique Views: {post.video_metrics.get('post_video_views_unique', 0)}")
            lines.append(f"  - Total Watch Time: {post.video_metrics.get('post_video_view_time_ms', 0)}ms")
            lines.append(f"  - Avg Watch Time: {post.video_metrics.get('post_video_avg_time_watched_ms', 0)}ms")
            if post.video_metrics.get('video_length_ms'):
                lines.append(f"  - Video Length: {post.video_metrics.get('video_length_ms', 0)}ms")

        if not post.metrics and not post.video_metrics:
            lines.append("- Metrics: Not cached (run 'insights fetch-posts' to populate)")

        if post.comments:
            lines.append(f"- Comments ({len(post.comments)}):")
            for comment in post.comments[:5]:  # Limit to 5 comments shown
                username = comment.get('commenter_username', 'Unknown')
                text = comment.get('comment_text', '')[:100]
                lines.append(f"  - @{username}: {text}")
            if len(post.comments) > 5:
                lines.append(f"  ... and {len(post.comments) - 5} more comments")
        lines.append("")

    # Instagram posts
    lines.append("## Instagram Posts")
    lines.append(f"Total posts in database: {context.total_instagram_posts}")
    lines.append(f"Posts with metrics: {len([p for p in context.instagram_posts if p.metrics])}")
    lines.append("")

    for i, post in enumerate(context.instagram_posts, 1):
        lines.append(f"### Instagram Post #{i}")
        lines.append(f"- Type: {post.post_type}")
        lines.append(f"- Published: {post.published_at}")
        if post.metrics and post.metrics.get('permalink'):
            lines.append(f"- Link: {post.metrics.get('permalink')}")
        text = post.text or ""
        lines.append(f"- Text: {text[:200]}{'...' if len(text) > 200 else ''}")

        if post.metrics:
            lines.append("- Metrics:")
            lines.append(f"  - Views: {post.metrics.get('views', 0)}")
            lines.append(f"  - Likes: {post.metrics.get('likes', 0)}")
            lines.append(f"  - Comments: {post.metrics.get('comments', 0)}")
            lines.append(f"  - Saves: {post.metrics.get('saved', 0)}")
            lines.append(f"  - Shares: {post.metrics.get('shares', 0)}")
            # For reels, show watch time metrics
            if post.metrics.get('ig_reels_avg_watch_time_ms'):
                lines.append(f"  - Avg Watch Time: {post.metrics.get('ig_reels_avg_watch_time_ms')}ms")
            if post.metrics.get('ig_reels_video_view_total_time_ms'):
                lines.append(f"  - Total Watch Time: {post.metrics.get('ig_reels_video_view_total_time_ms')}ms")
        else:
            lines.append("- Metrics: Not cached (run 'insights fetch-posts' to populate)")

        if post.comments:
            lines.append(f"- Comments ({len(post.comments)}):")
            for comment in post.comments[:5]:
                username = comment.get('commenter_username', 'Unknown')
                text = comment.get('comment_text', '')[:100]
                lines.append(f"  - @{username}: {text}")
            if len(post.comments) > 5:
                lines.append(f"  ... and {len(post.comments) - 5} more comments")
        lines.append("")

    return "\n".join(lines)
