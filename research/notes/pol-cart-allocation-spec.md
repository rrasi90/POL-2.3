---
id: pol-cart-allocation-spec
title: "Technical Specification: POL Smart Basket Optimization Algorithm"
tags:
  - pol-b2b-benchmark-2d6747
  - algorithm-spec
  - cart-allocation
created: 2026-09-03
tier: institutional
type: note
status: evergreen
utility_score: 18.5
---

# Technical Specification: POL Smart Basket Optimization Algorithm

Inputs:
- Shopping Cart items {SKU_i, Quantity_i}
- Wholesaler inventory matrix {Stock_v, SKU_i, Price_v, SKU_i}
- Wholesaler MOQ constraints {MOQ_v}
- Delivery fee matrix {DeliveryFee_v}
- Cutoff time and delivery window constraints {DeliveryWindow_v}

Objective:
Minimize Total Cost = Sum(Price_v,i * Q_i) + Sum(DeliveryFee_v)
Subject to:
1. Vendor Count <= 2 (Strict maximum 2 drops per order)
2. Sub-basket value per vendor >= MOQ_v
3. All selected items fulfilled in full without stockout risk

Output:
Optimal basket allocation presented to retailer with single-click checkout.
