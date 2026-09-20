# ماتریس نقش‌ها و سطوح دسترسی (Roles & Permissions Matrix - RBAC)
## پروژه پُل (POL) — B2B FMCG Platform
**شناسه سند:** `PROD-SPEC-004`  
**وضعیت:** مصوب و نهایی  
**نسخه:** ۲.۰ (تثبیت‌شده برای Platform Core و Sprint 0)  
**تاریخ به‌روزرسانی:** سپتامبر ۲۰۲۶  

---

### ۱. معماری کنترل دسترسی مبتنی بر نقش و سازمان (Organization-Scoped RBAC)

در پلتفرم پُل، امنیت اطلاعات تجاری، حریم خصوصی قیمت‌ها و صحت تراکنش‌های مالی از طریق مدل **کنترل دسترسی مبتنی بر نقش سازمانی (Organization-Scoped RBAC)** تضمین می‌شود:
1. **سازمان (`organizations`) به عنوان مرز اصلی مستأجری (Tenant Boundary):** هر سوپرمارکت، بنکدار، باربری یا تیم اپراتوری پُل یک نهاد سازمانی مستقل است.
2. **عضویت کاربر در سازمان (`memberships`):** کاربران هویت مستقل دارند و می‌توانند عضو یک یا چند سازمان باشند (مثلاً صاحب چند سوپرمارکت). دسترسی‌ها و نقش‌ها بر اساس عضویت در سازمان فعال ارزیابی می‌شوند.
3. **تفکیک کامل داده‌های تجاری:** هیچ سازمان بنکداری دسترسی به موجودی، قیمت‌های تخفیفی یا فاکتورهای بنکدار دیگر ندارد. سوپرمارکت‌ها نیز صرفاً به اسناد سازمان خود دسترسی دارند.

---

### ۲. تعریف سازمان‌ها و نقش‌های کاربری در سیستم (Organizations & Roles)

#### ۲.۱. انواع سازمان (Organization Types)
* `RETAILER`: خرده‌فروشان و سوپرمارکت‌ها.
* `VENDOR`: بنکداران، عمده‌فروشان و توزیع‌کنندگان مستقر در شهرک بنکداران اهواز.
* `OPERATOR`: سازمان داخلی پلتفرم پُل جهت مدیریت، پشتیبانی، تطبیق کاتالوگ و داوری.

> **نکته معماری مدل لجستیک (Option A Fulfillment):** در فاز MVP، باربری‌ها و رانندگان فاقد ساختار سازمان مستقل (`CARRIER`) در جدول `organizations` هستند. هویت راننده توسط بنکدار/باربری احراز شده و مشخصات راننده (`driver_name`, `driver_phone`, `vehicle_plate`) مستقیماً به عنوان متادیتای تحویل در جدول `deliveries` ثبت می‌شود.

#### ۲.۲. مرجعیت احراز صلاحیت و وضعیت فیلد `users.role` (Deprecation Notice)
> **مهم — منسوخ شدن مرجعیت `users.role`:** فیلد `users.role` در سطح کاربر از نظر احراز دسترسی و مرجعیت تصمیم‌گیری **کاملاً منسوخ (Deprecated)** است و هیچ‌گونه حق دسترسی ایجاد نمی‌کند. تنها منبع حقیقت (SSoT) برای بررسی دسترسی‌ها، نقش فعال کاربر در جدول `organization_memberships.role` منطبق با `user_sessions.active_organization_id` است.

#### ۲.۳. نقش‌های سیستمی و سازمانی کانونیکال (System & Membership Roles)
1. **مدیر ارشد پلتفرم (`ADMIN_SUPER` — با نام قدیمی `SUPER_ADMIN`):**
   * دسترسی سراسری نامحدود به مدیریت سیستم، تنظیمات پلتفرم، پارامترهای کارمزد، ایجاد مدیران، و لاگ‌های امنیتی تغییرات حساس (`admin_audit_logs`). منحصراً متعلق به سازمان نوع `OPERATOR`.
2. **مدیر عملیات و پشتیبانی (`OPS_AGENT` — با نام قدیمی `OPS_ADMIN`):**
   * نظارت بر جریان زنده سفارش‌ها، داوری دعاوی تجاری (`disputes`)، تخصیص تیکت‌های پشتیبانی (`support_cases`)، تایید کاندیداهای کاتالوگ، لغو اضطراری سفارش‌ها و مدیریت اعلانات سراسری (`broadcasts`). منحصراً متعلق به سازمان نوع `OPERATOR`.
