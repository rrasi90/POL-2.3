import os

temp_dir = r"research/runs/pol-b2b-benchmark-2d6747/temp"

draft_a = """# POL B2B Strategy Report — Draft A: Empirical Benchmarks & Operational Mechanics

## Angle: Operational Realism & Global Comparative Archetypes
This draft anchors on empirical evidence across 28 global platforms (Cartona, OmniRetail, Bazaar, GrowSari, Jumbotail, Chari, Wasoko, MaxAB, Udaan, Capiter).

### Key Empirical Findings:
1. Asset-Light vs 1P: 1P inventory distribution in FMCG has an inverted cost structure (3-5% gross margins vs 8-12% logistics OpEx). 1P models in high-inflation environments (Wasoko, MaxAB, Capiter) experienced severe downrounds, shutdowns, or restructuring by 2024-2026. Asset-light models (OmniRetail, Cartona) achieved operating profitability (EBITDA positive) at 80%+ gross margin on net commissions.
2. Anti-Bypass Defensibility: Pure price-comparison directories (e.g. GudangAda) suffer severe disintermediation. Platforms that survive bundle multi-vendor cart consolidation, embedded credit, wholesaler ERP, and manufacturer trade promotions.
3. Phygital Migration: Reps are essential for the first 3 orders, but order booking must transition to autonomous night-time ordering (9 PM - 12 AM). Cartona and Bazaar reached >75-80% autonomous re-order rates within 90 days.
"""

draft_b = """# POL B2B Strategy Report — Draft B: Structural Economics & Financial Architecture

## Angle: Unit Economics, Capital Efficiency & Regulatory Clearing
This draft focuses on the financial mechanics, margin decomposition, Cheque Sayadi underwriting, and bank integration in Iran.

### Key Economic Insights:
1. Capital Insulation: POL must never lend off its own balance sheet. Lending from equity led to the Capiter collapse, TradeDepot write-downs, and Udaan's 2026 debt default. POL operates as a technology and underwriting layer for partner commercial banks.
2. Iranian Market Structure: Greater Tehran represents ~25-30% of Iran's $25B-$35B FMCG trade. Traditional Banakdaran in Molavi and Anbar Naft have deep capital and warehouse networks. POL partners with them as fulfillment nodes.
3. Cheque Sayadi Architecture: Sayadi purple cheques registered with the Central Bank of Iran provide legal enforceability. POL links transaction frequency to pre-approved credit lines underwritten by partner banks.
"""

draft_c = """# POL B2B Strategy Report — Draft C: Execution Thesis, Product Architecture & Cold-Start Playbook

## Angle: Product Systems, Cart Routing & Phased Tehran Go-To-Market
This draft develops the actionable roadmap, algorithmic specification, and organizational execution for POL.

### Key Product & Execution Choices:
1. Cart Allocation Algorithm: Enforces Dynamic Clustered Routing capping vendor splits to maximum 2 delivery drops per order, balancing SKU availability with store reception constraints.
2. The 3-Phase Phygital Playbook: Territory mapping in Tehran Districts 2 and 4. Reps incentivize store owners to order autonomously at night, scaling rep productivity from 50 to 250+ stores.
3. Rumelt Strategic Thesis: Clear diagnosis of traditional wholesale fragmentation, guiding policy of asset-light middleware, and coherent operational actions.
"""

with open(os.path.join(temp_dir, "draft-a.md"), "w", encoding="utf-8") as f:
    f.write(draft_a.strip() + "\n")

with open(os.path.join(temp_dir, "draft-b.md"), "w", encoding="utf-8") as f:
    f.write(draft_b.strip() + "\n")

with open(os.path.join(temp_dir, "draft-c.md"), "w", encoding="utf-8") as f:
    f.write(draft_c.strip() + "\n")

print("Triple drafts (a, b, c) successfully generated.")
