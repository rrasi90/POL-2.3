-- Migration: 048_bind_media_upload_target.sql
-- Purpose:
--   Bind a presigned upload to the target it was authorized for so confirm-upload
--   cannot retarget the trusted derivative to another object.

ALTER TABLE media_assets
    ADD COLUMN IF NOT EXISTS upload_target_type VARCHAR(30),
    ADD COLUMN IF NOT EXISTS upload_target_id UUID;

ALTER TABLE media_assets
    DROP CONSTRAINT IF EXISTS ck_media_upload_target_type;

ALTER TABLE media_assets
    ADD CONSTRAINT ck_media_upload_target_type
    CHECK (
        upload_target_type IS NULL
        OR upload_target_type IN (
            'PRODUCT','VENDOR','CANDIDATE','DISPUTE','DELIVERY','PAYMENT','SUPPORT'
        )
    );

CREATE INDEX IF NOT EXISTS idx_media_assets_upload_target
    ON media_assets (upload_target_type, upload_target_id)
    WHERE upload_target_type IS NOT NULL AND upload_target_id IS NOT NULL;


-- Any legacy in-flight upload created before target binding existed is not safely
-- confirmable because its authorization intent cannot be reconstructed. Fail closed
-- by invalidating such orphaned rows before enforcing the new invariant.
UPDATE media_assets
SET status = 'DELETED'
WHERE status = 'UPLOADING'
  AND (upload_target_type IS NULL OR upload_target_id IS NULL);

ALTER TABLE media_assets
    DROP CONSTRAINT IF EXISTS ck_media_upload_target_required;

ALTER TABLE media_assets
    ADD CONSTRAINT ck_media_upload_target_required
    CHECK (
        status <> 'UPLOADING'
        OR (upload_target_type IS NOT NULL AND upload_target_id IS NOT NULL)
    );
