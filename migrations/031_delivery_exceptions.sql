-- Migration 031: Delivery Exceptions — Stage 25
-- Canonical table for delivery-time exceptions (doorstep rejection, damage, incomplete, wrong items).

CREATE TABLE IF NOT EXISTS delivery_exceptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    delivery_id UUID NOT NULL REFERENCES deliveries(id) ON DELETE CASCADE,
    order_id UUID NOT NULL REFERENCES orders(id),
    retailer_id UUID NOT NULL REFERENCES retailers(id),
    vendor_id UUID NOT NULL REFERENCES vendors(id),
    exception_type VARCHAR(30) NOT NULL CHECK (
        exception_type IN (
            'DOORSTEP_REJECTION', 'DAMAGED_GOODS', 'ITEM_DISCREPANCY',
            'INCOMPLETE_DELIVERY', 'VENDOR_NO_SHOW', 'QUALITY_ISSUE', 'OTHER'
        )
    ),
    status VARCHAR(20) NOT NULL DEFAULT 'REPORTED' CHECK (
        status IN ('REPORTED', 'UNDER_REVIEW', 'RESOLVED', 'ESCALATED', 'CANCELLED')
    ),
    description TEXT,
    resolution_type VARCHAR(30) CHECK (
        resolution_type IN (
            'FULL_REFUND', 'PARTIAL_REFUND', 'REPLACEMENT',
            'NO_ACTION', 'RETURN_PICKUP', 'ESCALATED_TO_OPS'
        )
    ),
    resolution_note TEXT,
    reported_by_user_id UUID NOT NULL,
    reported_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_delivery_exceptions_delivery_id ON delivery_exceptions(delivery_id);
CREATE INDEX idx_delivery_exceptions_order_id ON delivery_exceptions(order_id);
CREATE INDEX idx_delivery_exceptions_vendor_id ON delivery_exceptions(vendor_id);
CREATE INDEX idx_delivery_exceptions_status ON delivery_exceptions(status);
CREATE INDEX idx_delivery_exceptions_reported_at ON delivery_exceptions(reported_at);

COMMENT ON TABLE delivery_exceptions IS 'Delivery-time exceptions reported by retailers at doorstep or after delivery (Stage 25).';
COMMENT ON COLUMN delivery_exceptions.exception_type IS 'EX-04: DAMAGED_GOODS, EX-05: ITEM_DISCREPANCY, EX-06: DOORSTEP_REJECTION, EX-07: VENDOR_NO_SHOW';
COMMENT ON COLUMN delivery_exceptions.status IS 'REPORTED → UNDER_REVIEW → RESOLVED/ESCALATED/CANCELLED';
COMMENT ON COLUMN delivery_exceptions.resolution_type IS 'Resolution after review: refund, replacement, return pickup, or no action.';
