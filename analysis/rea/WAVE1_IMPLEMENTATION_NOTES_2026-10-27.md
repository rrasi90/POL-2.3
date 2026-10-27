# Wave 1 Implementation Notes — 2026-10-27

**Branch:** `fix/pol-wave1-qa-mock-route-docs-20261027`  
**Base:** `ui/visual-qa-screen-completion-20261025` at `09efd5b810f96634bba703f06b914ba034c9d7b9`  
**Purpose:** implement and document a first safe set of fixes from the v3 Cartona/POL handoff without changing production domain behavior or merging into the target branch.

## Changes prepared

1. **B-01 — duplicate admin route registrations**
   - Removed duplicate `POST /admin/broadcasts`, `POST /admin/broadcasts/{broadcast_id}/dispatch`, `POST /admin/categories`, and `PATCH /admin/categories/{category_id}` handlers from `scripts/api/routes/management.py`.
   - Canonical handlers remain in `scripts/api/routes/admin.py`, where the mutation routes have explicit `require_roles(...)` dependencies.
   - Added `scripts/test_admin_route_registration_uniqueness.py` and wired it into the existing static verification workflow. The check inspects router declarations directly because a normalized OpenAPI path set can hide duplicate registrations.

2. **B-02 — runtime route inventory drift (corrected during verification)**
   - Source read-back established that `scripts/api/main.py` includes `privacy_router` under `/api/v1`, and `scripts/api/routes/privacy.py` registers `POST /export` and delegates to `boundary.privacy_export()`.
   - The support router also registers `GET /support/cases/{case_id}/messages`; both routes must remain in the canonical runtime inventory.
   - An earlier edit that described `/privacy/export` as unimplemented was incorrect. This follow-up restores the route to `EXPECTED_BUSINESS_ROUTES`, removes the false known-gap assertion and corrects the API map/contract language.
   - Route registration alone does not prove privacy correctness. Own-user scoping, data minimization, output schema, audit behavior and functional coverage still require explicit behavior/security tests.

3. **B-03 — retailer mock transport**
   - Added `mvp/apps/mobile/src/mock/retailerMockTransport.ts` with synthetic retailer fixtures and isolated mock behavior for role context, catalog search, basket versioning, allocation preview, checkout, idempotency, orders/items/timeline/delivery, returns/disputes, vendor storefront, invoices, support, profile and notifications.
   - Routed retailer mock sessions to this module from `mockTransport.ts`; vendor fixtures remain separate.
   - Expanded `mvp/apps/mobile/scripts/mock_transport_qa.ts` to exercise retailer owner/staff roles, search, basket stale-version rejection, allocation totals, idempotent checkout and conflicting payload rejection, order details, timeline, storefront, invoice and support.

4. **B-08 — Persian UI text cleanup (static-only partial)**
   - Replaced visible “Master Product” with “کالای اصلی” in the retailer basket error, translated visible “SKU” search placeholders to “شناسهٔ کالا”, translated the vendor SKU label to “شناسهٔ کالای بنکداری”, and replaced the Latin x-mask in the login validation hint with a Persian-digit example.
   - This is not a full RTL/visual QA pass. Device screenshots and a full visible-string audit still require the local environment.

5. **B-06 — existing order stepper mapping was incomplete**
   - The handoff described the stepper as missing; static code inspection found a four-step order progress card already present in `OrderDetailMobileScreen.tsx`.
   - The old mapping marked `READY` as step 2 instead of step 3 and treated `ARRIVED` as though it were an order status. The progress mapping now lives in `orderProgressStage()` in `src/utils/statusLabels.ts`: accepted/preparing → step 2, ready/dispatched → step 3, delivered → step 4.
   - Added status mapping assertions to the mobile mock QA script. This is a static/logic correction and still needs actual local execution and device review.

