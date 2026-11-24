# POL MVP — KNOWN GAPS / CONFLICTS / BLOCKED

**Rule (Master Instruction §3):** higher authority wins; log here; unresolved = screen status `GAP` + minimal stub; do not guess; do not stop build unless critical dependency.

**Status values in this file:** `RESOLVED` | `CONFLICT` | `GAP` | `BLOCKED_EXTERNAL` | `PROPOSED`

---

## G-001 — OTP digit count (CONFLICT — RESOLVED)

- **Sources:** former D-018 four-digit authentication policy versus legacy design-map six-digit references.
- **Resolution (2026-11-24):** founder amendment supersedes the former length; D-018 authentication OTP is exactly six ASCII numeric digits.
- **Implementation:** merged in PR #59. LOGIN/REGISTER accepts exactly six ASCII digits; 120s TTL, 60s resend, 3/5min phone+IP limit, five attempts and 10-minute lockout remain unchanged. Evidence: backend 852/852 on tested SHA `dbf0a228` (run 45488346802).

## G-002 — Master Tree filename / legacy reference (CONFLICT — RESOLVED)

- **Legacy reference:** an older governance document used a superseded tool-specific Master Tree filename; the active file is `50_POL_MASTER_PRODUCT_EXPERIENCE_DELIVERY_CONTROL_TREE_SPEC_…` v4.3.0.
- **Resolution:** the active file + v4.3.0 is canonical; execution tooling is not product authority.

## G-003 — Catalog list/search contract path (RESOLVED)

- **Canonical contract:** GET `/api/v1/products/search`
- **Current implementation:** `catalog_products_search` behind `/api/v1/products/search`, with `q`, optional `category_id`, `page`, `limit`, contract envelope, pagination, current lowest vendor price and available-vendor count.
- **Compatibility:** existing `/api/v1/catalog/search` remains available for current screens; it is no longer the only real path.
- **Evidence:** catalog HTTP contract test added to the verification suite.
- **Status:** RESOLVED for source/path parity; public deployed performance and media URL configuration remain deployment evidence.

## G-004 — Notifications inbox path (RESOLVED)

- **Contract:** `/api/v1/inbox/items*`
- **Current implementation:** `GET /api/v1/inbox/items`, `PATCH /api/v1/inbox/items/{item_id}/read`, and `PATCH /api/v1/inbox/items/read-all`, alongside `/api/v1/notifications` and preferences.
- **Evidence:** HTTP notification tests cover listing, unread count, deep links, tenant-scoped mark-read, idempotent mark-all-read, and read-state projection. Historical CI evidence exists for an earlier verified commit; fresh remediation CI is currently blocked before useful job-step execution.
- **Status:** RESOLVED for source + historical automated evidence; fresh post-remediation CI remains blocked.

## G-005 — Notification read/deep-link projection (RESOLVED)

- **Current canonical wire field:** `is_read`, with `deep_link` on durable inbox items.
- **Current implementation:** `/api/v1/inbox/items*` exposes unread filtering/counts and mark-one/mark-all read operations; `/api/v1/notifications` projects read state and deep link.
- **Evidence:** current notification HTTP tests pass for projection, tenant-scoped read, and idempotent read-all; earlier verification CI green is historical evidence; fresh post-remediation CI is currently blocked before useful step execution.
- **Status:** RESOLVED for source + automated CI evidence.

## G-006 — Corporate routes absent from legacy route map (RESOLVED)

- Spec 22 C-01…C-08 + Master Tree CP-* are implemented as public static pages.
- Current canonical paths are `/`, `/retailers`, `/vendors`, `/how`, `/pilot`, `/about`, `/contact`, `/legal`, matching the current `MVP_SCREEN_MATRIX.md`.
- **Status:** RESOLVED. The older route-map omission is historical documentation drift, not a runtime gap.

## G-007 — Admin users / organizations screen family (RESOLVED)

Admin user and organization list/status APIs now exist behind the canonical administrative boundary, with audit logging and session invalidation on deactivation/suspension. Web screens are connected to live data.


## G-008 — Pilot analytics O-09 HTTP (RESOLVED)

Authenticated /api/v1/ops/analytics and /api/v1/ops/analytics/weekly routes now expose the existing KPI calculation service through POLApplicationBoundary. The /ops/analytics screen consumes the live API; KPI source-of-truth remains scripts/pilot_kpis.py + scripts/analytics_lineage.py.


## G-009 — Vendor customers V-09 list API (RESOLVED)

/api/v1/vendors/customers now returns tenant-scoped retailers derived from real vendor orders, with search and pagination. /vendor/customers consumes the API and does not fabricate rows.


## G-010 — Staff/access management V-11 / permission APIs (RESOLVED)

Vendor staff list/invite/update is implemented with owner-only mutations, tenant scoping, last-owner protection and audit logs. D-026/VD-15 is now source-implemented with tenant-scoped delegated grant/revoke, effective-permission evaluation, privilege ceiling, append-only permission audit, and Web + Android Permission Editor surfaces.


## G-011 — Admin broadcasts / SLA overrides / category admin (RESOLVED)

- `POST /admin/sla-overrides`, `POST/PATCH /admin/categories`, and `POST /admin/broadcasts` + dispatch are REAL and audited.
- **Status:** RESOLVED.

## G-012 — Basket current GET (RESOLVED)

- `GET /api/v1/baskets/current` exists and the application boundary owns current-basket retrieval.
- **Status:** RESOLVED

## G-013 — Returns list all-orders (RESOLVED)

Ops now has /api/v1/ops/returns for a tenant-independent operational workbench over all returns, and /ops/rma consumes it directly.


## G-014 — Design contradictions register (RESOLVED)

Prior research noted: brand blue vs tokens, type scale variants, radius, motion bands, density labels, WCAG version wording, Latin fallback font, breakpoints, focus ring details, golden-screen set.
- **Resolution:** doc 56 (Precision Commerce) wins for visual tokens; motion bands 120–160 / 160–240 / 200–280 / ≤400ms; WCAG 2.2 where doc 21/22 adopt it.
- Anything still undefined at implement time → new `G-0xx` + `PROPOSED` token marked in code.
- **Status:** RESOLVED. The canonical visual design system defines the active token hierarchy, typography, spacing, radius, motion, density, WCAG reference, RTL, responsive and golden-screen requirements. New material changes must be registered as explicit decisions rather than treated as inherited contradictions.

## G-015 — OP-06 / OP-09 missing from Master Tree §9 listing (CONFLICT — RESOLVED)

- Spec 22 has O-06, O-09; Master Tree tree listing gaps numbering.
- **Resolution:** implement per spec 22 (higher for screen detail after decisions); tree is navigation aid.
- **Status:** RESOLVED for current build/source mappings; historical section numbering remains evidence only.

## G-016 — Phase C dead routes (HISTORICAL — RESOLVED)

- `/admin/users`, `/admin/orgs`, `/ops/finance`, `/ops/reconciliation` were nav-only.
- **Build:** only routes in SCREEN_MATRIX with sources; no dead links.

## G-017 — Backend HTTP coverage 21/50 at inventory snapshot (HISTORICAL — RESOLVED)

- Many CONTRACT endpoints not yet on FastAPI at Stage 07 snapshot; research-hardening added many REAL routes (orders list, support, field, etc.) beyond that snapshot.
- **Build:** prefer REAL map in API_MAP §3; remaining CONTRACT → MOCK same-contract.
- **Status:** RESOLVED on the current remediation branch: canonical ledger is now 50/50 HTTP_IMPLEMENTED; runtime CI evidence remains the release gate.

## G-018 — Android readiness RED in design audit 60 (HISTORICAL)

- Dual-client mandated (D-026) but audit marks Android RED pre-build.
- **Build:** Phase 3 still required by contract; not a Phase 0 blocker.
- **Status:** HISTORICAL / RESOLVED. Mobile implementation and prior local/device verification exist on the current project line; final CI runner evidence remains separate.

## G-019 — Working tree lacks many canonical files (HISTORICAL — RESOLVED)

- Docs on `origin/product-architecture-evolution-2026-09-20` / research-hardening; working tree `main` has partial 50/56 staged.
- **Resolution:** `git show <ref>:<path>` for reads (§2.8); do not switch branches unless necessary.
- **Status:** HISTORICAL / RESOLVED. The active source-of-truth references now point only to files present on the current remediation branch; missing historical documents are not treated as active authority.

## G-020 — Corporate `PUBLIC_ANON` not a backend role (RESOLVED — BY DESIGN)

- Marketing screens need no auth; no API required for C-01…08 static content.
- **Status:** RESOLVED (by design). Corporate surfaces are static public pages and intentionally do not require an authenticated backend role.

## G-021 — Partial-acceptance proposal list (RESOLVED)

- `GET /api/v1/orders/{order_id}/partial-acceptance-proposals` now returns the canonical proposal rows and item reductions, with vendor/retailer tenant scoping.
- **Status:** RESOLVED

## G-022 — Delivery OTP schema vs D-018 (RESOLVED)

- **Sources:** D-029 requires six-digit newly issued delivery OTPs. The prior four-digit delivery format remains a data-compatibility exception only for codes already issued to in-flight deliveries before migration 077.
- **Resolution (2026-11-24):** new dispatches use six ASCII digits via DELIVERY_OTP_CODE_LENGTH and secure randomness. Migration 077 stores the actual length of existing delivery codes without rotating or re-sending them; a previously issued four-digit in-flight code may complete only its original delivery.
- **Status:** RESOLVED — PR #59 merged; migration 077 applied and verified in PostgreSQL 18 CI on tested SHA `dbf0a228` (run 45488346802).

---

## How to add

```
## G-0xx — Title (TYPE)
- Sources: …
- Resolution / Build action: …
- Status: …
```

Update SCREEN_MATRIX status + API_MAP when an entry changes.

## Phase 3 / live-e2e execution notes — 2026-09-23

- Historical mobile CI cycles remain evidence, but the current remediation branch must not inherit their green certification automatically because fresh GitHub runs currently fail before useful step execution.
- D-028 barcode matching is implemented at the canonical API boundary, with legacy and extended request compatibility; camera/device transport remains a client/runtime concern.
- Mobile Night theme verification and live checkout/idempotency are now recorded as LOCAL-01…04 PASS in the execution tracker; deployment/runtime evidence remains separate.
- Live basket → allocation → checkout e2e remains pending in the local environment because the current catalog seed/search path and orderability criteria still need live verification. This is an execution task, not a reason to stop other work.


## G-023 — Field assisted catalog empty-query request (RESOLVED)

- Finding: F-03 AssistedOrderScreen previously issued GET /api/v1/catalog/search?limit=40 when the query was empty, while the authoritative route requires q with min_length=1.
- Source remediation (2026-09-24): Mobile now short-circuits an empty query locally and never calls the route without q; the explicit search action reports that the query is required.
- Status: RESOLVED — post-remediation device retest PASS (2026-09-24).

## G-024 — Field assisted catalog product field mapping (RESOLVED)

- Finding: F-03 catalog rows could fall back to — because the API canonical fields are canonical_name_fa and master_sku, while the mobile adapter primarily expected name / sku.
- Source remediation (2026-09-24): Mobile now prefers canonical_name_fa for display and master_sku for SKU fallback, while retaining compatibility fallbacks.
- Status: RESOLVED — post-remediation device retest PASS (2026-09-24).

## G-025 — Mobile Night theme runtime wiring (RESOLVED)

- Finding: Night palette existed but runtime styles were created statically and there was no user-facing Light/Night control; changing system UI mode therefore did not update the rendered app.
- Source remediation (2026-09-24): Added centralized runtime theme context, dynamic themed style factories for mobile screens/shared components, system-aware initial mode, and explicit Light/Night controls in Account. app.json now uses automatic interface style.
- Status: RESOLVED for runtime wiring — post-remediation Night-theme device retest PASS (2026-09-24); broader screen-by-screen visual coverage remains a separate QA scope if required.

## G-026 — Mobile phone input vs E.164 contract (RESOLVED)

- Finding: Authentication storage/test fixtures use E.164 (+...), while the mobile login UI accepted/displayed local 09... input without normalization.
- Source remediation (2026-09-24): Mobile normalizes Iranian local numbers to E.164 before auth and backend OTP request/verification schemas now enforce the E.164 pattern.
- Status: RESOLVED — local authentication/device retest PASS (2026-09-24).

## G-029 — Web token persistence uses localStorage (SECURITY GAP — RESOLVED)

