# backend/services/insights_context_builder.py

"""
Context builder for the insights agent.

Fetches all posts, metrics, and comments needed for the context-stuffing approach.
This eliminates the need for the agent to make tool calls.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from backend.config.settings import settings
from backend.database.repositories.completed_posts import CompletedPostRepository
from backend.tools.engagement_tools import (
    fetch_facebook_page_insights,
    fetch_facebook_post_insights,
    fetch_facebook_video_insights,
    fetch_instagram_media_insights,
    fetch_instagram_account_insights,
    fetch_platform_comments,
)
from backend.models.insights import (
    FacebookPageInsight,
    FacebookPostInsight,
    FacebookVideoInsight,
    InstagramMediaInsight,
    InstagramAccountInsight,
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

    # Comments on this post
    comments: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class InsightsContext:
    """Complete context for the insights agent."""
    business_asset_id: str

    # Account-level metrics
    facebook_page_insights: List[FacebookPageInsight] = field(default_factory=list)
    instagram_account_insights: Optional[InstagramAccountInsight] = None

    # Posts with engagement
    facebook_posts: List[PostWithEngagement] = field(default_factory=list)
    instagram_posts: List[PostWithEngagement] = field(default_factory=list)

    # Summary stats
    total_facebook_posts: int = 0
    total_instagram_posts: int = 0
    analysis_period_days: int = 14


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
    """Fetch account-level metrics for both platforms."""
    days_back = settings.insights_account_metrics_days

    # Facebook page insights
    context.facebook_page_insights = await fetch_facebook_page_insights(
        business_asset_id=context.business_asset_id,
        period="day",
        days_back=days_back
    )

    # Instagram account insights
    context.instagram_account_insights = await fetch_instagram_account_insights(
        business_asset_id=context.business_asset_id,
        days_back=days_back
    )


async def _fetch_posts_with_engagement(context: InsightsContext) -> None:
    """Fetch recent published posts and their engagement metrics."""
    posts_repo = CompletedPostRepository()

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

        # Fetch engagement based on post type
        if post.post_type == "facebook_video":
            metrics = await fetch_facebook_video_insights(
                business_asset_id=context.business_asset_id,
                video_id=post.platform_post_id
            )
            if metrics:
                post_with_engagement.metrics = metrics.model_dump()
        else:
            # facebook_feed or other types
            metrics = await fetch_facebook_post_insights(
                business_asset_id=context.business_asset_id,
                platform_post_id=post.platform_post_id
            )
            if metrics:
                post_with_engagement.metrics = metrics.model_dump()

        # Fetch comments for this post
        comments = await fetch_platform_comments(
            business_asset_id=context.business_asset_id,
            platform="facebook",
            post_id=post.platform_post_id,
            limit=20
        )
        post_with_engagement.comments = comments

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

        # Determine media type for Instagram
        if "reel" in post.post_type.lower():
            media_type = "reel"
        elif "carousel" in post.post_type.lower():
            media_type = "carousel"
        else:
            media_type = "image"

        metrics = await fetch_instagram_media_insights(
            business_asset_id=context.business_asset_id,
            media_id=post.platform_post_id,
            media_type=media_type
        )
        if metrics:
            post_with_engagement.metrics = metrics.model_dump()

        # Fetch comments for this post
        comments = await fetch_platform_comments(
            business_asset_id=context.business_asset_id,
            platform="instagram",
            post_id=post.platform_post_id,
            limit=20
        )
        post_with_engagement.comments = comments

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
        # Aggregate by metric name
        metrics_by_name: Dict[str, List[int]] = {}
        for insight in context.facebook_page_insights:
            if insight.name not in metrics_by_name:
                metrics_by_name[insight.name] = []
            if isinstance(insight.value, (int, float)):
                metrics_by_name[insight.name].append(insight.value)

        for name, values in metrics_by_name.items():
            total = sum(values)
            lines.append(f"- {name}: {total} (over {len(values)} days)")
    else:
        lines.append("No Facebook page metrics available")
    lines.append("")

    # Instagram account metrics
    lines.append("### Instagram Account Metrics")
    if context.instagram_account_insights:
        ig = context.instagram_account_insights
        lines.append(f"- Accounts Engaged: {ig.accounts_engaged}")
        lines.append(f"- Total Interactions: {ig.total_interactions}")
        lines.append(f"- Reach: {ig.reach}")
        lines.append(f"- Views: {ig.views}")
        lines.append(f"- Profile Link Taps: {ig.profile_link_taps}")
        if ig.follows is not None:
            lines.append(f"- New Follows: {ig.follows}")
        if ig.unfollows is not None:
            lines.append(f"- Unfollows: {ig.unfollows}")
    else:
        lines.append("No Instagram account metrics available")
    lines.append("")

    # Facebook posts
    lines.append("## Facebook Posts")
    lines.append(f"Total posts in database: {context.total_facebook_posts}")
    lines.append(f"Posts with metrics: {len(context.facebook_posts)}")
    lines.append("")

    for i, post in enumerate(context.facebook_posts, 1):
        lines.append(f"### Facebook Post #{i}")
        lines.append(f"- Type: {post.post_type}")
        lines.append(f"- Published: {post.published_at}")
        lines.append(f"- Text: {post.text[:200]}{'...' if len(post.text) > 200 else ''}")

        if post.metrics:
            lines.append("- Metrics:")
            if post.post_type == "facebook_video":
                lines.append(f"  - Total Views: {post.metrics.get('total_views', 0)}")
                lines.append(f"  - Unique Reach: {post.metrics.get('unique_views', 0)}")
                lines.append(f"  - Avg Watch Time: {post.metrics.get('avg_time_watched_ms', 0)}ms")
                lines.append(f"  - Total Watch Time: {post.metrics.get('total_time_watched_ms', 0)}ms")
                if post.metrics.get('reels_total_plays'):
                    lines.append(f"  - Reels Plays: {post.metrics.get('reels_total_plays')}")
                if post.metrics.get('reels_replay_count'):
                    lines.append(f"  - Replays: {post.metrics.get('reels_replay_count')}")
                if post.metrics.get('reactions_by_type'):
                    lines.append(f"  - Social Actions: {post.metrics.get('reactions_by_type')}")
            else:
                lines.append(f"  - Clicks: {post.metrics.get('clicks', 0)}")
                lines.append(f"  - Reactions: {post.metrics.get('reactions_like', 0)} likes")
                if post.metrics.get('reactions_love'):
                    lines.append(f"  - Loves: {post.metrics.get('reactions_love', 0)}")
                if post.metrics.get('reactions_by_type'):
                    rt = post.metrics['reactions_by_type']
                    lines.append(f"  - Reaction Breakdown: {rt}")
        else:
            lines.append("- Metrics: Not available")

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
    lines.append(f"Posts with metrics: {len(context.instagram_posts)}")
    lines.append("")

    for i, post in enumerate(context.instagram_posts, 1):
        lines.append(f"### Instagram Post #{i}")
        lines.append(f"- Type: {post.post_type}")
        lines.append(f"- Published: {post.published_at}")
        if post.metrics and post.metrics.get('permalink'):
            lines.append(f"- Link: {post.metrics.get('permalink')}")
        lines.append(f"- Text: {post.text[:200]}{'...' if len(post.text) > 200 else ''}")

        if post.metrics:
            lines.append("- Metrics:")
            lines.append(f"  - Reach: {post.metrics.get('reach', 0)}")
            lines.append(f"  - Views: {post.metrics.get('views', 0)}")
            lines.append(f"  - Total Interactions: {post.metrics.get('total_interactions', 0)}")
            lines.append(f"  - Likes: {post.metrics.get('likes', 0)}")
            lines.append(f"  - Comments: {post.metrics.get('comments', 0)}")
            lines.append(f"  - Saves: {post.metrics.get('saves', 0)}")
            lines.append(f"  - Shares: {post.metrics.get('shares', 0)}")
            if post.metrics.get('avg_watch_time_ms'):
                lines.append(f"  - Avg Watch Time: {post.metrics.get('avg_watch_time_ms')}ms")
        else:
            lines.append("- Metrics: Not available")

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
