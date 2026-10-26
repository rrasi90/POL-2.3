# Synthetic Fixture Spec (Run 2026-10-27)

Deterministic, non-personal seed data for the golden scenarios. Builds on the existing harness `scripts/e2e_seed.py` / `e2e_db.py` (which already migrates+seeds+serves for Playwright).

## Seed entities

- Orgs: VEN-1, VEN-2 (vendors, separate orgs); RET-1, RET-2 (retailers); OP-1 (operator)
- Users: ven1-owner (VENDOR_OWNER), ven1-staff (VENDOR_STAFF, delegated catalog only — deny-list active), ven2-owner; ret1-owner, ret1-staff; ret2-owner; ops-admin (ADMIN_SUPER); driver-placeholder (no role — proves D-01 gap)
- Branch/membership: each retailer 1 org; ret1 has 2 memberships? No — POL org model is per-org; record org-scoping expectations
- Products: P-1..P-6 across VEN-1/VEN-2, barcodes scoped global+vendor, units: carton(12)/pack(4)/piece, MOQ 3 cartons on P-1
- Inventory: P-1 stock 5 cartons (race-test target), P-3 zero stock
- Prices: P-1 price history (2 entries) for snapshot checks
- Orders: ORD-full (delivered), ORD-multi (2-vendor group), ORD-shortage (partial accepted), ORD-cancelled, ORD-disputed (dispute OPEN → INVESTIGATING), ORD-returned
- Payments: evidence-uploaded pending verify; direct-transfer recorded
- Exceptions: one failed delivery with exception record; one dispute with refund PENDING
- Negative rows: expired OTP challenge, revoked session, deactivated staff user, stale order (past vendor deadline)

## Reset & determinism

- Idempotent seed (delete-by-fixed-ids then insert), fixed timestamps (fixture clock, mirroring mock's frozen 2026-09-29 pattern), no real PII (phones 10000000001-…99, names "Test Vendor 1")
- All writes pass migration contract checks (integrity guards 019/062/064-068/073)
- E2E_STAGING variant: same seeds against staging DB via e2e_serve.py

## Mapping to golden scenarios

G1 uses ORD-full path from fresh seeds; G2 seeds ORD-shortage precondition; G3 failure fixture; G4 dispute/refund chain; G5 race fixture (P-1 stock 5, two concurrent checkouts); G6 is untestable until driver substrate exists (documented gap).

## Mock parity rule

Any fixture used in mock mode must have the same shape the live API emits (audit §6 drift list is the checklist). Retailer flows currently have NO mock coverage — adding them is part of the implementation run, not this one.
