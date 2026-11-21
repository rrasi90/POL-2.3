# POL-2.3 Implementation Selection Matrix

**Baseline:** `main` @ `fbcdd7448d809a3281cc1ea8c43218d42e8762ca`
**Date:** 2026-11-19 — **Status column resolved** against `TEST_EVIDENCE_INDEX.md`; checkpoint branch refresh reconciled 2026-11-19.

| Capability | Candidate(s) | Selected direction | Rejected / deferred behavior | Required acceptance evidence | Status (2026-11-19) |
|---|---|---|---|---|---|
| Product scope | #44 vs current main | D-014 multi-vendor MVP; #44 wording ported | D-003 single-vendor MVP wording is historical only | Cross-document consistency | **RESOLVED** — #44 file byte-identical in INT; D-003 marked historical in Decision Register |
| Android QA gate | merged #43 vs #40 | Keep #43's stronger current-main fail-closed gate | Do not downgrade to #40's older 82-row gate | Fixture tests; blocked ledger keeps APK jobs skipped | **RESOLVED** — gate verified fail-closed `BLOCKED` on INT head; APK jobs skip |
| Expo dependencies | merged #46 vs #45 | Keep #46's Expo `~57.0.31` / React `19.2.3`; port only #45 `expo run:*` scripts | Do not copy #45's older Expo `~57.0.24` | typecheck + QA suites | **RESOLVED** — scripts present, pins preserved, mobile suites green on INT |
| Mobile motion | #29 vs #40 | #40 as base; salvage #29-only fixes where superior | No wholesale merge of dirty #29 | Motion suites + reduced-motion/RTL behavior | **RESOLVED** — all 21 motion files in INT with INT improvements; 28/28 + 23/23 + typecheck green |
| OTP policy | #49 vs #50 vs D-018 | No six-digit adoption; D-018 four-digit stands locked | No migration 077; no silent policy change | Decision Register + OTP tests | **RESOLVED (rejected)** — #49/#50 closed 2026-11-19 with D-018 rationale; four-digit contract exercised by auth matrix tests on INT |
| Delivery OTP migration | #50 migration 077 | Deferred until semantics/outbox/in-flight handling proven | No random rotation/nullification stranding active challenges | Disposable PG18 migration test + recipient-only tests | **CLOSED (not ported)** — stays rejected absent a new delivery-OTP decision; delivery OTP remains a separate domain concern |
| Test/security matrices | #47 | Preserve unique tests; never import stale results as certification | No brittle duplicate tests | Backend/web suites | **RESOLVED** — 3 behavioral suites salvaged (`4994f9d0`, provenance headers); doc-sync modules deferred; 849/849 green |
| Visual QA and Cartona | #51 | Preserve research artifacts with provenance; static inference ≠ runtime observation | No stale/placeholder screenshots; no six-digit-baseline captures | Asset/provenance audit; runtime captures post-merge | **PARTIALLY RESOLVED** — Cartona evidence preserved with limits in INT; screenshot bulk excluded as stale pre-i18n; regeneration tracked post-merge |
| Admin routes and retailer mocks | #52 | Port route uniqueness + retailer mock fixes after contract comparison | No privacy claim from route registration alone | Full suite + privacy lifecycle + mock isolation | **RESOLVED** — route uniqueness gate + mock transport verified in INT; E2E 41/41 incl. tenant isolation |
| Web refresh/session | `fix/web-refresh-session-preserve-20261030` (no PR) | Preserve rehydrated profile across token refresh; retain its later checkpoint as historical evidence | — | Byte-identity + regression tests; archive provenance review | **CODE RESOLVED / BRANCH ARCHIVE_ONLY** — fix commit `b4a48801` is byte-identical in INT; remote tip is now `d5ab26bb`. Its checkpoint adds six dated REA run-evidence files absent from INT; Expo `ios`/`android` script values match INT. Keep the branch as archive evidence; do not merge the historical run files wholesale. |
| Vercel QA environment | `vercel-qa` branch | HOLD for TODO-025 owner; isolated mock QA rework only | Never deploy near production data/secrets | Isolated environment + smoke evidence | **HOLD** — documented owner lane |
| VPS deployment docs | closed #18/#22 | Salvage as dated evidence for TODO-029 | Do not treat as current deploy recipe | Doc review + fresh staging run when access returns | **RESOLVED (salvaged)** — 3 docs ported in `4994f9d0` |

## Quality rule

Choose by correctness, security, reliability, maintainability, test quality, compatibility and current-SHA evidence. A newer or larger PR does not automatically supersede an older implementation.
