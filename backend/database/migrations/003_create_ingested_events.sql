-- backend/database/migrations/003_create_ingested_events.sql
-- Ingested events table (pre-deduplication)

CREATE TABLE IF NOT EXISTS ingested_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    location TEXT NOT NULL,
    description TEXT NOT NULL,
    sources JSONB DEFAULT '[]'::jsonb,  -- Array of source objects
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ingested_by TEXT NOT NULL,

    -- Constraints
    CONSTRAINT non_empty_name CHECK (LENGTH(TRIM(name)) > 0),
    CONSTRAINT non_empty_location CHECK (LENGTH(TRIM(location)) > 0),
    CONSTRAINT non_empty_description CHECK (LENGTH(TRIM(description)) > 0),
    CONSTRAINT non_empty_ingested_by CHECK (LENGTH(TRIM(ingested_by)) > 0),
    CONSTRAINT valid_time_range CHECK (end_time IS NULL OR start_time IS NULL OR end_time >= start_time)
);

-- Indexes
CREATE INDEX idx_ingested_events_ingested_by ON ingested_events(ingested_by);
CREATE INDEX idx_ingested_events_created_at ON ingested_events(created_at DESC);
CREATE INDEX idx_ingested_events_location ON ingested_events(location);

-- GIN index for JSONB sources column (for searching within sources)
CREATE INDEX idx_ingested_events_sources ON ingested_events USING GIN(sources);

COMMENT ON TABLE ingested_events IS 'Raw events from research agents (before deduplication)';
COMMENT ON COLUMN ingested_events.sources IS 'JSON array of source objects';
COMMENT ON COLUMN ingested_events.ingested_by IS 'Agent that ingested this event (e.g., Perplexity Sonar, ChatGPT Deep Research)';
