-- 071: Delivery OTP recipient channel + durable attempt accounting
-- (completes G-438/G-439 remediation).
--
-- G-439 removed the delivery OTP from the vendor dispatch response. The
-- canonical recipient channel is the DELIVERY_OTP_GENERATED outbox event,
-- targeted at the retailer organization (INBOX). The event payload now carries
-- delivery_otp (see fulfillment_service.dispatch_order); this migration
-- versions the notification template so the rendered inbox body contains the
-- code. Versioned forward: the worker selects the latest effective template.
--
-- G-438 hardening: the OTP attempt cap must survive per-request transaction
-- rollback (an invalid-OTP HTTP request rolls back its whole transaction), so
-- the authoritative attempt counter lives in its own table, written by the
-- application boundary in an independent transaction before the confirmation
-- transaction starts. deliveries.delivery_otp_attempt_count (migration 033/068)
-- is superseded by this table and remains only for historical rows.

INSERT INTO notification_templates (
    event_name, channel, version, title_template, body_template,
    priority, allow_opt_out, effective_from
)
VALUES (
    'DELIVERY_OTP_GENERATED',
    'INBOX',
    '1.1',
    'کد تحویل ایجاد شد',
    'سفارش شما ارسال شد. کد تأیید تحویل (یکبارمصرف): {{delivery_otp}}',
    'CRITICAL',
    FALSE,
    now()
);

CREATE TABLE IF NOT EXISTS delivery_otp_attempts (
    delivery_id UUID PRIMARY KEY REFERENCES deliveries(id) ON DELETE CASCADE,
    attempt_count INT NOT NULL DEFAULT 0 CHECK (attempt_count >= 0),
    last_attempt_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
