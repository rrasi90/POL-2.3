# POL-2.3 Master Mobile Visual Inventory

Run: 2026-09-28
Branch: visual-capture/baseline-2026-09-28
Base commit: f90fe3117c1881545e32181381ec50a1a6960f9e
Phase: CAPTURE ONLY
Runtime status: BLOCKED_RUNTIME

## Authority and reconciliation

- Canonical screen authority: `mvp/MVP_SCREEN_MATRIX.md`
- Cross-cutting state authority: `mvp/CROSS_CUTTING_STATE_ACTION_MATRIX.md`
- Android parity: `mvp/apps/mobile/src/__tests__/parity.md`
- Current runtime entry: `mvp/apps/mobile/App.tsx`
- Current screen implementation: `mvp/apps/mobile/src/screens/*`
- Theme implementation: `mvp/apps/mobile/src/theme.ts`

## Important current-source discrepancy

The requested protocol names two independent Android products/packages:
- POL Market: `ir.pol.market`
- POL Vendor: `ir.pol.vendor`

The current repository implementation does **not** contain those package IDs. `mvp/apps/mobile/app.json` currently declares one Expo Android package:
`com.anonymous.polmobile`.

This is recorded as a finding only. No source change is made during Capture Phase.

## Inventory status semantics

- PENDING: inventory item discovered, capture not attempted.
- BLOCKED_RUNTIME: capture required but no real Android runtime is available in the current execution environment.
- CAPTURED: permitted only after real Android screenshot + file/dimension/readability/SHA256 verification.
- N/A: only after evidence proves the state is not applicable.

Because the current environment has no `adb` and no Android emulator executable, every required capture below is currently BLOCKED_RUNTIME. No screenshot is claimed as captured.

## Inventory

