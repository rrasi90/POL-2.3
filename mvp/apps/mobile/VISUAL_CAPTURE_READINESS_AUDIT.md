# HISTORICAL / SUPERSEDED AUDIT\n\n> This audit describes the 2026-09-28 capture branch state. It is retained for provenance and must not be used as current repository/configuration evidence. Current authority is the `main` branch HEAD.\n\n# Visual Capture Readiness Audit

## Repository State

Repository: rrasi90/POL-2.3
Main HEAD: f90fe3117c1881545e32181381ec50a1a6960f9e
Capture branch: visual-capture/baseline-2026-09-28

GitHub compare proves the capture branch is based directly on current main:
- merge base = f90fe3117c1881545e32181381ec50a1a6960f9e
- behind main = 0
- ahead of main = 4
- all four commits are Capture documentation/evidence infrastructure only.

Capture-branch commits:
1. daee76a0 — master visual inventory
2. f40ff7cf — capture manifest
3. 9574dcda — capture ledger
4. e103ac1d — evidence README

No mobile source, package configuration, dependency, navigation implementation, or Android native source was changed by this branch.

A local checkout is not mounted in the current environment, so local uncommitted git status and local remotes cannot be independently verified. Remote branch ancestry/diff is verified.

## Runtime Availability

| Component | Status | Evidence |
|---|---|---|
| adb | MISSING | command not found |
| Android Emulator | MISSING | command not found |
| sdkmanager | MISSING | command not found |
| avdmanager | MISSING | command not found |
| ANDROID_HOME | UNSET | empty |
| ANDROID_SDK_ROOT | UNSET | empty |
| JAVA_HOME | UNSET | empty |
| Java | AVAILABLE | OpenJDK 21.0.11 |
| Node | AVAILABLE | v22.16.0 |
| npm | AVAILABLE | 10.9.2 |
| npx | AVAILABLE | 10.9.2 |
| Gradle executable | MISSING | command not found |
| Physical Android device | NOT VERIFIED | adb unavailable |
| AVD | NOT VERIFIED | emulator unavailable |

Classification: ENVIRONMENT_BLOCKER. This is not by itself a Repository defect.

## Historical Runtime Evidence

mvp/LOCAL_EXECUTION_TRACKER.md contains historical device evidence dated 2026-09-24:
- emulator-5554
- AVD POL_API_Emulator
- Pixel 6 / API 35
- Android SDK/platform tools
- rebuilt debug APK com.anonymous.polmobile
- adb install/launch

This is historical evidence only. It does not make a current Android runtime available and is not current Capture evidence.

## Android Toolchain

mvp/apps/mobile/package.json declares:
- Expo ~57.0.24
- React Native 0.86.3
- React 19.2.3

The mobile scripts include:
- android: expo start --android
- build: expo export --platform android --output-dir ./dist

The build script is an Expo Android export, not a native APK build.

There is no committed mvp/apps/mobile/android directory.

Therefore native APK capture requires a native/prebuild route plus Android SDK/device tooling, unless an external native artifact is supplied.

## Package Identity

Current source statically contains:

POL Market expected: ir.pol.market
POL Vendor expected: ir.pol.vendor
Current observed Expo package: com.anonymous.polmobile

Evidence:
mvp/apps/mobile/app.json:20 contains com.anonymous.polmobile.

Repository-wide search found:
- com.anonymous.polmobile: present
- ir.pol.market: absent
- ir.pol.vendor: absent
- POL_APP_VARIANT: absent
- build_android_variant: absent
- index.retailer: absent
- index.vendor: absent

Historical device evidence also identifies com.anonymous.polmobile as the installed debug APK package.

Conclusion:
This is not merely an app.json typo. Current main contains one statically configured Expo application and no source evidence for two independent Market/Vendor Android package identities.

Native package identity of a newly generated build remains RUNTIME_NOT_VERIFIED.

## Expo Configuration

app.json exists and is the only Expo configuration found.

mvp/apps/mobile/app.json:
- name = pol-mobile
- slug = pol-mobile
- version = 1.0.0
- orientation = portrait
- userInterfaceStyle = automatic
- android.package = com.anonymous.polmobile

No app.config.js or app.config.ts exists.
No EAS configuration was found.

Therefore there is no app.json/app.config conflict. The actual problem is the absence of variant configuration.

## Build Architecture

package.json sets main = index.ts.

index.ts registers App using Expo registerRootComponent.

App.tsx is the single application root. It imports:
- AccountMobileScreen
- AssistedOrderScreen
- FieldTaskDetailScreen
- FieldTaskListScreen
- LoginScreen
- OpsMobileScreen
- OrderDetailMobileScreen
- RetailerMobileScreen
- VendorMobileScreen

The route union contains:
- login
- field
- task
- assisted
- workspace
- order-detail
- account

Role routing then selects RetailerMobileScreen, VendorMobileScreen, OpsMobileScreen, or FieldTaskListScreen.

No current mobile:
- AppShell.tsx
- AppRetailer.tsx
- AppVendor.tsx
- index.retailer.ts
- index.vendor.ts

exists in the expected paths.

No build_android_variant script exists.
No POL_APP_VARIANT selector exists.

