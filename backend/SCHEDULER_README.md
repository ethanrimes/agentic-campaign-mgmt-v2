# Scheduler Documentation

Centralized automated scheduler for the Social Media Manager content pipeline.

## Overview

The scheduler (`backend/scheduler.py`) automates all content pipeline operations:

- **Content Seed Creation**: Ingesting news events, discovering trends, generating creative ideas
- **Analysis & Planning**: Analyzing post performance, planning content, creating posts
- **Publishing**: Publishing content to Facebook and Instagram

## Quick Start

### Prerequisites

Ensure APScheduler is installed:

```bash
pip install apscheduler
```

### Running the Scheduler

```bash
# From project root
python -m backend.scheduler
```

Or make it executable:

```bash
chmod +x backend/scheduler.py
./backend/scheduler.py
```

### Running in Background (Production)

Using `nohup`:

```bash
nohup python -m backend.scheduler > scheduler.log 2>&1 &
```

Using `systemd` (recommended for production):

```bash
# Create service file at /etc/systemd/system/social-media-scheduler.service
sudo systemctl enable social-media-scheduler
sudo systemctl start social-media-scheduler
sudo systemctl status social-media-scheduler
```

## Default Schedule

| Job | Frequency | Description |
|-----|-----------|-------------|
| **News Pipeline** | Every 3 hours | Ingest news + deduplicate |
| **Trend Discovery** | Every 3 hours | Discover trending content |
| **Ungrounded Ideas** | Every 6 hours | Generate creative ideas |
| **Planning Pipeline** | Daily at 2 AM | Insights + Planner + Content Creation |
| **Facebook Publishing** | Every 2 hours | Publish to Facebook |
| **Instagram Publishing** | Every 2 hours | Publish to Instagram (offset by 1hr) |

## Architecture

### Job Pipelines

The scheduler uses **pipeline jobs** that chain multiple commands together:

#### News Pipeline
1. Ingest news events from Perplexity
2. Deduplicate events (runs immediately after ingestion)

#### Planning Pipeline
1. Analyze insights from published posts
2. Run planner to create content tasks
3. Create content for all tasks (runs immediately after planner)

This ensures dependent jobs run in sequence without needing to schedule them separately.

### Job Configuration

Each job is configured with:

- **`max_instances=1`**: Prevents overlapping executions
- **`coalesce=True`**: If a job is missed (e.g., server downtime), only run once when back online
- **Error handling**: Failed jobs are logged but don't stop the scheduler

## Modifying the Schedule

### Changing Intervals

Edit the `create_scheduler()` function in `backend/scheduler.py`:

#### Interval-based Jobs

```python
# Change from every 3 hours to every 4 hours
scheduler.add_job(
    run_news_pipeline,
    'interval',
    hours=4,  # Changed from 3 to 4
    id='news_pipeline',
    name='News Ingestion Pipeline',
    max_instances=1,
    coalesce=True
)
```

Available interval options:
- `weeks`, `days`, `hours`, `minutes`, `seconds`
- Example: `days=1, hours=12` = every 36 hours

#### Cron-based Jobs

```python
# Run daily at 2 AM
scheduler.add_job(
    run_planning_pipeline,
    'cron',
    hour=2,
    minute=0,
    id='planning_pipeline',
    max_instances=1
)

# Run every Monday at 9 AM
scheduler.add_job(
    run_some_job,
    'cron',
    day_of_week='mon',
    hour=9,
    minute=0
)

# Run twice daily (8 AM and 8 PM)
scheduler.add_job(
    run_some_job,
    'cron',
    hour='8,20',
    minute=0
)
```

Cron options:
- `year`, `month`, `day`, `week`, `day_of_week`, `hour`, `minute`, `second`
- Supports ranges: `hour='9-17'` (9 AM to 5 PM)
- Supports intervals: `hour='*/4'` (every 4 hours)

### Offsetting Jobs

To avoid all jobs running at once, use offsets:

```python
# Job 1: Starts immediately
scheduler.add_job(func1, 'interval', hours=2)

# Job 2: Starts 1 hour later
scheduler.add_job(func2, 'interval', hours=2, minutes=60)

# Job 3: Starts 30 minutes later
scheduler.add_job(func3, 'interval', hours=2, minutes=30)
```

### Running Jobs Immediately on Startup

```python
from datetime import datetime

scheduler.add_job(
    run_news_pipeline,
    'interval',
    hours=3,
    next_run_time=datetime.now()  # Run immediately when scheduler starts
)
```

### Disabling a Job

Comment out the `add_job()` call:

```python
# scheduler.add_job(
#     run_facebook_publishing,
#     'interval',
#     hours=2,
#     id='facebook_publishing',
#     name='Facebook Publishing'
# )
```

