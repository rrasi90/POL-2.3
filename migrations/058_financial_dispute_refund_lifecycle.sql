-- 058: Financial dispute/refund lifecycle hardening
-- Forward-only remediation. Safe on fresh databases and existing installations
-- where the new columns/indexes are additive.

ALTER TABLE disputes
    ADD COLUMN IF NOT EXISTS idempotency_key VARCHAR(128),
    ADD COLUMN IF NOT EXISTS created_by_user_id UUID REFERENCES users(id);

CREATE UNIQUE INDEX IF NOT EXISTS uq_dispute_idempotency_key
    ON disputes(idempotency_key)
    WHERE idempotency_key IS NOT NULL;

CREATE TABLE IF NOT EXISTS dispute_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dispute_id UUID NOT NULL REFERENCES disputes(id) ON DELETE CASCADE,
    from_status VARCHAR(30),
    to_status VARCHAR(30) NOT NULL,
    actor_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    actor_organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    reason TEXT,
    event_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_dispute_events_dispute_created
    ON dispute_events(dispute_id, created_at ASC);

CREATE OR REPLACE FUNCTION pol_guard_dispute_events_append_only_v058()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'dispute_events is append-only and cannot be updated or deleted'
        USING ERRCODE = '55000';
END;
$$;

DROP TRIGGER IF EXISTS trg_dispute_events_append_only_v058 ON dispute_events;
CREATE TRIGGER trg_dispute_events_append_only_v058
BEFORE UPDATE OR DELETE ON dispute_events
FOR EACH ROW EXECUTE FUNCTION pol_guard_dispute_events_append_only_v058();

CREATE TABLE IF NOT EXISTS dispute_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dispute_id UUID NOT NULL REFERENCES disputes(id) ON DELETE CASCADE,
    order_item_id UUID NOT NULL REFERENCES order_items(id) ON DELETE RESTRICT,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    claimed_amount_toman BIGINT NOT NULL CHECK (claimed_amount_toman > 0),
    reason_code VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_dispute_item UNIQUE (dispute_id, order_item_id)
);

ALTER TABLE disputes
    ADD CONSTRAINT chk_dispute_approved_amount_v058
    CHECK (approved_amount_toman IS NULL OR approved_amount_toman >= 0);

ALTER TABLE refunds
    ADD COLUMN IF NOT EXISTS idempotency_key VARCHAR(128),
    ADD COLUMN IF NOT EXISTS approved_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS completed_by_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS source_type VARCHAR(30) NOT NULL DEFAULT 'DISPUTE';

CREATE UNIQUE INDEX IF NOT EXISTS uq_refund_idempotency_key
    ON refunds(idempotency_key)
    WHERE idempotency_key IS NOT NULL;

ALTER TABLE settlement_adjustments
    ADD COLUMN IF NOT EXISTS refund_id UUID REFERENCES refunds(id) ON DELETE SET NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_refund_settlement_adjustment_v058
    ON settlement_adjustments(refund_id)
    WHERE refund_id IS NOT NULL;

ALTER TABLE settlement_adjustments
    DROP CONSTRAINT IF EXISTS settlement_adjustments_adjustment_type_check;

ALTER TABLE settlement_adjustments
    ADD CONSTRAINT settlement_adjustments_adjustment_type_check_v058
    CHECK (adjustment_type IN (
        'SHORTAGE_DEDUCTION','DAMAGE_COMPENSATION','PRICE_CORRECTION',
        'SLA_PENALTY','PROMOTION_CREDIT','REFUND'
    ));

CREATE OR REPLACE FUNCTION pol_guard_new_dispute_evidence_v058()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.evidence_media_id IS NULL THEN
        RAISE EXCEPTION 'DISPUTE_EVIDENCE_REQUIRED'
            USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_new_dispute_evidence_v058 ON disputes;
CREATE TRIGGER trg_new_dispute_evidence_v058
BEFORE INSERT ON disputes
FOR EACH ROW EXECUTE FUNCTION pol_guard_new_dispute_evidence_v058();

CREATE OR REPLACE FUNCTION pol_guard_completed_refund_payment_v058()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.status = 'COMPLETED' AND NEW.payment_id IS NULL THEN
        RAISE EXCEPTION 'COMPLETED_REFUND_REQUIRES_PAYMENT'
            USING ERRCODE = '23514';
    END IF;
    IF NEW.status = 'COMPLETED' AND NEW.completed_by_user_id IS NULL THEN
        RAISE EXCEPTION 'COMPLETED_REFUND_REQUIRES_ACTOR'
            USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_completed_refund_payment_v058 ON refunds;
CREATE TRIGGER trg_completed_refund_payment_v058
BEFORE INSERT OR UPDATE OF status, payment_id, completed_by_user_id ON refunds
FOR EACH ROW EXECUTE FUNCTION pol_guard_completed_refund_payment_v058();
