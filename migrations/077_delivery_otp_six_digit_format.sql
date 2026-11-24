-- 077: Six-digit delivery OTP policy with safe legacy in-flight compatibility.
--
-- New dispatches receive six-digit delivery OTPs. Existing active delivery rows
-- may still contain four-digit codes issued under the former policy; those
-- values are retained until their delivery reaches a terminal state. This
-- migration deliberately does NOT rotate, clear, or re-send any active code.
--
-- The new length column defaults to six for every newly inserted delivery.
-- Existing rows are backfilled from the actual stored code length so their
-- original recipient notification remains valid.

ALTER TABLE deliveries
    ADD COLUMN IF NOT EXISTS delivery_otp_length SMALLINT NOT NULL DEFAULT 6;

UPDATE deliveries
   SET delivery_otp_length = char_length(delivery_otp)::SMALLINT
 WHERE delivery_otp IS NOT NULL
   AND delivery_otp_length <> char_length(delivery_otp)::SMALLINT;

ALTER TABLE deliveries
    DROP CONSTRAINT IF EXISTS chk_delivery_otp_format_v068;

ALTER TABLE deliveries
    ADD CONSTRAINT chk_delivery_otp_format_v068
    CHECK (
        delivery_otp IS NULL
        OR (
            delivery_otp_length = 6
            AND delivery_otp ~ '^[0-9]{6}$'
        )
        OR (
            delivery_otp_length = 4
            AND delivery_otp ~ '^[0-9]{4}$'
        )
    )
    NOT VALID;

ALTER TABLE deliveries
    VALIDATE CONSTRAINT chk_delivery_otp_format_v068;

COMMENT ON COLUMN deliveries.delivery_otp IS
    'Recipient-only delivery OTP. New dispatches issue six numeric digits (D-029); legacy active four-digit codes remain valid until terminal completion.';

COMMENT ON COLUMN deliveries.delivery_otp_length IS
    'Length of the stored delivery OTP. Defaults to six for new rows; migration 077 backfills the actual length for legacy in-flight deliveries.';
