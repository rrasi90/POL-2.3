-- 026_auth_otp_rate_limit_and_lockout.sql
-- D-018: OTP rate-limit (3/5min/phone+IP) and phone lockout (10min after 5 failures)
-- Backward-safe: ADD COLUMN IF NOT EXISTS with defaults for existing rows.

-- 1. Add IP address to otp_challenges (rate-limit scope = phone+IP)
ALTER TABLE otp_challenges
    ADD COLUMN IF NOT EXISTS ip_address VARCHAR(45) NOT NULL DEFAULT '';

-- 2. Add lockout timestamp to otp_challenges (lockout scope = phone only)
ALTER TABLE otp_challenges
    ADD COLUMN IF NOT EXISTS blocked_at TIMESTAMPTZ;

-- 3. Index for rate-limit query: phone + ip + created_at
CREATE INDEX IF NOT EXISTS idx_otp_challenges_phone_ip_created
    ON otp_challenges (phone_number, ip_address, created_at);

-- 4. Index for lockout check: phone + status + blocked_at
CREATE INDEX IF NOT EXISTS idx_otp_challenges_phone_blocked
    ON otp_challenges (phone_number, status, blocked_at);