3. **فعال‌ساز میدانی پُل (`FIELD_ACTIVATOR`):**
   * نماینده میدانی پُل در شهرک بنکداران و بازار اهواز. مسئول Onboarding حضوری مغازه‌داران، عکاسی مدارک، آموزش ثبت سفارش، پیگیری فیزیکی تاخیر بنکداران و بازرسی حضوری در موارد اختلاف بار. منحصراً متعلق به سازمان نوع `OPERATOR`.
4. **مالک سازمان بنکداری (`VENDOR_OWNER`):**
   * صاحب حساب بنکداری. مدیریت موجودی و قیمت‌گذاری کالاها، تایید یا رد سفارش‌های ورودی، معرفی و عزل پرسنل انبار، تایید رسیدهای پرداخت و دریافت فاکتورهای رسمی. منحصراً متعلق به سازمان نوع `VENDOR`.
5. **کاربر انبار بنکداری (`VENDOR_STAFF`):**
   * پرسنل انبار بنکدار. مشاهده سفارش‌های تاییدشده، پرینت لیست جمع‌آوری بار (Pick List)، ثبت کسری بار حین بسته‌بندی، تغییر وضعیت به `DISPATCHED` با ثبت مشخصات راننده وانت. منحصراً متعلق به سازمان نوع `VENDOR`.
6. **مالک سازمان سوپرمارکت (`RETAILER_OWNER`):**
   * خریدار نهایی B2B. جستجو در کاتالوگ، مقایسه قیمت، افزودن به سبد، ثبت نهایی سفارش، تایید تحویل کالا با کد OTP، ثبت مغایرت تجاری، ایجاد تیکت پشتیبانی و دعوت از شاگردان مغازه. منحصراً متعلق به سازمان نوع `RETAILER`.
7. **شاگرد / پرسنل سوپرمارکت (`RETAILER_STAFF`):**
   * پیگیری سفارش‌های جاری پای مغازه، تایید تحویل کالا در مقصد، و ثبت موارد کسری یا آسیب‌دیدگی ظاهری. منحصراً متعلق به سازمان نوع `RETAILER`.

#### ۲.۴. قواعد تغییرناپذیر انطباق نقش با نوع سازمان (Role Invariants — DB Enforced)
بر اساس قانون شماره ۱۵ معماری و تریگر دیتابیس `trg_enforce_org_membership_role_invariant`:
* انتساب نقش‌های خرده‌فروشی (`RETAILER_*`) صرفاً در سازمان‌های نوع `RETAILER` مجاز است.
* انتساب نقش‌های بنکداری (`VENDOR_*`) صرفاً در سازمان‌های نوع `VENDOR` مجاز است.
* انتساب نقش‌های پلتفرم و عملیات (`ADMIN_SUPER`, `OPS_AGENT`, `FIELD_ACTIVATOR`) صرفاً در سازمان‌های نوع `OPERATOR` مجاز است.
* هرگونه تخطی از این قاعده مستقیماً توسط موتور PostgreSQL با خطای یکپارچگی رد می‌شود.

---

### ۳. جدول ماتریس جامع دسترسی‌ها (Permissions Matrix)

