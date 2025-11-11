-- backend/database/migrations/007_create_insight_reports.sql
-- Insight reports from the insights agent

CREATE TABLE IF NOT EXISTS insight_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    summary TEXT NOT NULL,
    findings TEXT NOT NULL,
    tool_calls JSONB DEFAULT '[]'::jsonb,  -- Array of ToolCall objects
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by TEXT NOT NULL,  -- Foundation model used

    -- Constraints
    CONSTRAINT non_empty_summary CHECK (LENGTH(TRIM(summary)) > 0),
    CONSTRAINT non_empty_findings CHECK (LENGTH(TRIM(findings)) > 0),
    CONSTRAINT non_empty_created_by CHECK (LENGTH(TRIM(created_by)) > 0)
);

-- Indexes
CREATE INDEX idx_insight_reports_created_at ON insight_reports(created_at DESC);
CREATE INDEX idx_insight_reports_created_by ON insight_reports(created_by);

-- GIN index for JSONB tool_calls
CREATE INDEX idx_insight_reports_tool_calls ON insight_reports USING GIN(tool_calls);

-- Full-text search on summary and findings
CREATE INDEX idx_insight_reports_search ON insight_reports
    USING GIN(to_tsvector('english', summary || ' ' || findings));

COMMENT ON TABLE insight_reports IS 'Insight reports analyzing what content works with the audience';
COMMENT ON COLUMN insight_reports.tool_calls IS 'JSON array of ToolCall objects (tool name, arguments, results)';