- **Historical source finding (2026-09-24):** the web auth store persisted access/refresh bearer credentials in browser localStorage.
- **Current source remediation:** mvp/apps/web/src/lib/auth/store.ts now persists profile metadata only; accessToken remains in memory. Browser refresh uses the server-managed `pol_refresh` HttpOnly/Secure/SameSite cookie.
- **Transport hardening:** web verify/refresh endpoints do not expose the refresh credential in JSON when the cookie-backed flow is used; refresh tests assert this behavior.
- **Residual verification:** browser-runtime/XSS and production-cookie deployment evidence remain separate release evidence.
- **Status:** SOURCE REMEDIATED; final release gate is CI/runtime evidence.

## G-030 — Browser-to-API CORS policy was not previously explicit (RESOLVED)

- **Finding:** web API client uses a separate API base origin while FastAPI had no explicit CORS policy in the audited transport source.
- **Source remediation (2026-09-24):** FastAPI now applies environment-scoped CORS with explicit local development origins, requires POL_CORS_ORIGINS in production, forbids wildcard production CORS, and has a transport test for allowed/blocked origins.
- **Status:** SOURCE REMEDIATED; final release gate is CI/runtime evidence.

## G-031 — Duplicate barcode route / schema collision (RESOLVED — 2026-09-25)

- Finding: two route modules registered the same POST /api/v1/products/match-barcode path with incompatible request models.
- Resolution: one canonical route now serves both legacy and extended request shapes; duplicate registration was removed; route uniqueness regression coverage was added.
- Status: RESOLVED in source; fresh CI certification remains separate.

## G-032 — Direct candidate idempotency / notification targeting (RESOLVED — 2026-09-25)

- Finding: direct candidate creation could create a new candidate and overwrite an existing vendor-SKU association, and candidate-created outbox events lacked recipient targets.
- Resolution: advisory-lock serialization, existing-association replay, rejection protection, tenant-aware authorization, targeted outbox fields and dedupe key, plus HTTP regression coverage were added.
- Status: RESOLVED in source; fresh CI certification remains separate.

## G-033 — Deterministic OTP outside explicit test environment (SECURITY GAP — REMEDIATED)

- **Finding (2026-09-25):** AuthService.request_otp previously selected deterministic `1234` for every non-production environment, so an unset/unknown environment could silently inherit the test credential.
- **Resolution:** deterministic OTP is now allowed only when `ENVIRONMENT=test` and production-mode detection is false. All other environments use cryptographically random six-digit OTPs under the amended D-018 policy. The `test_code` response field is exposed only in the explicit test environment.
- **Regression proof:** scripts/test_auth_contract.py::test_static_otp_is_strictly_test_only covers explicit test mode plus development, unknown and unset environment cases.
- **CI status:** the six-digit OTP generation/authentication path and test-only deterministic behavior passed the PR #59 full backend suite (852/852, run 45488346802).
- **Status:** SOURCE REMEDIATED / CI VERIFIED for the PR #59 tested SHA.

## G-034 — Delivery exception notification routing (RESOLVED — 2026-09-25)

- Finding: delivery exception outbox events were emitted without explicit user/organization targets, while the canonical integration worker requires explicit routing.
- Resolution: report events route to active vendor members, resolved events to active retailer members, escalation events to active operator/admin members; per-recipient dedupe keys and INBOX channel hints are persisted.
- Additional hardening: report/get/list/resolve/escalate paths now enforce tenant and actor boundaries at the service layer.
- Notification templates added in migration 042.
- Status: RESOLVED in source; fresh CI certification remains separate.

## G-035 — Fulfillment lifecycle notification template coverage (RESOLVED — 2026-09-25)

- Finding: lifecycle events emitted by fulfillment/timeout workers included PREPARING, READY, DISPATCHED, DELIVERY_OTP_GENERATED, DELIVERED and CANCELLED, but the notification template registry did not cover all emitted events.
- Resolution: migration 045 adds active INBOX templates for all six events. ORDER_DELIVERED and ORDER_CANCELLED now route to both commercial parties where the canonical notification matrix requires it.
- Status: RESOLVED in source; fresh CI certification remains separate.
## G-036 — Barcode-only candidate concurrency (RESOLVED — 2026-09-25)

- Finding: application-level replay checks did not by themselves guarantee uniqueness when two barcode-only candidate submissions raced concurrently.
- Resolution: migration 046 adds a partial unique index on (vendor_id, barcode) for PENDING_REVIEW candidates; the application insert uses the same conflict target and re-reads the canonical candidate on conflict.
- Status: RESOLVED in source; fresh CI certification remains separate.
## G-037 — Notification worker inactive-user delivery (RESOLVED — 2026-09-25)

- Finding: canonical integration validated active organization membership but did not also require users.is_active.
- Resolution: worker now verifies active user + active membership + active organization; membership-isolation regression coverage adds an inactive-user case.
- Status: RESOLVED in source; fresh CI certification remains separate.
## G-038 — Duplicate payment verification HTTP route (RESOLVED — 2026-09-25)

- Finding: POST /api/v1/orders/{order_id}/payments/verify was registered twice in the same router.
- Resolution: retained the canonical implementation and removed the duplicate registration; route uniqueness regression now covers this class automatically.
- Status: RESOLVED in source; fresh CI certification remains separate.
## G-039 — Boundary role resolution trusted inactive users/orgs (RESOLVED — 2026-09-25)

- Finding: the central application-boundary role resolver accepted ACTIVE memberships without independently checking users.is_active and organizations.status.
- Resolution: role resolution now requires active user, active membership and active organization; batch contract regression covers inactive-user and suspended-organization contexts.
- Status: RESOLVED in source; fresh CI certification remains separate.
## G-040 — Payment evidence tenant isolation and retry idempotency (RESOLVED — 2026-09-25)

- Finding: evidence reads were order-ID based without explicit tenant authorization, and duplicate submissions using the globally unique external reference could surface as a raw database conflict.
- Resolution: reads require active retailer/vendor tenant membership; submissions require an active user; repeated external references return the existing evidence for the same payment with idempotent_replay=true, while cross-payment reuse is rejected.
- Regression coverage: wrong-tenant read plus same-reference replay HTTP tests.
- Status: RESOLVED in source; fresh CI certification remains separate.


## G-041 — Bearer/refresh token validity after principal deactivation (SECURITY GAP — REMEDIATED — 2026-09-26)

- **Finding:** access-token validation trusted an ACTIVE session + ACTIVE membership without independently checking `users.is_active` and `organizations.status`; refresh-token validation had the same omission.
- **Resolution:** `validate_access_token` now requires active user + active organization + active membership. `AuthService.refresh_access_token` enforces the same principal checks before issuing a new access token or rotating the refresh token.
- **Regression proof:** `scripts/test_auth_contract.py` now covers inactive-user and inactive-organization rejection for both bearer access tokens and refresh tokens.
- **Status:** SOURCE REMEDIATED / FRESH CI PENDING


## G-042 — Payment evidence / verification role drift (SECURITY GAP — REMEDIATED — 2026-09-26)

- **Finding:** payment evidence submission previously allowed `RETAILER_STAFF`; payment verification previously allowed `VENDOR_STAFF`, exceeding the current payment responsibility boundary.
- **Resolution:** retailer-side payment evidence now requires `RETAILER_OWNER`; verification now requires `VENDOR_OWNER` or authorized ops/admin roles. Vendor-side evidence collection remains available for the evidence types already defined by the API contract.
- **Regression proof:** `scripts/test_http_payment_evidence.py` adds explicit Retailer Staff submission rejection and Vendor Staff verification rejection.
- **Status:** SOURCE REMEDIATED / FRESH CI PENDING


## G-043 — Presigned media upload target retargeting (SECURITY GAP — REMEDIATED — 2026-09-26)

- **Finding:** the presign request authorized one target, but confirm-upload accepted a caller-supplied target independently; an upload could therefore be rebound to another object accessible to the same actor.
- **Resolution:** migration `048_bind_media_upload_target.sql` binds `upload_target_type` + `upload_target_id` to the presigned asset. Confirmation rejects any target mismatch before storage finalization.
- **Regression proof:** `scripts/test_media_service.py::test_presigned_upload_target_cannot_be_retargeted` plus schema assertions for migration 048.
- **Status:** SOURCE REMEDIATED / FRESH CI PENDING


## G-044 — Authentication OTP purpose / organization binding (SECURITY GAP — REMEDIATED — 2026-09-26)

- **Finding:** authentication OTP verification selected the latest pending challenge by phone without restricting its purpose to LOGIN/REGISTER, and it did not require the selected organization itself to be ACTIVE.
- **Resolution:** auth verification now accepts only LOGIN/REGISTER challenges and requires an ACTIVE user, ACTIVE membership, and ACTIVE organization before session creation.
- **Regression proof:** `scripts/test_auth_contract.py` covers suspended-organization rejection and prevents ORDER_CONFIRMATION challenges from being consumed by authentication verification.
- **Status:** SOURCE REMEDIATED / FRESH CI PENDING


## G-045 — Organization switch valid-target regression (SECURITY / CORRECTNESS — REMEDIATED — 2026-09-26)

- **Finding:** `AuthService.switch_organization` performed an additional `cur.fetchone()` after validating the target membership. No query preceded that fetch, so the cursor returned no row and every otherwise-valid organization switch was rejected.
- **Resolution:** removed the stray cursor fetch. Target user/session ownership, session state, target membership, user state and organization state remain explicitly validated before the session context is updated.
- **Regression proof:** `scripts/test_auth_contract.py::test_p0_switch_organization_valid_target_succeeds` now verifies successful tenant switching, persisted active organization, and the newly issued JWT role/org/session claims.
- **Status:** SOURCE REMEDIATED / FRESH CI PENDING


## G-046 — Retailer staff commerce-command overreach (SECURITY / RBAC — REMEDIATED — 2026-09-26)

- **Finding:** basket creation/modification/allocation and checkout were reachable from an active RETAILER_STAFF membership even though the approved role matrix reserves basket creation/checkout authority to RETAILER_OWNER (with field-assisted execution handled separately).
- **Resolution:** canonical basket/allocation mutations now explicitly require RETAILER_OWNER; checkout-from-allocation-plan now resolves only an active RETAILER_OWNER membership.
- **Regression proof:** scripts/test_basket_allocation_application.py covers staff rejection for basket create/add/allocation; checkout source authorization is owner-only.
- **Status:** SOURCE REMEDIATED / FRESH CI PENDING

## G-047 — Retailer staff partial-acceptance decision overreach (SECURITY / RBAC — REMEDIATED — 2026-09-26)

- **Finding:** partial-acceptance approve/decline queries accepted both RETAILER_OWNER and RETAILER_STAFF, allowing a staff member to make a quantity/financial order decision.
- **Resolution:** canonical partial-acceptance approve/decline now require an active RETAILER_OWNER; vendor-side proposal creation remains governed by the vendor acceptance permission.
- **Regression proof:** scripts/test_partial_acceptance.py::test_retailer_staff_cannot_decide_partial_acceptance verifies the decision is rejected and the proposal remains PENDING.
- **Status:** SOURCE REMEDIATED / FRESH CI PENDING

## G-048 — Vendor staff order-acceptance permission drift (SECURITY / RBAC — REMEDIATED — 2026-09-26)

- **Finding:** VENDOR_STAFF still carried the generic order.accept permission even though the approved role matrix assigns order acceptance/rejection to VENDOR_OWNER.
- **Resolution:** order.accept was removed from the VENDOR_STAFF baseline permission set; vendor owner retains it.
- **Regression proof:** scripts/test_delegated_permissions.py::test_vendor_staff_role_does_not_receive_order_accept_permission.
- **Status:** SOURCE REMEDIATED / FRESH CI PENDING


## G-049 — Retailer staff formal-dispute opening overreach (SECURITY / RBAC — REMEDIATED — 2026-09-26)

- **Finding:** the formal dispute-open path enforced retailer tenancy but did not independently restrict the actor to RETAILER_OWNER, allowing a retailer staff membership to invoke the client-facing dispute command.
- **Resolution:** both the HTTP route and the application boundary now require an active RETAILER_OWNER membership in an active retailer organization.
- **Regression proof:** scripts/test_http_returns_disputes.py::TestDisputeOpen::test_retailer_staff_cannot_open_formal_dispute.
- **Status:** SOURCE REMEDIATED / FRESH CI PENDING


## G-050 — Expo SDK 57 CI Node-runtime mismatch (TOOLCHAIN — REMEDIATED — 2026-09-26)

