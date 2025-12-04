-- Migration 034: Fix unique constraints for insights tables
-- The original migration used unique indexes, but ON CONFLICT requires actual unique constraints

-- ============================================================================
-- FACEBOOK PAGE INSIGHTS - Fix unique constraint
-- ============================================================================

-- Drop the existing unique index
DROP INDEX IF EXISTS idx_fb_page_insights_business_asset;

-- Add proper unique constraint (using business_asset_id only since one page per asset)
ALTER TABLE facebook_page_insights
    DROP CONSTRAINT IF EXISTS fb_page_insights_business_asset_unique;

ALTER TABLE facebook_page_insights
    ADD CONSTRAINT fb_page_insights_business_asset_unique
    UNIQUE (business_asset_id);


-- ============================================================================
-- INSTAGRAM ACCOUNT INSIGHTS - Fix unique constraint
-- ============================================================================

-- Drop the existing unique index
DROP INDEX IF EXISTS idx_ig_account_insights_business_asset;

-- Add proper unique constraint (using business_asset_id only since one account per asset)
ALTER TABLE instagram_account_insights
    DROP CONSTRAINT IF EXISTS ig_account_insights_business_asset_unique;

ALTER TABLE instagram_account_insights
    ADD CONSTRAINT ig_account_insights_business_asset_unique
    UNIQUE (business_asset_id);


-- ============================================================================
-- FACEBOOK POST INSIGHTS - Fix unique constraint
-- ============================================================================

-- Drop the existing unique index
DROP INDEX IF EXISTS idx_fb_post_insights_platform_post;

-- Add proper unique constraint
ALTER TABLE facebook_post_insights
    DROP CONSTRAINT IF EXISTS fb_post_insights_platform_post_unique;

ALTER TABLE facebook_post_insights
    ADD CONSTRAINT fb_post_insights_platform_post_unique
    UNIQUE (business_asset_id, platform_post_id);


-- ============================================================================
-- FACEBOOK VIDEO INSIGHTS - Fix unique constraint
-- ============================================================================

-- Drop the existing unique index
DROP INDEX IF EXISTS idx_fb_video_insights_platform_video;

-- Add proper unique constraint
ALTER TABLE facebook_video_insights
    DROP CONSTRAINT IF EXISTS fb_video_insights_platform_video_unique;

ALTER TABLE facebook_video_insights
    ADD CONSTRAINT fb_video_insights_platform_video_unique
    UNIQUE (business_asset_id, platform_video_id);


-- ============================================================================
-- INSTAGRAM MEDIA INSIGHTS - Fix unique constraint
-- ============================================================================

-- Drop the existing unique index
DROP INDEX IF EXISTS idx_ig_media_insights_platform_media;

-- Add proper unique constraint
ALTER TABLE instagram_media_insights
    DROP CONSTRAINT IF EXISTS ig_media_insights_platform_media_unique;

ALTER TABLE instagram_media_insights
    ADD CONSTRAINT ig_media_insights_platform_media_unique
    UNIQUE (business_asset_id, platform_media_id);
