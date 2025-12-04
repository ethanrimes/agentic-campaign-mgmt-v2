#!/usr/bin/env python3
# backend/scheduler.py

"""
Centralized scheduler for automated content pipeline.

This scheduler orchestrates all automated tasks including:
- Content seed creation (news, trends, ungrounded ideas)
- Analysis and planning
- Content creation
- Publishing to social media platforms

Multi-Tenancy Support:
- Set BUSINESS_ASSETS environment variable with comma-separated list of asset IDs
- Example: BUSINESS_ASSETS=penndailybuzz,eaglesnationfanhuddle,flyeaglesflycommunity
- Each job will run for all active business assets

See SCHEDULER_README.md for usage instructions.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
import signal
import subprocess
import sys
import time
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from backend.utils import get_logger
from backend.database.repositories.business_assets import BusinessAssetRepository
from backend.config.settings import settings

logger = get_logger(__name__)

# Base command for all CLI operations
BASE_CMD = [sys.executable, "-m", "backend.cli.main"]


# ============================================================================
# BUSINESS ASSET MANAGEMENT
# ============================================================================

def get_active_business_assets() -> list[str]:
    """
    Get list of active business asset IDs.

    Reads from BUSINESS_ASSETS environment variable (comma-separated list),
    or falls back to fetching all active assets from the database.

    Returns:
        List of business asset IDs
    """
    # Check environment variable first
    env_assets = os.getenv("BUSINESS_ASSETS", "").strip()

    if env_assets:
        assets = [asset.strip() for asset in env_assets.split(",") if asset.strip()]
        logger.info(f"Using business assets from BUSINESS_ASSETS env var: {assets}")
        return assets

    # Fall back to database
    try:
        repo = BusinessAssetRepository()
        active_assets = repo.get_all_active()
        asset_ids = [asset.id for asset in active_assets]
        logger.info(f"Loaded {len(asset_ids)} active business assets from database: {asset_ids}")
        return asset_ids
    except Exception as e:
        logger.error(f"Failed to load business assets from database: {e}")
        logger.warning("No business assets configured - scheduler will not run any jobs")
        return []


# ============================================================================
# SCHEDULING CONFIGURATION
# ============================================================================

class SchedulingConfig:
    """
    Configuration for post scheduling.

    Defines when and how often posts should be published to each platform.
    All times are in hours unless otherwise specified.

    Media Sharing Architecture:
    - Content creation generates posts with shared media across platforms
    - Verification only runs on primary posts (Instagram)
    - Secondary posts (Facebook) inherit verification status automatically
    - Publishing pipeline: verify -> publish IG -> publish FB
    """

    # Publishing frequency (hours between posts)
    FACEBOOK_POST_INTERVAL_HOURS = 6  # Post to Facebook every 6 hours
    INSTAGRAM_POST_INTERVAL_HOURS = 6  # Post to Instagram every 6 hours

    # Initial delay before first post (hours from content creation)
    FACEBOOK_INITIAL_DELAY_HOURS = 0  # No delay for Facebook posts
    INSTAGRAM_INITIAL_DELAY_HOURS = 0  # No delay for Instagram posts

    # Publishing pipeline check frequency (minutes)
    # How often to run: verification -> facebook publishing -> instagram publishing
    # The pipeline ensures verification happens before any publishing
    PUBLISH_CHECK_INTERVAL_MINUTES = 30

    # Comment management (minutes)
    INSTAGRAM_COMMENT_CHECK_INTERVAL_MINUTES = 180  # Check for new Instagram comments
    COMMENT_RESPONDER_INTERVAL_MINUTES = 15  # Process and respond to pending comments

    # Content pipeline scheduling (hours)
    NEWS_PIPELINE_INTERVAL_HOURS = 12  # News ingestion + deduplication
    TREND_DISCOVERY_INTERVAL_HOURS = 24  # Trend discovery
    UNGROUNDED_GENERATION_INTERVAL_HOURS = 12  # Ungrounded idea generation
    PLANNING_PIPELINE_INTERVAL_HOURS = 6  # Insights + planner + content creation

    # Insights fetching (from settings)
    @property
    def INSIGHTS_FETCH_INTERVAL_HOURS(self):
        return settings.insights_fetch_interval_hours

    @property
    def INSIGHTS_ENABLED(self):
        return settings.insights_enable_scheduled_fetch


SCHEDULING_CONFIG = SchedulingConfig()


def run_command(cmd_args: list, description: str):
    """
    Execute a CLI command and log the result.

    Args:
        cmd_args: Command arguments to append to base command
        description: Human-readable description of the task
    """
    logger.info(f"Starting task: {description}")
    start_time = datetime.now()

    try:
        result = subprocess.run(
            BASE_CMD + cmd_args,
            capture_output=True,
            text=True,
            check=True
        )

        duration = (datetime.now() - start_time).total_seconds()
        logger.info(
            f"Task completed: {description}",
            duration_seconds=duration,
            stdout=result.stdout[-500:] if result.stdout else None
        )

        return result

    except subprocess.CalledProcessError as e:
        duration = (datetime.now() - start_time).total_seconds()
        logger.error(
            f"Task failed: {description}",
            duration_seconds=duration,
            error=str(e),
            stderr=e.stderr[-500:] if e.stderr else None
        )
        raise


# ============================================================================
# CONTENT SEED CREATION JOBS
# ============================================================================

def run_news_ingestion():
    """Ingest news events from Perplexity Sonar for all business assets."""
    assets = get_active_business_assets()
    for asset_id in assets:
        run_command(
            ["news-events", "ingest-perplexity", "--business-asset-id", asset_id, "--count", "3"],
            f"News Event Ingestion - {asset_id}"
        )


def run_news_deduplication():
    """Deduplicate news events after ingestion for all business assets."""
    assets = get_active_business_assets()
    for asset_id in assets:
        run_command(
            ["news-events", "deduplicate", "--business-asset-id", asset_id],
            f"News Event Deduplication - {asset_id}"
        )


def run_news_pipeline():
    """Run complete news ingestion pipeline (ingest + deduplicate) for all business assets."""
    try:
        run_news_ingestion()
        run_news_deduplication()
    except Exception as e:
        logger.error("News pipeline failed", error=str(e))


def run_trend_discovery():
    """Discover trending content on social media for all business assets."""
    assets = get_active_business_assets()
    for asset_id in assets:
        run_command(
            ["trends", "discover", "--business-asset-id", asset_id, "--count", "2"],
            f"Trend Discovery - {asset_id}"
        )


def run_ungrounded_generation():
    """Generate creative ungrounded content ideas for all business assets."""
    assets = get_active_business_assets()
    for asset_id in assets:
        run_command(
            ["ungrounded", "generate", "--business-asset-id", asset_id, "--count", "3"],
            f"Ungrounded Idea Generation - {asset_id}"
        )


# ============================================================================
# INSIGHTS FETCHING JOBS
# ============================================================================

def run_insights_fetch():
    """Fetch and cache insights metrics from Facebook and Instagram for all business assets.

    This fetches:
    - Page-level metrics (Facebook page insights, Instagram account insights)
    - Post-level metrics for recent posts (limited by settings.insights_post_limit)

    Metrics are cached in the database and used by the insights agent.
    """
    assets = get_active_business_assets()
    for asset_id in assets:
        # Fetch page/account level insights
        run_command(
            ["insights", "fetch-account", "--business-asset-id", asset_id],
            f"Fetch Account Insights - {asset_id}"
        )
        # Fetch post-level insights
        run_command(
            ["insights", "fetch-posts", "--business-asset-id", asset_id],
            f"Fetch Post Insights - {asset_id}"
        )


# ============================================================================
# ANALYSIS & PLANNING JOBS
# ============================================================================

def run_insights_analysis():
    """Analyze published content performance for all business assets."""
    assets = get_active_business_assets()
    for asset_id in assets:
        run_command(
            ["insights", "analyze", "--business-asset-id", asset_id, "--days", "30"],
            f"Insights Analysis - {asset_id}"
        )


def run_planner():
    """Run content planning to create tasks from seeds for all business assets."""
    assets = get_active_business_assets()
    for asset_id in assets:
        run_command(
            ["planner", "run", "--business-asset-id", asset_id, "--max-retries", "3"],
            f"Content Planning - {asset_id}"
        )


def run_content_creation():
    """Create content for all pending tasks for all business assets."""
    assets = get_active_business_assets()
    for asset_id in assets:
        run_command(
            ["content", "create-all", "--business-asset-id", asset_id],
            f"Content Creation - {asset_id}"
        )


def run_planning_pipeline():
    """Run complete planning pipeline (insights + planner + content creation) for all business assets."""
    try:
        run_insights_analysis()
        run_planner()
        run_content_creation()
    except Exception as e:
        logger.error("Planning pipeline failed", error=str(e))


# ============================================================================
# VERIFICATION JOBS
# ============================================================================

def run_verification():
    """Verify all unverified pending posts for all business assets.

    This should run before publishing to ensure only verified content is published.
    Uses shared media verification groups - only primary posts are verified,
    secondary posts automatically inherit the verification result.
    """
    assets = get_active_business_assets()
    for asset_id in assets:
        run_command(
            ["verifier", "verify-all", "--business-asset-id", asset_id],
            f"Content Verification - {asset_id}"
        )


# ============================================================================
# PUBLISHING JOBS
# ============================================================================

def run_facebook_publishing():
    """Check for and publish scheduled Facebook posts for all business assets.

    Only publishes posts that have been verified (verification_status='verified').
    """
    assets = get_active_business_assets()
    for asset_id in assets:
        run_command(
            ["publish", "facebook", "--business-asset-id", asset_id],
            f"Facebook Publishing - {asset_id}"
        )


def run_instagram_publishing():
    """Check for and publish scheduled Instagram posts for all business assets.

    Only publishes posts that have been verified (verification_status='verified').
    """
    assets = get_active_business_assets()
    for asset_id in assets:
        run_command(
            ["publish", "instagram", "--business-asset-id", asset_id],
            f"Instagram Publishing - {asset_id}"
        )


def run_publishing_pipeline():
    """Run verification then publish to both platforms.

    This pipeline ensures:
    1. All unverified posts are verified first
    2. Only verified posts are published
    3. Media sharing groups are handled correctly (verify once, publish to both)
    """
    try:
        run_verification()
        run_facebook_publishing()
        run_instagram_publishing()
    except Exception as e:
        logger.error("Publishing pipeline failed", error=str(e))


# ============================================================================
# COMMENT MANAGEMENT JOBS
# ============================================================================

def run_instagram_comment_check():
    """Check for new comments on Instagram posts for all business assets."""
    assets = get_active_business_assets()
    for asset_id in assets:
        run_command(
            ["comments", "check-instagram", "--business-asset-id", asset_id],
            f"Instagram Comment Check - {asset_id}"
        )


def run_comment_responder():
    """Process pending comments and generate responses for all business assets."""
    assets = get_active_business_assets()
    for asset_id in assets:
        run_command(
            ["comments", "respond", "--business-asset-id", asset_id],
            f"Comment Responder - {asset_id}"
        )


# ============================================================================
# SCHEDULER EVENT LISTENERS
# ============================================================================

def job_listener(event):
    """Log scheduler events."""
    if event.exception:
        logger.error(
            "Scheduled job failed",
            job_id=event.job_id,
            exception=str(event.exception)
        )
    else:
        logger.info(
            "Scheduled job completed",
            job_id=event.job_id
        )


# ============================================================================
# SCHEDULER CONFIGURATION
# ============================================================================

def create_scheduler():
    """Create and configure the scheduler with all jobs."""
    executors = {
        'default': ThreadPoolExecutor(20)  # Allow up to 20 concurrent jobs
    }
    scheduler = BackgroundScheduler(executors=executors)

    # Add event listener
    scheduler.add_listener(job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    # ========================================================================
    # CONTENT SEED CREATION
    # ========================================================================

    # News ingestion + deduplication pipeline
    scheduler.add_job(
        run_news_pipeline,
        'interval',
        hours=SCHEDULING_CONFIG.NEWS_PIPELINE_INTERVAL_HOURS,
        id='news_pipeline',
        name='News Ingestion Pipeline',
        max_instances=1,
        coalesce=True,
        next_run_time=datetime.now()  # Run immediately on startup
    )

    # Trend discovery
    scheduler.add_job(
        run_trend_discovery,
        'interval',
        hours=SCHEDULING_CONFIG.TREND_DISCOVERY_INTERVAL_HOURS,
        id='trend_discovery',
        name='Trend Discovery',
        max_instances=1,
        coalesce=True,
        next_run_time=datetime.now()
    )

    # Ungrounded generation
    scheduler.add_job(
        run_ungrounded_generation,
        'interval',
        hours=SCHEDULING_CONFIG.UNGROUNDED_GENERATION_INTERVAL_HOURS,
        id='ungrounded_generation',
        name='Ungrounded Idea Generation',
        max_instances=1,
        coalesce=True,
        next_run_time=datetime.now()
    )

    # ========================================================================
    # INSIGHTS FETCHING
    # ========================================================================

    # Insights fetching - fetch and cache metrics from Facebook and Instagram
    if SCHEDULING_CONFIG.INSIGHTS_ENABLED:
        scheduler.add_job(
            run_insights_fetch,
            'interval',
            hours=SCHEDULING_CONFIG.INSIGHTS_FETCH_INTERVAL_HOURS,
            id='insights_fetch',
            name='Insights Fetching (Facebook + Instagram)',
            max_instances=1,
            coalesce=True,
            next_run_time=datetime.now()  # Run immediately on startup
        )
        logger.info(
            "Insights fetching scheduled",
            interval_hours=SCHEDULING_CONFIG.INSIGHTS_FETCH_INTERVAL_HOURS
        )
    else:
        logger.info("Insights fetching disabled by settings.insights_enable_scheduled_fetch")

    # ========================================================================
    # ANALYSIS & PLANNING
    # ========================================================================

    # Planning pipeline (insights + planner + content creation)
    scheduler.add_job(
        run_planning_pipeline,
        'interval',
        hours=SCHEDULING_CONFIG.PLANNING_PIPELINE_INTERVAL_HOURS,
        id='planning_pipeline',
        name='Planning Pipeline (Insights + Planner + Content Creation)',
        max_instances=1,
        coalesce=True,
        next_run_time=datetime.now()
    )

    # ========================================================================
    # VERIFICATION & PUBLISHING
    # ========================================================================

    # Publishing pipeline (verification + facebook + instagram)
    # Runs verification first, then publishes verified posts to both platforms
    # This ensures media sharing groups are verified once and published to both
    scheduler.add_job(
        run_publishing_pipeline,
        'interval',
        minutes=SCHEDULING_CONFIG.PUBLISH_CHECK_INTERVAL_MINUTES,
        id='publishing_pipeline',
        name='Publishing Pipeline (Verify + Publish)',
        max_instances=1,
        coalesce=True,
        next_run_time=datetime.now()
    )

    # ========================================================================
    # COMMENT MANAGEMENT
    # ========================================================================

    # Instagram comment checking - poll for new comments
    scheduler.add_job(
        run_instagram_comment_check,
        'interval',
        minutes=SCHEDULING_CONFIG.INSTAGRAM_COMMENT_CHECK_INTERVAL_MINUTES,
        id='instagram_comment_check',
        name='Instagram Comment Check',
        max_instances=1,
        coalesce=True,
        next_run_time=datetime.now()
    )

    # Comment responder - process pending comments and generate responses
    scheduler.add_job(
        run_comment_responder,
        'interval',
        minutes=SCHEDULING_CONFIG.COMMENT_RESPONDER_INTERVAL_MINUTES,
        id='comment_responder',
        name='Comment Responder',
        max_instances=1,
        coalesce=True,
        next_run_time=datetime.now()
    )

    # ========================================================================
    # MONITORING
    # ========================================================================

    # Heartbeat - log every 5 minutes to confirm scheduler is alive
    scheduler.add_job(
        lambda: logger.info("Scheduler heartbeat - still running"),
        'interval',
        minutes=5,
        id='heartbeat',
        name='Heartbeat',
        max_instances=1,
        coalesce=True,
        next_run_time=datetime.now()
    )

    return scheduler


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def signal_handler(signum, frame):
    """Handle termination signals."""
    logger.info(f"Received signal {signum}, shutting down...")
    raise SystemExit(0)


def main():
    """Start the scheduler."""
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    logger.info("=" * 80)
    logger.info("Starting Social Media Manager Scheduler")
    logger.info("=" * 80)

    scheduler = create_scheduler()

    # Print scheduled jobs
    logger.info("Scheduled Jobs:")
    for job in scheduler.get_jobs():
        logger.info(f"  - {job.name} (ID: {job.id})")
        logger.info(f"    Trigger: {job.trigger}")

        # Get next run time (compute from trigger if not available)
        try:
            next_run = job.next_run_time or scheduler.get_job(job.id).next_run_time
            if next_run:
                logger.info(f"    Next run: {next_run}")
        except (AttributeError, TypeError):
            # If next_run_time not available, compute from trigger
            try:
                next_run = job.trigger.get_next_fire_time(None, datetime.now())
                if next_run:
                    logger.info(f"    Next run: {next_run}")
            except Exception:
                pass

    logger.info("=" * 80)
    logger.info("Scheduler started. Press Ctrl+C to exit.")
    logger.info("=" * 80)

    scheduler.start()
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Scheduler crashed with error: {e}", exc_info=True)
    finally:
        scheduler.shutdown()
        logger.info("Scheduler shutdown complete")


if __name__ == "__main__":
    main()
