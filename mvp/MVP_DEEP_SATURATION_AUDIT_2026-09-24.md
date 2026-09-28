# POL MVP — Deep Saturation Audit & Closure Plan

Audit ID: POL-MVP-DSA-2026-09-24
Audit branch: audit/mvp-deep-saturation-2026-09-24
Baseline commit: 091790a

Purpose: exhaustive review of the MVP beyond screen-count and happy-path completeness, covering product, UX states, domain, API, data, security, privacy, mobile/web lifecycle, operations, observability, release, and evidence.

## 1. Execution principle

This audit is evidence-first.

Every finding is classified as VERIFIED, IMPLEMENTED/UNVERIFIED, GAP, CONFLICT, BLOCKED_EXTERNAL, OUT_OF_SCOPE, or OPEN_DECISION.

No new feature is implemented merely because it is common in other applications.

## 2. Ordered audit path

### Stage A — Source-of-truth lock
1. Lock Decision Register.
2. Lock CURRENT_SOURCE_OF_TRUTH.
3. Reconcile MVP Definition / PRD / domain authorities.
4. Reconcile API map, screen matrix and known gaps.
5. Separate historical evidence from current evidence.

### Stage B — Repository topology
6. Enumerate backend, web, mobile, migrations, workers, CI and scripts.
7. Build file-level implementation map.
8. Detect duplicate runtimes, duplicate business logic and stale artifacts.
9. Identify test/evidence infrastructure.

### Stage C — Capability closure
10. Enumerate every MVP capability.
11. For each capability map persona, surface, screen, action, input, output, domain state, UI state, API, DB, event, notification, audit, permission and QA evidence.
12. Mark missing closure without inventing behavior.

### Stage D — Cross-cutting runtime audit
13. Loading. 14. Empty. 15. Success. 16. Validation. 17. Error. 18. Retry. 19. Timeout. 20. Conflict. 21. Offline. 22. Stale data. 23. Unauthorized. 24. Forbidden. 25. Session expired. 26. Rate limited. 27. Maintenance. 28. Partial failure. 29. Process restart/recovery. 30. Duplicate submission.

### Stage E — Identity/security/privacy
31. OTP lifecycle and abuse controls.
32. Access/refresh token lifecycle.
33. Session revocation.
34. Secure credential storage.
35. Tenant isolation.
36. RBAC / membership.
37. Resource-level authorization.
38. Enumeration resistance.
39. Rate limiting.
40. Secrets.
41. Logs/PII.
42. Network security.
43. File/media security.
44. Consent and privacy lifecycle.
45. Data retention/deletion/export.

### Stage F — Commerce integrity
46. Basket versioning.
47. Allocation determinism.
48. Inventory reservation.
49. Price/MOQ/MOV changes.
50. Checkout idempotency.
51. Order lifecycle.
52. Partial acceptance.
53. Invoice timing.
54. Payment attempts.
55. Settlement.
56. Refund.
57. Dispute/adjustment.
58. Delivery/POD.
59. Reconciliation.

### Stage G — Application lifecycle
60. Web navigation/back/refresh/deep-link.
61. Mobile launch/resume/background/kill/relaunch.
62. Network transitions.
63. Cache invalidation.
64. Optimistic/pessimistic mutation behavior.
65. App update compatibility.
66. Maintenance/degraded service.
67. Feature/config flags where actually required.

### Stage H — UX/platform quality
68. Responsive.
69. RTL/mixed direction.
70. Accessibility.
71. Dynamic text.
72. Keyboard/input behavior.
73. Touch targets.
74. Theme Light/Night.
75. Device permissions.
76. Notifications/deep links.
77. Media upload.
78. Large data/pagination.
79. Search/filter/sort.

### Stage I — Operations/support
80. Support case lifecycle.
81. Internal vs customer-visible communication.
82. Escalation.
83. SLA.
84. Exception queues.
85. Field operations.
86. Delivery failure recovery.
87. Audit trails.
88. Operator tooling.

### Stage J — Observability/release
89. Request/correlation IDs.
90. Structured logs.
91. Domain events.
92. Outbox retries/dead-letter/replay.
93. Crash/error telemetry.
94. Business analytics event taxonomy.
95. Health/readiness.
96. Backup/restore.
97. Migration rollback/recovery.
98. CI/CD.
99. Environment separation.
100. Release/version policy.

## 3. Current evidence already confirmed

