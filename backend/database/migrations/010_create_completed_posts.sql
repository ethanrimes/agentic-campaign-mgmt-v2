-- backend/database/migrations/010_create_completed_posts.sql
-- Completed posts ready for publishing

CREATE TYPE platform_type AS ENUM ('facebook', 'instagram');
CREATE TYPE post_type AS ENUM (
    'instagram_image',
    'instagram_carousel',
    'instagram_reel',
    'instagram_story',
    'facebook_feed',
    'facebook_video'
);
CREATE TYPE post_status AS ENUM ('pending', 'published', 'failed');

CREATE TABLE IF NOT EXISTS completed_posts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Task and seed references
    task_id UUID NOT NULL REFERENCES content_creation_tasks(id) ON DELETE CASCADE,
    content_seed_id UUID NOT NULL,
    content_seed_type seed_type NOT NULL,

    -- Platform and type
    platform platform_type NOT NULL,
    post_type post_type NOT NULL,

    -- Content
    text TEXT NOT NULL,
    media_urls TEXT[] DEFAULT ARRAY[]::TEXT[],

    -- Optional metadata
    location TEXT,
    music TEXT,
    hashtags TEXT[] DEFAULT ARRAY[]::TEXT[],

    -- Publishing status
    status post_status DEFAULT 'pending',
    published_at TIMESTAMP WITH TIME ZONE,
    platform_post_id TEXT,
    platform_post_url TEXT,
    error_message TEXT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Constraints
    CONSTRAINT non_empty_text CHECK (LENGTH(TRIM(text)) > 0),
    CONSTRAINT published_requires_timestamp CHECK (
        (status != 'published') OR (published_at IS NOT NULL AND platform_post_id IS NOT NULL)
    )
);

-- Indexes
CREATE INDEX idx_completed_posts_task_id ON completed_posts(task_id);
CREATE INDEX idx_completed_posts_seed_id ON completed_posts(content_seed_id);
CREATE INDEX idx_completed_posts_platform ON completed_posts(platform);
CREATE INDEX idx_completed_posts_status ON completed_posts(status);
CREATE INDEX idx_completed_posts_created_at ON completed_posts(created_at DESC);
CREATE INDEX idx_completed_posts_published_at ON completed_posts(published_at DESC);

-- Composite index for finding unpublished posts by platform
CREATE INDEX idx_completed_posts_pending_by_platform ON completed_posts(platform, created_at)
    WHERE status = 'pending';

-- GIN indexes for arrays
CREATE INDEX idx_completed_posts_hashtags ON completed_posts USING GIN(hashtags);

COMMENT ON TABLE completed_posts IS 'Completed posts ready for or already published';
COMMENT ON COLUMN completed_posts.media_urls IS 'Array of Supabase URLs to media files';
COMMENT ON COLUMN completed_posts.platform_post_id IS 'Post ID from Facebook/Instagram API';