| منبع / عملیات در سیستم | `SUPER_ADMIN` | `OPS_ADMIN` | `FIELD_ACTIVATOR` | `VENDOR_OWNER` | `VENDOR_STAFF` | `RETAILER_OWNER` | `RETAILER_STAFF` |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **کاتالوگ و قیمت‌های عمومی بازار** | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |
| **تعریف و ویرایش قیمت اقلام انبار خود** | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| **به‌روزرسانی موجودی و اسکن سریع بارکد** | ✅ | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ |
| **ایجاد سبد خرید و افزایش نسخه** | ❌ | ❌ | ✅ (کمکی) | ❌ | ❌ | ✅ | ❌ |
| **ثبت نهایی سفارش (Checkout)** | ❌ | ❌ | ✅ (به نیابت) | ❌ | ❌ | ✅ | ❌ |
| **تأیید یا رد سفارش ورودی (SLA)** | ✅ | ✅ (اضطراری) | ❌ | ✅ | ❌ | ❌ | ❌ |
| **ثبت کسری در پذیرش (`PARTIAL_ACCEPT`)** | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| **بسته‌بندی و ارسال بار با مشخصات راننده** | ✅ | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ |
| **تأیید تحویل سفارش با کد OTP** | ✅ | ✅ | ✅ (حضوری) | ❌ | ❌ | ✅ | ✅ |
| **ثبت فیش واریز / روش پرداخت مستقیم** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| **تأیید رسید پرداخت مستقیم بنکداری** | ✅ | ✅ (نظارتی) | ❌ | ✅ | ❌ | ❌ | ❌ |
| **ثبت مغایرت رسمی تجاری (`disputes`)** | ❌ | ❌ | ✅ (کمکی) | ❌ | ❌ | ✅ | ❌ |
| **داوری و صدور حکم نهایی حل اختلاف** | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **ایجاد تیکت پشتیبانی (`support_cases`)** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **پاسخ و ارجاع تیکت‌های پشتیبانی** | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **ایجاد و انتشار اعلانات همگانی (`broadcasts`)** | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **تمدید زمان مجاز پذیرش (SLA Override)** | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **مشاهده و دانلود فاکتور رسمی** | ✅ | ✅ | ❌ | ✅ (فاکتور خود) | ❌ | ✅ (فاکتور خود) | ❌ |
| **مدیریت اعضای سازمان (`memberships`)** | ✅ | ❌ | ❌ | ✅ (سازمان خود) | ❌ | ✅ (سازمان خود) | ❌ |
| **مشاهده لاگ‌های امنیتی ادمین (`audit_logs`)** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

---

### ۴. تفکیک دامنه و چندمستأجری (Multi-Tenancy & Data Isolation)

1. **انزوای کامل کاتالوگ و انبار بنکداران:** هر بنکدار فقط و فقط سوابق انبار و قیمت‌گذاری اختصاصی خود در `vendor_inventory` و `vendor_products` را می‌بیند.
2. **محرمانگی فاکتورها و سوابق مالی:** جدول `invoices` و رکوردهای `payments` مستقیماً با `retailer_organization_id` و `vendor_organization_id` محدود شده‌اند و هیچ بنکدار دیگری به مبالغ، اقلام و صورت‌حساب‌های سایر بنکداران دسترسی ندارد.
3. **احراز هویت پیامکی و مدیریت سشن‌ها:**
   * احراز هویت اولیه با شماره همراه معتبر و ارسال رمز یکبار مصرف (SMS OTP) از طریق جدول `otp_challenges`.
   * محدودیت ۵ بار تلاش ناموفق برای هر کد OTP قبل از قفل امنیتی چالش (`status = 'BLOCKED'`).
   * هر ورود موفق منجر به ثبت در جدول `user_sessions` و نگهداری شناسه دستگاه در `user_devices`.
   * خروج از حساب یا لغو اضطراری با لغو فوری سشن (`status = 'REVOKED'`, `revoked_at = now()`) انجام می‌شود.
4. **ساختار کانونیکال توکن احراز هویت (JWT Claims):**
```json
{
  "sub": "b2c140a3-f04b-4c22-9218-c2fa5342a781",
  "org_id": "7d91e843-c03b-4191-87aa-29775089c93a",
  "membership_id": "d0498b82-cb52-4752-9599-231a473f3281",
  "role": "RETAILER_OWNER",
  "org_type": "RETAILER",
  "cluster_id": "ahvaz_cluster_01",
  "iat": 1726260000,
  "exp": 1726346400
}
```
5. **سوئیچ بین سازمان‌ها:** کاربری که دارای چند عضویت معتبر در سازمان‌های مختلف است، می‌تواند با فراخوانی اندپوینت `/auth/switch-organization` بدون نیاز به ورود مجدد، توکن جدیدی با `org_id` و `role` سازمان مقصد دریافت کند.


---

## ۵. مدل دسترسی تفویضی مدیر سازمان (Delegated Permissions) — Amendment 2026-09-20

### ۵.۱. اصل معماری

نقش سازمانی Role سطح مسئولیت پایه را مشخص می‌کند؛ اما «دسترسی واقعی به قابلیت‌ها» می‌تواند برای هر عضویت سازمانی توسط مدیر مجاز تنظیم شود.

