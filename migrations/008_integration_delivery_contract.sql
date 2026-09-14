-- ============================================================================
-- POL Integration & Delivery Contract
-- Migration 008
-- Purpose: make domain -> outbox -> notification -> delivery a hard boundary.
-- MVP remains NON_CUSTODIAL_DIRECT and asset-light.
-- ============================================================================

-- 1. Explicit routing metadata on integration/outbox events.
ALTER TABLE outbox_events
    ADD COLUMN IF NOT EXISTS target_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS target_organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS dedupe_key VARCHAR(255),
    ADD COLUMN IF NOT EXISTS channel_hint VARCHAR(16);

ALTER TABLE outbox_events
    DROP CONSTRAINT IF EXISTS chk_outbox_channel_hint;

ALTER TABLE outbox_events
    ADD CONSTRAINT chk_outbox_channel_hint
    CHECK (channel_hint IS NULL OR channel_hint IN ('INBOX', 'PUSH', 'SMS'));

CREATE UNIQUE INDEX IF NOT EXISTS uq_outbox_dedupe_key
    ON outbox_events(event_name, dedupe_key)
    WHERE dedupe_key IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_outbox_routing_target
    ON outbox_events(target_organization_id, target_user_id, status, created_at);

-- Backfill the currently canonical daily inventory reminder target directly
-- from the vendor identity already carried by the event payload.
UPDATE outbox_events oe
SET target_user_id = v.user_id,
    target_organization_id = v.organization_id,
    channel_hint = 'PUSH',
    dedupe_key = oe.event_id
FROM vendors v
WHERE oe.event_name = 'DAILY_INVENTORY_REMINDER'
  AND oe.aggregate_type = 'VENDOR_INVENTORY'
  AND oe.aggregate_id = v.id
  AND oe.target_user_id IS NULL;

-- 2. Delivery attempts are operational records, separate from the logical
-- notification itself. This supports retries, provider references and audit.
CREATE TABLE IF NOT EXISTS notification_deliveries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    notification_id UUID NOT NULL REFERENCES notifications(id) ON DELETE CASCADE,
    channel VARCHAR(16) NOT NULL CHECK (channel IN ('INBOX', 'PUSH', 'SMS')),
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING'
        CHECK (status IN ('PENDING', 'SENT', 'FAILED', 'SUPPRESSED', 'EXPIRED')),
    attempt_count INTEGER NOT NULL DEFAULT 0 CHECK (attempt_count >= 0),
    provider_message_id VARCHAR(255),
    last_error TEXT,
    scheduled_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    sent_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_notification_delivery_channel UNIQUE (notification_id, channel)
);

CREATE INDEX IF NOT EXISTS idx_notification_deliveries_pending
    ON notification_deliveries(status, scheduled_at);

-- 3. Versioned templates are operational configuration, not application logic.
CREATE TABLE IF NOT EXISTS notification_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_name VARCHAR(100) NOT NULL,
    channel VARCHAR(16) NOT NULL CHECK (channel IN ('INBOX', 'PUSH', 'SMS')),
    version VARCHAR(32) NOT NULL,
    title_template TEXT,
    body_template TEXT NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    priority VARCHAR(16) NOT NULL DEFAULT 'NORMAL'
        CHECK (priority IN ('LOW', 'NORMAL', 'HIGH', 'CRITICAL')),
    allow_opt_out BOOLEAN NOT NULL DEFAULT TRUE,
    effective_from TIMESTAMPTZ NOT NULL DEFAULT now(),
    effective_until TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT chk_notification_template_effective
        CHECK (effective_until IS NULL OR effective_until > effective_from),
    CONSTRAINT uq_notification_template_version
        UNIQUE (event_name, channel, version)
);

CREATE INDEX IF NOT EXISTS idx_notification_templates_active
    ON notification_templates(event_name, channel, enabled, effective_from DESC);

-- 4. Any logical notification insertion automatically enters the delivery
-- pipeline. This closes the architectural loophole where a service could write
-- notifications directly and bypass outbox-based delivery/retry semantics.
CREATE OR REPLACE FUNCTION pol_enqueue_notification_delivery()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO outbox_events (
        id,
        event_id,
        event_name,
        aggregate_type,
        aggregate_id,
        payload,
        status,
        target_user_id,
        target_organization_id,
        dedupe_key,
        channel_hint
    ) VALUES (
        gen_random_uuid(),
        'notify_delivery_' || NEW.id::text,
        'NOTIFICATION_DELIVERY_REQUESTED',
        'NOTIFICATION',
        NEW.id,
        jsonb_build_object(
            'notification_id', NEW.id,
            'user_id', NEW.user_id,
            'organization_id', NEW.organization_id,
            'event_name', NEW.event_name,
            'priority', NEW.priority
        ),
        'PENDING',
        NEW.user_id,
        NEW.organization_id,
        'notification:' || NEW.id::text,
        'INBOX'
    )
    ON CONFLICT (event_name, dedupe_key) WHERE dedupe_key IS NOT NULL DO NOTHING;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_notification_enqueue_delivery ON notifications;
CREATE TRIGGER trg_notification_enqueue_delivery
AFTER INSERT ON notifications
FOR EACH ROW
EXECUTE FUNCTION pol_enqueue_notification_delivery();

-- 5. Canonical seed templates. They are intentionally generic; product copy
-- should be refined during visual/product design without changing routing.
INSERT INTO notification_templates (event_name, channel, version, title_template, body_template, priority, allow_opt_out)
VALUES
('ORDER_SUBMITTED', 'INBOX', '1.0', 'سفارش ثبت شد', 'سفارش شما ثبت شد.', 'NORMAL', TRUE),
('ORDER_ACCEPTED', 'INBOX', '1.0', 'سفارش پذیرفته شد', 'بنکدار سفارش شما را پذیرفت.', 'NORMAL', TRUE),
('ORDER_REJECTED', 'INBOX', '1.0', 'سفارش رد شد', 'این سفارش توسط بنکدار رد شد.', 'HIGH', TRUE),
('DAILY_INVENTORY_REMINDER', 'PUSH', '1.0', 'تأیید موجودی امروز', 'آیا موجودی امروز انبار درست است؟', 'NORMAL', FALSE),
('FEEDBACK_REPLIED', 'INBOX', '1.0', 'پاسخ به بازخورد شما', '{{body}}', 'NORMAL', TRUE)
ON CONFLICT (event_name, channel, version) DO NOTHING;
