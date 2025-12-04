# backend/cli/insights.py

"""CLI commands for insights agent and insights fetching."""

import click
from backend.utils import get_logger
from backend.config.settings import settings

logger = get_logger(__name__)


@click.group(name="insights")
def insights():
    """Insights agent commands"""
    pass


@insights.command()
@click.option(
    '--business-asset-id',
    required=True,
    type=str,
    help='Business asset ID (e.g., penndailybuzz, eaglesnationfanhuddle)'
)
@click.option("--days", default=14, help="Number of days to analyze")
def analyze(business_asset_id: str, days: int):
    """Run insights analysis on recent content"""
    import asyncio
    from backend.agents.insights import run_insights_analysis

    logger.info("Running insights analysis", business_asset_id=business_asset_id, days=days)
    click.echo(f"📊 Analyzing content from past {days} days...")

    result = asyncio.run(run_insights_analysis(business_asset_id, days))

    click.echo(f"✅ Insights analysis complete (Report ID: {result['id']})")
    click.echo(f"\nSummary: {result['summary']}")


@insights.command()
@click.option(
    '--business-asset-id',
    required=True,
    type=str,
    help='Business asset ID (e.g., penndailybuzz, eaglesnationfanhuddle)'
)
@click.option("--limit", default=5, help="Number of reports to display")
def list(business_asset_id: str, limit: int):
    """List recent insight reports"""
    import asyncio
    from backend.database.repositories import InsightsRepository

    async def _list_reports():
        repo = InsightsRepository()
        return await repo.get_recent(business_asset_id, limit=limit)

    reports = asyncio.run(_list_reports())

    click.echo(f"\n📈 Recent Insight Reports ({len(reports)}):\n")
    for report in reports:
        click.echo(f"  Summary: {report.summary}")
        click.echo(f"  Created: {report.created_at}")
        click.echo()


@insights.command()
@click.option(
    '--business-asset-id',
    required=True,
    type=str,
    help='Business asset ID (e.g., penndailybuzz, eaglesnationfanhuddle)'
)
def latest(business_asset_id: str):
    """Show the latest insight report"""
    import asyncio
    from backend.database.repositories import InsightsRepository

    async def _get_latest():
        repo = InsightsRepository()
        return await repo.get_latest(business_asset_id)

    report = asyncio.run(_get_latest())

    if not report:
        click.echo("No insight reports found")
        return

    click.echo(f"\n📊 Latest Insight Report\n")
    click.echo(f"Created: {report.created_at}")
    click.echo(f"\nSummary:\n{report.summary}\n")
    click.echo(f"\nFindings:\n{report.findings}\n")


# =============================================================================
# INSIGHTS FETCHING COMMANDS
# =============================================================================


@insights.command(name="fetch-account")
@click.option(
    '--business-asset-id',
    required=True,
    type=str,
    help='Business asset ID (e.g., penndailybuzz, eaglesnationfanhuddle)'
)
def fetch_account(business_asset_id: str):
    """Fetch and cache account-level insights (page/profile metrics).

    This fetches:
    - Facebook page insights (views, engagements, followers, reactions)
    - Instagram account insights (followers, reach, profile info)

    Metrics are stored in the database for use by the insights agent.
    """
    import asyncio
    from backend.services.insights_fetcher import fetch_account_insights

    logger.info(
        "Fetching account insights",
        business_asset_id=business_asset_id
    )
    click.echo(f"📊 Fetching account-level insights for {business_asset_id}...")

    result = asyncio.run(fetch_account_insights(business_asset_id))

    # Display results
    if result.get("facebook"):
        fb = result["facebook"]
        click.echo(f"\n✅ Facebook Page Insights:")
        click.echo(f"   Page: {fb.get('page_name', 'N/A')}")
        click.echo(f"   Views (day): {fb.get('page_views_total', 0)}")
        click.echo(f"   Engagements (day): {fb.get('page_post_engagements', 0)}")
        click.echo(f"   Follows: {fb.get('page_follows', 0)}")

    if result.get("instagram"):
        ig = result["instagram"]
        click.echo(f"\n✅ Instagram Account Insights:")
        click.echo(f"   Username: @{ig.get('username', 'N/A')}")
        click.echo(f"   Followers: {ig.get('followers_count', 0)}")
        click.echo(f"   Reach (day): {ig.get('reach_day', 0)}")
        click.echo(f"   Reach (week): {ig.get('reach_week', 0)}")

    if result.get("errors"):
        click.echo(f"\n⚠️  Errors encountered:")
        for error in result["errors"]:
            click.echo(f"   - {error}")


