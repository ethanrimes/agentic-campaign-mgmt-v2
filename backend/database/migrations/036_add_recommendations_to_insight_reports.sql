-- backend/database/migrations/036_add_recommendations_to_insight_reports.sql
-- Add recommendations column to insight_reports for storing actionable engagement recommendations

ALTER TABLE insight_reports
ADD COLUMN recommendations JSONB DEFAULT '[]'::jsonb;

-- Add a comment for the new column
COMMENT ON COLUMN insight_reports.recommendations IS 'JSON array of actionable recommendations for maximizing engagement';

-- Update the full-text search index to include recommendations
DROP INDEX IF EXISTS idx_insight_reports_search;
CREATE INDEX idx_insight_reports_search ON insight_reports
    USING GIN(to_tsvector('english', summary || ' ' || findings || ' ' || COALESCE(recommendations::text, '')));
