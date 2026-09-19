# Vendor Acceptance UI Contract — Stage 21
**Date:** 2026-09-19  
**Status:** ACTIVE  
**Macro:** M-04  
**Decision Reference:** D-014 (checkout flow), D-018 (SLA/auth)

---

## 1. Order Status State Machine

### 1.1 All Valid Statuses

| Status | Meaning | Who Sets It |
|--------|---------|-------------|
| `SUBMITTED` | Order created, awaiting vendor response | System (checkout) |
| `ACCEPTED` | Vendor fully accepted all items | Vendor |
| `PARTIALLY_ACCEPTED` | Vendor proposed shortage, retailer approved | Retailer (approval) |
| `REJECTED` | Vendor rejected entire order | Vendor |
| `CANCELLED` | Order cancelled (timeout or mutual) | System (timeout) or User |
| `PREPARING` | Warehouse picking in progress | Vendor (future) |
| `READY` | Items packed, invoice printed | Vendor (future) |
| `DISPATCHED` | Handed to carrier | Vendor |
| `DELIVERED` | Confirmed via OTP at delivery | System (OTP) |

### 1.2 Valid Transitions

```
SUBMITTED ──accept──> ACCEPTED ──prepare──> PREPARING ──ready──> READY ──dispatch──> DISPATCHED ──deliver──> DELIVERED
    │                                                                              
    ├──reject──> REJECTED                                                          
    │                                                                              
    ├──propose shortage──> SUBMITTED + PENDING proposal                            
    │     ├──retailer approve──> PARTIALLY_ACCEPTED ──prepare──> PREPARING ──> ... 
    │     └──retailer decline──> SUBMITTED (unchanged)                             
    │                                                                              
    └──timeout (2h)──> CANCELLED                                                   
```

---

## 2. SLA Timer Contract

### 2.1 Vendor Acceptance SLA

| Parameter | Value | Source |
|-----------|-------|--------|
| SLA Duration | **2.0 working hours** (120 minutes) | `sla_calendar.py:12` |
| Working Hours | 08:00–18:00 Tehran time | `sla_calendar.py:9-10` |
| Working Days | Saturday–Thursday (Friday excluded) | `sla_calendar.py:16` |
| Holidays | Loaded from `operational_holidays` table | `sla_calendar.py:74-86` |
| Timezone | `Asia/Tehran` | `sla_calendar.py:8` |

### 2.2 Deadline Calculation

At checkout, `vendor_acceptance_deadline_at` is set:
```
deadline = calculate_sla_deadline(submitted_at, duration_hours=2.0, holidays=holidays)
```

The calculation:
1. Convert `submitted_at` to Tehran timezone
2. Walk forward through working time only (08:00–18:00, Sat–Thu, non-holiday)
3. Skip nights (18:00–08:00), Fridays, and holidays
4. Return the timestamp when 2.0 working hours are exhausted

### 2.3 Deadline Response Header

The API response MUST include the deadline for UI countdown display:

```json
{
  "success": true,
  "data": {
    "id": "...",
    "order_status": "SUBMITTED",
    "vendor_acceptance_deadline_at": "2026-09-19T12:30:00Z"
  }
}
```

### 2.4 UI Countdown Behavior

- **Vendor view**: Show countdown timer from `vendor_acceptance_deadline_at`
- **Retailer view**: Show "Waiting for vendor response" with elapsed time
- When deadline passes: order status changes to `CANCELLED` automatically
- UI must poll or subscribe for real-time status updates

---

## 3. Vendor Actions by Status

### 3.1 SUBMITTED — Vendor Can Act

| Action | Button Label | API Endpoint | Guard |
|--------|-------------|--------------|-------|
| Accept full order | "پذیرش کامل" | `POST /orders/{id}/accept` | No PENDING proposal |
| Reject order | "رد سفارش" | `POST /orders/{id}/reject` | No PENDING proposal, non-empty reason |
| Propose partial | "پیشنهاد کسری" | `POST /orders/{id}/partial-acceptance-proposals` | At least one shortage item |

### 3.2 SUBMITTED — Vendor Cannot Act While Proposal Pending

If a PENDING proposal exists, accept/reject are **disabled**. The vendor must wait for retailer decision.

### 3.3 Other Statuses — Vendor View Only

| Status | Vendor Can See | Available Actions |
|--------|---------------|-------------------|
| `ACCEPTED` | Yes | View order details |
| `PARTIALLY_ACCEPTED` | Yes | View order details |
| `REJECTED` | Yes | View (terminal) |
| `CANCELLED` | Yes | View (terminal) |
| `PREPARING` | Yes | View (future: mark ready) |
| `READY` | Yes | View (future: dispatch) |
| `DISPATCHED` | Yes | View (waiting for delivery) |
| `DELIVERED` | Yes | View (terminal) |

---

## 4. Retailer Actions by Status

### 4.1 SUBMITTED — With Pending Proposal

| Action | Button Label | API Endpoint |
|--------|-------------|--------------|
| Approve proposal | "تأیید پیشنهاد" | `POST /orders/{id}/partial-acceptance-proposals/{pid}/approve` |
| Decline proposal | "رد پیشنهاد" | `POST /orders/{id}/partial-acceptance-proposals/{pid}/decline` |

