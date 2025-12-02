-- Migration: Unified content formats for cross-platform media sharing
-- This migration transitions from platform-specific planning to format-based planning

-- Add new unified format columns to content_creation_tasks
ALTER TABLE content_creation_tasks
ADD COLUMN IF NOT EXISTS image_posts INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS video_posts INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS text_only_posts INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS scheduled_times JSONB DEFAULT '[]'::jsonb;

-- Make old platform-specific columns nullable (for backwards compatibility)
-- These columns will be deprecated but kept for existing tasks
ALTER TABLE content_creation_tasks
ALTER COLUMN instagram_image_posts DROP NOT NULL,
ALTER COLUMN instagram_reel_posts DROP NOT NULL,
ALTER COLUMN facebook_feed_posts DROP NOT NULL,
ALTER COLUMN facebook_video_posts DROP NOT NULL,
ALTER COLUMN image_budget DROP NOT NULL,
ALTER COLUMN video_budget DROP NOT NULL;

-- Set defaults for old columns to NULL for new tasks
ALTER TABLE content_creation_tasks
ALTER COLUMN instagram_image_posts SET DEFAULT NULL,
ALTER COLUMN instagram_reel_posts SET DEFAULT NULL,
ALTER COLUMN facebook_feed_posts SET DEFAULT NULL,
ALTER COLUMN facebook_video_posts SET DEFAULT NULL;

-- Add comment explaining the transition
COMMENT ON COLUMN content_creation_tasks.image_posts IS 'Unified format: each creates 1 IG image + 1 FB feed post';
COMMENT ON COLUMN content_creation_tasks.video_posts IS 'Unified format: each creates 1 IG reel + 1 FB video post';
COMMENT ON COLUMN content_creation_tasks.text_only_posts IS 'Facebook-only text posts (no media)';
COMMENT ON COLUMN content_creation_tasks.scheduled_times IS 'JSON array of ISO datetime strings for each post';

-- Deprecated columns (kept for backwards compatibility)
COMMENT ON COLUMN content_creation_tasks.instagram_image_posts IS 'DEPRECATED: Use image_posts instead';
COMMENT ON COLUMN content_creation_tasks.instagram_reel_posts IS 'DEPRECATED: Use video_posts instead';
COMMENT ON COLUMN content_creation_tasks.facebook_feed_posts IS 'DEPRECATED: Use image_posts instead';
COMMENT ON COLUMN content_creation_tasks.facebook_video_posts IS 'DEPRECATED: Use video_posts instead';
