-- 065: Order-scoped media authorization is required for pre-created
-- dispute/payment evidence whose final child aggregate is not created yet.

ALTER TABLE media_assets
    DROP CONSTRAINT IF EXISTS ck_media_upload_target_type;

ALTER TABLE media_assets
    ADD CONSTRAINT ck_media_upload_target_type
    CHECK (
        upload_target_type IS NULL
        OR upload_target_type IN (
            'PRODUCT','VENDOR','CANDIDATE','ORDER','DISPUTE',
            'DELIVERY','PAYMENT','SUPPORT'
        )
    );
