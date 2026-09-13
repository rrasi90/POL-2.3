# POL — Notification Event Matrix & User Inbox Policy

**Document ID:** POL-MATRIX-NOTIF-001  
**Governing Documents:** MASTER_SYSTEM_ARCHITECTURE.md, NOTIFICATION_DOMAIN.md  
**Target Release:** POL MVP Pilot (Sprint 0)  

---

## 1. Overview & Policy Rules

This matrix governs all notifications produced across the POL platform. Every business domain event is evaluated against this matrix to determine:
1. **Target Recipient(s)**: Specific organization roles receiving the event.
2. **User Inbox Persistence**: Permanent storage in user_inbox_items (Yes/No, read status, expiration).
3. **Push Channel**: Delivery via WebPush / FCM for urgent updates.
4. **SMS Channel**: Delivery via SMS gateway (Transactional or Fallback).
5. **Urgency / Priority**: CRITICAL (bypass opt-out), HIGH, NORMAL, LOW.
6. **Actionable / Deep Link**: Navigation route in mobile or web app.

---

## 2. Notification Event Matrix

| Domain | Event Name | Target Recipient | Priority | Inbox | Push | SMS Policy | Deep Link / Action | Opt-Out Allowed |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Auth & Security** | AUTH_OTP_REQUESTED | User Mobile | CRITICAL | No | No | Immediate SMS | N/A (Enter code) | No |
| **Auth & Security** | AUTH_SESSION_REVOKED | User | HIGH | Yes | Yes | If suspicious | /auth/login | No |
| **Auth & Security** | AUTH_SUSPICIOUS_LOGIN | User | CRITICAL | Yes | Yes | Immediate SMS | /security/sessions | No |
| **Commerce / Order** | ORDER_GROUP_SUBMITTED | Retailer Owner/Staff | HIGH | Yes | Yes | Transactional SMS | /retailer/orders/{group_id} | No |
| **Commerce / Order** | ORDER_SUBMITTED | Vendor Owner/Staff | CRITICAL | Yes | Yes | Immediate SMS Alert | /vendor/orders/{order_id} | No |
| **Commerce / Order** | ORDER_ACCEPTED | Retailer Owner/Staff | HIGH | Yes | Yes | Optional SMS | /retailer/orders/{order_id} | Yes |
| **Commerce / Order** | ORDER_REJECTED | Retailer Owner/Staff | HIGH | Yes | Yes | Immediate SMS Alert | /retailer/orders/{order_id} | No |
| **Commerce / Order** | ORDER_TIMEOUT_EXPIRED | Retailer Owner/Staff | HIGH | Yes | Yes | Immediate SMS Alert | /retailer/orders/{order_id} | No |
| **Commerce / Order** | ORDER_TIMEOUT_WARNING | Vendor Owner/Staff | CRITICAL | Yes | Yes | Immediate SMS Alert | /vendor/orders/{order_id} | No |
| **Fulfillment** | ORDER_DISPATCHED | Retailer Owner/Staff | HIGH | Yes | Yes | Optional SMS | /retailer/orders/{order_id}/tracking | Yes |
| **Fulfillment** | DELIVERY_OTP_GENERATED | Retailer Owner | CRITICAL | Yes | Yes | Immediate SMS OTP | /retailer/orders/{order_id}/otp | No |
| **Fulfillment** | ORDER_DELIVERED | Retailer, Vendor | NORMAL | Yes | Yes | Optional SMS | /orders/{order_id} | Yes |
| **Direct Payment** | PAYMENT_PROOF_SUBMITTED| Vendor Owner | HIGH | Yes | Yes | Optional SMS | /vendor/payments/{payment_id} | Yes |
| **Direct Payment** | PAYMENT_VERIFIED | Retailer Owner | HIGH | Yes | Yes | Optional SMS | /retailer/payments/{payment_id} | Yes |
| **Direct Payment** | PAYMENT_REJECTED | Retailer Owner | CRITICAL | Yes | Yes | Immediate SMS Alert | /retailer/payments/{payment_id} | No |
| **Disputes** | DISPUTE_OPENED | Vendor, Admin | CRITICAL | Yes | Yes | Immediate SMS Alert | /disputes/{dispute_id} | No |
| **Disputes** | DISPUTE_EVIDENCE_ADDED| Opposite Party, Admin | NORMAL | Yes | Yes | No SMS | /disputes/{dispute_id} | Yes |
| **Disputes** | DISPUTE_RESOLVED | Retailer, Vendor | HIGH | Yes | Yes | Immediate SMS Alert | /disputes/{dispute_id} | No |
| **Support** | SUPPORT_CASE_OPENED | User, Ops Support | NORMAL | Yes | No | No SMS | /support/cases/{case_id} | Yes |
| **Support** | SUPPORT_MESSAGE_RECEIVED| Case Participants | HIGH | Yes | Yes | No SMS | /support/cases/{case_id} | Yes |
| **Support** | SUPPORT_CASE_RESOLVED | User | NORMAL | Yes | Yes | No SMS | /support/cases/{case_id} | Yes |
| **Catalog** | CANDIDATE_SKU_APPROVED | Submitting Vendor | NORMAL | Yes | Yes | No SMS | /vendor/catalog | Yes |
| **Catalog** | CANDIDATE_SKU_REJECTED | Submitting Vendor | NORMAL | Yes | Yes | No SMS | /vendor/catalog | Yes |
| **Vendor Ops** | VENDOR_ONBOARDING_APPROVED| Vendor Owner | HIGH | Yes | Yes | Immediate SMS | /vendor/dashboard | No |
| **Vendor Ops** | VENDOR_SUSPENDED | Vendor Owner | CRITICAL | Yes | Yes | Immediate SMS Alert | /vendor/account-status | No |
| **Field Ops** | FIELD_TASK_ASSIGNED | Field Activator | NORMAL | Yes | Yes | No SMS | /field/tasks/{task_id} | Yes |
| **Broadcast** | ADMIN_BROADCAST_MESSAGE| Target Audience Cohort| NORMAL | Yes | Yes | If Urgent Broadcast | /inbox/{message_id} | Yes |

---

## 3. Inbox Lifecycle & Retention Policies

1. **Transactional Notifications**: Retained for 90 days. Unread items show active badge count.
2. **Promotional & Broadcast Messages**: Retained for 30 days. Auto-archive on expiration.
3. **Read / Unread State**: Tracked individually per user via user_inbox_items.is_read and 
ead_at.
4. **Failure Decoupling**: If SMS gateway or Push service returns 5xx error, user_inbox_items is already safely committed. A delivery retry record is scheduled without rolling back application state.
