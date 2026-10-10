# 08 — Money Surfaces & Growth Loops

Wallet, BNPL installments, rewards, quizzes, campaigns. Evidence: ps3, ps4, strings, events, flags.

---

## 8.1 Wallet (محفظة كرتونة)

- Entry: credit-home widget "رصيد المحفظة" + "شحن المحفظة" CTA, profile, checkout toggle (`wallet_clicked`, `viewWallet`, `legacyWalletTopUp`)
- Strings reveal full feature set:
  - "رصيد محفظة كرتونة"، "رصيد فوري"
  - "شحن المحفظة" (top-up), "تم الشحن"
  - "تاريخ معاملات المحفظة" (transaction history)
  - "حدود استخدام المحفظة" (usage limits policy screen)
  - "خصم من المحفظة"، "مبلغ المحفظة غير صحيح" (validation)
  - "اتضافت لمحفظتك" (credit added)
  - Refund automation: "تم إلغاء الطلب بنجاح. وفي حالة استخدام أي رصيد من محفظة كرتونة، هيتم رد المبلغ تلقائياً خلال وقت قصير"
  - Cashback crediting: "سيتم إضافة المبلغ إلى رصيدك في محفظة كرتونة بعد استلام الطلب"
- Cart checkout partial usage (see 06)

## 8.2 Installments / BNPL (كرتونة بالأجل) — ps4 + wizard events

- **Activation wizard** (multi-step): `installment_wizard_step_viewed` — collects "الحد الإئتماني المطلوب (قيمة الفلوس اللي هتحتاجها)" (requested credit limit) + "الإيراد الشهري (المبيعات والطلبيات والفواتير)" (monthly revenue) → `installment_activation_requested` / `installment_activation_request_failed2` / pending state (`installment_activation_pending_viewed2`)
- Credit dashboard (ps4): used/limit + progress + wallet + dues list ("المستحقات")
- Pay-later marketing home skin ("اشتري دلوقتي وادفع بعدين"، "ادفع بعدين"، "ادفع براحتك")
- Installment plan picker: "اختر خطة الدفع"، "ادفع طلباتك على دفعات"، "طلب تقسيط الآن"، "تأكيد التقسيط"، "لم يتم تأكيد التقسيط. حاول مرة أخرى" — **plan selection is a distinct confirmation step**
- Bottom-nav legacy installment tab (`bottom_navigation_legacy_installment_clicked`) + finance web-app bridge (`CARTONA_FINANCE_WEB_APP_BASE_URL`, `IONIC_APP_URL` — a separate finance web app embedded)

## 8.3 Payments hub

- `payments_section_viewed` — aggregate screen for methods/dues/statements
- Payment method vocabulary across surfaces: كاش (cash), كاش باك (cashback), تفسيط (installments), عند الاستلام (COD), ربح كرتونة (Cartona profit), دفعات (installment plans), "من إجمالي الطلب"

## 8.4 Rewards / goals (الأهداف والمكافآت)

- Gamified targets tied to purchase volume: "برافو! وصلت لأول مكافأة - كمّل عشان توصل لـ …"، "تم الوصول للهدف! في انتظار إغلاق فترة الهدف لاستلام المكافآت"، "لو وصلت للمستوى التالي، المكافأة الأكبر هتحل محل الحالية" (tier replacement rule), "لا توجد أهداف منتهية الصلاحية"
- Home widget (`goals_widget_clicked`)
- Cashback mechanics: "الحد الأقصى للكاش باك"، "% للحفاظ على توازن طرق الدفع"
- Gifts: "اضغط عشان تفتح هديتك" (tap-to-open gift), scratch cards (eid_al_adha_scratch_opened, eid_al_adha_box_picked, eid_al_adha_gift_redeemed)

## 8.5 Ramadan quiz (rmdn_quiz_*)

- Home banner (hdr/bdy impression+click), quiz screen with daily questions (`rmdn_quiz_screen_day_click`), correct/wrong answers, reward ladder ("إجابة صح كمان وتوصل لأعلى مكافأة")، profile CTA (`rmdn_quiz_profile_cta_click`)
- Retention loop: daily check-in + reward tiers + "مبروك! وصلت لأعلى مكافأة - أنت بطل رمضان!"

## 8.6 Campaign stories

- Full-screen story format (slides + CTA + dismiss) for Eid al-Fitr & general campaigns — `communication_campaign_in_app_story_*`

## 8.7 Design logic for POL

1. **Wallet = refund rail + cashback rail + partial payment rail** in one balance. Iranian version should merge کیف پول + پاداش + بازگشت وجه همینجا.
2. **BNPL is a funnel with its own wizard, docs, pending state, and finance web-app** — credit underwriting is a product surface, not a back-office detail.
3. **Dues (المستحقات) on the home** — money visibility before money actions.
4. **Rewards ladder with replacement rule** (higher tier replaces current) — prevents reward stacking abuse.
5. **Cultural season skins** (Ramadan/Eid/World Cup) are feature flags, not releases — Iranian equivalent: نوروز/شب یلدا/رمضان flags.
