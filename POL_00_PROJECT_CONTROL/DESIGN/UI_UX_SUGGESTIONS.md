# POL B2B FMCG Platform — UI/UX Upgrade Suggestions

**Date:** 2026-09-20  
**Status:** DRAFT  
**Scope:** Complete UI/UX overhaul from mock state to production-grade B2B SaaS design system

---

## 1. Executive Summary

The POL platform currently has **2 routes, 12 components, zero design tokens, and zero API wiring** (except auth). The backend has **92 API endpoints across 7 roles** with complex business state machines. This document provides a comprehensive UI/UX upgrade plan organized by domain.

### Current vs Target

| Metric | Current | Target |
|--------|---------|--------|
| Routes | 2 (`/`, `/auth`) | 15+ role-based routes |
| Components | 12 (presentational) | 60+ (wired to API) |
| Design tokens | 0 | 40+ (colors, spacing, typography, elevation) |
| RTL support | Basic (`dir="rtl"`) | Full (logical properties, mirrored icons) |
| API integration | 1 endpoint (auth) | 92 endpoints wired |
| Responsive | Minimal | Mobile-first with breakpoints |
| Accessibility | None | WCAG 2.1 AA |

---

## 2. Design System Foundation

### 2.1 Color Palette

#### Brand Colors
| Token | Value | Usage |
|-------|-------|-------|
| `--color-primary` | `#1E40AF` (Blue-800) | Primary actions, CTAs |
| `--color-primary-hover` | `#1E3A8A` (Blue-900) | Hover states |
| `--color-primary-light` | `#DBEAFE` (Blue-100) | Backgrounds, selections |
| `--color-secondary` | `#059669` (Emerald-600) | Success, financial positive |
| `--color-accent` | `#7C3AED` (Violet-600) | Alerts, badges |

#### Status Colors (Semantic Triad)
| Status | Background | Icon | Text | Usage |
|--------|------------|------|------|-------|
| Success | `#DCFCE7` | `#22C55E` | `#15803D` | DELIVERED, CONFIRMED, SETTLED |
| Warning | `#FEF9C3` | `#EAB308` | `#A16207` | PENDING, IN_PROGRESS, REVIEW |
| Error | `#FEE2E2` | `#EF4444` | `#B91C1C` | CANCELLED, DISPUTED, FAILED |
| Info | `#DBEAFE` | `#3B82F6` | `#1D4ED8` | CREATED, SUBMITTED, NEW |

#### Neutral Palette
| Token | Value | Usage |
|-------|-------|-------|
| `--color-bg` | `#F9FAFB` | Page background |
| `--color-surface` | `#FFFFFF` | Card backgrounds |
| `--color-border` | `#E5E7EB` | Borders, dividers |
| `--color-text-primary` | `#111827` | Headings, primary text |
| `--color-text-secondary` | `#6B7280` | Descriptions, labels |
| `--color-text-muted` | `#9CA3AF` | Placeholders, hints |

### 2.2 Typography

#### Font Stack (Persian-First)
```
Vazirmatn, IRANSans, IRANYekan, Estedad, Tahoma, Arial, sans-serif
```

#### Type Scale
| Token | Size | Weight | Line Height | Usage |
|-------|------|--------|-------------|-------|
| `--text-h1` | 28px | 700 | 1.2 | Page titles |
| `--text-h2` | 22px | 600 | 1.3 | Section headers |
| `--text-h3` | 18px | 600 | 1.4 | Card titles |
| `--text-body` | 14px | 400 | 1.6 | Body text |
| `--text-small` | 12px | 400 | 1.5 | Captions, hints |
| `--text-badge` | 11px | 500 | 1.0 | Status badges |

### 2.3 Spacing Scale
| Token | Value | Usage |
|-------|-------|-------|
| `--space-1` | 4px | Tight gaps |
| `--space-2` | 8px | Component inner spacing |
| `--space-3` | 12px | Card padding |
| `--space-4` | 16px | Standard gaps |
| `--space-5` | 20px | Section spacing |
| `--space-6` | 24px | Large section spacing |
| `--space-8` | 32px | Page margins |

### 2.4 Elevation
| Token | Value | Usage |
|-------|-------|-------|
| `--shadow-sm` | `0 1px 2px rgba(0,0,0,0.05)` | Subtle cards |
| `--shadow-md` | `0 4px 6px rgba(0,0,0,0.07)` | Raised cards |
| `--shadow-lg` | `0 10px 15px rgba(0,0,0,0.1)` | Dropdowns, modals |
| `--shadow-xl` | `0 20px 25px rgba(0,0,0,0.1)` | Modal overlays |

### 2.5 Border Radius
| Token | Value | Usage |
|-------|-------|-------|
| `--radius-sm` | 6px | Buttons, inputs |
| `--radius-md` | 8px | Cards |
| `--radius-lg` | 12px | Modals, panels |
| `--radius-full` | 9999px | Badges, avatars |

---

## 3. Gap Analysis — Frontend Code vs Backend API

