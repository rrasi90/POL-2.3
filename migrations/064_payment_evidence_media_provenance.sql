-- 064: Payment evidence media provenance.
ALTER TABLE payment_evidence
    ADD COLUMN IF NOT EXISTS evidence_media_id UUID REFERENCES media_assets(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_payment_evidence_media_v064
    ON payment_evidence(evidence_media_id)
    WHERE evidence_media_id IS NOT NULL;

CREATE OR REPLACE FUNCTION pol_validate_payment_evidence_media_v064()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    asset RECORD;
    payment_order_id UUID;
BEGIN
    SELECT p.order_id
      INTO payment_order_id
      FROM payments p
     WHERE p.id = NEW.payment_id;

    IF NEW.evidence_type = 'RECEIPT_IMAGE' AND NEW.evidence_media_id IS NULL THEN
        RAISE EXCEPTION 'RECEIPT_IMAGE_REQUIRES_MEDIA'
            USING ERRCODE = '23514';
    END IF;

    IF NEW.evidence_media_id IS NOT NULL THEN
        SELECT *
          INTO asset
          FROM media_assets
         WHERE id = NEW.evidence_media_id
         FOR SHARE;

        IF NOT FOUND THEN
            RAISE EXCEPTION 'PAYMENT_EVIDENCE_MEDIA_NOT_FOUND'
                USING ERRCODE = '23514';
        END IF;

        IF asset.status <> 'READY' THEN
            RAISE EXCEPTION 'PAYMENT_EVIDENCE_MEDIA_NOT_READY'
                USING ERRCODE = '23514';
        END IF;

        IF NEW.captured_by_user_id IS NOT NULL
           AND asset.uploaded_by_user_id <> NEW.captured_by_user_id THEN
            RAISE EXCEPTION 'PAYMENT_EVIDENCE_MEDIA_OWNER_MISMATCH'
                USING ERRCODE = '23514';
        END IF;

        IF upper(COALESCE(asset.upload_target_type,'')) = 'ORDER'
           AND asset.upload_target_id IS NOT NULL
           AND asset.upload_target_id::text <> payment_order_id::text THEN
            RAISE EXCEPTION 'PAYMENT_EVIDENCE_MEDIA_ORDER_MISMATCH'
                USING ERRCODE = '23514';
        END IF;

        IF upper(COALESCE(asset.upload_target_type,'')) NOT IN ('ORDER','PAYMENT','') THEN
            RAISE EXCEPTION 'PAYMENT_EVIDENCE_MEDIA_PURPOSE_INVALID'
                USING ERRCODE = '23514';
        END IF;
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_validate_payment_evidence_media_v064 ON payment_evidence;
CREATE TRIGGER trg_validate_payment_evidence_media_v064
BEFORE INSERT OR UPDATE OF evidence_media_id, payment_id, evidence_type, captured_by_user_id
ON payment_evidence
FOR EACH ROW
EXECUTE FUNCTION pol_validate_payment_evidence_media_v064();
