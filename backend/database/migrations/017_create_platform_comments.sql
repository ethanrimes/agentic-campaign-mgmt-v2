-- backend/database/migrations/017_create_platform_comments.sql
-- Platform comments from Facebook and Instagram for AI-powered response generation

CREATE TYPE comment_status AS ENUM ('pending', 'responded', 'failed', 'ignored');

CREATE TABLE IF NOT EXISTS platform_comments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Platform identification
    platform platform_type NOT NULL,
    comment_id TEXT NOT NULL UNIQUE,  -- Platform's unique comment ID
    post_id TEXT NOT NULL,  -- Platform's post ID this comment belongs to

    -- Comment content
    comment_text TEXT NOT NULL,
    commenter_username TEXT NOT NULL,
    commenter_id TEXT NOT NULL,
    parent_comment_id TEXT,  -- For replies to comments (threading)

    -- Metadata from platform
    created_time TIMESTAMP WITH TIME ZONE NOT NULL,
    like_count INTEGER DEFAULT 0,
    permalink_url TEXT,

    -- Response tracking
    status comment_status DEFAULT 'pending',
    response_text TEXT,
    response_comment_id TEXT,  -- Platform ID of our reply
    responded_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,

    -- Optional link to our completed_posts if we can match it
    our_post_id UUID REFERENCES completed_posts(id) ON DELETE SET NULL,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Constraints
    CONSTRAINT non_empty_comment CHECK (LENGTH(TRIM(comment_text)) > 0),
    CONSTRAINT responded_requires_response CHECK (
        (status != 'responded') OR (response_text IS NOT NULL AND responded_at IS NOT NULL)
    ),
    CONSTRAINT unique_platform_comment UNIQUE (platform, comment_id)
);

-- Indexes for efficient querying
CREATE INDEX idx_platform_comments_platform ON platform_comments(platform);
CREATE INDEX idx_platform_comments_status ON platform_comments(status);
CREATE INDEX idx_platform_comments_post_id ON platform_comments(post_id);
CREATE INDEX idx_platform_comments_created_time ON platform_comments(created_time DESC);
CREATE INDEX idx_platform_comments_our_post_id ON platform_comments(our_post_id);

-- Composite index for finding pending comments by platform
CREATE INDEX idx_platform_comments_pending_by_platform
    ON platform_comments(platform, created_time DESC)
    WHERE status = 'pending';

-- Composite index for finding responded comments
CREATE INDEX idx_platform_comments_responded
    ON platform_comments(responded_at DESC)
    WHERE status = 'responded';

-- Update timestamp trigger
CREATE OR REPLACE FUNCTION update_platform_comments_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_platform_comments_updated_at
    BEFORE UPDATE ON platform_comments
    FOR EACH ROW
    EXECUTE FUNCTION update_platform_comments_updated_at();

-- Comments
COMMENT ON TABLE platform_comments IS 'Comments from Facebook and Instagram posts for AI-powered response generation';
COMMENT ON COLUMN platform_comments.comment_id IS 'Unique comment ID from the platform (Facebook or Instagram)';
COMMENT ON COLUMN platform_comments.post_id IS 'Platform post ID this comment belongs to';
COMMENT ON COLUMN platform_comments.parent_comment_id IS 'If this is a reply to another comment, the parent comment ID';
COMMENT ON COLUMN platform_comments.our_post_id IS 'Optional reference to our completed_posts table if we can match it';
COMMENT ON COLUMN platform_comments.response_comment_id IS 'Platform ID of our AI-generated reply comment';
COMMENT ON COLUMN platform_comments.retry_count IS 'Number of times we attempted to respond to this comment';
