# POL Penpot Design Specifications

**Date:** 2026-09-20  
**Status:** DRAFT  
**Penpot MCP:** Configured (requires opencode restart to activate)

---

## 1. Penpot Project Structure

### Page Organization
```
POL Design System
├── 00-Tokens (colors, typography, spacing, elevation)
├── 01-Components (buttons, inputs, cards, badges, tables, modals)
├── 02-Auth (login, OTP verify)
├── 03-Retailer (catalog, basket, checkout, order list, order detail)
├── 04-Vendor (inventory, order queue, settlements, storefront)
├── 05-Field (task list, task detail)
├── 06-OPS (support cases, admin dashboard)
├── 07-Shared (navigation, sidebar, notifications, empty states)
├── 08-Responsive (mobile variants of all screens)
└── 09-Flows (user journey diagrams)
```

---

## 2. Screen Specifications — Auth Domain

### 2.1 Login Screen (`/auth`)
**Route:** `/auth` (login step)  
**Target Users:** All 7 roles  
**Layout:** Centered card on neutral background

**Components:**
- App logo + "POL" branding at top
- Phone number input with `+98` prefix (Persian format)
- "Send OTP" primary button
- Error message area (validation, rate limit, lockout)
- Language toggle (FA/EN) in top corner

**States:**
- Default: Empty phone input
- Loading: Button shows spinner + "Sending..."
- Success: Transitions to OTP screen
- Error: Red banner with specific message
- Rate limited: Timer countdown showing retry wait
- Locked out: Lock icon + "Account temporarily locked" message

**Design Notes:**
- Phone input must use `inputMode="tel"` and `dir="ltr"` for number entry
- RTL layout but LTR phone number field
- Persian placeholder: `09123456789`

### 2.2 OTP Verification Screen
**Route:** `/auth` (verify step)  
**Target Users:** All 7 roles  
**Layout:** Centered card with back navigation

**Components:**
- "Change number" back link
- 4-digit OTP input (individual digit boxes)
- Resend timer (120s countdown)
- Resend button (appears after 120s)
- Verify primary button

**States:**
- Default: Empty OTP boxes
- Loading: Button shows spinner + "Verifying..."
- Success: Redirects to dashboard (role-based)
- Error: "Invalid code" with retry prompt
- Expired: "Code expired. Resend new code."
- Rate limited: Timer + "Too many attempts. Wait X minutes."

**Design Notes:**
- OTP input uses `inputMode="numeric"`, `autoComplete="one-time-code"`
- Individual digit boxes with auto-focus progression
- Persian text: "کد ۴ رقمی ارسال شده به {phone} را وارد کنید"

---

## 3. Screen Specifications — Retailer Domain

### 3.1 Product Catalog (`/retailer/catalog`)
**Route:** `/retailer/catalog`  
**Target Users:** RETAILER_OWNER, RETAILER_STAFF  
**Layout:** Sidebar + main content area

**Components:**
- Search bar (top, full width)
- Category filter chips (horizontal scroll)
- Brand filter chips
- Vendor filter chips
- Product grid (2-3 columns)
- Product cards with image, name, brand, vendor, pack size, price, "Add to Basket" button
- Basket floating action button (bottom-right, shows item count)

**States:**
- Loading: Skeleton cards
- Empty: "No products found" with illustration
- Results: Product grid with filters applied
- Error: Retry prompt

**Design Notes:**
- Product card MUST show vendor name/logo prominently (trust signal)
- Price displays in Toman with `toLocaleString("fa-IR")`
- RTL: Grid flows right-to-left
- Mobile: Single column, sticky search bar

### 3.2 Shopping Basket (`/retailer/basket`)
**Route:** `/retailer/basket`  
**Target Users:** RETAILER_OWNER, RETAILER_STAFF  
**Layout:** Full-width list with summary sidebar

**Components:**
- Basket items list (product image, name, vendor, quantity +/- controls, unit price, line total)
- Remove item button (swipe on mobile)
- Vendor group headers (items grouped by vendor)
- Subtotal per vendor
- Grand total
- "Proceed to Checkout" primary button
- "Continue Shopping" secondary button

**States:**
- Empty: "Your basket is empty" with illustration + "Browse Catalog" CTA
- Items present: List with running totals
- Loading: Spinner on checkout button
- Error: Specific item availability issues highlighted

**Design Notes:**
- Items grouped by vendor (multi-vendor ordering)
- Quantity controls: +/- buttons with manual input
- Real-time total recalculation
- Vendor-specific delivery estimates shown per group

### 3.3 Checkout (`/retailer/checkout`)
**Route:** `/retailer/checkout`  
**Target Users:** RETAILER_OWNER, RETAILER_STAFF  
**Layout:** Multi-step form

