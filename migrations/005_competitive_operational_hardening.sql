-- ============================================================================
-- POL Competitive Operational Hardening
-- Migration 005
-- Evidence-derived from B2B marketplace operating patterns (Cartona, Udaan,
-- Wasoko, MaxAB) and POL creative-destruction audit.
-- MVP remains asset-light and NON_CUSTODIAL_DIRECT.
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS btree_gist;

-- 1. Checkout idempotency must be database-enforced, not convention-only.
CREATE UNIQUE INDEX IF NOT EXISTS uq_order_groups_checkout_idempotency_key
    ON order_groups(checkout_idempotency_key)
    WHERE checkout_idempotency_key IS NOT NULL;

-- 2. Inventory invariant: reservations can never exceed physical stock.
ALTER TABLE vendor_inventory
    ADD CONSTRAINT chk_vendor_inventory_reserved_le_physical
    CHECK (reserved_quantity <= physical_quantity);

-- 3. Canonical temporal pricing invariant.
-- Migration 001 used effective_to; migration 004 introduced effective_until.
-- Backfill the newer field, then prevent overlapping validity windows.
UPDATE vendor_prices
SET effective_until = effective_to
WHERE effective_until IS NULL
  AND effective_to IS NOT NULL;

ALTER TABLE vendor_prices
    ADD CONSTRAINT chk_vendor_price_effective_window
    CHECK (effective_until IS NULL OR effective_until > effective_from);

ALTER TABLE vendor_prices
    ADD CONSTRAINT ex_vendor_price_no_overlap
    EXCLUDE USING gist (
        vendor_product_id WITH =,
        tstzrange(effective_from, COALESCE(effective_until, 'infinity'::timestamptz), '[)') WITH &&
    );

-- 4. Vendor operating windows/cutoffs, inspired by B2B logistics practices.
CREATE TABLE IF NOT EXISTS vendor_operating_windows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vendor_id UUID NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
    weekday SMALLINT NOT NULL CHECK (weekday BETWEEN 0 AND 6),
    opens_at TIME NOT NULL,
    closes_at TIME NOT NULL,
    order_cutoff_at TIME,
    dispatch_cutoff_at TIME,
    timezone VARCHAR(64) NOT NULL DEFAULT 'Asia/Tehran',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    effective_from TIMESTAMPTZ NOT NULL DEFAULT now(),
    effective_until TIMESTAMPTZ,
    CONSTRAINT chk_vendor_window_order CHECK (closes_at > opens_at),
    CONSTRAINT chk_vendor_window_effective CHECK (effective_until IS NULL OR effective_until > effective_from),
    CONSTRAINT uq_vendor_operating_window UNIQUE (vendor_id, weekday, effective_from)
);

CREATE INDEX IF NOT EXISTS idx_vendor_operating_windows_vendor
    ON vendor_operating_windows(vendor_id, weekday, is_active);

CREATE TABLE IF NOT EXISTS vendor_capacity_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vendor_id UUID NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
    effective_from TIMESTAMPTZ NOT NULL DEFAULT now(),
    effective_until TIMESTAMPTZ,
    max_orders_per_day INTEGER CHECK (max_orders_per_day IS NULL OR max_orders_per_day >= 0),
    max_orders_per_window INTEGER CHECK (max_orders_per_window IS NULL OR max_orders_per_window >= 0),
    max_pick_units_per_hour INTEGER CHECK (max_pick_units_per_hour IS NULL OR max_pick_units_per_hour >= 0),
    max_dispatches_per_day INTEGER CHECK (max_dispatches_per_day IS NULL OR max_dispatches_per_day >= 0),
    timezone VARCHAR(64) NOT NULL DEFAULT 'Asia/Tehran',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT chk_vendor_capacity_effective CHECK (effective_until IS NULL OR effective_until > effective_from),
    CONSTRAINT uq_vendor_capacity_start UNIQUE (vendor_id, effective_from)
);

CREATE INDEX IF NOT EXISTS idx_vendor_capacity_vendor
    ON vendor_capacity_profiles(vendor_id, effective_from DESC);

