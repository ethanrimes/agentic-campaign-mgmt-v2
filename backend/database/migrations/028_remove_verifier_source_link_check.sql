-- backend/database/migrations/028_remove_verifier_source_link_check.sql
-- Remove has_source_link_if_news column from verifier_responses
-- Source links are now deterministically appended by the content agent, so verification is not needed

-- Drop the existing constraint that references has_source_link_if_news
ALTER TABLE verifier_responses DROP CONSTRAINT IF EXISTS valid_approval;

-- Drop the column
ALTER TABLE verifier_responses DROP COLUMN IF EXISTS has_source_link_if_news;

-- Add new constraint without has_source_link_if_news
ALTER TABLE verifier_responses ADD CONSTRAINT valid_approval CHECK (
    -- If approved, must have passed all applicable checks
    (is_approved = FALSE) OR
    (has_no_offensive_content = TRUE AND
     (has_no_misinformation IS NULL OR has_no_misinformation = TRUE))
);

COMMENT ON CONSTRAINT valid_approval ON verifier_responses IS 'Ensures approved posts passed all applicable checks (offensive content and misinformation for news events)';
