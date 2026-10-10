# 03 — Registration & KYC Funnel

The heart of Cartona's B2B model: a **6-step KYC wizard** producing a verified retailer profile, reviewed by ops before activation. Evidence: video frames 028–040 (`use_*`), assets (`registration-screen-background.png`, `account_created.png`, `national_id_*` placeholders), full event set.

---

## 3.0 Funnel order (event-sequenced)

```
Phone → OTP → Personal info → Business type → Location map → Address details
      → Shop OUTSIDE photo → Shop INSIDE photo → Success → (ops review) → Activation
```

Contact escape hatch on every step: call + chat (`register_contact_call_clicked2`, `register_contact_chat_clicked2`).

---

## 3.1 Registration — phone + OTP

Same anatomy as login (phone field, boxed OTP, countdown, resend). Separate events so funnel analytics can split login vs register drop-off: `registration_screen_viewed` → `registration_phone_entered` → `registration_next_clicked` → `registration_otp_viewed` → `registration_otp_submitted` → `registration_otp_verification_result`.
Conflict path: `postreg_existing_account` — "this number already has an account" with action (`postreg_existing_action_clicked`).

## 3.2 Personal info (بيانات شخصية)

- Fields: name (اسمك), phone, [national-ID related fields exist in assets]
- Copy from binary: "سنتصل بك لتأكيد بيانات المستخدم والبدء في التفعيل"
- Events: `register_personal_info_viewed2`, `_changed`, `_error`, `reg_personal_info_next_clicked`

## 3.3 Business type (نوع النشاط)

- **26 pictogram tiles** (flat two-tone navy icons): bakery, cafe, pharmacy, restaurant, market, kiosk, retail, supermarket categories… plus institutional verticals (hospital, school, university, hotel, gym, factory, mosque, charity, company, cinema, playstation, wedding, garden, youth center, warehouse, supplier, army place, clean shop, spice, roaster, bazaar)
- Has **search** within the picker (`reg_business_type_search_used2`) — needed because 26 tiles don't fit one screen
- Single-select; CTA next (`reg_business_type_next_clicked`)
- Event on selection: `register_business_type_selected` → **this value drives catalog/pricing segmentation server-side**

## 3.4 Location map (الموقع على الخريطة)

- Map view (Google Maps primary, OSM fallback) + draggable pin
- Map search (`register_location_search_used2`) + "استخدم موقعي الحالي" auto-position (`reg_location_auto_position_used`)
- Pin-move counted (`register_location_pin_moved`) — implies a confirm step before enabling Next
- Helper copy: "كبّر الخريطة لتحديد الموقع بدقة" (zoom the map for accuracy)

## 3.5 Address details (تفاصيل العنوان)

- Free-text address components + branches: "اختر الفرع اللي عايز تطلب عليه" (multi-branch retailers!)
- Branch images upload with constraints: `RETAILER_BRANCH_IMAGE_MAX_WIDTH/HEIGHT/QUALITY`, `SHOULD_UPLOAD_BRANCH_IMAGES_FROM_GALLERY`
- Events: `register_address_details_viewed/changed/error`, `reg_address_details_next_clicked`

## 3.6 Shop photos — outside then inside (KYC proof)

Two consecutive camera steps, each a full mini-flow:
1. Photo step screen (`reg_outside_photo_viewed` / `reg_inside_photo_viewed`)
2. "Take photo" CTA (`..._take_clicked`) → camera (`..._captured`)
3. Upload lifecycle events (`..._upload_started`, `..._upload_result`)
4. **Help overlay** (`..._help_clicked` → `reg_out_photo_help_viewed`/`reg_in_photo_help_viewed` → `..._help_closed`) — teaches what a valid shop photo looks like
5. **Skippable** (`..._skipped`) — ops can review later; activation is manual anyway
6. Next (`..._next_clicked`)

Frames 028–040 show: form fields with inline errors (red), green progress segments at top, keyboard handling (`adjustResize`), and an address autocomplete row.

## 3.7 Success & activation

- Success screen: illustration (`account_created.png`) + confetti (`flutter_confetti`) + CTA (`register_success_screen_viewed`, `register_success_cta_clicked`, `registration_success`)
- Key copy (from binary): **"دلوقتي إنت جاهز تعمل طلبية، وفريقنا هيتواصل معاك بعد كده لتفعيل الحساب"** — self-serve ordering is allowed, but full activation (credit, etc.) comes after ops review
- Post-login gate for incomplete users: `postlogin_register_required` + `postlogin_register_action_clicked`

## 3.8 What POL must replicate (design logic)

1. **Every step = one screen, one decision.** 6 steps × single-purpose beats one giant form on this audience.
2. **Persistent call/chat escape hatch** on all steps — abandonment rescue.
3. **Photo steps teach before they ask** (help overlay), and are skippable but tracked.
4. **Map step is interactive** (pin drag + search + GPS) and validated by pin-move events.
5. **Business-type drives the catalog** — an Iran version should map this to Iranian retail verticals (سوپرمارکت، نانوایی، داروخانه، رستوران، کافه، ...)
6. **Success celebrates + sets expectation** of a human follow-up call.
