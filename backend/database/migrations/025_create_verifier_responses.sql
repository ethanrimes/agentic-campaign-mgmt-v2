-- backend/database/migrations/025_create_verifier_responses.sql
-- Table for storing verifier LLM responses for content safety verification

CREATE TABLE IF NOT EXISTS verifier_responses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Foreign key to the completed post being verified
    completed_post_id UUID NOT NULL REFERENCES completed_posts(id) ON DELETE CASCADE,

    -- Business asset for multi-tenancy
    business_asset_id TEXT NOT NULL,

    -- Verification result
    is_approved BOOLEAN NOT NULL,

    -- Checklist results (stored as individual fields for queryability)
    has_source_link_if_news BOOLEAN,  -- NULL if not a news event
    has_no_offensive_content BOOLEAN NOT NULL,
    has_no_misinformation BOOLEAN,    -- NULL if not a news event

    -- Detailed reasoning from the verifier LLM
    reasoning TEXT NOT NULL,

    -- Any specific issues found
    issues_found TEXT[],

    -- Model used for verification
    model TEXT NOT NULL DEFAULT 'gemini-2.5-flash',

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Constraints
    CONSTRAINT valid_approval CHECK (
        -- If approved, must have passed all applicable checks
        (is_approved = FALSE) OR
        (has_no_offensive_content = TRUE AND
         (has_source_link_if_news IS NULL OR has_source_link_if_news = TRUE) AND
         (has_no_misinformation IS NULL OR has_no_misinformation = TRUE))
    )
);

-- Indexes
CREATE INDEX idx_verifier_responses_completed_post_id ON verifier_responses(completed_post_id);
CREATE INDEX idx_verifier_responses_business_asset_id ON verifier_responses(business_asset_id);
CREATE INDEX idx_verifier_responses_is_approved ON verifier_responses(is_approved);
CREATE INDEX idx_verifier_responses_created_at ON verifier_responses(created_at DESC);

-- Unique constraint: one verification per post (latest wins, but we keep history)
-- Actually, we allow multiple verifications to keep audit trail
-- CREATE UNIQUE INDEX idx_verifier_responses_unique_post ON verifier_responses(completed_post_id);

COMMENT ON TABLE verifier_responses IS 'Stores verification results from the content safety verifier LLM';
COMMENT ON COLUMN verifier_responses.has_source_link_if_news IS 'Whether news event posts include source links (NULL for non-news content)';
COMMENT ON COLUMN verifier_responses.has_no_offensive_content IS 'Whether the content passes offensive content check';
COMMENT ON COLUMN verifier_responses.has_no_misinformation IS 'Whether news content passes misinformation check (NULL for non-news content)';
COMMENT ON COLUMN verifier_responses.reasoning IS 'Detailed reasoning from the verifier LLM explaining the decision';
COMMENT ON COLUMN verifier_responses.issues_found IS 'Array of specific issues found during verification';
