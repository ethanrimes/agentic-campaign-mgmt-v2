-- backend/database/migrations/013_change_media_urls_to_media_ids.sql
-- Change completed_posts to reference media table via foreign keys instead of storing URLs

-- Add new media_ids column as UUID array
ALTER TABLE completed_posts
ADD COLUMN media_ids UUID[] DEFAULT ARRAY[]::UUID[];

-- Drop old media_urls column
ALTER TABLE completed_posts
DROP COLUMN media_urls;

-- Add index for media_ids array (for faster lookups)
CREATE INDEX idx_completed_posts_media_ids ON completed_posts USING GIN(media_ids);

COMMENT ON COLUMN completed_posts.media_ids IS 'Array of UUIDs referencing media table';

-- Note: We're using UUID[] array instead of a junction table for simplicity
-- Each media_id should reference a row in the media table
-- To query posts with their media, use:
--   SELECT cp.*, array_agg(m.*) as media
--   FROM completed_posts cp
--   LEFT JOIN media m ON m.id = ANY(cp.media_ids)
--   GROUP BY cp.id