زنجیره مرجع دسترسی:

**Organization → Membership → Role → Delegated Permissions → Client Surface**

این مدل جایگزین organization_memberships.role به‌عنوان منبع RBAC نمی‌شود؛ بلکه بعد تفویض قابلیت‌ها را روی همان عضویت اضافه می‌کند.

### ۵.۲. قواعد قطعی

1. **Server-side authorization:** همه دسترسی‌های حساس در Backend اعتبارسنجی می‌شوند.
2. **Deny by default:** قابلیت جدید تا زمانی که صریحاً برای Role/Permission مجاز نشده باشد قابل اجرا نیست.
3. **Least privilege:** هر عضو فقط حداقل قابلیت لازم برای وظیفه خود را دریافت می‌کند.
4. **Tenant isolation:** مدیر بنکداری یا خرده‌فروشی فقط می‌تواند دسترسی اعضای سازمان خودش را تنظیم کند.
5. **Privilege ceiling:** مدیر سازمان نمی‌تواند نقش/مجوزهای سطح پلتفرم مانند ADMIN_SUPER را به عضو سازمان خود تفویض کند.
6. **Auditability:** هر Grant/Revoke باید actor، target membership، permission، timestamp و reason داشته باشد.
7. **Client neutrality:** Web و Android از یک authorization boundary مشترک استفاده می‌کنند؛ هیچ client منطق مجوز مستقل و متناقض ندارد.

### ۵.۳. نمونه Permissionهای قابلیت‌محور

| Domain | Permission | نمونه نقش پایه |
|---|---|---|
| Catalog | catalog.view | همه نقش‌های مرتبط |
| Catalog | catalog.manage | Vendor Owner / Ops |
| Inventory | inventory.view | Vendor Owner / Vendor Staff |
| Inventory | inventory.scan | Vendor Owner / Vendor Staff |
| Inventory | inventory.adjust | Vendor Owner / Delegated Staff |
| Pricing | price.view | مجاز بر اساس scope |
| Pricing | price.manage | Vendor Owner / Delegated Staff |
| Orders | order.view | کاربران مجاز همان سازمان |
| Orders | order.accept | Vendor Owner / Delegated Staff |
| Orders | order.fulfillment | Vendor Owner / Vendor Staff |
| Delivery | delivery.dispatch | Vendor Owner / Vendor Staff |
| Delivery | delivery.handoff | کاربران مجاز Fulfillment |
| Finance | payment.view | کاربران مالی مجاز |
| Finance | payment.record | کاربران مجاز عملیاتی |
| Finance | settlement.view | Vendor Owner / کاربران مالی مجاز |
| People | membership.manage | Organization Owner |
| Reports | reports.view | طبق تفویض مدیر |

این جدول «catalog اولیه permission» است؛ grantهای نهایی باید هنگام applicationization با route/command matrix سازگار شوند.

---

## ۵.۴. برابری Web و Android

برای همه Personaهای کانونیکال پروژه:

- Web client در دسترس است.
- Android client در دسترس است.
- Backend و Domain Model مشترک است.
- مجوزها بین دو client مشترک است.
- تفاوت فقط در UX و context of use است.

### Web — اولویت تعامل

- مدیریت
- جستجوی گسترده
- قیمت‌گذاری
- catalog maintenance
- reports
- reconciliation
- bulk operations

### Android — اولویت تعامل

- warehouse operations
- field work
- quick actions
- barcode scan
- picking
- dispatch
- delivery confirmation
- exception capture

Android یک نسخه کوچک‌شده از Web نیست؛ یک client عملیاتی با همان permission contract است.

---

## ۵.۵. Scanner Permission

قابلیت اسکن بارکد باید یک permission مستقل و قابل تفویض باشد:

inventory.scan

اسکن به‌خودی‌خود مجوز ایجاد Master Product نیست.

Flow:

**Scan → Match → Exact / Ambiguous / Unknown → Candidate Review → Canonical Master**

---

## ۵.۶. Financial Access

دسترسی به سوابق پرداخت، refund، invoice و settlement باید capability-based و tenant-scoped باشد.

مخفی کردن مسیر یا دکمه در Client به‌تنهایی کنترل دسترسی محسوب نمی‌شود.
