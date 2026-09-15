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
- `code_hash` (VARCHAR 128): Salted SHA-256 hash of the 5-digit verification code.
- `purpose` (VARCHAR 32): `LOGIN`, `REGISTER`, `ORDER_CONFIRMATION`, `DELIVERY_CONFIRM`.
- `attempts_count` (INT DEFAULT 0).
- `max_attempts` (INT DEFAULT 5).
- `status` (VARCHAR 32): `PENDING`, `VERIFIED`, `EXPIRED`, `BLOCKED`.
- `expires_at` (TIMESTAMPTZ): 120-second validity window.
- `created_at` (TIMESTAMPTZ).

---

## 3. Strict Tenant Isolation Rules

1. **Context Derivation & JWT Claim Governance**:
   - The user's bearer token carries derived/cached authorization claims: `{ "user_id": "...", "org_id": "...", "role": "...", "membership_id": "..." }`.
   - **CRITICAL INVARIANT:** JWT claims are **strictly derived and cached authorization context**, NOT the primary Source of Truth. Middleware and security-sensitive handlers must validate that `user_id` holds an `ACTIVE` membership in `org_id` with the declared `role` in the database.
   - Profile/persona data must NOT be packed into JWT claims as mutable truth.
2. **Resource Scoping**:
   - Retailer endpoints query resources strictly by `retailer.organization_id = token.org_id`.
   - Vendor endpoints query resources strictly by `vendor.organization_id = token.org_id`.
   - Cross-tenant data access attempts return `403 Forbidden` and write an alert to `admin_audit_logs`.
3. **Multi-Store & Multiple Memberships**:
   - If a business owner owns 2 retail stores, each store is registered as an Organization.
   - The user switches tenant context by calling `POST /api/v1/auth/switch-context { "target_org_id": "..." }`. The system validates membership and issues a refreshed access token scoped to the selected organization.

---

## 4. Canonical 5-Layer Profile Hierarchy (D-017)

Per decision `D-017` and `USER_PROFILE_AND_PERSONA_MODEL.md`, the platform enforces a strict 5-layer identity and operational persona model:

```text
Layer 1: users (Authentication credentials, phone number, system audit)
  ↓ 1:1
Layer 2: user_profiles (Universal human identity: full name, avatar, preferred lang)
  ↓ 1:N
Layer 3: organization_memberships (Tenant boundary, role: RETAILER_OWNER, VENDOR_OWNER, etc.)
  ↓ 1:1
Layer 4: membership_profiles (Tenant-scoped operational profile: job title, shift hours)
  ↓ 1:1
Layer 5: Persona Profiles (Domain-specific operational data)
         ├── retailer_profiles (Store name, business license, GPS coords)
         ├── wholesaler_profiles (Depot code, MOV/MOQ rules, warehouse zone)
         └── staff_profiles (Badge ID, supervisor ID, assigned vehicle/terminal)
```

### Authorization vs Personalization Separation Invariant
- **Identity:** Sourced from `user_profiles`.
- **Authorization & RBAC:** Sourced strictly from `organization_memberships.role` and `organizations.org_type`.
- **Operational UI & Personalization:** Sourced from `membership_profiles` and persona profiles (`retailer_profiles`, `wholesaler_profiles`, `staff_profiles`).
- `users.role` is **DEPRECATED** and must never be evaluated for access control.
- Persona profile fields never grant RBAC permissions.

---

## 5. Canonical User Profile API Contracts & Runtime Status

| Endpoint | Method | Purpose | Canonical Request / Payload | Target Response Status | Runtime Status |
|:---|:---:|:---|:---|:---:|:---:|
| `/api/v1/profile` | `GET` | Retrieve authenticated user's universal profile | Header: `Bearer <token>` | `200 OK` (Profile JSON) | `CONTRACT_SPECIFIED` / `PYTHON_SERVICE_VALIDATED` |
| `/api/v1/profile` | `PUT` | Update universal human profile (name, avatar, lang) | `{"full_name": "...", "avatar_url": "..."}` | `200 OK` (Updated Profile) | `CONTRACT_SPECIFIED` / `PYTHON_SERVICE_VALIDATED` |
| `/api/v1/profile/completion` | `GET` | Calculate profile completion percentage & missing fields | Header: `Bearer <token>` | `200 OK` (`{"completion_percentage": 85, "missing_fields": [...]}`) | `CONTRACT_SPECIFIED` / `PYTHON_SERVICE_VALIDATED` |
| `/api/v1/membership/profile` | `GET` / `PUT` | Retrieve or update tenant-scoped membership profile | `{"job_title": "Store Manager", "notification_preferences": {...}}` | `200 OK` | `CONTRACT_SPECIFIED` / `PYTHON_SERVICE_VALIDATED` |
| `/api/v1/profile/context` | `GET` | Full resolved active tenant + persona context for client UI | Header: `Bearer <token>` | `200 OK` (Resolved 5-layer context) | `CONTRACT_SPECIFIED` / `PYTHON_SERVICE_VALIDATED` |

> **Note on Runtime Deployment:** The domain service and database schema for these endpoints are implemented and fully verified via `scripts/user_profiles.py` and `scripts/test_user_profiles.py` on PostgreSQL 18. HTTP gateway routing is marked `CONTRACT_SPECIFIED` / `NOT_YET_DEPLOYED_AT_HTTP` until the HTTP reverse proxy layer is stood up.
