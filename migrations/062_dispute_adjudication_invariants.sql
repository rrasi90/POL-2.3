-- 062: Dispute adjudication invariants at the PostgreSQL boundary.
-- Forward-only. Existing historical rows are left untouched; future
-- transitions into RESOLVED/CLOSED are enforced centrally.

CREATE OR REPLACE FUNCTION pol_validate_dispute_adjudication_v062()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    completed_refund BIGINT;
BEGIN
    IF NEW.dispute_status IN ('RESOLVED','CLOSED') THEN
        IF COALESCE(NEW.claimed_amount_toman, 0) <= 0 THEN
            RAISE EXCEPTION 'RESOLVED_DISPUTE_REQUIRES_POSITIVE_CLAIM'
                USING ERRCODE = '23514';
        END IF;

        IF COALESCE(NEW.approved_amount_toman, -1) < 0
           OR NEW.approved_amount_toman > NEW.claimed_amount_toman THEN
            RAISE EXCEPTION 'DISPUTE_APPROVED_AMOUNT_OUT_OF_BOUNDS'
                USING ERRCODE = '23514';
        END IF;

        IF NEW.resolution_outcome IS NULL THEN
            RAISE EXCEPTION 'RESOLVED_DISPUTE_REQUIRES_OUTCOME'
                USING ERRCODE = '23514';
        END IF;

        IF NEW.resolution_outcome = 'REJECTED_CLAIM'
           AND NEW.approved_amount_toman <> 0 THEN
            RAISE EXCEPTION 'REJECTED_DISPUTE_MUST_HAVE_ZERO_AWARD'
                USING ERRCODE = '23514';
        END IF;

        IF NEW.resolution_outcome = 'REPLACEMENT_ORDER'
           AND NEW.approved_amount_toman <> 0 THEN
            RAISE EXCEPTION 'REPLACEMENT_RESOLUTION_MUST_HAVE_ZERO_CASH_AWARD'
                USING ERRCODE = '23514';
        END IF;

        IF NEW.resolution_outcome = 'ADJUSTED_SHORTAGE'
           AND NEW.approved_amount_toman <= 0 THEN
            RAISE EXCEPTION 'ADJUSTED_SHORTAGE_REQUIRES_POSITIVE_AWARD'
                USING ERRCODE = '23514';
        END IF;
    END IF;

    IF NEW.dispute_status = 'CLOSED'
       AND COALESCE(NEW.approved_amount_toman, 0) > 0 THEN
        SELECT COALESCE(SUM(amount_toman),0)
          INTO completed_refund
        FROM refunds
        WHERE dispute_id = NEW.id
          AND status = 'COMPLETED';

        IF completed_refund <> NEW.approved_amount_toman THEN
            RAISE EXCEPTION 'CLOSED_DISPUTE_REFUND_TOTAL_MUST_MATCH_AWARD'
                USING ERRCODE = '23514';
        END IF;
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_validate_dispute_adjudication_v062 ON disputes;
CREATE TRIGGER trg_validate_dispute_adjudication_v062
BEFORE INSERT OR UPDATE OF dispute_status, resolution_outcome,
    approved_amount_toman, claimed_amount_toman
ON disputes
FOR EACH ROW
EXECUTE FUNCTION pol_validate_dispute_adjudication_v062();

CREATE INDEX IF NOT EXISTS idx_disputes_order_status_v062
    ON disputes(order_id, dispute_status, created_at DESC);
