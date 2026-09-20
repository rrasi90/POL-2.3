# POL Role-Based Screen Inventory

**Date:** 2026-09-20  
**Status:** DRAFT

---

## 1. Screen Access Matrix

| Screen | ADMIN_SUPER | OPS_AGENT | FIELD_ACTIVATOR | VENDOR_OWNER | VENDOR_STAFF | RETAILER_OWNER | RETAILER_STAFF |
|--------|:-----------:|:---------:|:---------------:|:------------:|:------------:|:--------------:|:--------------:|
| Login | Y | Y | Y | Y | Y | Y | Y |
| OTP Verify | Y | Y | Y | Y | Y | Y | Y |
| Admin Dashboard | Y | - | - | - | - | - | - |
| User Management | Y | - | - | - | - | - | - |
| Org Management | Y | - | - | - | - | - | - |
| OPS Dashboard | - | Y | - | - | - | - | - |
| Support Cases | - | Y | - | - | - | - | - |
| Reconciliation | - | Y | - | - | - | - | - |
| Finance Overview | - | Y | - | Y | - | - | - |
| Field Tasks | - | Y | Y | - | - | - | - |
| Vendor Dashboard | - | - | - | Y | - | - | - |
| Vendor Catalog | - | - | - | Y | Y | - | - |
| Vendor Orders | - | - | - | Y | Y | - | - |
| Vendor Inventory | - | - | - | Y | Y | - | - |
| Vendor Settlements | - | - | - | Y | - | - | - |
| Vendor Storefront | - | - | - | Y | Y | - | - |
| Retailer Catalog | - | - | - | - | - | Y | Y |
| Retailer Basket | - | - | - | - | - | Y | Y |
| Retailer Checkout | - | - | - | - | - | Y | Y |
| Retailer Orders | - | - | - | - | - | Y | Y |
| Retailer Returns | - | - | - | - | - | Y | - |
| Notifications | Y | Y | Y | Y | Y | Y | Y |
| Profile | Y | Y | Y | Y | Y | Y | Y |

---

## 2. Screen Details Per Role

### 2.1 ADMIN_SUPER (10 screens)
1. **Admin Dashboard** — System KPIs, user count, order volume, revenue
2. **User Management** — List/search/filter users, view/edit user details
3. **Organization Management** — List orgs, view org details, manage memberships
4. **System Configuration** — Feature flags, system settings
5. **Audit Log** — System activity log with filters
6. **Support Cases** — All cases across all orgs
7. **Finance Overview** — Revenue, commissions, settlements
8. **Notifications** — System notifications
9. **Profile** — Personal profile settings
10. **Field Tasks** — All tasks (read-only assignment)

### 2.2 OPS_AGENT (8 screens)
1. **OPS Dashboard** — Open cases, pending tasks, KPIs
2. **Support Cases** — Full CRUD, message, transition
3. **Reconciliation** — Payment disputes, evidence review
4. **Finance Overview** — Transaction list, settlement batches
5. **Field Tasks** — Create, assign, monitor tasks
6. **Notifications** — Operational notifications
7. **Profile** — Personal profile settings
8. **Referrals** — View/manage vendor referrals

### 2.3 FIELD_ACTIVATOR (4 screens)
1. **Task List** — Assigned tasks with status tabs
2. **Task Detail** — Task details, location, notes, photos
3. **Notifications** — Task-related notifications
4. **Profile** — Personal profile settings

### 2.4 VENDOR_OWNER (8 screens)
1. **Vendor Dashboard** — KPIs, recent orders, quick actions
2. **Vendor Catalog** — Full CRUD, pricing, images
3. **Vendor Orders** — Accept/reject/partial acceptance
4. **Vendor Inventory** — Daily confirm, adjustments
5. **Vendor Settlements** — Batch list, detail, export
6. **Vendor Storefront** — Public-facing product display
7. **Notifications** — Order/inventory notifications
8. **Profile** — Personal + org profile settings

### 2.5 VENDOR_STAFF (5 screens)
1. **Vendor Catalog** — Read + limited edit
2. **Vendor Orders** — Accept/reject (limited)
3. **Vendor Inventory** — Daily confirm
4. **Notifications** — Task-related notifications
5. **Profile** — Personal profile settings

