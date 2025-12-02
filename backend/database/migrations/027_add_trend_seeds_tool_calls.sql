-- backend/database/migrations/027_add_trend_seeds_tool_calls.sql
-- Add tool_calls column to trend_seeds table for storing agent tool call history

-- Add tool_calls column
ALTER TABLE trend_seeds
ADD COLUMN IF NOT EXISTS tool_calls JSONB DEFAULT '[]'::jsonb;

-- Add index for tool_calls (GIN index for JSONB queries)
CREATE INDEX IF NOT EXISTS idx_trend_seeds_tool_calls ON trend_seeds USING GIN(tool_calls);

-- Add comment
COMMENT ON COLUMN trend_seeds.tool_calls IS 'JSON array of tool calls made by the trend discovery agent, matching the format used in insight_reports';
