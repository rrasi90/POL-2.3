-- ============================================================================
-- POL PLATFORM OPERATIONAL INTELLIGENCE & DOMAIN COMPLETION SCHEMA
-- Migration: 004_operational_intelligence.sql
-- ============================================================================

-- 1. Daily Inventory Confirmations (Vendor Warehouse Daily Health Check)
CREATE TABLE IF NOT EXISTS daily_inventory_confirmations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vendor_id UUID NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
    confirmation_date DATE NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'CONFIRMED_NO_CHANGES', 'CONFIRMED_WITH_CHANGES', 'MISSED', 'ESCALATED')),
    actor_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    confirmed_at TIMESTAMPTZ,
    changed_item_count INT NOT NULL DEFAULT 0,
    source VARCHAR(32) NOT NULL DEFAULT 'WEB_PANEL' CHECK (source IN ('WEB_PANEL', 'MOBILE_APP', 'SMS_BOT', 'SYSTEM_TIMEOUT', 'ADMIN_OVERRIDE')),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_vendor_daily_confirmation UNIQUE (vendor_id, confirmation_date)
);

CREATE INDEX IF NOT EXISTS idx_daily_inv_conf_vendor_date ON daily_inventory_confirmations(vendor_id, confirmation_date);
CREATE INDEX IF NOT EXISTS idx_daily_inv_conf_status ON daily_inventory_confirmations(status);

-- 2. Daily Inventory Confirmation Delta Items
CREATE TABLE IF NOT EXISTS daily_inventory_confirmation_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    confirmation_id UUID NOT NULL REFERENCES daily_inventory_confirmations(id) ON DELETE CASCADE,
    vendor_product_id UUID NOT NULL REFERENCES vendor_products(id) ON DELETE CASCADE,
    previous_quantity INT NOT NULL,
    declared_quantity INT NOT NULL,
    difference INT GENERATED ALWAYS AS (declared_quantity - previous_quantity) STORED,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_conf_item_product UNIQUE (confirmation_id, vendor_product_id)
);

-- 3. Inventory Confidence & Freshness Columns on vendor_inventory
ALTER TABLE vendor_inventory ADD COLUMN IF NOT EXISTS last_confirmed_at TIMESTAMPTZ;
ALTER TABLE vendor_inventory ADD COLUMN IF NOT EXISTS inventory_confidence VARCHAR(32) NOT NULL DEFAULT 'STALE' CHECK (inventory_confidence IN ('CONFIRMED_TODAY', 'CONFIRMED_YESTERDAY', 'STALE'));
ALTER TABLE vendor_inventory ADD COLUMN IF NOT EXISTS verification_source VARCHAR(32) NOT NULL DEFAULT 'MANUAL' CHECK (verification_source IN ('MANUAL', 'BARCODE_SCAN', 'API', 'DAILY_CONFIRMATION', 'SYSTEM_INFERRED'));

