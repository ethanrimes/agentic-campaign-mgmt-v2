-- backend/database/migrations/038_add_manually_overridden_verification_status.sql
-- Add 'manually_overridden' as a verification status option

-- PostgreSQL ENUMs cannot be altered inline - we need to recreate
-- First, add the new value to the enum type
ALTER TYPE verification_status ADD VALUE IF NOT EXISTS 'manually_overridden';

-- Update the index for posts ready to publish to include manually_overridden
DROP INDEX IF EXISTS idx_completed_posts_verified_pending;
CREATE INDEX idx_completed_posts_verified_pending ON completed_posts(platform, scheduled_posting_time)
    WHERE status = 'pending' AND (verification_status = 'verified' OR verification_status = 'manually_overridden');

COMMENT ON COLUMN completed_posts.verification_status IS 'Content verification status: unverified (not yet checked), verified (approved), rejected (failed verification), manually_overridden (rejected but manually approved)';
