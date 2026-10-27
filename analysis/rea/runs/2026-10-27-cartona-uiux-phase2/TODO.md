# TODO — 2026-10-27-cartona-uiux-phase2

> آخرین وضعیت / Latest state: CP0 in progress — research branch created, baseline written, initial commit pending.
> کار بعدی / Next: commit + push CP0, then start CP1 (prior-research audit).
> مانع اصلی / Main blocker: none. gh CLI unauthenticated (PR step deferred to CP9 per user decision).

Statuses: `NOT_STARTED | IN_PROGRESS | BLOCKED | PARTIAL | DONE | WONT_DO_WITH_REASON`

---

## CP0 — GitHub sync & baseline

### task-001: Sync GitHub and record baseline
- Description: fetch --all --prune, verify branch/remote state, create research branch, write baseline.md/json.
- Rationale: mission §5–7; all later phases depend on verified starting state.
- Expected output: baseline.md, baseline.json on research branch.
- Status: DONE
- Priority: high
- Dependencies: none
- Method: `git fetch --all --prune`; `git checkout -b research/cartona-uiux-extraction-phase2-20261027` from `fix/pol-wave1-qa-mock-route-docs-20261027` @ `74e7ded6`.
- Result: branch created at 74e7ded6; remote clean; baseline.md + baseline.json written.
- Evidence: baseline.md; baseline.json; session log (fetch output clean, no new refs).
- Commit: (this commit)
- Blockers: none
- Next: task-002 push verification.

### task-002: Initial commit + push with remote SHA verification
- Description: commit baseline/TODO/progress-log/execution-plan; push; verify remote SHA equals local HEAD.
- Rationale: mission §7 requires mission visible on GitHub from the start.
- Expected output: remote branch `research/cartona-uiux-extraction-phase2-20261027` at local HEAD.
- Status: DONE
- Priority: high
- Dependencies: task-001
- Method: git guard checklist (status → diff review → allowlist → `git diff --check` → secret scan) → commit → push → `git ls-remote origin <branch>`.
- Result: commit `9a69f62c` pushed; remote SHA `9a69f62c` == local HEAD (verified via `git ls-remote origin research/cartona-uiux-extraction-phase2-20261027`).
- Evidence: progress-log.md CP0 entry.
- Commit: 9a69f62c
- Blockers: none
- Next: CP1.

## CP1 — Prior-research audit

### task-101: Re-validate prior-run claims with metric normalization
- Description: re-verify each claim of the 2026-10-27 remediation run (version, package, Flutter, 113 entries / 103 assets, ~1,494 strings vs 1,652-line corpus — recount with documented rules, 70 endpoints classified individually, 21 screens STATIC_INFERRED, ABI failure, 6,426 fns / 312 VM classes / 0 app classes, complementary APKs UNAVAILABLE).
- Rationale: mission §9–10 + Addendum F.
- Expected output: previous-research-audit.md with per-claim verdicts + method.
- Status: NOT_STARTED
- Priority: high
- Dependencies: CP0
- Method: read raw artifacts; recount with scripts in tools/; classify endpoint refs individually.
- Result: —
- Evidence: —
- Commit: —
- Blockers: —
- Next: —

## CP2 — APK inventory, environment, tooling

### task-201: APK inventory + integrity report
- Description: full metadata (package, versions, split, ABI, density, locale, cert fingerprint) + SHA-256 recompute for 4 Cartona + 3 POL APKs.
- Status: NOT_STARTED | Priority: high | Dependencies: CP0
- Result: — | Evidence: — | Commit: — | Blockers: — | Next: —

### task-202: Android environment matrix
- Description: SDK/AVD/device/tool inventory incl. installed system images (for Addendum B emulator selection).
- Status: NOT_STARTED | Priority: high | Dependencies: CP0
- Result: — | Evidence: — | Commit: — | Blockers: — | Next: —

