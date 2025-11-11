-- backend/database/migrations/004_create_news_event_seeds.sql
-- Canonical news event seeds (after deduplication)

CREATE TABLE IF NOT EXISTS news_event_seeds (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    location TEXT NOT NULL,
    description TEXT NOT NULL,
    sources JSONB DEFAULT '[]'::jsonb,  -- Array of source objects
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Constraints
    CONSTRAINT non_empty_name CHECK (LENGTH(TRIM(name)) > 0),
    CONSTRAINT non_empty_location CHECK (LENGTH(TRIM(location)) > 0),
    CONSTRAINT non_empty_description CHECK (LENGTH(TRIM(description)) > 0),
    CONSTRAINT valid_time_range CHECK (end_time IS NULL OR start_time IS NULL OR end_time >= start_time)
);

-- Indexes
CREATE INDEX idx_news_event_seeds_name ON news_event_seeds(name);
CREATE INDEX idx_news_event_seeds_location ON news_event_seeds(location);
CREATE INDEX idx_news_event_seeds_created_at ON news_event_seeds(created_at DESC);
CREATE INDEX idx_news_event_seeds_start_time ON news_event_seeds(start_time);

-- GIN index for JSONB sources
CREATE INDEX idx_news_event_seeds_sources ON news_event_seeds USING GIN(sources);

-- Full-text search index on name and description
CREATE INDEX idx_news_event_seeds_search ON news_event_seeds
    USING GIN(to_tsvector('english', name || ' ' || description));

COMMENT ON TABLE news_event_seeds IS 'Canonical news event content seeds (deduplicated and consolidated)';