| ID | App | Role | Screen / Sub-screen | Type | Entry Path | Source | Canonical | Required States | Themes | Runtime Reachability | Screenshot | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| VQA-M-001 | SHARED | PUBLIC_ANON | Login / phone | Auth | App launch | LoginScreen.tsx | SH-AUTH-01 | PHONE_ENTRY | LIGHT/NIGHT | route: login | YES | BLOCKED_RUNTIME |
| VQA-M-002 | SHARED | PUBLIC_ANON | Login / phone validation error | Auth | Login → invalid phone | LoginScreen.tsx | SH-AUTH-01 | PHONE_ERROR | LIGHT/NIGHT | reachable by UI | YES | BLOCKED_RUNTIME |
| VQA-M-003 | SHARED | PUBLIC_ANON | Login / OTP entry | Auth | Login → request OTP | LoginScreen.tsx | SH-AUTH-02 | OTP_ENTRY/INFO | LIGHT/NIGHT | external auth required | YES | BLOCKED_RUNTIME |
| VQA-M-004 | SHARED | PUBLIC_ANON | Login / OTP error | Auth | OTP entry → invalid OTP | LoginScreen.tsx | SH-AUTH-02 | OTP_ERROR | LIGHT/NIGHT | external auth required | YES | BLOCKED_RUNTIME |
| VQA-M-005 | SHARED | PUBLIC_ANON | Login / loading | Auth | OTP request/verify | LoginScreen.tsx | SH-AUTH-01/02 | LOADING | LIGHT/NIGHT | external auth required | YES | BLOCKED_RUNTIME |
| VQA-M-006 | SHARED | AUTHENTICATED | Account / profile | Account | Workspace → account | AccountMobileScreen.tsx | SH-PROFILE-01 | LOADED/FORM/ERROR/SUCCESS | LIGHT/NIGHT | route: account | YES | BLOCKED_RUNTIME |
| VQA-M-007 | SHARED | AUTHENTICATED | Account / notifications | Account | Account → notifications | AccountMobileScreen.tsx | SH-NOTIF-01 | LOADED/EMPTY/ERROR/LOADING | LIGHT/NIGHT | route: account tab | YES | BLOCKED_RUNTIME |
| VQA-M-008 | SHARED | AUTHENTICATED | Account / notification preferences | Account | Account → preferences | AccountMobileScreen.tsx | SH-NOTIF-02 | DEFAULT/SAVED/ERROR/LOADING | LIGHT/NIGHT | route: account tab | YES | BLOCKED_RUNTIME |
| VQA-M-009 | SHARED | AUTHENTICATED | Account / theme light | Theme | Account → روشن | AccountMobileScreen.tsx + theme.ts | CC-30 | LIGHT | LIGHT | runtime toggle | YES | BLOCKED_RUNTIME |
| VQA-M-010 | SHARED | AUTHENTICATED | Account / theme night | Theme | Account → شب | AccountMobileScreen.tsx + theme.ts | CC-30 | NIGHT | NIGHT | runtime toggle | YES | BLOCKED_RUNTIME |
| VQA-M-011 | SHARED | AUTHENTICATED | Account / logout transition | Session | Account → خروج | AccountMobileScreen.tsx | CC-27 | LOADING/ERROR | LIGHT/NIGHT | backend session required | YES | BLOCKED_RUNTIME |
| VQA-M-012 | MARKET | RETAILER_OWNER | Retailer workspace / catalog | Workspace | Auth → retailer | RetailerMobileScreen.tsx | R-02/R-03 | DEFAULT/LOADING/ERROR | LIGHT/NIGHT | role-routed | YES | BLOCKED_RUNTIME |
| VQA-M-013 | MARKET | RETAILER_STAFF | Retailer workspace / catalog | Workspace | Auth → retailer | RetailerMobileScreen.tsx | R-02/R-03 | DEFAULT/LOADING/ERROR | LIGHT/NIGHT | role-routed | YES | BLOCKED_RUNTIME |
| VQA-M-014 | MARKET | RETAILER_* | Catalog / empty | State | Workspace → catalog | RetailerMobileScreen.tsx | R-03 | EMPTY | LIGHT/NIGHT | API/data required | YES | BLOCKED_RUNTIME |
| VQA-M-015 | MARKET | RETAILER_* | Catalog / results | State | Workspace → catalog → search | RetailerMobileScreen.tsx | R-03 | LOADED | LIGHT/NIGHT | API/data required | YES | BLOCKED_RUNTIME |
| VQA-M-016 | MARKET | RETAILER_* | Vendor search | Nested | Catalog → vendors | RetailerMobileScreen.tsx | R-17 | DEFAULT/LOADED/EMPTY/ERROR | LIGHT/NIGHT | API/data required | YES | BLOCKED_RUNTIME |
| VQA-M-017 | MARKET | RETAILER_* | Vendor storefront | Nested | Vendors → storefront | RetailerMobileScreen.tsx | R-18 | LOADED/EMPTY/ERROR | LIGHT/NIGHT | API/data required | YES | BLOCKED_RUNTIME |
| VQA-M-018 | MARKET | RETAILER_* | Basket / empty | Commerce | Workspace → basket | RetailerMobileScreen.tsx | R-06 | EMPTY | LIGHT/NIGHT | API/data required | YES | BLOCKED_RUNTIME |
| VQA-M-019 | MARKET | RETAILER_* | Basket / populated | Commerce | Catalog → add → basket | RetailerMobileScreen.tsx | R-06 | LOADED/MUTATION/ERROR | LIGHT/NIGHT | real API required | YES | BLOCKED_RUNTIME |
| VQA-M-020 | MARKET | RETAILER_* | Allocation review | Commerce | Basket → allocation | RetailerMobileScreen.tsx | R-07 | LOADING/LOADED/ERROR/PARTIAL | LIGHT/NIGHT | real API required | YES | BLOCKED_RUNTIME |
| VQA-M-021 | MARKET | RETAILER_* | Checkout / confirmation | Commerce | Allocation → checkout | RetailerMobileScreen.tsx | R-08 | FORM/CONFIRMATION/ERROR | LIGHT/NIGHT | real API required | YES | BLOCKED_RUNTIME |
| VQA-M-022 | MARKET | RETAILER_* | Orders / history | Commerce | Workspace → orders | RetailerMobileScreen.tsx | R-10 | EMPTY/LOADED/ERROR | LIGHT/NIGHT | API/data required | YES | BLOCKED_RUNTIME |
| VQA-M-023 | MARKET | RETAILER_* | Order detail / normal | Detail | Orders → order | OrderDetailMobileScreen.tsx | R-09B | LOADED | LIGHT/NIGHT | real order required | YES | BLOCKED_RUNTIME |
| VQA-M-024 | MARKET | RETAILER_OWNER | Order detail / partial acceptance review | Detail State | Order detail | OrderDetailMobileScreen.tsx | R-09C | PARTIAL_ACCEPTANCE | LIGHT/NIGHT | real proposal required | YES | BLOCKED_RUNTIME |
| VQA-M-025 | MARKET | RETAILER_* | Order detail / delivery tracking | Detail State | Order detail | OrderDetailMobileScreen.tsx | R-09D | DELIVERY | LIGHT/NIGHT | real delivery required | YES | BLOCKED_RUNTIME |
| VQA-M-026 | MARKET | RETAILER_* | Order detail / handoff-delivery proof | Detail State | Order detail | OrderDetailMobileScreen.tsx | R-09E | HANDOFF/CONFIRMATION | LIGHT/NIGHT | real delivery/POD required | YES | BLOCKED_RUNTIME |
| VQA-M-027 | MARKET | RETAILER_OWNER | Returns / return submission | Nested | Order detail → return | OrderDetailMobileScreen.tsx | R-11 | FORM/ERROR/SUCCESS | LIGHT/NIGHT | real order required | YES | BLOCKED_RUNTIME |
| VQA-M-028 | MARKET | RETAILER_OWNER | Dispute / submission | Nested | Order detail → dispute | OrderDetailMobileScreen.tsx | R-11 | FORM/ERROR/SUCCESS | LIGHT/NIGHT | real order required | YES | BLOCKED_RUNTIME |
| VQA-M-029 | MARKET | RETAILER_* | Support | Nested | Workspace → support | RetailerMobileScreen.tsx / SupportMobileScreen.tsx | R-12 | EMPTY/LOADED/ERROR/FORM | LIGHT/NIGHT | implementation reachable only if wired | YES | BLOCKED_RUNTIME |
| VQA-M-030 | MARKET | RETAILER_OWNER | Financial activity | Finance | Workspace → finance | RetailerMobileScreen.tsx | R-16 | EMPTY/LOADED/ERROR | LIGHT/NIGHT | API/data required | YES | BLOCKED_RUNTIME |
| VQA-M-031 | VENDOR | VENDOR_OWNER | Vendor workspace / orders | Workspace | Auth → vendor | VendorMobileScreen.tsx | V-01/V-02 | DEFAULT/LOADED/EMPTY/ERROR | LIGHT/NIGHT | role-routed | YES | BLOCKED_RUNTIME |
| VQA-M-032 | VENDOR | VENDOR_STAFF | Vendor workspace / orders | Workspace | Auth → vendor | VendorMobileScreen.tsx | V-01/V-02 | DEFAULT/LOADED/EMPTY/ERROR | LIGHT/NIGHT | role-routed | YES | BLOCKED_RUNTIME |
| VQA-M-033 | VENDOR | VENDOR_* | Order detail / normal | Detail | Vendor orders → order | OrderDetailMobileScreen.tsx | V-03 | LOADED | LIGHT/NIGHT | real order required | YES | BLOCKED_RUNTIME |
| VQA-M-034 | VENDOR | VENDOR_* | Order detail / partial acceptance | Detail State | Vendor order → partial | OrderDetailMobileScreen.tsx | V-03 | PARTIAL_ACCEPTANCE | LIGHT/NIGHT | real order required | YES | BLOCKED_RUNTIME |
| VQA-M-035 | VENDOR | VENDOR_* | Order detail / accept-reject | Detail State | Vendor order → action | OrderDetailMobileScreen.tsx | V-03 | ACCEPT/REJECT/ERROR | LIGHT/NIGHT | real order required | YES | BLOCKED_RUNTIME |
| VQA-M-036 | VENDOR | VENDOR_* | Order lifecycle / preparing-ready-dispatch | Detail State | Vendor order lifecycle | OrderDetailMobileScreen.tsx | V-03 | PREPARING/READY/DISPATCH | LIGHT/NIGHT | real order required | YES | BLOCKED_RUNTIME |
| VQA-M-037 | VENDOR | VENDOR_* | Inventory | Workspace tab | Vendor → inventory | VendorMobileScreen.tsx | V-06 | LOADED/EMPTY/ERROR | LIGHT/NIGHT | API/data required | YES | BLOCKED_RUNTIME |
| VQA-M-038 | VENDOR | VENDOR_* | Daily inventory confirmation | Workspace tab | Vendor → daily | VendorMobileScreen.tsx | V-07 | PENDING/CONFIRMED/ERROR | LIGHT/NIGHT | API/data required | YES | BLOCKED_RUNTIME |
| VQA-M-039 | VENDOR | VENDOR_* | Referrals | Workspace tab | Vendor → referrals | VendorMobileScreen.tsx | V-08 | EMPTY/LOADED/ERROR | LIGHT/NIGHT | API/data required | YES | BLOCKED_RUNTIME |
| VQA-M-040 | VENDOR | VENDOR_OWNER | Settlements | Workspace tab | Vendor → settlements | VendorMobileScreen.tsx | V-10 | EMPTY/LOADED/ERROR | LIGHT/NIGHT | API/data required | YES | BLOCKED_RUNTIME |
| VQA-M-041 | VENDOR | VENDOR_OWNER | Financial activity | Workspace tab | Vendor → finance | VendorMobileScreen.tsx | V-17 | EMPTY/LOADED/ERROR | LIGHT/NIGHT | API/data required | YES | BLOCKED_RUNTIME |
| VQA-M-042 | VENDOR | VENDOR_* | Customers | Workspace tab | Vendor → customers | VendorMobileScreen.tsx | V-09 | EMPTY/LOADED/ERROR/SEARCH | LIGHT/NIGHT | API/data required | YES | BLOCKED_RUNTIME |
| VQA-M-043 | VENDOR | VENDOR_OWNER | Staff | Workspace tab | Vendor → staff | VendorMobileScreen.tsx | V-11 | EMPTY/LOADED/INVITE/ERROR | LIGHT/NIGHT | API/data required | YES | BLOCKED_RUNTIME |
| VQA-M-044 | VENDOR | VENDOR_OWNER | Permission editor | Nested | Staff → permissions | VendorMobileScreen.tsx | V-11 | LOADED/EDIT/SAVE/ERROR | LIGHT/NIGHT | API/data required | YES | BLOCKED_RUNTIME |
| VQA-M-045 | OPS | OPS_AGENT | Ops overview | Workspace | Auth → ops | OpsMobileScreen.tsx | O-01 | LOADED/EMPTY/ERROR | LIGHT/NIGHT | API/data required | YES | BLOCKED_RUNTIME |
| VQA-M-046 | OPS | OPS_AGENT | Unified queues | Nested | Ops → queues | OpsMobileScreen.tsx | O-02 | LOADED/EMPTY/ERROR | LIGHT/NIGHT | API/data required | YES | BLOCKED_RUNTIME |
| VQA-M-047 | OPS | OPS_AGENT | Reconciliation | Workspace tab | Ops → reconciliation | OpsMobileScreen.tsx | O-06 | LOADED/EMPTY/ERROR | LIGHT/NIGHT | API/data required | YES | BLOCKED_RUNTIME |
| VQA-M-048 | OPS | OPS_AGENT | Risk / reliability | Workspace tab | Ops → risk | OpsMobileScreen.tsx | O-07 | LOADED/EMPTY/ERROR | LIGHT/NIGHT | API/data required | YES | BLOCKED_RUNTIME |
| VQA-M-049 | OPS | OPS_AGENT | Analytics | Workspace tab | Ops → analytics | OpsMobileScreen.tsx | O-09 | LOADED/EMPTY/ERROR | LIGHT/NIGHT | API/data required | YES | BLOCKED_RUNTIME |
| VQA-M-050 | OPS | OPS_AGENT | Notifications operations | Workspace tab | Ops → notifications | OpsMobileScreen.tsx | O-08 | LOADED/EMPTY/ERROR | LIGHT/NIGHT | API/data required | YES | BLOCKED_RUNTIME |
| VQA-M-051 | OPS | OPS_AGENT | Support workbench | Workspace tab | Ops → support | OpsMobileScreen.tsx / SupportMobileScreen.tsx | O-05 | EMPTY/LOADED/FORM/ERROR | LIGHT/NIGHT | implementation wiring must be runtime-confirmed | YES | BLOCKED_RUNTIME |
| VQA-M-052 | OPS | OPS_AGENT/ADMIN_SUPER | Catalog candidate review | Workspace tab | Ops → candidates | OpsMobileScreen.tsx | OP-13 | EMPTY/LOADED/REVIEW/ERROR | LIGHT/NIGHT | API/data required | YES | BLOCKED_RUNTIME |
| VQA-M-053 | OPS | ADMIN_SUPER | Users | Workspace tab | Ops/Admin → users | OpsMobileScreen.tsx | O-10B | EMPTY/LOADED/EDIT/ERROR | LIGHT/NIGHT | API/data required | YES | BLOCKED_RUNTIME |
| VQA-M-054 | OPS | ADMIN_SUPER | Organizations | Workspace tab | Ops/Admin → organizations | OpsMobileScreen.tsx | O-10B | EMPTY/LOADED/EDIT/ERROR | LIGHT/NIGHT | API/data required | YES | BLOCKED_RUNTIME |
| VQA-M-055 | OPS | ADMIN_SUPER | Audit log | Workspace tab | Ops/Admin → audit | OpsMobileScreen.tsx | O-10 | EMPTY/LOADED/ERROR | LIGHT/NIGHT | API/data required | YES | BLOCKED_RUNTIME |
| VQA-M-056 | FIELD | FIELD_ACTIVATOR | Field task list | Field | Auth → field | FieldTaskListScreen.tsx | F-01 | EMPTY/LOADED/ERROR/LOADING | LIGHT/NIGHT | role-routed | YES | BLOCKED_RUNTIME |
| VQA-M-057 | FIELD | FIELD_ACTIVATOR | Field task detail | Field Detail | Task list → task | FieldTaskDetailScreen.tsx | F-02/F-04 | LOADED/FORM/SAVED/ERROR | LIGHT/NIGHT | real task required | YES | BLOCKED_RUNTIME |
| VQA-M-058 | FIELD | FIELD_ACTIVATOR | Assisted order | Field Commerce | Field → assisted order | AssistedOrderScreen.tsx | F-03 | EMPTY/RESULTS/ERROR/SEARCH | LIGHT/NIGHT | real API/data required | YES | BLOCKED_RUNTIME |
| VQA-M-059 | FIELD | FIELD_ACTIVATOR | Offline banner state | Cross-cutting | Field screen → failed request | OfflineBanner.tsx | F-05 | OFFLINE/RECOVERED | LIGHT/NIGHT | runtime network failure required | YES | BLOCKED_RUNTIME |
| VQA-M-060 | SHARED | AUTHENTICATED | Cold restart / restored session | Session | OS/app restart | App.tsx + api.ts | CC-29 | BOOT/RESTORED/EXPIRED | LIGHT/NIGHT | device runtime required | YES | BLOCKED_RUNTIME |

## Cross-check conclusions

1. The current mobile runtime exposes routes from `App.tsx`: login, field, task, assisted, order-detail, account, retailer workspace, vendor workspace, ops/admin workspace.
2. The source contains `SupportMobileScreen.tsx`, but `App.tsx` does not directly route to it; support appears to be embedded/reached through workspace implementations and must be verified in runtime before it is considered reachable.
3. Barcode R-03B/V-16 has canonical HTTP semantics but the parity document explicitly states that the device camera adapter is not implemented; it is therefore not included as a falsely capturable camera screen.
4. Corporate web-only screens C-01…C-08 are not Android screens and are not included as Android capture items.
5. The screen matrix contains 68 canonical product surfaces, while this inventory isolates the current Android-relevant implementation and its visual states; canonical web-only surfaces are retained in the matrix and are not silently treated as Android captures.
6. Night-theme support exists in source, but the parity document explicitly keeps screen-by-screen Night visual verification as a separate QA gate. This phase therefore requires actual Night captures and does not infer them from source.