6. **Mock response contract fidelity — timeline and support messages**
   - The live order-timeline endpoint returns an array; the retailer mock now matches that shape rather than returning a `timeline` wrapper the screen would silently ignore.
   - The support screen posts and renders `message_text`; both retailer and vendor mocks now honor that field, return `sender_type: USER`, and expose GET case messages. Vendor QA asserts read-after-write.

7. **Checkout idempotency in the retailer mock**
   - Added a canonical request fingerprint to mock checkout state. Replays with the same key and same payload return the original response; using the same key with a different payload is rejected.
   - Added a negative QA assertion for conflicting-payload reuse. This models the project's idempotency/fingerprint intent in the mock; it is not a substitute for running real QA.

8. **CI trigger scope**
   - Added the admin-route regression to the existing static workflow.
   - Expanded the `pull_request.branches` filters in both static and mobile workflows to include `ui/visual-qa-screen-completion-20261025`, so later PRs targeting this development branch can receive those checks once the workflow change is present in the base branch.
   - An attempt to run workflows from this branch returned failed jobs with `runner_id=0` and `steps=[]`; no test commands executed and logs were unavailable from the connector. Since the trigger change is part of this PR, it does not itself prove that this PR's tests ran.
   - Temporary `fix/**` push triggers were reverted to avoid triggering all fix branches.

## Required local verification before merge

From repository root, with the project virtual environment/development dependencies configured:

```powershell
$env:PYTHONPATH = "."
$env:POL_JWT_SECRET = "static-gate-secret-not-for-production"
python scripts/test_admin_route_registration_uniqueness.py
python -m pytest scripts/test_admin_route_registration_uniqueness.py scripts/test_api_boundary_route_inventory.py -q
python scripts/test_api_route_hygiene.py
```

From `mvp/` after `npm ci`:

```powershell
npm run qa:mock --workspace @pol/mobile
npm run typecheck --workspace @pol/mobile
npm run qa:functional --workspace @pol/mobile
npm run qa:regression --workspace @pol/mobile
```

Also run the full documented backend verification suite if the local PostgreSQL test environment is available. Save stdout/stderr and exit codes in the execution log. Do not merge until required tests run; fix failures instead of relabeling them as environmental without evidence.

## Acceptance checks

- Router overlap between the canonical guarded admin router and management admin router is empty.
- The four shared admin routes have exactly one declaration, in `admin.py`.
- Runtime route inventory includes registered `POST /privacy/export` and `GET /support/cases/{case_id}/messages`; registration is distinguished from full privacy-behavior verification.
- Retailer mock can complete search → create basket → add items → allocation preview → idempotent checkout → read order details.
- Timeline and support-message mock response shapes match the client contract.
- Existing vendor mock QA remains green.
- No backend business logic, schema, migrations, auth policy or production configuration was changed.
- This branch remains unmerged until the agent records local test results and reviews the PR diff.

## Reconciliation of the supplied agent execution trace — 2026-10-27

- The trace’s final summary reports `fix/pol-wave1-qa-mock-route-docs-20261027` but lists remote HEAD `09efd5b8`. That SHA is the **base SHA of PR #52** (`ui/visual-qa-screen-completion-20261025`), not proof that the Wave 1 head was synced.
- The same summary primarily describes `analysis/rea/runs/2026-10-27-cartona-remediation-deep-extraction`; those extraction artifacts and their validator do not prove the Wave 1 Python/mobile tests passed.
- The trace mentions test commands and a generic mock-QA success, but does not preserve dependable command output, exit codes and timestamps for the required Wave 1 suite.
- At review time, GitHub returned no commit status entries and no PR-triggered workflow runs for the reviewed PR head. Treat CI and local Wave 1 verification as **UNVERIFIED** until the correct branch is checked out and exact results are recorded.
- Do not merge or mark PASS solely based on the appended Cartona extraction summary.

## Verification status

**IMPLEMENTED_PENDING_LOCAL_VERIFICATION.** Remote file read-back and PR diff were verified. Automated commands have not been executed in this environment; the local agent must run the commands above, fix failures and add exact results before merge.
