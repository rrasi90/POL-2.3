# POL Global Engineering Audit — 2026-09-14

**Governance reconciliation amendment:** 2026-09-18

**Scope:** Full repository / architecture review after MVP hardening and User Profile completion.

**Audit level:** Principal/Staff Engineer review standard.

## 1. Architecture verified

### Identity and tenancy
- `organization_memberships.role` is RBAC SSoT.
- `user_sessions.active_organization_id` is the request tenant context.
- `users.role`, `retailers.user_id`, and `vendors.user_id` are legacy compatibility fields only.
- Role/organization-type database invariants remain enforced.

### User profile
- Every user receives exactly one `user_profiles` row automatically.
- Every membership receives one `membership_profiles` row.
- Retailer, vendor, operator and field personas receive structured contextual profiles.
- UI personalization is separated from authorization.
- Role transitions remove stale persona subprofiles.

### Commerce
- Basket -> AllocationPlan -> OrderGroup -> Order -> OrderItem remains canonical.
- Multi-vendor MVP remains D-014.
- Checkout is server-side revalidated before reservation.
- Inventory reservation and checkout idempotency are database-backed.
- Temporal vendor pricing is enforced.

### Referral
- Vendor Referral is MVP under D-016.
- Attribution is first-touch and immutable for the retailer in MVP.
- First order activates attribution.
- Incentives/rewards are explicitly future-only.

### Finance / trust
- Payment model remains non-custodial direct settlement.
- Payment evidence is observational; independent evidence is not summed.
- Unsupported split-payment evidence no longer causes a worker runtime exception.
- RMA has an explicit refund linkage before REFUNDED.

### Notifications / async
- Domain transaction -> outbox -> integration -> notification -> provider delivery remains the async ownership model.
- Provider acceptance is distinct from actual delivery receipt.
- Notification recipient routing is explicit.
- Daily inventory routing is fail-closed per vendor while preserving batch health.

## 2. Product / UX verified

- Retailer: simple, reorder-oriented, order-centric experience.
- Vendor owner: catalog, price, inventory, orders, daily confirmation, referral.
- Vendor staff: function-specific views for sales, warehouse, operations, finance.
- Operator: explicit dashboard scope.
- Field activator: task-first, assisted onboarding/order flow.
- Profile UI is persona-specific but never an authorization mechanism.

## 3. Engineering defects corrected in this pass

1. Missing universal user profile model.
2. Missing tenant-specific persona context.
3. Missing role-specific profile structures.
4. Missing profile application boundary.
5. Missing profile route verification.
6. Missing environment verification for profile cardinality.
7. Stale persona profile risk after membership role transition.
8. RMA refund lifecycle had no explicit refund creation/linkage.
9. `SPLIT_PAYMENT` evidence could produce an empty-observation runtime failure.
10. Route coverage did not previously include profile routes.
11. Decision Register did not previously lock the profile model.

## 4. Explicit architectural boundaries retained

These are intentionally **not** activated in MVP:

- BNPL / trade credit
- wallet / escrow / custody
- owned logistics
- heavy procurement / quotation workflows
- advanced AI recommendation
- multi-touch referral rewards
- advertising
- complex loyalty / gamification
- manufacturer-facing commerce

See `POL_00_PROJECT_CONTROL/FUTURE_VERSION_NOT_MVP.md` for the non-MVP roadmap.

## 5. Production-readiness gates still requiring separate implementation

The repository is an engineering/domain verification environment, not yet a claim of a deployed production application. Before real production traffic, these gates must still be completed:

### A. Production HTTP/API runtime
D-020 now canonically selects FastAPI as the production HTTP transport adapter behind `POLApplicationBoundary`. The repository contains the FastAPI transport entrypoint; actual production deployment/certification remains a later gate.

### B. Production authentication provider
Production authentication still has open provider/infrastructure gates. D-018 rotation policy remains explicitly undecided; the repository must not infer a rotation requirement from this audit. Provider-backed OTP/SMS, secret management, production rate-limit infrastructure and deployment certification remain later gates.

### C. Live provider certification
SMS/push providers are adapter-neutral and must receive concrete credentials, delivery receipts/webhooks, secret rotation and production certification.

### D. UI implementation
`06_PRODUCT/USER_PROFILE_UX_SPEC.md` defines the product contract. Actual Android/PWA/vendor/admin UI implementation remains a separate client implementation phase.

### E. Operational observability
Production requires centralized structured logs, metrics, traces, alerting, worker lag monitoring, dead-letter monitoring, and audit-log retention policy.

### F. Backup / recovery / migration operations
PostgreSQL backup, restore drills, PITR, migration rollback policy and production data retention require deployment-level implementation.

## 6. Audit conclusion

The canonical data/domain architecture is substantially more complete after this pass, but the project must not confuse a highly verified domain core with a deployed production service.

The next engineering gate is therefore **production applicationization**, not additional speculative MVP feature expansion.