- **Finding:** the mobile verification workflow used Node 20 while the repository's Expo SDK 57 stack requires Node 22.13.x or newer.
- **Resolution:** mobile CI now uses Node 22.23.1; mvp/package.json and the lockfile declare Node >=22.13.0.
- **Evidence:** Expo's current SDK reference lists 22.13.x as the minimum Node.js version for SDK 57.
- **Status:** SOURCE REMEDIATED / FRESH CI EXECUTION BLOCKED BEFORE STEPS


## G-051 — Delegated permission could reintroduce owner-only capabilities (SECURITY / RBAC — REMEDIATED — 2026-09-26)

- **Finding:** removing an owner-only capability from a staff role's baseline permission set did not by itself prevent an owner from re-granting that capability through delegated permissions.
- **Resolution:** role-aware delegation ceilings now explicitly block owner-only capabilities such as VENDOR_STAFF order acceptance and membership management.
- **Regression proof:** scripts/test_delegated_permissions.py::test_owner_only_permissions_cannot_be_delegated_to_vendor_staff.
- **Status:** SOURCE REMEDIATED / FRESH CI PENDING


## G-052 — Delegated Permission Ceiling Must Hold at Evaluation Time
**Class:** Security / RBAC / Defense-in-Depth  
**Finding:** Earlier hardening blocked new grants of owner-only permissions to restricted roles, but a legacy or directly seeded GRANTED row could still be added to effective_permissions() and become active.  
**Remediation:** Effective-permission evaluation now filters delegated grants through the canonical role delegation-deny ceiling and ignores unknown/non-canonical delegated permission keys. The membership-management response exposes the same target-role-aware delegation ceiling.  
**Regression:** `scripts/test_delegated_permissions.py` covers both the direct legacy-grant path and the exposed delegatable-permission catalog.  
**Status:** **SOURCE REMEDIATED / FRESH CI PENDING**

## G-053 — Product Media Authorization Must Be Vendor-Product Scoped
**Class:** Security / Multi-Tenancy / Media Provenance  
**Finding:** Product media authorization previously checked only that the actor belonged to a vendor/operator organization. A vendor member could therefore attempt to attach media to an unrelated Master Product outside that vendor's active product relationship. Operator uploads also inherited VENDOR_UPLOADED provenance.  
**Remediation:** Vendor product-media authorization now requires an active `vendor_products` relationship for the target Master Product in the actor's organization. Operator-authorized product media is recorded with `POL_OWNED` provenance; canonical OPS and legacy aliases are accepted consistently.  
**Regression:** `scripts/test_media_service.py` covers vendor ownership, unrelated-tenant rejection and operator provenance.  
**Status:** **SOURCE REMEDIATED / FRESH CI PENDING**

## G-054 — Legacy In-Flight Media Uploads Must Fail Closed
**Class:** Security / Upload Integrity / Migration Safety  
**Finding:** Migration 048 introduced upload target binding, but pre-migration `UPLOADING` rows with a null target could otherwise reach confirmation because the runtime validator treated a missing binding as implicitly acceptable.  
**Remediation:** Confirm-upload now rejects any `UPLOADING` asset without an immutable target binding. Migration 048 invalidates legacy unbound `UPLOADING` rows as `DELETED` and adds a PostgreSQL CHECK invariant requiring both target fields for every in-flight upload.  
**Regression:** `scripts/test_media_service.py` covers missing-binding rejection.  
**Status:** **SOURCE REMEDIATED / FRESH CI PENDING**


## G-055 — Field Task HTTP/Boundary Contract Alignment
**Class:** Runtime Contract / API Integration / Field Operations  
**Finding:** `/api/v1/field/tasks` passed `retailer_id`/`vendor_id`, while the application boundary previously accepted only `target_organization_id`, creating a transport-to-domain signature mismatch.  
**Remediation:** `field_task_create()` now accepts the route contract, resolves retailer/vendor targets to their active organization, rejects ambiguous target combinations, and validates the target organization and assigned user state before insertion.  
**Regression:** `scripts/test_http_field_tasks.py` now creates a real retailer target and verifies the resolved target organization through the HTTP endpoint.  
**Status:** **SOURCE REMEDIATED / FRESH CI PENDING**

## G-056 — Support Case Related Order Must Be Tenant-Bound
**Class:** Security / Multi-Tenancy / Referential Integrity  
**Finding:** Support case creation checked the active support organization but did not independently verify that an optional `related_order_id` belonged to that same retailer/vendor organization. A guessed order UUID could therefore be persisted as a cross-tenant support reference.  
**Remediation:** `CanonicalSupportService.create_case()` now verifies active membership and requires the related order to resolve through its retailer or vendor organization to the active support tenant before insertion.  
**Regression:** `scripts/test_http_support.py` creates an order under another retailer organization and verifies support creation is rejected with HTTP 403.  
**Status:** **SOURCE REMEDIATED / FRESH CI PENDING**


## G-057 — HTTP Referral Redemption Must Materialize Attribution
**Class:** Functional Correctness / Referral Lifecycle / API-Domain Contract  
**Finding:** The HTTP `POST /api/v1/referrals/{referral_id}/redeem` boundary previously treated redemption as a vendor-side counter increment and did not execute the canonical retailer first-touch attribution flow required by D-016.  
**Remediation:** The boundary now resolves the active retailer from the authenticated organization, loads the canonical referral independently of vendor tenant, and delegates redemption to `VendorReferralService.redeem_referral()` using a deterministic HTTP idempotency key. This persists `vendor_referral_attributions` and emits the canonical analytics outbox event while keeping retailer first-touch uniqueness.  
**Regression:** New `scripts/test_http_referrals.py` verifies first redemption creates an attribution and a repeated HTTP redemption replays without incrementing the quota twice.  
**Status:** **SOURCE REMEDIATED / FRESH CI PENDING**

## G-058 — Delegated Permission Projection Drift (SECURITY / RBAC — REMEDIATED — 2026-09-26)

- **Finding:** `membership_permissions()` previously added every `GRANTED` delegated permission to its reported `effective_permissions`, even when the target role's canonical delegation ceiling denied that capability or the key was non-canonical. This could make the management projection disagree with the runtime `effective_permissions()` evaluator.
- **Resolution:** the membership projection now applies the same canonical-permission and target-role deny-ceiling filters as runtime authorization before reporting an effective delegated permission.
- **Regression proof:** `scripts/test_delegated_permissions.py::test_historical_owner_only_grant_cannot_become_effective` asserts that a legacy owner-only grant does not appear in the projected effective permissions.
- **Status:** **SOURCE REMEDIATED / FRESH CI PENDING**

## G-059 — Organization-Switch Refresh-Token Documentation Drift (CONTRACT / AUTH — REMEDIATED — 2026-09-26)

- **Finding:** `06_PRODUCT/API_Contracts.md` stated that `POST /auth/switch-organization` rotates and replaces the refresh-token hash, while the actual `AuthService.switch_organization()` implementation only updates the active organization and issues a new access token.
- **Resolution:** API documentation now reflects the implementation: refresh rotation occurs on `POST /auth/refresh`; organization switching does not rotate the refresh token. D-018 remains the governing open policy decision and no new behavior was invented.
- **Regression / evidence:** source-contract inspection confirms the documented response and implementation path are aligned; future policy changes must be recorded as a superseding D-018 decision before changing either behavior.
- **Status:** **SOURCE/DOC REMEDIATED / FRESH CI PENDING**

## G-060 — Operator Invoice List Scope Drift (SECURITY / FINANCE / API CONTRACT — REMEDIATED — 2026-09-26)

- **Finding:** the canonical RBAC/API contract grants `ADMIN_SUPER`/`OPS_ADMIN` read access to formal invoices, and `invoice_get()` already treated operator actors as global read-only viewers, but `invoices_list()` filtered operator users by their OPERATOR organization ID. Because invoices are owned by retailer/vendor organizations, operator invoice listings could therefore be empty even though direct detail access was permitted.
- **Resolution:** operator invoice listing now uses an explicit read-only global scope (`WHERE 1 = 1`), while retailer/vendor tenants remain strictly organization-scoped.
- **Regression proof:** `scripts/test_http_finance.py::TestInvoiceList::test_ops_list_cross_tenant_invoices` creates an active `ADMIN_SUPER` operator session and verifies that an invoice belonging to separate retailer/vendor tenants is returned by the operator list endpoint.
- **Status:** **SOURCE REMEDIATED / FRESH CI PENDING**

## G-061 — Vendor Referral Create Contract Drift (API / UI / DOMAIN — REMEDIATED — 2026-09-26)

- **Finding:** the Vendor Referral create path diverged across layers: the UI sent `code`, the HTTP schema required an unrelated `referred_retailer_id`, the application boundary wrote `vendor_referrals` directly instead of using the canonical D-016 service, and an older HTTP regression redeemed a referral using the vendor token rather than a retailer token. This made the V-08 create flow incompatible with the canonical first-touch model.
- **Resolution:** referral creation now accepts an optional `referral_code` and optional quota/expiry controls, generates a canonical `POLV-XXXXXXXX` code when omitted, validates custom codes in the canonical `VendorReferralService`, and the HTTP boundary delegates to that service. The web client sends/reads `referral_code`. Referral redemption tests now use the retailer identity and verify attribution plus quota behavior.
- **Contract source:** D-016 — vendor creates a referral code/link; retailer redeems once as first-touch attribution; no reward/wallet engine in MVP.
- **Status:** **SOURCE REMEDIATED / FRESH CI PENDING**

## G-062 — Field Task Lifecycle Transition Gap (DOMAIN INTEGRITY — REMEDIATED — 2026-09-26)

- **Finding:** `field_tasks.status` had a DB enum/check constraint but `PATCH /field/tasks/:id` accepted any allowed status from any current state, permitting rollback or impossible jumps such as `IN_PROGRESS -> ASSIGNED` or changing terminal tasks back into active work.
- **Resolution:** the application boundary now enforces the canonical transition graph: `ASSIGNED -> IN_PROGRESS/FAILED/CANCELLED`; `IN_PROGRESS -> COMPLETED/FAILED/CANCELLED`; `FAILED -> IN_PROGRESS/CANCELLED`; `COMPLETED` and `CANCELLED` are terminal for status. The HTTP schema constrains the status vocabulary and the Field Task detail UI only offers valid next states while still allowing notes updates.
- **Regression proof:** `scripts/test_http_field_tasks.py::TestFieldTaskCRUD::test_task_cannot_roll_back_from_in_progress_to_assigned` verifies server rejection and state preservation after an invalid rollback.
- **Status:** **SOURCE REMEDIATED / FRESH CI PENDING**

## G-063 — Last Active Vendor Owner Suspension Gap (IAM / TENANT INTEGRITY — REMEDIATED — 2026-09-26)

- **Finding:** `vendor_staff_update` protected the last active `VENDOR_OWNER` from demotion/revocation but allowed that same last owner to be suspended, potentially leaving the vendor organization without any active owner and therefore without an operator able to manage staff/access.
- **Resolution:** the last-owner safeguard now treats `SUSPENDED` exactly like `REVOKED`/demotion. At least one other active vendor owner must exist before an active owner can be suspended, revoked, or demoted.
- **Regression proof:** `scripts/test_http_management.py::test_vendor_owner_cannot_suspend_last_active_owner` verifies HTTP rejection and membership state preservation.
- **Status:** **SOURCE REMEDIATED / FRESH CI PENDING**


---

# 2026-09-26 — Deep Audit Remediation Intake Register

This section is the persistent intake ledger for findings previously identified in the deep audit/remediation conversations but not yet demonstrably closed by the current remediation line.

**Rule:** Registration is not closure. Each item remains **OPEN** until a source fix, regression/evidence record, and persisted closure entry exist. Historical PASS evidence does not close a later finding.

## A. Previously identified deep-audit gaps — individually actionable

