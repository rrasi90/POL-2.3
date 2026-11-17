# POL-2.3 Implementation Selection Matrix

**Baseline:** `main` @ `fbcdd7448d809a3281cc1ea8c43218d42e8762ca`
**Date:** 2026-11-17

| Capability | Candidate(s) | Selected direction | Rejected / deferred behavior | Required acceptance evidence |
|---|---|---|---|---|
| Product scope | #44 vs current main | D-014 multi-vendor MVP; #44 wording now ported | D-003 single-vendor MVP wording is historical and must not remain as active scope | Cross-document consistency across Product Vision, Decision Register, MVP Definition and user journeys |
| Android QA gate | merged #43 vs #40 | Keep #43's stronger current-main gate including TODO-012..017, duplicate/malformed/unknown IDs and fail-closed semantics | Do not downgrade to #40's older 82-row gate | Gate fixture tests; blocked real TODO ledger must continue to skip APK jobs |
| Expo dependencies | merged #46 vs #45 | Keep #46's Expo `~57.0.31` and React `19.2.3`; port only #45 native `expo run:*` scripts | Do not copy #45's older Expo `~57.0.24` | Expo doctor, typecheck, export and native-run script validation |
| Mobile motion | #29 vs #40 | #40 is the starting candidate; salvage #29-only fixes where proven superior | No wholesale merge of dirty #29 or stale workflow/gate from #40 | Motion interruption, reduced-motion, cleanup, RTL, Android runtime and regression suites |
| OTP policy | #49 vs #50 vs current D-018 | No policy decision accepted yet. Treat six-digit behavior as a proposal requiring coherent D-018 amendment and security review | Do not silently change auth policy or conflate auth/delivery lifecycle | Decision Register and API/schema/UI consistency; OTP tests on implementation; separate policy semantics |
| Delivery OTP migration | #50 migration 077 | Deferred until raw/hash/reference semantics, outbox delivery and in-flight challenge remediation are proven | No direct random rotation or nullification that strands an active recipient challenge | Disposable PostgreSQL 18 migration test with legacy terminal and active records; recipient-only delivery/verification tests |
| Test/security matrices | #47 | Preserve unique tests and source-backed matrices after diffing against current main | Do not import stale test results as current certification or duplicate brittle tests | Backend/web tests, API contracts, RBAC/OWASP, traceability consistency and evidence references |
| Visual QA and Cartona | #51 | Preserve valid captures and research artifacts with provenance and rights metadata | Do not treat static inference as observed runtime behavior; no stale/placeholder screenshots | Verify all assets, page/viewport/theme identity, source provenance and current UI relation |
| Admin routes and retailer mocks | #52 | Port route uniqueness and retailer mock fixes only after current implementation/contract comparison | Do not claim privacy correctness from route registration alone; do not regress vendor mocks | Full backend suite, privacy lifecycle, role authorization, route inventory, retailer/vendor mock isolation and functional QA |

## Quality rule

Choose by correctness, security, reliability, maintainability, test quality, compatibility and current-SHA evidence. A newer or larger PR does not automatically supersede an older implementation.