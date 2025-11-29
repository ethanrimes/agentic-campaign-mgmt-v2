-- Delete orphaned content_creation_tasks that reference non-existent seeds
-- This should be run BEFORE applying migration 023

-- Delete tasks with orphaned news_event seeds
DELETE FROM content_creation_tasks AS t
WHERE t.content_seed_type = 'news_event'
  AND NOT EXISTS (
      SELECT 1 FROM news_event_seeds n
      WHERE n.id = t.content_seed_id
        AND n.business_asset_id = t.business_asset_id
  );

-- Delete tasks with orphaned trend seeds
DELETE FROM content_creation_tasks AS t
WHERE t.content_seed_type = 'trend'
  AND NOT EXISTS (
      SELECT 1 FROM trend_seeds ts
      WHERE ts.id = t.content_seed_id
        AND ts.business_asset_id = t.business_asset_id
  );

-- Delete tasks with orphaned ungrounded seeds
DELETE FROM content_creation_tasks AS t
WHERE t.content_seed_type = 'ungrounded'
  AND NOT EXISTS (
      SELECT 1 FROM ungrounded_seeds u
      WHERE u.id = t.content_seed_id
        AND u.business_asset_id = t.business_asset_id
  );
