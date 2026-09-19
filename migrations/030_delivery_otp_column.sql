-- 030: Add delivery_otp to deliveries — Stage 24 Proof of Delivery

ALTER TABLE deliveries ADD COLUMN IF NOT EXISTS delivery_otp VARCHAR(6);
CREATE INDEX IF NOT EXISTS idx_deliveries_otp ON deliveries (delivery_otp) WHERE delivery_otp IS NOT NULL;

COMMENT ON COLUMN deliveries.delivery_otp IS '6-digit OTP for delivery verification — generated at dispatch, verified at POD.';