| ID | Severity | Finding | Status |
|---|---:|---|---|
| G-308 | P1 | Operating-window selection can resolve weekday from capacity timezone before applying the window timezone; deterministic cross-timezone semantics are incomplete. | RESOLVED — source fix a4683721; regression 4fc8804e |
| G-309 | P1 | Cross-midnight operating windows do not resolve the previous weekday after midnight. | RESOLVED — source logic introduced with G-308; regression e64ea3bd |
| G-310 | P1 | Overnight `order_cutoff_at` lacks day-offset/instant semantics. | RESOLVED — source ad8b827e; regression 570a6452 |
| G-311 | P1 | Daily/hourly vendor capacity is check-then-act and lacks atomic reservation/invariant enforcement. | RESOLVED — transactional advisory lock 4f6f8aec; regression 59f83384 |
| G-312 | P1 | Admin audit immutability is not DB-enforced against UPDATE/DELETE. | RESOLVED — migration 049 / 6dd3791e; regression 03979c4c |
| G-313 | P1 | Inventory audit history can be cascaded away through `vendor_product_id`. | RESOLVED — migration 050 / 4a87a750; regression b3008be1 |
| G-314 | P1 | Notification retention/expiry is not canonically populated and no auto-archive worker is evidenced. | RESOLVED — migration 051 / d209963c; worker 63adf6d1; regression 061c7d88 |
| G-315 | P1 | Privacy export/account-deletion lifecycle lacks a runtime API/workflow. | RESOLVED — migration 052 / 1603218e; service c8d01227; HTTP a74da82a; route registry 7ee49596; regression 1fbf3511 |
| G-316 | P1 | Runtime media schema diverges from canonical media specification; approval/provenance/media-type/checksum semantics are incomplete. | RESOLVED — migration 053 / 6fa46ec8; service 3ff27c8f; schema docs bd5d5261; regression f5f5b0df |
| G-317 | P1 | Public product-media serving lacks canonical approval/provenance/private-reference gating. | RESOLVED — query e1991dd5; regression 31f2c994 |
| G-318 | P1 | Canonical media ingestion pipeline (presign → confirm → validate → process → thumbnail/resumable) is not fully implemented/evidenced. | RESOLVED_CODE / EXTERNAL_EVIDENCE_PENDING — migration b6cb7877; service 6ccc1618→3af490e5; API 2564d61; regression 408639c5→6ccc1618 |
| G-319 | P1 | POD/dispute media references lack READY + ownership + tenant + purpose validation. | RESOLVED — validator b7c4e56a; dispute 7c078b5f; POD 891778b1; regression a0a5d55b |
| G-320 | P2 | DB media DELETED lifecycle lacks explicit object-storage reconciliation. | RESOLVED_CODE / PROVIDER_EVIDENCE_PENDING — migration 2b7c4d6e; worker 47656dc4; regression fd611fe5 |
| G-325 | P1 | Basket/allocation stale-version handling and checkout consistency require complete canonical enforcement. | RESOLVED — gateway/revalidation source; stale regression already persisted |
| G-326 | P1 | Stale-checkout must return a canonical 409 Conflict contract. | RESOLVED — 409 mapper 7f11226a; stale exception 2f221746; HTTP regression af860ce5 |
| G-327 | P1 | Checkout must be atomic across allocation/order/reservation mutations. | RESOLVED_SOURCE/REGRESSION — transactional gateway + rollback test d8e8a5aa |
| G-328 | P1 | Client/server basket-allocation-checkout state coherence is incomplete. | RESOLVED_CODE / DEVICE_EVIDENCE_PENDING — mobile 753d5e5c; API 2493c647; QA 8f1c2b60 |
| G-329 | P1 | DB/runtime evidence for stale/concurrent basket/checkout invariants is incomplete. | RESOLVED_CODE / EXECUTION_EVIDENCE_PENDING — stale validation existing regression; rollback d8e8a5aa; HTTP 409 af860ce5 |
| G-330 | P1 | Allocation tie-breaking is not fully deterministic. | RESOLVED_CODE / EXECUTION_PENDING — source 6dcaa74c/9377e38a; regression 12964486 |
| G-331 | P1 | Allocation tie-selection semantics are incomplete/under-specified in runtime. | RESOLVED_CODE / EXECUTION_PENDING — source 6dcaa74c/9377e38a; regression 12964486 |
| G-332 | P1 | Allocation ignores/removes pack_quantity semantics in candidate scoring/selection. | RESOLVED_CODE / EXECUTION_PENDING — source 6dcaa74c/9377e38a/b8b673ea; regression 12964486 |
| G-333 | P1 | Allocation behavior for K>=3 vendors is not fully covered by deterministic tests. | RESOLVED_CODE / EXECUTION_PENDING — regression 12964486 |
| G-334 | P1 | Allocation-result identity/hash does not fully cover canonical input/decision identity. | RESOLVED_CODE / EXECUTION_PENDING — source 6dcaa74c/9377e38a/b8b673ea/0c759d1c/a3d0a358/cba145bd; regression 12964486 |
| G-335 | P1 | Allocation regression coverage is incomplete for adversarial/tie/packing cases. | RESOLVED_CODE / EXECUTION_PENDING — regression 12964486 |
| G-336 | P1 | Reservation-expiry worker/runtime path is not fully evidenced as canonical. | RESOLVED_CODE / EXECUTION_PENDING — worker existing + boundary 621b170a; regression 3ecea65c |
| G-337 | P1 | Retailer cancellation/release of active reservation is incomplete. | RESOLVED_CODE / EXECUTION_PENDING — service d5c4716b; boundary 1043c57c; route 98e9ddb1; regression c8cd55c7 |
| G-338 | P1 | Reservation time semantics are not fully aligned with the canonical checkout/Journey timing contract. | RESOLVED_CODE / EXECUTION_PENDING — source 04e105d5; regression 6f6ae7ae |
| G-339 | P1 | Reservation lifecycle tests rely too heavily on direct SQL seeding rather than canonical runtime commands. | RESOLVED_CODE / EXECUTION_PENDING — runtime lifecycle regression 7c3e6d2a |
| G-340 | P1 | Reservation concurrency is not fully verified through the real runtime path. | RESOLVED_CODE / EXECUTION_PENDING — ReservationService dbb01751→dbf9f0a1; concurrency 536f6e7a |
| G-341 | P1 | Reservation idempotency is not DB-enforced end-to-end. | RESOLVED_CODE / EXECUTION_PENDING — migration 056 a3b976a4; service dbf9f0a1; concurrency 536f6e7a |
| G-342 | P1 | Reservation and inventory reserved_quantity reconciliation invariant is incomplete. | RESOLVED_CODE / EXECUTION_PENDING — migration 057 43380c08; concurrency ecb42e20 |
| G-343 | P1 | Reservation lifecycle needs an independent durable event/audit record rather than inference only. | RESOLVED_CODE / EXECUTION_PENDING — 24b27330/af98846c/7dde8adf/fa4d1a82 + regressions 3db5ebc5/1474189e/38c10528 |
| G-179..G-195 | P1/P2 | Earlier Return/RMA and Audit/Event deep-audit findings covering return client contract, cumulative ceilings, refund evidence/approval, replay/idempotency, dispute-outbox routing, audit/event envelope, sequence/lineage, poison-event isolation and read-only Ops behavior. | OPEN |

## B. Later audit ranges previously found but not atomically recovered into the canonical repo register

| IDs | Domain / finding family | Status |
|---|---|---|
| G-235..G-239 | Daily Inventory lifecycle, runtime/reconciliation, tenant scoping and evidence gaps. | OPEN |
| G-240..G-246 | Order-item quantity invariants, reconciliation, partial/zero/negative quantity enforcement and runtime evidence. | OPEN |
| G-247..G-255 | Unit normalization/conversion, pack/unit arithmetic, allocation quantity semantics and cross-layer unit consistency. | OPEN |
| G-256..G-265 | Price×quantity arithmetic, MOQ, discounts, line/subtotal/group totals, rounding, currency precision, authoritative calculation and reconciliation. | OPEN |
| G-266..G-274 | Checkout/group integrity, atomicity, partial acceptance, orphan states, rollback/failure and runtime evidence. | OPEN |
| G-284..G-307 | Blocks 36–39 findings: deep lifecycle/contract/concurrency/evidence defects identified before the temporal block. Exact atomic titles remain to be reconstructed from the audit transcript before implementation. | OPEN / RECOVERY REQUIRED |
| G-321..G-324 | Blocks 43+ findings covering data/notification/consent/preferences/inbox/retention/export lifecycle. Exact atomic titles require transcript reconstruction before implementation. | OPEN / RECOVERY REQUIRED |
| G-344..G-407 | Blocks 47–56 findings spanning subsequent domain, security, reconciliation, dispute/RMA and cross-module deep-audit checks. Exact atomic titles require transcript reconstruction before implementation; IDs are intentionally retained and not considered closed. | OPEN / RECOVERY REQUIRED |
| G-440..G-451 | Delivery/POD findings after G-439: ARRIVED runtime, duplicate/concurrent POD, delivered_quantity, OTP lifecycle/event/routing, proof validation/provenance, FAILED semantics and endpoint parity. | OPEN |
| G-452..G-465 | Payment/Settlement/Reconciliation findings: checkout→payment integration, direct-transfer path, reconciliation bypass, amount invariants, events, settlement/invoice projection, payment attempts/status vocabulary, multi-payment selection, idempotency and Payment Evidence→Media linkage. | PARTIALLY RESOLVED 2026-09-26 — see Stage-12 record; checkout→payment and reconciliation case-feed remain OPEN with root causes registered |

## C. Explicit latest Return/Dispute/Refund findings recovered from the audit transcript

| ID | Severity | Finding | Status |
|---|---:|---|---|
| G-408 | P1 | Canonical Dispute→Refund path does not exist as a direct runtime flow; current refund creation is RMA-driven. | OPEN |
| G-409 | P1 | Canonical Finance Refund HTTP APIs are missing; runtime exposes only RMA transition endpoints. | OPEN |
| G-410 | P1 | Completing a refund does not transition the linked payment to REFUNDED. | OPEN |
| G-411 | P1 | Refund amount has no complete financial ceiling against paid/disputed/eligible/returned value. | OPEN |
| G-412 | P1 | Refund does not atomically reconcile with Settlement Adjustment. | OPEN |
| G-413 | P1 | Canonical refund state machine differs from the RMA-driven runtime state machine. | OPEN |
| G-414 | P1 | Refund-specific domain events are not emitted to the outbox. | OPEN |
| G-415 | P1 | Refund approval/completion lacks required administrative audit trail. | OPEN |
| G-416 | P2 | Two-person completion exists, but the approval/creation actor model is not unified with canonical Finance states. | OPEN |
| G-417 | P2 | Refund/payment provenance cannot reliably select the payment for multi-payment orders. | OPEN |
| G-418 | P2 | Refund schema documentation lags executable migration provenance fields. | OPEN |
| G-419 | P2 | Refund idempotency is path-specific (dispute vs return) and lacks a cross-path single-refund invariant. | OPEN |
| G-420 | P2 | RMA admission is not explicitly constrained to delivered orders. | OPEN |
| G-421 | P1 | Dispute-create request contract does not fully match the canonical claim/evidence requirements. | RESOLVED — see dispute-chain closure record (2026-09-26) |
| G-422 | P1 | Dispute admission does not enforce DELIVERED + four-hour eligibility. | RESOLVED — see dispute-chain closure record (2026-09-26) |
| G-423 | P1 | `evidence_media_id` is optional at runtime although canonical dispute admission requires evidence. | RESOLVED — see dispute-chain closure record (2026-09-26) |
| G-424 | P1 | No item-level dispute scope (`dispute_items`, quantities, item amount/reason). | RESOLVED — see dispute-chain closure record (2026-09-26) |
| G-425 | P1 | `approved_amount_toman` has no invariant bounding it to the claim. | RESOLVED — see dispute-chain closure record (2026-09-26) |
| G-426 | P1 | Resolution outcome has no enforced relationship to approved/refunded amount. | RESOLVED — see dispute-chain closure record (2026-09-26) |
| G-427 | P1 | Dispute resolution lifecycle OPEN→INVESTIGATING→RESOLVED→CLOSED is absent from runtime. | RESOLVED — see dispute-chain closure record (2026-09-26) |
| G-428 | P1 | Canonical `PATCH /api/v1/disputes/{id}/resolve` is absent. | RESOLVED — see dispute-chain closure record (2026-09-26) |
| G-429 | P1 | Open Dispute can attach to an inappropriate settlement status; active-settlement selection is not state-aware. | RESOLVED — see dispute-chain closure record (2026-09-26) |
| G-430 | P1 | Dispute-open and settlement close/payout have a concurrency race; settlement is not locked/state-conditioned atomically. | RESOLVED — see dispute-chain closure record (2026-09-26) |
| G-431 | P1 | `orders.dispute_status` projection cannot be maintained across the full dispute lifecycle. | RESOLVED — see dispute-chain closure record (2026-09-26) |
| G-432 | P1 | Dispute-open event payload carries incorrect/insufficient aggregate and amount data. | RESOLVED — see dispute-chain closure record (2026-09-26) |
| G-433 | P1 | Runtime and canonical dispute event naming are inconsistent. | RESOLVED — see dispute-chain closure record (2026-09-26) |
| G-434 | P2 | Dispute lacks an independent immutable transition-history stream. | RESOLVED — see dispute-chain closure record (2026-09-26) |
| G-435 | P2 | Ops assignment/investigation is modeled in DB but lacks the corresponding runtime command. | RESOLVED — see dispute-chain closure record (2026-09-26) |
| G-436 | P2 | Dispute evidence ownership/provenance is not enforced at admission. | RESOLVED — see dispute-chain closure record (2026-09-26) |
| G-437 | P2 | Dispute creation lacks true HTTP idempotency/fingerprint replay semantics. | RESOLVED — see dispute-chain closure record (2026-09-26) |
| G-438 | P1 | Delivery OTP is not actually mandatory for the DISPATCHED→DELIVERED transition. | RESOLVED — see closure record below (2026-09-26) |
| G-439 | P1 | Delivery OTP is returned to the vendor caller, exposing a secret that should remain with the delivery recipient/proof flow. | RESOLVED — see closure record below (2026-09-26) |


