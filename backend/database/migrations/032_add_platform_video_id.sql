-- backend/database/migrations/032_add_platform_video_id.sql
-- Add platform_video_id column for storing Facebook/Instagram video IDs
-- This enables easy access to video-specific metrics via the Graph API

ALTER TABLE completed_posts
ADD COLUMN platform_video_id TEXT;

-- Create index for efficient lookups by video ID
CREATE INDEX idx_completed_posts_platform_video_id ON completed_posts(platform_video_id)
    WHERE platform_video_id IS NOT NULL;

COMMENT ON COLUMN completed_posts.platform_video_id IS 'Video ID from Facebook/Instagram API for video posts (reels, videos). Used to fetch video-specific insights via /{video-id}/video_insights';
