# POL Certification Addendum — 14 September 2026

## Purpose

This addendum corrects the certification wording for the operational-intelligence cycle and records the exact boundary of what the GitHub Actions evidence proves.

## Verified CI Evidence

- Workflow run: `34818313995`
- Tested commit: `f3a65a3060d2f09ca7bf9cbd1b270b13f539ca2f`
- PostgreSQL: `18.6` in the GitHub Actions `postgres:18-alpine` service
- Schema observed by the verification artifact: `62` base tables
- Tests: `47 collected / 47 passed / 0 failed / 0 skipped`
- Subsequent documentation commit: `18129cfc27605daa415d545487f47af93013891d`

## Correct Certification Boundary

The run establishes:

1. `CI_VERIFIED` — the canonical migration chain, environment verification and automated verification suite passed in GitHub Actions.
2. `DATABASE_RUNTIME_VERIFIED` — PostgreSQL schema, constraints and tested transaction paths executed successfully in the CI database.
3. `DOMAIN_RUNTIME_VERIFIED` — the tested Python domain/application services executed successfully against the CI database.

The run does **not** by itself establish:

- `FULL_APPLICATION_RUNTIME_VERIFIED`
- production readiness of the Android/PWA clients
- production readiness of external SMS, push, object-storage, queue, API-gateway or observability integrations
- successful end-to-end deployment of the complete production architecture

These remain separate implementation and environment verification gates.

## PostgreSQL Version Correction

Earlier cycle text stated PostgreSQL `18.4`. The authoritative GitHub Actions service for run `34818313995` is `postgres:18-alpine`, and the generated verification artifact reports the concrete runtime version as PostgreSQL `18.6`. Future certification documents must use `18.6` for this run.

## Checkout Boundary Correction

`RevalidationCheckoutService.revalidate_and_checkout` is the canonical safe checkout path. A new `CanonicalCheckoutGateway` has been added as the application-facing entry point. New callers must use the gateway rather than importing the legacy `CheckoutService` directly.

A regression test prevents verification/test code from reintroducing imports of the legacy checkout service outside `domain_services.py`.

The legacy class remains in `domain_services.py` for compatibility during this transition; complete deletion should occur only after all real application-layer callers have been migrated and the application stack exists in the repository.

## CI Workflow Label Correction

The workflow step previously labelled `Apply Canonical Dynamic Migration Chain (001 -> 002 -> 003)` has been corrected to `Apply Canonical Dynamic Migration Chain (001 -> N)` because the migration runner dynamically discovers all SQL migrations.

## Final Status

**Cycle status: `DOMAIN_VERIFIED + DATABASE_VERIFIED + CI_VERIFIED`**

**Full application runtime verification: `NOT YET PROVEN`**
