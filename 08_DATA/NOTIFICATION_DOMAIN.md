# POL — Notification Platform & Broadcast Subsystem

**Document ID:** `POL-DATA-NOTIF-001`  
**Governing Authority:** `MASTER_SYSTEM_ARCHITECTURE.md`, `NOTIFICATION_EVENT_MATRIX.md`  
**Target Release:** POL MVP Pilot (Sprint 0)  

---

## 1. Architectural Principles

1. **Transactional Decoupling**: Business transactions commit only the state change and an `outbox_events` row. External communications (SMS / Push) are dispatched asynchronously by background workers. Failure of an SMS provider never aborts order placement.
2. **Inbox SSoT**: Every user-facing notification generates a durable row in `user_inbox_items`. The user inbox is the authoritative repository of alerts and updates.
3. **Admin Broadcast Safety**: Broadcast messages require audience criteria evaluation, a frozen recipient snapshot (`broadcast_recipients`), and authorization before dispatch. Broadcasts route through the exact same notification pipeline as transactional alerts.

```text
                               ┌─────────────────────────┐
                               │ Business DB Transaction │
                               │  (Order, Dispute, etc.) │
                               └────────────┬────────────┘
                                            │
                                  writes to outbox_events
                                            ▼
                               ┌─────────────────────────┐
                               │  Outbox Poller / Worker │
                               └────────────┬────────────┘
                                            │
                               creates notification record
                                            ▼
                               ┌─────────────────────────┐
                               │      notifications      │
                               └──────┬───────────┬──────┘
                                      │           │
                durable in-app record │           │ channel dispatch
                                      ▼           ▼
                           ┌─────────────────┐ ┌─────────────────────────┐
                           │ user_inbox_items│ │ notification_deliveries │
                           └─────────────────┘ └───────┬─────────┬───────┘
                                                       │         │
                                                       ▼         ▼
                                                  [WebPush/FCM] [SMS]
```

---

## 2. Notification Platform Entities

### 2.1 `notifications`
Represents the abstract intent to notify a user regarding a domain event.
- `id` (UUID, PK).
- `user_id` (UUID, FK -> `users.id` ON DELETE CASCADE).
- `organization_id` (UUID, FK -> `organizations.id` ON DELETE SET NULL).
- `event_name` (VARCHAR 64): Corresponds to canonical event in `NOTIFICATION_EVENT_MATRIX.md`.
- `title` (VARCHAR 255).
- `body` (TEXT).
- `data_payload` (JSONB): Metadata, deep links, order IDs.
- `priority` (VARCHAR 16): `LOW`, `NORMAL`, `HIGH`, `CRITICAL`.
- `created_at` (TIMESTAMPTZ).

### 2.2 `notification_deliveries`
Tracks delivery attempts across specific physical communication channels.
- `id` (UUID, PK).
- `notification_id` (UUID, FK -> `notifications.id` ON DELETE CASCADE).
- `channel` (VARCHAR 16): `INBOX`, `PUSH`, `SMS`.
- `provider` (VARCHAR 32): e.g., `KAVENEGAR`, `FIREBASE`, `INTERNAL_INBOX`.
- `provider_message_id` (VARCHAR 128).
- `status` (VARCHAR 16): `PENDING`, `SENT`, `DELIVERED`, `FAILED`, `SKIPPED`.
- `failure_reason` (TEXT).
- `attempt_count` (INT DEFAULT 0).
- `next_retry_at` (TIMESTAMPTZ).
- `delivered_at` (TIMESTAMPTZ).
- `created_at` (TIMESTAMPTZ).

### 2.3 `user_inbox_items`
Persistent user-facing inbox displayed in the mobile and web client headers.
- `id` (UUID, PK).
- `user_id` (UUID, FK -> `users.id` ON DELETE CASCADE).
- `notification_id` (UUID, FK -> `notifications.id` ON DELETE SET NULL).
- `title` (VARCHAR 255).
- `body` (TEXT).
- `category` (VARCHAR 32): `ORDERS`, `PAYMENTS`, `DELIVERY`, `DISPUTES`, `SECURITY`, `SUPPORT`, `SYSTEM`, `MARKETING`.
- `deep_link` (TEXT): Client navigation URI (e.g. `/retailer/orders/123`).
- `is_read` (BOOLEAN DEFAULT FALSE).
- `read_at` (TIMESTAMPTZ).
- `is_archived` (BOOLEAN DEFAULT FALSE).
- `expires_at` (TIMESTAMPTZ).
- `created_at` (TIMESTAMPTZ).

### 2.4 `notification_preferences`
User channel toggles per notification category.
- `id` (UUID, PK).
- `user_id` (UUID, FK -> `users.id` ON DELETE CASCADE).
- `category` (VARCHAR 32).
- `push_enabled` (BOOLEAN DEFAULT TRUE).
- `sms_enabled` (BOOLEAN DEFAULT TRUE).
- *Rule*: Transactional notifications with `priority = 'CRITICAL'` ignore preference toggles.

---

## 3. Admin Broadcast Domain

### 3.1 `broadcast_messages`
Operational announcements created by Platform Operations.
- `id` (UUID, PK).
- `admin_user_id` (UUID, FK -> `users.id`).
- `title` (VARCHAR 255).
- `body` (TEXT).
- `target_criteria` (JSONB): Audience filtering rule (e.g., `{"role": "RETAILER_OWNER", "city": "Ahvaz"}`).
- `status` (VARCHAR 32): `DRAFT`, `SCHEDULED`, `PROCESSING`, `COMPLETED`, `CANCELLED`.
- `recipient_count` (INT DEFAULT 0).
- `approved_by` (UUID, FK -> `users.id`).
- `scheduled_at`, `completed_at`, `created_at` (TIMESTAMPTZ).

### 3.2 `broadcast_recipients`
Immutable snapshot of target users generated at broadcast approval time.
- `id` (UUID, PK).
- `broadcast_id` (UUID, FK -> `broadcast_messages.id` ON DELETE CASCADE).
- `user_id` (UUID, FK -> `users.id`).
- `organization_id` (UUID, FK -> `organizations.id`).
- `notification_id` (UUID, FK -> `notifications.id`).
- `status` (VARCHAR 16): `PENDING`, `SENT`, `FAILED`.
- *Constraint*: `UNIQUE(broadcast_id, user_id)`.
