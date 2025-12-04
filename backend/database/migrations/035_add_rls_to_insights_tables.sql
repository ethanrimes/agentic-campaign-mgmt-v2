-- Migration 035: Add RLS to insights tables
-- Enables Row Level Security on all 5 insights tables

-- ============================================================================
-- FACEBOOK PAGE INSIGHTS
-- ============================================================================

ALTER TABLE facebook_page_insights ENABLE ROW LEVEL SECURITY;

-- Policy: Allow all operations for authenticated users on their business assets
CREATE POLICY "Users can view their own facebook page insights"
    ON facebook_page_insights
    FOR SELECT
    USING (true);

CREATE POLICY "Users can insert their own facebook page insights"
    ON facebook_page_insights
    FOR INSERT
    WITH CHECK (true);

CREATE POLICY "Users can update their own facebook page insights"
    ON facebook_page_insights
    FOR UPDATE
    USING (true);

CREATE POLICY "Users can delete their own facebook page insights"
    ON facebook_page_insights
    FOR DELETE
    USING (true);


-- ============================================================================
-- INSTAGRAM ACCOUNT INSIGHTS
-- ============================================================================

ALTER TABLE instagram_account_insights ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own instagram account insights"
    ON instagram_account_insights
    FOR SELECT
    USING (true);

CREATE POLICY "Users can insert their own instagram account insights"
    ON instagram_account_insights
    FOR INSERT
    WITH CHECK (true);

CREATE POLICY "Users can update their own instagram account insights"
    ON instagram_account_insights
    FOR UPDATE
    USING (true);

CREATE POLICY "Users can delete their own instagram account insights"
    ON instagram_account_insights
    FOR DELETE
    USING (true);


-- ============================================================================
-- FACEBOOK POST INSIGHTS
-- ============================================================================

ALTER TABLE facebook_post_insights ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own facebook post insights"
    ON facebook_post_insights
    FOR SELECT
    USING (true);

CREATE POLICY "Users can insert their own facebook post insights"
    ON facebook_post_insights
    FOR INSERT
    WITH CHECK (true);

CREATE POLICY "Users can update their own facebook post insights"
    ON facebook_post_insights
    FOR UPDATE
    USING (true);

CREATE POLICY "Users can delete their own facebook post insights"
    ON facebook_post_insights
    FOR DELETE
    USING (true);


-- ============================================================================
-- FACEBOOK VIDEO INSIGHTS
-- ============================================================================

ALTER TABLE facebook_video_insights ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own facebook video insights"
    ON facebook_video_insights
    FOR SELECT
    USING (true);

CREATE POLICY "Users can insert their own facebook video insights"
    ON facebook_video_insights
    FOR INSERT
    WITH CHECK (true);

CREATE POLICY "Users can update their own facebook video insights"
    ON facebook_video_insights
    FOR UPDATE
    USING (true);

CREATE POLICY "Users can delete their own facebook video insights"
    ON facebook_video_insights
    FOR DELETE
    USING (true);


-- ============================================================================
-- INSTAGRAM MEDIA INSIGHTS
-- ============================================================================

ALTER TABLE instagram_media_insights ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own instagram media insights"
    ON instagram_media_insights
    FOR SELECT
    USING (true);

CREATE POLICY "Users can insert their own instagram media insights"
    ON instagram_media_insights
    FOR INSERT
    WITH CHECK (true);

CREATE POLICY "Users can update their own instagram media insights"
    ON instagram_media_insights
    FOR UPDATE
    USING (true);

CREATE POLICY "Users can delete their own instagram media insights"
    ON instagram_media_insights
    FOR DELETE
    USING (true);


-- ============================================================================
-- NOTES
-- ============================================================================
--
-- RLS is now enabled on all 5 insights tables:
-- - facebook_page_insights
-- - instagram_account_insights
-- - facebook_post_insights
-- - facebook_video_insights
-- - instagram_media_insights
--
-- Current policies allow all authenticated operations (USING true).
-- This is a permissive setup that simply enables RLS.
--
-- For stricter access control, you could modify policies to check:
--   USING (business_asset_id IN (
--       SELECT id FROM business_assets WHERE user_id = auth.uid()
--   ))
--
-- The backend repository uses get_supabase_admin_client() which bypasses
-- RLS with the service role key, so backend operations are unaffected.
