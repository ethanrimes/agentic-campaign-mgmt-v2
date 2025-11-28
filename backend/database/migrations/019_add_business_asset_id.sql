-- Migration 019: Add business_asset_id to all tables
-- This migration adds business_asset_id foreign key to all tables to support multi-tenancy

-- Add business_asset_id to completed_posts
ALTER TABLE completed_posts
ADD COLUMN business_asset_id TEXT REFERENCES business_assets(id);

CREATE INDEX IF NOT EXISTS idx_completed_posts_business_asset ON completed_posts(business_asset_id);

-- Add business_asset_id to content_creation_tasks
ALTER TABLE content_creation_tasks
ADD COLUMN business_asset_id TEXT REFERENCES business_assets(id);

CREATE INDEX IF NOT EXISTS idx_content_creation_tasks_business_asset ON content_creation_tasks(business_asset_id);

-- Add business_asset_id to media
ALTER TABLE media
ADD COLUMN business_asset_id TEXT REFERENCES business_assets(id);

CREATE INDEX IF NOT EXISTS idx_media_business_asset ON media(business_asset_id);

-- Add business_asset_id to news_event_seeds
ALTER TABLE news_event_seeds
ADD COLUMN business_asset_id TEXT REFERENCES business_assets(id);

CREATE INDEX IF NOT EXISTS idx_news_event_seeds_business_asset ON news_event_seeds(business_asset_id);

-- Add business_asset_id to trend_seeds
ALTER TABLE trend_seeds
ADD COLUMN business_asset_id TEXT REFERENCES business_assets(id);

CREATE INDEX IF NOT EXISTS idx_trend_seeds_business_asset ON trend_seeds(business_asset_id);

-- Add business_asset_id to ungrounded_seeds
ALTER TABLE ungrounded_seeds
ADD COLUMN business_asset_id TEXT REFERENCES business_assets(id);

CREATE INDEX IF NOT EXISTS idx_ungrounded_seeds_business_asset ON ungrounded_seeds(business_asset_id);

-- Add business_asset_id to insight_reports
ALTER TABLE insight_reports
ADD COLUMN business_asset_id TEXT REFERENCES business_assets(id);

CREATE INDEX IF NOT EXISTS idx_insight_reports_business_asset ON insight_reports(business_asset_id);

-- Add business_asset_id to planner_outputs
ALTER TABLE planner_outputs
ADD COLUMN business_asset_id TEXT REFERENCES business_assets(id);

CREATE INDEX IF NOT EXISTS idx_planner_outputs_business_asset ON planner_outputs(business_asset_id);

-- Add business_asset_id to platform_comments
ALTER TABLE platform_comments
ADD COLUMN business_asset_id TEXT REFERENCES business_assets(id);

CREATE INDEX IF NOT EXISTS idx_platform_comments_business_asset ON platform_comments(business_asset_id);

-- Add comments explaining the purpose
COMMENT ON COLUMN completed_posts.business_asset_id IS 'References the business asset this post belongs to';
COMMENT ON COLUMN content_creation_tasks.business_asset_id IS 'References the business asset this task belongs to';
COMMENT ON COLUMN media.business_asset_id IS 'References the business asset this media belongs to';
COMMENT ON COLUMN news_event_seeds.business_asset_id IS 'References the business asset this seed belongs to';
COMMENT ON COLUMN trend_seeds.business_asset_id IS 'References the business asset this seed belongs to';
COMMENT ON COLUMN ungrounded_seeds.business_asset_id IS 'References the business asset this seed belongs to';
COMMENT ON COLUMN insight_reports.business_asset_id IS 'References the business asset this report belongs to';
COMMENT ON COLUMN planner_outputs.business_asset_id IS 'References the business asset this planner output belongs to';
COMMENT ON COLUMN platform_comments.business_asset_id IS 'References the business asset this comment belongs to';
