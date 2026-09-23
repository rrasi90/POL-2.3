-- ============================================================================
-- POL Migration 024
-- Runtime bug-fix guards from the 2026-09-16 project-wide audit.
-- ============================================================================

ALTER TABLE refunds
    ADD COLUMN IF NOT EXISTS completed_by_user_id UUID REFERENCES users(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_refunds_completed_by
    ON refunds(completed_by_user_id, completed_at);

ALTER TABLE outbox_events
    ADD COLUMN IF NOT EXISTS last_error TEXT;

ALTER TABLE outbox_events DROP CONSTRAINT IF EXISTS outbox_events_status_check;
ALTER TABLE outbox_events DROP CONSTRAINT IF EXISTS outbox_status_check;
ALTER TABLE outbox_events DROP CONSTRAINT IF EXISTS chk_outbox_status;
ALTER TABLE outbox_events
    ADD CONSTRAINT outbox_events_status_canonical_check
    CHECK (status IN ('PENDING', 'PUBLISHED', 'FAILED'));

CREATE INDEX IF NOT EXISTS idx_outbox_failed
    ON outbox_events(status, created_at)
    WHERE status = 'FAILED';

CREATE INDEX IF NOT EXISTS idx_order_items_order_vendor_product
    ON order_items(order_id, vendor_product_id);

CREATE UNIQUE INDEX IF NOT EXISTS uq_return_items_return_order_item
    ON return_items(return_id, order_item_id);

-- Reusing a checkout idempotency key with a materially different payload must
-- be rejected rather than silently replaying the previous order group.
ALTER TABLE order_groups
    ADD COLUMN IF NOT EXISTS checkout_request_fingerprint VARCHAR(64);

CREATE INDEX IF NOT EXISTS idx_order_groups_checkout_fingerprint
    ON order_groups(checkout_idempotency_key, checkout_request_fingerprint);
