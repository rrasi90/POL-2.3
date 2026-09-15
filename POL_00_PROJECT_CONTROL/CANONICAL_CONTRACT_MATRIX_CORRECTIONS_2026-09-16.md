# POL Canonical Contract Matrix — Corrections 2026-09-16

**Status:** CANONICAL CORRECTION OVERLAY

This document is part of the canonical contract source. It supersedes only the conflicting rows/claims identified below in `CANONICAL_CONTRACT_MATRIX.md`; all non-conflicting rows remain unchanged.

## C-01 — Canonical role names

The canonical authorization roles are:

- `ADMIN_SUPER`
- `OPS_AGENT`
- `RETAILER_OWNER`
- `RETAILER_STAFF`
- `VENDOR_OWNER`
- `VENDOR_STAFF`
- `FIELD_ACTIVATOR`

`SUPER_ADMIN` and `OPS_ADMIN` are legacy aliases accepted only for backward compatibility during migration. They are not the preferred canonical vocabulary and must not be used for new UI/API documentation.

Authority remains `organization_memberships.role` plus active tenant context; `users.role` is not an authorization source.

## C-02 — Basket status vocabulary

The current database/application contract does **not** establish `LOCKED` or `MERGED` as canonical basket statuses. The current canonical basket status set is the set enforced by the PostgreSQL schema and current services:

- `OPEN`
- `ABANDONED`
- `SUBMITTED`
- `EXPIRED`

Any future `LOCKED` or `MERGED` state requires a separate schema/application decision before it can appear in canonical API or UX documentation.

## C-03 — User Profile / Persona database terminology

The canonical implementation tables are:

- `user_profiles`
- `membership_profiles`
- `retailer_membership_profiles`
- `vendor_membership_profiles`
- `operator_membership_profiles`
- `field_activator_profiles`

Conceptual UX documentation may use `PersonaProfile`, but must not introduce legacy implementation names such as `retailer_profiles`, `vendor_profiles`, `operator_profiles`, or `staff_profiles` as if they were current tables.

## C-04 — Frontend transport vs design terminology

The approved technical architecture specifies Next.js/React for web and React Native/Expo for the retailer mobile surface. The design system remains transport-agnostic; endpoint method/version details are owned by the canonical API contract and must be reconciled before frontend integration.

## C-05 — Validation status must reflect actual runtime scope

`RUNTIME_VERIFIED` means the domain behavior has actually executed against PostgreSQL 18 through the repository verification harness. It does **not** mean that a production HTTP server, live authentication provider, SMS/push provider, observability stack, deployment topology, backup/PITR or production client UI has been certified.

## C-06 — Design dependency

`13_PRODUCT_DESIGN/15_CROSS_PROJECT_DESIGN_AUDIT_2026-09-15.md` and the completed design specification files must consume this correction overlay before high-fidelity design work. A visual artifact must never reintroduce superseded role, status or table terminology.
