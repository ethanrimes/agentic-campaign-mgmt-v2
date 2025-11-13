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
    """Publish content to Facebook."""
    run_command(
        ["publish", "facebook", "--limit", "1"],
        "Facebook Publishing"
    )


def run_instagram_publishing():
    """Publish content to Instagram."""
    run_command(
        ["publish", "instagram", "--limit", "1"],
        "Instagram Publishing"
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
    # CONTENT SEED CREATION (every 3-6 hours)
    # ========================================================================

    # News ingestion + deduplication pipeline - every 3 hours
    scheduler.add_job(
        run_news_pipeline,
        'interval',
        hours=3,
        id='news_pipeline',
        name='News Ingestion Pipeline',
        max_instances=1,
        coalesce=True,
        next_run_time=datetime.now()  # Run immediately on startup
    )

    # Trend discovery - every 3 hours (offset by 1 hour)
    scheduler.add_job(
        run_trend_discovery,
        'interval',
        hours=3,
        id='trend_discovery',
        name='Trend Discovery',
        max_instances=1,
        coalesce=True
    )

    # Ungrounded generation - every 6 hours
    scheduler.add_job(
        run_ungrounded_generation,
        'interval',
        hours=6,
        id='ungrounded_generation',
        name='Ungrounded Idea Generation',
        max_instances=1,
        coalesce=True
    )

    # ========================================================================
    # ANALYSIS & PLANNING (daily at 2 AM)
    # ========================================================================

    # Planning pipeline (insights + planner + content creation) - daily at 2 AM
    scheduler.add_job(
        run_planning_pipeline,
        'cron',
        hour=2,
        minute=0,
        id='planning_pipeline',
        name='Planning Pipeline (Insights + Planner + Content Creation)',
        max_instances=1,
        coalesce=True
    )

    # ========================================================================
    # PUBLISHING (every 2 hours)
    # ========================================================================

    # Facebook publishing - every 2 hours
    scheduler.add_job(
        run_facebook_publishing,
        'interval',
        hours=2,
        id='facebook_publishing',
        name='Facebook Publishing',
        max_instances=1,
        coalesce=True
    )

    # Instagram publishing - every 2 hours (offset by 1 hour)
    scheduler.add_job(
        run_instagram_publishing,
        'interval',
        hours=2,
        id='instagram_publishing',
        name='Instagram Publishing',
        max_instances=1,
        coalesce=True,
        # Start 1 hour after scheduler starts to alternate with Facebook
        minutes=60
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
