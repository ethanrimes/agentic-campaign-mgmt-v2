-- backend/database/migrations/039_add_verifier_manual_override.sql
-- Add is_manually_overridden field to verifier_responses table

-- Add the column with default false
ALTER TABLE verifier_responses
ADD COLUMN IF NOT EXISTS is_manually_overridden boolean NOT NULL DEFAULT false;

-- Add override metadata columns
ALTER TABLE verifier_responses
ADD COLUMN IF NOT EXISTS override_reason text,
ADD COLUMN IF NOT EXISTS overridden_at timestamp with time zone;

-- Create index for finding overridden reports
CREATE INDEX IF NOT EXISTS idx_verifier_responses_overridden
    ON verifier_responses(business_asset_id, is_manually_overridden)
    WHERE is_manually_overridden = true;

COMMENT ON COLUMN verifier_responses.is_manually_overridden IS 'True if this verification was manually overridden to allow publishing despite rejection';
COMMENT ON COLUMN verifier_responses.override_reason IS 'Optional reason provided when manually overriding a rejection';
COMMENT ON COLUMN verifier_responses.overridden_at IS 'Timestamp when the manual override was applied';
