-- 073: Payment ledger integrity for the G-452..G-465 closure.
--
-- 1. PAYMENT_VERIFIED outbox events previously had no notification template
--    (orphaned outbox contract): the integration worker could not render them.
--    Version the canonical template here.
-- 2. Payment creation had no idempotency binding: add request idempotency
--    columns with a partial unique index so a retried direct-payment record
--    cannot create duplicate financial rows (mirrors refunds/checkout model
--    from migration 061).

INSERT INTO notification_templates (
    event_name, channel, version, title_template, body_template,
    priority, allow_opt_out, effective_from
)
VALUES (
    'PAYMENT_VERIFIED',
    'INBOX',
    '1.0',
    'پرداخت تأیید شد',
    'پرداخت سفارش شما با مبلغ {{amount_toman}} تومان تأیید شد.',
    'HIGH',
    FALSE,
    now()
);

ALTER TABLE payments
    ADD COLUMN IF NOT EXISTS idempotency_key VARCHAR(128),
    ADD COLUMN IF NOT EXISTS idempotency_fingerprint VARCHAR(64);

CREATE UNIQUE INDEX IF NOT EXISTS uq_payments_idempotency_key
    ON payments(idempotency_key)
    WHERE idempotency_key IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_payments_idempotency_fingerprint_v073
    ON payments(idempotency_key, idempotency_fingerprint)
    WHERE idempotency_key IS NOT NULL;
