-- Migration 041: Allow external (human-posted) content in completed_posts
-- External posts discovered from the Instagram API have no task or content seed.
-- This makes task_id nullable and relaxes the seed constraint from "exactly 1" to "at most 1".

-- Step 1: Make task_id nullable (external posts have no task)
ALTER TABLE completed_posts
ALTER COLUMN task_id DROP NOT NULL;

-- Step 2: Relax seed constraint to allow zero seeds (external posts)
ALTER TABLE completed_posts
DROP CONSTRAINT IF EXISTS content_seed_exclusive_check;

ALTER TABLE completed_posts
ADD CONSTRAINT content_seed_exclusive_check
  CHECK (num_nonnulls(news_event_seed_id, trend_seed_id, ungrounded_seed_id) <= 1);
