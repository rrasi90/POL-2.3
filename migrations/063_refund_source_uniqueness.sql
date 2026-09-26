-- 063: The prior remediation briefly enforced one active refund per order.
-- That was too strict for multiple legitimate return/refund sources on one order.
-- Canonical identity is one refund per dispute or one refund per return.

DROP INDEX IF EXISTS uq_active_refund_per_order_v058;

CREATE UNIQUE INDEX IF NOT EXISTS uq_refund_per_dispute_v063
    ON refunds(dispute_id)
    WHERE dispute_id IS NOT NULL
      AND status IN ('PENDING','APPROVED','COMPLETED');

CREATE UNIQUE INDEX IF NOT EXISTS uq_refund_per_return_v063
    ON refunds(return_id)
    WHERE return_id IS NOT NULL
      AND status IN ('PENDING','APPROVED','COMPLETED');

ALTER TABLE refunds
    DROP CONSTRAINT IF EXISTS chk_refund_source_consistency_v063;

ALTER TABLE refunds
    ADD CONSTRAINT chk_refund_source_consistency_v063
    CHECK (
        (source_type = 'DISPUTE' AND dispute_id IS NOT NULL)
        OR
        (source_type = 'RMA' AND return_id IS NOT NULL)
    );
