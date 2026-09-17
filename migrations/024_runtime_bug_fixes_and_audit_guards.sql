-- ============================================================================
-- POL Migration 024
-- Runtime bug-fix guards from the 2026-09-16 project-wide audit.
-- ============================================================================

-- RMA refund separation of duties: the actor who completes the refund must be
-- auditable and must be distinct from the approver.
ALTER TABLE refunds
    ADD COLUMN IF NOT EXISTS completed_by_user_id UUID REFERENCES users(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_refunds_completed_by
    ON refunds(completed_by_user_id, completed_at);

-- Outbox unsupported-event quarantine requires an explicit terminal failure
-- state and an operator-visible reason. Existing deployments may use any of
-- the historical constraint names, so remove them defensively before adding
-- the canonical status constraint.
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

-- Preserve the D-014 aggregate rule at data level: every order is owned by one
-- vendor, while individual order-items remain separately addressable.
CREATE INDEX IF NOT EXISTS idx_order_items_order_vendor_product
    ON order_items(order_id, vendor_product_id);

-- A return may contain each source order item at most once. The application
-- service also aggregates duplicate request lines before validation.
CREATE UNIQUE INDEX IF NOT EXISTS uq_return_items_return_order_item
    ON return_items(return_id, order_item_id);
