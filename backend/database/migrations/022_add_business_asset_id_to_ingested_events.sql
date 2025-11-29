-- Migration 022: Add business_asset_id to ingested_events
-- The ingested_events table was missing business_asset_id from migration 019

-- Add business_asset_id to ingested_events (nullable first, will be made NOT NULL after data migration)
ALTER TABLE ingested_events
ADD COLUMN IF NOT EXISTS business_asset_id TEXT REFERENCES business_assets(id);

CREATE INDEX IF NOT EXISTS idx_ingested_events_business_asset ON ingested_events(business_asset_id);

COMMENT ON COLUMN ingested_events.business_asset_id IS 'References the business asset this ingested event belongs to';
