# POL Integration Contracts

**Status:** CANONICAL ENGINEERING CONTRACT
**Scope:** Sprint 0 / MVP foundation
**Principle:** Every cross-domain workflow must have one authoritative write path, explicit ownership, an atomic state boundary, and a recoverable asynchronous side-effect path.

## 1. Canonical communication boundary

```text
Domain transaction
  -> domain event / outbox record (same DB transaction)
  -> asynchronous worker
  -> notification / external integration
  -> delivery attempt
  -> provider result / audit
```

A domain service must not require an external provider to succeed before its database transaction can commit.

## 2. Canonical commerce route

```text
Retailer
 -> Organization/Membership
 -> Catalog / Vendor Product
 -> Basket
 -> AllocationPlan
 -> CanonicalCheckoutGateway
 -> allocation integrity validation
 -> checkout revalidation
 -> atomic inventory reservation
 -> OrderGroup
 -> child Orders
 -> Vendor acceptance/rejection
 -> Fulfillment
 -> POD
 -> Payment evidence/reconciliation
 -> Settlement
 -> Dispute / Return / Refund / Adjustment
 -> completion
```

### Invariants

- Basket ownership is checked against retailer identity.
- Allocation plan must match the current basket version and remain within TTL.
- Every basket line must map exactly once in MVP.
- Requested quantity, MOQ, vendor MOV and current price are revalidated at checkout.
- Available inventory = physical - reserved; requested quantity may not exceed availability.
- Inventory rows are locked immediately before reservation.
- Checkout replay is deterministic by idempotency key and retailer ownership.
- OrderGroup is an aggregate projection, never the source of a child-order lifecycle.
- Dispute status is orthogonal to operational order status.
- Payment remains NON_CUSTODIAL_DIRECT during MVP.

## 3. Inventory intelligence route

```text
Vendor responsible person
 -> daily confirmation
 -> PENDING / CONFIRMED_NO_CHANGES / CONFIRMED_WITH_CHANGES / MISSED
 -> outbox reminder
 -> notification delivery
 -> inventory freshness/confidence
 -> allocation eligibility
 -> observed fulfillment outcomes
 -> vendor reliability ledger
```

Normal path must remain one primary user action: confirm today's inventory.

## 4. Feedback route

```text
Any role
 -> FeedbackSubmission
 -> automatic safe context
 -> outbox event
 -> admin inbox
 -> triage / assignment / response
 -> user notification
 -> closure
```

Feedback is not Support and is not Dispute.

## 5. Notification route

Every logical notification must have an explicit user + organization target unless the event is explicitly an admin broadcast. A logical notification automatically enters `outbox_events` through the DB delivery trigger; delivery attempts are tracked separately in `notification_deliveries`.

Critical notifications are non-opt-out. Transactional messages follow the policy matrix. SMS is fallback, not the primary application write path.

## 6. Idempotency contract

The following operations must be safely replayable:

| Operation | Idempotency boundary |
|---|---|
| Checkout | `order_groups.checkout_idempotency_key` + retailer binding |
| Inventory reminder | event/date/vendor dedupe key |
| Notification delivery | `notification_id + channel` |
| Payment reconciliation | open-case uniqueness per payment |
| Refund | one active refund per dispute |
| Support assignment | one active assignment per case |
| Daily inventory confirmation | one confirmation per vendor/date |

## 7. Error semantics

A stale price, insufficient stock, expired allocation, invalid tenant, exceeded vendor capacity, or closed operating window is a **recoverable business rejection**, not an infrastructure failure.

The API/UI layer must surface the smallest actionable explanation and allow the user to recover without losing unrelated basket state.

## 8. Research-derived operating stance

- Cartona validates the value of an asset-light marketplace that digitizes existing supplier/retailer operations rather than replacing them. [TechCrunch, 2021](https://techcrunch.com/2021/09/21/cartona-gets-4-5m-pre-series-a-to-connect-retailers-with-suppliers-in-egypt/)
- Cartona explicitly positions ease-of-use and a single digital marketplace as part of the value proposition. [Cartona](https://cartona.com/)
- Wasoko demonstrates that ordering convenience and reliable last-mile operations are critical for high-frequency FMCG replenishment, including lightweight mobile/SMS ordering. [Wasoko](https://wasoko.com/press/empowering-informal-retailers-the-impact-of-wasokos-last-mile-delivery-network/)
- MaxAB shows the importance of an integrated procurement + logistics + customer-support operating model. [TechCrunch, 2019](https://techcrunch.com/2019/09/25/maxab-raises-6m-seed-round-to-optimize-egypts-b2b-grocery-markets/)
- B2B commerce systems benefit from location-specific terms, catalogs and quantity rules rather than treating a company as a single undifferentiated buyer. [Shopify B2B](https://help.shopify.com/en/manual/b2b/companies-and-customers/creating-companies), [Shopify quantity rules](https://help.shopify.com/en/manual/b2b/catalogs/quantity-pricing)

These are patterns to adapt, not reasons to expand the Ahvaz MVP into credit, escrow, asset-owning logistics or heavy procurement.
