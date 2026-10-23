# POL API — served endpoint inventory

Auto-generated from `scripts/api/main.py` OpenAPI (TODO-133). Do not hand-edit:
regenerate with `POL_UPDATE_API_INVENTORY=1 pytest scripts/test_api_inventory.py`.

| Method | Path | Auth | Deprecated | Summary |
| --- | --- | --- | --- | --- |
| `GET` | `/api/v1/admin/audit-logs` | yes |  | List Audit Logs |
| `POST` | `/api/v1/admin/broadcasts` | yes |  | Admin Broadcast Create |
| `POST` | `/api/v1/admin/broadcasts/{broadcast_id}/dispatch` | yes |  | Admin Broadcast Dispatch |
| `POST` | `/api/v1/admin/categories` | yes |  | Admin Category Create |
| `PATCH` | `/api/v1/admin/categories/{category_id}` | yes |  | Admin Category Update |
| `GET` | `/api/v1/admin/exceptions/dashboard` | yes |  | Exceptions Dashboard |
| `GET` | `/api/v1/admin/organizations` | yes |  | Admin Organizations |
| `PATCH` | `/api/v1/admin/organizations/{organization_id}/status` | yes |  | Admin Organization Status |
| `GET` | `/api/v1/admin/product-candidates` | yes |  | Admin Product Candidates |
| `PATCH` | `/api/v1/admin/product-candidates/{candidate_id}` | yes |  | Admin Product Candidate Review |
| `POST` | `/api/v1/admin/sla-overrides` | yes |  | Admin Sla Override |
| `GET` | `/api/v1/admin/users` | yes |  | Admin Users |
| `PATCH` | `/api/v1/admin/users/{user_id}/status` | yes |  | Admin User Status |
| `POST` | `/api/v1/auth/logout-all` | yes |  | Logout All |
| `POST` | `/api/v1/auth/refresh` | yes |  | Refresh |
| `POST` | `/api/v1/auth/request-otp` | yes |  | Request Otp |
| `DELETE` | `/api/v1/auth/sessions/current` | yes |  | Revoke Current Session |
| `DELETE` | `/api/v1/auth/sessions/{session_id}` | yes |  | Revoke Session |
| `POST` | `/api/v1/auth/switch-organization` | yes |  | Switch Organization |
| `POST` | `/api/v1/auth/verify-otp` | yes |  | Verify Otp |
| `POST` | `/api/v1/baskets` | yes |  | Create Basket |
| `GET` | `/api/v1/baskets/current` | yes |  | Current Basket |
| `POST` | `/api/v1/baskets/{basket_id}/allocation-preview` | yes |  | Allocation Preview |
| `POST` | `/api/v1/baskets/{basket_id}/items` | yes |  | Add Basket Item |
| `GET` | `/api/v1/catalog/barcode/lookup` | yes |  | Barcode Lookup |
| `GET` | `/api/v1/catalog/categories` | yes |  | Catalog Categories |
| `GET` | `/api/v1/catalog/products/{product_id}` | yes |  | Catalog Product Detail |
| `GET` | `/api/v1/catalog/products/{product_id}/compare-inventory` | yes |  | Catalog Compare Inventory |
| `GET` | `/api/v1/catalog/products/{product_id}/compare-prices` | yes |  | Catalog Compare Prices |
| `GET` | `/api/v1/catalog/products/{product_id}/vendors` | yes |  | Catalog Product Vendors |
| `GET` | `/api/v1/catalog/search` | yes |  | Catalog Search |
| `GET` | `/api/v1/catalog/vendors/products` | yes |  | Vendor List Products |
| `POST` | `/api/v1/catalog/vendors/products` | yes |  | Vendor Create Product |
| `PATCH` | `/api/v1/catalog/vendors/products/{vendor_product_id}` | yes |  | Vendor Update Product |
| `GET` | `/api/v1/catalog/vendors/products/{vendor_product_id}/inventory` | yes |  | Vendor Inventory Get |
| `PATCH` | `/api/v1/catalog/vendors/products/{vendor_product_id}/inventory` | yes |  | Vendor Inventory Adjust |
| `GET` | `/api/v1/catalog/vendors/products/{vendor_product_id}/prices` | yes |  | Vendor Price History |
| `POST` | `/api/v1/catalog/vendors/products/{vendor_product_id}/prices` | yes |  | Vendor Price Set |
| `GET` | `/api/v1/catalog/vendors/products/{vendor_product_id}/prices/current` | yes |  | Vendor Price Current |
| `GET` | `/api/v1/categories` | yes |  | Categories List |
| `GET` | `/api/v1/disputes/{dispute_id}` | yes |  | Get Dispute |
| `POST` | `/api/v1/disputes/{dispute_id}/close` | yes |  | Close Dispute |
| `POST` | `/api/v1/disputes/{dispute_id}/investigate` | yes |  | Investigate Dispute |
| `PATCH` | `/api/v1/disputes/{dispute_id}/resolve` | yes |  | Resolve Dispute |
| `GET` | `/api/v1/field/tasks` | yes |  | List Field Tasks |
| `POST` | `/api/v1/field/tasks` | yes |  | Create Field Task |
| `GET` | `/api/v1/field/tasks/{task_id}` | yes |  | Get Field Task |
| `PATCH` | `/api/v1/field/tasks/{task_id}` | yes |  | Update Field Task |
| `GET` | `/api/v1/finance/reconciliation` | yes |  | List Reconciliation Cases |
| `GET` | `/api/v1/finance/reconciliation/{case_id}` | yes |  | Get Reconciliation Case |
| `PATCH` | `/api/v1/finance/reconciliation/{case_id}/resolve` | yes |  | Resolve Reconciliation Case |
| `GET` | `/api/v1/finance/refunds` | yes |  | List Refunds |
| `POST` | `/api/v1/finance/refunds/issue` | yes |  | Issue Refund |
| `GET` | `/api/v1/finance/refunds/{refund_id}` | yes |  | Get Refund |
| `POST` | `/api/v1/finance/refunds/{refund_id}/approve` | yes |  | Approve Refund |
| `POST` | `/api/v1/finance/refunds/{refund_id}/complete` | yes |  | Complete Refund |
| `GET` | `/api/v1/inbox/items` | yes |  | List Inbox Items |
| `PATCH` | `/api/v1/inbox/items/read-all` | yes |  | Mark All Inbox Read |
| `PATCH` | `/api/v1/inbox/items/{item_id}/read` | yes |  | Mark Inbox Item Read |
| `GET` | `/api/v1/inventory/daily/{confirmation_date}` | yes |  | Daily Inventory Get |
| `POST` | `/api/v1/inventory/daily/{confirmation_date}/confirm` | yes |  | Daily Inventory Confirm No Changes |
| `POST` | `/api/v1/inventory/daily/{confirmation_date}/confirm-with-changes` | yes |  | Daily Inventory Confirm With Changes |
| `GET` | `/api/v1/invoices` | yes |  | List Invoices |
| `GET` | `/api/v1/invoices/{invoice_id}` | yes |  | Get Invoice |
| `POST` | `/api/v1/media/confirm-upload` | yes |  | Media Confirm Upload |
| `POST` | `/api/v1/media/presigned-url` | yes |  | Media Presigned Url |
| `POST` | `/api/v1/media/resumable/complete` | yes |  | Media Resumable Complete |
| `POST` | `/api/v1/media/resumable/init` | yes |  | Media Resumable Init |
| `GET` | `/api/v1/membership/profile` | yes |  | Get Membership Profile |
| `PUT` | `/api/v1/membership/profile` | yes |  | Update Membership Profile |
| `GET` | `/api/v1/notifications` | yes |  | List Notifications |
| `GET` | `/api/v1/notifications/preferences` | yes |  | Get Notification Preferences |
| `PUT` | `/api/v1/notifications/preferences` | yes |  | Update Notification Preference |
| `GET` | `/api/v1/ops/analytics` | yes |  | Pilot Analytics |
| `GET` | `/api/v1/ops/analytics/weekly` | yes |  | Pilot Analytics Weekly |
| `GET` | `/api/v1/ops/permissions` | yes |  | Permission Catalog |
| `GET` | `/api/v1/ops/permissions/audit` | yes |  | Permission Audit |
| `GET` | `/api/v1/ops/returns` | yes |  | Global Returns |
| `GET` | `/api/v1/orders` | yes |  | List Orders |
| `POST` | `/api/v1/orders` | yes |  | Create Order |
| `GET` | `/api/v1/orders/delivery-exceptions/{exception_id}` | yes |  | Get Delivery Exception |
| `PATCH` | `/api/v1/orders/delivery-exceptions/{exception_id}/escalate` | yes |  | Escalate Delivery Exception |
| `PATCH` | `/api/v1/orders/delivery-exceptions/{exception_id}/resolve` | yes |  | Resolve Delivery Exception |
| `GET` | `/api/v1/orders/group/{order_group_id}` | yes |  | Get Order Group |
| `GET` | `/api/v1/orders/group/{order_group_id}/orders` | yes |  | Get Order Group Child Orders |
| `GET` | `/api/v1/orders/{order_id}` | yes |  | Get Order |
| `POST` | `/api/v1/orders/{order_id}/accept` | yes |  | Accept Order |
| `POST` | `/api/v1/orders/{order_id}/cancel` | yes |  | Cancel Order |
| `POST` | `/api/v1/orders/{order_id}/deliver` | yes |  | Confirm Delivery |
| `GET` | `/api/v1/orders/{order_id}/delivery` | yes |  | Get Delivery |
| `GET` | `/api/v1/orders/{order_id}/delivery-exceptions` | yes |  | List Delivery Exceptions |
| `POST` | `/api/v1/orders/{order_id}/delivery-exceptions` | yes |  | Report Delivery Exception |
| `POST` | `/api/v1/orders/{order_id}/delivery/arrived` | yes |  | Delivery Arrived |
| `POST` | `/api/v1/orders/{order_id}/delivery/failed` | yes |  | Delivery Failed |
| `POST` | `/api/v1/orders/{order_id}/delivery/in-transit` | yes |  | Delivery In Transit |
| `POST` | `/api/v1/orders/{order_id}/delivery/picked-up` | yes |  | Delivery Picked Up |
| `GET` | `/api/v1/orders/{order_id}/delivery/proof` | yes |  | Get Delivery Proof |
| `POST` | `/api/v1/orders/{order_id}/dispatch` | yes |  | Dispatch Order |
| `GET` | `/api/v1/orders/{order_id}/disputes` | yes |  | List Disputes For Order |
| `POST` | `/api/v1/orders/{order_id}/disputes` | yes |  | Open Dispute |
| `GET` | `/api/v1/orders/{order_id}/invoice` | yes |  | Get Invoice For Order |
| `GET` | `/api/v1/orders/{order_id}/items` | yes |  | Get Order Items |
| `GET` | `/api/v1/orders/{order_id}/partial-acceptance-proposals` | yes |  | List Partial Acceptance Proposals |
| `POST` | `/api/v1/orders/{order_id}/partial-acceptance-proposals` | yes |  | Propose Partial Acceptance |
| `POST` | `/api/v1/orders/{order_id}/partial-acceptance-proposals/{proposal_id}/approve` | yes |  | Approve Partial Acceptance |
| `POST` | `/api/v1/orders/{order_id}/partial-acceptance-proposals/{proposal_id}/decline` | yes |  | Decline Partial Acceptance |
| `POST` | `/api/v1/orders/{order_id}/payments/direct-transfer` | yes |  | Record Direct Transfer |
| `GET` | `/api/v1/orders/{order_id}/payments/evidence` | yes |  | List Payment Evidence |
| `POST` | `/api/v1/orders/{order_id}/payments/evidence` | yes |  | Submit Payment Evidence |
| `POST` | `/api/v1/orders/{order_id}/payments/verify` | yes |  | Verify Payment |
| `POST` | `/api/v1/orders/{order_id}/payments/{payment_id}/verify` | yes |  | Verify Payment By Id |
| `POST` | `/api/v1/orders/{order_id}/preparing` | yes |  | Mark Preparing |
| `POST` | `/api/v1/orders/{order_id}/ready` | yes |  | Mark Ready |
| `POST` | `/api/v1/orders/{order_id}/reject` | yes |  | Reject Order |
| `GET` | `/api/v1/orders/{order_id}/returns` | yes |  | List Returns For Order |
| `POST` | `/api/v1/orders/{order_id}/returns` | yes |  | Create Return Request |
| `GET` | `/api/v1/orders/{order_id}/timeline` | yes |  | Get Order Timeline |
| `POST` | `/api/v1/privacy/deletion` | yes |  | Request Account Deletion |
| `POST` | `/api/v1/privacy/export` | yes |  | Request Data Export |
| `POST` | `/api/v1/product-candidates` | yes |  | Create Product Candidate |
| `POST` | `/api/v1/products/match-barcode` | yes |  | Match Barcode |
| `GET` | `/api/v1/products/search` | yes |  | Products Search |
| `GET` | `/api/v1/profile` | yes |  | Get Profile |
| `PUT` | `/api/v1/profile` | yes |  | Update Profile |
| `GET` | `/api/v1/profile/completion` | yes |  | Get Profile Completion |
| `GET` | `/api/v1/profile/context` | yes |  | Get Profile Context |
| `GET` | `/api/v1/referrals` | yes |  | List Referrals |
| `POST` | `/api/v1/referrals` | yes |  | Create Referral |
| `GET` | `/api/v1/referrals/{referral_id}` | yes |  | Get Referral |
| `POST` | `/api/v1/referrals/{referral_id}/redeem` | yes |  | Redeem Referral |
| `GET` | `/api/v1/returns/{return_id}` | yes |  | Get Return |
| `PATCH` | `/api/v1/returns/{return_id}` | yes |  | Transition Return |
| `POST` | `/api/v1/returns/{return_id}/refund/approve` | yes |  | Approve Return Refund |
| `GET` | `/api/v1/search` | yes |  | Unified Search |
| `GET` | `/api/v1/settlements/{settlement_id}` | yes |  | Get Settlement |
| `GET` | `/api/v1/storefront/vendors` | yes |  | Storefront List Vendors |
| `GET` | `/api/v1/storefront/vendors/{vendor_id}` | yes |  | Storefront Vendor Detail |
| `GET` | `/api/v1/storefront/vendors/{vendor_id}/products` | yes |  | Storefront Vendor Products |
| `GET` | `/api/v1/support/cases` | yes |  | List Support Cases |
| `POST` | `/api/v1/support/cases` | yes |  | Create Support Case |
| `GET` | `/api/v1/support/cases/{case_id}` | yes |  | Get Support Case |
| `PATCH` | `/api/v1/support/cases/{case_id}` | yes |  | Transition Support Case Legacy |
| `POST` | `/api/v1/support/cases/{case_id}/assign` | yes |  | Assign Support Case |
| `POST` | `/api/v1/support/cases/{case_id}/messages` | yes |  | Add Support Message |
| `PATCH` | `/api/v1/support/cases/{case_id}/status` | yes |  | Transition Support Case |
| `GET` | `/api/v1/vendors/customers` | yes |  | Vendor Customers |
| `POST` | `/api/v1/vendors/inventory/continuous-scan` | yes |  | Continuous Scan |
| `POST` | `/api/v1/vendors/inventory/publish` | yes |  | Publish Inventory |
| `GET` | `/api/v1/vendors/settlements` | yes |  | List Settlements |
| `GET` | `/api/v1/vendors/staff` | yes |  | Vendor Staff |
| `POST` | `/api/v1/vendors/staff/invite` | yes |  | Vendor Staff Invite |
| `PATCH` | `/api/v1/vendors/staff/{membership_id}` | yes |  | Vendor Staff Update |
| `GET` | `/api/v1/vendors/staff/{membership_id}/permissions` | yes |  | Vendor Staff Permissions |
| `POST` | `/api/v1/vendors/staff/{membership_id}/permissions` | yes |  | Vendor Staff Permission Grant |
| `POST` | `/api/v1/vendors/staff/{membership_id}/permissions/{permission_key}/revoke` | yes |  | Vendor Staff Permission Revoke |
| `GET` | `/healthz` | yes |  | Healthz |
| `GET` | `/readyz` | yes |  | Readyz |

Total operations: 157
