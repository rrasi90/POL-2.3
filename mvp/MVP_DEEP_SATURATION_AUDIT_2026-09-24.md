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

### DSA-001 — Mobile access token is memory-only in audited source
Class: CONFLICT / P0 security-lifecycle review.
mvp/apps/mobile/src/api.ts declares a module-level access token and does not use SecureStore/Keychain persistence. No mobile refresh flow is present in that file.
This conflicts with the device-evidence note claiming the session survives app restart.
Required closure: cold process-kill/relaunch test on the current APK plus runtime-storage inspection. Then adopt one canonical policy; do not infer behavior.

### DSA-002 — Mobile 401 recovery is absent
Class: GAP / P1, dependent on auth policy.
The audited mobile API client sends the bearer token but does not implement the web client's documented refresh-and-single-retry lifecycle.
Required closure: after the existing refresh-token-rotation decision is closed, implement the canonical mobile lifecycle.

### DSA-003 — Mobile explicit logout/revocation surface is absent
Class: GAP / P1.
The audited Account screen has profile, notifications, preferences and theme controls, but no logout/revoke-session action.
Backend session revocation contracts already exist.
Required closure: implement after auth policy reconciliation.

### DSA-004 — Cross-cutting state coverage must become an executable matrix
Class: GOVERNANCE GAP / P1.
The Master Tree specifies global states, but the current delivery controls do not yet provide one machine-checkable matrix proving that every mutation/query has the applicable state coverage.
Required closure: add a cross-cutting state/action matrix and use it as a QA gate.

### DSA-005 — Notification actionability is contract-limited
Class: CONTRACT GAP.
The notification domain models read state and deep links, but current live notification API evidence shows that the runtime projection does not return read state and no mark-read route exists.
Required closure: keep the current UI honest; close the backend notification contract before adding unread/deep-link claims.

### DSA-006 — Live commerce closure remains open
Class: EXECUTION GAP.
Current delivery records explicitly leave live basket → allocation → checkout → order lifecycle and checkout idempotency replay open.
Required closure: execute against current PG18/FastAPI environment and capture evidence on the current commit.

### DSA-007 — Night-theme verification is not equivalent to token existence
Class: QA GAP.
Mobile Light/Night token infrastructure exists and recent device retest closed the earlier runtime wiring defect, but screen-by-screen visual verification remains a distinct gate.
Required closure: verify every applicable mobile screen in both themes, including dialogs, keyboard states and error/empty/loading surfaces.

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
10. Re-run full regression.
11. Perform final independent second pass.
12. Only then update delivery DoD.