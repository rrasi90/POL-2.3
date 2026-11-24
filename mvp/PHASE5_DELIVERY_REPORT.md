# POL MVP — Phase 5 Delivery Report

**Date:** 2026-09-26  
**Branch:** `main`  
**Report baseline:** remediation branch current source; historical baseline retained only as provenance.  
**Report policy:** this is a living delivery report; do not store a mutable "current HEAD" claim here. Repository HEAD is authoritative via Git.  
**Authority:** `DECISION_REGISTER.md` (D-001…D-028) → CURRENT_SOURCE_OF_TRUTH → `BUILD_PLAN.md` → module evidence  

---

## Current remediation reconciliation — 2026-09-25

**Branch:** `remediation/full-closure-2026-09-25`  
**Current source state:** the remediation branch has continued well beyond the historical 2026-09-24 delivery snapshot. Do not use the historical phase tables below as the current release state.

### Current evidence
- Local evidence recorded in `mvp/LOCAL_EXECUTION_TRACKER.md`: LOCAL-01 Night theme **PASS**, LOCAL-02 live basket→allocation→checkout→order **16/16 PASS**, LOCAL-03 checkout idempotency replay **12/12 PASS**, LOCAL-04 post-remediation device smoke **PASS**.
- Current remediation source now includes canonical barcode matching/candidate quarantine, vendor continuous inventory scan/publish, admin SLA overrides, admin category/broadcast routes, global returns, partial-acceptance listing, payment verification variants, dispute resolution, durable inbox routes, and catalog candidate review.
- The old 497-test / run-`805` claims in this document are historical and must not be used as current CI evidence.

### Current CI state
Fresh pull-request runs triggered by remediation commits are currently **failing before useful step-level execution** (the latest mobile and independent verification runs complete within a few seconds; the independent run exposes no executed job steps). Therefore no new green CI claim is made from those runs until GitHub Actions produces actual step logs.

### Remaining closure classes
1. **Open product/security decisions:** D-018 refresh-token rotation policy and invoice timing. D-024 currently defines storefront as a read/order surface; no separate write contract is canonical.
2. **Runtime/deployment evidence:** production browser cookie configuration, deployed provider execution, push-provider delivery, production metrics/observability.
3. **Partial capability:** O-07 risk/reliability and any other explicitly documented limited surfaces.
4. **Fresh CI certification:** rerun the full backend and mobile gates after the current GitHub Actions execution blocker is cleared.

## 1. Phases done

| Phase | Name | Status | Evidence |
|-------|------|--------|----------|
| DS | Deep Saturation Reconciliation | **COMPLETED / CONTROL ADDED** | `MVP_DEEP_SATURATION_AUDIT_2026-09-24.md`, `CROSS_CUTTING_STATE_ACTION_MATRIX.md`, CI green on merged commit `23976ac` |
| 0 | Discovery & Artifacts | **DONE** | `MVP_SCREEN_MATRIX.md`, `MVP_API_MAP.md`, `MVP_KNOWN_GAPS.md`, BUILD GATE 0 checklist |
| 1 | Foundation + Design System | **DONE** | packages typecheck/build green; tokens Light+Night; shell + middleware role gates |
| 2 | Web MVP | **DONE (impl + partial e2e)** | 68 screens; ≥3 QA cycles/module; 19 VERIFIED live (cycle 5) |
| 3 | Android MVP (Expo) | **IN PROGRESS / REMEDIATED SOURCE** | Supported parity is implemented; G-023…G-026 and D-028 source defects are remediated. Remaining executable evidence: current-device cold-relaunch/storage inspection, screen-by-screen Light/Night visual QA, and live checkout/idempotency evidence. |
| 4 | Global QA + Regression | **SOURCE REMEDIATED / FRESH CI BLOCKED** | Historical green suites remain evidence only. Current remediation runs create jobs that fail before executing any job step; live basket→allocation→checkout→order E2E + idempotency replay remain separate runtime evidence. |
| 5 | Delivery + Final Audit | **REOPENED** | Phase 3 mobile verification is now through Cycle 3; delivery remains open for Night visual verification, live checkout/idempotency E2E, and final reconciliation. |

---

## 2. Remaining gaps

