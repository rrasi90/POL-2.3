> **ARCHIVED HISTORICAL EVIDENCE — NOT CURRENT MAINLINE CERTIFICATION**
>
> Source branch: `test/journey-evidence-20261022` (PR #47, observed head `c700232c80cf78dd471ec5b8ca55fcad2b13c414`).
> This copy preserves the dated evidence as originally recorded. Individual evidence rows may refer to earlier SHAs and historical repository trees. None of these PASS/VERIFIED claims certifies current `main` or the integration branch. Re-run the referenced generator/tests on the exact target SHA before using these results for release decisions.
>
---
# POL MVP — Screen / API / test parity

Generated from `mvp/apps/web/src/app/**/page.tsx`, `src/middleware.ts`, the
`/api/v1` literals inside each page, and `mvp/apps/web/tests/*.spec.ts`.
Regenerate with `POL_UPDATE_SCREEN_PARITY=1 python -m pytest scripts/test_screen_parity.py`.

`COVERED` = at least one Playwright spec drives the route; `GAP` = shipped with
no browser test; `STATIC` = intentionally API-free page; `SHELL` = navigation-only
hub (reason recorded).

| Route | Page | Guard (role prefix) | APIs called by the page | Browser specs | Status |
| --- | --- | --- | --- | --- | --- |
| `/` | `mvp/apps/web/src/app/page.tsx` | PUBLIC | — | `delivery-flow.spec.ts` | COVERED |
| `/about` | `mvp/apps/web/src/app/about/page.tsx` | PUBLIC | — | — | STATIC |
| `/admin` | `mvp/apps/web/src/app/(dashboard)/admin/page.tsx` | ADMIN_SUPER (`/admin`) | — | `login.spec.ts` | COVERED |
| `/admin/orgs` | `mvp/apps/web/src/app/(dashboard)/admin/orgs/page.tsx` | ADMIN_SUPER (`/admin`) | `/api/v1/admin/organizations`<br>`/api/v1/admin/organizations/` | — | GAP |
| `/admin/users` | `mvp/apps/web/src/app/(dashboard)/admin/users/page.tsx` | ADMIN_SUPER (`/admin`) | `/api/v1/admin/users`<br>`/api/v1/admin/users/` | `login.spec.ts` | COVERED |
| `/auth/login` | `mvp/apps/web/src/app/auth/login/page.tsx` | AUTHENTICATED (fallback: session required) | `/api/v1/auth/request-otp`<br>`/api/v1/auth/verify-otp` | `login.spec.ts`<br>`navigation-states.spec.ts`<br>`resilience.spec.ts` | COVERED |
| `/contact` | `mvp/apps/web/src/app/contact/page.tsx` | PUBLIC | — | — | STATIC |
| `/dev/components` | `mvp/apps/web/src/app/dev/components/page.tsx` | AUTHENTICATED (fallback: session required) | — | — | STATIC |
| `/field` | `mvp/apps/web/src/app/(dashboard)/field/page.tsx` | FIELD_ACTIVATOR, OPS_AGENT (`/field`) | `/api/v1/field/tasks` | — | GAP |
| `/field/tasks/{id}` | `mvp/apps/web/src/app/(dashboard)/field/tasks/[id]/page.tsx` | FIELD_ACTIVATOR, OPS_AGENT (`/field`) | `/api/v1/field/tasks/${taskId}` | — | GAP |
| `/how` | `mvp/apps/web/src/app/how/page.tsx` | PUBLIC | — | — | STATIC |
| `/legal` | `mvp/apps/web/src/app/legal/page.tsx` | PUBLIC | — | — | STATIC |
| `/notifications` | `mvp/apps/web/src/app/(dashboard)/notifications/page.tsx` | AUTHENTICATED (`/notifications`) | `/api/v1/notifications` | — | GAP |
| `/notifications/preferences` | `mvp/apps/web/src/app/(dashboard)/notifications/preferences/page.tsx` | AUTHENTICATED (`/notifications`) | `/api/v1/notifications/preferences` | — | GAP |
| `/ops` | `mvp/apps/web/src/app/(dashboard)/ops/page.tsx` | OPS_AGENT, ADMIN_SUPER (`/ops`) | `/api/v1/admin/exceptions/dashboard`<br>`/api/v1/orders` | `login.spec.ts` | COVERED |
| `/ops/admin` | `mvp/apps/web/src/app/(dashboard)/ops/admin/page.tsx` | OPS_AGENT, ADMIN_SUPER (`/ops`) | `/api/v1/admin/audit-logs`<br>`/api/v1/admin/exceptions/dashboard` | — | GAP |
| `/ops/analytics` | `mvp/apps/web/src/app/(dashboard)/ops/analytics/page.tsx` | OPS_AGENT, ADMIN_SUPER (`/ops`) | `/api/v1/ops/analytics` | — | GAP |
| `/ops/catalog-candidates` | `mvp/apps/web/src/app/(dashboard)/ops/catalog-candidates/page.tsx` | OPS_AGENT, ADMIN_SUPER (`/ops`) | `/api/v1/admin/product-candidates`<br>`/api/v1/admin/product-candidates/${candidate.candidate_id}` | — | GAP |
| `/ops/notifications` | `mvp/apps/web/src/app/(dashboard)/ops/notifications/page.tsx` | OPS_AGENT, ADMIN_SUPER (`/ops`) | `/api/v1/notifications` | — | GAP |
| `/ops/permissions` | `mvp/apps/web/src/app/(dashboard)/ops/permissions/page.tsx` | OPS_AGENT, ADMIN_SUPER (`/ops`) | `/api/v1/ops/permissions` | — | GAP |
| `/ops/queues` | `mvp/apps/web/src/app/(dashboard)/ops/queues/page.tsx` | OPS_AGENT, ADMIN_SUPER (`/ops`) | `/api/v1/finance/reconciliation`<br>`/api/v1/orders`<br>`/api/v1/support/cases` | — | GAP |
| `/ops/reconciliation` | `mvp/apps/web/src/app/(dashboard)/ops/reconciliation/page.tsx` | OPS_AGENT, ADMIN_SUPER (`/ops`) | `/api/v1/finance/reconciliation`<br>`/api/v1/finance/reconciliation/${id}`<br>`/api/v1/finance/reconciliation/${selectedId}/resolve` | — | GAP |
| `/ops/risk` | `mvp/apps/web/src/app/(dashboard)/ops/risk/page.tsx` | OPS_AGENT, ADMIN_SUPER (`/ops`) | `/api/v1/admin/exceptions/dashboard`<br>`/api/v1/finance/reconciliation` | — | GAP |
| `/ops/rma` | `mvp/apps/web/src/app/(dashboard)/ops/rma/page.tsx` | OPS_AGENT, ADMIN_SUPER (`/ops`) | `/api/v1/ops/returns` | — | GAP |
| `/ops/support` | `mvp/apps/web/src/app/(dashboard)/ops/support/page.tsx` | OPS_AGENT, ADMIN_SUPER (`/ops`) | `/api/v1/support/cases`<br>`/api/v1/support/cases/${id}`<br>`/api/v1/support/cases/${selectedId}/messages`<br>`/api/v1/support/cases/${selectedId}/status` | — | GAP |
| `/ops/{type}/{id}` | `mvp/apps/web/src/app/(dashboard)/ops/[type]/[id]/page.tsx` | OPS_AGENT, ADMIN_SUPER (`/ops`) | `/api/v1/finance/reconciliation/${objectId}`<br>`/api/v1/orders/${idOf(rec.id)}/accept`<br>`/api/v1/orders/${idOf(rec.id)}/reject`<br>`/api/v1/orders/${objectId}`<br>`/api/v1/orders/${objectId}/returns`<br>`/api/v1/orders/${objectId}/timeline`<br>`/api/v1/support/cases/${idOf(rec.id)}`<br>`/api/v1/support/cases/${objectId}` | — | GAP |
| `/pilot` | `mvp/apps/web/src/app/pilot/page.tsx` | PUBLIC | — | — | STATIC |
| `/profile` | `mvp/apps/web/src/app/(dashboard)/profile/page.tsx` | AUTHENTICATED (`/profile`) | `/api/v1/profile`<br>`/api/v1/profile/context` | — | GAP |
| `/retailer` | `mvp/apps/web/src/app/(dashboard)/retailer/page.tsx` | RETAILER_OWNER, RETAILER_STAFF (`/retailer`) | `/api/v1/orders` | `delivery-flow.spec.ts`<br>`login.spec.ts`<br>`navigation-states.spec.ts` | COVERED |
| `/retailer/basket` | `mvp/apps/web/src/app/(dashboard)/retailer/basket/page.tsx` | RETAILER_OWNER, RETAILER_STAFF (`/retailer`) | `/api/v1/baskets`<br>`/api/v1/baskets/${basketId}/items`<br>`/api/v1/baskets/current` | — | GAP |
| `/retailer/catalog` | `mvp/apps/web/src/app/(dashboard)/retailer/catalog/page.tsx` | RETAILER_OWNER, RETAILER_STAFF (`/retailer`) | `/api/v1/catalog/categories`<br>`/api/v1/catalog/search`<br>`/api/v1/search` | — | GAP |
| `/retailer/catalog/{id}` | `mvp/apps/web/src/app/(dashboard)/retailer/catalog/[id]/page.tsx` | RETAILER_OWNER, RETAILER_STAFF (`/retailer`) | `/api/v1/catalog/products/${productId}`<br>`/api/v1/catalog/products/${productId}/compare-inventory`<br>`/api/v1/catalog/products/${productId}/compare-prices`<br>`/api/v1/catalog/products/${productId}/vendors` | — | GAP |
| `/retailer/checkout` | `mvp/apps/web/src/app/(dashboard)/retailer/checkout/page.tsx` | RETAILER_OWNER, RETAILER_STAFF (`/retailer`) | `/api/v1/baskets/${serverBasketId}/allocation-preview`<br>`/api/v1/orders` | — | GAP |
| `/retailer/finance` | `mvp/apps/web/src/app/(dashboard)/retailer/finance/page.tsx` | RETAILER_OWNER, RETAILER_STAFF (`/retailer`) | `/api/v1/invoices` | — | GAP |
| `/retailer/orders` | `mvp/apps/web/src/app/(dashboard)/retailer/orders/page.tsx` | RETAILER_OWNER, RETAILER_STAFF (`/retailer`) | `/api/v1/orders` | `delivery-flow.spec.ts`<br>`login.spec.ts`<br>`navigation-states.spec.ts` | COVERED |
| `/retailer/orders/group/{id}` | `mvp/apps/web/src/app/(dashboard)/retailer/orders/group/[id]/page.tsx` | RETAILER_OWNER, RETAILER_STAFF (`/retailer`) | `/api/v1/orders/group/${groupId}`<br>`/api/v1/orders/group/${groupId}/orders` | — | GAP |
| `/retailer/orders/{id}` | `mvp/apps/web/src/app/(dashboard)/retailer/orders/[id]/page.tsx` | RETAILER_OWNER, RETAILER_STAFF (`/retailer`) | `/api/v1/orders/${orderId}`<br>`/api/v1/orders/${orderId}${path}`<br>`/api/v1/orders/${orderId}/deliver`<br>`/api/v1/orders/${orderId}/delivery`<br>`/api/v1/orders/${orderId}/delivery/proof`<br>`/api/v1/orders/${orderId}/items`<br>`/api/v1/orders/${orderId}/partial-acceptance-proposals/${proposalId}/decline`<br>`/api/v1/orders/${orderId}/timeline` | `delivery-flow.spec.ts` | COVERED |
| `/retailer/orders/{id}/returns` | `mvp/apps/web/src/app/(dashboard)/retailer/orders/[id]/returns/page.tsx` | RETAILER_OWNER, RETAILER_STAFF (`/retailer`) | `/api/v1/orders/${orderId}/disputes`<br>`/api/v1/orders/${orderId}/returns` | — | GAP |
| `/retailer/support` | `mvp/apps/web/src/app/(dashboard)/retailer/support/page.tsx` | RETAILER_OWNER, RETAILER_STAFF (`/retailer`) | `/api/v1/support/cases`<br>`/api/v1/support/cases/${id}`<br>`/api/v1/support/cases/${selectedId}/messages` | — | GAP |
| `/retailer/vendors` | `mvp/apps/web/src/app/(dashboard)/retailer/vendors/page.tsx` | RETAILER_OWNER, RETAILER_STAFF (`/retailer`) | `/api/v1/storefront/vendors` | — | GAP |
| `/retailer/vendors/{id}` | `mvp/apps/web/src/app/(dashboard)/retailer/vendors/[id]/page.tsx` | RETAILER_OWNER, RETAILER_STAFF (`/retailer`) | `/api/v1/storefront/vendors/${vendorId}`<br>`/api/v1/storefront/vendors/${vendorId}/products` | — | GAP |
| `/retailers` | `mvp/apps/web/src/app/retailers/page.tsx` | PUBLIC | — | — | STATIC |
| `/vendor` | `mvp/apps/web/src/app/(dashboard)/vendor/page.tsx` | VENDOR_OWNER, VENDOR_STAFF (`/vendor`) | `/api/v1/orders` | `delivery-flow.spec.ts`<br>`login.spec.ts`<br>`navigation-states.spec.ts` | COVERED |
| `/vendor/catalog` | `mvp/apps/web/src/app/(dashboard)/vendor/catalog/page.tsx` | VENDOR_OWNER, VENDOR_STAFF (`/vendor`) | `/api/v1/catalog/vendors/products` | — | GAP |
| `/vendor/catalog/{id}/prices` | `mvp/apps/web/src/app/(dashboard)/vendor/catalog/[id]/prices/page.tsx` | VENDOR_OWNER, VENDOR_STAFF (`/vendor`) | `/api/v1/catalog/vendors/products/${vendorProductId}/prices`<br>`/api/v1/catalog/vendors/products/${vendorProductId}/prices/current` | — | GAP |
| `/vendor/customers` | `mvp/apps/web/src/app/(dashboard)/vendor/customers/page.tsx` | VENDOR_OWNER, VENDOR_STAFF (`/vendor`) | `/api/v1/vendors/customers${qs}` | — | GAP |
| `/vendor/finance` | `mvp/apps/web/src/app/(dashboard)/vendor/finance/page.tsx` | VENDOR_OWNER, VENDOR_STAFF (`/vendor`) | `/api/v1/invoices`<br>`/api/v1/vendors/settlements` | — | GAP |
| `/vendor/inventory` | `mvp/apps/web/src/app/(dashboard)/vendor/inventory/page.tsx` | VENDOR_OWNER, VENDOR_STAFF (`/vendor`) | `/api/v1/catalog/vendors/products`<br>`/api/v1/catalog/vendors/products/${vpId}/inventory` | — | GAP |
| `/vendor/inventory/daily` | `mvp/apps/web/src/app/(dashboard)/vendor/inventory/daily/page.tsx` | VENDOR_OWNER, VENDOR_STAFF (`/vendor`) | `/api/v1/inventory/daily/${date}/confirm`<br>`/api/v1/inventory/daily/${date}/confirm-with-changes`<br>`/api/v1/inventory/daily/${d}` | — | GAP |
| `/vendor/orders` | `mvp/apps/web/src/app/(dashboard)/vendor/orders/page.tsx` | VENDOR_OWNER, VENDOR_STAFF (`/vendor`) | `/api/v1/orders` | `delivery-flow.spec.ts`<br>`login.spec.ts`<br>`navigation-states.spec.ts` | COVERED |
| `/vendor/orders/{id}` | `mvp/apps/web/src/app/(dashboard)/vendor/orders/[id]/page.tsx` | VENDOR_OWNER, VENDOR_STAFF (`/vendor`) | `/api/v1/orders/${orderId}`<br>`/api/v1/orders/${orderId}${path}`<br>`/api/v1/orders/${orderId}/delivery`<br>`/api/v1/orders/${orderId}/delivery/${target}`<br>`/api/v1/orders/${orderId}/dispatch`<br>`/api/v1/orders/${orderId}/items`<br>`/api/v1/orders/${orderId}/partial-acceptance-proposals`<br>`/api/v1/orders/${orderId}/timeline` | `delivery-flow.spec.ts` | COVERED |
| `/vendor/referrals` | `mvp/apps/web/src/app/(dashboard)/vendor/referrals/page.tsx` | VENDOR_OWNER, VENDOR_STAFF (`/vendor`) | `/api/v1/referrals` | — | GAP |
| `/vendor/settlements` | `mvp/apps/web/src/app/(dashboard)/vendor/settlements/page.tsx` | VENDOR_OWNER, VENDOR_STAFF (`/vendor`) | `/api/v1/invoices`<br>`/api/v1/vendors/settlements` | — | GAP |
| `/vendor/staff` | `mvp/apps/web/src/app/(dashboard)/vendor/staff/page.tsx` | VENDOR_OWNER, VENDOR_STAFF (`/vendor`) | `/api/v1/vendors/staff`<br>`/api/v1/vendors/staff/${member.membership_id}`<br>`/api/v1/vendors/staff/${membershipId}/permissions`<br>`/api/v1/vendors/staff/${selected}/permissions`<br>`/api/v1/vendors/staff/${selected}/permissions/${encodeURIComponent(permission)}/revoke`<br>`/api/v1/vendors/staff/invite` | — | GAP |
| `/vendor/storefront` | `mvp/apps/web/src/app/(dashboard)/vendor/storefront/page.tsx` | VENDOR_OWNER, VENDOR_STAFF (`/vendor`) | `/api/v1/storefront/vendors`<br>`/api/v1/storefront/vendors/${match.id}/products`<br>`/api/v1/storefront/vendors/${v.id}/products` | — | GAP |
| `/vendors` | `mvp/apps/web/src/app/vendors/page.tsx` | PUBLIC | — | — | STATIC |

**Totals:** 56 routes — 11 covered, 37 gap, 8 static, 0 shell.
