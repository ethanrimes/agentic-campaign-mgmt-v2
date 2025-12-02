# CLI Commands Reference

All CLI commands require `--business-asset-id` to specify which business asset to operate on.

```bash
# Base command
python -m backend.cli.main <command> <subcommand> [options]
```

---

## News Events

Ingest and manage news event seeds for content creation.

```bash
# Ingest news via Perplexity Sonar
python -m backend.cli.main news-events ingest-perplexity --business-asset-id penndailybuzz --topic "Philadelphia" --count 5

# Ingest without topic (uses target audience)
python -m backend.cli.main news-events ingest-perplexity --business-asset-id penndailybuzz --count 3

# Ingest via ChatGPT Deep Research
python -m backend.cli.main news-events ingest-deep-research --business-asset-id penndailybuzz --query "UPenn campus events" --count 5

# Ingest deep research without query (uses target audience)
python -m backend.cli.main news-events ingest-deep-research --business-asset-id penndailybuzz --count 3

# Deduplicate ingested events
python -m backend.cli.main news-events deduplicate --business-asset-id penndailybuzz

# List recent news event seeds
python -m backend.cli.main news-events list --business-asset-id penndailybuzz --limit 10
```

---

## Trends

Discover and manage trend seeds from social media.

```bash
# Discover trends with specific query
python -m backend.cli.main trends discover --business-asset-id penndailybuzz --query "UPenn students" --count 2

# Discover trends without query (uses target audience)
python -m backend.cli.main trends discover --business-asset-id penndailybuzz --count 2

# List recent trend seeds
python -m backend.cli.main trends list --business-asset-id penndailybuzz --limit 10
```

---

## Ungrounded (Creative Ideas)

Generate creative content ideas not tied to specific news or trends.

```bash
# Generate creative content ideas
python -m backend.cli.main ungrounded generate --business-asset-id penndailybuzz --count 5

# List recent ungrounded seeds
python -m backend.cli.main ungrounded list --business-asset-id penndailybuzz --limit 10
```

---

## Insights

Analyze content performance and generate insight reports.

```bash
# Run insights analysis
python -m backend.cli.main insights analyze --business-asset-id penndailybuzz --days 14

# List recent insight reports
python -m backend.cli.main insights list --business-asset-id penndailybuzz --limit 5

# Show the latest insight report
python -m backend.cli.main insights latest --business-asset-id penndailybuzz
```

---

## Planner

Run the content planning agent to create weekly content plans.

```bash
# Run planner to create content plan
python -m backend.cli.main planner run --business-asset-id oceankindnesscollective --max-retries 3
```

---

## Content Creation

Create content from pending tasks. Supports unified format where each image/video post creates both an Instagram and Facebook post.

### Media Sharing Options

- `--share-media`: Reuse the same media across Instagram and Facebook (default). Creates a verification group where only the Instagram post is verified, and Facebook inherits the result.
- `--no-share-media`: Generate separate media for each platform. Both posts are verified independently.

```bash
# Create content for all pending tasks (default: shares media across platforms)
python -m backend.cli.main content create-all --business-asset-id penndailybuzz

# Create content with explicit media sharing (reduces verification work)
python -m backend.cli.main content create-all --business-asset-id oceankindnesscollective --share-media

# Create content with separate media for each platform (both verified independently)
python -m backend.cli.main content create-all --business-asset-id penndailybuzz --no-share-media

# Create content for all pending tasks (skip verification)
python -m backend.cli.main content create-all --business-asset-id penndailybuzz --skip-verify

# Create content for a specific task
python -m backend.cli.main content create --business-asset-id penndailybuzz --task-id <task-uuid>

# Create content for a specific task with media sharing options
python -m backend.cli.main content create --business-asset-id penndailybuzz --task-id <task-uuid> --share-media
python -m backend.cli.main content create --business-asset-id penndailybuzz --task-id <task-uuid> --no-share-media

# Create content for a specific task (skip verification)
python -m backend.cli.main content create --business-asset-id penndailybuzz --task-id <task-uuid> --skip-verify

# List pending content creation tasks
python -m backend.cli.main content pending --business-asset-id penndailybuzz --limit 10
```

---

## Verifier

Verify content before publishing.

### Verification Groups

When content is created with `--share-media` (the default), Instagram and Facebook posts share a **verification group**. Only the primary post (Instagram) is verified, and the secondary post (Facebook) automatically inherits the result. This reduces verification work by 50% when sharing media.

```bash
# Verify a specific post
python -m backend.cli.main verifier verify --business-asset-id penndailybuzz --post-id <post-uuid>

# Verify all unverified pending posts (only verifies primary posts in groups)
python -m backend.cli.main verifier verify-all --business-asset-id penndailybuzz

# Show verification statistics
python -m backend.cli.main verifier stats --business-asset-id penndailybuzz

# List recently rejected posts
python -m backend.cli.main verifier rejected --business-asset-id penndailybuzz --limit 10

# List unverified pending posts
python -m backend.cli.main verifier unverified --business-asset-id penndailybuzz --limit 20
```

---

## Publishing

Publish scheduled content to social platforms.

```bash
# Publish scheduled Facebook posts
python -m backend.cli.main publish facebook --business-asset-id eaglesnationfanhuddle --limit 2

# Publish scheduled Instagram posts
python -m backend.cli.main publish instagram --business-asset-id eaglesnationfanhuddle --limit 10

# Publish all scheduled posts (all platforms)
python -m backend.cli.main publish all --business-asset-id penndailybuzz --limit 10
```

---

## Comments

Manage and respond to comments on published posts.

```bash
# Check for new Instagram comments
python -m backend.cli.main comments check-instagram --business-asset-id penndailybuzz --max-media 20

# Process and respond to pending comments (all platforms)
python -m backend.cli.main comments respond --business-asset-id penndailybuzz --platform all --limit 10

# Process and respond to Facebook comments only
python -m backend.cli.main comments respond --business-asset-id penndailybuzz --platform facebook --limit 10

# Process and respond to Instagram comments only
python -m backend.cli.main comments respond --business-asset-id penndailybuzz --platform instagram --limit 10

# Test comment responder on a specific comment (dry run)
python -m backend.cli.main comments test-responder --business-asset-id penndailybuzz <comment-id> --platform instagram
```

---

## Full Pipeline Example

Run the complete content pipeline:

```bash
# 1. Gather content seeds
python -m backend.cli.main news-events ingest-perplexity --business-asset-id penndailybuzz --count 5
python -m backend.cli.main news-events deduplicate --business-asset-id penndailybuzz
python -m backend.cli.main trends discover --business-asset-id penndailybuzz --count 3
python -m backend.cli.main ungrounded generate --business-asset-id penndailybuzz --count 3

# 2. Analyze past performance
python -m backend.cli.main insights analyze --business-asset-id penndailybuzz --days 14

# 3. Create content plan
python -m backend.cli.main planner run --business-asset-id penndailybuzz --max-retries 3

# 4. Generate content
python -m backend.cli.main content create-all --business-asset-id penndailybuzz

# 5. Verify content (if not auto-verified)
python -m backend.cli.main verifier verify-all --business-asset-id penndailybuzz

# 6. Publish content
python -m backend.cli.main publish all --business-asset-id penndailybuzz

# 7. Monitor and respond to comments
python -m backend.cli.main comments check-instagram --business-asset-id penndailybuzz
python -m backend.cli.main comments respond --business-asset-id penndailybuzz
```