Therefore current architecture is Single Application + Role Routing, not two independently packaged Android applications.

## Static Navigation

Current route graph:

App
├── no token -> LoginScreen
├── account -> AccountMobileScreen
├── FIELD_ACTIVATOR -> FieldTaskListScreen
│   ├── task -> FieldTaskDetailScreen
│   └── assisted -> AssistedOrderScreen
├── order-detail -> OrderDetailMobileScreen
├── RETAILER_OWNER / RETAILER_STAFF -> RetailerMobileScreen
├── VENDOR_OWNER / VENDOR_STAFF -> VendorMobileScreen
└── OPS_AGENT / ADMIN_SUPER -> OpsMobileScreen

This is statically verified. Runtime reachability is not claimed.

## SupportMobileScreen Trace

The previous Capture Finding that SupportMobileScreen was unreachable is not supported by current source.

RetailerMobileScreen:
- imports SupportMobileScreen
- declares a support tab
- has a support button
- renders SupportMobileScreen when the support tab is active

OpsMobileScreen:
- imports SupportMobileScreen
- declares a support tab
- has a support button
- renders SupportMobileScreen when the support tab is active

Correct classification:

STATICALLY_REACHABLE
RUNTIME_NOT_VERIFIED

It is not an orphan component.

## Role Matrix

Current mobile Role type contains seven roles:
- ADMIN_SUPER
- OPS_AGENT
- FIELD_ACTIVATOR
- VENDOR_OWNER
- VENDOR_STAFF
- RETAILER_OWNER
- RETAILER_STAFF

RetailerMobileScreen statically accepts only RETAILER_OWNER and RETAILER_STAFF.

VendorMobileScreen statically accepts only VENDOR_OWNER and VENDOR_STAFF.

However the root application and Login flow are global. Login normalizes backend roles against the complete seven-role list and App.tsx routes those roles into the corresponding workspace.

Therefore:
- role-level workspace separation exists;
- package-level Market/Vendor separation does not.

## Login Role Boundary

LoginScreen has no Market/Vendor app identity and no package-specific allowedRoles boundary.

The backend supplies the role, normalizeRole validates it against the global role set, and App.tsx routes it.

Static result:
Market roles = RETAILER_OWNER / RETAILER_STAFF at the workspace component boundary.
Vendor roles = VENDOR_OWNER / VENDOR_STAFF at the workspace component boundary.
Ops/Admin/Field are also valid roles in the same application.

## Android Native State

No current mvp/apps/mobile/android directory exists.

Therefore:
PREBUILD_REQUIRED

Current main does not expose committed native:
- applicationId
- namespace
- MainActivity
- MainApplication
- AndroidManifest.xml
- Gradle project

Historical local build evidence must not be mistaken for current committed native source.

## Screen Inventory Reconciliation

Current working Capture Inventory: 60 items.

Static review found no obvious accidental duplicate IDs. The inventory's use of separate visual states and themes is legitimate where source has distinct rendering branches.

However 60 is not yet sufficient to prove complete canonical-to-mobile coverage.

Examples requiring explicit reconciliation:
- canonical R-09 order-group detail is distinct from R-09B child order detail;
- canonical Vendor surfaces such as V-04, V-05, V-12 and V-14 are not represented by dedicated current mobile screens in the parity matrix;
- V-16 barcode continuous scan is explicitly outside the current device camera adapter scope;
- canonical Ops surfaces such as O-03, O-04 and OP-11 require explicit mobile-scope disposition.

These are not automatically declared Android bugs because the current mobile parity document defines a narrower mobile implementation scope.

Classification:
CANONICAL_MOBILE_SCOPE_REQUIRES_RECONCILIATION

Inventory summary:
- current items: 60
- obvious duplicate identities: 0
- clearly stale source references: 0
- statically reachable Support correction: 1
- canonical surfaces needing explicit mobile-scope disposition: multiple
- runtime verified: 0
- runtime blocked: 60

## Visual State Discovery

Current source contains explicit branches for:
- loading
- error
- empty
- success/notice
- forms
- confirmation/action
- partial acceptance
- order lifecycle
- delivery stages
- returns
- disputes
- notification tabs
- preference states
- light theme
- night theme
- offline banner
- role-specific workspace branches

Therefore the final capture matrix must remain state-aware; one screenshot per component is not sufficient.

## Findings

