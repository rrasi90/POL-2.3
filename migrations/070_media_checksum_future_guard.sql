-- 070: Canonical checksum invariant.
-- Historical rows may retain NULL for forensic/reconciliation compatibility;
-- all new and updated READY assets must carry a valid SHA-256 fingerprint.
ALTER TABLE media_assets
    DROP CONSTRAINT IF EXISTS chk_media_asset_checksum_required_v070;

ALTER TABLE media_assets
    ADD CONSTRAINT chk_media_asset_checksum_required_v070
    CHECK (
        status <> 'READY'
        OR (checksum_sha256 IS NOT NULL AND checksum_sha256 ~ '^[0-9a-f]{64}$')
    )
    NOT VALID;
