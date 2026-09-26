-- 067: Financial ceiling and cross-entity provenance for all new/updated refunds.
CREATE OR REPLACE FUNCTION pol_validate_refund_financial_bounds_v067()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    payment_row RECORD;
    approved_award BIGINT;
    other_active BIGINT;
    return_order UUID;
BEGIN
    IF NEW.status IN ('PENDING','APPROVED','COMPLETED') THEN
        IF NEW.payment_id IS NULL THEN
            RAISE EXCEPTION 'ACTIVE_REFUND_REQUIRES_PAYMENT'
                USING ERRCODE = '23514';
        END IF;

        SELECT p.*
          INTO payment_row
          FROM payments p
         WHERE p.id = NEW.payment_id
         FOR SHARE;

        IF NOT FOUND THEN
            RAISE EXCEPTION 'REFUND_PAYMENT_NOT_FOUND'
                USING ERRCODE = '23514';
        END IF;

        IF payment_row.order_id <> NEW.order_id
           OR payment_row.retailer_id <> NEW.retailer_id THEN
            RAISE EXCEPTION 'REFUND_PAYMENT_PROVENANCE_MISMATCH'
                USING ERRCODE = '23514';
        END IF;

        SELECT COALESCE(SUM(r.amount_toman),0)
          INTO other_active
          FROM refunds r
         WHERE r.payment_id = NEW.payment_id
           AND r.id <> NEW.id
           AND r.status IN ('PENDING','APPROVED','COMPLETED');

        IF other_active + NEW.amount_toman > payment_row.amount_toman THEN
            RAISE EXCEPTION 'REFUND_EXCEEDS_PAYMENT_AMOUNT'
                USING ERRCODE = '23514';
        END IF;

        IF NEW.dispute_id IS NOT NULL THEN
            SELECT d.approved_amount_toman
              INTO approved_award
              FROM disputes d
             WHERE d.id = NEW.dispute_id
             FOR SHARE;

            IF NOT FOUND OR NEW.order_id <> (SELECT order_id FROM disputes WHERE id=NEW.dispute_id) THEN
                RAISE EXCEPTION 'REFUND_DISPUTE_PROVENANCE_MISMATCH'
                    USING ERRCODE = '23514';
            END IF;

            IF COALESCE(approved_award,0) <= 0
               OR NEW.amount_toman > approved_award THEN
                RAISE EXCEPTION 'REFUND_EXCEEDS_DISPUTE_AWARD'
                    USING ERRCODE = '23514';
            END IF;
        END IF;

        IF NEW.return_id IS NOT NULL THEN
            SELECT r.order_id, r.approved_refund_amount_toman
              INTO return_order, approved_award
              FROM returns r
             WHERE r.id = NEW.return_id
             FOR SHARE;

            IF NOT FOUND OR return_order <> NEW.order_id THEN
                RAISE EXCEPTION 'REFUND_RETURN_PROVENANCE_MISMATCH'
                    USING ERRCODE = '23514';
            END IF;

            IF COALESCE(approved_award,0) <= 0
               OR NEW.amount_toman > approved_award THEN
                RAISE EXCEPTION 'REFUND_EXCEEDS_RETURN_AWARD'
                    USING ERRCODE = '23514';
            END IF;
        END IF;
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_validate_refund_financial_bounds_v067 ON refunds;
CREATE TRIGGER trg_validate_refund_financial_bounds_v067
BEFORE INSERT OR UPDATE OF order_id, payment_id, dispute_id, return_id,
    retailer_id, amount_toman, status
ON refunds
FOR EACH ROW
EXECUTE FUNCTION pol_validate_refund_financial_bounds_v067();
