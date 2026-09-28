-- 059: Refund creator provenance for canonical separation of duties.
ALTER TABLE refunds
    ADD COLUMN IF NOT EXISTS created_by_user_id UUID REFERENCES users(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_refunds_order_status_v059
    ON refunds(order_id, status, created_at DESC);
