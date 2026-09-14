# POL User Profile UX Specification — MVP

**Status:** CANONICAL MVP UX CONTRACT  
**Backend source:** `POL_00_PROJECT_CONTROL/USER_PROFILE_AND_PERSONA_MODEL.md`  
**Explicit rule:** Profile UI must adapt to the active persona, but UI visibility is never authorization.

## 1. Global profile architecture

The user opens a single `Profile` entry point.

Top section:
- Avatar
- Display name
- Active organization name
- Active persona / job title
- Profile completion indicator

Primary tabs:

`پروفایل من` · `حساب و امنیت` · `اعلان‌ها` · `محیط کاری`

`محیط کاری` changes according to the active organization membership.

## 2. Retailer UI

### Home shortcuts
`خرید مجدد` · `سبد` · `سفارش‌های من` · `فروشنده‌ها` · `پشتیبانی`

### Profile sections
1. اطلاعات شخصی
2. اطلاعات فروشگاه
3. نحوه سفارش
4. اعلان‌ها
5. آدرس‌های تحویل
6. حساب و امنیت

Retailer owner sees store-management entry points. Retailer staff sees only the operational fields allowed by membership role.

## 3. Vendor owner UI

### Home shortcuts
`سفارش‌ها` · `موجودی` · `قیمت‌ها` · `کاتالوگ` · `تأیید موجودی امروز` · `معرفی مشتری`

### Profile sections
1. اطلاعات شخصی
2. اطلاعات بنکداری
3. نقش کاری
4. مسئولیت انبار
5. تنظیمات اعلان
6. معرفی مشتری / Referral
7. حساب و امنیت

The referral section is MVP and only exposes code/link creation and attribution summary. No reward wallet is shown.

## 4. Vendor staff UI

The first screen is selected by `vendor_membership_profiles.job_function`:

- SALES → retailers / orders / referral
- WAREHOUSE → inventory / daily confirmation
- OPERATIONS → orders / fulfillment
- FINANCE → invoices / payment reconciliation
- STAFF → scoped operations

Profile does not expose unavailable modules merely because the user can technically reach a route.

## 5. Operator UI

Operator profile exposes:
- dashboard scope
- job function
- assigned queue
- notification controls
- account/security

Examples:

`SUPPORT` → support cases + user communications

`FINANCE` → reconciliation + settlement views

`OPS` → orders + vendor operations + delivery

`FIELD` → field tasks + assisted onboarding

`ANALYTICS` → KPI/read-only analytics

## 6. Field Activator UI

Primary sections:
- today's tasks
- retailer/vendor onboarding
- assisted first order
- training
- follow-up
- territory
- activation target

The workflow must prioritize one-handed mobile operation and minimum typing.

## 7. Account & Security

Every persona gets the same security section:

- phone number / verification status
- active sessions
- device list
- revoke other sessions
- last login
- security notices

Authentication state is independent of persona state.

## 8. Notification preferences

Users can control channels where policy allows:
- INBOX
- PUSH
- SMS

Transactional-critical events may remain mandatory according to notification policy. User preferences cannot suppress mandatory legal/operational records.

## 9. Design invariants

- One primary profile entry point.
- Never expose irrelevant fields by persona.
- Do not ask a retailer for vendor-only fields.
- Do not ask a warehouse operator to maintain finance settings.
- Do not bury daily operational actions inside deep settings.
- Profile completion should reduce friction, not become a blocking form unless a field is truly required for the next business operation.
- Use Persian-first labels in MVP.
- Use Tomans for customer-facing money.
- Preserve large touch targets and simple card layouts for older retailer demographics.

## 10. Responsive behavior

### Retailer Android / PWA
Bottom navigation is primary. Profile is a secondary utility surface.

### Vendor Web
Desktop two-column profile: identity/settings on the left, operational persona card on the right.

### Field Activator Mobile
Task-first layout; profile is accessible from the top-right utility control.

### Admin Web
Profile and current operator scope are always visible in the global shell; switching organization/role context requires explicit user action.

## 11. State handling

Profile UI states:
- loading
- complete
- incomplete
- suspended
- no active organization
- active organization selected

Never silently fall back to another organization when active context is missing.
