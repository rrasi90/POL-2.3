-- ============================================================================
-- POL Migration 054
-- Deep-audit remediation: G-318
-- Resumable media ingestion sessions + trusted derivative variants.
-- ============================================================================

CREATE TABLE IF NOT EXISTS media_upload_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    media_asset_id UUID NOT NULL UNIQUE REFERENCES media_assets(id) ON DELETE CASCADE,
    provider_upload_id VARCHAR(255) NOT NULL UNIQUE,
    part_size_bytes INTEGER NOT NULL CHECK (part_size_bytes BETWEEN 262144 AND 5242880),
    part_count INTEGER NOT NULL CHECK (part_count BETWEEN 1 AND 10000),
    status VARCHAR(16) NOT NULL DEFAULT 'OPEN'
        CHECK (status IN ('OPEN', 'COMPLETED', 'ABORTED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ,
    aborted_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS media_upload_parts (
    session_id UUID NOT NULL REFERENCES media_upload_sessions(id) ON DELETE CASCADE,
    part_number INTEGER NOT NULL CHECK (part_number BETWEEN 1 AND 10000),
    etag VARCHAR(255) NOT NULL,
    size_bytes INTEGER CHECK (size_bytes IS NULL OR size_bytes > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (session_id, part_number)
);

CREATE TABLE IF NOT EXISTS media_variants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_media_asset_id UUID NOT NULL REFERENCES media_assets(id) ON DELETE RESTRICT,
    variant_type VARCHAR(24) NOT NULL CHECK (variant_type IN ('THUMBNAIL', 'DETAIL')),
    storage_bucket VARCHAR(100) NOT NULL,
    storage_key VARCHAR(500) NOT NULL UNIQUE,
    mime_type VARCHAR(50) NOT NULL DEFAULT 'image/webp',
    file_size_bytes INTEGER NOT NULL CHECK (file_size_bytes > 0),
    width INTEGER NOT NULL CHECK (width > 0),
    height INTEGER NOT NULL CHECK (height > 0),
    checksum_sha256 VARCHAR(64) NOT NULL CHECK (checksum_sha256 ~ '^[0-9a-f]{64}$'),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_media_variant_type UNIQUE (source_media_asset_id, variant_type)
);

CREATE INDEX IF NOT EXISTS idx_media_upload_sessions_status
    ON media_upload_sessions(status, created_at);

CREATE INDEX IF NOT EXISTS idx_media_variants_source
    ON media_variants(source_media_asset_id, variant_type);
