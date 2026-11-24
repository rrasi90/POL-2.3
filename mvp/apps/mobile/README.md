# POL MVP Mobile

Phase 3 Expo client under the monorepo. This app uses the backend as the sole
source of business rules and keeps the mobile API client local to the app.

## Current implementation

- Backend-derived role routing for all seven canonical roles.
- 6-digit OTP authentication (D-018); new delivery OTPs are six digits (D-029).
- Field-first F-01…F-05 with request-failure offline state + healthz retry.
- Retailer foundation: catalog search, basket, allocation preview, checkout with Idempotency-Key, orders and order detail.
- Vendor foundation: order queue/actions, partial-acceptance proposal, inventory, daily confirmation, settlements and order detail.
- Ops/Admin foundation: exceptions dashboard, queue read model, reconciliation and ADMIN audit read.
- Central Light/Night palette foundation.
- No Driver App (D-023).

## Verification

CI workflow: .github/workflows/pol-mvp-mobile.yml

Required checks:
1. npm ci from mvp/
2. mobile typecheck
3. Expo public config validation
4. Expo Android export

Mobile status remains IMPLEMENTED until the evidence is recorded in parity.md and
MVP_SCREEN_MATRIX.md. Minimum three Phase-3 QA cycles are required.

## Explicit remaining work

- Remaining mobile scope is primarily device/runtime-specific barcode camera verification, screen-by-screen visual verification, and any future explicitly approved vendor storefront-write contract. Vendor support, customers and delegated staff access are included in the current Vendor workspace.
- D-028 barcode lookup/match, candidate creation, continuous-scan and publish contracts are wired; native camera permission/capture and physical scanner behavior remain device/runtime verification gates.
- Screen-by-screen Night-theme visual verification remains a device/runtime QA gate.
- Live basket → allocation → checkout e2e remains a local-environment execution task.
- `npm run qa:pre-apk --workspace @pol/mobile` is the deterministic source/config gate immediately before native APK build.


## Android installable builds

### Mock-data verification stage

Use the same Vendor UI and API client with deterministic in-memory mock data before connecting to the VPS:

```bash
EXPO_PUBLIC_DATA_MODE=mock npx expo start
```

Mock mode covers Vendor OTP login, role boundary, orders/lifecycle, inventory, pricing, daily confirmation, finance, customers, staff/delegated permissions, storefront, barcode lookup/candidate flow, continuous scan/publish, invoice/settlement detail, support, profile and notifications. For manual testing, use an Owner phone such as +989160000001 or a Staff phone ending in 0002; the Mock OTP accepts any four numeric digits. Mock mode is for QA only and is rejected by the Vendor release build gate.

The mobile source produces two independent Android products from the same canonical client:

- **POL Market / پل بازار** — retailer roles only (`RETAILER_OWNER`, `RETAILER_STAFF`), package `ir.pol.market`.
- **POL Vendor / پل بنکدار** — vendor roles only (`VENDOR_OWNER`, `VENDOR_STAFF`), package `ir.pol.vendor`.

Build locally from `mvp/apps/mobile`:

```bash
npm run build:apk:retailer
npm run build:apk:vendor
```

Outputs:

- `dist/retailer/POL-Market.apk`
- `dist/vendor/POL-Vendor.apk`

The Android build uses Expo prebuild + native Gradle `assembleRelease`; Expo export alone is not treated as an installable APK. Vendor release builds require `EXPO_PUBLIC_API_BASE_URL` with HTTPS and reject emulator/loopback URLs and mock data mode.

The role boundary is enforced both at the mobile shell and at OTP-login handling. Backend authorization remains the canonical security boundary.

For live staging connectivity checks, set `EXPO_PUBLIC_API_BASE_URL` and run `npm run qa:live`. The existing VPS was observed serving `http://85.198.50.29`; that HTTP endpoint is for non-production staging verification only. A TLS/HTTPS endpoint is required before producing a Vendor release APK.
