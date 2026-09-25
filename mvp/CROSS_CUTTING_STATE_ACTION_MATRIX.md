# POL MVP — Cross-Cutting State / Action Matrix

Version: 1.0 — 2026-09-24
Purpose: single executable governance matrix for cross-cutting behavior. This is complementary to the screen matrix; it does not replace domain state machines.

## Status vocabulary
- VERIFIED — implementation and evidence support the behavior.
- IMPLEMENTED — source exists; current runtime evidence is incomplete.
- GAP — required behavior is absent or contract is incomplete.
- CONFLICT — sources/evidence disagree.
- OPEN_DECISION — behavior must not be invented.
- OUT_OF_SCOPE — explicitly excluded from MVP.

## Required dimensions
Every in-scope action must be evaluated for: Preconditions | Validation | Loading | Success | Empty/No-op | Error | Retry | Timeout | Conflict/Stale | Offline | 401 | 403 | Rate limit | Duplicate/Idempotency | Tenant scope | Audit | Notification | Recovery | Accessibility/RTL | Theme | QA evidence.

## Critical action matrix

| ID | Capability / Action | Tenant | Permission | Loading | Error/Retry | Offline | Conflict | Idempotency | Audit | Notification | Status | Evidence / next |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CC-01 | Request OTP | user/phone | public | yes | yes | no | n/a | request throttling | auth event | SMS | IMPLEMENTED | OTP operational config + auth tests; targeted abuse runtime test |
| CC-02 | Verify OTP | user/phone | public | yes | yes | no | expired/blocked | OTP attempt guard | auth event | auth result | IMPLEMENTED | identity/tenant tests; targeted replay test |
| CC-03 | Refresh session | organization | session | yes | yes | no | refresh policy OPEN | n/a | session event | security notification if policy requires | OPEN_DECISION | D-018 rotation policy |
| CC-04 | Revoke current session | organization | authenticated | yes | yes | no | already revoked | idempotent desired | audit | optional security | IMPLEMENTED | backend contract; mobile UI GAP |
| CC-05 | Switch organization | organization | membership | yes | yes | no | membership changed | request-safe | audit | context change optional | IMPLEMENTED | identity/membership runtime tests |
| CC-06 | Search catalog | organization | catalog.read | yes | yes/retry | limited | stale catalog | n/a | optional | none | IMPLEMENTED | live smoke; pagination/search deep audit |
| CC-07 | Add basket item | organization | basket.write | yes | yes/retry | policy needed | basket version | mutation-safe | domain event | optional | IMPLEMENTED | basket version test; offline policy audit |
| CC-08 | Allocation preview | organization | checkout.read | yes | yes/retry | forbidden | inventory/MOQ/MOV changes | request-safe | event/audit | optional | IMPLEMENTED | allocation tests; live E2E open |
| CC-09 | Create order / checkout | organization | checkout.write | yes | yes/retry | forbidden | revalidation | REQUIRED | audit/event | order notification | IMPLEMENTED | gateway/idempotency source; live replay open |
| CC-10 | Vendor accept order | organization | vendor.order.accept | yes | yes/retry | forbidden | state conflict | REQUIRED | audit | retailer notification | IMPLEMENTED | order state tests; live lifecycle open |
| CC-11 | Partial acceptance approve | organization | retailer.order.approve | yes | yes/retry | forbidden | proposal closed/stale | REQUIRED | audit | vendor notification | IMPLEMENTED | timeline-derived proposal; edge-case audit |
| CC-12 | Dispatch order | organization | vendor.delivery.dispatch | yes | yes/retry | forbidden | state conflict | REQUIRED | audit | delivery notification | IMPLEMENTED | delivery OTP persistence fixed; runtime E2E open |
| CC-13 | Confirm delivery / POD | receiver/order | receiver token | yes | yes/retry | forbidden | OTP mismatch/expired | REQUIRED | audit | delivered notification | IMPLEMENTED | POD tests; device flow audit |
| CC-14 | Create dispute | organization/order | retailer.dispute.create | yes | yes/retry | policy needed | duplicate dispute | REQUIRED | audit | ops notification | IMPLEMENTED | dispute tests; media security audit |
| CC-15 | Resolve dispute | organization/order | ops.dispute.resolve | yes | yes/retry | forbidden | already resolved | REQUIRED | audit | retailer/vendor notification | IMPLEMENTED | settlement adjustment tests |
| CC-16 | Create support case | organization | support.create | yes | yes/retry | policy needed | duplicate | REQUIRED | audit | support notification | IMPLEMENTED | support tests; attachment audit |
| CC-17 | Add support message | organization/case | support.message | yes | yes/retry | policy needed | closed case | REQUIRED | audit | recipient notification | IMPLEMENTED | support tests; internal/customer visibility audit |
| CC-18 | Update profile | user/org | profile.write | yes | yes/retry | no | concurrent edit | safe retry | audit where sensitive | none | IMPLEMENTED | API + UI; stale/concurrency audit |
| CC-19 | Update notification preferences | user | notification.manage | yes | yes/retry | no | concurrent edit | safe retry | audit optional | none | IMPLEMENTED | API + mobile UI; preference semantics audit |
| CC-20 | Read notifications | user | notification.read | yes | yes/retry | cached only if supported | stale | n/a | none | none | CONTRACT GAP | live API omits read/deep-link fields; G-005/G-004 |
| CC-21 | Mark notification read | user | notification.write | yes | yes/retry | no | already read | idempotent | audit optional | none | GAP | no current HTTP route |
| CC-22 | Vendor inventory update | organization | vendor.inventory.write | yes | yes/retry | no | concurrent inventory | REQUIRED where mutation retries | audit | optional | IMPLEMENTED | source/runtime concurrency audit |
| CC-23 | Invoice read | organization | finance.read | yes | yes/retry | cache only if supported | timing policy | n/a | financial audit | optional | OPEN_DECISION | invoice timing still OPEN |
| CC-24 | Payment verification | organization/order | finance.verify | yes | yes/retry | forbidden | duplicate/out-of-order | REQUIRED | financial audit | payment notification | IMPLEMENTED | payment RBAC/idempotency tests |
| CC-25 | Settlement adjustment | organization/order | ops.finance.adjust | yes | yes/retry | forbidden | duplicate adjustment | REQUIRED | immutable financial audit | settlement notification | IMPLEMENTED | dispute/settlement tests |
| CC-26 | Refund creation | organization/order | ops.finance.refund | yes | yes/retry | forbidden | refund > paid / duplicate | REQUIRED | immutable financial audit | refund notification | IMPLEMENTED | refund tests; end-to-end financial drill open |
| CC-27 | Logout mobile | user/session | authenticated | yes | yes | no | already revoked | idempotent | session audit | security optional | IMPLEMENTED | source remediation on audit branch; device/CI verification pending |
| CC-28 | Mobile 401 recovery | organization | authenticated | yes | retry once | no | refresh failure | safe retry | auth audit | session-expired UX | IMPLEMENTED | source has single-flight refresh + one retry; current CI/device evidence remains required |
| CC-29 | Mobile cold restart | user/session | authenticated | boot | boot error | n/a | stale session | n/a | auth event | none | IMPLEMENTED | SecureStore restoration exists; current APK cold-restart evidence remains required |
| CC-30 | Mobile theme switch | user/device | authenticated | n/a | n/a | n/a | system mode | n/a | none | none | IMPLEMENTED | source remediation; screen-by-screen visual evidence open |

## Closure rule
A row is not VERIFIED merely because the API or screen exists. It must have current evidence for the behavior dimensions that matter to that action.

## Next matrix expansion
After the critical-action pass, expand this matrix to every screen action in MVP_SCREEN_MATRIX.md. Any action without a row is a traceability defect.