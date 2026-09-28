---
version: alpha
name: POL Precision Commerce
description: Canonical visual design system mirror for POL B2B FMCG commerce platform.
colors:
  bg-canvas: "#F7F9FC"
  surface-default: "#FFFFFF"
  surface-subtle: "#F1F5F9"
  surface-elevated: "#FFFFFF"
  border-subtle: "#E2E8F0"
  border-strong: "#CBD5E1"
  text-primary: "#0F172A"
  text-secondary: "#475569"
  text-muted: "#64748B"
  text-disabled: "#94A3B8"
  brand-primary: "#2563EB"
  primary: "#2563EB"
  brand-hover: "#1D4ED8"
  brand-active: "#1E40AF"
  brand-accent: "#4F46E5"
  semantic-success: "#15803D"
  semantic-warning: "#B45309"
  semantic-danger: "#B91C1C"
  semantic-info: "#1D4ED8"
  focus-ring: "#2563EB"
typography:
  displayXl:
    fontFamily: Vazirmatn
    fontSize: 32px
    lineHeight: 40px
    fontWeight: 700
  displayL:
    fontFamily: Vazirmatn
    fontSize: 28px
    lineHeight: 36px
    fontWeight: 700
  h1:
    fontFamily: Vazirmatn
    fontSize: 24px
    lineHeight: 32px
    fontWeight: 700
  h2:
    fontFamily: Vazirmatn
    fontSize: 20px
    lineHeight: 28px
    fontWeight: 600
  h3:
    fontFamily: Vazirmatn
    fontSize: 18px
    lineHeight: 26px
    fontWeight: 600
  title:
    fontFamily: Vazirmatn
    fontSize: 16px
    lineHeight: 24px
    fontWeight: 600
  body:
    fontFamily: Vazirmatn
    fontSize: 14px
    lineHeight: 22px
    fontWeight: 400
  bodySm:
    fontFamily: Vazirmatn
    fontSize: 13px
    lineHeight: 20px
    fontWeight: 400
  label:
    fontFamily: Vazirmatn
    fontSize: 12px
    lineHeight: 18px
    fontWeight: 500
  caption:
    fontFamily: Vazirmatn
    fontSize: 11px
    lineHeight: 16px
    fontWeight: 400
spacing:
  space-1: 4px
  space-2: 8px
  space-3: 12px
  space-4: 16px
  space-5: 20px
  space-6: 24px
  space-7: 32px
  space-8: 40px
  space-9: 48px
  space-10: 64px
rounded:
  xs: 4px
  sm: 8px
  md: 12px
  lg: 16px
  xl: 20px
  pill: 999px
---

## Overview

POL adopts **Precision Commerce** as the canonical visual direction (Document ID: `POL-DESIGN-VISUAL-001` v2.0.0).
The design system delivers an operational B2B FMCG experience that is precise, professional, reliable, modern, clear, calm, and efficient.
It is an information-dense commerce interface supporting catalog search, multi-vendor comparison, order workflows, daily inventory confirmation, and operational queue triage across Light and Night themes with primary Persian RTL orientation.

## Colors

The color palette is strictly semantic and restrained. Neutral surfaces carry the majority of the visual area. Primary blue (`#2563EB` / `#60A5FA`) is reserved for primary interaction, active navigation, and deliberate emphasis. Accent indigo (`#4F46E5` / `#818CF8`) provides secondary emphasis. Semantic colors (success `#15803D`, warning `#B45309`, danger `#B91C1C`) appear only where operational meaning requires them.

## Themes

Light and Night are first-class peers. Night theme uses blue-charcoal tonal layers rather than pure black or inverted white cards.

| Token | Light Value | Night Value | Semantic Role |
|---|---|---|---|
| `bg.canvas` | `#F7F9FC` | `#0F141C` | App canvas background |
| `surface.default` | `#FFFFFF` | `#151C27` | Primary surface container |
| `surface.subtle` | `#F1F5F9` | `#1B2431` | Grouped/secondary surface |
| `surface.elevated` | `#FFFFFF` | `#202A38` | Modal, drawer, elevated layer |
| `border.subtle` | `#E2E8F0` | `#2A3646` | Standard divider and border |
| `border.strong` | `#CBD5E1` | `#3A4A5F` | Emphasized / focus border |
| `text.primary` | `#0F172A` | `#F8FAFC` | Primary high-contrast text |
| `text.secondary` | `#475569` | `#CBD5E1` | Supporting descriptive text |
| `text.muted` | `#64748B` | `#94A3B8` | Metadata, timestamps, captions |
| `text.disabled` | `#94A3B8` | `#64748B` | Disabled action and text |
| `brand.primary` | `#2563EB` | `#60A5FA` | Primary brand action |
| `brand.hover` | `#1D4ED8` | `#93C5FD` | Interactive hover state |
| `brand.active` | `#1E40AF` | `#3B82F6` | Pressed / active state |
| `brand.accent` | `#4F46E5` | `#818CF8` | Secondary brand accent |
| `semantic.success` | `#15803D` | `#4ADE80` | Success, verified, completed |
| `semantic.warning` | `#B45309` | `#FBBF24` | Warning, pending, attention |
| `semantic.danger` | `#B91C1C` | `#F87171` | Error, rejected, destructive |
| `semantic.info` | `#1D4ED8` | `#60A5FA` | Operational informational notices |
| `focus.ring` | `#2563EB` | `#93C5FD` | Accessible keyboard focus outline |

