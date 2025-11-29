# Schema Migration Summary: Foreign Key Enforcement for Content Seeds

## Problem
Content seeds (news_event_seeds, trend_seeds, ungrounded_seeds) could be deleted while tasks and posts still referenced them, causing foreign key constraint violations when trying to create new posts.

## Root Cause
1. `content_creation_tasks` table had no foreign key constraints - just stored a UUID and type string
2. `completed_posts` table had proper foreign keys with `ON DELETE CASCADE`, but this meant posts were silently deleted when seeds were deleted
3. No protection against deleting seeds that had associated pending tasks

## Solution

### 1. Database Schema Changes

#### Migration 023: Add Foreign Keys to `content_creation_tasks`

**File**: `backend/database/migrations/023_add_content_seed_foreign_keys_to_tasks.sql`

**Changes**:
- Replaced single `content_seed_id` + `content_seed_type` columns with three separate foreign key columns:
  - `news_event_seed_id` → `news_event_seeds(id)` with `ON DELETE RESTRICT`
  - `trend_seed_id` → `trend_seeds(id)` with `ON DELETE RESTRICT`
  - `ungrounded_seed_id` → `ungrounded_seeds(id)` with `ON DELETE RESTRICT`
- Added check constraint to ensure exactly one seed reference is set (for non-failed tasks)
- Migrated existing data to new columns (only for tasks with valid seed references)
- Created indexes on new foreign key columns

**Key Feature**: `ON DELETE RESTRICT` prevents seed deletion if any tasks reference them

#### Cleanup Script: Delete Orphaned Tasks

**File**: `scripts/delete_orphaned_tasks.sql`

Removes tasks that reference non-existent seeds before applying migration 023

### 2. Code Changes

#### A. Updated `ContentCreationTask` Model

**File**: `backend/models/tasks.py`

**Changes**:
```python
# Old schema
content_seed_id: UUID
content_seed_type: Literal["news_event", "trend", "ungrounded"]

# New schema
news_event_seed_id: Optional[UUID] = None
trend_seed_id: Optional[UUID] = None
ungrounded_seed_id: Optional[UUID] = None

# Added backward-compatible properties
@property
def content_seed_id(self) -> UUID:
    """Returns the set seed ID"""

@property
def content_seed_type(self) -> Literal["news_event", "trend", "ungrounded"]:
    """Returns the seed type based on which field is set"""
```

#### B. Updated Planner Agent

**File**: `backend/agents/planner/runner.py`

**Changes**:
```python
# Old code
task = ContentCreationTask(
    business_asset_id=self.business_asset_id,
    content_seed_id=allocation["seed_id"],
    content_seed_type=allocation["seed_type"],
    ...
)

# New code
seed_kwargs = {}
if seed_type == "news_event":
    seed_kwargs["news_event_seed_id"] = seed_id
elif seed_type == "trend":
    seed_kwargs["trend_seed_id"] = seed_id
elif seed_type == "ungrounded":
    seed_kwargs["ungrounded_seed_id"] = seed_id

task = ContentCreationTask(
    business_asset_id=self.business_asset_id,
    **seed_kwargs,
    ...
)
```

**Result**: Planner now correctly sets the appropriate foreign key column when creating tasks

#### C. Updated Content Creation Agent

**File**: `backend/agents/content_creation/content_agent.py`

**Changes**:
```python
# Old code
seed_reference = {}
if task.content_seed_type == "news_event":
    seed_reference["news_event_seed_id"] = task.content_seed_id
# ... etc

completed_post = CompletedPost(
    **seed_reference,
    ...
)

# New code - Direct deterministic copy from task
completed_post = CompletedPost(
    news_event_seed_id=task.news_event_seed_id,
    trend_seed_id=task.trend_seed_id,
    ungrounded_seed_id=task.ungrounded_seed_id,
    ...
)
```

**Key Improvement**: Seed references are now **deterministically** copied from the task to the post - no logic needed, just copy the foreign key fields directly

#### D. Added Orphaned Task Detection

**File**: `backend/agents/content_creation/content_agent.py`

Added validation to check if seed exists before creating content:

```python
# Check if seed exists (handle orphaned tasks)
if not seed:
    error_msg = f"Content seed {task.content_seed_id} ({task.content_seed_type}) no longer exists"
    logger.error("Orphaned task detected", task_id=task_id, error=error_msg)
    await self.tasks_repo.update(
        self.business_asset_id,
        task_id,
        {"status": "failed", "error_message": error_msg}
    )
    raise Exception(error_msg)
```

#### E. Created Cleanup Utility

**File**: `scripts/cleanup_orphaned_tasks.py`

Utility script to find and optionally fix orphaned tasks (tasks referencing deleted seeds)

## Migration Steps

1. **Delete orphaned tasks**:
   ```bash
   psql $SUPABASE_DB_URL -f scripts/delete_orphaned_tasks.sql
   ```

2. **Apply migration 023**:
   ```bash
   psql $SUPABASE_DB_URL -f backend/database/migrations/023_add_content_seed_foreign_keys_to_tasks.sql
   ```

3. **Verify**: Run planner and content creation to ensure they work with new schema

## Benefits

1. **Data Integrity**: Database enforces referential integrity - can't delete seeds with pending tasks
2. **Deterministic Seed References**: Posts inherit seed IDs directly from tasks (no mapping logic)
3. **Clearer Schema**: Foreign key relationships are explicit in the database
4. **Better Error Messages**: Orphaned tasks are detected early and failed with clear error messages
5. **Backward Compatibility**: Properties maintain backward compatibility with old code

## Testing

Run these commands to verify the migration:

```bash
# Test planner creates tasks correctly
python -m backend.cli.main planner run --business-asset-id penndailybuzz

# Test content creation uses correct seed references
python -m backend.cli.main content create --business-asset-id penndailybuzz

# Check for orphaned tasks
python -m scripts.cleanup_orphaned_tasks penndailybuzz
```