| ID | Gap | Status | Owner / next |
|----|-----|--------|--------------|
| G-003 | Catalog path/search contract | **SOURCE RESOLVED / CI PENDING** | Canonical search implementation and compatibility route exist on the remediation branch. |
| G-004 | Notification inbox/read contract | **SOURCE RESOLVED / CI PENDING** | Canonical inbox routes and notification projection exist; fresh CI certification remains pending. |
| G-007/008/009/010/011/012/013/015/017/019/020/021 | Historical missing HTTP families | **SOURCE RESOLVED / CI PENDING** | Current remediation branch contains live application routes and corresponding tests; stale shell-only state must not be used as current status. |
| G-006 | Corporate public routes | **RESOLVED** | Current screen matrix and web route set contain the corporate public surfaces. |
| G-029 | Web token persistence in localStorage | **SOURCE REMEDIATED / BROWSER PENDING** | Access token is memory-only; refresh credential is server-managed HttpOnly/Secure cookie. |
| G-030 | Browser-to-API CORS policy | **SOURCE REMEDIATED / DEPLOYMENT VERIFY** | Explicit environment-scoped CORS is enforced and wildcard production CORS is rejected. |
| D-024 | Vendor Discovery / Storefront | **RESOLVED SCOPE** | Storefront is a first-class read/order surface. Any future write fields require an explicit scope extension; D-024 does not define them. |
| OP-11 | Permission catalog + audit | **SOURCE IMPLEMENTED / FRESH QA PENDING** | Canonical permission catalog, tenant-scoped grant/revoke, effective access, and append-only permission audit are now implemented. |
| Refresh-token rotation | D-018 policy | **OPEN DECISION** | Runtime behavior must not be promoted to final policy without an explicit decision. |
| Invoice timing | on ACCEPTED default | **OPEN** | confirm before finance e2e |
| Phase 3 remaining | Night visual verification + current-device cold relaunch/storage evidence | **OPEN** | D-028 and G-023…G-026 source remediated; execute remaining runtime/device gates |
| Phase 4 remaining | Live basket POST → allocation → checkout → order lifecycle + idempotency replay | **OPEN** | runtime execution evidence still required |
| WAVE-02 | OpenPencil MCP design board | **BLOCKED_EXTERNAL** | start OpenPencil app (B-02) |

**Resolved in current reconciliation:** G-001, G-002, G-005, G-022, G-023, G-024, G-025, G-026 (device/local retest PASS on 2026-09-24), plus mobile logout source remediation and API security-header/CORS hardening on audit branch merged as commit `23976ac`.

**Web screen coverage (cycle 5 baseline):** 68 total — **40 IMPLEMENTED / 19 VERIFIED / 8 GAP / 1 N/A / 0 PENDING**.

**Mobile implementation coverage:** Field F-01…F-05 + Retailer/Vendor/Ops foundation surfaces implemented; not promoted to VERIFIED pending mobile QA evidence.

---

## 3. Structural + vibe defects fixed

See `BUILD_PLAN.md` §11 defect log (full table). Highlights:

- Restored missing `scripts/api/**`, 62 research modules/tests, `application_boundary` storefront/search methods → live 200s.
- Decision drift: `OTP_CODE_LENGTH` 6→4 (D-018); login + delivery schemas `^\d{4}$`.
- **G-022:** delivery OTP generated but **never persisted** on INSERT → fixed; schema/generation/UI aligned to D-018.
- Restored `DECISION_REGISTER` D-016/D-017, `Assumptions` D-015/016/017, `CURRENT_SOURCE_OF_TRUTH` hierarchy `Basket → AllocationPlan → OrderGroup → Order → OrderItem`.
- Transport tests client fixtures; payment verify RBAC `OPS_AGENT|VENDOR_OWNER`; legacy_imports gate preserved.
- Web login `session.role` → `current_organization.role`.
- Mobile: backend-derived role routing for all seven roles; local API client now supports contract headers including Idempotency-Key and PUT; F-05 OfflineBanner no longer claims offline sync; Light/Night token foundation preserved; Order Detail lifecycle, vendor search/storefront, support, return/dispute, and shared profile/notifications added.

---

## 4. Historical GitHub discrepancies

This section contains historical reconciliation evidence and is not the current branch state.

| Item | Before | After |
|------|--------|-------|
| `origin/main` vs local | ahead 3, then ahead 1 | **0 / 0** at `dbcfb59` |
| CI | run 35833163192 failure (263226a), 35835229423 success (00245bf) | **35837588088 success** on `dbcfb59` |
| Missing files on main vs research | `scripts/api/**`, ~62 research files, D-016/017 register rows, CST hierarchy | restored from `origin/research-hardening-2026-09-14` and committed |
| Branches used | research-hardening + product-architecture-evolution as sources of truth | content merged into main commits |

Untracked (intentionally not committed): `docker-compose.yml`, `monitoring/`, `fonts/`, `frontend/`, `driver-stamford-07020/`, `design_references/`, `research/runs/`, junk `POL`, helper `artifacts/*` scripts.

---

## 5. Final screen / API coverage

- **Historical screen snapshot:** 68 — 40 IMP / 19 VER / 8 GAP / 1 N/A (`MVP_SCREEN_MATRIX.md` §H).
- **APIs:** `MVP_API_MAP.md` — deliver OTP pattern `^\d{4}$` (G-022 RESOLVED); catalog/search/notifications use REAL paths; gaps documented.
- **Live smoke:** FastAPI `:8000` healthz **200**, Next `:3001` **200**; 19 screens VERIFIED cycle 5; route crawl 47/47 previously.
- **Mobile Field:** F-01…F-05 wired to real field routes + healthz offline banner (parity.md).

