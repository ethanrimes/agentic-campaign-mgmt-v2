-- backend/database/migrations/016_refactor_content_seed_foreign_keys.sql
-- Refactor completed_posts to use proper foreign keys for content seeds

-- Step 1: Add three new nullable foreign key columns
ALTER TABLE completed_posts
ADD COLUMN news_event_seed_id UUID REFERENCES news_event_seeds(id) ON DELETE CASCADE,
ADD COLUMN trend_seed_id UUID REFERENCES trend_seeds(id) ON DELETE CASCADE,
ADD COLUMN ungrounded_seed_id UUID REFERENCES ungrounded_seeds(id) ON DELETE CASCADE;

-- Step 2: Migrate existing data based on content_seed_type
-- News event seeds
UPDATE completed_posts
SET news_event_seed_id = content_seed_id
WHERE content_seed_type = 'news_event';

-- Trend seeds
UPDATE completed_posts
SET trend_seed_id = content_seed_id
WHERE content_seed_type = 'trend';

-- Ungrounded seeds
UPDATE completed_posts
SET ungrounded_seed_id = content_seed_id
WHERE content_seed_type = 'ungrounded';

-- Step 3: Add constraint to ensure exactly one seed reference is set
ALTER TABLE completed_posts
ADD CONSTRAINT content_seed_exclusive_check CHECK (
    (
        (news_event_seed_id IS NOT NULL)::int +
        (trend_seed_id IS NOT NULL)::int +
        (ungrounded_seed_id IS NOT NULL)::int
    ) = 1
);

-- Step 4: Drop old columns
ALTER TABLE completed_posts
DROP COLUMN content_seed_id,
DROP COLUMN content_seed_type;

-- Step 5: Create indexes for the new foreign key columns
CREATE INDEX idx_completed_posts_news_event_seed_id ON completed_posts(news_event_seed_id)
    WHERE news_event_seed_id IS NOT NULL;
CREATE INDEX idx_completed_posts_trend_seed_id ON completed_posts(trend_seed_id)
    WHERE trend_seed_id IS NOT NULL;
CREATE INDEX idx_completed_posts_ungrounded_seed_id ON completed_posts(ungrounded_seed_id)
    WHERE ungrounded_seed_id IS NOT NULL;

COMMENT ON COLUMN completed_posts.news_event_seed_id IS 'Foreign key to news_event_seeds table (mutually exclusive with other seed types)';
COMMENT ON COLUMN completed_posts.trend_seed_id IS 'Foreign key to trend_seeds table (mutually exclusive with other seed types)';
COMMENT ON COLUMN completed_posts.ungrounded_seed_id IS 'Foreign key to ungrounded_seeds table (mutually exclusive with other seed types)';