@insights.command(name="fetch-posts")
@click.option(
    '--business-asset-id',
    required=True,
    type=str,
    help='Business asset ID (e.g., penndailybuzz, eaglesnationfanhuddle)'
)
@click.option(
    '--limit',
    default=None,
    type=int,
    help=f'Max posts to fetch per platform (default: {settings.insights_post_limit})'
)
@click.option(
    '--days-back',
    default=None,
    type=int,
    help=f'Only fetch posts from last N days (default: {settings.insights_post_days_back})'
)
def fetch_posts(business_asset_id: str, limit: int, days_back: int):
    """Fetch and cache post-level insights for recent posts.

    This fetches:
    - Facebook post insights (reach, impressions, reactions, comments, shares)
    - Facebook video insights (views, watch time, avg watch time)
    - Instagram media insights (likes, comments, saves, shares, views)

    Metrics are stored in the database for use by the insights agent.
    """
    import asyncio
    from backend.services.insights_fetcher import fetch_post_insights

    # Use defaults from settings if not provided
    limit = limit or settings.insights_post_limit
    days_back = days_back or settings.insights_post_days_back

    logger.info(
        "Fetching post insights",
        business_asset_id=business_asset_id,
        limit=limit,
        days_back=days_back
    )
    click.echo(f"📊 Fetching post-level insights for {business_asset_id}...")
    click.echo(f"   Limit: {limit} posts per platform")
    click.echo(f"   Days back: {days_back}")

    result = asyncio.run(fetch_post_insights(business_asset_id, limit=limit, days_back=days_back))

    # Display results
    fb_count = result.get("facebook_posts_fetched", 0)
    fb_videos = result.get("facebook_videos_fetched", 0)
    ig_count = result.get("instagram_media_fetched", 0)

    click.echo(f"\n✅ Fetch Complete:")
    click.echo(f"   Facebook posts: {fb_count}")
    click.echo(f"   Facebook videos: {fb_videos}")
    click.echo(f"   Instagram media: {ig_count}")

    if result.get("errors"):
        click.echo(f"\n⚠️  Errors encountered: {len(result['errors'])}")
        for error in result["errors"][:5]:  # Show first 5 errors
            click.echo(f"   - {error}")


@insights.command(name="fetch-all")
@click.option(
    '--business-asset-id',
    required=True,
    type=str,
    help='Business asset ID (e.g., penndailybuzz, eaglesnationfanhuddle)'
)
def fetch_all(business_asset_id: str):
    """Fetch all insights (account + posts) for a business asset.

    This is a convenience command that runs both fetch-account and fetch-posts.
    """
    import asyncio
    from backend.services.insights_fetcher import fetch_all_insights

    logger.info(
        "Fetching all insights",
        business_asset_id=business_asset_id
    )
    click.echo(f"📊 Fetching all insights for {business_asset_id}...")

    result = asyncio.run(fetch_all_insights(business_asset_id))

    click.echo(f"\n✅ All insights fetched successfully")
    click.echo(f"   Account insights: {'✓' if result.get('account') else '✗'}")
    click.echo(f"   Post insights: {'✓' if result.get('posts') else '✗'}")

    total_errors = len(result.get("account", {}).get("errors", [])) + len(result.get("posts", {}).get("errors", []))
    if total_errors > 0:
        click.echo(f"\n⚠️  Total errors: {total_errors}")


@insights.command(name="show-cached")
@click.option(
    '--business-asset-id',
    required=True,
    type=str,
    help='Business asset ID (e.g., penndailybuzz, eaglesnationfanhuddle)'
)
@click.option(
    '--platform',
    type=click.Choice(['facebook', 'instagram', 'all']),
    default='all',
    help='Platform to show cached insights for'
)
def show_cached(business_asset_id: str, platform: str):
    """Show cached insights from the database.

    Displays the most recently fetched insights data.
    """
    import asyncio
    from backend.services.insights_fetcher import get_cached_insights

    logger.info(
        "Showing cached insights",
        business_asset_id=business_asset_id,
        platform=platform
    )

    result = asyncio.run(get_cached_insights(business_asset_id, platform))

    if platform in ('facebook', 'all') and result.get("facebook_page"):
        fb = result["facebook_page"]
        click.echo(f"\n📘 Facebook Page Insights (cached):")
        click.echo(f"   Page: {fb.page_name or 'N/A'}")
        click.echo(f"   Last fetched: {fb.metrics_fetched_at}")
        click.echo(f"   Views (day): {fb.page_views_total}")
        click.echo(f"   Engagements (day): {fb.page_post_engagements}")
        click.echo(f"   Follows: {fb.page_follows}")
        click.echo(f"   Video views (day): {fb.page_video_views}")

    if platform in ('facebook', 'all') and result.get("facebook_posts"):
        posts = result["facebook_posts"]
        click.echo(f"\n📘 Facebook Posts ({len(posts)} cached):")
        for post in posts[:5]:  # Show first 5
            click.echo(f"   - {post.platform_post_id}: {post.reactions_total} reactions, {post.comments} comments")

    if platform in ('instagram', 'all') and result.get("instagram_account"):
        ig = result["instagram_account"]
        click.echo(f"\n📸 Instagram Account Insights (cached):")
        click.echo(f"   Username: @{ig.username or 'N/A'}")
        click.echo(f"   Last fetched: {ig.metrics_fetched_at}")
        click.echo(f"   Followers: {ig.followers_count}")
        click.echo(f"   Reach (day): {ig.reach_day}")
        click.echo(f"   Reach (week): {ig.reach_week}")

    if platform in ('instagram', 'all') and result.get("instagram_media"):
        media = result["instagram_media"]
        click.echo(f"\n📸 Instagram Media ({len(media)} cached):")
        for m in media[:5]:  # Show first 5
            click.echo(f"   - {m.platform_media_id}: {m.likes} likes, {m.comments} comments, {m.views} views")
