#!/usr/bin/env python3
# backend/scheduler.py

"""
Centralized scheduler for automated content pipeline.

This scheduler orchestrates all automated tasks including:
- Content seed creation (news, trends, ungrounded ideas)
- Analysis and planning
- Content creation
- Publishing to social media platforms

See SCHEDULER_README.md for usage instructions.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import subprocess
import sys
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from backend.utils import get_logger

logger = get_logger(__name__)

# Base command for all CLI operations
BASE_CMD = [sys.executable, "-m", "backend.cli.main"]


# ============================================================================
# SCHEDULING CONFIGURATION
# ============================================================================

class SchedulingConfig:
    """
    Configuration for post scheduling.

    Defines when and how often posts should be published to each platform.
    All times are in hours unless otherwise specified.
    """

    # Publishing frequency (hours between posts)
    FACEBOOK_POST_INTERVAL_HOURS = 12  # Post to Facebook once per day
    INSTAGRAM_POST_INTERVAL_HOURS = 8  # Post to Instagram twice per day

    # Initial delay before first post (hours from content creation)
    FACEBOOK_INITIAL_DELAY_HOURS = 2  # Wait 2 hours before first Facebook post
    INSTAGRAM_INITIAL_DELAY_HOURS = 1  # Wait 1 hour before first Instagram post

    # Publishing check frequency (minutes)
    # How often the publisher scripts should check for posts to publish
    PUBLISH_CHECK_INTERVAL_MINUTES = 5

    # Comment management (minutes)
    INSTAGRAM_COMMENT_CHECK_INTERVAL_MINUTES = 180  # Check for new Instagram comments
    COMMENT_RESPONDER_INTERVAL_MINUTES = 5  # Process and respond to pending comments

    # Content pipeline scheduling (hours)
    NEWS_PIPELINE_INTERVAL_HOURS = 6  # News ingestion + deduplication
    TREND_DISCOVERY_INTERVAL_HOURS = 6  # Trend discovery
    UNGROUNDED_GENERATION_INTERVAL_HOURS = 12  # Ungrounded idea generation

    # Analysis and planning (cron)
    PLANNING_PIPELINE_HOUR = 2  # Daily at 2 AM


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
    """Ingest news events from Perplexity Sonar."""
    run_command(
        ["news-events", "ingest-perplexity", "--topic", "Philadelphia", "--count", "3"],
        "News Event Ingestion"
    )


def run_news_deduplication():
    """Deduplicate news events after ingestion."""
    run_command(
        ["news-events", "deduplicate"],
        "News Event Deduplication"
    )


def run_news_pipeline():
    """Run complete news ingestion pipeline (ingest + deduplicate)."""
    try:
        run_news_ingestion()
        run_news_deduplication()
    except Exception as e:
        logger.error("News pipeline failed", error=str(e))


def run_trend_discovery():
    """Discover trending content on social media."""
    run_command(
        ["trends", "discover", "--query", "UPenn students", "--count", "2"],
        "Trend Discovery"
    )


def run_ungrounded_generation():
    """Generate creative ungrounded content ideas."""
    run_command(
        ["ungrounded", "generate", "--count", "3"],
        "Ungrounded Idea Generation"
    )


# ============================================================================
# ANALYSIS & PLANNING JOBS
# ============================================================================

def run_insights_analysis():
    """Analyze published content performance."""
    run_command(
        ["insights", "analyze", "--days", "30"],
        "Insights Analysis"
    )


def run_planner():
    """Run content planning to create tasks from seeds."""
    run_command(
        ["planner", "run", "--max-retries", "3"],
        "Content Planning"
    )


def run_content_creation():
    """Create content for all pending tasks."""
    run_command(
        ["content", "create-all"],
        "Content Creation"
    )


def run_planning_pipeline():
    """Run complete planning pipeline (insights + planner + content creation)."""
    try:
        run_insights_analysis()
        run_planner()
        run_content_creation()
    except Exception as e:
        logger.error("Planning pipeline failed", error=str(e))


# ============================================================================
# PUBLISHING JOBS
# ============================================================================

def run_facebook_publishing():
    """Check for and publish scheduled Facebook posts."""
    run_command(
        ["publish", "facebook"],
        "Facebook Publishing"
    )


def run_instagram_publishing():
    """Check for and publish scheduled Instagram posts."""
    run_command(
        ["publish", "instagram"],
        "Instagram Publishing"
    )


# ============================================================================
# COMMENT MANAGEMENT JOBS
# ============================================================================

def run_instagram_comment_check():
    """Check for new comments on Instagram posts."""
    run_command(
        ["comments", "check-instagram"],
        "Instagram Comment Check"
    )


def run_comment_responder():
    """Process pending comments and generate responses."""
    run_command(
        ["comments", "respond"],
        "Comment Responder"
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
    scheduler = BlockingScheduler()

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
        coalesce=True
    )

    # Ungrounded generation
    scheduler.add_job(
        run_ungrounded_generation,
        'interval',
        hours=SCHEDULING_CONFIG.UNGROUNDED_GENERATION_INTERVAL_HOURS,
        id='ungrounded_generation',
        name='Ungrounded Idea Generation',
        max_instances=1,
        coalesce=True
    )

    # ========================================================================
    # ANALYSIS & PLANNING
    # ========================================================================

    # Planning pipeline (insights + planner + content creation)
    scheduler.add_job(
        run_planning_pipeline,
        'cron',
        hour=SCHEDULING_CONFIG.PLANNING_PIPELINE_HOUR,
        minute=0,
        id='planning_pipeline',
        name='Planning Pipeline (Insights + Planner + Content Creation)',
        max_instances=1,
        coalesce=True
    )

    # ========================================================================
    # PUBLISHING
    # ========================================================================

    # Facebook publishing - check for scheduled posts at configured interval
    scheduler.add_job(
        run_facebook_publishing,
        'interval',
        minutes=SCHEDULING_CONFIG.PUBLISH_CHECK_INTERVAL_MINUTES,
        id='facebook_publishing',
        name='Facebook Publishing',
        max_instances=1,
        coalesce=True
    )

    # Instagram publishing - check for scheduled posts at configured interval
    scheduler.add_job(
        run_instagram_publishing,
        'interval',
        minutes=SCHEDULING_CONFIG.PUBLISH_CHECK_INTERVAL_MINUTES,
        id='instagram_publishing',
        name='Instagram Publishing',
        max_instances=1,
        coalesce=True
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
        coalesce=True
    )

    # Comment responder - process pending comments and generate responses
    scheduler.add_job(
        run_comment_responder,
        'interval',
        minutes=SCHEDULING_CONFIG.COMMENT_RESPONDER_INTERVAL_MINUTES,
        id='comment_responder',
        name='Comment Responder',
        max_instances=1,
        coalesce=True
    )

    return scheduler


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Start the scheduler."""
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

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped by user")
        scheduler.shutdown()


if __name__ == "__main__":
    main()
