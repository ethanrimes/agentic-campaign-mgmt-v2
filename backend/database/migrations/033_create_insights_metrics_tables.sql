-- Migration 033: Create insights metrics tables for cached engagement data
-- These tables cache insights from the Meta API to avoid repeated queries

-- ============================================================================
-- FACEBOOK PAGE INSIGHTS (account-level metrics)
-- ============================================================================

CREATE TABLE IF NOT EXISTS facebook_page_insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_asset_id TEXT NOT NULL REFERENCES business_assets(id) ON DELETE CASCADE,

    -- Page metadata
    page_id TEXT NOT NULL,
    page_name TEXT,
    page_picture_url TEXT,

    -- Page-level metrics (aggregated/latest values)
    -- Views & impressions
    page_views_total INTEGER DEFAULT 0,
    page_views_total_week INTEGER DEFAULT 0,
    page_views_total_days_28 INTEGER DEFAULT 0,

    -- Actions & engagement
    page_total_actions INTEGER DEFAULT 0,
    page_total_actions_days_28 INTEGER DEFAULT 0,
    page_post_engagements INTEGER DEFAULT 0,
    page_post_engagements_week INTEGER DEFAULT 0,
    page_post_engagements_days_28 INTEGER DEFAULT 0,

    -- Follows
    page_follows INTEGER DEFAULT 0,

    -- Media views
    page_media_view INTEGER DEFAULT 0,
    page_media_view_week INTEGER DEFAULT 0,
    page_media_view_days_28 INTEGER DEFAULT 0,
    page_media_view_from_followers INTEGER DEFAULT 0,
    page_media_view_from_non_followers INTEGER DEFAULT 0,

    -- Reactions (daily totals)
    reactions_like_total INTEGER DEFAULT 0,
    reactions_love_total INTEGER DEFAULT 0,
    reactions_wow_total INTEGER DEFAULT 0,
    reactions_haha_total INTEGER DEFAULT 0,
    reactions_sorry_total INTEGER DEFAULT 0,
    reactions_anger_total INTEGER DEFAULT 0,

    -- Reactions (week)
    reactions_like_week INTEGER DEFAULT 0,
    reactions_love_week INTEGER DEFAULT 0,
    reactions_wow_week INTEGER DEFAULT 0,
    reactions_haha_week INTEGER DEFAULT 0,
    reactions_sorry_week INTEGER DEFAULT 0,
    reactions_anger_week INTEGER DEFAULT 0,

    -- Video views
    page_video_views INTEGER DEFAULT 0,
    page_video_views_week INTEGER DEFAULT 0,
    page_video_views_days_28 INTEGER DEFAULT 0,

    -- Raw API response for additional data
    raw_metrics JSONB DEFAULT '{}',

    -- Timestamps
    metrics_fetched_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Unique constraint: one row per business asset
CREATE UNIQUE INDEX IF NOT EXISTS idx_fb_page_insights_business_asset
    ON facebook_page_insights(business_asset_id);

CREATE INDEX IF NOT EXISTS idx_fb_page_insights_fetched_at
    ON facebook_page_insights(metrics_fetched_at);


-- ============================================================================
-- INSTAGRAM ACCOUNT INSIGHTS (account-level metrics)
-- ============================================================================

CREATE TABLE IF NOT EXISTS instagram_account_insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_asset_id TEXT NOT NULL REFERENCES business_assets(id) ON DELETE CASCADE,

    -- Account metadata
    ig_user_id TEXT NOT NULL,
    username TEXT,
    name TEXT,
    biography TEXT,
    profile_picture_url TEXT,

    -- Basic counts
    followers_count INTEGER DEFAULT 0,
    follows_count INTEGER DEFAULT 0,
    media_count INTEGER DEFAULT 0,

    -- Reach metrics
    reach_day INTEGER DEFAULT 0,
    reach_week INTEGER DEFAULT 0,
    reach_days_28 INTEGER DEFAULT 0,

    -- Raw API response for additional data
    raw_metrics JSONB DEFAULT '{}',

    -- Timestamps
    metrics_fetched_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Unique constraint: one row per business asset