-- 5. Structured retailer locations: preserve location identity separately from order snapshots.
CREATE TABLE IF NOT EXISTS retailer_locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    retailer_id UUID NOT NULL REFERENCES retailers(id) ON DELETE CASCADE,
    label VARCHAR(100) NOT NULL DEFAULT 'MAIN_STORE',
    address TEXT NOT NULL,
    neighborhood VARCHAR(100),
    city VARCHAR(80) NOT NULL DEFAULT 'Ahvaz',
    latitude DECIMAL(10,7),
    longitude DECIMAL(10,7),
    landmark TEXT,
    delivery_notes TEXT,
    business_hours JSONB NOT NULL DEFAULT '{}'::jsonb,
    geo_confidence VARCHAR(20) NOT NULL DEFAULT 'UNKNOWN'
        CHECK (geo_confidence IN ('UNKNOWN', 'LOW', 'MEDIUM', 'HIGH', 'VERIFIED')),
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_retailer_location_label UNIQUE (retailer_id, label)
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_retailer_primary_location
    ON retailer_locations(retailer_id) WHERE is_primary = TRUE;

CREATE INDEX IF NOT EXISTS idx_retailer_locations_geo
    ON retailer_locations(city, neighborhood, latitude, longitude);

-- 6. Commercial terms foundation. Not active in MVP pricing yet.
CREATE TABLE IF NOT EXISTS commercial_terms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vendor_id UUID NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
    retailer_id UUID REFERENCES retailers(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    payment_term_code VARCHAR(32) NOT NULL DEFAULT 'PREPAID',
    discount_rate NUMERIC(7,4) NOT NULL DEFAULT 0 CHECK (discount_rate >= 0),
    cash_discount_rate NUMERIC(7,4) NOT NULL DEFAULT 0 CHECK (cash_discount_rate >= 0),
    delivery_term_code VARCHAR(32) NOT NULL DEFAULT 'STANDARD',
    return_policy_code VARCHAR(32) NOT NULL DEFAULT 'STANDARD',
    effective_from TIMESTAMPTZ NOT NULL DEFAULT now(),
    effective_until TIMESTAMPTZ,
    status VARCHAR(20) NOT NULL DEFAULT 'DRAFT' CHECK (status IN ('DRAFT', 'ACTIVE', 'EXPIRED', 'REVOKED')),
    created_by_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT chk_commercial_terms_effective CHECK (effective_until IS NULL OR effective_until > effective_from),
    CONSTRAINT chk_commercial_terms_discount CHECK (discount_rate <= 100 AND cash_discount_rate <= 100)
);

CREATE INDEX IF NOT EXISTS idx_commercial_terms_vendor_retailer
    ON commercial_terms(vendor_id, retailer_id, status, effective_from DESC);

-- 7. Payment evidence/reconciliation for the non-custodial model.
CREATE TABLE IF NOT EXISTS payment_evidence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payment_id UUID NOT NULL REFERENCES payments(id) ON DELETE CASCADE,
    evidence_type VARCHAR(32) NOT NULL CHECK (evidence_type IN ('BANK_REFERENCE', 'POS_REFERENCE', 'RECEIPT_IMAGE', 'VENDOR_CONFIRMATION', 'RETAILER_CONFIRMATION')),
    external_reference VARCHAR(255),
    claimed_amount_toman BIGINT CHECK (claimed_amount_toman >= 0),
    observed_amount_toman BIGINT CHECK (observed_amount_toman >= 0),
    evidence_uri TEXT,
    evidence_sha256 VARCHAR(64),
    captured_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    captured_by_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_payment_evidence_payment
    ON payment_evidence(payment_id, captured_at DESC);

CREATE TABLE IF NOT EXISTS payment_reconciliation_cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payment_id UUID NOT NULL REFERENCES payments(id) ON DELETE CASCADE,
    status VARCHAR(24) NOT NULL DEFAULT 'OPEN'
        CHECK (status IN ('OPEN', 'MATCHED', 'PARTIALLY_MATCHED', 'MISMATCH', 'RESOLVED', 'CANCELLED')),
    expected_amount_toman BIGINT NOT NULL CHECK (expected_amount_toman >= 0),
    observed_amount_toman BIGINT CHECK (observed_amount_toman >= 0),
    external_reference VARCHAR(255),
    resolution_reason TEXT,
    resolved_by_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    opened_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at TIMESTAMPTZ
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_payment_open_reconciliation
    ON payment_reconciliation_cases(payment_id)
    WHERE status IN ('OPEN', 'MISMATCH', 'PARTIALLY_MATCHED');

