-- Migration 040: Add reach column to instagram_media_insights
-- The reach metric is available from the Instagram API and measures unique accounts
-- that have seen the media. Impressions is deprecated for media created after July 2024.

-- Add reach column to instagram_media_insights
ALTER TABLE instagram_media_insights
ADD COLUMN IF NOT EXISTS reach INTEGER DEFAULT 0;

-- Add comment explaining the metric
COMMENT ON COLUMN instagram_media_insights.reach IS 'Unique accounts that have seen this media (estimated). Fetched from GET /{media_id}/insights?metric=reach';

-- Note: We are NOT adding an impressions column because:
-- 1. The impressions metric is deprecated for media created after July 2, 2024 (API v22.0+)
-- 2. Instagram API returns error: "The Media Insights API does not support the impressions metric for this media product type"
-- 3. Use reach or views as alternatives
