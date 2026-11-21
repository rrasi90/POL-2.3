# Driver App Readiness — پل راننده (Run 2026-10-27)

Verdict: **NOT BUILD-READY — P0 backend substrate missing.** No DRIVER role, no driver sessions, no driver-owned state transitions exist anywhere in the POL repository. This is a verified absence, not an assumption (audit §2.4, all tags `[NOT_FOUND]` after repo-wide search).

## What already exists (reusable substrate — [CODE_VERIFIED])

| Primitive | Location | Reusable for driver app? |
|---|---|---|
| Delivery state machine `ASSIGNED→PICKED_UP→IN_TRANSIT→ARRIVED→DELIVERED/FAILED` | migrations/001:457-458; orders.py:288-318 | YES — exactly the driver's job lifecycle |
| Delivery OTP (6-digit) + POD bounds | migrations/030, 071, 077, 068; orders.py:330-373 | YES — driver confirms delivery with it |
| Driver metadata (name/phone/plate) at dispatch | fulfillment_service.py:192-239 | Partially — data exists but driver is not an actor |
| DeliveryException lifecycle | orders.py:385-445 | YES — failed-delivery flows |
| OTP auth + session machinery | auth.py; auth_boundary.py | YES — pattern reusable for driver sessions |
| Two-variant build pipeline (retailer/vendor) | build_android_variant.mjs; app.config.js | Pattern reusable; hardcoded 2-variant enum needs a third branch |

## What is missing (P0 blockers, each with evidence)

1. **DRIVER role** — absent from `scripts/permissions.py:38-118` (7 roles), `migrations/001_initial_schema.sql:19-22` (role CHECK), `mvp/apps/mobile/src/types.ts:1-8`. The only trace is a display label `DRIVER: "راننده"` in statusLabels.ts:172.
2. **Driver principal/org model** — plan §33.7 decision: is a driver an OPERATOR-org member, a VENDOR-org member, or a new CARRIER org type? The DB trigger `trg_enforce_org_membership_role_invariant` (migrations/003:91-94) currently forbids any role outside RETAILER_*/VENDOR_*/platform-role mappings — a new DRIVER role REQUIRES touching this invariant + migration.
3. **Delivery-assignment ownership** — today `deliver` and stage transitions are vendor/ops-triggered (`orders.py:288-330` guards). A driver app means re-assigning these writes to the driver principal — authorization redesign, not just a new role (HIGH migration risk; plan §33.9).
4. **Driver app variant** — third entry file (`index.driver.ts`), third branch in `app.config.js:2-3,10,29` and `build_android_variant.mjs:7`; package ID (proposed `ir.pol.driver` — uniqueness check deferred per plan §33.6), Persian label, icon.
5. **Offline mutation semantics** — plan §33.9: delivery mutation retry/idempotency/conflict semantics are absent (idempotency exists only at checkout, migration 061). A driver on a weak network WILL double-submit "تحویل شد". Workflow WF-21.
6. **Mobile tests** — parity.md itself records "No Driver App (D-023)"; `mvp/apps/mobile/src/__tests__/` has no test framework.

## Cartona evidence for the driver loop (all MARKETING_CLAIM — public listing only)

Daily order list → platform-optimized routes → "advanced system to confirm the receipt of orders" → profit tracking → dedicated support. Location collection declared; "data can't be deleted". POD mechanics, cash handling, offline behavior, payout cycle: **not disclosed**. Cartona Express is young (500+ installs, Jul 2026). No APK available — artifact-level analysis impossible.

## Recommended minimal driver vertical slice (for decision, not yet build-ready)

1. (Backend) Add DRIVER role + org-type decision + driver sessions [D-01, L migration]
2. (Backend) Assign delivery → driver principal; stage transitions owned by assigned driver [D-04, authorization redesign]
3. (Backend) Idempotent delivery confirm (reuse checkout idempotency pattern) [D-07]
4. (Mobile) Third variant reusing AppShell: assignment list → pickup → stops → POD(OTP) → exceptions; offline = read-only cache until (3) ships
5. (QA) Role-isolation negative tests (driver A cannot see driver B assignments) + POD tests (exist for endpoint, need driver-context variants)

## Gate

`RUNTIME_PARITY_VERIFIED` for the driver app is **not claimable** in this run (no artifact, no runtime). `BUILD_HANDOFF_READY` for the driver app is **conditional** on the D-01 org-model product decision — the design decision is documented in `pol-api-adaptation-matrix.csv` (D-01/D-03/D-04/D-07 rows), but the org-model choice (§33.7) needs an explicit product/ops sign-off recorded before the implementation run starts.