-- 4. Suggestion & Feedback Box (Universal Across All Roles)
CREATE TABLE IF NOT EXISTS feedback_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    feedback_type VARCHAR(32) NOT NULL CHECK (feedback_type IN ('BUG', 'SUGGESTION', 'QUESTION', 'COMPLAINT', 'REQUEST')),
    priority VARCHAR(16) NOT NULL DEFAULT 'NORMAL' CHECK (priority IN ('LOW', 'NORMAL', 'HIGH', 'CRITICAL')),
    status VARCHAR(32) NOT NULL DEFAULT 'SUBMITTED' CHECK (status IN ('SUBMITTED', 'TRIAGED', 'IN_REVIEW', 'ACCEPTED', 'PLANNED', 'IMPLEMENTED', 'REJECTED', 'DUPLICATE', 'CLOSED')),
    visibility VARCHAR(32) NOT NULL DEFAULT 'PRIVATE_TO_ADMIN' CHECK (visibility IN ('PUBLIC_TO_TEAM', 'PRIVATE_TO_ADMIN', 'ORG_VISIBLE')),
    title VARCHAR(255),
    description TEXT NOT NULL,
    attachment_url TEXT,
    client_context JSONB NOT NULL DEFAULT '{}'::jsonb,
    assigned_to_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    admin_notes TEXT,
    admin_reply TEXT,
    related_order_id UUID REFERENCES orders(id) ON DELETE SET NULL,
    related_support_case_id UUID REFERENCES support_cases(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    triaged_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_feedback_user ON feedback_submissions(user_id);
CREATE INDEX IF NOT EXISTS idx_feedback_org ON feedback_submissions(organization_id);
CREATE INDEX IF NOT EXISTS idx_feedback_status ON feedback_submissions(status);
CREATE INDEX IF NOT EXISTS idx_feedback_priority ON feedback_submissions(priority);

-- 5. Vendor Reliability Events Ledger (Raw Event Ledger)
CREATE TABLE IF NOT EXISTS vendor_reliability_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vendor_id UUID NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
    event_type VARCHAR(64) NOT NULL CHECK (event_type IN (
        'ORDER_ACCEPTED', 'ORDER_REJECTED', 'ACCEPTANCE_LATE',
        'PREPARATION_LATE', 'DISPATCH_LATE', 'DELIVERY_LATE',
        'STOCKOUT_AFTER_CONFIRMATION', 'WRONG_ITEM', 'SHORTAGE', 'DAMAGE',
        'PRICE_CHANGED_AFTER_QUOTE', 'PAYMENT_CONFIRMATION_LATE',
        'DISPUTE_OPENED', 'DISPUTE_CONFIRMED',
        'DAILY_CONFIRMATION_COMPLETED', 'DAILY_CONFIRMATION_MISSED'
    )),
    order_id UUID REFERENCES orders(id) ON DELETE SET NULL,
    impact_score NUMERIC(5,2) NOT NULL DEFAULT 0.00,
    declared_value JSONB,
    observed_value JSONB,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_vendor_reliability_vendor ON vendor_reliability_events(vendor_id);
CREATE INDEX IF NOT EXISTS idx_vendor_reliability_type ON vendor_reliability_events(event_type);

-- 6. Price Versioning & Effective Date Range
ALTER TABLE vendor_prices ADD COLUMN IF NOT EXISTS price_version INT NOT NULL DEFAULT 1;
ALTER TABLE vendor_prices ADD COLUMN IF NOT EXISTS effective_from TIMESTAMPTZ NOT NULL DEFAULT now();
ALTER TABLE vendor_prices ADD COLUMN IF NOT EXISTS effective_until TIMESTAMPTZ;

-- 7. Product Identity Lifecycle & Merge Audit Logs
CREATE TABLE IF NOT EXISTS product_identity_lifecycle_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    actor_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    previous_status VARCHAR(32),
    new_status VARCHAR(32) NOT NULL,
    change_reason TEXT NOT NULL,
    merged_into_product_id UUID REFERENCES products(id) ON DELETE SET NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_product_identity_product ON product_identity_lifecycle_logs(product_id);

-- 8. Returns & Reverse Logistics (RMA)
CREATE TABLE IF NOT EXISTS returns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    return_number VARCHAR(64) UNIQUE NOT NULL,
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    retailer_id UUID NOT NULL REFERENCES retailers(id) ON DELETE CASCADE,
    vendor_id UUID NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
    status VARCHAR(32) NOT NULL DEFAULT 'RETURN_REQUESTED' CHECK (status IN (
        'RETURN_REQUESTED', 'PICKUP_REQUIRED', 'RETURN_IN_TRANSIT',
        'VENDOR_INSPECTION', 'ACCEPTED', 'REJECTED', 'CLOSED'
    )),
    reason TEXT NOT NULL,
    claimed_refund_amount_toman INT NOT NULL,
    inspection_outcome VARCHAR(32) CHECK (inspection_outcome IN ('RESTOCK', 'SCRAP', 'RETURN_TO_RETAILER', 'VENDOR_LIABILITY', 'LOGISTICS_DAMAGE')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_returns_order ON returns(order_id);
CREATE INDEX IF NOT EXISTS idx_returns_retailer ON returns(retailer_id);
CREATE INDEX IF NOT EXISTS idx_returns_vendor ON returns(vendor_id);
