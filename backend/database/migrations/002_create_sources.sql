-- backend/database/migrations/002_create_sources.sql
-- Sources table for news event seeds

CREATE TABLE IF NOT EXISTS sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    url TEXT NOT NULL,
    key_findings TEXT NOT NULL,
    found_by TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Indexes
    CONSTRAINT valid_url CHECK (url ~ '^https?://'),
    CONSTRAINT non_empty_findings CHECK (LENGTH(TRIM(key_findings)) > 0),
    CONSTRAINT non_empty_found_by CHECK (LENGTH(TRIM(found_by)) > 0)
);

-- Index for searching by found_by
CREATE INDEX idx_sources_found_by ON sources(found_by);

-- Index for created_at (for time-based queries)
CREATE INDEX idx_sources_created_at ON sources(created_at DESC);

COMMENT ON TABLE sources IS 'Source URLs with key findings for news event seeds';
COMMENT ON COLUMN sources.url IS 'Source URL';
COMMENT ON COLUMN sources.key_findings IS 'Relevant information extracted from this source';
COMMENT ON COLUMN sources.found_by IS 'Agent or tool that discovered this source';
