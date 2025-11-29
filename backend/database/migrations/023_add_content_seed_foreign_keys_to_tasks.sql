-- backend/database/migrations/023_add_content_seed_foreign_keys_to_tasks.sql
-- Add proper foreign key constraints to content_creation_tasks to prevent orphaned tasks

-- Step 1: Clean up any existing orphaned tasks (tasks referencing deleted seeds)
-- Mark them as failed so they don't cause issues
UPDATE content_creation_tasks AS t
SET status = 'failed',
    error_message = 'Content seed was deleted before task could be processed'
WHERE t.status = 'pending'
  AND t.content_seed_type = 'news_event'
  AND NOT EXISTS (
      SELECT 1 FROM news_event_seeds n
      WHERE n.id = t.content_seed_id
        AND n.business_asset_id = t.business_asset_id
  );

UPDATE content_creation_tasks AS t
SET status = 'failed',
    error_message = 'Content seed was deleted before task could be processed'
WHERE t.status = 'pending'
  AND t.content_seed_type = 'trend'
  AND NOT EXISTS (
      SELECT 1 FROM trend_seeds ts
      WHERE ts.id = t.content_seed_id
        AND ts.business_asset_id = t.business_asset_id
  );

UPDATE content_creation_tasks AS t
SET status = 'failed',
    error_message = 'Content seed was deleted before task could be processed'
WHERE t.status = 'pending'
  AND t.content_seed_type = 'ungrounded'
  AND NOT EXISTS (
      SELECT 1 FROM ungrounded_seeds u
      WHERE u.id = t.content_seed_id
        AND u.business_asset_id = t.business_asset_id
  );

-- Step 2: Split content_seed_id into three separate nullable foreign key columns
-- Add new columns
ALTER TABLE content_creation_tasks
ADD COLUMN news_event_seed_id UUID REFERENCES news_event_seeds(id) ON DELETE RESTRICT,
ADD COLUMN trend_seed_id UUID REFERENCES trend_seeds(id) ON DELETE RESTRICT,
ADD COLUMN ungrounded_seed_id UUID REFERENCES ungrounded_seeds(id) ON DELETE RESTRICT;

-- Step 3: Migrate existing data to the new columns (only for tasks with valid seeds)
-- For news_event seeds
UPDATE content_creation_tasks AS t
SET news_event_seed_id = t.content_seed_id
WHERE t.content_seed_type = 'news_event'
  AND EXISTS (
      SELECT 1 FROM news_event_seeds n
      WHERE n.id = t.content_seed_id
        AND n.business_asset_id = t.business_asset_id
  );

-- For trend seeds
UPDATE content_creation_tasks AS t
SET trend_seed_id = t.content_seed_id
WHERE t.content_seed_type = 'trend'
  AND EXISTS (
      SELECT 1 FROM trend_seeds ts
      WHERE ts.id = t.content_seed_id
        AND ts.business_asset_id = t.business_asset_id
  );

-- For ungrounded seeds
UPDATE content_creation_tasks AS t
SET ungrounded_seed_id = t.content_seed_id
WHERE t.content_seed_type = 'ungrounded'
  AND EXISTS (
      SELECT 1 FROM ungrounded_seeds u
      WHERE u.id = t.content_seed_id
        AND u.business_asset_id = t.business_asset_id
  );

-- Step 4: Add constraint to ensure exactly one seed reference is set (for non-failed tasks)
ALTER TABLE content_creation_tasks
ADD CONSTRAINT task_content_seed_exclusive_check CHECK (
    -- Failed tasks can have NULL seed references (if orphaned)
    status = 'failed' OR
    (
        (news_event_seed_id IS NOT NULL)::int +
        (trend_seed_id IS NOT NULL)::int +
        (ungrounded_seed_id IS NOT NULL)::int
    ) = 1
);

-- Step 5: Create indexes for the new foreign key columns
CREATE INDEX idx_content_creation_tasks_news_event_seed_id ON content_creation_tasks(news_event_seed_id)
    WHERE news_event_seed_id IS NOT NULL;
CREATE INDEX idx_content_creation_tasks_trend_seed_id ON content_creation_tasks(trend_seed_id)
    WHERE trend_seed_id IS NOT NULL;
CREATE INDEX idx_content_creation_tasks_ungrounded_seed_id ON content_creation_tasks(ungrounded_seed_id)
    WHERE ungrounded_seed_id IS NOT NULL;

-- Step 6: Drop old columns
ALTER TABLE content_creation_tasks
DROP COLUMN content_seed_id,
DROP COLUMN content_seed_type;

-- Step 7: Drop the old enum type since it's no longer used
DROP TYPE IF EXISTS seed_type;

-- Add comments
COMMENT ON COLUMN content_creation_tasks.news_event_seed_id IS 'Foreign key to news_event_seeds table with DELETE RESTRICT (mutually exclusive)';
COMMENT ON COLUMN content_creation_tasks.trend_seed_id IS 'Foreign key to trend_seeds table with DELETE RESTRICT (mutually exclusive)';
COMMENT ON COLUMN content_creation_tasks.ungrounded_seed_id IS 'Foreign key to ungrounded_seeds table with DELETE RESTRICT (mutually exclusive)';
