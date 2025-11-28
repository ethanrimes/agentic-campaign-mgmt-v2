-- Migration 021: Add target_audience to business_assets table
-- The target audience is stored as plain text (not encrypted) and can be several sentences long

ALTER TABLE business_assets
ADD COLUMN target_audience TEXT;

-- Set a default for existing records (can be updated via upload script)
UPDATE business_assets
SET target_audience = 'College students at the University of Pennsylvania interested in campus news, events, and local culture'
WHERE target_audience IS NULL;

-- Make it NOT NULL after setting defaults
ALTER TABLE business_assets
ALTER COLUMN target_audience SET NOT NULL;

-- Add comment explaining the column
COMMENT ON COLUMN business_assets.target_audience IS 'Description of the target audience for this business asset. Used in agent prompts to guide content creation and strategy.';
