# 09 — UI Strings Dictionary (curated, from binary)

Full raw list: `data/arabic_ui_strings.txt` (1,653 strings). Below: the ones that define screen anatomy and business rules, grouped. Use as functional reference for the Iranian equivalent (translate intent, not words).

## Order statuses & tracking
| String | Meaning |
|---|---|
| قيد الانتظار / قيد المراجعة | pending / under review |
| قيد التوصيل | out for delivery |
| تم التأكيد / تم التعديل / تم التوصيل | confirmed / edited / delivered |
| شكراً لك! طلبك الآن قيد المراجعة وسيتم تأكيده من المورد قريباً | post-submit expectation |
| عندك طلب قيد الانتظار من … | pending-order nudge |
| متابعة الطلبيات / تاريخ الاستلام | tracking title / delivery date |
| شارك الرمز فقط مع المندوب عند استلام الطلب لتأكيد التسليم | **delivery PIN shown to retailer, shared with courier at handover** |
| مفيش طلبات تم التأكيد / مفيش طلبات قيد التوصيل | tab empty states |
| يوم من تاريخ إنشائها. وبما إن المدة دي عدّت على الطلبية، فمش هنقدر نسجّل عليها شكوى أو طلب جديد | complaint window expiry |

## Registration / KYC
| String | Meaning |
|---|---|
| أدخل الاسم بالكامل / الاسم بالكامل | full name validation |
| التقط صورة مباشرة لواجهة المحل مع ظهور اللافتة والاسم | shop front photo instruction |
| اتأكد إن اسم المحل ظاهر | sign must be visible |
| اتأكد إن الصوره شاملة المحل من الداخل بشكل واضح | interior photo clarity rule |
| سنتصل بك لتأكيد بيانات المستخدم والبدء في التفعيل | human activation call promise |
| حسابك قيد المراجعة، فريقنا هيتواصل معاك قريباً | pending-activation state |
| اسم المسؤول مطلوب / اسم الفرع مطلوب | owner name / branch name required |
| دلوقتي إنت جاهز تعمل طلبية، وفريقنا هيتواصل معاك بعد كده لتفعيل الحساب | success screen copy |

## Cart & checkout
| String | Meaning |
|---|---|
| عربة التسوق / إتمام الطلبية / إرسال الطلب | cart / checkout / submit |
| إجمالي الطلب / من إجمالي الطلب | totals |
| استخدم رصيدك في المحفظة / خصم من المحفظة | wallet usage |
| المطلوب كاش بعد الرصيد | cash-after-wallet line |
| كاش باك (…) / الحد الأقصى للكاش باك | cashback + cap |
| راجع متطلبات الحد الأدنى | min-requirements warning |
| مبياخدش نفس المنتج بوحدتين مختلفين في الطلب الواحد. لازم تختار وحدة واحدة بس | unit-conflict rule |
| والكميات هتتزبط لوحدها لو في فرق عن الحد الأدنى أو الأقصى | auto-adjust promise |
| تغيّر الحد الأدنى للطلب: كان … | dynamic minimums notice |
| آسفين، المورد غير متاح حالياً. ما تقدرش تكمل الطلب دلوقتي. ممكن تطلب من مورد تاني | supplier-unavailable block |
| أي طلبيات خاصة أو ملاحظات للمورد... | order notes placeholder |
| اختر الفرع اللي عايز تطلب عليه | branch picker |
| تم إلغاء الطلب بنجاح. وفي حالة استخدام أي رصيد … هيتم رد المبلغ تلقائياً | cancel + auto-refund |

## Payments / wallet / BNPL
| String | Meaning |
|---|---|
| محفظة كرتونة / رصيد فوري / شحن المحفظة / تاريخ معاملات المحفظة | wallet suite |
| حدود استخدام المحفظة | wallet limits policy |
| ادفع بعدين / ادفع براحتك / اشتري دلوقتي وادفع بعدين | BNPL taglines |
| اختر خطة الدفع / طلب تقسيط الآن / تأكيد التقسيط / دفعات | installment plan flow |
| الحد الإئتماني المطلوب (قيمة الفلوس اللي هتحتاجها) | requested credit limit field |
| الإيراد الشهري (المبيعات والطلبيات والفواتير) | monthly revenue field |
| دفع عند الاستلام / كاش عند الاستلام | COD |
| الطلب بـ … / عند الطلب بـ | pay-with prefix |

## Supplier & product
| String | Meaning |
|---|---|
| الحد الأدنى للطلب / الحد الأدنى لعدد المنتجات / الحد الأدنى للكمية المطلوبة هو / الحد الأقصى للكمية المتاحة هو | minimums & stock limits |
| التوصيل خلال 24 ساعة | delivery SLA |
| اكتشف أفضل الموردين واضيفهم لقائمتك المفضلة للوصول السريع والطلب السهل | favorites value prop |
| جرب اسم مورد تاني أو تأكد من كتابة الاسم صح | supplier search error |
| اقتراحات في الطلب الواحد / تقدر تبعت 5 اقتراحات … | retailer-asks quota |

## Rewards & campaigns
| String | Meaning |
|---|---|
| برافو! وصلت لأول مكافأة - كمّل عشان توصل لـ … | reward ladder |
| لو وصلت للمستوى التالي، المكافأة الأكبر هتحل محل الحالية | tier replacement |
| تم الوصول للهدف! في انتظار إغلاق فترة الهدف لاستلام المكافآت | goal period close |
| إجابة صح كمان وتوصل لأعلى مكافأة | quiz reward |
| اضغط عشان تفتح هديتك | gift tap |

## System / states
| String | Meaning |
|---|---|
| أنت غير متصل بالإنترنت | offline banner |
| انتهت صلاحية الجلسة | session expired |
| في إصدار جديد فيه تحسينات ومميزات | update nag |
| اضغط للتأكيد / اضغط للتعديل / اضغط للحذف | generic tap affordances |
| نجمع معلومات الموقع الجغرافي (بإذنك) لتحسين خدمة التوصيل | location rationale |
| سماحك بالإشعارات يخلينا نوصلك بكل جديد من طلباتك، التنبيهات المهمة، والخصومات كمان | notification rationale |
