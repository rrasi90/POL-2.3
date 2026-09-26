# POL-2.3 — Remediation Re-Audit Checkpoint — 2026-09-26

## Scope

This checkpoint re-audits the remediation branch after the prior saturation audit and subsequent hardening batches. It distinguishes source-level closure from runtime/provider/governance evidence.

- Repository: rrasi90/POL-2.3
- Main at re-audit start: dbcfb9a974af53772a461db4e3f64afef70350e1
- Remediation branch: remediation/full-closure-2026-09-25
- Current branch head: 194daf012ee5a8312f335ebc0123d0865aca263b
- PR: #10
- Main remains untouched by this remediation work.

## Source remediations completed in this pass

1. Auth organization switching
   - Removed a stray cursor fetch that rejected valid organization switches.
   - Added a successful-switch regression covering persisted session context and JWT org/role/session claims.

2. Retailer commerce RBAC
   - Basket create/add/allocation-preview require RETAILER_OWNER.
   - Checkout-from-allocation-plan requires RETAILER_OWNER.
   - Added PostgreSQL regression coverage for RETAILER_STAFF rejection.

3. Partial acceptance RBAC
   - Retailer approve/decline decisions require RETAILER_OWNER.
   - Notification recipient queries preserve the intended retailer staff audience where applicable.
   - Added regression for retailer staff being unable to decide a pending proposal.

4. Vendor acceptance/rejection RBAC
   - Canonical vendor accept/reject service paths now require VENDOR_OWNER, not VENDOR_STAFF.
   - VENDOR_STAFF no longer has the order.accept base permission.
   - Added acceptance/rejection and permission-map regressions.

5. Formal dispute RBAC
   - Client-facing dispute creation now requires an active RETAILER_OWNER in an active retailer organization.
   - HTTP route and application-boundary checks are both enforced.
   - Added HTTP regression for retailer staff rejection.

6. Mobile CI toolchain
   - Expo SDK 57 mobile CI was using Node 20.
   - Workflow now uses Node 22.23.1.
   - mvp package and lockfile now require Node >=22.13.0.
   - Expo SDK 57 documentation lists Node 22.13.x as the minimum.

7. Documentation/source-of-truth reconciliation
   - Screen Matrix counts/statuses reconciled.
   - Local execution tracker updated to distinguish historical device evidence from current remediation certification.
   - Deep saturation audit updated so old 526/526 and mobile success statements remain explicitly historical.
   - Known gaps register extended with G-045 through G-050.

## Current CI evidence

The remediation branch repeatedly creates GitHub Actions jobs that fail within seconds with no executed step list (steps: null). Current runs include mobile verification, independent verification, and remediation static verification. Job-log retrieval is unavailable for these runs.

Therefore:
- No new current-head green CI certification is claimed.
- Historical 497/497 backend verification and prior mobile/device passes remain historical evidence for their tested commits.
- CI failure is currently an execution/evidence blocker rather than a demonstrated code-test failure.

## Remaining items that cannot be honestly closed by source editing alone

### Governance / contract decisions
- D-018 refresh-token rotation policy wording remains explicitly open. Current implementation rotates refresh tokens and rejects replay; source behavior must not be treated as a new product policy.
- Invoice timing remains an explicit contract decision; current implementation/documentation uses invoice-on-ACCEPTED behavior.
- D-024 storefront-write scope remains read/order only until a canonical write contract is approved.

### Runtime / deployment / provider evidence
- Browser runtime/XSS verification of the web cookie/session model.
- Production cookie configuration evidence.
- Production CORS origin configuration.
- Live SMS/provider credentials and delivery evidence.
- Real driver metrics source.
- OpenPencil WAVE-02 local MCP availability.
- Fresh current-head backend/mobile CI execution.
- Fresh current-head device/runtime smoke if the certification process requires it.

### Product capability boundary still intentionally separate
- Field-assisted basket/checkout remains modeled as a retailer-context assisted flow in the approved design; the current canonical basket/checkout endpoints do not impersonate a retailer from a FIELD_ACTIVATOR session. No new impersonation capability has been invented in this remediation pass.

## Release interpretation

Source remediation is substantially advanced and the branch has additional defense-in-depth beyond the prior audit. Final release certification still requires the explicit governance decisions and external runtime/provider/deployment evidence above, plus a usable fresh CI execution.


## Post-Reaudit Source Findings Closed — 2026-09-26

- **G-052 Delegated permission evaluation ceiling:** `effective_permissions()` now filters legacy/direct delegated grants through the target-role deny ceiling; regression added in `scripts/test_delegated_permissions.py`.
- **G-053 Product media tenant/provenance:** vendor product media now requires an active vendor-product relationship in the caller's organization; operator uploads use `POL_OWNED`; regression added in `scripts/test_media_service.py`.
- **G-054 Legacy unbound uploads:** unbound `UPLOADING` assets fail closed at runtime; migration 048 invalidates legacy unbound rows and enforces a database CHECK invariant.
- **G-055 Field task contract:** the field task HTTP route and application boundary now share the same retailer/vendor target contract and resolve target organization safely; HTTP regression added.
- **G-056 Support related-order tenancy:** support case creation now requires an optional related order to belong to the active support organization; cross-tenant HTTP regression added.

**G-057 HTTP Referral Redemption:** the HTTP redemption endpoint now executes the canonical retailer first-touch attribution service with deterministic idempotency; new HTTP regression covers creation and replay.

These are source-level closures. They are not marked as fresh CI PASS because current GitHub Actions executions still terminate before reporting any workflow step.

## Post-reaudit Source Finding Closed — G-058 — 2026-09-26

- `membership_permissions()` had a projection-only RBAC drift: legacy/direct `GRANTED` rows denied by the target-role delegation ceiling could still appear in its reported `effective_permissions`.
- The projection now applies the same canonical-key and target-role deny filters as `effective_permissions()`.
- Existing regression `test_historical_owner_only_grant_cannot_become_effective` now protects both runtime evaluation and management projection.
- This is a source-level remediation. Fresh CI certification remains blocked by the current GitHub Actions execution/evidence issue.

## Post-reaudit Source Finding Closed — G-059 / G-060 — 2026-09-26

- **G-059:** `POST /auth/switch-organization` documentation incorrectly claimed refresh-token rotation. The API contract now documents the actual implementation: organization switch changes the active organization and issues a new access token; refresh-token rotation remains on `POST /auth/refresh`, while D-018 remains the open policy decision.
- **G-060:** operator invoice-list scope was narrower than the approved finance/RBAC contract. `invoices_list()` now gives active operator administration the intended read-only cross-tenant invoice visibility, while retailer/vendor paths remain organization-scoped. A new HTTP regression covers the operator list path.
- These closures are source/contract-level. Current GitHub Actions runs continue to terminate before useful workflow steps, so no fresh CI PASS is claimed.
