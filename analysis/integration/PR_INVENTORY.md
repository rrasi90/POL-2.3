# POL-2.3 PR Inventory

**Generated:** 2026-11-18 22:09 UTC  
**Source:** `gh pr list --state all` (all 49 PRs; every state verified live 2026-11-19).
Machine-readable data: `PR_INVENTORY.csv`.

| PR | Title | State | Head -> Base | Head SHA | Disposition | Evidence |
|---|---|---|---|---|---|---|
| #55 | docs(integration): salvage PR54 REA evidence and reconcile branch inventory post #53 merge | MERGED/ready | `docs/post-merge-reconciliation-20261121` -> `main` | `3f8133d606` | **ALREADY_MERGED** | Salvaged six dated REA run-evidence files + branch-inventory reconciliation; merged as `fe0799b5`. |
| #54 | Fix/web refresh session preserve 20261030 | CLOSED/ready | `fix/web-refresh-session-preserve-20261030` -> `main` | `d5ab26bb5d3c` | **CLOSE_AS_SUPERSEDED** | Source fix `b4a48801` byte-identical in main via #53; six dated REA run-evidence files salvaged via #55; closed 2026-11-21 with supersession comment; branch retained ARCHIVE_ONLY. |
| #53 | Integration: evidence-driven POL-2.3 mainline consolidation | MERGED/ready | `integration/pol-2.3-mainline-consolidation-2026-11` -> `main` | `e772950d8da1` | **ALREADY_MERGED** | Merged into main as `0e2bf4c9` on 2026-11-21; local verification on `bfb28cef` (backend 849/849, static gate, browser E2E 41/41); Actions remain billing-blocked. |
| #52 | Wave 1: admin route hygiene, runtime inventory correction, retailer mock QA | CLOSED/draft | `fix/pol-wave1-qa-mock-route-docs-20261027` -> `ui/visual-qa-screen-completion-20261025` | `74e7ded6d695` | **CLOSE_AS_SUPERSEDED** | Wave-1 UI/route-hygiene/mock content verified in INT; screenshot bulk excluded as stale; closed 2026-11-19 with evidence comment. |
| #51 | ui: complete screen visual capture and reconcile QA evidence | CLOSED/draft | `ui/visual-qa-screen-completion-20261025` -> `fix/otp-six-digit-standard-20261025` | `09efd5b810f9` | **CLOSE_AS_SUPERSEDED** | Support tenant-isolation endpoint, admin route hygiene, viewport/a11y, refresh tip verified in INT; stale screenshots excluded. |
| #50 | fix(auth): standardize all OTP codes to six digits | CLOSED/ready | `fix/otp-six-digit-standard-20261025` -> `main` | `d49ad86bbda2` | **CLOSE_AS_SUPERSEDED** | Six-digit auth OTP + migration 077 contradict locked D-018; no policy-independent salvage; closed 2026-11-19. |
| #49 | feat(auth): standardize OTP policy on six digits | CLOSED/ready | `fix/otp-six-digit-contract-20261025` -> `main` | `ddeec06b11e8` | **CLOSE_AS_SUPERSEDED** | Same as #50; E2E helpers hardcode OTP=123456 (policy-dependent). |
| #48 | docs(design): retailer visual audit and agent execution TODO | MERGED/ready | `docs/retailer-visual-todo-v2-20261025` -> `main` | `7e73ec685c96` | **ALREADY_MERGED** | Merged; retailer visual audit TODO in main. |
| #47 | test: fix POD proof media isolation and record journey/security evidence | CLOSED/draft | `test/journey-evidence-20261022` -> `fix/mobile-dependency-alignment-20261022` | `c700232c80cf` | **SALVAGE** | Core ported in INT; 3 behavioral suites salvaged in 4994f9d0; doc-sync modules deferred; closed 2026-11-19. |
| #46 | fix(mobile): dedupe react, align Expo patch, drop dual Expo config | MERGED/ready | `fix/mobile-dependency-alignment-20261022` -> `main` | `2a912bbc5830` | **ALREADY_MERGED** | Merged = current main fbcdd744. |
| #45 | chore(mobile): use expo run:ios/android dev scripts (stacked on TODO-084 gate) | CLOSED/draft | `chore/mobile-expo-run-scripts-20261022` -> `fix/central-todo-084-apk-gate-20261022` | `17e7e54d735e` | **CLOSE_AS_SUPERSEDED** | Run scripts present in INT; Expo pin deviation documented; closed 2026-11-19. |
| #44 | docs: align Product Vision with D-014 multi-vendor MVP | CLOSED/draft | `docs/product-vision-d014-20261022` -> `main` | `658b5a2b3e85` | **CLOSE_AS_SUPERSEDED** | Product Vision byte-identical in INT; closed 2026-11-19. |
| #43 | Draft: enforce TODO-084 before Android QA APK builds | MERGED/ready | `fix/central-todo-084-apk-gate-20261022` -> `main` | `48f0fa627d40` | **ALREADY_MERGED** | Merged a7c99a99; fail-closed TODO-084 gate retained in INT. |
| #42 | Draft: reconcile canonical source paths and historical CI notes | CLOSED/draft | `agent/source-authority-reconcile-20261022` -> `main` | `d0914f076182` | **CLOSE_AS_SUPERSEDED** | Equivalent doc corrections verified in INT; closed 2026-11-19. |
| #41 | Draft: reconcile TODO dependencies and defer domain/SMS to final stage | MERGED/ready | `agent/todo-061-source-baseline-20261022` -> `main` | `afa46fc65500` | **ALREADY_MERGED** | Merged. |
| #40 | Draft: port mobile motion system and QA artifact coverage onto current main | CLOSED/draft | `agent/mobile-motion-port-20261022` -> `main` | `1c793b5363ef` | **CLOSE_AS_SUPERSEDED** | Motion port verified complete in INT; closed 2026-11-19. |
| #39 | docs: record PR #38 merge SHA and post-merge CI for TODO-007 | MERGED/ready | `docs/todo007-merge-evidence` -> `main` | `c5d28c62a070` | **ALREADY_MERGED** | Merged. |
| #38 | TODO-007: cross-persona delivery E2E + delivery-stage UI fixes | MERGED/ready | `agent/pol-2.4-todo007-delivery-e2e` -> `main` | `1ad3b41d8bf4` | **ALREADY_MERGED** | Merged. |
| #37 | docs: record PR #36 merge evidence and PR #29 conflict status | MERGED/ready | `docs/todo006-merge-evidence` -> `main` | `ec7fe60089e1` | **ALREADY_MERGED** | Merged. |
| #36 | test(web): browser E2E for retailer basket sync (TODO-006) + 3 web fixes | MERGED/ready | `agent/pol-2.4-e2e-20261013` -> `main` | `9be4c10e6388` | **ALREADY_MERGED** | Merged. |
| #35 | fix(web): reuse synced basket and continue checkout on retry | MERGED/ready | `fix/web-basket-sync-reuse-20261012` -> `main` | `b04aabd32ecd` | **ALREADY_MERGED** | Merged. |
| #34 | docs/test: finalize POL pre-build checklist and regression gates | MERGED/ready | `docs/pol-prebuild-checklist-mainbase-20261012` -> `main` | `d1fa7b55346a` | **ALREADY_MERGED** | Merged. |
| #33 | docs/test: finalize pre-build checklist and regression evidence | CLOSED/ready | `docs/pol-prebuild-checklist-release-20261012` -> `main` | `714f70f42745` | **CLOSE_AS_SUPERSEDED** | Superseded by merged #34; historical. |
| #32 | docs/test: finalize POL TODO evidence and UI regression gates | CLOSED/draft | `docs/todo-list-and-preflight-final-20261012` -> `main` | `748690b8efd5` | **CLOSE_AS_SUPERSEDED** | Superseded; historical. |
| #31 | docs: add TODO list and preflight helper | CLOSED/draft | `docs/todo-list-and-preflight-20261012` -> `main` | `e39a5c8e5214` | **CLOSE_AS_SUPERSEDED** | Superseded; historical. |
| #30 | Fix audit findings: OTP isolation, checkout sync and mobile release gates | MERGED/ready | `fix/audit-remediation-20261011` -> `main` | `45ff1e3d6498` | **ALREADY_MERGED** | Merged. |
| #29 | WIP: mobile motion layer and interrupted-animation fixes | CLOSED/draft | `fix/mobile-motion-audit-20261011` -> `main` | `f4fcf5a92c8c` | **CLOSE_AS_SUPERSEDED** | Superseded by #40/#53 motion implementation; unique fixes verified present. |
| #28 | fix(mobile): unblock npm ci on npm>=12 + emulator QA build path + runtime evidence | MERGED/ready | `agent/pol-2.4-execution-20261006` -> `main` | `8e6c9ca89beb` | **ALREADY_MERGED** | Merged; build_qa_x86.mjs present in INT. |
| #27 | build: enforce canonical dual-app Android release gates | MERGED/ready | `feat/canonical-dual-apk-release-gates-20261005` -> `main` | `edd417a263ec` | **ALREADY_MERGED** | Merged. |
| #26 | docs: reconcile historical mobile capture evidence | MERGED/ready | `chore/canonical-baseline-doc-reconcile-20261005` -> `main` | `d37c4a4945c4` | **ALREADY_MERGED** | Merged. |
| #25 | chore: add validated self-hosted VPS infrastructure | MERGED/ready | `integrate/vps-infra-20261005` -> `main` | `2dbd270ababc` | **ALREADY_MERGED** | Merged; VPS infra in main. |
| #24 | feat: converge POL product architecture, vendor app and retailer UI | MERGED/ready | `unified/pol-platform-20261005` -> `main` | `13b9eacecd0a` | **ALREADY_MERGED** | Merged. |
| #23 | docs: integrate mobile visual capture baseline | MERGED/ready | `visual-capture/baseline-2026-09-28` -> `unified/pol-platform-20261005` | `e46960899f2d` | **ALREADY_MERGED** | Merged. |
| #22 | chore: integrate VPS deployment and landing infrastructure | CLOSED/ready | `deploy/vps-self-hosted-20260928` -> `unified/pol-platform-20261005` | `732b88ec5221` | **CLOSE_AS_SUPERSEDED** | VPS docs salvaged to INT; infra merged via #25. |
| #21 | UI: match retailer mobile app to reference screens | CLOSED/ready | `ui/retailer-reference-match-20261005` -> `main` | `20192cbf8699` | **CLOSE_AS_SUPERSEDED** | Screen styling predates motion/i18n rewrite; design intent tracked by #48. |
| #20 | feat(vendor-app): production workspace v2 | MERGED/ready | `feat/vendor-app-production-20260928-v2` -> `main` | `d5875e9eec0f` | **ALREADY_MERGED** | Merged. |
| #19 | feat(vendor-app): build POL Vendor mobile workspace | CLOSED/ready | `feat/vendor-app-production-20260928` -> `main` | `4f786504f690` | **CLOSE_AS_SUPERSEDED** | Superseded by v2 (#20). |
| #18 | deploy: self-host POL on VPS | CLOSED/draft | `deploy/vps-self-hosted-20260928` -> `main` | `732b88ec5221` | **CLOSE_AS_SUPERSEDED** | Deployment docs salvaged; infra merged via #25. |
| #17 | feat: split mobile client into retailer and vendor Android APKs | MERGED/ready | `feat/android-retailer-vendor-apks` -> `main` | `d636530f1a05` | **ALREADY_MERGED** | Merged. |
| #16 | fix: close stale D-019/D-020 governance sync claims | MERGED/ready | `fix/remaining-canonical-contradictions-2026-09-28` -> `main` | `3b6524b3ffd5` | **ALREADY_MERGED** | Merged. |
| #15 | fix: reconcile remaining canonical contradictions | MERGED/ready | `fix/remaining-canonical-contradictions-2026-09-28` -> `main` | `f3a30b19c54a` | **ALREADY_MERGED** | Merged. |
| #14 | docs: mark remediation checkpoints as historical after main integration | MERGED/ready | `fix/current-main-governance-wording-2026-09-28` -> `main` | `80932a8e45ed` | **ALREADY_MERGED** | Merged. |
| #13 | fix: reconcile canonical migration and verification contradictions | MERGED/ready | `fix/canonical-contradictions-2026-09-28` -> `main` | `9c0c008e6959` | **ALREADY_MERGED** | Merged. |
| #12 | Integrate final remediation + Precision Commerce UI | MERGED/ready | `ui/redesign-precision-commerce` -> `main` | `58db4e5b87de` | **ALREADY_MERGED** | Merged. |
| #10 | remediation: full closure hardening pass | MERGED/draft | `remediation/full-closure-2026-09-25` -> `main` | `1f9b9dae9f05` | **ALREADY_MERGED** | Merged. |
| #9 | docs: close G-030 and refresh current CI evidence | CLOSED/ready | `audit/continue-closure-2026-09-24` -> `main` | `58408f4573f7` | **CLOSE_AS_SUPERSEDED** | Historical closure; docs evolved in main. |
| #8 | docs: reconcile MVP status after post-retest audit | MERGED/ready | `docs/reconcile-post-retest-status-2026-09-24` -> `main` | `561f18409d3a` | **ALREADY_MERGED** | Merged. |
| #7 | audit: deep MVP saturation and mobile auth closure | MERGED/ready | `audit/mvp-deep-saturation-2026-09-24` -> `main` | `cb65a323974c` | **ALREADY_MERGED** | Merged. |
| #6 | feat: add product architecture evolution wave 01 | MERGED/ready | `product-architecture-evolution-2026-09-20` -> `research-hardening-2026-09-14` | `2583abed0c43` | **ALREADY_MERGED** | Merged (via #12). |
| #4 | audit: reconcile canonical docs and certification boundary | CLOSED/draft | `audit/fix-canonical-drift-2026-09` -> `main` | `b9e54955c8f9` | **CLOSE_AS_SUPERSEDED** | Governance docs superseded by repeated reconciliations. |
| #1 | feat: apply evidence-derived B2B operational hardening | CLOSED/ready | `research-hardening-2026-09-14` -> `main` | `87c1546bbe83` | **ALREADY_MERGED** | Merged (via #12). |


---

## 2026-11-24 Live Refresh — PR #57 and #58

Live GitHub REST snapshot after the selective branch reconciliation:

- **54 PR records returned:** 33 merged, 21 closed unmerged, 0 open.
- **PR #57** — merged 2026-11-24 as `59ac9488b06cb62822f584ef5389f21e0f6dd6f5`. Added the root English README and installed Node.js 22 / `npm ci` in the independent verification workflow. The corrected workflow completed a 849/849 backend verification run on its tested source lineage; subsequent mainline verification is tracked separately.
- **PR #58** — merged 2026-11-24 as `e2524df8d8712f535369ae469292541861ea3da7`. Added the modernized POL batch-execution agent skill and the remaining-branch reconciliation record. Static Gate passed on the PR head and again post-merge. Independent Verification was still running at the time of this inventory refresh; no full-suite pass is claimed for the #58 merge SHA yet.

The original table above is a historical snapshot through #56. This dated live refresh is authoritative for #57 and #58 and for the counts stated here.
