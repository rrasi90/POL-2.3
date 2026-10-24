# -*- coding: utf-8 -*-
"""
POL Operational Configuration Contract
Canonical operational parameters for POL B2B FMCG Platform (Ahvaz Pilot).
"""

# Inventory & Reservation
RESERVATION_TTL_MINUTES = 15
ALLOCATION_PLAN_TTL_MINUTES = 15

# SLAs
VENDOR_ACCEPTANCE_SLA_HOURS = 2
VENDOR_ACCEPTANCE_TIMEOUT_REASON = "VENDOR_TIMEOUT"
DISPUTE_FILING_WINDOW_HOURS = 4
SUPPORT_FIRST_RESPONSE_SLA_HOURS = 1
SUPPORT_RESOLUTION_SLA_HOURS = 24

# Authentication & Security (D-018; amended 2026-10-25)
OTP_CODE_LENGTH = 6
OTP_TTL_SECONDS = 120
OTP_RESEND_INTERVAL_SECONDS = 60
OTP_MAX_ATTEMPTS = 5
OTP_LOCKOUT_MINUTES = 10
OTP_RATE_LIMIT_COUNT = 3          # D-018: max OTP requests per window
OTP_RATE_LIMIT_WINDOW_MINUTES = 5 # D-018: rate-limit window (phone+IP scoped)
OTP_SALT_BYTES = 16               # PBKDF2 salt size
OTP_PBKDF2_ITERATIONS = 100_000   # PBKDF2 iteration count
SESSION_TTL_HOURS = 720           # 30 days — D-018: refresh session lifetime
JWT_ALGORITHM = "HS256"
JWT_ISSUER = "pol-platform"
JWT_AUDIENCE = "pol-api"
JWT_ACCESS_TTL_SECONDS = 900      # 15 minutes — D-018: access token lifetime
REFRESH_TOKEN_BYTES = 32          # 256-bit opaque refresh token

# Finance & Settlement (Pilot Phase Ahvaz)
PILOT_COMMISSION_RATE = 0.000
PAYMENT_CUSTODY_MODEL = "NON_CUSTODIAL_DIRECT"

# Notifications & Messaging
NOTIFICATION_MAX_RETRIES = 3
NOTIFICATION_BACKOFF_SECONDS = [30, 120, 600]
NOTIFICATION_DEFAULT_CHANNELS = ["IN_APP", "SMS"]

# Operating Calendar (Ahvaz Wholesale Market / Shahr-e-Bonakdaran)
MARKET_BUSINESS_HOURS = {
    "open_hour": 8,
    "close_hour": 18,
    "working_days": [0, 1, 2, 3, 5, 6],  # Sat, Sun, Mon, Tue, Wed, Thu (Fri=4 is weekend)
    "weekend_day": 4,  # Friday
    "timezone": "Asia/Tehran"
}