### task-203: Tooling research (ARTEMIS + official Android docs + UI automation)
- Description: official repo/license/deps inspection of ARTEMIS; official adb/uiautomator/emulator docs; emulator image ABI compatibility research; source register.
- Status: NOT_STARTED | Priority: high | Dependencies: CP0
- Result: — | Evidence: — | Commit: — | Blockers: — | Next: —

### task-204: ARTEMIS feasibility verdict
- Description: install/run only if isolated + free + compatible; otherwise record BLOCKED/WONT_DO_WITH_REASON and proceed with ADB/uiautomator.
- Status: NOT_STARTED | Priority: medium | Dependencies: task-203
- Result: — | Evidence: — | Commit: — | Blockers: — | Next: —

## CP3 — Runtime attempt (device-first)

### task-301: Split compatibility pass (Addendum A)
- Description: per-APK metadata; device query (ABIs, Android version, density, dims, locale); select compatible split set; validate same package/version.
- Status: NOT_STARTED | Priority: high | Dependencies: task-201, device connected
- Result: — | Evidence: — | Commit: — | Blockers: — | Next: —

### task-302: Physical device install via adb install-multiple
- Description: validated install with full command/exit/stdout/stderr/device-state logging; launch; logcat; first screenshot.
- Status: NOT_STARTED | Priority: high | Dependencies: task-301
- Result: — | Evidence: — | Commit: — | Blockers: — | Next: —

### task-303: Emulator fallback paths (only if device unavailable at runtime moment)
- Description: per Addendum B — select image by verified ABI compatibility (Android 11 x86/x86_64 ARM translation caveats), never by API number; historical x86_64 failure reproduced only as supplementary test.
- Status: NOT_STARTED | Priority: medium | Dependencies: task-302 blocked
- Result: — | Evidence: — | Commit: — | Blockers: — | Next: —

## CP4 — Runtime observation

### task-401: Screenshot capture with metadata manifest
- Status: NOT_STARTED | Priority: high | Dependencies: task-302 success
### task-402: Screen catalog + interaction atlas updates
- Status: NOT_STARTED | Priority: high | Dependencies: task-401
### task-403: Reachable flow walkthrough (onboarding/login/OTP UI; post-auth only if user authorizes account)
- Status: NOT_STARTED | Priority: high | Dependencies: task-302 success

## CP5 — Assets

### task-501: Asset inventory rebuild + license classification
- Status: NOT_STARTED | Priority: medium | Dependencies: CP0
### task-502: Gallery index + contact sheets + color analysis
- Status: NOT_STARTED | Priority: medium | Dependencies: task-501

## CP6 — Flutter/Dart static analysis

### task-601: Re-verify snapshot facts + strings + endpoint catalog
- Status: NOT_STARTED | Priority: medium | Dependencies: CP1
### task-602: runtime-vs-static reconciliation
- Status: NOT_STARTED | Priority: medium | Dependencies: task-601 (+ task-402)

## CP7 — Complementary apps

### task-701: Supplier/driver app research from official sources + capability matrix
- Status: NOT_STARTED | Priority: medium | Dependencies: CP0

## CP8 — Design system + POL mapping

### task-801: Design token inventory + design system analysis + component catalog
- Status: NOT_STARTED | Priority: high | Dependencies: CP4/CP5/CP6
### task-802: Cartona→POL pattern mapping + gap register + recommendations + priority scoring + DS compatibility
- Status: NOT_STARTED | Priority: high | Dependencies: task-801

## CP9 — QA, final gate, publish

### task-901: Validation scripts + QA run
- Status: NOT_STARTED | Priority: high | Dependencies: all
### task-902: Final report + handoff + implementation cards
- Status: NOT_STARTED | Priority: high | Dependencies: task-901
### task-903: Product-freeze diff verification (zero POL code changes)
- Status: NOT_STARTED | Priority: high | Dependencies: all commits
### task-904: Draft PR (user runs gh auth login first) — base = fix/pol-wave1-qa-mock-route-docs-20261027; PR #52 verification; never merged before #52 resolution
- Status: NOT_STARTED | Priority: high | Dependencies: task-902
