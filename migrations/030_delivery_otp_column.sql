-- 030: Add delivery_otp to deliveries — Stage 24 Proof of Delivery

ALTER TABLE deliveries ADD COLUMN IF NOT EXISTS delivery_otp VARCHAR(6);
CREATE INDEX IF NOT EXISTS idx_deliveries_otp ON deliveries (delivery_otp) WHERE delivery_otp IS NOT NULL;

COMMENT ON COLUMN deliveries.delivery_otp IS '6-digit OTP (OTP_CODE_LENGTH=6; policy amended 2026-10-25) for delivery verification — generated at dispatch, verified at POD. Column VARCHAR(6) matches the current six-digit contract.';
