-- ============================================================================
-- POL MVP Vendor Referral + Cross-Domain Integrity Hardening
-- Migration 012
-- ============================================================================

-- --------------------------------------------------------------------------
-- 1. Vendor Referral is an ACTIVE MVP capability.
--    The pilot uses attribution only; no monetary referral reward is activated.
-- --------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS vendor_referrals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vendor_id UUID NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
    referral_code VARCHAR(32) NOT NULL,
    status VARCHAR(16) NOT NULL DEFAULT 'ACTIVE'
        CHECK (status IN ('ACTIVE', 'PAUSED', 'EXPIRED')),
    max_redemptions INTEGER CHECK (max_redemptions IS NULL OR max_redemptions > 0),
    redemption_count INTEGER NOT NULL DEFAULT 0 CHECK (redemption_count >= 0),
    expires_at TIMESTAMPTZ,
    created_by_user_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_vendor_referral_code UNIQUE (referral_code)
);

CREATE INDEX IF NOT EXISTS idx_vendor_referrals_vendor_status
    ON vendor_referrals(vendor_id, status);

CREATE TABLE IF NOT EXISTS vendor_referral_attributions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    referral_id UUID NOT NULL REFERENCES vendor_referrals(id) ON DELETE RESTRICT,
    vendor_id UUID NOT NULL REFERENCES vendors(id) ON DELETE RESTRICT,
    retailer_id UUID NOT NULL REFERENCES retailers(id) ON DELETE RESTRICT,
    referred_user_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    status VARCHAR(16) NOT NULL DEFAULT 'ATTRIBUTED'
        CHECK (status IN ('ATTRIBUTED', 'ACTIVATED', 'CONVERTED', 'REVOKED')),
    request_idempotency_key VARCHAR(128),
    first_order_id UUID REFERENCES orders(id) ON DELETE SET NULL,
    attributed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    activated_at TIMESTAMPTZ,
    converted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_referral_retailer_first_touch UNIQUE (retailer_id),
    CONSTRAINT uq_referral_attribution_idempotency UNIQUE (request_idempotency_key)
);

CREATE INDEX IF NOT EXISTS idx_referral_attributions_referral
    ON vendor_referral_attributions(referral_id, attributed_at DESC);
CREATE INDEX IF NOT EXISTS idx_referral_attributions_vendor
    ON vendor_referral_attributions(vendor_id, attributed_at DESC);

-- --------------------------------------------------------------------------
-- 2. Payment evidence is observational, not additive by default.
--    Keep the evidence rows for audit; runtime reconciliation must not
--    double-count independent observations of the same payment.
-- --------------------------------------------------------------------------
ALTER TABLE payment_evidence
    ADD COLUMN IF NOT EXISTS observation_scope VARCHAR(24) NOT NULL DEFAULT 'SINGLE_PAYMENT';

ALTER TABLE payment_evidence
    DROP CONSTRAINT IF EXISTS payment_evidence_observation_scope_check;
ALTER TABLE payment_evidence
    ADD CONSTRAINT payment_evidence_observation_scope_check
    CHECK (observation_scope IN ('SINGLE_PAYMENT', 'SPLIT_PAYMENT'));

-- --------------------------------------------------------------------------
-- 3. Delivery timestamps: provider acceptance is sent_at; end delivery is
--    delivered_at only when a provider receipt/webhook establishes it.
-- --------------------------------------------------------------------------
ALTER TABLE notification_deliveries
    ADD COLUMN IF NOT EXISTS delivery_receipt_at TIMESTAMPTZ;

-- --------------------------------------------------------------------------
-- 4. RMA money values should stay 64-bit in the canonical domain.
-- --------------------------------------------------------------------------
ALTER TABLE returns
    ALTER COLUMN claimed_refund_amount_toman TYPE BIGINT,
    ALTER COLUMN approved_refund_amount_toman TYPE BIGINT;
