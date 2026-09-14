-- ============================================================================
-- POL Migration 019
-- Explicit RMA -> refund linkage and non-zero approved refund invariant.
-- ============================================================================

ALTER TABLE refunds
    ADD COLUMN IF NOT EXISTS return_id UUID REFERENCES returns(id) ON DELETE SET NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_refund_per_return
    ON refunds(return_id)
    WHERE return_id IS NOT NULL;

ALTER TABLE returns
    ADD CONSTRAINT chk_returns_refund_pending_amount
    CHECK (status NOT IN ('REFUND_PENDING','REFUNDED') OR approved_refund_amount_toman IS NOT NULL);
