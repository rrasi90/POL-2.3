---
id: analysis-embedded-finance-credit-underwriting
title: "Embedded Finance & Credit Architecture: Lending Without Balance Sheet Exposure"
tags:
  - pol-b2b-benchmark-2d6747
  - embedded-finance
  - credit-underwriting
created: 2026-09-03
tier: institutional
type: note
status: evergreen
utility_score: 18.5
---

# Embedded Finance & Credit Architecture: Lending Without Balance Sheet Exposure

## 1. The Core Dilemma: To Lend or Not to Lend?
In emerging market retail, credit is the single highest driver of order conversion and retention. Over 70% of traditional retailers cite lack of working capital as their primary growth barrier.
However, when platforms lend from their own balance sheet (Capiter, TradeDepot, early Udaan), they take on severe default risks, regulatory banking scrutiny, and balance-sheet write-offs that destroy enterprise value.

## 2. The Winning Hybrid Model: Data Underwriting + Bank Capital
The surviving and profitable platforms (Cartona, OmniRetail, VinShop, Chari) follow a strict tripartite architecture:
1. POL provides: Proprietary transaction data, purchase frequency, SKU velocity, order completion history, and Sayadi cheque verification.
2. Bank/Fintech provides: Legal credit license, risk capital, balance sheet, and regulatory underwriting.
3. The Settlement Mechanism: The loan never touches the retailer hands as liquid cash. When the retailer places an order on POL, the bank pays the wholesaler directly; the retailer owes the bank within 14-30 days.

## 3. Risk Signals & Underwriting Parameters
POL calculates a real-time Dynamic Merchant Credit Limit (DMCL):
- Baseline Turnover: 25% of average monthly verified purchasing volume on POL.
- Velocity Factor: Orders placed per month (>8 orders/month increases credit cap).
- Repayment Integrity: Zero bounced cheques in the national Sayadi registry over the trailing 12 months.
- First-Loss Guarantees (FLDG): POL may provide a 2% to 5% first-loss pool funded by transaction fees to absorb minor delays, while the bank carries structural default risk.
