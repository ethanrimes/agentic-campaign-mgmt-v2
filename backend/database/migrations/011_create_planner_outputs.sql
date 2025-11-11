-- backend/database/migrations/011_create_planner_outputs.sql
-- Store planner agent outputs for auditing and analysis

CREATE TABLE IF NOT EXISTS planner_outputs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Plan content
    allocations JSONB NOT NULL,  -- Array of ContentSeedAllocation objects
    reasoning TEXT NOT NULL,
    week_start_date DATE NOT NULL,

    -- Success/failure tracking
    is_valid BOOLEAN NOT NULL DEFAULT FALSE,
    validation_errors TEXT[],  -- Array of guardrail violations (if any)

    -- Aggregated metrics (for quick queries)
    total_posts INTEGER NOT NULL,
    total_seeds INTEGER NOT NULL,
    total_images INTEGER NOT NULL,
    total_videos INTEGER NOT NULL,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by TEXT NOT NULL,  -- Foundation model used

    -- Constraints
    CONSTRAINT non_empty_reasoning CHECK (LENGTH(TRIM(reasoning)) > 0),
    CONSTRAINT valid_metrics CHECK (
        total_posts >= 0 AND
        total_seeds >= 0 AND
        total_images >= 0 AND
        total_videos >= 0
    )
);

-- Indexes
CREATE INDEX idx_planner_outputs_week_start ON planner_outputs(week_start_date DESC);
CREATE INDEX idx_planner_outputs_is_valid ON planner_outputs(is_valid);
CREATE INDEX idx_planner_outputs_created_at ON planner_outputs(created_at DESC);

-- GIN index for allocations JSONB
CREATE INDEX idx_planner_outputs_allocations ON planner_outputs USING GIN(allocations);

COMMENT ON TABLE planner_outputs IS 'Planner agent outputs (both valid and invalid plans)';
COMMENT ON COLUMN planner_outputs.is_valid IS 'Whether plan passed guardrail validation';
COMMENT ON COLUMN planner_outputs.validation_errors IS 'List of guardrail violations (empty if valid)';
