---
id: analysis-cart-allocation-single-vs-split
title: "Cart Allocation Architecture: Single-Vendor vs Split-Cart Optimization in B2B FMCG"
tags:
  - pol-b2b-benchmark-2d6747
  - cart-allocation
  - product-design
  - algorithmic-routing
created: 2026-09-03
source: "Engineering & Operational Benchmarks (Cartona, OmniBiz, Jumbotail, Udaan)"
tier: institutional
type: note
status: evergreen
utility_score: 17.5
---

# Cart Allocation Architecture: Single-Vendor vs Split-Cart Optimization

## 1. Recommended Cart Specification for POL (Iran)
- **The Smart Basket Optimizer Engine:** When a supermarket owner adds 20 SKUs to their cart, POL backend algorithm optimizes for Minimum Split Count (max 2 vendors) based on Total Price, Vendor MOQs, and Delivery Window Alignment.
- **User Interface Transparency:**
  - Option 1 (Fastest & Simplest): Fulfill entirely by Wholesaler X (1 delivery drop tomorrow at 9 AM).
  - Option 2 (Lowest Price): Fulfill by Wholesaler X + Wholesaler Y (2 delivery drops, Saves money).
- **Strict MOQ Enforcement:** Wholesalers set their own Minimum Order Quantity (e.g., minimum 5M Tomans). Sub-baskets below MOQ prompt the user to substitute items or add volume.
- **Unified Single Invoice & Single Settlement:** Regardless of backend split, the retailer receives one consolidated digital invoice from POL and settles via one payment or Sayadi Cheque. POL handles backend clearing.
