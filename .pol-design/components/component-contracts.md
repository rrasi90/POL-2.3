# POL Component Contracts & Visual Inventory

## 1. Atoms & Primitives (`@pol/ui`)
- **Button**:
  - Variants: `primary`, `secondary`, `outline`, `ghost`, `danger`
  - Sizes: `sm` (h-8), `md` (h-10), `lg` (h-12)
  - States: default, hover, active, focus-visible, disabled, loading (spinner)
- **Field & Input**:
  - Anatomy: Label (12px, font-medium), Input box (rounded-sm, 1px border-subtle -> 2px brand-primary), Helper/Error text (11px)
  - States: default, focus, error (semantic.danger), disabled
- **SearchField**:
  - Anatomy: Embedded search icon (RTL right-aligned), clear button (left), placeholder text
- **StatusChip**:
  - Tones: `neutral`, `success`, `warning`, `danger`, `info`
  - Shape: `radius.pill` (rounded-full)
  - Layout: Icon + text, subtle background tint (10-15% opacity), solid text & border
- **QtyStepper**:
  - Anatomy: Minus button, quantity display (tabular numerals), plus button, max stock indicator
- **State Feedback**:
  - `Skeleton`: Pulsing neutral subtle surface (`surface.subtle`)
  - `EmptyState`: Contextual icon/illustration, title (16px), description (14px), primary action button
  - `ErrorState`: Danger icon, clear explanation, retry button
  - `PermissionDenied`: Shield/lock icon, role requirement description

## 2. Commerce Components
- **Product Card**:
  - Media: Aspect-ratio 1:1 clean background image with fallback
  - Metadata: Brand, Category, SKU badge
  - Price Block: Unit price in Toman with tabular digits, discount badge (if applicable), pack size / MOQ
  - Action: Add to basket / QtyStepper
- **Order Row & Detail Panel**:
  - Header: Order #, Date/Time, Vendor Name, Total Toman, StatusChip
  - Tracking: Timeline with state steps (Draft, Confirmed, Allocated, Dispatched, Delivered)
  - Actions: Return/RMA, Support Ticket, Proof of Delivery
- **Inventory Daily Badge**:
  - Stale warning indicator (> 24 hours unconfirmed)
  - Fast-confirm action button
- **Delivery Handoff Card**:
  - Delivery OTP six-digit code entry, recipient signature/photo proof confirmation


**OTP amendment (2026-11-24):** Authentication OTP uses six ASCII digits under D-018. New delivery/POD OTPs use six digits under D-029. Only pre-migration in-flight delivery records may accept their already-issued four-digit code until terminal completion; no new four-digit OTP is issued.
