-- 061: Explicit request-fingerprint binding for replay-safe writes.
ALTER TABLE disputes
    ADD COLUMN IF NOT EXISTS idempotency_fingerprint VARCHAR(64);

ALTER TABLE refunds
    ADD COLUMN IF NOT EXISTS idempotency_fingerprint VARCHAR(64);

CREATE INDEX IF NOT EXISTS idx_disputes_idempotency_fingerprint_v061
    ON disputes(idempotency_key, idempotency_fingerprint)
    WHERE idempotency_key IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_refunds_idempotency_fingerprint_v061
    ON refunds(idempotency_key, idempotency_fingerprint)
    WHERE idempotency_key IS NOT NULL;
