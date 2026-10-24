# POL — Identity, Organization, Membership & Session Domain

**Document ID:** `POL-DATA-IAM-001`  
**Governing Authority:** `MASTER_SYSTEM_ARCHITECTURE.md`  
**Target Release:** POL MVP Pilot (Sprint 0)  

---

## 1. Overview & Conceptual Model

In the POL B2B FMCG platform, commerce entities (retailer grocery stores and wholesale distribution depots) operate as **Organizations**. Human actors (owners, store managers, warehouse pickers, accountants) operate as **Users** who hold scoped **Memberships** within one or more Organizations.

```text
┌─────────────────────────────────────────────────────────────┐
│                        Organization                         │
│   (Legal entity / Business profile / Tenant Isolation SSoT)  │
└──────────────────────────────┬──────────────────────────────┘
                               │ 1:N
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   Organization Membership                   │
│         (Role, Permissions, Scope, Membership Status)        │
└──────────────────────────────┬──────────────────────────────┘
                               │ N:1
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                            User                             │
│       (Phone Number, Full Name, Verification, Credentials)   │
└──────────────┬──────────────────────────────┬───────────────┘
               │ 1:N                          │ 1:N
               ▼                              ▼
┌──────────────────────────────┐┌─────────────────────────────┐
│         User Device          ││        User Session         │
│(Push Token, OS, Fingerprint) ││(Bearer Token, Tenant Context│
└──────────────────────────────┘└─────────────────────────────┘
```

---

## 2. Core Entities & Relational Schema

### 2.1 `organizations`
Represents a distinct B2B business tenant in the system.
- `id` (UUID, PK): Unique identifier.
- `name` (VARCHAR 255): Legal or commercial trading name.
- `org_type` (VARCHAR 32): `RETAILER`, `VENDOR`, or `OPERATOR`.
- `national_id` (VARCHAR 64): National corporate/commercial registration number.
- `status` (VARCHAR 32): `LEAD`, `PENDING_VERIFICATION`, `ACTIVE`, `SUSPENDED`, `REJECTED`.
- `created_at`, `updated_at` (TIMESTAMPTZ).

### 2.2 `organization_memberships`
Defines an active role and tenancy relationship between a User and an Organization.
- `id` (UUID, PK).
- `organization_id` (UUID, FK -> `organizations.id` ON DELETE CASCADE).
- `user_id` (UUID, FK -> `users.id` ON DELETE CASCADE).
- `role` (VARCHAR 32): `RETAILER_OWNER`, `RETAILER_STAFF`, `VENDOR_OWNER`, `VENDOR_STAFF`, `OPS_AGENT`, `ADMIN_SUPER`, `FIELD_ACTIVATOR`.
- `status` (VARCHAR 32): `INVITED`, `ACTIVE`, `SUSPENDED`, `REVOKED`.
- `is_primary` (BOOLEAN): Default active organization for user upon login.
- `created_at`, `updated_at` (TIMESTAMPTZ).
- *Constraint*: `UNIQUE(organization_id, user_id)` (A user cannot have duplicate memberships in the same organization).

### 2.3 `user_sessions`
Manages active authentication credentials, refresh tokens, and tenant scoping.
- `id` (UUID, PK).
- `user_id` (UUID, FK -> `users.id` ON DELETE CASCADE).
- `active_organization_id` (UUID, FK -> `organizations.id`): Active tenant context for API authorization.
- `token_hash` (VARCHAR 128, UNIQUE): SHA-256 hash of the bearer access token.
- `refresh_token_hash` (VARCHAR 128): SHA-256 hash of the long-lived refresh token.
- `device_id` (UUID, FK -> `user_devices.id`).
- `ip_address` (VARCHAR 45).
- `user_agent` (TEXT).
- `status` (VARCHAR 32): `ACTIVE`, `EXPIRED`, `REVOKED`.
- `expires_at` (TIMESTAMPTZ).
- `created_at`, `last_activity_at` (TIMESTAMPTZ).

### 2.4 `user_devices`
Registers physical hardware devices for push notifications and anti-fraud fingerprinting.
- `id` (UUID, PK).
- `user_id` (UUID, FK -> `users.id` ON DELETE CASCADE).
- `device_fingerprint` (VARCHAR 128): Client hardware hash.
- `device_type` (VARCHAR 32): `ANDROID`, `IOS`, `WEB`.
- `push_token` (TEXT): FCM or WebPush delivery endpoint token.
- `is_active` (BOOLEAN DEFAULT TRUE).
- `created_at`, `updated_at` (TIMESTAMPTZ).
- *Constraint*: `UNIQUE(user_id, device_fingerprint)`.

### 2.5 `otp_challenges`
Tracks SMS one-time password lifecycles and brute-force defenses.
- `id` (UUID, PK).
- `phone_number` (VARCHAR 32).
- `code_hash` (VARCHAR 128): Salted SHA-256 hash of the 6-digit verification code.
- `purpose` (VARCHAR 32): `LOGIN`, `REGISTER`, `ORDER_CONFIRMATION`, `DELIVERY_CONFIRM`.
- `attempts_count` (INT DEFAULT 0).
- `max_attempts` (INT DEFAULT 5).
- `status` (VARCHAR 32): `PENDING`, `VERIFIED`, `EXPIRED`, `BLOCKED`.
- `expires_at` (TIMESTAMPTZ): 120-second validity window.
- `created_at` (TIMESTAMPTZ).

---

## 3. Strict Tenant Isolation Rules

1. **Context Derivation**:
   - The user's bearer token carries a claim: `{ "user_id": "...", "org_id": "...", "role": "..." }`.
   - On every request, middleware validates that `user_id` holds an `ACTIVE` membership in `org_id` with the declared `role`.
2. **Resource Scoping**:
   - Retailer endpoints query resources strictly by `retailer.organization_id = token.org_id`.
   - Vendor endpoints query resources strictly by `vendor.organization_id = token.org_id`.
   - Cross-tenant data access attempts return `403 Forbidden` and write an alert to `admin_audit_logs`.
3. **Multi-Store & Multiple Memberships**:
   - If a business owner owns 2 retail stores, each store is registered as an Organization.
   - The user switches tenant context by calling `POST /api/v1/auth/switch-context { "target_org_id": "..." }`. The system validates membership and issues a refreshed access token scoped to the selected organization.
