# POL Canonical API / Application Boundary

**Status:** CANONICAL PRE-UI ENGINEERING CONTRACT  
**Scope:** MVP application boundary with FastAPI (D-020) as the production HTTP transport adapter.

## 1. Boundary rule

Client-facing transport code MUST NOT write directly to PostgreSQL domain tables and MUST NOT import legacy `domain_services` for business commands.

Transport adapter:

`HTTP / mobile client / web client -> request authentication -> ApplicationContext -> POLApplicationBoundary -> canonical domain service/gateway -> PostgreSQL transaction -> domain event/outbox -> async worker`

The current client-facing command facade is `scripts/application_boundary.py`; the FastAPI transport entrypoint is `scripts/api/main.py`.

## 1.1 HTTP transport status (Batch 6C)

The first HTTP transport slice is implemented at `scripts/api/` and exposes the canonical authentication/session and profile/context routes. Batch 6C-3 extends the production transport to the retailer basket → allocation-preview entrypoints.

The Batch 6C-2 checkout transport adds `POST /api/v1/orders` as the canonical authenticated checkout entrypoint. The route accepts the confirmed allocation-plan ID, delivery address, preferred payment method and idempotency key, derives the active retailer/basket allocation context server-side, and invokes `POLApplicationBoundary.checkout_from_allocation_plan()`. Allocation, freshness, stock, MOQ and reservation rules remain owned by the canonical checkout gateway; the HTTP adapter does not accept client-supplied retailer IDs or vendor allocation mechanics. The transport remains thin: it performs schema validation, authentication/session validation, ApplicationContext construction, error-envelope mapping, and transaction lifecycle management; it does not write domain tables directly or implement business state machines.

Authentication endpoints that establish or refresh a session (request-otp, verify-otp, refresh, switch-organization, session revocation) execute in the pre-ApplicationContext authentication/session layer through scripts/auth_application.py. They are not business-domain commands and therefore do not bypass the canonical POLApplicationBoundary for authenticated product capabilities. Once an access token is validated, all product profile/commerce/support capabilities enter POLApplicationBoundary with a derived ApplicationContext.

Batch 6C-3 adds `POST /api/v1/baskets`, `POST /api/v1/baskets/{basket_id}/items`, and `POST /api/v1/baskets/{basket_id}/allocation-preview`. These routes derive the retailer tenant from the authenticated membership, use the canonical optimistic basket-version guard, execute the deterministic multi-vendor allocation engine through `CanonicalBasketAllocationService`, persist the canonical `allocation_plans` / `allocation_items`, and return only the business-level allocation preview contract. They do not accept `retailer_id`, perform direct SQL in the route, or expose allocator internals.

## 2. ApplicationContext

Every request must carry:

- `user_id`: authenticated principal.
- `organization_id`: active tenant context selected from session/membership; never trusted from an arbitrary client body.
- `correlation_id`: request trace ID propagated into audit/outbox metadata by the transport adapter.

Authorization is evaluated from `organization_memberships` joined to active `organizations`. `users.role`, `vendors.user_id`, and `retailers.user_id` are legacy compatibility fields and are not authorization SSoT.

## 3. Canonical client commands / queries

| Capability | Canonical command boundary |
|---|---|
| **Universal profile read** | `profile_get()` |
| **Universal profile update** | `profile_update()` |
| **Profile completion** | `profile_completion()` |
| **Active-tenant persona read** | `profile_get()` with active organization context |
| **Active-tenant persona update** | `profile_membership_update()` |
| Basket create | `basket_create()` |
| Basket item add | `basket_add_item()` |
| Allocation preview | `basket_allocation_preview()` |
| Checkout | `checkout_from_allocation_plan()` → `checkout()` |
| Feedback list | `feedback_list()` |
| Feedback admin inbox | `feedback_admin_inbox()` |
| Feedback reply | `feedback_reply()` |
| Support create/read/message/assign/transition | `support_*()` |
| Vendor referral create/redeem | `create_vendor_referral()`, `redeem_vendor_referral()` |
| Return/RMA request/transition | `return_request()`, `return_transition()` |
| Payment reconciliation worker | `reconcile_payments()` |
| External notification delivery worker | `deliver_external_notifications()` |

## 4. Profile boundary rules

`user_profiles` is the universal identity/profile SSoT. One row MUST exist for every user.

`membership_profiles` is the tenant-specific persona SSoT. One row MUST exist for every organization membership.

Role-specific profile tables provide structured fields for retailer, vendor, operator and field personas. They are presentation/context data and MUST NOT be treated as a substitute for RBAC.

The client may personalize UI from profile context, but all server authorization MUST still evaluate `organization_memberships.role` and active organization status.

## 5. Idempotency

Commands that create externally meaningful state MUST expose an idempotency key where retries can otherwise duplicate state:

- checkout: `idempotency_key`
- return request: `idempotency_key`
- referral redemption: `request_idempotency_key`
- payment evidence: `external_reference` uniqueness
- notification provider attempt: deterministic `provider_attempt_key`

## 6. Error contract

Transport adapters map domain errors without bypassing domain state machines:

- `PermissionError` / boundary access errors -> HTTP 403
- missing entity / `KeyError` -> HTTP 404
- invalid state / `ValueError` / state-machine errors -> HTTP 409 or 422 according to transport semantics
- retryable provider error -> worker retry, not synchronous client retry
- permanent provider/configuration error -> durable FAILED delivery + operational visibility

## 7. Async ownership

Synchronous application transactions only persist durable state and enqueue outbox events. Provider calls, notification sending and reconciliation polling are worker responsibilities.

The provider boundary is deliberately provider-neutral until POL selects concrete SMS and push suppliers and provisions credentials. `scripts/provider_adapters.py` is the adapter contract; `scripts/provider_delivery_worker.py` is the execution/retry owner.

## 8. Legacy access prohibition

Before visual-design gate, repository/application integration must demonstrate that no HTTP/mobile/web adapter reaches:

- legacy `NotificationService` recipient fallback;
- legacy `FeedbackService.get_user_feedback` organization-OR query;
- simplified legacy `PaymentService` success shortcut;
- direct SQL writes to domain state from a transport handler.

## 9. MVP simplicity invariant

The API must not expose internal allocation mechanics, retry internals, reconciliation leases, or provider credentials to retailer/vendor clients. External contracts expose business intent and current business state; operational machinery remains internal.
