# POL-2.3 Release Readiness

**Date:** 2026-11-19
**Exact verified SHA:** `bfb28cefdb2bb13319d8508c8481911cb373fced` (integration branch, PR #53 OPEN/DRAFT)
**main:** `fbcdd7448d809a3281cc1ea8c43218d42e8762ca`

The four decisions below are deliberately separate. They are not blended into one "complete" status.

## 1. MERGE READINESS — **MERGE BLOCKED**

What is satisfied on the exact current SHA `bfb28cef`:
- Full local verification (see `TEST_EVIDENCE_INDEX.md` L1–L16): backend 849/849, static gate 4/4, web typecheck + `next build` + E2E 41/41, mobile typecheck + 28/28 + 23/23 + mock + pre-APK QA — all PASS, all on this SHA.
- No unresolved P0 security/data-integrity/API-contract defect found by those suites; the four defects discovered during verification are fixed and regression-covered (`1d50fe80`, `a96d66cd`).
- Branch/PR inventory complete (58 branches, 49 PRs — all dispositioned, zero NEEDS_REVIEW); all salvage provenance recorded; 9 superseded PRs closed with evidence comments; only #53 open.
- No unauthorized policy/schema/migration change: D-018 four-digit OTP preserved; migration head stays 076; non-custodial payment and tenant isolation untouched.

What is missing (the gate itself):
1. **Required GitHub Actions workflows with real runner steps on the exact pre-merge SHA.** All runs are pre-start blocked by account billing (`runner_id=0`, `steps=0` — see evidence index). Owner must restore billing/spending allowance or attach a secured self-hosted runner.
2. Branch protection with required checks on `main` — currently unavailable (paid feature, 403). Until CI runs, an owner-authorized documented equivalent would be required for any merge.
3. Review approval per repository policy.

Decision: **Do not merge PR #53 while CI is pre-start blocked.** Re-run all four workflows on the exact candidate SHA once billing is fixed; require successful test steps AND artifact uploads (a skipped Android QA matrix is not an APK success).

## 2. QA APK READINESS — **QA APK BLOCKED**

- TODO-084 prebuild gate is fail-closed `BLOCKED` by design on the current ledger (checked 2026-11-19 on `bfb28cef`).
- Known gate preconditions remain open: `next@15.5.25` / `shell-quote` advisories recorded in the journal require upgrade-with-tests or an owner-approved documented waiver; device QA chain TODO-018…024 is closed behind the gate.
- No APK was built, installed, or claimed in this session. Legacy `artifacts/android/*-Test.apk` files have unknown provenance and are rejected as evidence.
- Unblocking path: owner authorizes ledger closure of the remaining PRE-BUILD subset (or a documented exception), then TODO-009 QA artifacts on a single exact SHA.

## 3. STAGING READINESS — **STAGING BLOCKED (not attempted)**

- No staging deployment was executed this session; prior VPS evidence (`deploy/VPS_RUNTIME_VERIFICATION_2026-09-28.md`) is dated 2026-09-28 against an older tree and is retained as historical evidence only, not current runtime proof.
- Blockers: TODO-011 notification-retention secrets (`DATABASE_URL`/`POL_PG_DSN`) must be configured by the owner through the authorized interface; VPS access state must be revalidated; billing blocker also prevents CI-based deployment checks.
- The no-domain/test-provider staging lane (TODO-029/030) remains executable once access is revalidated — public DNS/TLS (TODO-153) is explicitly not a prerequisite for it.

## 4. RELEASE READINESS — **RELEASE NOT READY**

Independent of merge status, release requires gates that are all still open:
- TODO-055 full-suite re-run on the release-candidate SHA with CI artifacts — blocked by CI.
- TODO-056 release APK/AAB — blocked by TODO-084 (device lane, signing approvals).
- TODO-057 staging E2E — blocked (see 3).
- TODO-058 live-provider acceptance (SMS.ir live send/verify, object storage, domain/TLS) — external credentials/approvals not provided.
- TODO-059/060 business/legal decisions: D-018 refresh-token rotation (explicitly undecided), invoice timing, mutual-cancellation terms, pilot LOI verification — owner decisions, not agent-inventable.
- Non-custodial direct-payment scope preserved throughout; no custody-creating change was introduced.

## Next actions (dependency order)

1. Owner: restore Actions billing or attach secured self-hosted runner.
2. Agent: re-run the four workflows on PR #53's exact head; verify real runner steps + artifact uploads.
3. Agent: obtain review approval, merge #53, post-merge smoke on the resulting `main` tree.
4. Then: TODO-025 owner-lane (isolated Vercel QA rework), TODO-011 secrets, TODO-029 staging revalidation, TODO-084 ledger closure path, and only then device QA (TODO-009 → TODO-018…024).
