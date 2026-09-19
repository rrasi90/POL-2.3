# Stage 08 — Authentication Contract Audit — 2026-09-19

## Scope
Audit D-018 against the current authentication implementation without resolving the separately undecided refresh-token rotation policy.

## Canonical D-018 contract
- OTP: 4 digits.
- OTP TTL: 120 seconds.
- Resend interval: 60 seconds.
- Request rate limit: 3 requests / 5 minutes, scoped by phone + IP.
- Failed verification attempts: 5.
- Phone lockout: 10 minutes after the fifth failed attempt.
- Access token: JWT, 15-minute lifetime.
- Refresh session: server-tracked, 30-day lifetime.
- Refresh-token rotation: **UNDECIDED**; current non-rotating behavior is implementation behavior, not a final policy.
- Session revocation must invalidate access-token use through server-side session status.
- Membership context is authoritative from active organization membership; JWT claims are cached authorization context.

## Source audit

| Area | Evidence | Result |
|---|---|---|
| OTP length | `OTP_CODE_LENGTH=4`; request schema requires exactly 4 digits | ALIGNED |
| OTP TTL | `OTP_TTL_SECONDS=120`; DB expiry uses 120 seconds | ALIGNED |
| Resend interval | API response exposes `OTP_RESEND_INTERVAL_SECONDS=60` | ALIGNED |
| Rate limit | AuthService enforces 3/5min phone+IP with PostgreSQL advisory transaction lock | ALIGNED |
| Lockout | AuthService blocks after 5 failed attempts; request path enforces 10-minute phone-scoped lockout | ALIGNED |
| OTP hashing | PBKDF2-HMAC-SHA256, random salt, timing-safe comparison | ALIGNED |
| One-time consumption | Challenge is selected `FOR UPDATE` while PENDING; successful verification changes status to VERIFIED | FIXED in Stage 08 |
| Access JWT | HS256, issuer/audience, required claims, 900-second exp | ALIGNED |
| Session lifetime | `SESSION_TTL_HOURS=720`; DB session expiry is 30 days | ALIGNED |
| Session revocation | `validate_access_token` rejects non-ACTIVE sessions | ALIGNED |
| Membership authority | Active `organization_memberships` is checked against JWT org context | ALIGNED |
| Organization switch | Session active organization is updated and a new JWT is issued | ALIGNED |
| Refresh rotation | Current implementation does not rotate refresh token | **POLICY UNDECIDED — no change made** |
| Production OTP source | Production uses cryptographically random OTP; non-production may expose deterministic `1234` test code | CARRIED to Stage 09 |
| Secrets | JWT signing secret is environment-backed and fails closed when absent | ALIGNED |
| Provider delivery | No live SMS provider credential/certification established | EXTERNAL_PENDING / Stage 09 |

## Stage 08 change
The OTP verification query now locks the currently pending challenge with PostgreSQL `FOR UPDATE`. This prevents concurrent verification requests from both consuming the same OTP successfully. A regression test `T-AC20` was added.

## Explicit non-decisions
Stage 08 does **not** decide refresh-token rotation. D-018 remains authoritative and undecided on that point. Stage 10 owns closure of that decision/implementation gap.

## Remaining production boundary
The deterministic non-production OTP path and real SMS/provider boundary remain in Stage 09. No claim is made that live provider delivery is certified.

## Verification
- Prior full regression before Stage 08: Run #429, 214/214 expected after Stage 07 route repair; artifact 10578268045, digest `sha256:5b20fffcb4f45e9b418b23870cdc7d578fb642339ec25145709234985ac30f04`.
- Stage 08 introduced targeted auth source/test changes; fresh CI certification is required before closure.
