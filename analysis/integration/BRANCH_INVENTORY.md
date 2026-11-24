# POL-2.3 Branch Inventory

**Generated:** 2026-11-19 19:20 +03:30  
**main:** `fbcdd7448d809a3281cc1ea8c43218d42e8762ca`  
**Integration comparison baseline:** `e772950d8da1b47561d8554cbbeb5fcf0adbd7db` (PR #53 head immediately before this documentation-only refresh; 183 ahead / 0 behind main). The final commit containing this refreshed inventory is a docs-only child and is intentionally outside this snapshot.

Ahead/behind vs main and vs Integration; dispositions per live content comparison
(merge-base, file-level diffs, byte-identity checks, suite evidence on INT).
Machine-readable data: `BRANCH_INVENTORY.csv`.  
Disposition counts (58 refs): 31 ALREADY_INTEGRATED · 17 SUPERSEDED · 4 ARCHIVE_ONLY · 2 BLOCKED_POLICY · 1 HOLD · 1 SALVAGE_COMPLETED · 1 MERGE_CANDIDATE · 1 BASE.

| Branch | Head | Date | vs main (behind/ahead) | vs INT (behind/ahead) | Disposition | PR | Evidence |
|---|---|---|---|---|---|---|---|
| `agent/mobile-motion-port-20261022` | `1c793b53` | 2026-10-22 | 64/51 | 247/51 | **SUPERSEDED** | #40 closed | All 21 motion files + QA improvements verified present in INT; motion suites green (28/28, 23/23) on INT. |
| `agent/pol-2.3-integration-fdx` | `70e001f4` | 2026-10-22 | 65/2 | 248/2 | **SUPERSEDED** | - | expo run: scripts already in INT; journal entries historical; 2 unique files superseded by INT reconciliation. |
| `agent/pol-2.4-e2e-20261013` | `9be4c10e` | 2026-10-13 | 72/0 | 255/0 | **ALREADY_INTEGRATED** | #36 merged | ahead=0; browser E2E infra in main. |
| `agent/pol-2.4-execution-20261006` | `8e6c9ca8` | 2026-10-06 | 91/3 | 274/3 | **ALREADY_INTEGRATED** | #28 merged | build_qa_x86.mjs present in INT; remaining diff = workflow/artifacts superseded by #43/#53 gates. |
| `agent/source-authority-reconcile-20261022` | `d0914f07` | 2026-10-22 | 64/5 | 247/5 | **SUPERSEDED** | #42 closed | Equivalent corrections verified in INT (migration head 076, boundary path, historical checkpoints). |
| `agent/todo-061-source-baseline-20261022` | `afa46fc6` | 2026-10-22 | 30/0 | 213/0 | **ALREADY_INTEGRATED** | #41 merged | ahead=0. |
| `arena/01a0cdd2-pol-2-3` | `0489e3f9` | 2026-09-23 | 1277/10 | 1460/10 | **SUPERSEDED** | - | Sept 2026 stale artifacts/live_e2e experiments; superseded by later E2E infra (#36) and INT. |
| `audit/barcode-sms-closure-2026-09-24` | `eff21b6d` | 2026-09-25 | 1172/107 | 1355/107 | **SUPERSEDED** | - | Sept audit docs; findings closed via #7/#8/#16; governance docs reconciled repeatedly since. |
| `audit/continue-closure-2026-09-24` | `58408f45` | 2026-09-24 | 1172/5 | 1355/5 | **SUPERSEDED** | #9 closed | 3 docs present in main in evolved form; historical closure. |
| `audit/fix-canonical-drift-2026-09` | `b9e54955` | 2026-09-16 | 1338/4 | 1521/4 | **SUPERSEDED** | #4 closed | 4 governance docs superseded by repeated reconciliations. |
| `audit/mvp-deep-saturation-2026-09-24` | `cb65a323` | 2026-09-24 | 1178/0 | 1361/0 | **ALREADY_INTEGRATED** | #7 merged | ahead=0. |
| `backup/feat-mobile-motion-layer-20261022` | `2dfdd26a` | 2026-10-10 | 86/7 | 269/7 | **ARCHIVE_ONLY** | - | Backup branch; preserve, do not delete. |
| `chore/canonical-baseline-doc-reconcile-20261005` | `d37c4a49` | 2026-10-05 | 93/2 | 276/2 | **ALREADY_INTEGRATED** | #26 merged | Squash-duplicate commits; content in main. |
| `chore/mobile-expo-run-scripts-20261022` | `17e7e54d` | 2026-10-22 | 47/1 | 230/1 | **SUPERSEDED** | #45 closed | Run scripts ported to INT with documented Expo-version deviation (57.0.31 retained). |
| `deploy/vps-self-hosted-20260928` | `732b88ec` | 2026-09-29 | 294/84 | 477/84 | **ALREADY_INTEGRATED** | #18/#22 closed; #25 merged | Infra merged via #25; 3 deployment docs salvaged to INT (4994f9d0); remaining diff is dated evidence only. |
| `docs/pol-prebuild-checklist-mainbase-20261012` | `d1fa7b55` | 2026-10-12 | 85/8 | 268/8 | **ALREADY_INTEGRATED** | #34 merged | Squash-duplicates; content in main. |
| `docs/pol-prebuild-checklist-release-20261012` | `714f70f4` | 2026-10-12 | 86/28 | 269/28 | **SUPERSEDED** | #33 closed | Superseded by merged #34 and INT checklist reconciliation. |
| `docs/product-vision-d014-20261022` | `658b5a2b` | 2026-10-22 | 64/1 | 247/1 | **SUPERSEDED** | #44 closed | Single file byte-identical in INT. |
| `docs/reconcile-post-retest-status-2026-09-24` | `561f1840` | 2026-09-24 | 1173/0 | 1356/0 | **ALREADY_INTEGRATED** | #8 merged | ahead=0. |
| `docs/retailer-visual-todo-v2-20261025` | `7e73ec68` | 2026-10-25 | 5/0 | 188/0 | **ALREADY_INTEGRATED** | #48 merged | ahead=0. |
| `docs/todo-list-and-preflight-20261012` | `e39a5c8e` | 2026-10-12 | 86/20 | 269/20 | **SUPERSEDED** | #31 closed | Superseded by merged #34 + INT ledger. |
| `docs/todo-list-and-preflight-final-20261012` | `748690b8` | 2026-10-12 | 86/25 | 269/25 | **SUPERSEDED** | #32 closed | Same. |
| `docs/todo006-merge-evidence` | `ec7fe600` | 2026-10-13 | 70/0 | 253/0 | **ALREADY_INTEGRATED** | #37 merged | ahead=0. |
| `feat/android-retailer-vendor-apks` | `d636530f` | 2026-09-28 | 261/0 | 444/0 | **ALREADY_INTEGRATED** | #17 merged | ahead=0. |
| `feat/canonical-dual-apk-release-gates-20261005` | `edd417a2` | 2026-10-05 | 92/3 | 275/3 | **ALREADY_INTEGRATED** | #27 merged | Squash-duplicates; gates in main. |
| `feat/mobile-motion-layer` | `2dfdd26a` | 2026-10-10 | 86/7 | 269/7 | **ARCHIVE_ONLY** | - | Same SHA as backup branch; historical motion layer. |
| `feat/vendor-app-production-20260928` | `4f786504` | 2026-09-28 | 256/0 | 439/0 | **ALREADY_INTEGRATED** | #19 closed; #20 merged | Content superseded by v2 merge. |
| `feat/vendor-app-production-20260928-v2` | `d5875e9e` | 2026-09-29 | 127/0 | 310/0 | **ALREADY_INTEGRATED** | #20 merged | ahead=0. |
| `fix/audit-remediation-20261011` | `45ff1e3d` | 2026-10-11 | 86/9 | 269/9 | **ALREADY_INTEGRATED** | #30 merged | Squash-duplicates. |
| `fix/canonical-contradictions-2026-09-28` | `9c0c008e` | 2026-09-28 | 305/0 | 488/0 | **ALREADY_INTEGRATED** | #13 merged | ahead=0. |
| `fix/central-todo-084-apk-gate-20261022` | `48f0fa62` | 2026-10-22 | 47/0 | 230/0 | **ALREADY_INTEGRATED** | #43 merged | ahead=0. |
| `fix/current-main-governance-wording-2026-09-28` | `cef1606e` | 2026-09-28 | 300/2 | 483/2 | **ALREADY_INTEGRATED** | #14 merged | Squash-duplicates. |
| `fix/mobile-dependency-alignment-20261022` | `2a912bbc` | 2026-10-23 | 27/0 | 210/0 | **ALREADY_INTEGRATED** | #46 merged | ahead=0. |
| `fix/mobile-motion-audit-20261011` | `f4fcf5a9` | 2026-10-11 | 86/9 | 269/9 | **SUPERSEDED** | #29 closed | Unique fixes verified in INT (b85201ba review); superseded by stronger port. |
| `fix/otp-six-digit-contract-20261025` | `ddeec06b` | 2026-10-25 | 7/5 | 190/5 | **CLOSED — HISTORICAL / DO NOT MERGE WHOLE** | #49 closed | Historical 2026-11-19 policy assessment: the branch conflicted with the then-current four-digit D-018. That policy objection was superseded by the founder's 2026-11-24 six-digit amendment; the stale branch tip remains unsuitable for wholesale merge. |
| `fix/otp-six-digit-standard-20261025` | `d49ad86b` | 2026-10-25 | 7/16 | 190/16 | **BLOCKED_POLICY** | #50 closed | Same; delivery-OTP storage/rotation concerns recorded in PR_INTEGRATION_AUDIT. |
| `fix/pol-wave1-qa-mock-route-docs-20261027` | `74e7ded6` | 2026-10-27 | 7/250 | 190/250 | **SUPERSEDED** | #52 closed | Wave-1 content verified in INT; screenshot bulk excluded (stale pre-i18n). |
| `fix/remaining-canonical-contradictions-2026-09-28` | `3b6524b3` | 2026-09-28 | 296/0 | 479/0 | **ALREADY_INTEGRATED** | #15/#16 merged | ahead=0. |
| `fix/web-basket-sync-reuse-20261012` | `b04aabd3` | 2026-10-12 | 84/8 | 267/8 | **ALREADY_INTEGRATED** | #35 merged | Squash-duplicates. |
| `fix/web-refresh-session-preserve-20261030` | `d5ab26bb` | 2026-11-16 | 7/262 | 190/262 | **ARCHIVE_ONLY** | - | `b4a48801` source fix is byte-identical in main via PR #53. The six dated REA run-evidence files (`2026-10-29-mission2-internet-access`, `2026-10-30-mission3-stabilization`) were salvaged to main by the 2026-11-21 reconciliation PR. Branch retained as historical archive; do not merge run artifacts wholesale. |
| `hotfix/mobile-env-inline-babel` | `c5d2add1` | 2026-10-06 | 87/0 | 270/0 | **ALREADY_INTEGRATED** | - | ahead=0. |
| `hotfix/mobile-functional-defects` | `dd3477e1` | 2026-10-06 | 88/0 | 271/0 | **ALREADY_INTEGRATED** | - | ahead=0. |
| `integrate/vps-infra-20261005` | `2dbd270a` | 2026-10-05 | 94/0 | 277/0 | **ALREADY_INTEGRATED** | #25 merged | ahead=0. |
| `integration/pol-2.3-mainline-consolidation-2026-11` | `e772950d` | 2026-11-19 | 0/183 | 0/0 | **ALREADY_INTEGRATED** | #53 merged (0e2bf4c9) | PR #53 merged into main as `0e2bf4c9` on 2026-11-21; branch deleted post-merge. Local source tests on `bfb28cef` (backend 849/849, static gate, browser E2E 41/41). |
| `main` | `fbcdd744` | 2026-11-17 | 0/0 | 183/0 | **BASE** | - | Default branch; consolidation target. |
| `penpot-work-2026-09-16` | `541b3a1e` | 2026-09-16 | 1338/197 | 1521/197 | **ARCHIVE_ONLY** | - | Historical design/research skills docs; superseded by later design system. |
| `product-architecture-evolution-2026-09-20` | `bf7f25e9` | 2026-10-05 | 1338/584 | 1521/584 | **ALREADY_INTEGRATED** | #6 merged (via #12) | Old September wave merged; residual = generic skills/research docs. |
| `remediation/full-closure-2026-09-25` | `1f9b9dae` | 2026-09-26 | 346/0 | 529/0 | **ALREADY_INTEGRATED** | #10 merged | ahead=0. |
| `remediation/master-gap-closure-2026-09-26` | `3d1d4601` | 2026-09-27 | 325/0 | 508/0 | **ALREADY_INTEGRATED** | - | ahead=0. |
| `research-hardening-2026-09-14` | `87c1546b` | 2026-09-21 | 1338/582 | 1521/582 | **ALREADY_INTEGRATED** | #1 merged (via #12) | ahead=0 for code; residual research/skills docs archival only. |
| `research/cartona-uiux-extraction-phase2-20261027` | `a219a2bf` | 2026-10-27 | 7/260 | 190/260 | **SUPERSEDED** | no PR | Contained in web-refresh chain; INT preserved its own Cartona evidence set with provenance. |
| `test/journey-evidence-20261022` | `c700232c` | 2026-10-24 | 27/26 | 210/26 | **SALVAGE_COMPLETED** | #47 closed | Core ported; 3 behavioral suites + provenance salvaged in 4994f9d0; doc-sync modules deliberately deferred (archived docs). |
| `ui/redesign-precision-commerce` | `58db4e5b` | 2026-09-27 | 317/0 | 500/0 | **ALREADY_INTEGRATED** | #12 merged | ahead=0. |
| `ui/retailer-reference-match-20261005` | `20192cbf` | 2026-10-05 | 294/9 | 477/9 | **SUPERSEDED** | #21 closed | Screen styling predates motion/i18n rewrite; design intent tracked by merged #48. |
| `ui/visual-qa-screen-completion-20261025` | `09efd5b8` | 2026-10-27 | 7/196 | 190/196 | **SUPERSEDED** | #51 closed | Salvaged into INT; screenshots stale pre-i18n; visual QA to regenerate post-merge. |
| `unified/pol-platform-20261005` | `13b9eace` | 2026-10-05 | 106/0 | 289/0 | **ALREADY_INTEGRATED** | #24 merged | ahead=0. |
| `vercel-qa` | `8d3ad01f` | 2026-09-28 | 1325/11 | 1508/11 | **HOLD** | no PR | Vercel-QA proxy/workflow/manifest unique; TODO-025 requires isolated mock QA env rework; never deploy near production. |
| `visual-capture/baseline-2026-09-28` | `e4696089` | 2026-09-28 | 289/0 | 472/0 | **ALREADY_INTEGRATED** | #23 merged | ahead=0. |

---

## 2026-11-21 Update — post-merge reconciliation and branch cleanup

- **PR #53 merged into main as `0e2bf4c9`** (2026-11-21). Local main fast-forwarded 185 commits to `0e2bf4c9`. The integration-branch row above moves MERGE_CANDIDATE → ALREADY_INTEGRATED.
- **`fix/web-refresh-session-preserve-20261030` (PR #54):** the six dated REA run-evidence files (`2026-10-29-mission2-internet-access`, `2026-10-30-mission3-stabilization`) were salvaged to main by the 2026-11-21 reconciliation PR; the source fix `b4a48801` remains byte-identical in main via PR #53. Branch retained as ARCHIVE_ONLY.
- **Branch cleanup (2026-11-21):** remote branches with ALREADY_INTEGRATED / SUPERSEDED / SALVAGE_COMPLETED dispositions — including the merged integration branch and the two fully-integrated `hotfix/*` branches — were deleted locally and on origin. Every deleted head SHA remains recorded in `BRANCH_INVENTORY.csv` for recovery.
- **Retained refs:** `fix/otp-six-digit-contract-20261025` + `fix/otp-six-digit-standard-20261025` (CLOSED / HISTORICAL — the former four-digit D-018 policy objection was superseded on 2026-11-24; neither stale branch is to be merged wholesale; use PR #59's selective current-main implementation), `vercel-qa` (HOLD, TODO-025), `penpot-work-2026-09-16` and `feat/mobile-motion-layer` + `backup/feat-mobile-motion-layer-20261022` (ARCHIVE_ONLY), `fix/web-refresh-session-preserve-20261030` (ARCHIVE_ONLY).
- **Local-only backups retained:** `backup/local-main-ed815b2` and `backup/pre-exec-20261022`. `backup/local-main-ed815b2` carries six Sept-2026 gap-closure commits (G-003/G-004/G-011/G-012/G-023..G-026); a 2026-11-21 feature-level verification confirmed every closure is re-implemented in main under the consolidated route architecture — G-004 inbox (`scripts/api/routes/notifications.py` inbox_router: GET /inbox/items, PATCH /items/{id}/read, PATCH /items/read-all), G-011 SLA override (`scripts/api/routes/management.py` POST /admin/sla-overrides + route-inventory entry), G-011 category admin (`scripts/api/routes/admin.py` POST /categories, PATCH /categories/{id} — create_category), G-003/G-012 parity (products/search in `products.py`/`catalog.py`, baskets/current in `baskets.py`), and G-023..G-026 governance docs evolved (`CANONICAL_CONTRACT_MATRIX.md`, `PLATFORM_COMPLETION_GAP_REGISTER.md`). Disposition: SUPERSEDED; retained as backup per convention.
- **Stashes `stash@{0..2}` retained** on 2026-10-era bases; all three assessed obsolete on 2026-11-21 — `stash@{1}`/`stash@{2}` pin Expo `~57.0.24` which would regress the deliberate `~57.0.31` alignment from merged PR #46, and `stash@{0}` is an alternative Cartona registry restructure superseded by main's ported evidence set. Dropped only on owner confirmation.


---

## 2026-11-24 Live Branch Refresh — Post PR #58

**Current main:** `e2524df8d8712f535369ae469292541861ea3da7` (merge of PR #58).  
**Current remote branches:** 10 total, including main; 9 non-main refs.  
**Current open PRs:** 0.

The current remote refs were re-read from GitHub after PR #58 merged. Two short-lived integration refs remain on the remote but are already ancestors of main:

| Branch | Head | Relation to current main | Disposition |
|---|---|---|---|
| `integration/selective-salvage-remaining-branches-20261124` | `1f0fe96cbf0b` | 0 ahead / 1 behind; no file diff | **ALREADY_MERGED** — PR #58, merge commit `e2524df8`. Retained for traceability. |
| `fix/verification-ci-node-install-20261124` | `dbe443ca8db7` | 0 ahead / 6 behind; no file diff | **ALREADY_MERGED** — PR #57, merge commit `59ac9488`. Retained for traceability. |

The other retained refs keep their prior dispositions: both mobile-motion refs and web-refresh are archive-only, both six-digit OTP branches are policy-blocked by D-018, `vercel-qa` is HOLD under TODO-025, and `penpot-work-2026-09-16` is archive-only after the bounded skill salvage. No archive/backup branch was deleted.

The mainline verification workflow triggered by merge commit `e2524df8` was still running at the time of this refresh. The Remediation Static Gate completed successfully; no full-suite or release certification is claimed yet.


## 2026-11-24 Live Refresh — OTP policy supersession

The initial historical branch table above reflects the previous D-018 four-digit decision. On 2026-11-24, the founder superseded that rule with six-digit login/registration OTP and approved D-029 for new six-digit delivery/POD OTP. Consequently, the previous OTP BLOCKED_POLICY label is no longer the current policy disposition. The two old branch tips remain stale and must not be merged wholesale; a clean selective implementation is being re-authored from current main on feat/six-digit-otp-and-social-impact-readme-20261124. Migration 077 preserves existing in-flight delivery codes while ensuring new delivery codes are six digits. The feature is not considered verified until exact-SHA CI and security review complete.
