-- backend/database/migrations/014_refactor_sources_to_foreign_keys.sql
-- Refactor sources from JSONB to proper foreign key relationships

-- ============================================================================
-- STEP 1: Create junction tables for many-to-many relationships
-- ============================================================================

-- Junction table: ingested_events <-> sources
CREATE TABLE IF NOT EXISTS ingested_event_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ingested_event_id UUID NOT NULL REFERENCES ingested_events(id) ON DELETE CASCADE,
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Ensure no duplicate relationships
    CONSTRAINT unique_ingested_event_source UNIQUE (ingested_event_id, source_id)
);

-- Junction table: news_event_seeds <-> sources
CREATE TABLE IF NOT EXISTS news_event_seed_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    news_event_seed_id UUID NOT NULL REFERENCES news_event_seeds(id) ON DELETE CASCADE,
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Ensure no duplicate relationships
    CONSTRAINT unique_news_event_seed_source UNIQUE (news_event_seed_id, source_id)
);

-- Create indexes for efficient lookups
CREATE INDEX idx_ingested_event_sources_event ON ingested_event_sources(ingested_event_id);
CREATE INDEX idx_ingested_event_sources_source ON ingested_event_sources(source_id);
CREATE INDEX idx_news_event_seed_sources_seed ON news_event_seed_sources(news_event_seed_id);
CREATE INDEX idx_news_event_seed_sources_source ON news_event_seed_sources(source_id);

-- Add comments
COMMENT ON TABLE ingested_event_sources IS 'Junction table linking ingested events to their sources';
COMMENT ON TABLE news_event_seed_sources IS 'Junction table linking news event seeds to their sources';

-- ============================================================================
-- STEP 2: Data migration (if there's existing data in JSONB columns)
-- ============================================================================

-- Note: This migration script assumes you'll handle data migration separately
-- or that the JSONB sources columns are currently empty. If you have existing
-- data, you'll need to write a Python script to:
-- 1. Read the JSONB sources from each row
-- 2. Create entries in the sources table
-- 3. Create junction table entries
-- 4. Then drop the JSONB columns

-- For now, we'll keep the JSONB columns as a backup during transition
-- They can be removed in a future migration after data is fully migrated

-- ============================================================================
-- STEP 3: Optional - Drop JSONB columns (only after data migration)
-- ============================================================================

-- Uncomment these lines ONLY after you've migrated all data:
-- ALTER TABLE ingested_events DROP COLUMN IF EXISTS sources;
-- DROP INDEX IF EXISTS idx_ingested_events_sources;
-- ALTER TABLE news_event_seeds DROP COLUMN IF EXISTS sources;
-- DROP INDEX IF EXISTS idx_news_event_seeds_sources;
