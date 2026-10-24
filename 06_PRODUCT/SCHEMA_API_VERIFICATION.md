# ممیزی و انطباق قراردادهای API با اسکیما پایگاه داده (Schema & API Cross-Verification)
## POL Architecture & Cross-Layer Contract Reconciliation
**شناسه سند:** `ARCH-VERIF-001`  
**وضعیت:** مصوب و ممیزی‌شده  
**دامنه:** تطابق ۱۰۰٪ قراردادهای API (`API_Contracts.md`) با ساختار فیزیکی دیتابیس (`001_initial_schema.sql` / `Data_Schema.md`)  
**تاریخ انتشار:** سپتامبر ۲۰۲۶  

---

## ۱. جدول نگاشت و انطباق لایه به لایه (API to Schema Mapping)

| اندپوینت API | متد | موجودیت دیتابیس متناظر | فیلدهای کلیدی بدنه درخواست / پاسخ | انطباق با اسکیما | وضعیت ممیزی |
|---|:---:|---|---|:---:|:---:|
| `/products/search` | `GET` | `products`, `brands`, `categories`, `product_media` | `id`, `master_sku`, `canonical_name_fa`, `lowest_unit_price_toman` | ۱۰۰٪ مطابق | **VERIFIED** |
| `/products/match-barcode` | `POST` | `product_identifiers`, `products` | `raw_barcode`, `scan_source` → `match_status`, `product` | ۱۰۰٪ مطابق | **VERIFIED** |
| `/product-candidates` | `POST` | `product_candidates`, `media_assets` | `proposed_title`, `barcode`, `vendor_sku`, `photo_asset_id` | ۱۰۰٪ مطابق | **VERIFIED** |
| `/vendors/inventory/continuous-scan` | `POST` | `vendor_products`, `vendor_prices`, `vendor_inventory` | `product_id`, `vendor_sku`, `packaging_unit`, `physical_quantity`, `unit_price_toman` | ۱۰۰٪ مطابق | **VERIFIED** |
| `/baskets/:id/items` | `POST` | `basket_items`, `baskets` | `product_id`, `requested_quantity`, `requested_unit`, `pack_quantity` | ۱۰۰٪ مطابق | **VERIFIED** |
| `/baskets/:id/allocation-preview` | `POST` | `allocation_plans`, `allocation_items` | `allocation_plan_id`, `strategy`, `selected_vendor`, `total_amount_toman` | ۱۰۰٪ مطابق | **VERIFIED** |
| `/orders` | `POST` | `order_groups`, `orders`, `order_items` | `allocation_plan_id`, `delivery_address`, `preferred_payment_method` | ۱۰۰٪ مطابق | **VERIFIED** |
| `/orders/:id/accept` | `POST` | `orders`, `vendor_inventory`, `inventory_audit_log` | `order_id` → وضعیت `ACCEPTED` | ۱۰۰٪ مطابق | **VERIFIED** |
| `/orders/:id/partial-accept` | `POST` | `orders`, `order_items` | `items: [{ order_item_id, accepted_quantity, reason }]` | ۱۰۰٪ مطابق | **VERIFIED** |
| `/orders/:id/dispatch` | `POST` | `orders`, `deliveries` | `driver_name`, `driver_phone`, `vehicle_plate`, `carrier_name` | ۱۰۰٪ مطابق | **VERIFIED** |
| `/orders/:id/deliver` | `POST` | `orders`, `deliveries`, `proof_of_delivery` | `otp_code` دقیقاً ۶ رقم عددی / `signature` → وضعیت `DELIVERED` | قرارداد شش‌رقمی؛ اجرای آزمون تازه لازم است | **IMPLEMENTED / REVERIFY** |
| `/orders/:id/disputes` | `POST` | `disputes`, `orders` | `claimed_amount_toman`, `description`, `evidence_media_id` | ۱۰۰٪ مطابق | **VERIFIED** |
| `/disputes/:id/resolve` | `PATCH` | `disputes`, `settlement_adjustments` | `outcome`, `approved_amount_toman`, `reason` | ۱۰۰٪ مطابق | **VERIFIED** |

---

## ۲. راستی‌آزمایی انتزاع واحدها (Generic Unit Abstraction Verification)

* **پایگاه داده:**
  - `vendor_inventory` از فیلدهای جنریک `inventory_unit`, `physical_quantity`, `reserved_quantity`, `available_quantity` پشتیبانی می‌کند.
  - `basket_items` از `requested_quantity`, `requested_unit`, `pack_quantity` پشتیبانی می‌کند.
  - `order_items` از `ordered_quantity`, `accepted_quantity`, `delivered_quantity`, `packaging_unit_snapshot`, `pack_quantity_snapshot`, `unit_price_toman` پشتیبانی می‌کند.
* **قراردادهای API:**
  - تمامی فیلدهای قدیمی کارتن‌محور (`available_cartons`, `requested_cartons`, `price_per_carton_toman`) حذف و با فیلدهای جنریک `quantity`, `unit`, `unit_price_toman`, `packaging_unit` جایگزین شده‌اند.
* **نتیجه:** انتزاع واحدها در لایه API و دیتابیس به صورت کاملاً همگام و جنریک عمل می‌کند.

---

## ۳. راستی‌آزمایی استقلال ماشین وضعیت سفارش و دعاوی (State Separation Verification)

1. **ماشین وضعیت سفارش (`orders.order_status`):**
   `CREATED` → `SUBMITTED` → `ACCEPTED` / `PARTIALLY_ACCEPTED` → `PREPARING` → `READY` → `DISPATCHED` → `DELIVERED` (یا `CANCELLED` / `REJECTED`).
   - فاقد وضعیت `DISPUTED`.
2. **ماشین وضعیت اختلاف (`disputes.dispute_status`):**
   `OPENED` → `UNDER_REVIEW` → `RESOLVED_SETTLEMENT_ADJUSTMENT` / `RESOLVED_REFUND_APPROVED` / `RESOLVED_VENDOR_FAVOR` / `REJECTED` → `CLOSED`.
   - ثبت ادعا صرفاً وضعیت سفارش در `orders.dispute_status` را به `OPEN` تغییر می‌دهد بدون آنکه وضعیت تحویل فیزیکی (`DELIVERED`) را دگرگون کند.