CREATE UNIQUE INDEX IF NOT EXISTS idx_ig_account_insights_business_asset
    ON instagram_account_insights(business_asset_id);

CREATE INDEX IF NOT EXISTS idx_ig_account_insights_fetched_at
    ON instagram_account_insights(metrics_fetched_at);


-- ============================================================================
-- FACEBOOK POST INSIGHTS (post-level metrics for feed posts/photos)
-- ============================================================================

CREATE TABLE IF NOT EXISTS facebook_post_insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_asset_id TEXT NOT NULL REFERENCES business_assets(id) ON DELETE CASCADE,

    -- Post identification
    platform_post_id TEXT NOT NULL,
    completed_post_id UUID REFERENCES completed_posts(id) ON DELETE SET NULL,

    -- Post-level metrics
    post_media_view INTEGER DEFAULT 0,
    post_media_view_from_followers INTEGER DEFAULT 0,
    post_media_view_from_non_followers INTEGER DEFAULT 0,

    post_impressions_unique INTEGER DEFAULT 0,
    post_impressions_organic_unique INTEGER DEFAULT 0,

    -- Reactions
    reactions_like INTEGER DEFAULT 0,
    reactions_love INTEGER DEFAULT 0,
    reactions_wow INTEGER DEFAULT 0,
    reactions_haha INTEGER DEFAULT 0,
    reactions_sorry INTEGER DEFAULT 0,
    reactions_anger INTEGER DEFAULT 0,
    reactions_by_type JSONB DEFAULT '{}',

    -- Raw API response
    raw_metrics JSONB DEFAULT '{}',

    -- Timestamps
    metrics_fetched_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Unique constraint: one row per post
CREATE UNIQUE INDEX IF NOT EXISTS idx_fb_post_insights_platform_post
    ON facebook_post_insights(business_asset_id, platform_post_id);

CREATE INDEX IF NOT EXISTS idx_fb_post_insights_completed_post
    ON facebook_post_insights(completed_post_id);

CREATE INDEX IF NOT EXISTS idx_fb_post_insights_fetched_at
    ON facebook_post_insights(metrics_fetched_at);


-- ============================================================================
-- FACEBOOK VIDEO INSIGHTS (video/reel metrics)
-- ============================================================================

CREATE TABLE IF NOT EXISTS facebook_video_insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_asset_id TEXT NOT NULL REFERENCES business_assets(id) ON DELETE CASCADE,

    -- Video identification
    platform_video_id TEXT NOT NULL,
    completed_post_id UUID REFERENCES completed_posts(id) ON DELETE SET NULL,

    -- Video metrics
    post_video_views INTEGER DEFAULT 0,
    post_video_views_unique INTEGER DEFAULT 0,
    post_video_view_time_ms BIGINT DEFAULT 0,
    post_video_avg_time_watched_ms INTEGER DEFAULT 0,
    post_video_length_ms INTEGER DEFAULT 0,

    -- Raw API response
    raw_metrics JSONB DEFAULT '{}',

    -- Timestamps
    metrics_fetched_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Unique constraint: one row per video
CREATE UNIQUE INDEX IF NOT EXISTS idx_fb_video_insights_platform_video
    ON facebook_video_insights(business_asset_id, platform_video_id);

CREATE INDEX IF NOT EXISTS idx_fb_video_insights_completed_post
    ON facebook_video_insights(completed_post_id);

CREATE INDEX IF NOT EXISTS idx_fb_video_insights_fetched_at
    ON facebook_video_insights(metrics_fetched_at);


-- ============================================================================
-- INSTAGRAM MEDIA INSIGHTS (post/reel metrics)
-- ============================================================================

