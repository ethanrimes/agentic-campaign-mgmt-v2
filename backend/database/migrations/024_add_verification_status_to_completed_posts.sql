-- backend/database/migrations/024_add_verification_status_to_completed_posts.sql
-- Add verification status to completed posts for content safety verification

-- Create verification status enum
CREATE TYPE verification_status AS ENUM ('unverified', 'verified', 'rejected');

-- Add verification_status column to completed_posts
-- Default to 'unverified' so all existing posts are marked as unverified
ALTER TABLE completed_posts
ADD COLUMN verification_status verification_status DEFAULT 'unverified' NOT NULL;

-- Create index for filtering by verification status
CREATE INDEX idx_completed_posts_verification_status ON completed_posts(verification_status);

-- Composite index for finding verified pending posts ready to publish
CREATE INDEX idx_completed_posts_verified_pending ON completed_posts(platform, scheduled_posting_time)
    WHERE status = 'pending' AND verification_status = 'verified';

COMMENT ON COLUMN completed_posts.verification_status IS 'Content verification status: unverified (not yet checked), verified (approved), rejected (failed verification)';
