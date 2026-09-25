-- ============================================================================
-- 033_delivery_lifecycle_and_pod_integrity.sql
-- Canonical delivery lifecycle timestamps, OTP lifecycle, location snapshot,
-- and one-attempt/one-POD invariants.
-- ============================================================================

ALTER TABLE deliveries
    ADD COLUMN IF NOT EXISTS assigned_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS picked_up_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS in_transit_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS arrived_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS failed_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS delivery_otp_expires_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS delivery_otp_attempt_count INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS delivery_otp_used_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS last_otp_attempt_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS current_latitude NUMERIC(9,6),
    ADD COLUMN IF NOT EXISTS current_longitude NUMERIC(9,6),
    ADD COLUMN IF NOT EXISTS last_location_at TIMESTAMPTZ;

ALTER TABLE deliveries
    ADD CONSTRAINT chk_delivery_otp_attempt_count_nonnegative_v033
    CHECK (delivery_otp_attempt_count >= 0);

ALTER TABLE deliveries
    ADD CONSTRAINT chk_delivery_latitude_v033
    CHECK (current_latitude IS NULL OR current_latitude BETWEEN -90 AND 90);

ALTER TABLE deliveries
    ADD CONSTRAINT chk_delivery_longitude_v033
    CHECK (current_longitude IS NULL OR current_longitude BETWEEN -180 AND 180);

CREATE UNIQUE INDEX IF NOT EXISTS uq_delivery_attempt_number_v033
    ON delivery_attempts(delivery_id, attempt_number);

CREATE UNIQUE INDEX IF NOT EXISTS uq_delivery_one_pod_v033
    ON proof_of_delivery(delivery_id);

-- A completed delivery may not accept another OTP.
CREATE OR REPLACE FUNCTION pol_guard_delivery_otp_reuse_v033()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.delivery_otp_used_at IS NOT NULL
       AND (OLD.delivery_otp_used_at IS NOT NULL OR NEW.delivery_otp_used_at < OLD.delivery_otp_expires_at OR OLD.delivery_otp_expires_at IS NULL) THEN
        IF OLD.delivery_otp_used_at IS NOT NULL THEN
            RAISE EXCEPTION 'DELIVERY_OTP_ALREADY_USED'
                USING ERRCODE = '55000';
        END IF;
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_delivery_otp_reuse_v033 ON deliveries;
CREATE TRIGGER trg_delivery_otp_reuse_v033
BEFORE UPDATE OF delivery_otp_used_at ON deliveries
FOR EACH ROW
EXECUTE FUNCTION pol_guard_delivery_otp_reuse_v033();
