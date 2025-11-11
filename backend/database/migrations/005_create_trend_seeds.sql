-- backend/database/migrations/005_create_trend_seeds.sql
-- Trend seeds from social media

CREATE TABLE IF NOT EXISTS trend_seeds (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    hashtags TEXT[] DEFAULT ARRAY[]::TEXT[],
    posts JSONB DEFAULT '[]'::jsonb,  -- Array of ScraperPost objects
    users JSONB DEFAULT '[]'::jsonb,  -- Array of User objects
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by TEXT NOT NULL,  -- Foundation model used

    -- Constraints
    CONSTRAINT non_empty_name CHECK (LENGTH(TRIM(name)) > 0),
    CONSTRAINT non_empty_description CHECK (LENGTH(TRIM(description)) > 0),
    CONSTRAINT non_empty_created_by CHECK (LENGTH(TRIM(created_by)) > 0)
);

-- Indexes
CREATE INDEX idx_trend_seeds_name ON trend_seeds(name);
CREATE INDEX idx_trend_seeds_created_at ON trend_seeds(created_at DESC);
CREATE INDEX idx_trend_seeds_created_by ON trend_seeds(created_by);

-- GIN indexes for array and JSONB columns
CREATE INDEX idx_trend_seeds_hashtags ON trend_seeds USING GIN(hashtags);
CREATE INDEX idx_trend_seeds_posts ON trend_seeds USING GIN(posts);
CREATE INDEX idx_trend_seeds_users ON trend_seeds USING GIN(users);

-- Full-text search on name and description
CREATE INDEX idx_trend_seeds_search ON trend_seeds
    USING GIN(to_tsvector('english', name || ' ' || description));

COMMENT ON TABLE trend_seeds IS 'Trend content seeds discovered from social media';
COMMENT ON COLUMN trend_seeds.posts IS 'JSON array of ScraperPost objects';
COMMENT ON COLUMN trend_seeds.users IS 'JSON array of User objects';
