# POL Worker Architecture & Runtime Contract

**Document ID:** `POL-WORKER-001`  
**Status:** ACTIVE / CANONICAL  
**Effective:** 2026-09-18  
**Decisions:** D-015, D-019, D-020

## 1. Canonical execution model

POL uses a **PostgreSQL 18 transactional outbox + Python worker** architecture.

```
HTTP / Domain Transaction
        |
        v
PostgreSQL 18 transaction
  business rows + outbox_events(PENDING)
        |
        v
Python worker process
  SELECT ... FOR UPDATE SKIP LOCKED
        |
        +--> logical notification / reconciliation / timeout processing
        |
        v
PostgreSQL state transition
```

The `outbox_events` row is the durable source of truth. Redis Streams, BullMQ, Kafka and other message brokers are not required for canonical MVP event delivery.

## 2. Worker responsibilities

| Worker | Source | Claim/lease model | Canonical responsibility |
|---|---|---|---|
| `CanonicalIntegrationWorker` | `outbox_events` | PostgreSQL row lock | materialize logical notifications, verify recipient membership, quarantine unsupported events |
| `ProviderDeliveryWorker` | `notification_deliveries` | PostgreSQL lease + `SKIP LOCKED` | call SMS/Push adapters, retry transient failures, persist provider attempts |
| `PaymentReconciliationWorker` | `payment_reconciliation_cases` | PostgreSQL lease + `SKIP LOCKED` | reconcile non-custodial payment evidence |
| `VendorAcceptanceTimeoutWorker` | `orders` | PostgreSQL row lock + `SKIP LOCKED` | enforce persisted vendor-acceptance deadlines, release reservations, notify/penalize/create ops tasks |

Vendor-acceptance timeout execution remains behind the canonical operations/application boundary because it requires explicit ops authorization/context. It is not assigned a fabricated SYSTEM/RBAC identity.

## 3. Concurrency and recovery

Workers must be safe to run concurrently:

- claim work with PostgreSQL `FOR UPDATE SKIP LOCKED`;
- use durable status transitions;
- use explicit leases where provider/payment side effects can outlive one DB transaction;
- use idempotency/dedupe keys where applicable;
- never treat process memory as the source of truth;
- a crashed worker must leave work recoverable from PostgreSQL state.

No Redis queue is required for correctness or recovery.

## 4. Redis boundary

Redis is **not** the canonical event bus or outbox transport.

A future Redis deployment may be used for non-authoritative concerns explicitly permitted by product/engineering decisions (for example cache, rate limiting or session-adjacent acceleration), but loss of Redis must not delete or orphan canonical business events.

## 5. Scheduling / process model

The production deployment must run the Python worker modules as a long-lived worker service or equivalent process supervisor. The process supervisor/scheduler is deployment infrastructure; it does not become a second application runtime.

The repository currently exposes worker classes and transactional contracts. Final deployment wiring, process supervision and infrastructure health checks are Stage 45 scope.

## 6. Explicitly superseded queue wording

The following architecture concepts are **historical / superseded for the canonical MVP worker path**:

- BullMQ as the event queue;
- Redis Streams as the durable outbox transport;
- Node.js as a required worker runtime;
- a Redis queue as the recovery source for domain events.

The durable source remains PostgreSQL 18.

## 7. Verification contract

Any future queue/worker change must preserve:

1. PostgreSQL as durable outbox source of truth;
2. Python as the only production backend runtime;
3. concurrent-safe claiming;
4. provider/payment lease recovery;
5. no business-event dependency on Redis availability.
