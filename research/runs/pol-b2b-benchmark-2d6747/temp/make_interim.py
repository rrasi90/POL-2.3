import os

notes_dir = r"research/notes"
os.makedirs(notes_dir, exist_ok=True)

def write_interim(filename, title, tags, content):
    tag_str = "\n".join([f"  - {t}" for t in tags])
    doc = f"""---
id: {filename.replace('.md', '')}
title: "{title}"
tags:
{tag_str}
created: 2026-09-03
tier: institutional
type: interim
status: evergreen
utility_score: 19.0
---

{content.strip()}
"""
    path = os.path.join(notes_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(doc.strip() + "\n")
    print(f"Generated interim note: {filename}")

# Locus 1
write_interim("interim-locus-asset-light.md",
    "Interim Note: Asset-Light Structural Defensibility vs 1P Inventory Distribution",
    ["pol-b2b-benchmark-2d6747", "locus-asset-light-structural-defensibility", "interim"],
    """# Interim Note: Asset-Light Structural Defensibility vs 1P Inventory Distribution

## 1. Synthesis of Evidence
Analysis of 28 global benchmarks demonstrates an overwhelming bifurcation:
- Every major 1P B2B FMCG player in emerging markets (Wasoko, MaxAB, Capiter, Ula, Retailo, early Udaan) suffered catastrophic capital destruction, downrounds, debt defaults, or liquidation.
- The fundamental root cause is structural: FMCG gross margins on branded staples are 3% to 6%. Operating a 1P network of leased central warehouses, proprietary truck fleets, and delivery personnel costs 8% to 12% of GMV. In high-inflation economies (Egypt, Kenya, Pakistan, Nigeria, Iran), currency devaluation destroys the replacement value of warehouse inventory.
- Conversely, pure asset-light platforms (Cartona in Egypt, OmniRetail in Nigeria, PriyoShop in Bangladesh) survived macroeconomic crises, achieved positive EBIT/EBITDA, and scaled rapidly by turning traditional wholesalers into fulfillment partners.

## 2. Counter-Arguments & Trade-offs
Critics argue that asset-light models sacrifice fulfillment control (lower OTIF) and face severe disintermediation risks. However, the evidence reveals that OTIF issues can be resolved via algorithmic vendor scoring and financial escrow, whereas the negative unit economics of 1P warehouse operations cannot be solved even with hundreds of millions in venture capital.

## 3. Committed position
**Position:** POL must commit unequivocally to a 100% Asset-Light marketplace middleware architecture for its baseline FMCG distribution. POL must not own warehouses, must not buy truck fleets, and must not hold inventory on its balance sheet.
**Confidence Level:** HIGH (95%).
**What evidence would change my mind:** If an empirical case emerges in an emerging market with >30% inflation where a 1P FMCG startup achieved sustained, un-subsidized net profitability while owning warehouses and trucks (zero such cases exist to date)."""
)

# Locus 2
write_interim("interim-locus-anti-disintermediation.md",
    "Interim Note: Anti-Disintermediation Architecture & Mathematical Anti-Bypass Moats",
    ["pol-b2b-benchmark-2d6747", "locus-anti-disintermediation-mechanisms", "interim"],
    """# Interim Note: Anti-Disintermediation Architecture & Mathematical Anti-Bypass Moats

## 1. Synthesis of Evidence
Platform bypass is the fatal flaw of shallow directories (e.g., GudangAda crisis in Indonesia). When a platform offers only a catalog, merchants bypass it to save 2% commission.
However, evidence from OmniRetail (Nigeria), Cartona (Egypt), and VinShop (Vietnam) proves that bypass is eliminated when the platform embeds 4 non-replicable operational workflows:
1. Multi-vendor basket aggregation (supermarkets buy 40 SKUs from 3 wholesalers in 1 single digital checkout; offline bypassing requires 3 separate calls, 3 reconciliations, and 3 payments).
2. Embedded bank credit lines (pre-approved working capital is usable ONLY for transactions executed through the platform).
3. Wholesaler operating software (Mplify model: running daily warehouse inventory, invoicing, and driver dispatch through POL software).
4. Direct manufacturer promotional rebates (Unilever/Kaleh rebates credited exclusively on digital app orders).

## 2. Committed position
**Position:** Platform bypass is not an inevitable fate; it is the consequence of lazy product design. POL can achieve near-zero bypass by making the economic, operational, and financing penalty of bypassing the platform vastly exceed the 2-3% platform take rate.
**Confidence Level:** HIGH (90%).
**What evidence would change my mind:** If retailers in test clusters systematically forfeit 30-day bank credit lines and manufacturer volume discounts solely to make offline phone calls to individual wholesalers."""
)

# Locus 3
write_interim("interim-locus-embedded-credit.md",
    "Interim Note: Embedded Credit Architecture & Default Insulation via Bank Partnerships",
    ["pol-b2b-benchmark-2d6747", "locus-embedded-credit-default-insulation", "interim"],
    """# Interim Note: Embedded Credit Architecture & Default Insulation via Bank Partnerships

## 1. Synthesis of Evidence
In emerging markets, access to working capital is the single most powerful retention driver.
- Platforms that lent from their own equity or borrowed venture debt (Capiter, TradeDepot, early Udaan) suffered severe default spikes, liquidity crises, and balance-sheet insolvency.
- Successful platforms (VinShop with Techcombank, Cartona with AMAN and Contact Financial, Jumbotail with SC Ventures / Standard Chartered) acted strictly as data underwriting intermediaries. The bank provides the balance sheet, capital, and regulatory umbrella; the platform provides real-time SKU velocity, transaction frequency, and default risk scoring.

## 2. Committed position
**Position:** POL must never become a licensed bank and must never lend from its own equity balance sheet. POL must establish a tripartite partnership with leading Iranian commercial banks (بانک‌های عامل), providing transaction underwriting telemetry and Sayadi cheque verification while the bank carries credit risk and disburses funds directly to wholesalers.
**Confidence Level:** HIGH (95%).
**What evidence would change my mind:** If Iranian commercial banks completely refuse to provide credit facilities to MSME retail networks even when backstopped by transaction data and verified Sayadi cheques."""
)

# Locus 4
write_interim("interim-locus-cart-allocation.md",
    "Interim Note: Cart Allocation & Dynamic Clustered Routing Algorithm",
    ["pol-b2b-benchmark-2d6747", "locus-cart-allocation-dynamic-clustering", "interim"],
    """# Interim Note: Cart Allocation & Dynamic Clustered Routing Algorithm

## 1. Synthesis of Evidence
Single-vendor carts cause up to 45% basket abandonment due to stockouts on key SKUs. Conversely, unconstrained multi-vendor carts (Udaan model) create logistical chaos: 4-5 delivery trucks arrive at a cramped neighborhood grocery store at random hours, infuriating store owners.
The optimal solution, deployed by OmniRetail and mature Cartona, is **Dynamic Clustered Routing (capping vendor drops to maximum 2 per order)**.

## 2. Committed position
**Position:** POL must implement an algorithmic Smart Basket Optimizer that groups multi-SKU carts into a maximum of 2 fulfillment wholesalers based on price, stock availability, vendor MOQs, and morning delivery window alignment, presenting a unified single digital invoice to the supermarket.
**Confidence Level:** HIGH (90%).
**What evidence would change my mind:** If field testing reveals that supermarkets strongly prefer a single-wholesaler order even when it costs 8% more and has 3 missing SKUs."""
)

# Locus 5
write_interim("interim-locus-phygital-migration.md",
    "Interim Note: Phygital Field Force Lifecycle & Autonomous Re-Order Habituation",
    ["pol-b2b-benchmark-2d6747", "locus-phygital-field-force-migration-velocity", "interim"],
    """# Interim Note: Phygital Field Force Lifecycle & Autonomous Re-Order Habituation

## 1. Synthesis of Evidence
Traditional mom-and-pop grocery owners are non-tech-savvy and distrustful of cold digital marketing.
- Every successful emerging market benchmark relied on human field agents for initial store mapping, app installation, and placing the first 3 orders.
- However, permanent sales reps create unsustainable OpEx ($10-$15 per order).
- Successful platforms engineered a 90-day transition: compensating reps based on **Autonomous Re-Order Migration Rate**, transitioning store owners to self-serve ordering between 9 PM and midnight after closing their shops. Over 75-80% of mature reorders become digital self-serve, allowing sales reps to manage 250+ stores each.

## 2. Committed position
**Position:** POL must deploy a dedicated, territory-mapped field force in Tehran for the cold-start phase, but structure rep compensation strictly around migrating supermarkets to autonomous night-time ordering within 90 days. Reps then evolve into relationship managers and financial onboarding agents.
**Confidence Level:** HIGH (95%).
**What evidence would change my mind:** If supermarkets in pilot districts refuse to place orders autonomously after 5 assisted orders and require ongoing in-person visits to book standard inventory."""
)

print("All 5 interim notes successfully written.")
