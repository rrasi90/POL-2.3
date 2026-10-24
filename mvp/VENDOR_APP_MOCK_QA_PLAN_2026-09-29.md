# POL Vendor Android — Mock Data Verification Plan
**Date:** 2026-09-29
**Branch:** `feat/vendor-app-production-20260928-v2`

## Purpose
Verify the Vendor Android application against deterministic mock data before native APK creation or live VPS connection.

## Test accounts
- Vendor Owner: `+989160000001`
- Vendor Staff: `+989160000002`
- Mock OTP: any six numeric digits.

## Pass criteria
A flow is PASS only when:
1. the intended UI state is reachable;
2. the displayed data is internally consistent;
3. the API client uses the canonical route;
4. the correct role can perform the action;
5. an unauthorized role is denied;
6. loading, empty, error and success states remain understandable in Persian;
7. the same state survives refresh/reload inside the current session.

## Core scenarios

### Authentication / identity
- Owner login.
- Staff login.
- Non-vendor role rejected by Vendor app.
- Invalid phone rejected.
- Invalid OTP length rejected.
- Logout clears the session.

### Orders
- Submitted order appears in queue.
- Owner accepts.
- Staff cannot accept/reject/partial-accept.
- Owner partial-acceptance proposal.
- Staff prepares.
- Staff marks ready.
- Owner/staff dispatch.
- Order detail items and timeline remain consistent.

### Inventory / pricing
- Physical/reserved/sellable values render.
- Staff edits physical inventory.
- Staff cannot change price.
- Owner changes price.
- Daily inventory load.
- Daily confirmation with and without changes.

### Finance
- Owner invoice list.
- Owner invoice detail.
- Owner settlement list.
- Owner settlement detail.
- Staff cannot access invoice/settlement data.
- Toman values and dates render correctly.

### Customers / staff / permissions
- Customer search.
- Staff list.
- Owner invite.
- Staff cannot invite.
- Owner opens delegated permissions.
- Owner grants/revokes a permitted delegation.
- Effective permissions reflect the change.

### Storefront
- Owner sees Vendor storefront preview.
- Vendor products show price, packaging and availability.
- Storefront does not create a second data model.

### Barcode / scan
- EXACT match.
- HIGH_CONFIDENCE match.
- AMBIGUOUS match.
- NO_MATCH.
- Candidate creation.
- Continuous-scan submission.
- Inventory publish.
- Actual camera capture remains a device test, not a mock-only claim.

### Support
- Create support case.
- Related order.
- Open case detail.
- Send message.
- Empty subject/message validation.

### Profile / notifications
- Profile load.
- Profile edit.
- Tehran timezone.
- Notification list.
- Preference list from canonical array response.
- Push/SMS preference update.
- Session logout.

### Persian / RTL
- RTL layout remains mirrored.
- Persian text is right-aligned.
- Phone, barcode, SKU and ISO-like identifiers remain readable LTR.
- Persian/Arabic input digits normalize correctly.
- Toman and quantity display use Persian digits.
- Persian calendar output uses Tehran timezone.
- Light and Night preserve the same hierarchy.

## Required result
Do not build an APK until this plan and the executable Mock QA command both pass.

Current executable command:
`npm run qa:mock --workspace @pol/mobile`

Manual app mode:
`EXPO_PUBLIC_DATA_MODE=mock npx expo start`