| ID | Category | Severity | Finding | Evidence | Status |
|---|---|---:|---|---|---|
| CAP-AUD-001 | ENVIRONMENT_BLOCKER | P1 | No Android runtime/tooling available in current environment. | adb/emulator/sdkmanager/avdmanager missing; SDK env vars unset. | OPEN |
| CAP-AUD-002 | ARCHITECTURE_CONTRADICTION | P1 | Current mobile is one role-routed app, not two independently packaged Market/Vendor apps. | App.tsx, types.ts, absence of variant entrypoints. | OPEN |
| CAP-AUD-003 | CONFIGURATION_BUG | P1 | Current Expo package is com.anonymous.polmobile; expected Market/Vendor IDs are absent. | app.json:20; repository search. | OPEN |
| CAP-AUD-004 | BUILD_RISK | P1 | No deterministic two-APK build contract exists. | No build_android_variant, POL_APP_VARIANT, native android project, or variant commands. | OPEN |
| CAP-AUD-005 | BUILD_RISK | P1 | Current build script is Expo Android export, not native APK generation. | mvp/apps/mobile/package.json:22. | OPEN |
| CAP-AUD-006 | STATIC_NAVIGATION_GAP | INFO | Previous Support orphan finding was incorrect; Support is statically reachable from Retailer and Ops. | RetailerMobileScreen and OpsMobileScreen imports/tabs/render branches. | RECLASSIFIED |
| CAP-AUD-007 | RUNTIME_UNKNOWN | P1 | Native package identity of a newly generated current build cannot be runtime-confirmed here. | No adb/emulator and no committed native project. | OPEN |
| CAP-AUD-008 | ARCHITECTURE_CONTRADICTION | P1 | Login/app role boundary is global seven-role routing rather than package-specific Market/Vendor authentication. | types.ts:1-8,45-56; App.tsx:116-127; LoginScreen.tsx. | OPEN |
| CAP-AUD-009 | STALE_DOCUMENTATION | P2 | Expected two-app file model is not represented in current main mobile source. | No current mobile AppShell/AppRetailer/AppVendor/variant indexes. | OPEN |
| CAP-AUD-010 | STALE_INVENTORY | P2 | 60-item inventory is not yet proven exhaustive against canonical-to-mobile scope. | MVP_SCREEN_MATRIX vs mobile parity/current screens. | OPEN |
| CAP-AUD-011 | RUNTIME_UNKNOWN | INFO | Historical device evidence exists but is not current runtime evidence. | LOCAL_EXECUTION_TRACKER.md LOCAL-04. | DOCUMENTED |
| CAP-AUD-012 | BRANCH_DIVERGENCE | INFO | Capture branch is exactly four commits ahead and zero behind main. | GitHub compare. | EXPECTED |

## Blockers

Environment:
1. No adb.
2. No Android Emulator.
3. No Android SDK command-line tools.
4. No current device transport.
5. No current AVD in this environment.

Repository/configuration:
1. No two-package Market/Vendor implementation.
2. No Market package ID.
3. No Vendor package ID.
4. No variant selector.
5. No variant build script.
6. No deterministic two-APK commands.
7. No committed native Android project.

## Risks

RISK-01: A single com.anonymous.polmobile APK must not be captured and labeled as both Market and Vendor.

RISK-02: Historical screenshots/device evidence must not be promoted to current Capture evidence.

RISK-03: The 60-item inventory must not be declared exhaustive until canonical mobile scope is reconciled.

RISK-04: A clean environment cannot reproduce two distinct APK identities from current repository scripts.

## Required Actions

### ENVIRONMENT
Provide a real Android runtime, adb, Android SDK platform tools, emulator or physical device, and stable device profile. Do not install anything as part of this audit.

### CONFIG
Decide and document whether POL Market and POL Vendor are truly separate Android applications. If yes, define authoritative package IDs and deterministic variant configuration, then verify resolved Expo config and native applicationId.

### ARCHITECTURE
If two apps are canonical, implement deterministic Market/Vendor entrypoints and package selection. Do not create two labels over one unified APK.

### DOCUMENTATION
Reconcile the 68-screen canonical matrix with actual mobile scope. Explicitly disposition surfaces absent from mobile. Correct the Support finding to STATICALLY_REACHABLE / RUNTIME_NOT_VERIFIED.

### CAPTURE
Only after architecture/configuration and runtime are resolved:
Resolve build identity -> native build -> install -> verify package -> launch -> real navigation -> real state -> screenshot -> SHA256 -> manifest -> ledger.

## Capture Readiness

Current status: NOT_READY_CONFIGURATION_CONTRADICTION

Reason:
There is an environment blocker, but the deeper pre-capture issue is that current main does not implement the requested two-package Market/Vendor Android boundary.

Simply providing an emulator would make runtime execution possible, but would not by itself make Market/Vendor package-specific evidence valid.

No Capture was performed.
Screenshots: 0
UI changes: 0
Architecture changes: 0
Package changes: 0
Navigation changes: 0

## Final Diagnostic Verdict

# NOT_READY_CONFIGURATION_CONTRADICTION

The current environment is blocked, but the repository also has a substantive architecture/configuration contradiction relative to the requested two-app capture protocol.

Environment problem:
No Android runtime/toolchain in this execution environment.

Repository problem:
One unified role-routed Expo mobile app; no two-package configuration; no variant build architecture; no native Android project committed.

Branch problem:
None. Capture branch is cleanly based on current main and contains only four capture documentation/evidence commits.

Documentation/inventory problem:
The previous Support finding was stale/incorrect. The 60-item inventory also needs final canonical-to-mobile scope reconciliation before completeness can be claimed.

Before Capture:
1. Resolve the Market/Vendor product boundary.
2. Establish deterministic package/build identity.
3. Reconcile canonical mobile scope and update the inventory.
4. Provide a real Android runtime.
5. Then begin real capture.

This audit made no product or architecture changes.
