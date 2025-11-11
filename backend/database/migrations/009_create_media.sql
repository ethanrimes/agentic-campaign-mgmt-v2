-- backend/database/migrations/009_create_media.sql
-- Generated images and videos

CREATE TYPE media_type AS ENUM ('image', 'video');

CREATE TABLE IF NOT EXISTS media (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    media_type media_type NOT NULL,
    storage_path TEXT NOT NULL UNIQUE,
    public_url TEXT NOT NULL,

    -- Generation metadata
    prompt TEXT,
    input_image_url TEXT,  -- For I2V models
    model TEXT,

    -- Dimensions and file info
    width INTEGER,
    height INTEGER,
    duration REAL,  -- For videos (seconds)
    file_size INTEGER,  -- Bytes
    mime_type TEXT NOT NULL,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Constraints
    CONSTRAINT non_empty_storage_path CHECK (LENGTH(TRIM(storage_path)) > 0),
    CONSTRAINT non_empty_public_url CHECK (LENGTH(TRIM(public_url)) > 0),
    CONSTRAINT valid_dimensions CHECK (
        (width IS NULL AND height IS NULL) OR (width > 0 AND height > 0)
    ),
    CONSTRAINT valid_duration CHECK (duration IS NULL OR duration > 0),
    CONSTRAINT valid_file_size CHECK (file_size IS NULL OR file_size > 0)
);

-- Indexes
CREATE INDEX idx_media_type ON media(media_type);
CREATE INDEX idx_media_created_at ON media(created_at DESC);
CREATE INDEX idx_media_model ON media(model);

COMMENT ON TABLE media IS 'Generated images and videos stored in Supabase storage';
COMMENT ON COLUMN media.storage_path IS 'Path in Supabase storage bucket';
COMMENT ON COLUMN media.public_url IS 'Public URL for accessing the media';
COMMENT ON COLUMN media.duration IS 'Video duration in seconds';