### G-438 / G-439 Closure Record — 2026-09-26
- **Finding re-verified:** the interrupted remediation line had already removed `delivery_otp` from the vendor dispatch response (G-439 source) and implemented mandatory OTP confirmation (ARRIVED gate, recipient name, single-use consumption, expiry) — but (a) the recipient channel was missing entirely (the DELIVERY_OTP_GENERATED event payload and template carried no code, so no actor could ever complete delivery), and (b) the 5-attempt cap lived in the per-request transaction and was rolled back on every rejection, so brute-force protection never engaged. Stale tests still asserted the leaked-OTP contract.
- **Resolution (this branch):**
  1. Recipient channel: `DELIVERY_OTP_GENERATED` outbox payload now carries `delivery_otp`; template version 1.1 (migration 071) renders it into the targeted retailer inbox (INBOX channel, ops untouched, vendor response stays clean).
  2. Durable attempt accounting: new `delivery_otp_attempts` table (migration 071); `POLApplicationBoundary.retailer_confirm_delivery` records each verification attempt in an **independent transaction** before the confirmation transaction starts (guarded: not consumed, not expired); cap 5 per the delivery-specific OTP attempt policy (separate from D-018 login attempts); `deliveries.delivery_otp_attempt_count` superseded (kept for historical rows; 068 CHECK retained).
  3. Corruption repair on this path: `list_delivery_exceptions` security pre-check SQL had duplicated/joined fragments (unparseable) — rebuilt.
  4. Tests updated to the canonical contract: vendor dispatch response must NOT contain `delivery_otp`; tests fetch the OTP from the recipient outbox channel; POD photo media must be READY and pre-bound to the DELIVERY target (G-319/G-054 model); escalation fan-out asserted against the seeded ops org.
- **Files changed:** `scripts/fulfillment_service.py`, `scripts/application_boundary.py`, `scripts/delivery_exceptions.py`, `migrations/071_delivery_otp_recipient_channel.sql`, `scripts/test_http_fulfillment.py`, `scripts/test_http_proof_of_delivery.py`, `scripts/test_http_delivery_exceptions.py`.
- **Test evidence:** `test_http_fulfillment.py` 15/15; `test_http_proof_of_delivery.py` incl. `TestOTPAttemptCap::test_otp_attempt_limit` (5 wrong attempts then correct OTP → 422 attempt-limit); `test_http_delivery_exceptions.py` 12/12; delivery tracking/exceptions/proof cluster 49 passed / 0 failed.
- **Commits:** `792980c` (fix(gap): complete G-438/G-439 delivery OTP remediation).
- **Verification state:** SOURCE PATCH + REGRESSION + LOCAL RUNTIME EVIDENCE on branch `remediation/master-gap-closure-2026-09-26`; fresh CI execution pending (remote push intentionally deferred).

### Phase-0 record — branch state on adoption (2026-09-26)
- Adopted `origin/remediation/full-closure-2026-09-25` (826 commits ahead of origin/main) as the working line: `remediation/master-gap-closure-2026-09-26`.
- The tip carried committed corruption from the interrupted run (45 collection errors; "fresh CI blocked" note in this ledger): spliced `from __future__` import in `fulfillment_service.py`, orphan `)` in `delivery_exceptions.py`/`refund_service.py`, stray backslash-n lines in `test_delegated_permissions.py`, parametrize decorators attached to wrong tests in `test_batch3_contract_matrix.py`/`test_e2e_mvp_platform.py`, and migration 062 referencing a nonexistent `disputes.created_at`. All repaired (`3e0b2bc`, `971e07e`).
- pol_test schema was behind the migration chain (060–071); applied locally. 062 required the index fix above before it could apply anywhere.
- Suite trajectory on this line: 430/637 (2026-09-26 baseline after corruption repair) → **544/637** after Block 58 closure + schema sync. Remaining 93 failures concentrate in the still-OPEN Block 56/57 chains (refund/RMA/dispute/payment), e2e platform, concurrency and worker clusters — these are the next remediation units, each requiring the READ→ROOT-CAUSE→PATCH→TEST cycle; none may be closed by test-editing alone.


### Dispute chain closure record — G-421..G-437 (2026-09-26)
- **Revalidation:** the interrupted remediation had wired the full HTTP/boundary
  layer (`POST /orders/{id}/disputes`, `POST /disputes/{id}/investigate`,
  `PATCH /disputes/{id}/resolve`, `POST /disputes/{id}/close`) and DB schema
  (dispute_items, dispute_events append-only, idempotency columns, migration 062
  adjudication invariants) but the domain implementation was never committed:
  `DisputeService.open_dispute_v2/investigate_dispute/resolve_canonical/
  close_canonical` were referenced by `canonical_dispute.py` and did not exist,
  so every dispute creation 500'd. Additionally the boundary passed
  `str(None)` ("None") as the idempotency key for key-less requests, and
  `orders.dispute_status_check` did not carry the canonical INVESTIGATING/RESOLVED
  vocabulary.
- **Resolution:** canonical domain chain implemented in `DisputeService`:
  admission (DELIVERED gate, 4h filing window per operational_config, mandatory
  READY/owner/order-bound evidence re-bound to DISPUTE on admission, item-level
  scope validated against order items, key+fingerprint idempotency with
  mismatch-422 and cross-key same-payload replay, state-aware settlement attach
  under FOR UPDATE with status-conditioned update and CLOSED rejection),
  investigation (OPEN->INVESTIGATING with ops assignment), resolution
  (INVESTIGATING-only, outcome/amount invariants mirroring 062, settlement
  SHORTAGE_DEDUCTION adjustment, replay-safe), close (RESOLVED->CLOSED with
  pre-checked refund-total invariant as 422). Every transition writes the
  append-only dispute_events stream and the orders dispute_status projection
  (migration 072 widens the projection vocabulary). Outbox is limited to the two
  templated canonical events (DISPUTE_OPENED -> vendor org, DISPUTE_RESOLVED ->
  both parties).
- **Files changed:** `scripts/domain_services.py`, `scripts/application_boundary.py`,
  `migrations/072_orders_dispute_status_projection.sql`.
- **Test evidence:** `scripts/test_http_returns_disputes.py` 18/18 (open/tenant
  query/list, expired window 422, evidence-required, staff-overreach 403,
  investigate/resolve/reconcile with settlement_adjustments row
  SHORTAGE_DEDUCTION + applied_by audit, idempotent resolution
  (second call same result, single adjustment), non-ops resolve 403,
  resolution-cannot-exceed-claim 422).
- **Verification state:** SOURCE PATCH + REGRESSION + HTTP EVIDENCE on
  `remediation/master-gap-closure-2026-09-26`; concurrency evidence is
  code-level (row locks + status-conditioned updates); dedicated concurrent
  dispute race test remains a follow-up evidence item.
- **OPEN_DECISION carried:** MUTUAL_AGREEMENT award has no settlement
  adjustment mapping in the canonical docs (adjustment_type enum has no
  matching semantic); implemented as award-without-adjustment pending an
  explicit settlement-mapping decision.


### Stage 11 closure record — Delivery/POD G-440..G-451 (2026-09-26)
- **Failure inventory mapping (11 test_http_vendor_order failures):** root cause
  was test-harness staleness, not runtime defects — the vendor order routes
  evaluate the delegated-permission dependency (require_permission("order.accept"))
  which the transport-contract tests did not override; the DB-backed permission
  query received the harness's synthetic ids. Harness modernized (grants
  check_permission), routes verified contract-correct 16/16 → evidence for G-449.
  Separately, `scripts/api/routes/admin.py` used `Annotated[...]` annotations
  without importing `Annotated`, so any OpenAPI generation after a plain module
  import failed with pydantic's incomplete-TypeAdapter error (this was the
  long-standing `test_api_boundary_route_inventory` failure) — import added;
  the static route-inventory registry was regenerated to the current canonical
  surface (155 business + 2 ops routes).
- **G-440 ARRIVED runtime: RESOLVED (verified).** DISPATCHED→PICKED_UP→IN_TRANSIT→
  ARRIVED→DELIVERED executes end-to-end over HTTP: legality map enforced
  (ASSIGNED→ARRIVED jump → 422), vendor/field actor authorization, stage
  timestamps persisted (picked_up_at/in_transit_at/arrived_at), delivery_timeline_events
  rows, DELIVERY_* outbox events to the retailer org, same-state idempotent
  replay, order-status DISPATCHED guard. Evidence: TestG440ArrivedRuntime 4/4.
- **G-441 duplicate/concurrent POD: RESOLVED (verified).** Two simultaneous HTTP
  confirmations (ThreadPoolExecutor, real TestClients): exactly one terminal
  mutation — one POD row, one DELIVERED delivery, OTP consumed once; the second
  request is either a deterministic 200 replay (idempotent_replay) or a 422.
  Evidence: TestG441ConcurrentPod (DB assertions included).
- **G-442 delivered_quantity: RESOLVED (verified).** 0 <= delivered <= ordered,
  delivered <= accepted enforced; missing payload defaults to accepted_quantity;
  partial → SHORTAGE, zero → REJECTED, full → FULFILLED (projection derived from
  real quantities); unknown order_item_id → 422; duplicate payload entry → 422
  (source fix in confirm_delivery). DB backstop: migration 068 CHECKs.
  Evidence: TestG442DeliveredQuantity 7/7.
- **G-443/G-444 OTP lifecycle + routing: RESOLVED (verified in Stage-10/Block-58
  closure, commit 792980c).** generated → recipient-only channel (retailer org
  inbox via DELIVERY_OTP_GENERATED v1.1 template; vendor response and payload
  never carry it) → attempted (durable delivery_otp_attempts, rollback-proof) →
  consumed once (atomic used_at) → expired/locked. No evidence to reopen.
- **G-445/G-446 proof validation/provenance: RESOLVED (verified).** PHOTO_PROOF
  requires READY media owned by the reporter and pre-bound to the exact DELIVERY
  target (unbound/foreign media → 422); non-media proof types
  (PHYSICAL_SIGNATURE/STORE_STAMP/OTP_CODE) accepted per contract without media.
  Evidence: TestG445G446ProofValidation 2/2 + test_http_proof_of_delivery.py.
- **G-447 FAILED semantics: RESOLVED (runtime semantics documented; canonical
  doc gap noted).** FAILED is legal only from IN_TRANSIT/ARRIVED (ASSIGNED → 422),
  requires the delivery to remain order-DISPATCHED, persists failed_reason +
  failed_at, writes a FAILED timeline row + DELIVERY_FAILED outbox event, is
  idempotent on duplicate (replay), and never implies order DELIVERED — a
  post-FAILED delivery confirmation is rejected (422) because confirmation
  requires ARRIVED. Note: Order_Lifecycle.md defines the FAILED state but no
  post-FAILED transition narrative; the runtime behavior is recorded here as
  the implementation contract. Evidence: TestG447FailedSemantics 4/4.
- **G-448 state-machine consistency: RESOLVED (reconciled).** API routes
  (picked-up/in-transit/arrived/failed/deliver) ↔ runtime legality map ↔ DB
  CHECK vocabulary (ASSIGNED, PICKED_UP, IN_TRANSIT, ARRIVED, DELIVERED, FAILED)
  are one-to-one; per-stage timestamp columns align with the runtime map.
- **G-449 endpoint parity: RESOLVED (verified).** Every Delivery/POD contract
  endpoint verified route→schema→boundary→service→DB; the route-inventory gate
  (155 routes) is green against the live app.
- **G-450 POD persistence/replay: RESOLVED (verified).** Successful confirmation
  creates exactly one POD row and one terminal delivery state; identical retry
  replays (idempotent_replay=true) without a second POD.
- **G-451 evidence/audit/event consistency: RESOLVED (verified).** After the
  terminal transition the order row (DELIVERED), delivery row, single POD,
  ORDER_DELIVERED outbox events (per recipient org) and the terminal
  order_timeline_events row all reference the same state.
