-- Migration 018: Create business_assets table
-- This table stores credentials and metadata for each business asset (Facebook + Instagram page combination)

CREATE TABLE IF NOT EXISTS business_assets (
    -- Use business name as ID (e.g., 'penndailybuzz', 'eaglesnationfanhuddle')
    id TEXT PRIMARY KEY,

    -- Display name for the business asset
    name TEXT NOT NULL,

    -- Meta platform credentials (encrypted)
    -- Note: facebook_page_id and instagram_account_id are not sensitive, but we store them here for consistency
    facebook_page_id TEXT NOT NULL,
    app_users_instagram_account_id TEXT NOT NULL,

    -- Encrypted access tokens (use ENCRYPTION_KEY to encrypt/decrypt)
    facebook_page_access_token_encrypted TEXT NOT NULL,
    instagram_page_access_token_encrypted TEXT NOT NULL,

    -- Status tracking
    is_active BOOLEAN DEFAULT TRUE NOT NULL,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Create index on is_active for efficient filtering of active assets
CREATE INDEX IF NOT EXISTS idx_business_assets_active ON business_assets(is_active);

-- Add comment describing the table
COMMENT ON TABLE business_assets IS 'Stores credentials and metadata for each business asset (Facebook + Instagram page combination). Tokens are encrypted using ENCRYPTION_KEY.';
