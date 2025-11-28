-- Migration 020: Migrate existing data to penndailybuzz business asset
-- This migration creates the default business asset and assigns all existing data to it

-- Step 1: Insert penndailybuzz as the default business asset
-- Note: The tokens will need to be populated separately using the upload script
-- For now, we'll use placeholder values that must be updated
INSERT INTO business_assets (
    id,
    name,
    facebook_page_id,
    app_users_instagram_account_id,
    facebook_page_access_token_encrypted,
    instagram_page_access_token_encrypted,
    is_active,
    created_at,
    updated_at
) VALUES (
    'penndailybuzz',
    'Penn Daily Buzz',
    'PLACEHOLDER_FB_PAGE_ID',  -- To be updated via upload script
    'PLACEHOLDER_IG_ACCOUNT_ID',  -- To be updated via upload script
    'PLACEHOLDER_FB_TOKEN',  -- To be updated via upload script
    'PLACEHOLDER_IG_TOKEN',  -- To be updated via upload script
    TRUE,
    NOW(),
    NOW()
) ON CONFLICT (id) DO NOTHING;

-- Step 2: Update all existing records to use penndailybuzz as their business_asset_id

UPDATE completed_posts
SET business_asset_id = 'penndailybuzz'
WHERE business_asset_id IS NULL;

UPDATE content_creation_tasks
SET business_asset_id = 'penndailybuzz'
WHERE business_asset_id IS NULL;

UPDATE media
SET business_asset_id = 'penndailybuzz'
WHERE business_asset_id IS NULL;

UPDATE news_event_seeds
SET business_asset_id = 'penndailybuzz'
WHERE business_asset_id IS NULL;

UPDATE trend_seeds
SET business_asset_id = 'penndailybuzz'
WHERE business_asset_id IS NULL;

UPDATE ungrounded_seeds
SET business_asset_id = 'penndailybuzz'
WHERE business_asset_id IS NULL;

UPDATE insight_reports
SET business_asset_id = 'penndailybuzz'
WHERE business_asset_id IS NULL;

UPDATE planner_outputs
SET business_asset_id = 'penndailybuzz'
WHERE business_asset_id IS NULL;

UPDATE platform_comments
SET business_asset_id = 'penndailybuzz'
WHERE business_asset_id IS NULL;

-- Step 3: Make business_asset_id NOT NULL now that all records have been migrated

ALTER TABLE completed_posts
ALTER COLUMN business_asset_id SET NOT NULL;

ALTER TABLE content_creation_tasks
ALTER COLUMN business_asset_id SET NOT NULL;

ALTER TABLE media
ALTER COLUMN business_asset_id SET NOT NULL;

ALTER TABLE news_event_seeds
ALTER COLUMN business_asset_id SET NOT NULL;

ALTER TABLE trend_seeds
ALTER COLUMN business_asset_id SET NOT NULL;

ALTER TABLE ungrounded_seeds
ALTER COLUMN business_asset_id SET NOT NULL;

ALTER TABLE insight_reports
ALTER COLUMN business_asset_id SET NOT NULL;

ALTER TABLE planner_outputs
ALTER COLUMN business_asset_id SET NOT NULL;

ALTER TABLE platform_comments
ALTER COLUMN business_asset_id SET NOT NULL;

-- Add comment
COMMENT ON TABLE business_assets IS 'After migration, run scripts/upload_business_assets.py to populate actual encrypted credentials';