- **Files changed:** `scripts/test_http_vendor_order.py` (harness),
  `scripts/api/routes/admin.py` (missing import),
  `scripts/test_api_boundary_route_inventory.py` (registry + reuse production app),
  `scripts/fulfillment_service.py` (duplicate delivered_items rejection),
  `scripts/test_http_delivery_pod_g440_451.py` (new, 19 cases).
- **Verification state:** SOURCE PATCH + REGRESSION + HTTP EVIDENCE + CONCURRENCY
  EVIDENCE (HTTP-level) on `remediation/master-gap-closure-2026-09-26`.


### Stage 12 closure record — Payment/Settlement/Reconciliation G-452..G-465 (2026-09-26)
Parallel diagnosis (failure inventory: 11 finance + 4 batch2 RMA + 2 cross_entity + 1 payment_evidence) produced per-failure root causes; remediation results:

**REVALIDATED_RESOLVED (source verified with file:line evidence; tests green):**
- Direct-transfer path: `POST /orders/{id}/payments/evidence` + `/payments/direct-transfer` + `/payments/verify` fully implemented with tenant/owner provenance (active membership EXISTS subqueries), amount bounds (<=0 rejected; >payment amount rejected), READY media bound to ORDER/PAYMENT targets (064/065/066 DB triggers), external_reference idempotency incl. cross-payment reuse rejection.
- Settlement/invoice projection: invoices org-scoped (retailer_organization_id/vendor_organization_id; ops cross-tenant read-only), settlements vendor-only via vendors.organization_id join; detail access re-checks ownership.
- Payment status vocabulary: single canonical CHECK set (PENDING/INITIATED/SUCCESS/FAILED/CANCELLED/REFUNDED) used consistently; `payment_attempts` table is schema-only (no runtime writer) — noted.
- Payment Evidence→Media linkage: code + DB triggers enforce READY+owner+ORDER/PAYMENT binding.

**RESOLVED this stage (source fixes with regression evidence):**
- Idempotency (payment creation): migration 073 adds payments.idempotency_key/idempotency_fingerprint + partial unique index (mirrors refunds/checkout model).
- Events: PAYMENT_VERIFIED had no notification template (orphaned outbox contract) — template v1.0 added by migration 073; refund chain events (CREATED/APPROVED/COMPLETED/PAYMENT_REFUNDED) verified as real DB rows by batch2 tests.
- Multi-payment selection asymmetry: verify_payment without payment_id silently picked the latest record; now requires explicit payment_id when an order has multiple payment records (mirrors the evidence-side guard).
- RMA/Refund chain (batch2, 4 failures → root-cause chain fixed in scripts/returns_rma.py): (1) REFUND_PENDING→REFUND_PENDING idempotent replay added (ops-gated; linked refund materialization is ON CONFLICT DO NOTHING); (2) `_complete_refund` used an unassigned `fully_refunded` variable (UnboundLocalError — a regression from commit 24deed2) and never marked payments REFUNDED; restored the completed-sum computation + state-conditioned `payments.payment_status='REFUNDED'` (mirrors refund_service.py); (3) `approve_refund` locked a nullable LEFT JOIN side (FOR UPDATE → FeatureNotSupported); now `FOR UPDATE OF r`; (4) audit inserts used an unimported `Json(...)` (NameError); now `json.dumps(...)`. Test-side: event filter excluded REFUND_APPROVED and the expectation omitted the legitimate REFUND_CREATED event — corrected.

**TEST-stale repairs (source correct):** test_http_finance `_seed_finance` violated the migration-068 fulfillment-consistency constraint (11 failures); test_cross_entity expectations updated to the newer canonical guards (067 `REFUND_PAYMENT_PROVENANCE_MISMATCH`, 068 CHECK constraint names); test_http_payment_evidence `_seed_order` never returned `media_id`.

**OPEN (root cause identified, next units):**
- checkout→payment integration: the contract endpoint `POST /orders/{id}/payments/direct-receipt` (matrix row 14) is not implemented; `PaymentService.record_direct_payment` exists but is unwired (test-only caller), so freshly checked-out orders have no payment row for the evidence/verify chain to operate on. Next remediation unit: wire the contract route through the boundary using the existing domain service + 073 idempotency columns.
- Reconciliation: matching worker is conflict-safe and state-conditioned, but (a) no runtime feed creates `payment_reconciliation_cases` (only fixtures) and (b) the "trusted" evidence types are actor self-attestations — true bank/POS confirmation requires an external integration decision (OPEN_DECISION/BLOCKED_EXTERNAL).

**Files changed:** scripts/returns_rma.py, scripts/application_boundary.py, migrations/073_payment_idempotency_and_verified_template.sql, test_http_finance.py, test_cross_entity_integrity_032.py, test_http_payment_evidence.py, test_batch2_rma_and_outbox.py.
**Verification state:** SOURCE PATCH + REGRESSION + HTTP/DB EVIDENCE on remediation/master-gap-closure-2026-09-26; 17/17 in-scope failures green (finance 11, batch2 4, cross_entity 2, payment_evidence 1... plus cross_entity full file green).


### Stage 13 record — E2E/Concurrency/Inventory/Management/Auth/Media/Migrations (2026-09-26, INTERIM)
**Suite trajectory on this branch:** 430/637 (baseline) → 544 → 551 → 600/656 → **647/656** (HEAD 1b810b8).

