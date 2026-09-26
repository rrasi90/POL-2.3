# POL-2.3 — Remediation Re-Audit Checkpoint — 2026-09-26

## Scope

This checkpoint re-audits the remediation branch after the prior saturation audit and subsequent hardening batches. It distinguishes source-level closure from runtime/provider/governance evidence.

- Repository: rrasi90/POL-2.3
- Main at re-audit start: dbcfb9a974af53772a461db4e3f64afef70350e1
- Remediation branch: remediation/full-closure-2026-09-25
- Current branch head: 888d1cf93de3e1944503ce457c1196f623718f05
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
