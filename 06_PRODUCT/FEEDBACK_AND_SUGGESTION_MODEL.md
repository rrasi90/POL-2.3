# POL — Universal Feedback & Suggestion System (صندوق بازخورد و پیشنهادات همگانی)

**Domain:** Operational Intelligence, User Voice & Continuous Improvement  
**Audience:** Retailers, Vendors, Field Activators, Ops Support, Product Managers  
**Implementation State:** DOMAIN_VERIFIED (Migration 004 + `FeedbackService`)

---

## 1. Objective & Operational Reality

در بازارهای B2B سنتی و در فرآیند راه‌اندازی، شکاف بزرگی بین **آنچه مهندسان تصور می‌کنند** و **آنچه در مغازه سوپرمارکت یا انبار بنکدار رخ می‌دهد** وجود دارد. سوپرمارکت‌دار ممکن است با مشکلی در سرعت جستجو یا عدم یافتن یک برند مواجه شود، اما زمان تماس با پشتیبانی را نداشته باشد.

هدف صندوق بازخورد و پیشنهادات همگانی:
> تبدیل پلتفرم پُل به یک سیستم یادگیرنده با ایجاد **ساده‌ترین راه ارسال نظر، گزارش باگ، یا پیشنهاد کالای ناموجود با حداقل اصطکاک (Zero-Friction Contextual Feedback)**.

---

## 2. Friction Minimization Principles

1. **حداکثر ۲ فیلد اجباری:** کاربر فقط نوع بازخورد (`نوع: پیشنهاد / باگ / درخواست کالا / انتقاد`) و توضیحات متنی را می‌نویسد.
2. **ثبت خودکار مشخصات فنی (Zero-Effort Context):** هرگز از سوپرمارکت‌دار یا بنکدار پرسیده نمی‌شود «از چه ورژنی استفاده می‌کنی؟» یا «در کدام صفحه بودی؟». سامانه موارد زیر را در لایه فرانت‌اند/کلاینت و سشن به‌صورت خودکار در شیء `client_context` ذخیره می‌کند:
   - `screen`: آدرس یا نام صفحه فعلی (مثلاً `/catalog/dairy`)
   - `route`: نام روت در React Native / Next.js
   - `device`: مدل گوشی کاربر (مثلاً `Samsung SM-A525F`)
   - `app_version`: نسخه اپلیکیشن
   - `user_id` و `organization_id`: استخراج از توکن احراز هویت
   - `correlation_id`: شناسه رهگیری درخواست
3. **دسترسی دائمی:** در تمام صفحات اپلیکیشن سوپرمارکت و پنل بنکدار، یک دکمه شناور یا گزینه در منو برای ارسال نظر در دسترس است.

---

## 3. Triage & Administrative Lifecycle

```text
[کاربر: سوپرمارکت / بنکدار / فعال‌ساز میدانی]
             │
             ▼
      (ثبت سریع نظر)
             │
             ▼
        SUBMITTED ────────┐ (ورود به کارتابل ادمین پُل)
             │            │
             ▼            ▼
         IN_REVIEW ◄──────┘ (تخصیص به کارشناس عملیات / محصول)
             │
      ┌──────┴──────┐
      ▼             ▼
   ACCEPTED      REJECTED (با ثبت دلیل مدیریتی)
      │             │
      └──────┬──────┘
             ▼
         RESOLVED
             │
             ▼
(ارسال پاسخ رسمی و نوتیفیکیشن بسته شدن به کاربر - Closed Loop)
```

---

## 4. Closed-Loop Feedback Invariant (پاسخ به کاربر)

یکی از عوامل اصلی دلسردی کاربران سنتی این است که احساس می‌کنند نظراتشان خوانده نمی‌شود.
در پلتفرم پُل:
- هرگاه ادمین عملیات به بازخوردی پاسخ دهد (`reply_to_feedback`):
  - فیلدهای `admin_reply` و `replied_at` مقداردهی می‌شوند.
  - بلافاصله رویداد `FEEDBACK_REPLIED` در جدول `notifications` تولید می‌شود.
  - پیامکی با لحن محترمانه و کوتاه برای کاربر فرستاده می‌شود:
    *«همکار گرامی در سوپرمارکت گلستان، پاسخ به پیشنهاد شما در سامانه پُل ثبت شد. از همراهی شما سپاسگزاریم.»*

---

## 5. Security & Multi-Tenant Isolation

- **سوپرمارکت‌ها و بنکداران:** در متد `get_user_feedback`، کوئری مستقیماً به `organization_id` کاربر مقید است. هیچ کاربری به بازخوردها یا انتقادات سایر سازمان‌ها دسترسی ندارد.
- **تیم عملیات پُل (OPS_ADMIN):** در متد `get_admin_inbox`، ادمین‌ها به تمام بازخوردهای سراسر پلتفرم با امکان فیلتر بر اساس وضعیت، نوع بازخورد و فوریت (`URGENT`, `HIGH`, `NORMAL`) دسترسی دارند.

---

## 6. Schema Reference (`004_operational_intelligence.sql`)

```sql
CREATE TABLE feedback_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    feedback_type VARCHAR(32) NOT NULL, -- BUG, SUGGESTION, COMPLAINT, FEATURE_REQUEST, MISSING_PRODUCT
    title VARCHAR(255),
    description TEXT NOT NULL,
    attachment_url TEXT,
    client_context JSONB DEFAULT '{}'::jsonb,
    priority VARCHAR(16) NOT NULL DEFAULT 'NORMAL',
    status VARCHAR(32) NOT NULL DEFAULT 'SUBMITTED',
    assigned_to_user_id UUID REFERENCES users(id),
    admin_notes TEXT,
    admin_reply TEXT,
    triaged_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```