-- 8. Retailer saved lists / quick reorder foundation for high-frequency FMCG replenishment.
CREATE TABLE IF NOT EXISTS retailer_saved_lists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    retailer_id UUID NOT NULL REFERENCES retailers(id) ON DELETE CASCADE,
    name VARCHAR(120) NOT NULL,
    list_type VARCHAR(24) NOT NULL DEFAULT 'REORDER'
        CHECK (list_type IN ('REORDER', 'FAVORITES', 'ROUTINE', 'CUSTOM')),
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS retailer_saved_list_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    saved_list_id UUID NOT NULL REFERENCES retailer_saved_lists(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
    default_quantity INTEGER NOT NULL DEFAULT 1 CHECK (default_quantity > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_saved_list_product UNIQUE (saved_list_id, product_id)
);

-- 9. Explicit data-consent record for SMS/push/marketing and future privacy controls.
CREATE TABLE IF NOT EXISTS data_consents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    consent_type VARCHAR(32) NOT NULL CHECK (consent_type IN ('TRANSACTIONAL_SMS', 'TRANSACTIONAL_PUSH', 'MARKETING_SMS', 'MARKETING_PUSH', 'MEDIA_STORAGE', 'LOCATION_USAGE')),
    status VARCHAR(16) NOT NULL CHECK (status IN ('GRANTED', 'REVOKED')),
    source VARCHAR(32) NOT NULL DEFAULT 'APP',
    version VARCHAR(32) NOT NULL DEFAULT '1.0',
    granted_at TIMESTAMPTZ,
    revoked_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_active_consent
    ON data_consents(user_id, organization_id, consent_type)
    WHERE status = 'GRANTED';

-- 10. Risk / abuse evidence ledger.
CREATE TABLE IF NOT EXISTS risk_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subject_type VARCHAR(24) NOT NULL CHECK (subject_type IN ('USER', 'ORGANIZATION', 'RETAILER', 'VENDOR', 'ORDER', 'PAYMENT')),
    subject_id UUID NOT NULL,
    event_type VARCHAR(64) NOT NULL,
    severity VARCHAR(16) NOT NULL DEFAULT 'LOW' CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    score_delta NUMERIC(7,2) NOT NULL DEFAULT 0,
    source VARCHAR(32) NOT NULL DEFAULT 'SYSTEM',
    evidence JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_risk_events_subject
    ON risk_events(subject_type, subject_id, created_at DESC);

-- 11. Metric lineage: every production KPI must identify its source and calculation version.
CREATE TABLE IF NOT EXISTS metric_definitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_key VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    definition TEXT NOT NULL,
    source_events JSONB NOT NULL DEFAULT '[]'::jsonb,
    source_tables JSONB NOT NULL DEFAULT '[]'::jsonb,
    calculation_version VARCHAR(32) NOT NULL DEFAULT '1.0',
    timezone VARCHAR(64) NOT NULL DEFAULT 'Asia/Tehran',
    denominator_rules TEXT,
    cohort_rules TEXT,
    status VARCHAR(16) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('DRAFT', 'ACTIVE', 'DEPRECATED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 12. Lightweight experimentation foundation; no experiment is active by default.
CREATE TABLE IF NOT EXISTS experiments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_key VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    hypothesis TEXT NOT NULL,
    control_definition JSONB NOT NULL DEFAULT '{}'::jsonb,
    treatment_definition JSONB NOT NULL DEFAULT '{}'::jsonb,
    success_metric_key VARCHAR(100),
    status VARCHAR(20) NOT NULL DEFAULT 'DRAFT' CHECK (status IN ('DRAFT', 'ACTIVE', 'PAUSED', 'COMPLETED', 'CANCELLED')),
    starts_at TIMESTAMPTZ,
    ends_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS experiment_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_id UUID NOT NULL REFERENCES experiments(id) ON DELETE CASCADE,
    subject_type VARCHAR(16) NOT NULL CHECK (subject_type IN ('USER', 'ORGANIZATION', 'RETAILER', 'VENDOR')),
    subject_id UUID NOT NULL,
    variant VARCHAR(32) NOT NULL CHECK (variant IN ('CONTROL', 'TREATMENT')),
    assigned_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_experiment_subject UNIQUE (experiment_id, subject_type, subject_id)
);

CREATE INDEX IF NOT EXISTS idx_experiment_assignments_variant
    ON experiment_assignments(experiment_id, variant);
