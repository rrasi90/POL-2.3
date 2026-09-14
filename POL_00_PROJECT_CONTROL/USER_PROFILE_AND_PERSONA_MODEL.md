# POL Canonical User Profile & Persona Model

**Status:** CANONICAL MVP DESIGN
**Document ID:** `POL-PROFILE-001`
**Rule:** Every POL user MUST have exactly one universal user profile. Every organization membership MUST have exactly one tenant-specific membership profile.

## 1. Why two layers exist

A `User` is a human identity and may participate in more than one organization. A `Membership` is the user's role and context inside one tenant.

Therefore:

```text
User
  └── UserProfile                         # personal identity/preferences
       └── Membership                     # one per organization context
            └── MembershipProfile          # persona/dashboard/work preferences
                 └── Persona Profile       # structured fields for that role
```

`users.role` is legacy and is not authoritative. `organization_memberships.role` remains the RBAC source of truth.

## 2. Universal User Profile — all users

The profile screen always contains:

- Display name
- Profile image/avatar
- Phone number (read-only identity; verification status comes from auth)
- Email (optional)
- Language
- Timezone
- Bio / short description (optional)
- Notification preferences
- Active devices / sessions
- Account/security controls
- Profile completion state

No user sees fields that do not belong to their permissions or persona.

## 3. Retailer persona

### Retailer owner
Primary surface:
- Store identity and business details
- Browse/search/catalog
- Basket
- Orders/history
- Reorder/saved basket when activated
- Vendor referral redemption
- Support/feedback
- Delivery address/location

Profile context:
- Store role = OWNER
- Procurement scope
- Preferred order channel
- Reorder window preference

### Retailer staff
Same operational ordering surfaces, but personal profile emphasizes:
- Store role = STAFF / BUYER / CASHIER / MANAGER
- Assigned procurement scope
- Ordering channel
- Store-level permissions

A staff user must not automatically inherit owner-only organization administration.

## 4. Vendor persona

### Vendor owner
Primary surface:
- Business profile
- Catalog management
- Price management
- Inventory management
- Order acceptance/fulfillment
- Daily inventory confirmation
- Referral creation
- Vendor operational health
- Support/feedback

Profile context:
- Job function = OWNER
- Catalog/inventory/order/referral permissions
- Approval limit where applicable

### Vendor staff
Primary surface is determined by job function:

| Function | Primary UI | Sensitive actions |
|---|---|---|
| SALES | Retailer relationships, orders, referrals | No inventory/accounting admin by default |
| WAREHOUSE | Inventory, daily confirmation, fulfillment | No commercial-admin access by default |
| OPERATIONS | Orders, SLA, dispatch | Operational actions only |
| FINANCE | Payments, reconciliation, invoices | No inventory mutation by default |
| STAFF | Scoped vendor operations | Least-privilege default |

## 5. Operator / admin persona

Operator profiles are role/context-specific:

- ADMIN: global governance and configuration
- OPS: order / vendor / delivery operations
- SUPPORT: cases and customer communication
- FINANCE: payment and settlement operations
- FIELD: activator operations
- ANALYTICS: read-mostly KPI and cohort views

Operator dashboard scope MUST be explicit. A support operator does not automatically receive finance or configuration permissions.

## 6. Field Activator persona

Primary surface:
- Assigned retailer/vendor tasks
- Assisted onboarding
- Assisted first order
- Training
- Follow-up
- Referral/source attribution visibility where authorized

Profile context:
- Territory
- Daily activation target
- Assisted-order capability
- Field task queue

## 7. Manufacturer / future personas

Manufacturer-facing profiles are **NOT MVP**. The universal profile model intentionally supports future organization types without granting manufacturer functionality to MVP users.

Potential future persona: `MANUFACTURER_ANALYST` / manufacturer commercial user.

This document does not activate that capability.

## 8. Personalization rules

The client selects the default home/dashboard from canonical membership context:

```text
role + organization type + membership_profile.preferred_dashboard
```

The client MUST NOT infer authorization from UI visibility. UI personalization is presentation; server-side membership authorization is the security boundary.

## 9. Profile completion

Profile completion is a UX metric, not a permission boundary.

Core completion checks:
- display name
- phone identity
- language
- timezone
- contextual title/job function
- dashboard preference
- onboarding readiness

The system may show a completion percentage, but incomplete profiles do not bypass mandatory operational fields.

## 10. Profile update rules

Users may update their own universal profile.

Membership-specific profile edits require an active membership in the selected organization.

Role/permission changes remain administrative IAM operations and cannot be achieved through profile editing.

## 11. Data ownership

| Data | Source of Truth |
|---|---|
| Authentication identity | `users` + auth/session subsystem |
| Universal human profile | `user_profiles` |
| Tenant membership / RBAC | `organization_memberships` |
| Tenant persona settings | `membership_profiles` |
| Retailer persona fields | `retailer_membership_profiles` |
| Vendor persona fields | `vendor_membership_profiles` |
| Operator persona fields | `operator_membership_profiles` |
| Field persona fields | `field_activator_profiles` |
| Notification channel preference | `notification_preferences` + profile default channel |
| Store/business identity | retailer/vendor organization domain |

## 12. MVP boundary

Active now:
- Universal user profile
- Membership-specific persona context
- Role-appropriate dashboard selection
- Profile completion
- Role-appropriate profile editing

Not activated now:
- social profiles
- public follower graph
- profile-based credit scoring
- AI-generated profiles
- public professional marketplace profiles

Those are future concepts and require a separate canonical decision.
