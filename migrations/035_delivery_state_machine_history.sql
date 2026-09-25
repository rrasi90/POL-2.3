-- ============================================================================
-- 035_delivery_state_machine_history.sql
-- ============================================================================

ALTER TABLE deliveries
    ADD COLUMN IF NOT EXISTS failed_reason TEXT;

CREATE TABLE IF NOT EXISTS delivery_timeline_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    delivery_id UUID NOT NULL REFERENCES deliveries(id) ON DELETE CASCADE,
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    from_status VARCHAR(20),
    to_status VARCHAR(20) NOT NULL,
    actor_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    actor_organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    event_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_delivery_timeline_delivery_created_v035
    ON delivery_timeline_events(delivery_id, created_at ASC);

CREATE OR REPLACE FUNCTION pol_validate_delivery_status_transition_v035()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.delivery_status = OLD.delivery_status THEN
        RETURN NEW;
    END IF;

    IF (OLD.delivery_status, NEW.delivery_status) IN (
        ('ASSIGNED','PICKED_UP'),
        ('PICKED_UP','IN_TRANSIT'),
        ('IN_TRANSIT','ARRIVED'),
        ('ARRIVED','DELIVERED'),
        ('IN_TRANSIT','FAILED'),
        ('ARRIVED','FAILED')
    ) THEN
        RETURN NEW;
    END IF;

    RAISE EXCEPTION 'DELIVERY_INVALID_TRANSITION: % -> %',
        OLD.delivery_status, NEW.delivery_status
        USING ERRCODE = '23514';
END;
$$;

DROP TRIGGER IF EXISTS trg_validate_delivery_status_transition_v035 ON deliveries;
CREATE TRIGGER trg_validate_delivery_status_transition_v035
BEFORE UPDATE OF delivery_status ON deliveries
FOR EACH ROW
EXECUTE FUNCTION pol_validate_delivery_status_transition_v035();

CREATE OR REPLACE FUNCTION pol_guard_delivery_timeline_append_only_v035()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'delivery_timeline_events is append-only and cannot be updated or deleted'
        USING ERRCODE = '55000';
END;
$$;

DROP TRIGGER IF EXISTS trg_delivery_timeline_append_only_v035 ON delivery_timeline_events;
CREATE TRIGGER trg_delivery_timeline_append_only_v035
BEFORE UPDATE OR DELETE ON delivery_timeline_events
FOR EACH ROW
EXECUTE FUNCTION pol_guard_delivery_timeline_append_only_v035();