---

## 6. Build / test status

| Check | Result |
|-------|--------|
| Historical full verification suite | **497/497 PASSED** in 210.67s — `artifacts/pol-test-results.json` `overall_status=PASSED` |
| Targeted delivery/POD/field/hierarchy | 73/73 passed (pre-suite) |
| `verify_repository_consistency` | **PASS 8 / FAIL 0**, EXIT 0 |
| `structural_audit.py` | **EXIT 0** |
| Web lint | **0 errors** (15 pre-existing warnings) |
| Web typecheck + build | EXIT 0 (50 routes) |
| Workspace typecheck (historical baseline) | EXIT 0; current mobile changes require new CI evidence |
| Historical migration chain snapshot | contiguous 001–031 at the recorded baseline; current branch contains migrations through 046 |
| Historical CI | **Code commit `f8ef267e`: backend verification run 35893284312 SUCCESS; mobile Cycle 3 run 35893284378 SUCCESS** |
| Live services | API healthz 200; Web 200 |

---

## 7. External blockers only (BLOCKED_EXTERNAL)

| ID | Blocker | Note |
|----|---------|------|
| B-01 | Real metrics source for `driver-stamford-07020/collector.py` | no real feed |
| B-02 | OpenPencil MCP `:7600` down | curl exit 28 / code 000; WAVE-02 blocked |
| B-03 | SMS provider credentials | Live SMS provider credentials remain absent; deterministic OTP is now restricted to explicit `ENVIRONMENT=test` only; non-test environments use random OTPs. |
| B-07 | Grafana `:3000` vs Next | Next on `:3001` |
| G-003/G-004 literal contract path parity | **RESOLVED** | Canonical + compatibility HTTP paths are both implemented and covered by current route/tests; no source gap remains. |

No other external blockers claimed.

---

## 8. Historical audit state — 2026-09-23

The repository has been re-audited against the remaining execution gates. Documentation status has been reconciled so that historical green evidence is not treated as current verification. Mobile QA Cycles 1–3 were historically evidenced by CI: Cycle 1 run `35884012647`; Cycle 2 run `35886815013`; Cycle 3 run `35893284378`. At that snapshot the remaining executable gates were Night visual verification, live basket → allocation → checkout → order lifecycle E2E, and checkout idempotency replay. Those local gates are now recorded separately as LOCAL-01…04 PASS; V-09/V-11 and D-028 have since received source remediation. OpenPencil WAVE-02 remains BLOCKED_EXTERNAL if MCP `:7600` is unavailable.

No current test/build result is claimed from this audit because the available GitHub integration can modify/read repository content but does not provide a local project runtime for executing the commands.

## 9. Historical commits (delivery batch)

- `6c3953b` feat(backend): restore research-hardening source of truth and green 497-test suite  
- `f369704` docs: BUILD_PLAN + screen matrix QA cycle 5 + restore canonical docs  
- `263226a` feat(mvp): Expo mobile scaffold + web retailer/login fixes  
- `00245bf` fix(ci): align verify_environment with full migration chain (95 tables, 001-031)  
- `dbcfb59` fix(G-022): align delivery OTP to D-018 4-digit + persist delivery_otp; restore D-015/016/017 hierarchy docs; Phase 3 Field screens  
- `3c9bc4f` fix(mobile): expose online state for OfflineBanner  
- `24f1e16` ci(mobile): validate Expo Android export in CI

---

*Historical Phase 5 runtime evidence is preserved above for provenance. Current remediation source is not yet runtime-certified at the latest HEAD because the available GitHub Actions runs fail before useful step execution (`steps: null`). Fresh CI/runtime certification remains an explicit release gate.*


### Remediation continuation — 2026-09-26

- IAM: D-026 / VD-15 delegated permission grant/revoke, effective access, privilege ceiling, tenant scope and append-only permission audit implemented.
- Auth: inactive principal invalidation, OTP purpose isolation, active-organization binding and E.164 verify contract hardened.
- Media: migration 048 binds presigned uploads to their authorized target and rejects confirmation retargeting.
- Verification: migration-head and schema discovery are now dynamic; hard-coded current table-count certification was removed.
- Current CI evidence remains pending because remediation Actions fail before useful step execution.


## Policy Amendment — 2026-11-24 (Historical Report Preserved)

This report records the original 2026-09-23 four-digit OTP implementation as historical evidence. The current policy is superseding: login/registration OTP is six digits under D-018, and newly issued delivery OTPs are six digits under D-029. Migration 077 backfills stored delivery-code lengths and preserves already-issued four-digit in-flight codes until those deliveries reach a terminal state. Do not treat the old test evidence in this report as verification of the amended six-digit implementation.
