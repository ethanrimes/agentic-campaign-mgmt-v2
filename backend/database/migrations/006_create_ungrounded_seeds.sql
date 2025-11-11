-- backend/database/migrations/006_create_ungrounded_seeds.sql
-- Ungrounded (creative) content seeds

CREATE TABLE IF NOT EXISTS ungrounded_seeds (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    idea TEXT NOT NULL,
    format TEXT NOT NULL,
    details TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by TEXT NOT NULL,  -- Foundation model used

    -- Constraints
    CONSTRAINT non_empty_idea CHECK (LENGTH(TRIM(idea)) > 0),
    CONSTRAINT non_empty_format CHECK (LENGTH(TRIM(format)) > 0),
    CONSTRAINT non_empty_details CHECK (LENGTH(TRIM(details)) > 0),
    CONSTRAINT non_empty_created_by CHECK (LENGTH(TRIM(created_by)) > 0)
);

-- Indexes
CREATE INDEX idx_ungrounded_seeds_format ON ungrounded_seeds(format);
CREATE INDEX idx_ungrounded_seeds_created_at ON ungrounded_seeds(created_at DESC);
CREATE INDEX idx_ungrounded_seeds_created_by ON ungrounded_seeds(created_by);

-- Full-text search on idea and details
CREATE INDEX idx_ungrounded_seeds_search ON ungrounded_seeds
    USING GIN(to_tsvector('english', idea || ' ' || details));

COMMENT ON TABLE ungrounded_seeds IS 'Creative content seeds not grounded in news or trends';
COMMENT ON COLUMN ungrounded_seeds.format IS 'Intended medium (image, video, carousel, etc.)';
