# POL — Retailer Screen-by-Screen Design Specification

## 1. R-01 Onboarding

### R-01A Welcome
Frame: 390×844.
Structure top→bottom:
1. compact logo area
2. headline: «خرید عمده، ساده‌تر و سریع‌تر»
3. 1–2 line value explanation
4. simple product/distribution visual, not a marketing carousel
5. primary CTA: «شروع کنیم»
6. secondary support/help link

Do not collect business data here.

### R-01B Phone
- page title
- phone field
- short explanation
- primary CTA «ادامه»
- security reassurance

Focus stays on the phone field after entry; error copy is specific.

### R-01C OTP
- title
- masked phone reference
- 6-digit OTP field
- resend countdown
- change number
- primary action only when needed

### R-01D Shop context
Collect the minimum data required to establish shop context.
Use a short form, not a profile questionnaire.

### R-01E First-use guidance
Use 2–3 coachmarks maximum. Teach only the first action loop.

### R-01F First assisted order
Use a guided compact ordering surface; do not send the retailer into a full tutorial.

### R-01G Activation success
Show:
- activation confirmed
- next operational action
- optional «رفتن به خرید»

## 2. R-02 Home

Goal: help retailer decide what to do now.

Top:
- app bar
- active shop/context
- notification/support actions

Main:
1. Today queue: orders or exceptions requiring attention.
2. Continue ordering: recent/saved list.
3. Reorder strip: 3–5 highly relevant recent products/orders.
4. Search entry: large, obvious, always available.
5. Category shortcuts: only high-frequency categories.

Bottom: persistent navigation.

Do not use a large hero carousel.
Do not show six KPI cards.

Primary action hierarchy:
Search / Continue purchase > open order attention > reorder.

States:
- new user: onboarding continuation
- normal
- no previous purchases
- open exception
- degraded network

## 3. R-03 Search / Catalog

Top:
- back
- large search field
- scanner/SKU action if supported

Below:
- recent searches
- category/filter chips
- result count when useful

Result row:
`image | product name | pack | MOQ | price | availability | vendor | quantity`

Mobile: vertical compact row.
Desktop later: table/list hybrid.

No-result state:
- repeat query guidance
- spelling/alternative suggestion if available
- category fallback
- remove filters action

## 4. R-04 Product Detail

Top:
- product image
- name
- pack/unit

Commercial block:
- price
- MOQ/MOV
- availability/freshness
- vendor

Action area:
- quantity stepper
- primary «افزودن به سبد»
- secondary save/reorder

Vendor comparison opens as a sheet rather than navigating away when practical.

Do not hide MOQ or availability below long descriptions.

## 5. R-05 Vendor Comparison

Use a compact comparison sheet/page.

Each vendor row:
- vendor name
- price
- pack
- MOQ/MOV
- availability confidence
- relevant constraint
- select action

No visual ranking badge unless a documented canonical ranking algorithm exists.

Show neutral comparison, not «بهترین فروشنده».

## 6. R-06 Basket

Header:
- title
- item count
- edit action

Body:
- BasketLine repeated
- changed/unavailable warning inline
- vendor grouping only after allocation

Footer/sticky summary:
- subtotal/total
- key commercial caveat
- primary «ادامه بررسی»

Empty basket:
- concise explanation
- search CTA
- recent purchases if available

## 7. R-07 Allocation Review

Purpose statement at top:
«سبد شما بین چند بنکدار تقسیم شده است.»

For each allocation group:
- vendor identity
- assigned lines
- subtotal
- constraints
- delivery/fulfillment note where known

Changed lines:
- old value
- new value
- reason
- action

Primary CTA: «تأیید و ادامه».
Secondary: edit basket.

Avoid exposing internal AllocationPlan terminology.

## 8. R-08 Checkout / Confirmation

Use one review-first page rather than a long wizard.

Sections:
1. delivery/contact
2. order groups
3. direct settlement method
4. evidence instruction if applicable
5. final total
6. terms/important note
7. submit

CTA must include verb: «ثبت سفارش».

Before submit, show the exact total and any unresolved exception.

## 9. R-09 Order Group

Parent card:
- group number
- overall state
- total
- vendors
- exception indicator

Child order cards:
- vendor
- state
- items
- accepted/rejected quantities
- delivery/POD
- settlement evidence
- issue entry

Timeline uses text + icon + status label, not color alone.

## 10. R-10 Reorder

Entry points:
- order detail
- history
- saved list

Show a diff when historical commercial values changed:
«قیمت این کالا از خرید قبلی تغییر کرده است.»

Primary action: add all compatible items.
Allow item-level adjustment before final checkout.

## 11. R-11 Returns / Disputes

Use stepped disclosure:
1. select order
2. select issue type
3. select items/quantity
4. evidence
5. submit
6. tracking

Issue type labels must be concrete:
- کالای ناقص
- کالای اشتباه
- آسیب‌دیدگی
- اختلاف تعداد
- مشکل دیگر

Do not ask for a narrative before structured facts.

## 12. R-12 Support

Top:
- search/help suggestions
- create case

Case creation:
- subject/category
- order link when relevant
- message
- attachment
- submit

Case detail:
- state
- timeline
- last response
- next expected action
- reopen when closed and policy allows

## 13. R-13 Account

Sections:
- shop identity
- addresses
- notification preferences
- active organization/context
- security/sessions
- help
- usage guide

Do not mix high-frequency buying actions into account settings.

## 14. Retailer visual consistency rules

- Search field is visually persistent and recognizable.
- Quantity stepper uses one geometry everywhere.
- Price always aligns consistently and uses tabular numerals where supported.
- MOQ appears next to pack/price, not buried.
- Availability uses label + icon/state, not color alone.
- Primary CTA is usually one per screen.
- Use 16 px mobile page padding unless an edge-to-edge media area is intentional.
- Avoid 9–11 px UI text.
