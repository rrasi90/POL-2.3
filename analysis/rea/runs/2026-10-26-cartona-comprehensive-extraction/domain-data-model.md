# Domain Data Model — Cartona (hypothesis map from schema + endpoints)

## Directly observed local schema (VERIFIED from snapshot strings)
- cartona_v0016.sqlite
  - carts: cartona_user_storage_key UNIQUE, cartona_user_storage_id, local_key, reorder_products_count, cart_value_before_reorder, marked_as_abandoned_at, origin_order_id, created_via_reorder
  - search_summarized_product_history_v001 (search history)
- Abandoned-cart TTL constant: ABANDONED_CART_TIMEOUT_DURATION_HOURS (env-configurable)

## Server-side entities (HYPOTHESIS — inferred from endpoint nouns; no server access)
User/Retailer (me, register, skip-register, blocked) - Branch (list, change) - Supplier (variants, favorites, badges) - Product/Category (search v2, offers, ramadan, bids) - Cart (validate, storage/carts sync) - Order (history, lifecycle, reorder, tracking) - OrderSupportTicket (+types) - Notification (+read) - Campaign (stories, threads, eid cashback, ramadan quiz) - GmvTarget - Wallet/Credit (plans, consent, pay events, legacy installment)

## Relationships (inferred)
Retailer 1-N Branch 1-N Order; Order 1-N OrderItem [H]; Cart -reorder_origin-> Order (origin_order_id VERIFIED column); Supplier 1-N Product; Product N-N Category; Retailer N-N SupplierFavorite; Order 0-N SupportTicket; Retailer 1-0..1 CreditAccount [H]

## State transitions (VERIFIED tokens; transitions HYPOTHESIS)
Order: pending -> confirmed -> processing -> shipped -> out_for_delivery -> delivered | cancelled | rejected; returned/refunded tokens observed.
Cart: active -> abandoned (marked_as_abandoned_at) -> recovered or reordered.
Credit: plan_selected -> pay_success (webview event); legacy installment: activated/suspended.

## Storage map
carts + search history in local SQLite; session state in app storage; attribution in AppsFlyer prefs (backup-excluded).
