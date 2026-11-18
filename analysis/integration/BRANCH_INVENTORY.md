# POL-2.3 Branch Inventory

**Generated:** 2026-11-18 22:09 UTC  
**main:** `fbcdd7448d809a3281cc1ea8c43218d42e8762ca`  
**Integration:** `bfb28cefdb2bb13319d8508c8481911cb373fced` (PR #53, OPEN/DRAFT)

Ahead/behind vs main and vs Integration; dispositions per live content comparison
(merge-base, file-level diffs, byte-identity checks, suite evidence on INT).
Machine-readable data: `BRANCH_INVENTORY.csv`.

| Branch | Head | Date | vs main (behind/ahead) | vs INT (behind/ahead) | Disposition | PR | Evidence |
|---|---|---|---|---|---|---|---|
| `agent/mobile-motion-port-20261022` | `1c793b53` | 2026-10-22 | 64/51 | 238/51 | **SUPERSEDED** | #40 closed | All 21 motion files + QA improvements verified present in INT; motion suites green (28/28, 23/23) on INT. |
| `agent/pol-2.3-integration-fdx` | `70e001f4` | 2026-10-22 | 65/2 | 239/2 | **SUPERSEDED** | - | expo run: scripts already in INT; journal entries historical; 2 unique files superseded by INT reconciliation. |
| `agent/pol-2.4-e2e-20261013` | `9be4c10e` | 2026-10-13 | 72/0 | 246/0 | **ALREADY_INTEGRATED** | #36 merged | ahead=0; browser E2E infra in main. |
| `agent/pol-2.4-execution-20261006` | `8e6c9ca8` | 2026-10-06 | 91/3 | 265/3 | **ALREADY_INTEGRATED** | #28 merged | build_qa_x86.mjs present in INT; remaining diff = workflow/artifacts superseded by #43/#53 gates. |
| `agent/source-authority-reconcile-20261022` | `d0914f07` | 2026-10-22 | 64/5 | 238/5 | **SUPERSEDED** | #42 closed | Equivalent corrections verified in INT (migration head 076, boundary path, historical checkpoints). |
| `agent/todo-061-source-baseline-20261022` | `afa46fc6` | 2026-10-22 | 30/0 | 204/0 | **ALREADY_INTEGRATED** | #41 merged | ahead=0. |
| `arena/01a0cdd2-pol-2-3` | `0489e3f9` | 2026-09-23 | 1277/10 | 1451/10 | **SUPERSEDED** | - | Sept 2026 stale artifacts/live_e2e experiments; superseded by later E2E infra (#36) and INT. |
| `audit/barcode-sms-closure-2026-09-24` | `eff21b6d` | 2026-09-25 | 1172/107 | 1346/107 | **SUPERSEDED** | - | Sept audit docs; findings closed via #7/#8/#16; governance docs reconciled repeatedly since. |
| `audit/continue-closure-2026-09-24` | `58408f45` | 2026-09-24 | 1172/5 | 1346/5 | **SUPERSEDED** | #9 closed | 3 docs present in main in evolved form; historical closure. |
| `audit/fix-canonical-drift-2026-09` | `b9e54955` | 2026-09-16 | 1338/4 | 1512/4 | **SUPERSEDED** | #4 closed | 4 governance docs superseded by repeated reconciliations. |
| `audit/mvp-deep-saturation-2026-09-24` | `cb65a323` | 2026-09-24 | 1178/0 | 1352/0 | **ALREADY_INTEGRATED** | #7 merged | ahead=0. |
| `backup/feat-mobile-motion-layer-20261022` | `2dfdd26a` | 2026-10-10 | 86/7 | 260/7 | **ARCHIVE_ONLY** | - | Backup branch; preserve, do not delete. |
| `chore/canonical-baseline-doc-reconcile-20261005` | `d37c4a49` | 2026-10-05 | 93/2 | 267/2 | **ALREADY_INTEGRATED** | #26 merged | Squash-duplicate commits; content in main. |
| `chore/mobile-expo-run-scripts-20261022` | `17e7e54d` | 2026-10-22 | 47/1 | 221/1 | **SUPERSEDED** | #45 closed | Run scripts ported to INT with documented Expo-version deviation (57.0.31 retained). |
| `deploy/vps-self-hosted-20260928` | `732b88ec` | 2026-09-29 | 294/84 | 468/84 | **ALREADY_INTEGRATED** | #18/#22 closed; #25 merged | Infra merged via #25; 3 deployment docs salvaged to INT (4994f9d0); remaining diff is dated evidence only. |
| `docs/pol-prebuild-checklist-mainbase-20261012` | `d1fa7b55` | 2026-10-12 | 85/8 | 259/8 | **ALREADY_INTEGRATED** | #34 merged | Squash-duplicates; content in main. |
| `docs/pol-prebuild-checklist-release-20261012` | `714f70f4` | 2026-10-12 | 86/28 | 260/28 | **SUPERSEDED** | #33 closed | Superseded by merged #34 and INT checklist reconciliation. |
| `docs/product-vision-d014-20261022` | `658b5a2b` | 2026-10-22 | 64/1 | 238/1 | **SUPERSEDED** | #44 closed | Single file byte-identical in INT. |
| `docs/reconcile-post-retest-status-2026-09-24` | `561f1840` | 2026-09-24 | 1173/0 | 1347/0 | **ALREADY_INTEGRATED** | #8 merged | ahead=0. |
| `docs/retailer-visual-todo-v2-20261025` | `7e73ec68` | 2026-10-25 | 5/0 | 179/0 | **ALREADY_INTEGRATED** | #48 merged | ahead=0. |
| `docs/todo-list-and-preflight-20261012` | `e39a5c8e` | 2026-10-12 | 86/20 | 260/20 | **SUPERSEDED** | #31 closed | Superseded by merged #34 + INT ledger. |
| `docs/todo-list-and-preflight-final-20261012` | `748690b8` | 2026-10-12 | 86/25 | 260/25 | **SUPERSEDED** | #32 closed | Same. |
| `docs/todo006-merge-evidence` | `ec7fe600` | 2026-10-13 | 70/0 | 244/0 | **ALREADY_INTEGRATED** | #37 merged | ahead=0. |
| `feat/android-retailer-vendor-apks` | `d636530f` | 2026-09-28 | 261/0 | 435/0 | **ALREADY_INTEGRATED** | #17 merged | ahead=0. |
| `feat/canonical-dual-apk-release-gates-20261005` | `edd417a2` | 2026-10-05 | 92/3 | 266/3 | **ALREADY_INTEGRATED** | #27 merged | Squash-duplicates; gates in main. |
| `feat/mobile-motion-layer` | `2dfdd26a` | 2026-10-10 | 86/7 | 260/7 | **ARCHIVE_ONLY** | - | Same SHA as backup branch; historical motion layer. |
| `feat/vendor-app-production-20260928` | `4f786504` | 2026-09-28 | 256/0 | 430/0 | **ALREADY_INTEGRATED** | #19 closed; #20 merged | Content superseded by v2 merge. |
| `feat/vendor-app-production-20260928-v2` | `d5875e9e` | 2026-09-29 | 127/0 | 301/0 | **ALREADY_INTEGRATED** | #20 merged | ahead=0. |
| `fix/audit-remediation-20261011` | `45ff1e3d` | 2026-10-11 | 86/9 | 260/9 | **ALREADY_INTEGRATED** | #30 merged | Squash-duplicates. |
| `fix/canonical-contradictions-2026-09-28` | `9c0c008e` | 2026-09-28 | 305/0 | 479/0 | **ALREADY_INTEGRATED** | #13 merged | ahead=0. |
| `fix/central-todo-084-apk-gate-20261022` | `48f0fa62` | 2026-10-22 | 47/0 | 221/0 | **ALREADY_INTEGRATED** | #43 merged | ahead=0. |
| `fix/current-main-governance-wording-2026-09-28` | `cef1606e` | 2026-09-28 | 300/2 | 474/2 | **ALREADY_INTEGRATED** | #14 merged | Squash-duplicates. |
| `fix/mobile-dependency-alignment-20261022` | `2a912bbc` | 2026-10-23 | 27/0 | 201/0 | **ALREADY_INTEGRATED** | #46 merged | ahead=0. |
| `fix/mobile-motion-audit-20261011` | `f4fcf5a9` | 2026-10-11 | 86/9 | 260/9 | **SUPERSEDED** | #29 closed | Unique fixes verified in INT (b85201ba review); superseded by stronger port. |
| `fix/otp-six-digit-contract-20261025` | `ddeec06b` | 2026-10-25 | 7/5 | 181/5 | **BLOCKED_POLICY** | #49 closed | Six-digit OTP contradicts locked D-018; migration 077 rejected; E2E helpers hardcode OTP=123456. |
| `fix/otp-six-digit-standard-20261025` | `d49ad86b` | 2026-10-25 | 7/16 | 181/16 | **BLOCKED_POLICY** | #50 closed | Same; delivery-OTP storage/rotation concerns recorded in PR_INTEGRATION_AUDIT. |
| `fix/pol-wave1-qa-mock-route-docs-20261027` | `74e7ded6` | 2026-10-27 | 7/250 | 181/250 | **SUPERSEDED** | #52 closed | Wave-1 content verified in INT; screenshot bulk excluded (stale pre-i18n). |
| `fix/remaining-canonical-contradictions-2026-09-28` | `3b6524b3` | 2026-09-28 | 296/0 | 470/0 | **ALREADY_INTEGRATED** | #15/#16 merged | ahead=0. |
| `fix/web-basket-sync-reuse-20261012` | `b04aabd3` | 2026-10-12 | 84/8 | 258/8 | **ALREADY_INTEGRATED** | #35 merged | Squash-duplicates. |
| `fix/web-refresh-session-preserve-20261030` | `b4a48801` | 2026-10-30 | 7/261 | 181/261 | **SUPERSEDED** | no PR | Tip b4a48801 byte-identical in INT; rest = OTP chain + ported wave-1 + Cartona phase-2 research. |
| `hotfix/mobile-env-inline-babel` | `c5d2add1` | 2026-10-06 | 87/0 | 261/0 | **ALREADY_INTEGRATED** | - | ahead=0. |
| `hotfix/mobile-functional-defects` | `dd3477e1` | 2026-10-06 | 88/0 | 262/0 | **ALREADY_INTEGRATED** | - | ahead=0. |
| `integrate/vps-infra-20261005` | `2dbd270a` | 2026-10-05 | 94/0 | 268/0 | **ALREADY_INTEGRATED** | #25 merged | ahead=0. |
| `integration/pol-2.3-mainline-consolidation-2026-11` | `bfb28cef` | 2026-11-19 | 0/174 | 0/0 | **MERGE_CANDIDATE** | #53 | Only open PR; 174 ahead / 0 behind; local verification recorded; merge gated on CI-on-SHA (billing blocker). |
| `main` | `fbcdd744` | 2026-11-17 | 0/0 | 174/0 | **BASE** | - | Default branch; consolidation target. |
| `penpot-work-2026-09-16` | `541b3a1e` | 2026-09-16 | 1338/197 | 1512/197 | **ARCHIVE_ONLY** | - | Historical design/research skills docs; superseded by later design system. |
| `product-architecture-evolution-2026-09-20` | `bf7f25e9` | 2026-10-05 | 1338/584 | 1512/584 | **ALREADY_INTEGRATED** | #6 merged (via #12) | Old September wave merged; residual = generic skills/research docs. |
| `remediation/full-closure-2026-09-25` | `1f9b9dae` | 2026-09-26 | 346/0 | 520/0 | **ALREADY_INTEGRATED** | #10 merged | ahead=0. |
| `remediation/master-gap-closure-2026-09-26` | `3d1d4601` | 2026-09-27 | 325/0 | 499/0 | **ALREADY_INTEGRATED** | - | ahead=0. |
| `research-hardening-2026-09-14` | `87c1546b` | 2026-09-21 | 1338/582 | 1512/582 | **ALREADY_INTEGRATED** | #1 merged (via #12) | ahead=0 for code; residual research/skills docs archival only. |
| `research/cartona-uiux-extraction-phase2-20261027` | `a219a2bf` | 2026-10-27 | 7/260 | 181/260 | **SUPERSEDED** | no PR | Contained in web-refresh chain; INT preserved its own Cartona evidence set with provenance. |
| `test/journey-evidence-20261022` | `c700232c` | 2026-10-24 | 27/26 | 201/26 | **SALVAGE_COMPLETED** | #47 closed | Core ported; 3 behavioral suites + provenance salvaged in 4994f9d0; doc-sync modules deliberately deferred (archived docs). |
| `ui/redesign-precision-commerce` | `58db4e5b` | 2026-09-27 | 317/0 | 491/0 | **ALREADY_INTEGRATED** | #12 merged | ahead=0. |
| `ui/retailer-reference-match-20261005` | `20192cbf` | 2026-10-05 | 294/9 | 468/9 | **SUPERSEDED** | #21 closed | Screen styling predates motion/i18n rewrite; design intent tracked by merged #48. |
| `ui/visual-qa-screen-completion-20261025` | `09efd5b8` | 2026-10-27 | 7/196 | 181/196 | **SUPERSEDED** | #51 closed | Salvaged into INT; screenshots stale pre-i18n; visual QA to regenerate post-merge. |
| `unified/pol-platform-20261005` | `13b9eace` | 2026-10-05 | 106/0 | 280/0 | **ALREADY_INTEGRATED** | #24 merged | ahead=0. |
| `vercel-qa` | `8d3ad01f` | 2026-09-28 | 1325/11 | 1499/11 | **HOLD** | no PR | Vercel-QA proxy/workflow/manifest unique; TODO-025 requires isolated mock QA env rework; never deploy near production. |
| `visual-capture/baseline-2026-09-28` | `e4696089` | 2026-09-28 | 289/0 | 463/0 | **ALREADY_INTEGRATED** | #23 merged | ahead=0. |
