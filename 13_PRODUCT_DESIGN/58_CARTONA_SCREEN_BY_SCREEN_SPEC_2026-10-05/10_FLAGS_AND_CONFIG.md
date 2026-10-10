# 10 — Feature Flags & Remote Config (interpreted)

Raw list: `data/feature_flags.txt` (161). Cartona ships **nearly every product decision as a remote flag** — this is the app's real "design system of behavior". For POL: adopt the same pattern (Firebase Remote Config or equivalent) with these flag names as a starting taxonomy.

## Commerce engine
| Flag | Interpretation |
|---|---|
| `SUPPLIER_PAGE_VERSION` | supplier page layout experiment version |
| `SUPPLIER_PAGE_DEFAULT_TAB_IS_OFFERS` | supplier landing tab = offers vs products |
| `SUPPLIER_SHOWCASE_LIST_PAGE_SIZE` / `SUPPLIER_SHOWCASE_PRODUCTS_LIMIT` | showcase pagination sizing |
| `PURCHASABLE_PRODUCT_CARD_SUPPLIER_SCREEN_VARIANT_VERSION` | product card A/B (supplier context) |
| `PURCHASABLE_PRODUCT_CARD_SUPPLIER_SHOWCASE_VARIANT_VERSION` | product card A/B (showcase context) |
| `SHOW_MAX_QUANTITY_ON_PRODUCT_CARD` | show stock max on card |
| `CATEGORY_SCREEN_PRODUCTS_LIMIT` | category page product cap |
| `FLASH_OFFERS_PRODUCTS_LIMIT` | flash-offer section size |
| `HOME_SUPPLIER_CATEGORIES_SECTION_VERSION` | home category module version |
| `HOME_PAGE_DEFAULT_BANNER` | fallback banner |
| `MAX_QTY_CALC_ALGO` | quantity cap algorithm |
| `SCROLL_PAGINATION_THRESHOLD` | infinite scroll trigger point |

## Cart & checkout
| Flag | Interpretation |
|---|---|
| `ABANDONED_CART_TIMEOUT_DURATION_HOURS` | cart-abandonment recovery timer |
| `CARTS_SYNC_INTERVAL_SECONDS` | multi-device cart sync |
| `DELIVERY_VIA_CARTONA_ENABLE_PREFERRED_DELIVERY_DATE` | date picker (Cartona-fulfilled orders) |
| `DELIVERY_VIA_SUPPLIER_ENABLE_PREFERRED_DELIVERY_DATE2` | date picker (supplier-fulfilled orders) |

## Delivery & verification
| Flag | Interpretation |
|---|---|
| `ENABLE_SCREEN_WAKEUP2` | keep screen on (courier handover PIN display) |
| delivery PIN string ("شارك الرمز فقط مع المندوب…") | COD handover verification code |

## Registration / KYC
| Flag | Interpretation |
|---|---|
| `RETAILER_BRANCH_IMAGE_MAX_WIDTH/HEIGHT/QUALITY` | branch photo compression limits |
| `SHOULD_UPLOAD_BRANCH_IMAGES_FROM_GALLERY` | allow gallery uploads |
| `RETAILER_ASKS_OVERLAY_VERSION` | product-request overlay version |
| `RETAILER_ASKS_BANNER_MIN_QUERY_LENGTH` | show ask-banner only after N chars |
| `RETAILER_ASKS_OVERLAY_REGISTRATION_DELAY_DAYS` | hide ask-banner for brand-new accounts |

## Growth & theming
| Flag | Interpretation |
|---|---|
| `ENABLE_RAMADAN_THEME2` / `ENABLE_EID_AL_FETR_THEME` / `ENABLE_EID_AL_ADHA_THEME` / `ENABLE_WORLD_CUP_THEME` | seasonal skins incl. app-icon swap |
| `HOME_PAGE_DEFAULT_BANNER` | campaign fallback |

## Update governance
| Flag | Interpretation |
|---|---|
| `LATEST_APP_VERSION` / `MINIMUM_APP_VERSION` / `UPDATE_CHECK_INTERVAL_MINUTES` | soft-nag vs force-block update policy |

## Integrations (config keys)
| Key | Interpretation |
|---|---|
| `FRESHCHAT_APP_ID/KEY/DOMAIN`, `FRESHCHAT_RETAILERS_TOPIC`, `FRESHCHAT_FEATURE_ENABLED` | support chat config + topic per user type |
| `POSTHOG_HOST/PROJECT_TOKEN`, `SEGMENT_WRITE_KEY`, `FIREBASE_ANALYTICS_ENABLED`, `APPS_FLYER_APP_ID/DEV_KEY` | analytics switches — dual product analytics + attribution, all kill-switchable |
| `CARTONA_FINANCE_WEB_APP_BASE_URL` / `IONIC_APP_URL` | embedded finance web app (installments) |
| `HEALTH_CHECK_URL` / `INDEX_SERVICE_URL` | infra probes |
| `SERVER_BASE_URL` | API base (rotatable) |
| `SUPPORT_PHONE_NUMBER2` / `SUPPORT_EMAIL_ADDRESS` / `LEGAL_PHONE_NUMBER` / `LEGAL_EMAIL_ADDRESS` | contact surfaces |
| `ACTION_LOCALE_CHANGED_BY_WEBVIEW` | locale switch propagates from embedded webview |

## Takeaway for POL

1. **Flag everything that changes behavior** — Cartona even versions *sections* (home categories v?, supplier page v?) to run long-lived experiments.
2. **Kill-switch analytics & integrations** independently.
3. **Config-gate seasonal skins** including the launcher icon.
4. **PIN-handover + screen-wakeup flag** shows courier-facing moments designed into the retailer app itself.
