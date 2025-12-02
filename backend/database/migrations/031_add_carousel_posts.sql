-- Migration: Add carousel_posts column to content_creation_tasks
-- This enables carousel (multi-image) post support in the planner and content creation pipeline

-- Add carousel_posts column to content_creation_tasks table
ALTER TABLE content_creation_tasks
ADD COLUMN IF NOT EXISTS carousel_posts INTEGER DEFAULT 0;

-- Add a comment explaining the column
COMMENT ON COLUMN content_creation_tasks.carousel_posts IS 'Number of carousel posts to create (each creates 1 IG carousel + 1 FB carousel with 2-10 images)';
