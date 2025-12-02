-- Migration: Add verification groups for cross-platform media sharing optimization
-- When media is shared across platforms (Instagram + Facebook), we group posts together
-- to avoid duplicate verification processing. Only "primary" posts are verified,
-- and the result propagates to all posts in the same verification group.

-- Add verification group columns to completed_posts
ALTER TABLE completed_posts
ADD COLUMN IF NOT EXISTS verification_group_id UUID,
ADD COLUMN IF NOT EXISTS is_verification_primary BOOLEAN NOT NULL DEFAULT TRUE;

-- Create index for efficient group lookups
CREATE INDEX IF NOT EXISTS idx_completed_posts_verification_group_id
ON completed_posts(verification_group_id)
WHERE verification_group_id IS NOT NULL;

-- Index for finding primary posts that need verification
CREATE INDEX IF NOT EXISTS idx_completed_posts_verification_primary
ON completed_posts(is_verification_primary, verification_status)
WHERE is_verification_primary = TRUE;

-- Modify verifier_responses to reference verification_group_id instead of completed_post_id
-- First, add the new column
ALTER TABLE verifier_responses
ADD COLUMN IF NOT EXISTS verification_group_id UUID;

-- Create index on the new column
CREATE INDEX IF NOT EXISTS idx_verifier_responses_verification_group_id
ON verifier_responses(verification_group_id)
WHERE verification_group_id IS NOT NULL;

-- Add comments explaining the schema
COMMENT ON COLUMN completed_posts.verification_group_id IS 'Groups posts that share media for unified verification. NULL means standalone post (group size = 1)';
COMMENT ON COLUMN completed_posts.is_verification_primary IS 'TRUE = this post will be verified. FALSE = inherits verification from primary post in group';
COMMENT ON COLUMN verifier_responses.verification_group_id IS 'Links to verification group. When set, applies to all posts in the group';

-- Note: Existing completed_posts will have:
--   verification_group_id = NULL (standalone, no group)
--   is_verification_primary = TRUE (default, will be verified individually)
-- This maintains backwards compatibility with existing data.

-- For new shared-media posts:
--   - Instagram post: is_verification_primary = TRUE, verification_group_id = <new UUID>
--   - Facebook post: is_verification_primary = FALSE, verification_group_id = <same UUID>
--   - When verifier runs, it only processes primary posts
--   - After verification, update verification_status for ALL posts with matching verification_group_id
