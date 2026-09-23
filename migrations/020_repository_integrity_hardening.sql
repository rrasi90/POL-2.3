-- ============================================================================
-- POL Migration 020
-- Repository-wide integrity hardening discovered in the 2026-09-16 audit.
-- No new tables; strengthens temporal, consent, saved-list and RMA invariants.
-- ============================================================================

-- 1. Operating windows must support real overnight business hours such as
--    22:00-02:00. The previous closes_at > opens_at check contradicted the
--    application policy, which already implements cross-midnight windows.
ALTER TABLE vendor_operating_windows
    DROP CONSTRAINT IF EXISTS chk_vendor_window_order;

ALTER TABLE vendor_operating_windows
    ADD CONSTRAINT chk_vendor_window_order
    CHECK (opens_at <> closes_at);

-- Prevent overlapping effective configurations for the same vendor/day.
ALTER TABLE vendor_operating_windows
    DROP CONSTRAINT IF EXISTS ex_vendor_operating_window_no_overlap;

ALTER TABLE vendor_operating_windows
    ADD CONSTRAINT ex_vendor_operating_window_no_overlap
    EXCLUDE USING gist (
        vendor_id WITH =,
        weekday WITH =,
        tstzrange(effective_from, COALESCE(effective_until, 'infinity'::timestamptz), '[)') WITH &&
    );

-- 2. Capacity profiles are temporal configurations too; overlapping active
--    periods make "current capacity" nondeterministic.
ALTER TABLE vendor_capacity_profiles
    DROP CONSTRAINT IF EXISTS ex_vendor_capacity_profile_no_overlap;

ALTER TABLE vendor_capacity_profiles
    ADD CONSTRAINT ex_vendor_capacity_profile_no_overlap
    EXCLUDE USING gist (
        vendor_id WITH =,
        tstzrange(effective_from, COALESCE(effective_until, 'infinity'::timestamptz), '[)') WITH &&
    );

-- 3. A retailer may have only one default saved/reorder list.
CREATE UNIQUE INDEX IF NOT EXISTS uq_retailer_default_saved_list
    ON retailer_saved_lists(retailer_id)
    WHERE is_default = TRUE;

-- 4. PostgreSQL NULL semantics otherwise permit multiple global consents for
--    the same user/type. Keep one active global consent and one per tenant.
CREATE UNIQUE INDEX IF NOT EXISTS uq_active_global_consent
    ON data_consents(user_id, consent_type)
    WHERE status = 'GRANTED' AND organization_id IS NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_active_tenant_consent
    ON data_consents(user_id, organization_id, consent_type)
    WHERE status = 'GRANTED' AND organization_id IS NOT NULL;

-- 5. RMA states REFUND_PENDING/REFUNDED require a positive approved amount.
--    Service-level validation already requires this; the database now enforces
--    the same invariant for direct writes.
ALTER TABLE returns
    DROP CONSTRAINT IF EXISTS chk_returns_refund_pending_amount;

ALTER TABLE returns
    ADD CONSTRAINT chk_returns_refund_pending_amount
    CHECK (
        status NOT IN ('REFUND_PENDING', 'REFUNDED')
        OR approved_refund_amount_toman > 0
    );
