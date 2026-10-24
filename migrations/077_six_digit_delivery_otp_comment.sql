-- 077: Align delivery OTP column documentation with D-029 (2026-10-25).
-- The existing VARCHAR(6) storage column already supports the six-digit format.
-- Metadata only: no rewrite of historical migration 030 or delivery rows.
COMMENT ON COLUMN deliveries.delivery_otp IS
  '6-digit numeric delivery proof-of-delivery OTP (D-029); generated at dispatch and verified through the authorized retailer/receiver confirmation channel.';
