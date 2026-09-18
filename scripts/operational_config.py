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
DISPUTE_FILING_WINDOW_HOURS = 4
SUPPORT_FIRST_RESPONSE_SLA_HOURS = 1
SUPPORT_RESOLUTION_SLA_HOURS = 24

# Authentication & Security
OTP_CODE_LENGTH = 4
OTP_TTL_SECONDS = 120
OTP_MAX_ATTEMPTS = 5
OTP_LOCKOUT_MINUTES = 10
SESSION_TTL_HOURS = 0.25  # 15 minutes — D-018: access token lifetime

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