CREATE TABLE IF NOT EXISTS instagram_media_insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_asset_id TEXT NOT NULL REFERENCES business_assets(id) ON DELETE CASCADE,

    -- Media identification
    platform_media_id TEXT NOT NULL,
    completed_post_id UUID REFERENCES completed_posts(id) ON DELETE SET NULL,
    media_type TEXT, -- 'image', 'video', 'carousel', 'reel'
    permalink TEXT,

    -- Feed post metrics (all media types)
    comments INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    saved INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    views INTEGER DEFAULT 0,

    -- Reel-specific metrics
    ig_reels_avg_watch_time_ms INTEGER DEFAULT 0,
    ig_reels_video_view_total_time_ms BIGINT DEFAULT 0,

    -- Raw API response
    raw_metrics JSONB DEFAULT '{}',

    -- Timestamps
    metrics_fetched_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Unique constraint: one row per media
CREATE UNIQUE INDEX IF NOT EXISTS idx_ig_media_insights_platform_media
    ON instagram_media_insights(business_asset_id, platform_media_id);

CREATE INDEX IF NOT EXISTS idx_ig_media_insights_completed_post
    ON instagram_media_insights(completed_post_id);

CREATE INDEX IF NOT EXISTS idx_ig_media_insights_fetched_at
    ON instagram_media_insights(metrics_fetched_at);

CREATE INDEX IF NOT EXISTS idx_ig_media_insights_media_type
    ON instagram_media_insights(media_type);


-- ============================================================================
-- UPDATE TRIGGERS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_insights_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers to all insights tables
DROP TRIGGER IF EXISTS update_fb_page_insights_timestamp ON facebook_page_insights;
CREATE TRIGGER update_fb_page_insights_timestamp
    BEFORE UPDATE ON facebook_page_insights
    FOR EACH ROW
    EXECUTE FUNCTION update_insights_timestamp();

DROP TRIGGER IF EXISTS update_ig_account_insights_timestamp ON instagram_account_insights;
CREATE TRIGGER update_ig_account_insights_timestamp
    BEFORE UPDATE ON instagram_account_insights
    FOR EACH ROW
    EXECUTE FUNCTION update_insights_timestamp();

DROP TRIGGER IF EXISTS update_fb_post_insights_timestamp ON facebook_post_insights;
CREATE TRIGGER update_fb_post_insights_timestamp
    BEFORE UPDATE ON facebook_post_insights
    FOR EACH ROW
    EXECUTE FUNCTION update_insights_timestamp();

DROP TRIGGER IF EXISTS update_fb_video_insights_timestamp ON facebook_video_insights;
CREATE TRIGGER update_fb_video_insights_timestamp
    BEFORE UPDATE ON facebook_video_insights
    FOR EACH ROW
    EXECUTE FUNCTION update_insights_timestamp();

DROP TRIGGER IF EXISTS update_ig_media_insights_timestamp ON instagram_media_insights;
CREATE TRIGGER update_ig_media_insights_timestamp
    BEFORE UPDATE ON instagram_media_insights
    FOR EACH ROW
    EXECUTE FUNCTION update_insights_timestamp();


-- ============================================================================
-- COMMENTS
-- ============================================================================
--
-- This migration creates 5 tables:
-- 1. facebook_page_insights: Caches Facebook page-level metrics
-- 2. instagram_account_insights: Caches Instagram account-level metrics
-- 3. facebook_post_insights: Caches Facebook post metrics (feed posts/photos)
-- 4. facebook_video_insights: Caches Facebook video/reel metrics
-- 5. instagram_media_insights: Caches Instagram post/reel metrics
--
-- Key design decisions:
-- - One row per entity (page, post, video, media) - updated when refreshed
-- - business_asset_id for multi-tenancy
-- - completed_post_id links to our internal post record
-- - raw_metrics JSONB stores full API response for flexibility
-- - metrics_fetched_at tracks when data was last refreshed