### 2.6 RETAILER_OWNER (7 screens)
1. **Catalog Browse** — Search, filter, view products
2. **Shopping Basket** — Manage items, proceed to checkout
3. **Checkout** — Multi-step order placement
4. **Order List** — View all orders with filters
5. **Order Detail** — View order, track delivery
6. **Returns** — Request return, track status
7. **Notifications** — Order/delivery notifications

### 2.7 RETAILER_STAFF (5 screens)
1. **Catalog Browse** — Search, filter, view products
2. **Shopping Basket** — Manage items, proceed to checkout
3. **Checkout** — Multi-step order placement
4. **Order List** — View orders (limited)
5. **Notifications** — Order notifications

---

## 3. Navigation Structure Per Role

### ADMIN_SUPER
```
Dashboard
Users
Organizations
Settings
---
Support
Finance
---
Notifications
Profile
```

### OPS_AGENT
```
Dashboard
Support Cases
Reconciliation
Finance
---
Field Tasks
Referrals
---
Notifications
Profile
```

### FIELD_ACTIVATOR
```
My Tasks
---
Notifications
Profile
```

### VENDOR_OWNER
```
Dashboard
Catalog
Orders
Inventory
Settlements
Storefront
---
Notifications
Profile
```

### VENDOR_STAFF
```
Catalog
Orders
Inventory
---
Notifications
Profile
```

### RETAILER_OWNER
```
Catalog
Basket (with count badge)
Orders
Returns
---
Notifications
Profile
```

### RETAILER_STAFF
```
Catalog
Basket (with count badge)
Orders
---
Notifications
Profile
```

---

## 4. Route Definitions

| Route | Component | Roles | Auth Required |
|-------|-----------|-------|---------------|
| `/auth` | AuthPage | All | No |
| `/` | Dashboard (role-based) | All | Yes |
| `/admin/dashboard` | AdminDashboard | ADMIN_SUPER | Yes |
| `/admin/users` | UserManagement | ADMIN_SUPER | Yes |
| `/admin/orgs` | OrgManagement | ADMIN_SUPER | Yes |
| `/ops/dashboard` | OPSDashboard | OPS_AGENT | Yes |
| `/ops/support` | SupportCases | OPS_AGENT, ADMIN_SUPER | Yes |
| `/ops/reconciliation` | Reconciliation | OPS_AGENT | Yes |
| `/ops/finance` | FinanceOverview | OPS_AGENT, VENDOR_OWNER, ADMIN_SUPER | Yes |
| `/field/tasks` | FieldTasks | FIELD_ACTIVATOR, OPS_AGENT | Yes |
| `/field/tasks/[id]` | FieldTaskDetail | FIELD_ACTIVATOR | Yes |
| `/vendor/dashboard` | VendorDashboard | VENDOR_OWNER | Yes |
| `/vendor/catalog` | VendorCatalog | VENDOR_OWNER, VENDOR_STAFF | Yes |
| `/vendor/orders` | VendorOrders | VENDOR_OWNER, VENDOR_STAFF | Yes |
| `/vendor/inventory` | VendorInventory | VENDOR_OWNER, VENDOR_STAFF | Yes |
| `/vendor/settlements` | VendorSettlements | VENDOR_OWNER | Yes |
| `/vendor/storefront` | VendorStorefront | Public | No |
| `/retailer/catalog` | RetailerCatalog | RETAILER_OWNER, RETAILER_STAFF | Yes |
| `/retailer/basket` | RetailerBasket | RETAILER_OWNER, RETAILER_STAFF | Yes |
| `/retailer/checkout` | RetailerCheckout | RETAILER_OWNER, RETAILER_STAFF | Yes |
| `/retailer/orders` | RetailerOrders | RETAILER_OWNER, RETAILER_STAFF | Yes |
| `/retailer/orders/[id]` | RetailerOrderDetail | RETAILER_OWNER, RETAILER_STAFF | Yes |
| `/retailer/returns` | RetailerReturns | RETAILER_OWNER | Yes |
| `/notifications` | NotificationCenter | All | Yes |
| `/profile` | ProfileSettings | All | Yes |
