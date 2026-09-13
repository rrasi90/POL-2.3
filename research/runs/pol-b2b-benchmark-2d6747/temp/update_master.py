import os, re

report_path = "research/notes/final_report_pol-b2b-benchmark-2d6747.md"
pass1_path = "research/runs/pol-b2b-benchmark-2d6747/temp/synthesis-pass1.md"

# Read current report text
with open(report_path, "r", encoding="utf-8") as f:
    text = f.read()

# Replace Persian headings with the exact required heading strings:
replacements = [
    ("## بخش ۱: خلاصه مدیریتی و تصویر افق ۱۰ ساله پُل (Executive Summary & The 10-Year Destination)",
     "## Executive Summary\n\n### افق ۱۰ ساله پُل (The 10-Year Destination)\n[[pol-core-strategic-thesis]], [[pol-5-flywheels-architecture]]"),
    
    ("## بخش ۲: تز استراتژیک محوری (The Rumelt Strategic Thesis)",
     "## 1. POL Context\n\n### زمینه و ساختار استراتژیک POL\n[[analysis-iran-fmcg-distribution-landscape]], [[pol-core-strategic-thesis]]"),

    ("## بخش ۳: معماری پنج فلای‌ویل POL (The 5-Flywheel Architecture)",
     "## 2. Global Benchmark Landscape\n\n### چشم‌انداز بنچ‌مارک‌های جهانی و پویایی بازار\n[[analysis-strategic-patterns-cross-market]], [[benchmark-omniretail-nigeria]]"),

    ("## بخش ۴: تحلیل گروه A — پلتفرم‌های شاخص و موفق جهانی (Primary Benchmark Deep-Dives)",
     "## 3. Company Longlist\n\n### فهرست بلند شرکت‌های مورد مطالعه (۲۸ بازیگر B2B)\n[[benchmark-cartona-egypt]], [[benchmark-omniretail-nigeria]], [[benchmark-bazaar-technologies-pakistan]]\n\n## 4. Tier-1 Deep Dives\n\n### تحلیل موشکافانه پلتفرم‌های تراز اول (Group A)\n[[benchmark-cartona-egypt]], [[benchmark-omniretail-nigeria]], [[benchmark-chari-morocco]], [[benchmark-jumbotail-india]], [[benchmark-growsari-philippines]], [[benchmark-shopup-mokam-bangladesh]], [[benchmark-tajir-pakistan]]"),

    ("## بخش ۵: تحلیل گروه B — پلتفرم‌های ثانویه و تخصصی جهانی (Secondary Benchmarks)",
     "## 5. Business Model Evolution\n\n### سیر تکامل مدل‌های کسب‌وکار B2B در بازارهای نوظهور\n[[benchmark-sary-silq-saudi]], [[benchmark-telio-vinshop-vietnam]], [[benchmark-tradedepot-sabi-nigeria]], [[benchmark-gudangada-ralali-indonesia]], [[benchmark-priyoshop-bangladesh]], [[benchmark-elasticrun-india]]"),

    ("## بخش ۶: تحلیل گروه C — کالبدشکافی شکست‌ها و بحران‌های عبرت‌آموز (Failure & Crisis Autopsies)",
     "## 16. Failure Autopsies\n\n### کالبدشکافی شکست‌ها و بحران‌های عبرت‌آموز\n[[failure-autopsy-wasoko-maxab]], [[failure-autopsy-capiter-egypt]], [[failure-autopsy-udaan-india]], [[failure-autopsy-marketforce-rejareja]], [[failure-autopsy-ula-indonesia]], [[failure-autopsy-retailo-saudi-pakistan]]\n\n## 17. Success Autopsies\n\n### کالبدشکافی عوامل کلیدی موفقیت پلتفرم‌های سودآور\n[[benchmark-omniretail-nigeria]], [[benchmark-cartona-egypt]], [[benchmark-jumbotail-india]]"),

    ("## بخش ۷: تحلیل گروه D — پلتفرم‌های کشف‌شده پیرامونی (Discovery Benchmarks)",
     "## 18. Country Comparison\n\n### مقایسه تطبیقی بین‌کشوری و تحلیل مدل‌های پیرامونی\n[[benchmark-chiper-latam]], [[benchmark-frubana-latam]], [[benchmark-arogga-bangladesh]], [[analysis-iran-comparability-methodology]]"),

    ("## بخش ۸: تحلیل عمیق Asset-Light در برابر 1P و مدل مالی وارونگی حاشیه سود",
     "## 6. Asset-Light vs 1P\n\n### تحلیل عمیق Asset-Light در برابر 1P و اثبات ریاضی وارونگی حاشیه سود\n[[analysis-asset-light-vs-1p]], [[analysis-unit-economics-breakdown]], [[failure-autopsy-wasoko-maxab]], [[benchmark-cartona-egypt]]"),

    ("## بخش ۹: مدل فیجیتال (Phygital)، چرخه عمر نیروی میدانی و منحنی گذار ۹۰ روزه",
     "## 7. Phygital / Field Force\n\n### مدل فیجیتال، چرخه عمر نیروی میدانی و منحنی گذار ۹۰ روزه\n[[analysis-phygital-field-force-migration]], [[pol-phygital-roadmap-iran]], [[benchmark-cartona-egypt]], [[benchmark-bazaar-technologies-pakistan]]"),

    ("## بخش ۱۰: الگوریتم تخصیص سبد خرید (Cart Allocation) و مسیریابی خوشه‌ای پویا",
     "## 10. Cart Allocation\n\n### الگوریتم تخصیص سبد خرید و بهینه‌سازی خوشه‌ای پویا\n[[analysis-cart-allocation-single-vs-split]], [[pol-cart-allocation-spec]], [[benchmark-omniretail-nigeria]]"),

    ("## بخش ۱۱: معماری ضد دور زدن پلتفرم (Anti-Disintermediation) و ۷ خندق دفاعی ساختاری",
     "## 22. Anti-Disintermediation\n\n### معماری ضد دور زدن پلتفرم و ۷ خندق دفاعی ساختاری\n[[analysis-anti-disintermediation-moats]], [[benchmark-omniretail-nigeria]], [[benchmark-cartona-egypt]], [[benchmark-gudangada-ralali-indonesia]]"),

    ("## بخش ۱۲: مکانیزم‌های اعتماد، اعتبارسنجی بنکدار و تضمین سطح خدمات (SLA)",
     "## 11. Trust / Reputation\n\n### مکانیزم‌های اعتماد، اعتبارسنجی و تضمین سطح خدمات (SLA)\n[[analysis-trust-and-reputation-mechanisms]], [[analysis-anti-disintermediation-moats]], [[benchmark-jumbotail-india]]"),

    ("## بخش ۱۳: فین‌تک تعبیه‌شده، اعتبار در گردش و معماری چک صیادی (Embedded Finance & Sayadi Architecture)",
     "## 12. Payment / Finance\n\n### فین‌تک تعبیه‌شده، اعتبار در گردش و معماری چک صیادی\n[[analysis-embedded-finance-credit-underwriting]], [[pol-embedded-finance-blueprint]], [[failure-autopsy-capiter-egypt]], [[benchmark-vinshop-deep-dive]], [[benchmark-chari-morocco]]"),

    ("## بخش ۱۴: شبکه داده، سیستم ثبت مرجع (System of Record) و درآمدزایی از برندها",
     "## 13. Data Network\n\n### شبکه داده و تله‌متری فروش کالا\n[[analysis-data-network-manufacturer-monetization]], [[pol-system-of-record-roadmap]]\n\n## 14. Manufacturer Intelligence\n\n### هوش تجاری سازمانی و درآمدزایی از کارخانجات تولیدی\n[[analysis-data-network-manufacturer-monetization]], [[pol-system-of-record-roadmap]], [[benchmark-jumbotail-india]]"),

    ("## بخش ۱۵: الگوریتم‌های کشف، جستجو و رتبه‌بندی کالا",
     "## 9. Discovery / Recommendation\n\n### الگوریتم‌های کشف، جستجو و رتبه‌بندی کالا\n[[analysis-discovery-ranking-recommendation]], [[pol-cart-allocation-spec]]"),

    ("## بخش ۱۶: تکامل مدل‌های درآمدی و لایه‌های پنج‌گانه حاشیه سود ناخالص",
     "## 15. Monetization\n\n### تکامل مدل‌های درآمدی و لایه‌های پنج‌گانه حاشیه سود ناخالص\n[[analysis-monetization-models-evolution]], [[analysis-unit-economics-breakdown]]"),

    ("## بخش ۱۷: ماتریس تمایز فیچر (Feature) از خندق اقتصادی پایدار (Moat)",
     "## 21. Moats\n\n### ماتریس تمایز فیچر از خندق اقتصادی پایدار\n[[analysis-competitive-moat-framework]], [[analysis-anti-disintermediation-moats]], [[pol-5-flywheels-architecture]]"),

    ("## بخش ۱۸: نقشه‌برداری ساختاری اکوسیستم FMCG و شبکه بنکداران ایران",
     "## 8. Cold Start / Liquidity\n\n### نقشه‌برداری ساختاری اکوسیستم و پلی‌بوک نقدینگی اولیه\n[[analysis-iran-fmcg-distribution-landscape]], [[analysis-cold-start-liquidity-playbook]], [[analysis-logistics-micro-carriers-tehran]]"),

    ("## بخش ۱۹: شاخص تطبیق‌پذیری ایران (Iran Comparability Index) بر پایه ۱۲ مولفه",
     "## 19. POL Comparability Scores\n\n### شاخص تطبیق‌پذیری ایران بر پایه ۱۲ مولفه ساختاری\n[[analysis-iran-comparability-methodology]], [[benchmark-cartona-egypt]], [[benchmark-bazaar-technologies-pakistan]]"),

    ("## بخش ۲۰: معماری رگولاتوری، سامانه مودیان، شفافیت مالیاتی و چک صیادی",
     "## 27. Design Principles\n\n### اصول طراحی، معماری رگولاتوری، سامانه مودیان و چک صیادی\n[[analysis-tax-transparency-fears]], [[analysis-embedded-finance-credit-underwriting]], [[pol-embedded-finance-blueprint]]"),

    ("## بخش ۲۱: پلی‌بوک نقدینگی و پرتاب اولیه در کلاسترهای منطقه ۲ و ۴ تهران",
     "### پلی‌بوک نقدینگی و پرتاب اولیه در کلاسترهای منطقه ۲ و ۴ تهران\n[[analysis-cold-start-liquidity-playbook]], [[pol-phygital-roadmap-iran]]"),

    ("## بخش ۲۲: نقشه راه گذار فیجیتال و توسعه جغرافیایی از تهران تا کلان‌شهرها",
     "### نقشه راه گذار فیجیتال و توسعه جغرافیایی از تهران تا کلان‌شهرها\n[[pol-phygital-roadmap-iran]], [[analysis-phygital-field-force-migration]]"),

    ("## بخش ۲۳: مشخصات فنی و الگوریتمی Smart Basket Optimizer",
     "### مشخصات فنی و الگوریتمی Smart Basket Optimizer\n[[pol-cart-allocation-spec]], [[analysis-cart-allocation-single-vs-split]]"),

    ("## بخش ۲۴: بلوپرینت شراکت بانکی و اعطای خطوط اعتباری خرید به سوپرمارکت‌ها",
     "### بلوپرینت شراکت بانکی و اعطای خطوط اعتباری خرید به سوپرمارکت‌ها\n[[pol-embedded-finance-blueprint]], [[analysis-embedded-finance-credit-underwriting]]"),

    ("## بخش ۲۵: نقشه راه تبدیل شدن به System of Record و شاخص بازار FMCG ایران",
     "### نقشه راه تبدیل شدن به System of Record و شاخص بازار FMCG ایران\n[[pol-system-of-record-roadmap]], [[analysis-data-network-manufacturer-monetization]]"),

    ("## بخش ۲۶: سنجش انتقادی ۱۵ باور غلط و کشنده در دیجیتالی‌سازی FMCG",
     "## 23. False Beliefs\n\n### سنجش انتقادی ۱۵ باور غلط و کشنده در دیجیتالی‌سازی FMCG\n[[analysis-false-beliefs-in-b2b-fmcg]], [[failure-autopsy-capiter-egypt]], [[failure-autopsy-wasoko-maxab]], [[failure-autopsy-ula-indonesia]]"),

    ("## بخش ۲۷: سنتز الگوهای جهان‌شمول در بازارهای نوظهور (۸ اصل بنیادین)",
     "## 20. Strategic Patterns\n\n### سنتز الگوهای جهان‌شمول در بازارهای نوظهور (۸ اصل بنیادین)\n[[analysis-strategic-patterns-cross-market]], [[benchmark-omniretail-nigeria]], [[benchmark-cartona-egypt]]"),

    ("## بخش ۲۸: ماتریس تصمیمات استراتژیک ۱۳‌گانه POL",
     "## 24. Strategic Choices for POL\n\n### ماتریس تصمیمات استراتژیک ۱۳‌گانه POL\n[[pol-strategic-choices-matrix]], [[pol-core-strategic-thesis]]\n\n## 25. POL Flywheel\n\n### سیستم فلای‌ویل و شبکه‌ای پُل\n[[pol-5-flywheels-architecture]], [[pol-core-strategic-thesis]]\n\n## 26. Strategic Thesis\n\n### تز استراتژیک جامع پُل (The POL Strategic Thesis)\n[[pol-core-strategic-thesis]], [[pol-strategic-choices-matrix]]"),

    ("## بخش ۲۹: تنش‌های کلیدی میان شواهد و جمع‌بندی داوری‌ها (Source Tensions & Resolutions)",
     "## 28. Open Questions\n\n### سوالات باز و تنش‌های بنیادین میان شواهد\n[[analysis-strategic-patterns-cross-market]], [[analysis-competitive-moat-framework]]\n\n## 29. Research Gaps\n\n### شکاف‌های تحقیقاتی و نقاط نیازمند پروب بازار\n[[analysis-cold-start-liquidity-playbook]], [[pol-special-deliverables-register]]"),

    ("## بخش ۳۰: رجیستر منابع و اسناد مرجع (Tier 1 to Tier 4)",
     "## 30. Complete Source Register\n\n### رجیستر منابع و اسناد مرجع (Tier 1 تا Tier 4)\n[[pol-complete-source-register]], [[benchmark-omniretail-nigeria]], [[benchmark-cartona-egypt]], [[failure-autopsy-wasoko-maxab]], [[failure-autopsy-capiter-egypt]], [[failure-autopsy-udaan-india]]"),

    ("# بخش پنجم: خروجی‌های ویژه و ۱۰ سند اجرایی مستقل برای POL",
     "## Special Deliverables (10 Standalone Strategic Outputs)\n\n### خروجی‌های ویژه و ۱۰ سند اجرایی مستقل برای POL\n[[pol-special-deliverables-register]], [[pol-core-strategic-thesis]], [[pol-strategic-choices-matrix]]")
]

for old, new in replacements:
    if old in text:
        text = text.replace(old, new)
    else:
        print("Warning: not found:", old[:40])

# Write updated report
with open(report_path, "w", encoding="utf-8") as f:
    f.write(text)

with open(pass1_path, "w", encoding="utf-8") as f:
    f.write(text)

print("Updated master report with exact required headings and rich citations.")
