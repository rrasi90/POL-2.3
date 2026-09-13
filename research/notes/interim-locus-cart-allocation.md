---
id: interim-locus-cart-allocation
title: "Interim Note: Cart Allocation & Dynamic Clustered Routing Algorithm"
tags:
  - pol-b2b-benchmark-2d6747
  - locus-cart-allocation-dynamic-clustering
  - interim
created: 2026-09-03
tier: institutional
type: interim
status: evergreen
utility_score: 19.0
---

# Interim Note: Cart Allocation & Dynamic Clustered Routing Algorithm

## 1. Synthesis of Evidence
Single-vendor carts cause up to 45% basket abandonment due to stockouts on key SKUs. Conversely, unconstrained multi-vendor carts (Udaan model) create logistical chaos: 4-5 delivery trucks arrive at a cramped neighborhood grocery store at random hours, infuriating store owners.
The optimal solution, deployed by OmniRetail and mature Cartona, is **Dynamic Clustered Routing (capping vendor drops to maximum 2 per order)**.

## 2. Committed position
**Position:** POL must implement an algorithmic Smart Basket Optimizer that groups multi-SKU carts into a maximum of 2 fulfillment wholesalers based on price, stock availability, vendor MOQs, and morning delivery window alignment, presenting a unified single digital invoice to the supermarket.
**Confidence Level:** HIGH (90%).
**What evidence would change my mind:** If field testing reveals that supermarkets strongly prefer a single-wholesaler order even when it costs 8% more and has 3 missing SKUs.