The repository already contains substantial hardening beyond a normal MVP: membership-based tenant authorization; session/device domain; notification domain; transactional outbox; checkout idempotency/fingerprint protection; basket optimistic versioning; state-machine matrices; dispute/settlement separation; media/presigned-upload architecture; privacy/consent data model; current mobile CI cycles; structural and anti-vibe audits.

Therefore this audit must verify closure and source/evidence consistency rather than recreate those systems.

## 4. Findings confirmed in this pass

### DSA-001 — Mobile credential persistence is now SecureStore-backed
Class: SOURCE REMEDIATED / DEVICE-UNVERIFIED.
Current mvp/apps/mobile/src/api.ts stores access, refresh, and role/session metadata with Expo SecureStore; the in-memory access token is restored from SecureStore on process restart.
Residual closure: cold process-kill/relaunch on the current APK plus runtime-storage inspection remains required before treating device persistence as independently verified.

### DSA-002 — Mobile 401 recovery is now implemented
Class: SOURCE REMEDIATED / RUNTIME-UNVERIFIED.
Current mvp/apps/mobile/src/api.ts implements a single-flight refresh-and-single-retry flow on HTTP 401, restores session from SecureStore, and clears the session when refresh fails. The current backend returns a replacement refresh token and the mobile client persists that replacement.
Residual closure: execute/retain the mobile runtime regression evidence against the current release build. D-018 refresh-token rotation remains an explicit policy decision; the source behavior is documented as implementation state only.

### DSA-003 — Mobile explicit logout/revocation surface was absent; source remediation applied
Class: IMPLEMENTED / UNVERIFIED.
The audited Account screen initially had no logout/revoke-session action. A source remediation was applied on this audit branch: the mobile API client now exposes DELETE /api/v1/auth/sessions/current, Account exposes an explicit خروج از حساب action, and App returns to the login route after successful revocation.
Required closure: fresh mobile typecheck + functional regression + device logout/revocation test.

### DSA-004 — Cross-cutting state coverage matrix
Class: IMPLEMENTED / CI VERIFIED / EXPANSION REMAINS.
A machine-checkable-by-test cross-cutting state/action matrix now exists at `mvp/CROSS_CUTTING_STATE_ACTION_MATRIX.md`, and `scripts/test_cross_cutting_state_matrix.py` is executed inside the full verification suite.
Current evidence: backend verification CI run #805 passed 526/526.
Residual closure: expand the matrix from the current critical-action set to every MVP screen action before final DoD closure.

### DSA-005 — Notification actionability
Class: SOURCE REMEDIATED / CURRENT CI CERTIFICATION BLOCKED.
The current source now exposes durable inbox listing, unread filtering/counts, deep links, mark-one-read and mark-all-read routes, while `/notifications` also projects read state and deep-link data.
Current evidence: notification HTTP tests are included in the 526/526 green verification suite.
Residual closure: browser/device notification navigation and push-provider delivery remain separate runtime evidence.

### DSA-006 — Commerce integration closure
Class: AUTOMATED INTEGRATION VERIFIED / DEPLOYED-LIVE UNVERIFIED.
Current Master E2E completes the basket → allocation → checkout → order → vendor response → delivery → payment → dispute → notification chain on PostgreSQL 18, including checkout/idempotency and notification regression coverage.
Current evidence: 526/526 backend verification tests passed on run #805.
Residual closure: deployed environment / real-provider execution is not claimed from local CI evidence.

### DSA-007 — Night-theme verification is not equivalent to token existence
Class: QA GAP.
Mobile Light/Night token infrastructure exists and recent device retest closed the earlier runtime wiring defect, but screen-by-screen visual verification remains a distinct gate.
Required closure: verify every applicable mobile screen in both themes, including dialogs, keyboard states and error/empty/loading surfaces.

### DSA-009 — Baseline API security response headers added
Class: IMPLEMENTED / CI VERIFIED.
The FastAPI transport now emits X-Content-Type-Options, X-Frame-Options, Referrer-Policy and Permissions-Policy, while preserving X-Correlation-ID.
A transport regression test was added and passed in backend verification CI run #805.

### DSA-010 — Duplicate operational configuration constant removed
Class: RESOLVED.
`VENDOR_ACCEPTANCE_TIMEOUT_REASON` was declared twice in scripts/operational_config.py. The duplicate declaration was removed without changing its effective value.
### DSA-008 — Web/mobile security hardening needs runtime evidence
Class: SECURITY VERIFICATION GAP.
Repository search found strong identity/tenant test coverage, but this audit has not yet established fresh evidence for all of: secure client credential handling, HTTP security headers, enumeration resistance, rate limits beyond OTP, upload security and PII leakage in logs.
Required closure: inspect implementation and run targeted security tests; do not mark PASS from documentation alone.

