-- ============================================================================
-- POL Migration 055
-- Deep-audit remediation: G-320
-- Explicit object-storage reconciliation state for deleted media.
-- ============================================================================

ALTER TABLE media_assets
    ADD COLUMN IF NOT EXISTS storage_deleted_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS storage_delete_attempts INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS storage_delete_error TEXT;

ALTER TABLE media_variants
    ADD COLUMN IF NOT EXISTS storage_deleted_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS storage_delete_attempts INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS storage_delete_error TEXT;

CREATE INDEX IF NOT EXISTS idx_media_assets_storage_reconcile
    ON media_assets(status, storage_deleted_at, storage_delete_attempts)
    WHERE status = 'DELETED';

CREATE INDEX IF NOT EXISTS idx_media_variants_storage_reconcile
    ON media_variants(source_media_asset_id, storage_deleted_at, storage_delete_attempts);
