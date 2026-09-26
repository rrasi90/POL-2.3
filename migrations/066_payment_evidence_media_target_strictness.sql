-- 066: Payment evidence media must be explicitly bound to its aggregate.
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

        IF upper(COALESCE(asset.upload_target_type,'')) = 'ORDER' THEN
            IF asset.upload_target_id IS NULL
               OR asset.upload_target_id::text <> payment_order_id::text THEN
                RAISE EXCEPTION 'PAYMENT_EVIDENCE_MEDIA_ORDER_MISMATCH'
                    USING ERRCODE = '23514';
            END IF;
        ELSIF upper(COALESCE(asset.upload_target_type,'')) = 'PAYMENT' THEN
            IF asset.upload_target_id IS NULL
               OR asset.upload_target_id::text <> NEW.payment_id::text THEN
                RAISE EXCEPTION 'PAYMENT_EVIDENCE_MEDIA_PAYMENT_MISMATCH'
                    USING ERRCODE = '23514';
            END IF;
        ELSE
            RAISE EXCEPTION 'PAYMENT_EVIDENCE_MEDIA_PURPOSE_INVALID'
                USING ERRCODE = '23514';
        END IF;
    END IF;

    RETURN NEW;
END;
$$;
