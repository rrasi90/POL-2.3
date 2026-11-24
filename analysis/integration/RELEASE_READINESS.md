# POL-2.3 Release Readiness

**Date:** 2026-11-19 (documentation reconciliation)
**Latest locally tested source SHA:** `bfb28cefdb2bb13319d8508c8481911cb373fced`
**PR #53 head at latest Actions inspection:** `e772950d8da1b47561d8554cbbeb5fcf0adbd7db` (the documentation-only refresh in this file is a child commit)
**main:** `fbcdd7448d809a3281cc1ea8c43218d42e8762ca`

## Evidence scope and SHA relationship

The complete LOCAL verification matrix L1–L16 was executed on source SHA `bfb28cef` (2026-11-19); see `TEST_EVIDENCE_INDEX.md`. The PR head inspected at `e772950d` is 9 commits ahead of `bfb28cef` and 0 behind. The compare shows 11 changed paths: documentation/inventory/control files and the tracked test-result artifact. No application/runtime source file changed. Therefore the bfb28cef test results support the unchanged application source represented by e772950d, but they are **not a fresh test execution on e772950d**. The documentation refresh commit that carries this readiness correction is another docs-only child and does not claim new test execution.

The four decisions below remain deliberately separate.

## 1. MERGE READINESS — **MERGE BLOCKED**

### Satisfied for the application source in PR #53

- Backend 849/849; static gate 4/4; web typecheck + production build + Browser E2E 41/41; mobile typecheck + functional 28/28 + regression 23/23 + mock QA + pre-APK QA — all locally PASS on `bfb28cef`.
- The PR head reviewed at `b8c80bce` contains no application/runtime source changes relative to `bfb28cef`; only docs, inventories, governance records and the tracked test artifact changed.
- The four defects found during local verification were fixed and regression-covered (`1d50fe80`, `a96d66cd`).
- D-018 six-digit authentication OTP is now canonical; D-029 covers new six-digit delivery OTP; migration 077 is proposed on the pending OTP feature branch; non-custodial payment and tenant-isolation constraints preserved.
- Branch and PR inventories record 58 branches and 49 PRs. The checkpoint branch `fix/web-refresh-session-preserve-20261030` is now recorded at `d5ab26bb` and classified ARCHIVE_ONLY because six dated REA evidence files remain branch-only.

### Outstanding merge gates

1. **GitHub Actions with real runner steps on the exact latest PR head.** The four inspected runs on tested source SHA `bfb28cef` were pre-start blocked: every job had `runner_id=0` and `steps=0`, with the account-billing/spending-limit annotation. A fresh set of four workflows on PR head `e772950d` (IDs 44558971678 / 44558971582 / 44558971752 / 44558971716) repeated the same no-runner/no-step pattern. A commit-status query for `e772950d` returned no successful status contexts. Four PR-triggered workflow runs were created on that exact SHA (44558971678, 44558971582, 44558971752, 44558971716); every non-skipped job had `runner_id=0` and `steps=0`, finishing in about 1–2 seconds. The Android matrix job was skipped. These runs did not execute tests; the next CI run must target the then-current PR head after billing is restored.
2. **Branch protection / required checks.** A live branch metadata read on 2026-11-19 confirmed `main.protected=false`, `protection.enabled=false`, and required-status-check enforcement `off`. The branch-protection endpoint itself returned 403 through connected access, so no setting was changed. Repository owner/admin must enable protection and required checks through repository Settings / Rulesets if available; otherwise document the authorized exception and compensating controls. Do not describe branch protection as enabled.
3. **Review approval** under repository policy.

**Decision: do not merge PR #53 while CI is pre-start blocked or required review is missing.** Keep it Draft. Re-run all four workflows on the exact current PR head once billing/runner access is restored; require actual job steps, successful tests, and artifact uploads. A skipped Android QA matrix is not APK evidence.

### Owner-only infrastructure action

The Actions billing failure cannot be repaired by changing workflow YAML or repository files. The account owner must restore payment/spending allowance, or provision and register a properly secured self-hosted runner. No billing or runner change was made here.

## 2. QA APK READINESS — **QA APK BLOCKED**

- TODO-084 prebuild gate is fail-closed `BLOCKED` on the tested source ledger (`bfb28cef`).
- Known pre-build conditions remain open: the recorded `next@15.5.25` and `shell-quote` advisories require fresh advisory/lockfile verification and a tested upgrade, or an owner-approved time-bounded waiver.
- Device QA chain TODO-018…024 remains blocked behind TODO-084. No new APK was built or installed in this reconciliation.
- Do not use legacy `artifacts/android/*-Test.apk` files as current evidence without provenance, SHA, package/signature and install verification.

Unblocking path: verify and remediate the dependency advisories, obtain owner authorization for any remaining ledger exception, pass TODO-084 on one exact SHA, then build TODO-009 QA artifacts and run device QA.

## 3. STAGING READINESS — **STAGING BLOCKED (not attempted)**

- No staging deployment was executed in this reconciliation.
- Prior VPS evidence dated 2026-09-28 is historical only, not current runtime proof.
- TODO-011 requires the owner to configure `DATABASE_URL` / `POL_PG_DSN` through the authorized secret interface. Do not print or expose secret values.
- VPS access must be revalidated. The no-domain/test-provider staging lane (TODO-029/030) can be evaluated independently of public DNS/TLS (TODO-153); do not claim staging is ready until exact-SHA deployment and smoke evidence exist.

## 4. RELEASE READINESS — **RELEASE NOT READY**

Release remains blocked independently of the merge decision:

- TODO-055 full-suite CI rerun and artifacts on the release-candidate SHA — blocked by CI.
- TODO-056 release APK/AAB — blocked by TODO-084, device QA and signing approvals.
- TODO-057 staging E2E — not executed.
- TODO-058 live-provider acceptance (SMS.ir send/verify, object storage, public domain/TLS) — owner credentials and approvals not provided.
- TODO-059/060 business/legal decisions — D-018 refresh-token rotation, invoice timing, mutual-cancellation terms and pilot LOI verification remain owner decisions. Do not invent or silently resolve them.
- Non-custodial direct-payment scope remains unchanged.

## Next actions (dependency order)

1. Owner: restore GitHub Actions billing/spending allowance or register a secured self-hosted runner.
2. Owner/admin: verify and enable required PR checks / branch protection, or record the authorized exception.
3. Agent: rerun all four workflows on the exact then-current PR #53 head; verify runner IDs, executed steps, test results and artifact uploads.
4. Obtain required review approval; only then consider merging #53 and perform post-merge smoke on the resulting `main` SHA.
5. Continue owner-dependent work: TODO-011 secrets, TODO-025 isolated Vercel QA, TODO-029 staging revalidation, dependency remediation/TODO-084, then device QA.


## 2026-11-24 OTP amendment status

The six-digit OTP policy is approved in the current Decision Register, but the selective implementation is still under review on feat/six-digit-otp-and-social-impact-readme-20261124. The current main branch's prior backend verification predates this change and does not certify the new policy. Release readiness remains NOT READY until the exact amended SHA passes fresh backend, migration, web, browser, mobile, and security/review gates. Do not infer pilot or release authorization from the policy amendment alone.
