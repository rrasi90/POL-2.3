# عملیات جمع‌آوری، بارگیری و تحویل کالا (Fulfillment & Delivery Operations)
## پروژه پُل (POL) — B2B FMCG Platform
**شناسه سند:** `OPS-SPEC-001`  
**وضعیت:** مصوب و نهایی  
**نسخه:** ۱.۰  
**مرجع تصمیم‌گیری:** `D-008` (هزینه ناوگان ملکی پُل = ۰) و `D-001` (هاب شهرک بنکداران اهواز)  
**تاریخ به‌روزرسانی:** سپتامبر ۲۰۲۶  

---

### ۱. چارچوب عملیاتی و منطق زنجیره تأمین
پلتفرم پُل با تکیه بر مدل بدون دارایی (Asset-Light)، هیچ‌گونه انبار ملکی، کامیونت یا وانت بار اختصاصی خریداری و اداره نمی‌کند. در عوض، فرآیند آماده‌سازی و تحویل (Fulfillment) مستقیماً با اتصال به **زیرساخت لجستیک موجود در کلاستر ۶۱ هکتاری شهرک بنکداران اهواز** اجرا می‌شود.

**اصول حاکم:**
1. **هزینه ناوگان ملکی پُل صفر است (`D-008`):** ریسک استهلاک، بیمه راننده و سوخت متوجه پلتفرم نیست.
2. **استفاده از ظرفیت خالی باربری سنتی:** شهرک بنکداران اهواز دارای صدها دستگاه وانت نیسان، پیکان‌وانت و خاور مستقر در پایانه‌های باربری داخلی شهرک است.
3. **پنجره‌های زمانی تحویل استاندارد:** سفارش‌های ثبت‌شده تا ساعت ۲۳:۰۰ شب، در پنجره صبح (۹:۰۰ الی ۱۳:۰۰) و سفارش‌های صبح تا ساعت ۱۲:۰۰ ظهر، در پنجره عصر (۱۶:۰۰ الی ۲۰:۰۰) تحویل داده می‌شوند.

---

### ۲. مراحل ۴ گانه فرآیند فیزیکی (Physical Flow Pipeline)

```
[۱. انبار بنکدار (Picking & Packing)]
- دریافت سفارش در پنل بنکدار و صدور پرینت بار (Pick-List).
- کارگر انبار اقلام را جمع‌آوری و در پالت یا کارتن‌های استاندارد بارچینی می‌کند.
- الصاق برچسب مشخصات سفارش پُل (حاوی شماره سفارش، نام سوپرمارکت و مقصد).
        │
        ▼
[۲. تخصیص باربری و بارگیری (Loading & Dispatch)]
- بنکدار وانت باربری همیشگی خود یا باربری شهرک را فراخوان می‌کند.
- ثبت شماره پلاک، نام راننده و شماره تلفن در پنل سفارش‌ها.
- تغییر وضعیت در سامانه به «ارسال شد (DISPATCHED)».
        │
        ▼
[۳. ترانزیت و رهگیری در شهر اهواز (Transit)]
- حرکت راننده از شهرک بنکداران به سمت محله مقصد (مانند زیتون، کوروش، کیانپارس، پادادشهر).
- سوپرمارکت پیامک مشخصات راننده و لینک مشاهده وضعیت را دریافت می‌کند.
        │
        ▼
[۴. تخلیه، تطبیق و تحویل (Proof of Delivery - POD)]
- راننده بار را پای مغازه تخلیه می‌کند.
- مغازه‌دار اقلام را تطبیق داده و امضای دیجیتال / تایید نهایی در اپ را ثبت می‌کند.
- تسویه هزینه کالا و کرایه بار طبق توافق فاکتور.
```

---

### ۳. مدل مالی کرایه حمل و مسئولیت هزینه‌ها (Logistics Cost Model)

| سناریوی سفارش | مسئول پرداخت کرایه حمل | نحوه تسویه | اثر بر اقتصاد پُل |
| :--- | :--- | :--- | :---: |
| **سفارش عادی (بین ۵ الی ۲۰ میلیون تومان)** | **سوپرمارکت (خریدار)** | پرداخت مستقیم کرایه حمل به راننده وانت هنگام تحویل بار | $0$ هزینه برای پُل |
| **سفارش حجیم (بالای ۲۰ میلیون تومان)** | **بنکدار (ارسال رایگان)** | بنکدار کرایه را با راننده طرف قرارداد خود تسویه می‌کند | $0$ هزینه برای پُل |
| **برگشت بار به دلیل نقص فنی یا مغایرت** | **بنکدار مقصر** | بنکدار موظف به پرداخت کرایه وانت بازگشتی است | $0$ هزینه برای پُل |
| **برگشت بار به دلیل امتناع بی‌دلیل خریدار** | **سوپرمارکت خاطی** | هزینه وانت دوطرفه از اعتبار سوپرمارکت کسر می‌شود | $0$ هزینه برای پُل |

---

### ۴. توافق‌نامه سطح خدمات تحویل (Delivery SLAs)

* **نرخ تحویل به موقع و سالم (OTIF - On-Time In-Full):** حداقل تارگت ۹۰٪ برای تمامی بنکداران فعال در ماه اول، و ۹۵٪ از ماه دوم به بعد.
* **سقف زمان تحویل:** حداکثر ۲۴ ساعت از زمان تایید نهایی سفارش توسط بنکدار.
* **قاعده چیدمان فیزیکی ایمن:** تفکیک اکید اقلام شوینده شیمیایی (وایتکس، جرم‌گیر) از اقلام خوراکی و بسته‌بندی در محفظه بار وانت به منظور جلوگیری از هرگونه نشت یا مسمومیت کالا.

---

### ۵. نقش تیم فعال‌ساز میدانی در نظارت بر تحویل (Field Operations Support)
* در پایلوت ۳ ماهه اهواز، یک نفر از اعضای تیم عملیات میدانی پُل در پایانه باربری شهرک بنکداران مستقر است.
* وظیفه او بررسی میدانی کیفیت بارگیری، نظارت بر رفتار رانندگان، و مداخله سریع در صورت بروز تأخیر یا گم‌شدن آدرس سوپرمارکت‌ها است.


---

## 2026-09-20 Product Architecture Amendment — Lightweight Delivery Handoff

### ۶. Delivery Handoff Surface

The MVP does not require a full Driver App.

The delivery flow is extended with a restricted handoff surface:

**Dispatch → Handoff Link → Delivery Task → Receiver Confirmation → POD**

The handoff page should expose only the operational information required to complete delivery:

- delivery/order reference
- store/recipient
- delivery address and map action
- driver/carrier identity when registered by the vendor
- checklist / shortage or damage capture where permitted
- final confirmation

### ۷. Security contract

A delivery handoff token is a restricted capability token, not an authenticated user session.

It must be:

- opaque
- server generated
- cryptographically random
- high entropy
- short lived
- rate limited
- invalidated after completion
- HTTPS only
- served with no-store caching
- protected from referrer leakage
- unable on its own to alter financial state

Where the delivery link is insufficient to establish receiver authority, the flow must require the existing retailer/authorized receiver confirmation or delivery OTP.

### ۸. Android / Web parity

The same delivery domain is available through both clients:

- Web for authorized management/operations workflows
- Android for authorized field/warehouse/delivery tasks

The authorization boundary is shared; only the interaction model differs.

### ۹. MVP scope guardrail

Do not introduce a full driver account, driver organization, fleet-management application, or independent driver settlement model in this wave.
