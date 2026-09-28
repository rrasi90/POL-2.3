-- 041: inventory bulk-session persistence for continuous scan/publish.
BEGIN;

CREATE TABLE IF NOT EXISTS inventory_scan_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vendor_id UUID NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
    external_session_id VARCHAR(128) NOT NULL,
    created_by_user_id UUID NOT NULL REFERENCES users(id),
    status VARCHAR(16) NOT NULL DEFAULT 'DRAFT'
        CHECK (status IN ('DRAFT','PUBLISHED','CANCELLED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    published_at TIMESTAMPTZ,
    CONSTRAINT uq_inventory_scan_session_external UNIQUE (vendor_id, external_session_id)
);

CREATE TABLE IF NOT EXISTS inventory_scan_session_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES inventory_scan_sessions(id) ON DELETE CASCADE,
    vendor_product_id UUID NOT NULL REFERENCES vendor_products(id) ON DELETE CASCADE,
    physical_quantity INTEGER NOT NULL CHECK (physical_quantity >= 0),
    unit_price_toman BIGINT NOT NULL CHECK (unit_price_toman > 0),
    consumer_price_per_unit_toman BIGINT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_inventory_scan_item UNIQUE (session_id, vendor_product_id)
);

CREATE INDEX IF NOT EXISTS idx_inventory_scan_sessions_vendor_status
    ON inventory_scan_sessions(vendor_id, status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_inventory_scan_session_items_session
    ON inventory_scan_session_items(session_id);

COMMIT;
