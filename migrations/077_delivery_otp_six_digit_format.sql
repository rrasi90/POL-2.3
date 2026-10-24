-- 077: Update delivery OTP check constraint to six digits (D-018 amendment 2026-10-25).
--
-- D-018 standardized all authentication and delivery verification OTP codes
-- to exactly six decimal digits. Migration 068 had added constraint
-- chk_delivery_otp_format_v068 enforcing ^[0-9]{4}$.
-- This migration remediates any legacy non-6-digit delivery records and updates
-- the check constraint to require ^[0-9]{6}$.

-- 1. Remediate terminal deliveries: obsolete legacy OTPs are cleared safely
UPDATE deliveries
SET delivery_otp = NULL
WHERE delivery_otp IS NOT NULL
  AND NOT (delivery_otp ~ '^[0-9]{6}$')
  AND delivery_status IN ('DELIVERED', 'CANCELLED', 'FAILED', 'RETURNED');

-- 2. Remediate active in-flight deliveries: assign fresh 6-digit OTP and reset attempt counter
UPDATE deliveries
SET delivery_otp = LPAD(FLOOR(RANDOM() * 1000000)::TEXT, 6, '0'),
    delivery_otp_attempt_count = 0
WHERE delivery_otp IS NOT NULL
  AND NOT (delivery_otp ~ '^[0-9]{6}$')
  AND delivery_status IN ('ASSIGNED', 'DISPATCHED', 'ARRIVED');

-- 3. Replace the check constraint
ALTER TABLE deliveries
    DROP CONSTRAINT IF EXISTS chk_delivery_otp_format_v068;

ALTER TABLE deliveries
    ADD CONSTRAINT chk_delivery_otp_format_v068
    CHECK (delivery_otp IS NULL OR delivery_otp ~ '^[0-9]{6}$')
    NOT VALID;

-- 4. Validate constraint against existing reconciled data
ALTER TABLE deliveries
    VALIDATE CONSTRAINT chk_delivery_otp_format_v068;

-- 5. Update column comment
COMMENT ON COLUMN deliveries.delivery_otp IS
    '6-digit numeric OTP (OTP_CODE_LENGTH=6; policy amended 2026-10-25) for delivery verification at POD. Verified by chk_delivery_otp_format_v068.';
