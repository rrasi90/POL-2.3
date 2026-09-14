-- ============================================================================
-- POL Application Boundary / RMA / Support / Reconciliation / Provider Hardening
-- Migration 011
--
-- Purpose:
--   1. Complete the return/RMA lifecycle without activating escrow or POL custody.
--   2. Add explicit support authorization/auditability.
--   3. Make payment reconciliation worker-safe and idempotent.
--   4. Make external notification-provider delivery attempts auditable and claimable.
--
-- MVP posture remains NON_CUSTODIAL_DIRECT and asset-light.
-- ============================================================================

ALTER TABLE returns
    ADD COLUMN IF NOT EXISTS request_idempotency_key VARCHAR(128),
    ADD COLUMN IF NOT EXISTS initiated_by_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS requested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    ADD COLUMN IF NOT EXISTS approved_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS received_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS inspected_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS approved_refund_amount_toman BIGINT,
    ADD COLUMN IF NOT EXISTS refund_id UUID REFERENCES refunds(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS pickup_delivery_id UUID REFERENCES deliveries(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS resolution_reason TEXT;

ALTER TABLE returns
    DROP CONSTRAINT IF EXISTS returns_status_check;
ALTER TABLE returns
    DROP CONSTRAINT IF EXISTS returns_status_chk;
ALTER TABLE returns
    ADD CONSTRAINT returns_status_canonical_check
    CHECK (status IN (
        'RETURN_REQUESTED', 'APPROVED', 'PICKUP_REQUIRED', 'RETURN_IN_TRANSIT',
        'RECEIVED', 'VENDOR_INSPECTION', 'ACCEPTED', 'REFUND_PENDING',
        'REFUNDED', 'REJECTED', 'CANCELLED', 'CLOSED'
    ));

CREATE UNIQUE INDEX IF NOT EXISTS uq_returns_request_idempotency
    ON returns(request_idempotency_key)
    WHERE request_idempotency_key IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_open_return_per_order
    ON returns(order_id)
    WHERE status IN (
        'RETURN_REQUESTED', 'APPROVED', 'PICKUP_REQUIRED', 'RETURN_IN_TRANSIT',
        'RECEIVED', 'VENDOR_INSPECTION', 'ACCEPTED', 'REFUND_PENDING'
    );

CREATE TABLE IF NOT EXISTS return_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    return_id UUID NOT NULL REFERENCES returns(id) ON DELETE CASCADE,
    order_item_id UUID NOT NULL REFERENCES order_items(id) ON DELETE RESTRICT,
    requested_quantity INTEGER NOT NULL CHECK (requested_quantity > 0),
    received_quantity INTEGER NOT NULL DEFAULT 0 CHECK (received_quantity >= 0),
    accepted_quantity INTEGER NOT NULL DEFAULT 0 CHECK (accepted_quantity >= 0),
    unit_refund_amount_toman BIGINT NOT NULL DEFAULT 0 CHECK (unit_refund_amount_toman >= 0),
    reason_code VARCHAR(32) NOT NULL CHECK (reason_code IN (
        'DAMAGED', 'SHORTAGE', 'WRONG_ITEM', 'QUALITY', 'DELIVERY_ERROR', 'OTHER'
    )),
    inspection_note TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_return_order_item UNIQUE (return_id, order_item_id),
    CONSTRAINT chk_return_item_received_le_requested CHECK (received_quantity <= requested_quantity),
    CONSTRAINT chk_return_item_accepted_le_received CHECK (accepted_quantity <= received_quantity)
);

CREATE TABLE IF NOT EXISTS return_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    return_id UUID NOT NULL REFERENCES returns(id) ON DELETE CASCADE,
    from_status VARCHAR(32),
    to_status VARCHAR(32) NOT NULL,
    actor_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    reason TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_return_events_return_time
    ON return_events(return_id, created_at DESC);

ALTER TABLE support_cases
    ADD COLUMN IF NOT EXISTS created_by_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS closed_by_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS resolution_code VARCHAR(32),
    ADD COLUMN IF NOT EXISTS resolution_note TEXT;

CREATE TABLE IF NOT EXISTS support_case_access_audit (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    support_case_id UUID NOT NULL REFERENCES support_cases(id) ON DELETE CASCADE,
    actor_user_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    action VARCHAR(32) NOT NULL CHECK (action IN (
        'READ', 'CREATE', 'UPDATE', 'ASSIGN', 'MESSAGE', 'INTERNAL_NOTE', 'RESOLVE', 'CLOSE'
    )),
    allowed BOOLEAN NOT NULL,
    reason VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_support_access_audit_case
    ON support_case_access_audit(support_case_id, created_at DESC);

ALTER TABLE payment_reconciliation_cases
    ADD COLUMN IF NOT EXISTS attempt_count INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS last_attempt_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS next_retry_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS worker_lease_id VARCHAR(128),
    ADD COLUMN IF NOT EXISTS worker_lease_until TIMESTAMPTZ;

CREATE UNIQUE INDEX IF NOT EXISTS uq_payment_evidence_external_reference
    ON payment_evidence(external_reference)
    WHERE external_reference IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_payment_reconciliation_worker
    ON payment_reconciliation_cases(status, next_retry_at, opened_at);

CREATE TABLE IF NOT EXISTS payment_reconciliation_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reconciliation_case_id UUID NOT NULL REFERENCES payment_reconciliation_cases(id) ON DELETE CASCADE,
    attempt_number INTEGER NOT NULL,
    evidence_count INTEGER NOT NULL DEFAULT 0,
    observed_amount_toman BIGINT,
    outcome VARCHAR(24) NOT NULL CHECK (outcome IN ('MATCHED', 'PARTIAL', 'MISMATCH', 'NO_EVIDENCE', 'ERROR')),
    provider_reference VARCHAR(255),
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_payment_reconciliation_attempt UNIQUE (reconciliation_case_id, attempt_number)
);

CREATE INDEX IF NOT EXISTS idx_payment_reconciliation_attempts_case
    ON payment_reconciliation_attempts(reconciliation_case_id, created_at DESC);

ALTER TABLE notification_deliveries
    ADD COLUMN IF NOT EXISTS lease_id VARCHAR(128),
    ADD COLUMN IF NOT EXISTS lease_until TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS last_provider_code VARCHAR(64),
    ADD COLUMN IF NOT EXISTS provider_attempt_key VARCHAR(255);

CREATE UNIQUE INDEX IF NOT EXISTS uq_notification_provider_attempt_key
    ON notification_deliveries(provider_attempt_key)
    WHERE provider_attempt_key IS NOT NULL;

CREATE TABLE IF NOT EXISTS notification_provider_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    delivery_id UUID NOT NULL REFERENCES notification_deliveries(id) ON DELETE CASCADE,
    attempt_number INTEGER NOT NULL,
    channel VARCHAR(16) NOT NULL CHECK (channel IN ('PUSH','SMS')),
    provider VARCHAR(64) NOT NULL,
    idempotency_key VARCHAR(255) NOT NULL,
    request_fingerprint VARCHAR(128),
    provider_message_id VARCHAR(255),
    outcome VARCHAR(24) NOT NULL CHECK (outcome IN ('SENT','FAILED','RETRYABLE_FAILURE','PERMANENT_FAILURE','SKIPPED')),
    provider_code VARCHAR(64),
    error_message TEXT,
    response_metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ,
    CONSTRAINT uq_notification_provider_attempt UNIQUE (delivery_id, attempt_number),
    CONSTRAINT uq_notification_provider_idempotency UNIQUE (idempotency_key)
);

CREATE INDEX IF NOT EXISTS idx_notification_provider_attempts_delivery
    ON notification_provider_attempts(delivery_id, started_at DESC);
