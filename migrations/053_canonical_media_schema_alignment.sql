-- ============================================================================
-- POL Migration 053
-- Deep-audit remediation: G-316
-- Align runtime media schema with canonical product-media governance fields.
-- ============================================================================

ALTER TABLE media_assets
    ADD COLUMN IF NOT EXISTS bucket_name VARCHAR(100),
    ADD COLUMN IF NOT EXISTS object_key VARCHAR(500);

UPDATE media_assets
SET bucket_name = COALESCE(bucket_name, storage_bucket),
    object_key = COALESCE(object_key, storage_key)
WHERE bucket_name IS NULL OR object_key IS NULL;

ALTER TABLE media_assets
    ALTER COLUMN bucket_name SET NOT NULL,
    ALTER COLUMN object_key SET NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_media_assets_object_key
    ON media_assets(object_key);

ALTER TABLE product_media
    ADD COLUMN IF NOT EXISTS media_type VARCHAR(30),
    ADD COLUMN IF NOT EXISTS source_provenance VARCHAR(50),
    ADD COLUMN IF NOT EXISTS approval_status VARCHAR(30),
    ADD COLUMN IF NOT EXISTS approved_by_user_id UUID REFERENCES users(id),
    ADD COLUMN IF NOT EXISTS approved_at TIMESTAMPTZ;

UPDATE product_media pm
SET media_type = COALESCE(pm.media_type, 'PRIMARY_IMAGE'),
    source_provenance = COALESCE(pm.source_provenance, ma.provenance),
    approval_status = COALESCE(pm.approval_status, CASE
        WHEN ma.provenance = 'POL_OWNED' THEN 'APPROVED'
        ELSE 'APPROVED'
    END),
    approved_at = COALESCE(pm.approved_at, pm.created_at)
FROM media_assets ma
WHERE ma.id = pm.media_asset_id;

ALTER TABLE product_media
    ALTER COLUMN media_type SET DEFAULT 'PRIMARY_IMAGE',
    ALTER COLUMN source_provenance SET DEFAULT 'POL_OWNED',
    ALTER COLUMN approval_status SET DEFAULT 'PENDING';

ALTER TABLE product_media
    DROP CONSTRAINT IF EXISTS product_media_media_asset_id_fkey;

ALTER TABLE product_media
    ADD CONSTRAINT product_media_media_asset_id_fkey
    FOREIGN KEY (media_asset_id)
    REFERENCES media_assets(id)
    ON DELETE RESTRICT;

ALTER TABLE product_media
    DROP CONSTRAINT IF EXISTS chk_product_media_approval;

ALTER TABLE product_media
    ADD CONSTRAINT chk_product_media_approval
    CHECK (approval_status IN ('PENDING', 'APPROVED', 'REJECTED', 'PRIVATE_REFERENCE'));

ALTER TABLE product_media
    DROP CONSTRAINT IF EXISTS chk_media_asset_checksum_format;

ALTER TABLE media_assets
    ADD CONSTRAINT chk_media_asset_checksum_format
    CHECK (checksum_sha256 IS NULL OR checksum_sha256 ~ '^[0-9a-f]{64}$');

CREATE OR REPLACE FUNCTION sync_media_storage_aliases()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.storage_bucket := COALESCE(NEW.bucket_name, NEW.storage_bucket);
    NEW.bucket_name := COALESCE(NEW.bucket_name, NEW.storage_bucket);
    NEW.storage_key := COALESCE(NEW.object_key, NEW.storage_key);
    NEW.object_key := COALESCE(NEW.object_key, NEW.storage_key);
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_media_storage_aliases ON media_assets;

CREATE TRIGGER trg_media_storage_aliases
BEFORE INSERT OR UPDATE OF storage_bucket, storage_key, bucket_name, object_key
ON media_assets
FOR EACH ROW
EXECUTE FUNCTION sync_media_storage_aliases();
