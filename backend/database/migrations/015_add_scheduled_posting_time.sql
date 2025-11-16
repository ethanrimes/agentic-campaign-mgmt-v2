-- backend/database/migrations/015_add_scheduled_posting_time.sql
-- Add scheduled_posting_time column to completed_posts table

-- ============================================================================
-- Add scheduled_posting_time column
-- ============================================================================

ALTER TABLE completed_posts
ADD COLUMN IF NOT EXISTS scheduled_posting_time TIMESTAMP WITH TIME ZONE;

-- ============================================================================
-- Create index for efficient queries
-- ============================================================================

-- Index for finding posts ready to publish (pending posts with scheduled time <= now)
CREATE INDEX IF NOT EXISTS idx_completed_posts_scheduled_pending
ON completed_posts(platform, scheduled_posting_time)
WHERE status = 'pending' AND scheduled_posting_time IS NOT NULL;

-- ============================================================================
-- Add comments
-- ============================================================================

COMMENT ON COLUMN completed_posts.scheduled_posting_time IS 'When this post should be published (NULL means publish immediately)';

-- ============================================================================
-- Update existing pending posts (optional - set to NULL for manual handling)
-- ============================================================================

-- All existing pending posts will have NULL scheduled_posting_time
-- This means they won't be automatically published until manually scheduled
-- You can run the schedule update script to assign times to them
