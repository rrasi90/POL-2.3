# POL Database Schema Manifest — 2026-09-16

**Status:** CANONICAL CURRENT MANIFEST  
**Database:** PostgreSQL 18  
**Migration chain:** `migrations/001_*.sql` through `migrations/022_*.sql`  
**Current table count:** 90 public base tables  

## Canonical rules

1. The numbered migration chain is the physical schema source of truth.
2. Migrations 001–019 establish the 90-table domain/platform schema; migrations 020–022 add integrity constraints/triggers without adding tables.
3. PostgreSQL 18 is the only canonical runtime database (`D-015`).
4. SQLite is allowed only for isolated unit tests.
5. Generated verification artifacts are not schema source-of-truth and must not be committed.

## Current migration responsibilities

| Range | Responsibility |
|---|---|
| 001–003 | Initial domain/platform schema and contract reconciliation |
| 004 | Operational intelligence, daily inventory, feedback, reliability, RMA, identity lifecycle |
| 005 | Competitive operational hardening, temporal pricing, windows/capacity, payment evidence, saved lists, consent, risk, metrics, experiments |
| 006–007 | Temporal/effective vendor pricing integrity |
| 008–010 | Outbox routing, notification delivery/templates, inventory reminder scheduling |
| 011 | RMA, support audit, reconciliation/provider attempt hardening |
| 012 | Canonical route/template contract alignment |
| 013 | Vendor referral MVP and payment/RMA integrity extensions |
| 014–016 | Operational responsibility guards and referral/role integrity hardening |
| 017–018 | Universal user profile, membership profile and role-transition persona integrity |
| 019 | RMA/refund state integrity |
| 020 | Temporal, consent, saved-list and refund database invariants |
| 021 | Session tenant binding and cross-entity order/allocation integrity |
| 022 | Tenant ownership guards for support and feedback records |

## Required runtime invariants

- every user has exactly one `user_profiles` row;
- every organization membership has exactly one `membership_profiles` row;
- active session tenant must be an active membership of that session user;
- `OrderGroup.basket_id` must match `AllocationPlan.basket_id`;
- `OrderGroup.retailer_id` must match its basket retailer;
- child order retailer must match its order group;
- child order vendor must belong to an active vendor organization;
- support/feedback actor must belong to the target tenant;
- inventory reservation cannot exceed physical quantity;
- vendor price validity windows cannot overlap;
- vendor operating/capacity effective windows cannot overlap;
- only one active default saved list exists per retailer;
- active consent is unique per user/type globally or per tenant;
- RMA `REFUND_PENDING` / `REFUNDED` requires a positive approved refund amount;
- direct payment remains `NON_CUSTODIAL_DIRECT`.

## Verification requirement

A schema change is not considered complete until the full migration chain executes cleanly on PostgreSQL 18 and the verification suite passes. Table count alone is insufficient; constraints, triggers, tenant isolation and state-transition tests must also pass.
