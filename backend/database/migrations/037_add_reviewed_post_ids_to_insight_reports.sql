-- backend/database/migrations/037_add_reviewed_post_ids_to_insight_reports.sql
-- Add reviewed_post_ids column to insight_reports to track which posts were analyzed

-- Add the reviewed_post_ids column as UUID array referencing completed_posts
ALTER TABLE insight_reports
ADD COLUMN reviewed_post_ids UUID[] DEFAULT '{}';

-- Create index for efficient lookups
CREATE INDEX idx_insight_reports_reviewed_post_ids ON insight_reports USING GIN(reviewed_post_ids);

COMMENT ON COLUMN insight_reports.reviewed_post_ids IS 'Array of completed_post IDs that were reviewed/analyzed in this insight report';
