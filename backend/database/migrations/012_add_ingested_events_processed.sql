-- backend/database/migrations/012_add_ingested_events_processed.sql
-- Add processed tracking columns to ingested_events table

-- Add processed flag (defaults to FALSE for existing rows)
ALTER TABLE ingested_events
ADD COLUMN processed BOOLEAN NOT NULL DEFAULT FALSE;

-- Add timestamp for when the event was processed
ALTER TABLE ingested_events
ADD COLUMN processed_at TIMESTAMP WITH TIME ZONE;

-- Add reference to the canonical news event seed created/merged during deduplication
ALTER TABLE ingested_events
ADD COLUMN canonical_event_id UUID;

-- Add foreign key constraint to news_event_seeds
ALTER TABLE ingested_events
ADD CONSTRAINT fk_ingested_events_canonical_event
FOREIGN KEY (canonical_event_id) REFERENCES news_event_seeds(id) ON DELETE SET NULL;

-- Create index on processed column for efficient querying of unprocessed events
CREATE INDEX idx_ingested_events_processed ON ingested_events(processed) WHERE processed = FALSE;

-- Create index on canonical_event_id for lookups
CREATE INDEX idx_ingested_events_canonical_event_id ON ingested_events(canonical_event_id);

-- Add comments
COMMENT ON COLUMN ingested_events.processed IS 'Whether this event has been processed by the deduplicator';
COMMENT ON COLUMN ingested_events.processed_at IS 'When this event was processed by the deduplicator';
COMMENT ON COLUMN ingested_events.canonical_event_id IS 'ID of the canonical news event seed this was deduplicated into';