### 4.2 SUBMITTED — Without Pending Proposal

No actions. Retailer waits for vendor response.

### 4.3 Other Statuses — Retailer View Only

Same as vendor: view only for all non-terminal statuses.

---

## 5. Partial Acceptance Sub-Protocol

### 5.1 Proposal Lifecycle

```
Vendor creates proposal (PENDING)
    ├── Retailer approves → order becomes PARTIALLY_ACCEPTED, proposal → ACCEPTED
    └── Retailer declines  → order stays SUBMITTED, proposal → DECLINED
```

### 5.2 Proposal Structure

```json
{
  "proposal_id": "uuid",
  "order_id": "uuid",
  "vendor_id": "uuid",
  "status": "PENDING",
  "items": [
    {
      "order_item_id": "uuid",
      "product_name": "Product Name",
      "ordered_quantity": 10,
      "accepted_quantity": 7,
      "reason": "موجودی انبار کافی نیست"
    }
  ],
  "created_at": "2026-09-19T10:00:00Z"
}
```

### 5.3 Single Pending Proposal Rule

Only ONE PENDING proposal per order is allowed. Creating a second proposal while one is PENDING returns an error.

---

## 6. Timeout Behavior

### 6.1 Automatic Cancellation

When `vendor_acceptance_deadline_at` passes and order is still `SUBMITTED`:
1. Order status → `CANCELLED`
2. `cancellation_reason` → `VENDOR_TIMEOUT`
3. All ACTIVE reservations → `RELEASED`
4. PENDING proposals → `DECLINED` with reason `VENDOR_TIMEOUT`
5. Vendor reliability event: `ACCEPTANCE_LATE` with impact `-0.25`
6. Notification sent to retailer

### 6.2 UI After Timeout

- Vendor sees: "سفارش لغو شد (مهلت پاسخ‌گویی تمام شده)"
- Retailer sees: "سفارش توسط سیستم لغو شد (عدم پاسخ فروشنده)"

---

## 7. Dispute Status (Orthogonal)

Dispute state is tracked separately via `dispute_status` column:

| Value | Meaning |
|-------|---------|
| `NONE` | No dispute |
| `OPEN` | Dispute raised |
| `UNDER_REVIEW` | Under admin review |
| `RESOLVED_ADJUSTED` | Resolved with adjustment |
| `RESOLVED_REJECTED` | Resolved, dispute rejected |
| `CLOSED` | Dispute closed |

Dispute status is independent of order status. An order can have `order_status=DELIVERED` with `dispute_status=OPEN`.

---

## 8. Outbox Events for UI Notifications

| Event | Trigger | Recipients | Key Payload Fields |
|-------|---------|------------|-------------------|
| `ORDER_SUBMITTED` | Checkout | Vendor | order_id, order_number |
| `ORDER_ACCEPTED` | Full accept | Retailer | order_id, order_status |
| `ORDER_REJECTED` | Full reject | Retailer | order_id, rejection_reason |
| `ORDER_PARTIAL_ACCEPTANCE_PROPOSED` | Proposal created | Retailer | order_id, proposal_id, items |
| `ORDER_PARTIALLY_ACCEPTED` | Proposal approved | Both | order_id, order_status |
| `ORDER_PARTIAL_ACCEPTANCE_DECLINED` | Proposal declined | Vendor | order_id, decision_reason |
| `ORDER_CANCELLED` | Timeout | Retailer | order_id, cancellation_reason |

---

## 9. Route/Status Matrix

| Route | Method | Required Status | Actor |
|-------|--------|----------------|-------|
| `/orders` | GET | Any | Retailer/Vendor (filtered) |
| `/orders/{id}` | GET | Any | Owner (retailer or vendor) |
| `/orders/{id}/items` | GET | Any | Owner |
| `/orders/{id}/timeline` | GET | Any | Owner |
| `/orders/group/{id}` | GET | Any | Owner |
| `/orders/group/{id}/orders` | GET | Any | Owner |
| `/orders` | POST | — | Retailer (checkout) |
| `/orders/{id}/accept` | POST | SUBMITTED | Vendor, no PENDING proposal |
| `/orders/{id}/reject` | POST | SUBMITTED | Vendor, no PENDING proposal, reason required |
| `/orders/{id}/partial-acceptance-proposals` | POST | SUBMITTED | Vendor |
| `/orders/{id}/partial-acceptance-proposals/{pid}/approve` | POST | SUBMITTED | Retailer |
| `/orders/{id}/partial-acceptance-proposals/{pid}/decline` | POST | SUBMITTED | Retailer |

---

## 10. Frontend State Contract Rules

1. **Never fabricate states**: Only display statuses from the DB CHECK constraint
2. **Never fabricate transitions**: Only call endpoints that the state machine allows
3. **Show SLA countdown** only when `order_status == 'SUBMITTED'` and `vendor_acceptance_deadline_at` is set
4. **Disable action buttons** when pre-conditions are not met (e.g., PENDING proposal blocks accept/reject)
5. **Optimistic UI**: After a successful mutation, update local state immediately; reconcile on next poll
6. **Error states**: Show backend error messages verbatim (do not invent user-friendly overrides for business errors)
7. **Terminal states**: `REJECTED`, `CANCELLED`, `DELIVERED` have no further actions