## Modifying Job Behavior

### Changing Command Arguments

Edit the function that calls `run_command()`:

```python
def run_news_ingestion():
    """Ingest news events from Perplexity Sonar."""
    run_command(
        ["news-events", "ingest-perplexity",
         "--topic", "New York",  # Changed from Philadelphia
         "--count", "5"],         # Changed from 3
        "News Event Ingestion"
    )
```

### Adding a New Job

1. **Create the job function:**

```python
def run_my_new_job():
    """Description of what this job does."""
    run_command(
        ["my-command", "--arg", "value"],
        "My New Job"
    )
```

2. **Add it to the scheduler:**

```python
def create_scheduler():
    scheduler = BlockingScheduler()

    # ... existing jobs ...

    # Add your new job
    scheduler.add_job(
        run_my_new_job,
        'interval',
        hours=4,
        id='my_new_job',
        name='My New Job',
        max_instances=1,
        coalesce=True
    )

    return scheduler
```

### Creating Job Pipelines

To run multiple commands in sequence:

```python
def run_my_pipeline():
    """Run multiple commands in sequence."""
    try:
        run_command(["command1"], "Step 1")
        run_command(["command2"], "Step 2")
        run_command(["command3"], "Step 3")
    except Exception as e:
        logger.error("Pipeline failed", error=str(e))
```

## Monitoring

### View Logs

All operations are logged using the application logger:

```bash
# If running in foreground, logs appear in stdout

# If running with nohup
tail -f scheduler.log

# If using systemd
journalctl -u social-media-scheduler -f
```

### View Scheduled Jobs

The scheduler prints all jobs on startup:

```
Scheduled Jobs:
  - News Ingestion Pipeline (ID: news_pipeline)
    Trigger: interval[0:03:00:00]
    Next run: 2025-11-13 05:00:00
  - Trend Discovery (ID: trend_discovery)
    Trigger: interval[0:03:00:00]
    Next run: 2025-11-13 06:00:00
  ...
```

### Manual Job Execution

To run a job manually without waiting for the schedule:

```bash
# Run any CLI command directly
python -m backend.cli.main news-events ingest-perplexity --topic "Philadelphia" --count 3
python -m backend.cli.main planner run --max-retries 3
```

## Troubleshooting

### Job Fails Silently

Check the logs for error messages. The scheduler continues running even if individual jobs fail.

### Jobs Overlap

Increase the interval or ensure `max_instances=1` is set:

```python
scheduler.add_job(
    run_long_job,
    'interval',
    hours=2,
    max_instances=1  # Prevents overlapping executions
)
```

### Scheduler Won't Start

1. Check APScheduler is installed: `pip list | grep APScheduler`
2. Verify Python path is correct
3. Check for syntax errors in `scheduler.py`

### Job Not Running at Expected Time

- Verify timezone settings (scheduler uses system timezone by default)
- Check cron expression syntax
- Look for missed job warnings in logs

### Change Timezone

```python
from apscheduler.schedulers.blocking import BlockingScheduler
from pytz import timezone

scheduler = BlockingScheduler(timezone=timezone('US/Eastern'))
```

## Best Practices

1. **Test jobs individually** before adding to scheduler:
   ```bash
   python -m backend.cli.main news-events ingest-perplexity --topic "Philadelphia" --count 3
   ```

2. **Monitor logs regularly** to catch failures early

3. **Use pipelines** for dependent operations instead of timing separate jobs

4. **Offset jobs** to distribute load across time

5. **Set reasonable intervals** based on:
   - API rate limits
   - Content freshness requirements
   - System resources

6. **Use cron jobs** for specific times (e.g., daily at 2 AM) rather than intervals

7. **Keep max_instances=1** unless you specifically need parallel execution

## Production Deployment

### Using systemd (Linux)

Create `/etc/systemd/system/social-media-scheduler.service`:

```ini
[Unit]
Description=Social Media Manager Scheduler
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/social-media-manager-v2
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python -m backend.scheduler
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable social-media-scheduler
sudo systemctl start social-media-scheduler
sudo systemctl status social-media-scheduler
```

### Using Docker

Add to your `Dockerfile`:

```dockerfile
CMD ["python", "-m", "backend.scheduler"]
```

Or run as a separate service in `docker-compose.yml`:

```yaml
services:
  scheduler:
    build: .
    command: python -m backend.scheduler
    restart: always
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
```

### Using Screen (Simple)

```bash
screen -S scheduler
python -m backend.scheduler
# Press Ctrl+A then D to detach

# Reattach later
screen -r scheduler
```

## Support

For issues or questions:
1. Check the logs for error messages
2. Verify individual CLI commands work
3. Review APScheduler documentation: https://apscheduler.readthedocs.io/
