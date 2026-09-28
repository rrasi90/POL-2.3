-- Migration: 047_delegated_permissions_and_audit.sql
-- Purpose:
--   Implement D-026 / VD-15 delegated permissions as a tenant-scoped,
--   server-authoritative grant/revoke model with append-only audit.
--   Permission keys are constrained to the canonical Master Tree examples.

CREATE TABLE IF NOT EXISTS delegated_permission_grants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    membership_id UUID NOT NULL REFERENCES organization_memberships(id) ON DELETE CASCADE,
    permission_key VARCHAR(128) NOT NULL,
    status VARCHAR(16) NOT NULL DEFAULT 'GRANTED'
        CHECK (status IN ('GRANTED', 'REVOKED')),
    granted_by_user_id UUID NOT NULL REFERENCES users(id),
    granted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    revoked_by_user_id UUID REFERENCES users(id),
    revoked_at TIMESTAMPTZ,
    reason TEXT,
    CONSTRAINT ck_delegated_permission_revocation
        CHECK (
            (status = 'GRANTED' AND revoked_by_user_id IS NULL AND revoked_at IS NULL)
            OR
            (status = 'REVOKED' AND revoked_by_user_id IS NOT NULL AND revoked_at IS NOT NULL)
        ),
    CONSTRAINT uq_delegated_permission_membership_key
        UNIQUE (membership_id, permission_key),
    CONSTRAINT ck_delegated_permission_key
        CHECK (
            permission_key IN (
                'catalog.view',
                'catalog.manage',
                'inventory.view',
                'inventory.scan',
                'inventory.adjust',
                'price.view',
                'price.manage',
                'order.view',
                'order.accept',
                'order.fulfillment',
                'delivery.dispatch',
                'delivery.handoff',
                'payment.view',
                'payment.record',
                'settlement.view',
                'membership.manage',
                'reports.view'
            )
        )
);

CREATE INDEX IF NOT EXISTS idx_delegated_permission_active
    ON delegated_permission_grants (membership_id, permission_key)
    WHERE status = 'GRANTED';

CREATE TABLE IF NOT EXISTS permission_audit_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    membership_id UUID NOT NULL REFERENCES organization_memberships(id) ON DELETE RESTRICT,
    permission_key VARCHAR(128) NOT NULL
        CHECK (
            permission_key IN (
                'catalog.view',
                'catalog.manage',
                'inventory.view',
                'inventory.scan',
                'inventory.adjust',
                'price.view',
                'price.manage',
                'order.view',
                'order.accept',
                'order.fulfillment',
                'delivery.dispatch',
                'delivery.handoff',
                'payment.view',
                'payment.record',
                'settlement.view',
                'membership.manage',
                'reports.view'
            )
        ),
    action VARCHAR(16) NOT NULL CHECK (action IN ('GRANT', 'REVOKE')),
    actor_user_id UUID NOT NULL REFERENCES users(id),
    reason TEXT,
    client VARCHAR(32),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_permission_audit_membership_created
    ON permission_audit_events (membership_id, created_at DESC);

-- Historical audit is append-only at the database boundary.
CREATE OR REPLACE FUNCTION prevent_permission_audit_mutation()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'permission_audit_events is append-only';
END;
$$;

DROP TRIGGER IF EXISTS trg_permission_audit_no_update ON permission_audit_events;
CREATE TRIGGER trg_permission_audit_no_update
BEFORE UPDATE OR DELETE ON permission_audit_events
FOR EACH ROW
EXECUTE FUNCTION prevent_permission_audit_mutation();