**Steps:**
1. **Delivery Address** — Map picker or manual address entry
2. **Delivery Slot** — Date/time selection
3. **Payment Method** — Cash on delivery, online payment
4. **Review & Confirm** — Order summary, terms acceptance

**Components:**
- Step indicator (horizontal stepper, RTL)
- Address form (province, city, address, postal code, phone)
- Date picker (Jalali calendar)
- Time slot selector
- Payment method cards
- Order summary card
- "Place Order" primary button with idempotency key generation

**States:**
- Step 1 active: Address form
- Step 2 active: Slot selection
- Step 3 active: Payment selection
- Step 4 active: Review with all details
- Submitting: Full-page spinner
- Success: Order confirmation with order number
- Error: Specific field errors highlighted

**Design Notes:**
- Jalali calendar library required
- Address form uses Persian province/city data
- Multi-vendor orders show per-vendor subtotals
- Terms acceptance checkbox required before submit

### 3.4 Order List (`/retailer/orders`)
**Route:** `/retailer/orders`  
**Target Users:** RETAILER_OWNER, RETAILER_STAFF  
**Layout:** Filter tabs + list

**Components:**
- Status filter tabs (All, Active, Completed, Cancelled)
- Order cards (order number, date, vendor count, total, status badge)
- Sort dropdown (newest, oldest, highest amount)
- Pagination

**States:**
- Loading: Skeleton list
- Empty: "No orders yet" with illustration
- Results: Order list with status badges
- Error: Retry prompt

### 3.5 Order Detail (`/retailer/orders/{id}`)
**Route:** `/retailer/orders/{id}`  
**Target Users:** RETAILER_OWNER, RETAILER_STAFF  
**Layout:** Header + timeline + details

