-- backend/database/migrations/026_drop_deprecated_sources_jsonb.sql
-- Drop deprecated sources JSONB columns from news_event_seeds and ingested_events tables.
-- Sources are now stored in the normalized 'sources' table and linked via junction tables:
--   - news_event_seed_sources (news_event_seed_id, source_id)
--   - ingested_event_sources (ingested_event_id, source_id)

-- Drop the deprecated sources column from news_event_seeds
ALTER TABLE news_event_seeds DROP COLUMN IF EXISTS sources;

-- Drop the deprecated sources column from ingested_events
ALTER TABLE ingested_events DROP COLUMN IF EXISTS sources;

-- Drop the associated GIN indexes that were on the JSONB columns
DROP INDEX IF EXISTS idx_news_event_seeds_sources;
DROP INDEX IF EXISTS idx_ingested_events_sources;

-- Update comments
COMMENT ON TABLE news_event_seeds IS 'Canonical news event content seeds (deduplicated and consolidated). Sources are linked via news_event_seed_sources junction table.';
COMMENT ON TABLE ingested_events IS 'Raw events from research agents (before deduplication). Sources are linked via ingested_event_sources junction table.';