## 5. Closure rule

A finding is closed only when: canonical source is unambiguous; implementation exists; automated evidence exists where automatable; runtime/device evidence exists where runtime behavior matters; no contradictory document remains; the relevant gap/decision register is updated.

## 6. Final release gate

The MVP must not be called final merely because all screens are implemented.

Final closure requires:
Capability × Action × State × Permission × Tenant × API × Domain × Event × Notification × Audit × Platform × Theme × Accessibility × Recovery × QA Evidence

for every in-scope production capability.

## 7. Next execution order
1. Close/reconcile DSA-001 through DSA-003.
2. Build the cross-cutting state/action matrix.
3. Execute commerce live E2E + idempotency.
4. Execute security verification.
5. Execute mobile lifecycle/device matrix.
6. Execute notification/deep-link closure.
7. Execute accessibility/RTL/theme matrix.
8. Execute observability/recovery verification.
9. Reconcile all GAP/OPEN/CONFLICT registers.
10. Re-run the full backend and mobile CI gates after each source remediation.
11. Keep main untouched until the audit branch has a clean current CI evidence set.
10. Re-run full regression.
11. Perform final independent second pass.
12. Only then update delivery DoD.
### DSA-011 — Web access/refresh credentials no longer persist in localStorage
Class: SOURCE REMEDIATED / CURRENT CI CERTIFICATION BLOCKED / BROWSER VERIFICATION PENDING.
Current mvp/apps/web/src/lib/auth/store.ts keeps the access token in memory and stores only non-secret profile metadata in localStorage. The web refresh credential is carried by the server-managed `pol_refresh` HttpOnly/Secure/SameSite cookie.
Required closure: browser-runtime/XSS verification and production cookie configuration evidence; current remediation CI is not currently certifiable because GitHub Actions jobs are failing before useful step execution.

### DSA-012 — Browser-to-API CORS policy remediated
Class: SOURCE REMEDIATED / CI VERIFIED.
The FastAPI transport uses explicit environment-scoped CORS; production requires POL_CORS_ORIGINS and wildcard production CORS is rejected. A transport test covers an allowed localhost origin and a blocked external origin.
Required closure: deployment configuration must supply the intended production origins; the source/transport tests exist, but current remediation CI is not currently certifiable because GitHub Actions jobs are failing before useful step execution.

## 8.5 — Remediation verification checkpoint — 2026-09-25

- Remediation branch: `remediation/full-closure-2026-09-25`
- Head: `69a6a2536cc7296c840cbf76012656b65834ea5a`
- Backend verification CI run #805: **526/526 passed, 0 failed, 0 skipped**.
- Mobile verification run #202: **success**, including Expo Android export and regression QA.
- Canonical migration chain verified through migration `040_dispute_notification_template.sql`.
- Master E2E now reaches notification/inbox closure and passes on PostgreSQL 18.
- Remaining release evidence is explicitly limited to areas requiring a deployed browser/device/provider environment or unresolved contractual/product decisions; these are not converted to PASS by source-only evidence.


## 8.6 — Current remediation branch checkpoint — 2026-09-26

- Current branch: `remediation/full-closure-2026-09-25`.
- Current remediation head: `54e5aab3061bd8ec898f06b1ac37d903f64e4b28` at the time of this reconciliation.
- Source remediation has continued beyond checkpoint 8.5, including authentication tenant switching, retailer/vendor role boundaries for commerce decisions, formal dispute opening, and Expo SDK 57 toolchain alignment.
- Historical local/device evidence from 2026-09-24 remains valid as historical evidence for the tested build; it does not certify the current remediation head.
- Current pull-request CI runs for the remediation branch have repeatedly produced failed jobs before useful step-level execution; job steps are empty and job-log retrieval is unavailable. This is an evidence/execution blocker, not a source-level PASS or FAIL result.
- The old 526/526 backend and mobile success statements remain historical evidence only.
- Remaining non-technical gates are explicit governance/product decisions (D-018 refresh-token policy wording, invoice timing, D-024 storefront-write contract) and deployment/provider/browser/device evidence that cannot be honestly manufactured from repository inspection.
