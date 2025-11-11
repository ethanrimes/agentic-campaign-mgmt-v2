-- backend/database/migrations/008_create_content_creation_tasks.sql
-- Content creation tasks from the planner agent

CREATE TYPE task_status AS ENUM ('pending', 'in_progress', 'completed', 'failed');
CREATE TYPE seed_type AS ENUM ('news_event', 'trend', 'ungrounded');

CREATE TABLE IF NOT EXISTS content_creation_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Seed reference
    content_seed_id UUID NOT NULL,
    content_seed_type seed_type NOT NULL,

    -- Post allocations
    instagram_image_posts INTEGER DEFAULT 0 CHECK (instagram_image_posts >= 0),
    instagram_reel_posts INTEGER DEFAULT 0 CHECK (instagram_reel_posts >= 0),
    facebook_feed_posts INTEGER DEFAULT 0 CHECK (facebook_feed_posts >= 0),
    facebook_video_posts INTEGER DEFAULT 0 CHECK (facebook_video_posts >= 0),

    -- Media budgets
    image_budget INTEGER DEFAULT 0 CHECK (image_budget >= 0),
    video_budget INTEGER DEFAULT 0 CHECK (video_budget >= 0),

    -- Status
    status task_status DEFAULT 'pending',
    error_message TEXT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,

    -- Constraints
    CONSTRAINT valid_completion_order CHECK (
        (started_at IS NULL OR started_at >= created_at) AND
        (completed_at IS NULL OR (started_at IS NOT NULL AND completed_at >= started_at))
    )
);

-- Indexes
CREATE INDEX idx_content_creation_tasks_status ON content_creation_tasks(status);
CREATE INDEX idx_content_creation_tasks_seed_id ON content_creation_tasks(content_seed_id);
CREATE INDEX idx_content_creation_tasks_seed_type ON content_creation_tasks(content_seed_type);
CREATE INDEX idx_content_creation_tasks_created_at ON content_creation_tasks(created_at DESC);

-- Composite index for finding pending/in_progress tasks
CREATE INDEX idx_content_creation_tasks_active ON content_creation_tasks(status, created_at)
    WHERE status IN ('pending', 'in_progress');

COMMENT ON TABLE content_creation_tasks IS 'Content creation tasks from the planner agent';
COMMENT ON COLUMN content_creation_tasks.content_seed_id IS 'Foreign key to news_event_seeds, trend_seeds, or ungrounded_seeds';