### 3.1 Authentication Domain
| Aspect | Backend | Frontend | Gap |
|--------|---------|----------|-----|
| OTP Request | `POST /api/v1/auth/request-otp` with `client_fingerprint` | `api.post("/api/v1/auth/request-otp", { mobile_number: phone })` | Missing `client_fingerprint` field |
| OTP Verify | `POST /api/v1/auth/verify-otp` with `device_info` | `api.post("/api/v1/auth/verify-otp", { mobile_number, otp_code })` | Missing `device_info` field |
| Token storage | JWT + refresh token + sessions | `localStorage` only | No httpOnly cookie strategy; XSS vulnerable |
| 401 handling | `SESSION_EXPIRED`, `SESSION_REVOKED`, `INVALID_REFRESH_TOKEN` | Redirect to `/auth/login` | No refresh token retry; no differentiated error messages |
| Session management | `DELETE /sessions/{id}`, `DELETE /sessions/current`, `DELETE /logout-all` | None | Zero session UI |
| Org switching | `POST /api/v1/auth/switch-organization` | None | Zero multi-org support |

### 3.2 Catalog Domain
| Aspect | Backend | Frontend | Gap |
|--------|---------|----------|-----|
| Product listing | 6 read endpoints with filters (category, brand, vendor, search) | Hardcoded mock `Product[]` | Zero API wiring |
| Vendor info on products | Backend returns vendor_id, vendor_name | Frontend shows `p.brand` only | No vendor display |
| Price display | Backend returns `unit_price_toman` | Frontend shows `p.price_toman` | Field name mismatch |
| Product images | Backend has `image_url` field | Frontend shows "No image" placeholder | Zero image support |
| Category filtering | Backend: `/categories`, `/brands`, `/categories/{id}/products` | None | Zero filtering UI |
| Search | Backend: `/search?q=` | None | Zero search UI |

### 3.3 Orders Domain
| Aspect | Backend | Frontend | Gap |
|--------|---------|----------|-----|
| Order creation | `POST /api/v1/orders` with `allocation_plan_id` + `idempotency_key` | `CheckoutForm onSubmit()` calls no API | Zero checkout wiring |
| Order list | `GET /api/v1/orders` with status filter, pagination | Hardcoded mock `Order[]` | Zero API wiring |
| Order detail | `GET /api/v1/orders/{id}` with line items, timeline | Hardcoded mock `Order` | Zero API wiring |
| Multi-vendor | `OrderGroup` with child orders per vendor | Not shown | Zero multi-vendor UI |
| Vendor acceptance | `POST /orders/{id}/accept`, `/reject`, `/partial-acceptance-proposals` | `VendorOrderQueue` shows Accept/Reject buttons | Buttons exist but no API wiring |
| Delivery tracking | `/delivery-confirmation`, `/delivery-exceptions`, OTP confirm | Not shown | Zero delivery UI |
| Partial acceptance flow | 3-step proposal/counter/accept flow | Not shown | Zero complex flow UI |
| Returns | Full state machine (12 states) | Not shown | Zero returns UI |
| Disputes | Open, evidence, verify flow | Not shown | Zero disputes UI |
| Idempotency | Required for checkout | Not implemented | Critical missing |

### 3.4 Vendor Management Domain
| Aspect | Backend | Frontend | Gap |
|--------|---------|----------|-----|
| Vendor catalog CRUD | 8 endpoints (create, update, price, inventory) | `VendorInventoryTable` shows mock data | Zero API wiring |
| Vendor storefront | Not implemented in backend | Not implemented | Feature gap |
| Vendor search | Not implemented in backend | Not implemented | Feature gap |
| Daily inventory | `confirm`, `confirm-with-changes`, `history` | Not shown | Zero inventory workflow UI |
| Settlements | 5 finance endpoints | `VendorSettlementList` shows mock data | Zero API wiring |
| RBAC enforcement | `authorize_action` exists but is DEAD CODE | No role-based routing | Zero access control |

### 3.5 Operations Domain
| Aspect | Backend | Frontend | Gap |
|--------|---------|----------|-----|
| Support cases | Create, message, transition, list, get | `SupportCaseList` shows mock data | Zero API wiring |
| Field tasks | Create, update, list, get | `FieldTaskList` shows mock data | Zero API wiring |
| Referrals | Create, redeem, list, get | Not shown | Zero referrals UI |
| Notifications | List, preferences, update | `NotificationList` shows mock data | Zero API wiring |
| Admin | User list, org user list | Not shown | Zero admin UI |
| Financial | Transaction list, settlement batches, reconciliation | Not shown | Zero financial dashboard |

### 3.6 RBAC & Authorization
| Role | Backend Endpoints | Frontend Access |
|------|-------------------|-----------------|
| ADMIN_SUPER | All endpoints | Same as everyone |
| OPS_AGENT | Support, field tasks, admin, reconciliation | No differentiation |
| FIELD_ACTIVATOR | Field tasks, delivery | No differentiation |
| VENDOR_OWNER | Vendor catalog, orders, settlements, finance | No differentiation |
| VENDOR_STAFF | Limited vendor operations | No differentiation |
| RETAILER_OWNER | Catalog browse, orders, returns | No differentiation |
| RETAILER_STAFF | Limited retailer operations | No differentiation |

**Critical:** Zero role-based routing, zero menu filtering, zero UI differentiation by role.
