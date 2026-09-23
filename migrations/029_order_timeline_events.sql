-- 029: order_timeline_events — Stage 20 Order Query / Timeline HTTP
-- Provides an immutable append-only audit trail of every order status transition.

CREATE TABLE IF NOT EXISTS order_timeline_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    from_status VARCHAR(30),
    to_status VARCHAR(30) NOT NULL,
    actor_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    actor_organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    event_data JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_order_timeline_order_created
    ON order_timeline_events (order_id, created_at ASC);

CREATE INDEX IF NOT EXISTS idx_order_timeline_event_type
    ON order_timeline_events (order_id, event_type);

COMMENT ON TABLE order_timeline_events IS 'Immutable append-only audit trail for order lifecycle events — Stage 20.';