## Typography

Vazirmatn is the primary typeface for Persian content. Numeric values (prices in Toman, SKU, order IDs, quantities) must have stable digit alignment and tabular treatment without decorative treatments.

- **Display XL (32/40, Bold):** Top-level hero/landing page titles only.
- **Display L (28/36, Bold):** Major section introductions.
- **Heading 1 (24/32, Bold):** Canonical screen title and primary page header.
- **Heading 2 (20/28, SemiBold):** Major panel and section card titles.
- **Heading 3 (18/26, SemiBold):** Sub-section headers and modal headers.
- **Title (16/24, SemiBold):** Component titles, table column groupings.
- **Body (14/22, Regular):** Standard body text, form field values, descriptions.
- **Body Small (13/20, Regular):** Secondary data rows, dense list items.
- **Label (12/18, Medium):** Form labels, table headers, status chip text.
- **Caption (11/16, Regular):** Metadata, timestamps, helper text.

## Layout

A strict 4px base rhythm governs all layout, margins, and padding (`4, 8, 12, 16, 20, 24, 32, 40, 48, 64px`).
Information density is tailored by actor profile via density gears:

- **D1 — Spacious Commerce (Retailer):** 12px control Y-padding, 16px row padding, large touch targets (min 44px), generous whitespace, low cognitive load.
- **D2 — Balanced Operations (Vendor & General Web):** 10px control Y-padding, 12px row padding, structured list/table layouts, quick operational actions.
- **D3 — Dense Command (Operations):** 8px control Y-padding, 10px row padding, queue-first, exception-first, persistent contextual panels, keyboard-driven navigation.

## Elevation & Depth

Visual hierarchy is created primarily through surface layering and border distinction rather than heavy drop shadows:
- **Level 0 (Flat):** Canvas background (`bg.canvas`).
- **Level 1 (Card):** Default surface (`surface.default`) with subtle border (`border.subtle`). In Light theme, an optional restrained shadow (`0 1px 2px rgba(0,0,0,0.05)`) may be used.
- **Level 2 (Popout):** Menus, dropdowns, sticky action bars with subtle border and elevation.
- **Level 3 (Modal/Drawer):** Elevated surface (`surface.elevated`) with backdrop scrim. In Night theme, depth is achieved exclusively via surface luminance stepping (`#151C27` -> `#1B2431` -> `#202A38`).

## Shapes

- Interactive controls, buttons, and inputs utilize `radius.sm` (8px).
- Cards, panels, and content containers utilize `radius.md` (12px).
- Modals, drawers, and elevated sheets utilize `radius.lg` (16px).
- Status chips, badge tags, and pill indicators utilize `radius.pill` (999px). Pill shapes are never used for standard card containers.

## Components

- **Button:** Variants include `primary` (solid brand), `secondary` (subtle border/neutral surface), `outline` (transparent background with subtle border), `danger` (destructive action), and `ghost` (text only). Supports hover, active, focus-visible, loading (with non-blocking spinner), and disabled states.
- **Field & Input:** Clear label with 12px typography, 8px corner radius, 1px subtle border transitioning to 2px primary brand on focus. Explicit error state with helper text in `semantic.danger`.
- **StatusChip:** Compact pill status badge with tone mapping: `neutral` (default), `success` (active/delivered/approved), `warning` (pending/review/processing), `danger` (rejected/cancelled/failed), `info` (dispatched/allocated).
- **Table & DataRow:** Structured tabular presentation with sticky headers, clear column alignments, zebra or subtle dividers, and hover feedback on interactive rows.
- **State Feedback:** Skeletons for pending content, explicit EmptyState with contextual primary action, and ErrorState with recovery action.

## Do's and Don'ts

- Do maintain full Light and Night visual parity on every screen and component.
- Do keep Persian typography in Vazirmatn with correct RTL reading order and layout rails.
- Do use tabular digits for prices, quantities, order numbers, and SKU codes.
- Do preserve WCAG 2.2 AA contrast ratios on all text and interactive borders.
- Don't use purple-to-blue gradient backgrounds or decorative glassmorphism.
- Don't use color as the single communication channel for state or status.
- Don't mirror semantically non-directional icons in RTL mode (e.g. search, settings, barcode).
- Don't introduce arbitrary one-off hex colors outside the canonical semantic tokens.