**REAL SOURCE DEFECTS FIXED (classification A/B — not test debt):**
1. privacy_lifecycle: raw dicts to psycopg2 jsonb (export + deletion paths); export profile SELECT lacked user_id.
2. catalog_barcode_match: SELECT DISTINCT/ORDER BY mismatch (all barcode lookups 500'd); candidate upsert locked nullable join side; product_candidate_created outbox targeted vendor_id as target_user_id (FK violation).
3. canonical_basket_allocation: two SELECTs omitted pack_quantity (allocation preview + basket items path); allocation_preview was structurally broken.
4. application_boundary: vendor_inventory_continuous_scan wrote verification_source='CONTINUOUS_SCAN' outside the DB CHECK vocabulary (→BARCODE_SCAN); missing module datetime import; session-publish inventory_audit_log INSERT passed UUID into bigint new_price_toman and omitted old_price_toman; vendor_staff_invite returned unserializable datetime row.
5. Migration 074: three overlapping append-only guards on admin_audit_logs — the alphabetically-earlier v032 trigger shadowed the dedicated 049 guard (dead code); consolidated.
6. Earlier in Stage 13 scope: RMA chain fixes (returns_rma.py: replay, fully_refunded, locks, Json) and migration 073 payments idempotency + PAYMENT_VERIFIED template.

**TEST DEBT REPAIRED (classification G/H, source verified canonical):** 40+ test fixes across e2e platform, concurrency (reservation-sync under migration 057, dispute evidence under 058), inventory seed, policies messages, migrations assertions, auth contract (phone binding, session-context trigger, rate limit), media/support/management/field_tasks/delegated/timeout/broadcasts/transport/master_e2e/vendor_referral.

**REMAINING 9 FAILURES — root causes registered (NOT swept):**
- 2 cross_entity (test_append_only_admin_audit, test_migration_032_triggers): require POL_E2E_PG_DSN env — pass with it (environment, I).
- 2 e2e reservation tests: fixture basket lacks an orderable vendor (MOV/inventory setup) — test scenario setup incomplete (H, IN PROGRESS).
- 1 inventory_reservations + 1 master_e2e: same env/reservation-sync family (G/H, IN PROGRESS).
- 3 management (scan publish, candidate review, permission editor): scan chain still failing past the vocabulary fix — root cause chain under investigation (IN PROGRESS).

**OPEN DECISIONS / BLOCKED (unchanged):** checkout→payment direct-receipt route (root cause registered Stage 12); reconciliation case-feed + external confirmation trust model (BLOCKED_EXTERNAL); refresh-token rotation (D-018 undecided); MUTUAL_AGREEMENT settlement mapping.

## D. Recovery-control rule for G-321..G-407

The numbered IDs are deliberately retained as OPEN rather than silently dropped because the user required every prior finding to remain traceable. Before implementing any such item, its exact original audit wording must be recovered from the audit transcript/source artifact. No guessed implementation is permitted.

## E. Completion protocol

For every item:
1. source fix;
2. regression test / runtime evidence;
3. update this ledger immediately;
4. record fix commit SHA;
5. reconcile `BUILD_PLAN.md`, API/screen matrices and current source-of-truth docs;
6. only then change status from OPEN to RESOLVED.

At the end of each closed item, the ledger must contain:
- **Resolution**
- **Files changed**
- **Test evidence**
- **Commit**
- **Verification state**


### G-308 Closure Record
- **Resolution:** Operating-window lookup now evaluates active windows using each row's own timezone and derives the business weekday from that timezone before applying the window.
- **Files changed:** `scripts/operational_policies.py`, `scripts/test_e2e_mvp_platform.py`
- **Regression:** `test_operating_window_uses_its_own_timezone_for_weekday`
- **Source commit:** `a468372131a738b503e9167a52fbb5e2485f2125`
- **Test commit:** `4fc8804e2e13aec0669726c215d9e4beddd446c4`
- **Verification state:** SOURCE PATCH + REGRESSION ADDED; fresh CI execution remains separately pending.

### G-309 Closure Record
- **Resolution:** overnight windows now map post-midnight times to the previous local business weekday before selecting the window.
- **Regression:** `test_overnight_window_uses_previous_weekday_after_midnight`
- **Test commit:** `e64ea3bdade1c14b57b6134740d19e94eb731f0f`
- **Verification state:** SOURCE LOGIC + REGRESSION ADDED; fresh CI remains separate.

### G-310 Closure Record
- **Resolution:** cutoff is now evaluated as a timezone-aware local instant; overnight windows place a cutoff earlier than the opening time on the following business day.
- **Regression:** `test_overnight_order_cutoff_uses_next_day_semantics` verifies Wednesday 23:00 is allowed and Thursday 01:30 is rejected for a Wednesday 22:00→02:00 window with a 01:00 cutoff.
- **Source commit:** `ad8b827eab465c2d337368f3219ad31bb1da4fa5`
- **Regression commit:** `570a645286823e469d0a527888d20dc58da2fed9`
- **Verification state:** SOURCE FIX + REGRESSION PERSISTED; fresh CI remains separate.

### G-311 Closure Record
- **Resolution:** each vendor capacity decision now acquires a transaction-scoped PostgreSQL advisory lock before reading the capacity counters; vendor IDs are processed in sorted order to avoid multi-vendor lock-order deadlocks. The lock is held through the canonical checkout transaction, so capacity validation and subsequent order insertion cannot race for the same vendor.
- **Regression:** `test_vendor_capacity_lock_serializes_concurrent_checkout_decisions` proves the second transaction cannot enter the capacity check while the first transaction holds the vendor capacity lock, then observes the committed order and rejects the second decision at capacity 1.
- **Source commit:** `4f6f8ae64408669d92d6abd2fbf44e7e144f26c0`
- **Regression commit:** `59f83384ebf8122b4729c8c56aa1932e832d3ab9`
- **Verification state:** SOURCE FIX + CONCURRENCY REGRESSION PERSISTED; fresh CI remains separately blocked.

### G-312 Closure Record
- **Resolution:** migration `049_admin_audit_immutability.sql` installs a PostgreSQL trigger that rejects UPDATE and DELETE on `admin_audit_logs`, making the audit trail append-only at the database boundary.
- **Regression:** `test_admin_audit_logs_are_db_immutable` proves INSERT succeeds, UPDATE is rejected, DELETE is rejected, and the original row remains intact.
- **Migration commit:** `6dd3791e78224c6e8f14582a529a894a649c1d06`
- **Regression commit:** `03979c4c096fcec695d8cfbb1e972f68c3040cc9`
- **Verification state:** SOURCE + DATABASE CONSTRAINT + REGRESSION PERSISTED; fresh CI remains separate.

### G-313 Closure Record
- **Resolution:** `inventory_audit_log.vendor_product_id` now uses `ON DELETE RESTRICT` in migration `050_inventory_audit_history_restrict.sql`, so a referenced Vendor Product cannot be physically deleted while audit history exists.
- **Regression:** `test_inventory_audit_history_blocks_vendor_product_delete` inserts a real audit row, attempts deletion, and verifies both the history row and Vendor Product remain.
- **Migration commit:** `4a87a750f0ee80d9d31589ffe1d480fcbe3814df`
- **Regression commit:** `b3008be1e847085bddd5ede3222f1f8d0558285f`
- **Verification state:** SOURCE + DB FK + REGRESSION PERSISTED; fresh CI remains separate.

### G-314 Closure Record
- **Resolution:** migration `051_notification_retention_defaults.sql` backfills missing inbox expiry values and installs a write-time trigger: 30 days for `PROMOTIONS`, 90 days for transactional/system categories. `notification_retention_worker.py` archives expired, non-archived inbox rows in bounded batches using `FOR UPDATE SKIP LOCKED`.
- **Regression:** `test_notifications.py::test_notifications` now verifies write-time expiry and invokes the archive worker after forcing an expiry into the past.
- **Migration commit:** `d209963c05d002df14cc0776ba04ac0bd7485c9b`
- **Worker commit:** `63adf6d11911afebfc6fa0daf67b491250350a73`
- **Regression commit:** `061c7d883c37b63f9ba89beb7d890bb0f5e88886`
- **Verification state:** SOURCE + DB RETENTION RULE + WORKER + REGRESSION PERSISTED; fresh CI remains separate.

### G-315 Closure Record
- **Resolution:** added canonical `privacy_requests` lifecycle, authenticated export endpoint and authenticated account-deletion endpoint. Export returns a user-scoped versioned snapshot and persists only its SHA-256; deletion revokes sessions/devices/active consents and de-identifies direct identity/profile data while preserving business/financial/audit referential integrity.
- **HTTP:** `POST /api/v1/privacy/export`, `POST /api/v1/privacy/deletion`; registered in FastAPI route inventory and canonical API map/contract.
- **Regression:** `test_privacy_export_and_deletion_lifecycle` covers export scoping, checksum presence, de-identification, session/device/consent revocation, and persistence of membership/history.
- **Migration commit:** `1603218e6be3b84c30cd53736e3e06c58e43fc5b`
- **Service commit:** `c8d0122718003d8c184ed9c6d0001207f67451cf`
- **HTTP route commit:** `a74da82a84864bb491f1764bf1d53e5d7a297f36`
- **Boundary commit:** `58880d1f392de8710c57a9868362f2eccde369e1`
- **Schema commit:** `0c34f4ce66189976bc2a066faca05ea7103cfdec`
- **Route registry commit:** `7ee4959676a73b2a88330008cbf56b8971f84bba`
- **API map commit:** `b2830f7a16dfa2374cefad6d5c23a14d9817ca59`
- **API contract commit:** `df6b40d86e3a95dab5bdec381e3d5afdb7f4b86f`
- **Regression commit:** `1fbf3511d4656422de304eb14d7a8bccc761ef69`
- **Verification state:** SOURCE + DB LIFECYCLE + HTTP ROUTES + REGRESSION PERSISTED; fresh CI still pending.

### G-316 Closure Record
- **Resolution:** migration `053_canonical_media_schema_alignment.sql` adds canonical `bucket_name/object_key` aliases, product-media governance fields (`media_type`, `source_provenance`, `approval_status`, approver/timestamp), checksum format validation, and changes product-media media FK to `ON DELETE RESTRICT`. `MediaService` now writes the canonical governance fields and synchronizes storage aliases.
- **Regression:** `test_media_schema_alignment_and_governance_fields` verifies alias synchronization, nullable checksum while UPLOADING, and product-media governance fields at the PostgreSQL boundary.
- **Migration commit:** `6fa46ec8b4f627c34a176fb0a32d2d7179ee5b92`
- **Service commit:** `3ff27c8f6b5327a111cd639163954a2a6026e10b`
- **Regression commit:** `f5f5b0dff798da9770ec796a2f4fa6eaec15a1ad`
- **Schema-doc commit:** `bd5d5261c2a85ade28848ac33e99ed80beb49d97`
- **Verification state:** SOURCE + DB SCHEMA + SERVICE + REGRESSION PERSISTED; fresh CI/local execution remains pending due current network/CI constraints.

### G-317 Closure Record
- **Resolution:** canonical product-detail media now requires `READY` asset status, public provenance (`VENDOR_UPLOADED`, `MANUFACTURER_PROVIDED`, `POL_OWNED`) and `product_media.approval_status = 'APPROVED'`; `PRIVATE_REFERENCE` is explicitly excluded.
- **Source commit:** `e1991dd58f318b44f9c4bfb4dbd749e88eacbce0`
- **Regression commit:** `31f2c994b466f8c1982b02749d38357c91561cad`
- **Verification state:** SOURCE + PUBLIC-READ GATE + REGRESSION PERSISTED; fresh runtime/CI execution remains pending.

### G-318 Closure Record
- **Resolution:** resumable S3-compatible multipart sessions/parts are persisted, presigned part URLs are issued, multipart completion is validated for contiguous unique parts, and trusted processing now performs magic-byte/decode validation, explicit metadata/EXIF stripping, WebP conversion, SHA-256 calculation and 150×150 WebP thumbnail generation in `media_variants`.
- **HTTP:** `POST /api/v1/media/resumable/init` and `POST /api/v1/media/resumable/complete` are registered in the FastAPI route inventory and canonical API map/contract.
- **Regression:** `test_resumable_media_session_and_processing_pipeline` uses a fake S3 provider to exercise multipart session creation, completion, final processing and thumbnail persistence. Live S3/MinIO evidence cannot be certified in this environment without provider execution.
- **Migration commit:** `b6cb7877ab86200d16b3c3a613fd6c03da5ca4e2`
- **Service commits:** `53180faf2f2ddfad599ea34010b52e902bcd74f1`, `3af490e5bb916dbd78d4cee520d3728e98f36e32`, `6ccc1618d9a0b341f6395d4569cd2d3de184a063`
- **API route commit:** `2564d61a37749a93c1634ac5b8f64c1154758a80`
- **Route inventory:** `d44638a30bc2fe38457a6d78648cf2a5925b0aad`
- **API map:** `6087dae3e96261d16ec07fbb3457f2aca10b55b7`
- **API contract:** `4c60fbe40065169d936552f2b4e35d4a7bbc04cd`
- **Regression commits:** `408639c57feae3a747a46fc2d3c128b81121e230`, `6ccc1618d9a0b341f6395d4569cd2d3de184a063`
- **Verification state:** code and fake-provider regression persisted; live S3/MinIO runtime evidence + fresh CI remain pending.

### G-319 Closure Record
- **Resolution:** shared `validate_ready_attachment` now enforces READY lifecycle, exact uploader ownership, active organization context, exact `upload_target_type` purpose and exact `upload_target_id`. Dispute admission and POD confirmation both call the same validator before attaching evidence/proof.
- **Source commits:** `b7c4e56aaa17c33bc7b75a6256e8731d88a709a2`, `7c078b5f8b5204a04a2bcf288b434aed6f8c83c7`, `891778b17aeeb7033a9367c22c95c24e3c2017e2`
- **Regression:** `test_media_reference_requires_ready_owner_and_exact_purpose` verifies valid attachment plus wrong-purpose and wrong-target rejection.
- **Regression commit:** `a0a5d55ba31299a7f6de0731da18ed63e1079423`
- **Verification state:** SOURCE + SHARED VALIDATOR + DISPUTE/POD INTEGRATION + REGRESSION PERSISTED; fresh CI/runtime remains pending.

### G-320 Closure Record
- **Resolution:** migration `055_media_storage_reconciliation.sql` adds explicit storage-deletion timestamps, attempt counters and last errors for media assets and variants. `media_storage_reconcile_worker.py` claims DELETED assets with `SKIP LOCKED`, deletes source/variant provider objects first, and only then records successful reconciliation; failures retain retryable state/error.
- **Regression:** `test_deleted_media_storage_reconciliation_is_retryable` verifies provider deletion calls and post-success markers.
- **Migration commit:** `2b7c4d6e0c67d94e092cdb5e39637e6cbde7bfb5`
- **Worker commits:** `f9bbfeb2f9cc57e076432187d90f052f1f05b864`, `47656dc4f869536e8c9732f594fde950175a46e7`
- **Regression commit:** `fd611fe54a12043b6b3b846bb527b134bf13250a`
- **Verification state:** code + fake-provider regression persisted; live S3/MinIO execution remains pending.

### G-325 Closure Record
- **Resolution:** canonical checkout now serializes on the idempotency key, locks basket + allocation plan with `FOR UPDATE`, verifies current basket version equals allocation-plan basket version, and independently revalidates allocation payload against the persisted plan before creating orders/reservations. Basket mutation itself remains optimistic-version guarded.
- **Existing regression:** `test_stale_plan_version_rejected` verifies current basket v2 cannot consume a plan generated at v1; gateway/revalidation contain the same invariant in the real checkout path.
- **Verification state:** source + regression evidence persisted; fresh execution remains pending.

### G-326 Closure Record
- **Resolution:** introduced `ConflictError` as the canonical stale/competing-state transport error; FastAPI maps it to HTTP 409 with error code `CONFLICT`. Stale basket/plan validation raises `STALE_BASKET_VERSION` through this path.
- **Regression:** `test_checkout_stale_basket_returns_canonical_409` verifies the POST checkout route returns 409, `success=false`, error code `CONFLICT`, and the stale-version code in the message.
- **Source commits:** `7f11226aeba931e71dec8131258dc9bb3940c33b`, `2f221746aa0e06a09c6aa62df6827c91be496aa6`
- **Regression commit:** `af860ce59840e8ade8243384275680babce27847`
- **Verification state:** HTTP contract + exception mapping + regression persisted; fresh runtime/CI execution remains pending.

### G-327 Closure Record
- **Resolution:** canonical checkout runs inside the caller's PostgreSQL transaction; basket/allocation-plan locks, allocation validation, order-group/order-item creation, reservation creation, inventory reservation increment, plan consumption and basket finalization all occur before commit. A forced failure after the reservation stage rolls back the entire transaction.
- **Regression:** `test_checkout_is_atomic_on_failure_after_reservation_stage` now intentionally raises from event enqueue inside a real transaction and verifies zero persisted order groups/reservations, plan remains CONFIRMED, basket remains OPEN, and reserved quantity returns to zero.
- **Regression commit:** `d8e8a5aa2cb84f6604561beaf41d125acd824ec9`
- **Verification state:** source + rollback regression persisted; fresh execution/CI remains pending.

### G-328 Closure Record
- **Resolution:** retailer mobile now tracks the server basket version, receives `basket_version` from allocation preview, and handles canonical HTTP 409 conflicts by invalidating the stale allocation, fetching `/api/v1/baskets/current`, synchronizing local item quantities/IDs and retaining the server version. This prevents the UI from replaying a stale allocation after server rejection.
- **Source commits:** `753d5e5cc519cc85841f4e742308eb5131fdb9a4`, `2493c6477da5093a2d3c9f49f17b61ece713747b`
- **QA commit:** `8f1c2b60500c619a100ee71650bf74834c40fae7`
- **Verification state:** CODE + STATIC MOBILE QA GATE PERSISTED; actual device execution remains pending.

### G-329 Closure Record
- **Resolution:** evidence chain is now represented by dedicated regressions across layers: `test_stale_plan_version_rejected` at the allocation-integrity boundary, `test_checkout_is_atomic_on_failure_after_reservation_stage` across the transactional checkout path, and `test_checkout_stale_basket_returns_canonical_409` at HTTP transport.
- **Verification state:** source/test evidence persisted; fresh PostgreSQL runtime execution and CI certification remain pending. This item is not marked as a fresh-environment PASS.


### G-330 Closure Record
- **Resolution:** Total-order vendor tie-break now uses price, reputation, vendor_id and SKU id; adversarial vendor input order cannot change selection.
- **Evidence:** Test 13A in scripts/test_allocation_engine.py; commit 129644862a13550f610e6e4ef8f53b71ae9b3563
- **Verification state:** code/regression persisted; fresh CI/runtime execution remains pending.


### G-331 Closure Record
- **Resolution:** SKU-level tie selection now has a final deterministic SKU-id order for otherwise equal candidates.
- **Evidence:** Test 13B in scripts/test_allocation_engine.py; commit 129644862a13550f610e6e4ef8f53b71ae9b3563
- **Verification state:** code/regression persisted; fresh CI/runtime execution remains pending.


### G-332 Closure Record
- **Resolution:** pack_quantity is now part of VendorSKU/BasketItem semantics and candidate key, so allocation can only choose the exact commercial pack definition.
- **Evidence:** Test 13C in scripts/test_allocation_engine.py; commit 129644862a13550f610e6e4ef8f53b71ae9b3563
- **Verification state:** code/regression persisted; fresh CI/runtime execution remains pending.


### G-333 Closure Record
- **Resolution:** K>=3 remains open-ended; explicit K=3 coverage confirms no hidden two-vendor cap.
- **Evidence:** Test 13D in scripts/test_allocation_engine.py; commit 129644862a13550f610e6e4ef8f53b71ae9b3563
- **Verification state:** code/regression persisted; fresh CI/runtime execution remains pending.


### G-334 Closure Record
- **Resolution:** Allocation engine now emits a 64-char decision hash and canonical persistence fingerprints basket version/items, vendor state, SKU state, decision hash and algorithm version rather than only basket+total.
- **Evidence:** Test 13E; persistence source commit a3d0a35823331c3e263686c741223b54fdec97c4; test commit 129644862a13550f610e6e4ef8f53b71ae9b3563
- **Verification state:** code/regression persisted; fresh CI/runtime execution remains pending.


### G-335 Closure Record
- **Resolution:** Adversarial tie/pack reproducibility is covered for 100 repeated allocations with reversed SKU input order.
- **Evidence:** Test 13F in scripts/test_allocation_engine.py; commit 129644862a13550f610e6e4ef8f53b71ae9b3563
- **Verification state:** code/regression persisted; fresh CI/runtime execution remains pending.

### G-336 Closure Record
- **Resolution:** canonical `ReservationExpiryWorker.process_expired` now serves as the reservation-expiry command path; it claims due ACTIVE reservations with row locks, locks inventory, rejects reserved-quantity underflow, releases inventory, transitions reservation to EXPIRED, writes inventory audit evidence and emits `INVENTORY_RESERVATION_EXPIRED` to the outbox in the same transaction. The application boundary exposes this as an Ops maintenance command.
- **Boundary commit:** `621b170a81da5967fbff1d2df286388c8d03b9a3`
- **Regression commit:** `3ecea65c1b58378dc2acbd91b829fd95e8567cef`
- **Verification state:** source + regression persisted; fresh PostgreSQL execution/central scheduler evidence remains pending.

### G-337 Closure Record
- **Resolution:** added canonical retailer-side `SUBMITTED → CANCELLED` command. It validates active retailer tenancy, locks the order and its reservations, atomically decrements reserved stock, releases ACTIVE reservations, updates `cancellation_reason`, emits `ORDER_CANCELLED` to vendor recipients and returns an idempotent replay for already-cancelled orders.
- **HTTP:** `POST /api/v1/orders/{order_id}/cancel` for `RETAILER_OWNER/RETAILER_STAFF`.
- **Source commits:** service `d5c4716b3a1106fe0fb21b31a55a0deb75d27db9`, boundary `1043c57c5810f36cc246ac15107b47ffd9e62fe7`, route `98e9ddb121a5919c50fc7f1f2659db7df979594d`.
- **Regression:** `test_retailer_pre_acceptance_cancellation_releases_reservation` commit `c8cd55c7c21a04054da85a7426b8df203b8dfeee`.
- **Verification state:** source + route + regression persisted; fresh runtime execution remains pending.

### G-338 Closure Record
- **Resolution:** canonical checkout now sets every inventory reservation `expires_at` directly from the locked allocation plan's `expires_at` instant, removing independent `now()+15 minutes` drift.
- **Regression:** `test_reservation_expiry_matches_allocation_plan_expiry` creates a real plan and checkout and asserts reservation expiry equals plan expiry exactly.
- **Source commit:** `04e105d59042983dd70a240f3f7c40729efa15d2`
- **Regression commit:** `6f6ae7ae4f4109087e04b56e81c7683295ef8969`
- **Verification state:** source + E2E regression persisted; fresh PostgreSQL execution remains pending.


### G-339 Closure Record
- **Resolution:** Added runtime lifecycle regression: basket/plan/checkout creates real reservation; canonical vendor rejection releases it; second runtime checkout reaches expiry worker and releases stock.
- **Evidence:** 7c3e6d2a4e9bdc8b91b6c8fd4d8bf6fdbc9b1521
- **Verification state:** code + regression persisted; fresh PostgreSQL/CI execution remains pending.


### G-340 Closure Record
- **Resolution:** Two real PostgreSQL connections call ReservationService against one scarce inventory row; row locking allows exactly one reservation.
- **Evidence:** 536f6e7ae653db2b8762dc9accd03416480e7fe5
- **Verification state:** code + regression persisted; fresh PostgreSQL/CI execution remains pending.


### G-341 Closure Record
- **Resolution:** DB partial unique index enforces idempotency_key uniqueness; service re-checks after inventory locking and returns exact replay for concurrent same-key calls.
- **Evidence:** a3b976a4f2a9aa0970b9b34da2854118eabbb786; dbf9f0a195a0ae7c1e06065a6f432d07d9194b88; 536f6e7ae653db2b8762dc9accd03416480e7fe5
- **Verification state:** code + regression persisted; fresh PostgreSQL/CI execution remains pending.


### G-342 Closure Record
- **Resolution:** Deferred PostgreSQL constraint trigger enforces vendor_inventory.reserved_quantity = SUM(ACTIVE reservation quantity) at transaction commit; regression proves mismatched direct mutation is rejected.
- **Evidence:** 43380c08d752e3dcfe4dca70d5d84a3c5ac9a00d; ecb42e201b31ffb7f99222e522cd645b5c2d4421
- **Verification state:** code + regression persisted; fresh PostgreSQL/CI execution remains pending.

### G-343 Closure Record
- **Resolution:** reservation lifecycle now emits independent durable outbox events for `INVENTORY_RESERVATION_CREATED`, `INVENTORY_RESERVATION_CONSUMED`, `INVENTORY_RESERVATION_RELEASED`, and `INVENTORY_RESERVATION_EXPIRED`. Release events cover retailer cancellation and vendor acceptance timeout; consumption covers full vendor acceptance and partial acceptance; shortage release in partial acceptance emits a distinct release event. Canonical architecture event catalog has been updated.
- **Source commits:** `24b273301cc114d31348ea16cbc94c1ab79159f1`, `af98846fa4ca594473ff6c0482249508ebf159c3`, `7dde8adf442d1ea0b205d1407e6c7099c3d6a04f`, `fa4d1a82a37d5daa3e47d631f3c7b33b182bd592`.
- **Regression commits:** `3db5ebc525cdcdcfc0aa93e532ce319e7b80cb79`, `1474189e4e019e80df4b56a2229feed5aaa7a297`, `38c105283c3d4757d4c84342318e44fbd18abf57`.
- **Verification state:** source + architecture + regression evidence persisted; fresh PostgreSQL/CI execution remains pending.


## Remediation reconciliation — 2026-09-26 — second pass

The following closure claims are based on current runtime/source inspection on this remediation branch; they are not equivalent to a successful CI execution.

### Closed in source/runtime
- **G408-G439 — Dispute/Refund canonicalization:** required evidence and line items, delivered-order + filing-window checks, idempotency fingerprints, canonical investigation/resolution/closure lifecycle, DB adjudication guards, payment-linked refunds, source-scoped refund uniqueness, cumulative refund ceilings, actor separation, immutable dispute events, and canonical HTTP routes.
- **G440-G451 — Delivery/POD hardening:** dispatch no longer exposes the delivery OTP, active-delivery locking precedes POD media validation, OTP attempt limit and format are enforced, delivered quantities are bounded by ordered/accepted quantities, and POD test coverage was extended.
- **Payment Evidence subset:** explicit payment selection is required when an order has multiple payment records; evidence amount is bounded by the selected payment; RECEIPT_IMAGE requires READY media with exact order/payment target and uploader ownership.
- **RMA financial lifecycle:** refund creation is PENDING, approval is a separate operator action with two-person separation, completion creates the settlement adjustment, partial refund does not mark the payment fully refunded, and REFUND_PENDING cannot close before refund completion.
- **Audit/history/media controls:** admin/inventory audit history is append-only; READY media requires SHA-256; order-targeted media is allowed for pre-created evidence; notification retention has a daily scheduler entry point and workflow.

### Still requiring environment/external evidence
- GitHub Actions currently creates the verification jobs but they terminate before executing any step; the job-log endpoint also returns no stored log. Therefore **CI PASS is not claimed**.
- Live object-storage evidence and real device/mobile evidence remain external execution items; local/test-provider coverage does not substitute for that evidence.
- Deployment secrets/configuration (e.g. database secret for scheduled retention) remain environment configuration rather than repository guarantees.

### Design note
The remediation intentionally does **not** enforce one refund record per order. Refund uniqueness is source-scoped (one active refund per dispute or return) while cumulative payment ceilings prevent financial over-refunding across multiple legitimate refund sources.

### G-466 Closure Record — Member Fan-Out Deduplication & Event ID Isolation
- **Resolution:** Outbox events that fan out to multiple organization members generate unique per-row `event_id` and include member `user_id` in `dedupe_key`, preventing single-recipient truncation or duplicate key conflicts on multi-recipient notifications.
- **Source commits:** `95f9bb689d27fcfd90a8a407e79a93a3a45a6f9d`, `217e57ce56f26b6865fbf1a5c1385ae52853c46d`
- **Verification state:** RUNTIME VERIFIED (658/658 PASS).

### G-467 Closure Record — Retailer Cancellation Reservation-Release SQL Parameter Count
- **Resolution:** Corrected SQL parameter tuple count in `CanonicalRetailerOrderService.cancel_order` for `INVENTORY_RESERVATION_RELEASED` outbox emission (removed redundant extra string argument so 7 parameters match 7 `%s` placeholders).
- **Verification state:** RUNTIME VERIFIED (`test_retailer_pre_acceptance_cancellation_releases_reservation` PASS).

### G-468 Closure Record — Admin Category Create Audit Log Variable Alignment
- **Resolution:** Replaced unbound variable `category_id` with `row["id"]` and aligned SQL placeholder count in `POLApplicationBoundary.admin_category_create` `admin_audit_logs` write.
- **Verification state:** RUNTIME VERIFIED (`test_broadcast_and_category_admin_routes_use_real_boundary` PASS).

### G-469 Closure Record — RMA Settlement Status Guard
- **Resolution:** Added settlement status verification in `CanonicalReturnService._create_settlement_adjustment` to ensure adjustments only attach to active settlements (`CALCULATED`, `RECONCILED`, `DISPUTED`).
- **Verification state:** RUNTIME VERIFIED.

### G-470 Closure Record — Verification Suite Autonomous Secret Configuration
- **Resolution:** Added explicit default `POL_JWT_SECRET` in `scripts/run_verification_suite.py:configure_test_environment()` to prevent unconfigured shell environments from failing auth contracts.
- **Verification state:** RUNTIME VERIFIED (Suite self-contained, 658/658 PASS).



## Vendor Android audit closure — 2026-09-29

### Closed source/contract gaps
- Vendor logo asset binding: closed; mobile bundle is byte-identical to canonical Vendor asset.
- Vendor Staff acceptance/rejection/partial-acceptance UI authority: closed; Owner-only.
- Vendor Staff finance read authority: closed at ApplicationBoundary and regression-test level; Owner-only.
- Invoice/settlement response-field mapping: closed in mobile.
- V-13 invoice/settlement detail read surfaces: implemented.
- V-14 storefront read/preview: implemented.
- V-16 barcode lookup/match/candidate + continuous-scan/publish source flow: implemented.

### Remaining runtime gates
- Native camera permission/frame/continuous-scan runtime.
- Device visual verification for Persian RTL, Light/Night, font metrics and BIDI edge cases.
- Current-head executable CI evidence.
- Live HTTPS VPS endpoint verification.
- Native Expo/Gradle build and installation.


## OTP Policy Supersession — 2026-11-24

- D-018 now requires exactly six ASCII digits for all newly issued login/registration OTPs. Its existing TTL, resend interval, rate limit, maximum attempts, lockout and token lifetimes remain unchanged.
- D-029 requires exactly six ASCII digits for all newly issued delivery/POD OTPs, with a separate recipient-only and single-use lifecycle.
- Four-digit delivery OTPs are accepted only when they were already issued to an in-flight delivery before migration 077. They remain valid only for that delivery until terminal completion. Migration 077 never rotates or re-sends them.
- Historical examples, old smoke-test records and old screenshots that show four-digit login OTPs are superseded evidence and must not be used to describe the current policy.


## OTP change CI evidence — 2026-11-25

The D-018 / D-029 six-digit implementation was merged in PR #59. Exact tested SHA `dbf0a2284e4f16d0cc1e7568b78e81e11c5352a6`: backend 852/852, browser E2E 41/41, mobile 17/17 Expo steps, and static gate 11/11. The migration chain 001–077 applied successfully in PostgreSQL 18 CI. TODO-084 skipped the Android QA APK matrix; visual device QA, live SMS provider acceptance and production release gates remain separate.