**Components:**
- Order header (number, date, total)
- Horizontal progress stepper (CREATED > SUBMITTED > ACCEPTED > PREPARING > DISPATCHED > DELIVERED)
- Vendor sections (each vendor's items grouped)
- Delivery tracking per vendor
- Action buttons (Cancel, Return, Dispute)
- Order timeline (event log)

**States:**
- Loading: Skeleton
- Active order: Progress stepper with current state highlighted
- Delivered: Green completed state
- Cancelled: Red cancelled state with reason

---

## 4. Screen Specifications — Vendor Domain

### 4.1 Vendor Dashboard (`/vendor/dashboard`)
**Route:** `/vendor/dashboard`  
**Target Users:** VENDOR_OWNER, VENDOR_STAFF  
**Layout:** KPI cards + quick actions

**Components:**
- KPI cards row: Pending Orders, Today's Revenue, Active Products, Pending Shipments
- Recent orders list (top 5)
- Quick actions: "Manage Catalog", "View Orders", "Inventory"
- Revenue chart (last 7 days)

**States:**
- Loading: Skeleton cards
- Data loaded: KPIs with trend indicators
- No data: "Getting started" onboarding

### 4.2 Vendor Catalog Management (`/vendor/catalog`)
**Route:** `/vendor/catalog`  
**Target Users:** VENDOR_OWNER, VENDOR_STAFF  
**Layout:** Table + action panel

**Components:**
- Product table (name, SKU, price, stock, status, actions)
- "Add Product" button
- Bulk actions (edit price, adjust stock)
- Search/filter bar
- Inline edit for price and stock
- Status badges (ACTIVE, INACTIVE, OUT_OF_STOCK)

**States:**
- Empty: "Add your first product" CTA
- Products listed: Editable table
- Editing: Inline edit mode
- Saving: Spinner on changed rows

### 4.3 Vendor Order Queue (`/vendor/orders`)
**Route:** `/vendor/orders`  
**Target Users:** VENDOR_OWNER, VENDOR_STAFF  
**Layout:** Queue list with detail panel

**Components:**
- Status tabs (New, In Progress, Completed, All)
- Order cards (retailer name, items count, total, time since submission)
- Accept/Reject/Partial Accept buttons
- Order detail side panel (slides in from left in RTL)
- Partial acceptance form (item-by-item accept/reject with quantities)

**States:**
- New orders: Blue highlight, prominent Accept/Reject
- Processing: Yellow highlight, action buttons
- Completed: Green, read-only

### 4.4 Vendor Settlements (`/vendor/settlements`)
**Route:** `/vendor/settlements`  
**Target Users:** VENDOR_OWNER  
**Layout:** Summary cards + list

**Components:**
- Summary cards: Total Revenue, Commission Paid, Net Earnings, Pending Settlements
- Settlement batch list (batch ID, date, gross, commission, net, status)
- Settlement detail modal (order-level breakdown)
- Export button (CSV)

---

## 5. Screen Specifications — Field Domain

### 5.1 Field Task List (`/field/tasks`)
**Route:** `/field/tasks`  
**Target Users:** FIELD_ACTIVATOR  
**Layout:** Task cards with status indicators

**Components:**
- Status tabs (Assigned, In Progress, Completed, All)
- Task cards (type, status, retailer/vendor name, location, time, notes)
- Start/Complete action buttons
- Map view toggle (future)

**States:**
- Assigned: Blue, "Start" button
- In Progress: Yellow, "Complete" button
- Completed: Green, read-only

### 5.2 Field Task Detail (`/field/tasks/{id}`)
**Route:** `/field/tasks/{id}`  
**Target Users:** FIELD_ACTIVATOR  
**Layout:** Detail view with actions

**Components:**
- Task header (type, status, assigned date)
- Location display (address, map)
- Notes section (read + add note)
- Photo capture (for verification)
- Status transition buttons
- History timeline

---

## 6. Screen Specifications — OPS Domain

### 6.1 Support Cases (`/ops/support`)
**Route:** `/ops/support`  
**Target Users:** OPS_AGENT  
**Layout:** List + detail panel

**Components:**
- Status tabs (Open, In Progress, Waiting, Resolved, All)
- Priority badges (Low, Normal, High, Critical)
- Case cards (subject, retailer/vendor, status, priority, created date)
- Case detail panel (messages, actions, transitions)
- "Create Case" button
- Message composer

### 6.2 Admin Dashboard (`/admin/dashboard`)
**Route:** `/admin/dashboard`  
**Target Users:** ADMIN_SUPER  
**Layout:** Overview + management panels

**Components:**
- System health KPIs (total users, orders, revenue)
- User management table (name, role, org, status, actions)
- Organization list
- Audit log viewer
- System configuration panel

---

## 7. Shared Components

### 7.1 Navigation Sidebar
**Collapsed:** 64px wide, icons only  
**Expanded:** 256px wide, icons + labels  
**Items (by role):**
- ADMIN_SUPER: Dashboard, Users, Organizations, Settings
- OPS_AGENT: Dashboard, Support, Field Tasks, Finance
- FIELD_ACTIVATOR: Tasks, Map
- VENDOR_OWNER: Dashboard, Catalog, Orders, Inventory, Settlements
- VENDOR_STAFF: Catalog, Orders, Inventory
- RETAILER_OWNER: Catalog, Basket, Orders, Returns
- RETAILER_STAFF: Catalog, Basket, Orders

### 7.2 Top Header Bar
- App name/logo (left in RTL)
- Search bar (center)
- Notification bell with count badge
- User avatar + name dropdown
- Organization switcher (if multi-org)

### 7.3 Empty States
Each list/table screen needs:
- Illustration (SVG)
- Title ("No orders yet")
- Description ("When you place orders, they'll appear here.")
- CTA button ("Browse Catalog")

### 7.4 Error States
- 404: "Page not found" with home CTA
- 500: "Something went wrong" with retry CTA
- 401: "Session expired" with login CTA
- 403: "Access denied" with appropriate message
- Network: "Connection lost" with retry CTA

### 7.5 Loading States
- Skeleton screens (not spinners) for lists
- Spinner for actions (buttons, form submission)
- Progressive loading for images

### 7.6 Notification System
- Toast notifications (top-right, auto-dismiss 5s)
- Priority-based styling (LOW=gray, NORMAL=blue, HIGH=orange, CRITICAL=red)
- Notification center (full list with preferences)

---

## 8. Responsive Breakpoints

| Breakpoint | Width | Layout |
|------------|-------|--------|
| Mobile | < 640px | Single column, bottom nav, stacked cards |
| Tablet | 640-1024px | 2-column grid, collapsible sidebar |
| Desktop | > 1024px | Full sidebar, multi-column layout |

### Mobile-Specific Adaptations
- Tables become card lists
- Bottom navigation bar (5 items max)
- Swipe actions for list items
- Full-screen modals
- Floating action button for primary action

---

## 9. RTL Implementation Rules

1. Use CSS logical properties: `margin-inline-start` not `margin-left`
2. Mirror all directional icons (arrows, carets, chevrons)
3. Progress steppers flow right-to-left
4. Sidebars on the right side
5. Number inputs remain LTR within RTL containers
6. Date pickers use Jalali calendar
7. Currency displays: number LTR, "تومان" label RTL

---

## 10. Accessibility Requirements

- All interactive elements must have visible focus indicators
- Color contrast ratio minimum 4.5:1 for text
- All images need alt text
- Form inputs need associated labels
- Error messages need `role="alert"`
- Navigation needs skip-to-content link
- ARIA landmarks for page structure
- Keyboard navigation for all interactive elements
