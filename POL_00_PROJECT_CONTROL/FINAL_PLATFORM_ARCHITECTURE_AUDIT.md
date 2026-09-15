# POL Final Platform Architecture Audit — Current Certification Boundary

**Document ID:** `POL-GATE-2026-FINAL`  
**Version:** 2.1  
**Review date:** 2026-09-16  
**Status:** `CANONICAL / BOUNDED CERTIFICATION`  

## 1. Executive result

The repository contains a substantial, tested PostgreSQL/domain-service foundation for the POL MVP. The latest recorded independent CI evidence establishes successful migration, database-runtime, and domain-runtime verification for a specific tested commit. It does **not** establish full application or production readiness.

## 2. Verified evidence

For GitHub Actions workflow run `34818313995`:

- Tested commit: `f3a65a3060d2f09ca7bf9cbd1b270b13f539ca2f`
- PostgreSQL runtime: `18.6` (`postgres:18-alpine`)
- Base tables observed: `62`
- Automated tests: `47 collected / 47 passed / 0 failed / 0 skipped`
- Verification categories: CI, database runtime, and domain/application-service runtime.

The machine-readable artifact is `artifacts/pol-test-results.json`.

## 3. Current architecture

The current MVP decision is **D-014 Multi-Vendor Basket**: one retailer basket is allocated across the minimum necessary number of vendors; each basket line is assigned to at most one vendor and quantity splitting of a line is not supported in MVP. The resulting child orders have independent fulfillment, payment/settlement and dispute lifecycles.

Canonical IAM roles are `RETAILER_OWNER`, `RETAILER_STAFF`, `VENDOR_OWNER`, `VENDOR_STAFF`, `OPS_AGENT`, `ADMIN_SUPER`, and `FIELD_ACTIVATOR`. Legacy `SUPER_ADMIN`/`OPS_ADMIN` aliases are compatibility vocabulary only.

The canonical migration chain is `001 -> 002 -> 003 -> 004 -> N`, and the current recorded schema count is 62 base tables.

## 4. Checkout boundary

`CanonicalCheckoutGateway` in `scripts/checkout_gateway.py` is the application-facing checkout entry point and delegates to `RevalidationCheckoutService`. The revalidation path checks basket version, allocation expiry, current price and locked physical availability before creating orders/reservations.

The legacy `CheckoutService` remains in `scripts/domain_services.py` for compatibility and must not be introduced as a new application entry point.

## 5. What remains unproven

The recorded CI run does **not** prove:

- `FULL_APPLICATION_RUNTIME_VERIFIED`;
- production readiness of Android/React Native or PWA clients;
- production readiness of SMS, push, object storage, queue, API gateway or observability providers;
- production deployment and rollback behavior;
- real Ahvaz pilot outcomes, retention, vendor adoption, or unit economics.

These are separate implementation/environment/pilot gates.

## 6. Required next gate

Before declaring Sprint 0 implementation complete, run the canonical CI workflow against the current branch tip after all code/documentation changes. Then build the actual application/API layer on top of the canonical domain contracts and execute integration tests against PostgreSQL 18.

**Current certification status:** `CI_VERIFIED + DATABASE_RUNTIME_VERIFIED + DOMAIN_RUNTIME_VERIFIED` for the recorded commit.  
**Full application certification:** `NOT YET PROVEN`.
