# -*- coding: utf-8 -*-
"""Design System Guide and Reference Component Library pages for Pol."""

from typing import Any, Dict
from design_builder_tokens import (
    COLOR_PRIMARY, COLOR_PRIMARY_LIGHT, COLOR_PRIMARY_DARK,
    COLOR_BG, COLOR_SURFACE, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY,
    COLOR_TEXT_MUTED, COLOR_BORDER, COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER,
    rect, textbox, circle, home_indicator
)

def page_design_system_guide() -> Dict[str, Any]:
    """Page 11: Comprehensive Design System Guide for Pol."""
    objs = []
    
    # Header
    objs.append(rect("کادر سربرگ راهنما", 24, 24, 342, 70, COLOR_PRIMARY, 16, 16))
    objs.append(textbox("عنوان راهنمای سیستم طراحی", "راهنمای سیستم طراحی «پل»", 36, 36, 318, 26, 18, 800, "#FFFFFF", "right"))
    objs.append(textbox("زیرعنوان راهنمای طراحی", "مستندات توکن‌های بصری، تایپوگرافی، پالت رنگ و قواعد راست‌به‌چپ", 36, 62, 318, 20, 11, 400, "#BFDBFE", "right"))
    
    # 1. Color Palette Tokens Card
    objs.append(rect("کارت پالت رنگ", 24, 105, 342, 210, COLOR_SURFACE, 14, 14, COLOR_BORDER, 1))
    objs.append(textbox("تیتر پالت رنگ", "۱. پالت رنگی مصوب", 40, 116, 310, 20, 13, 800, COLOR_TEXT_PRIMARY, "right"))
    
    colors = [
        ("آبی اصلی", "#246BFD", COLOR_PRIMARY),
        ("سطح کارت", "#FFFFFF", "#E2E8F0"),
        ("پس‌زمینه", "#F5F7FA", "#CBD5E1"),
        ("متن اصلی", "#172033", COLOR_TEXT_PRIMARY),
        ("متن ثانویه", "#64748B", COLOR_TEXT_SECONDARY),
        ("موفقیت", "#0DB89D", COLOR_SUCCESS),
        ("هشدار", "#F59E0B", COLOR_WARNING),
        ("خطا و حذف", "#DC3545", COLOR_DANGER),
    ]
    for i, (cname, chex, cborder) in enumerate(colors):
        cy = 142 + i * 20
        objs.append(rect(f"سواچ {cname}", 326, cy + 2, 16, 14, chex, 4, 4, cborder, 1))
        objs.append(textbox(f"نام رنگ {cname}", cname, 110, cy, 210, 16, 11, 600, COLOR_TEXT_PRIMARY, "right"))
        objs.append(textbox(f"کد رنگ {cname}", chex, 36, cy, 70, 16, 11, 700, chex if chex != "#FFFFFF" else COLOR_TEXT_SECONDARY, "left"))
        
    # 2. Typography Scale Card
    objs.append(rect("کارت تایپوگرافی", 24, 325, 342, 175, COLOR_SURFACE, 14, 14, COLOR_BORDER, 1))
    objs.append(textbox("تیتر تایپوگرافی", "۲. مقیاس تایپوگرافی وزیرمتن", 40, 336, 310, 20, 13, 800, COLOR_TEXT_PRIMARY, "right"))
    
    type_scale = [
        ("تیترهای اصلی صفحات", "وزن ۸۰۰ • اندازهٔ ۲۴ پیکسل"),
        ("تیتر بخش‌ها و نام کالا", "وزن ۷۰۰ • اندازهٔ ۱۸ پیکسل"),
        ("متن بدنه و قیمت عمده", "وزن ۵۰۰ • اندازهٔ ۱۴ پیکسل"),
        ("توضیحات و واحد کالا", "وزن ۴۰۰ • اندازهٔ ۱۲ پیکسل"),
        ("برچسب‌ها و نشانگرها", "وزن ۶۰۰ • اندازهٔ ۱۰ پیکسل"),
    ]
    for i, (tname, tdesc) in enumerate(type_scale):
        ty = 362 + i * 24
        objs.append(textbox(f"نمونه تایپ {i}", tname, 40, ty, 170, 18, 11, 700, COLOR_TEXT_PRIMARY, "right"))
        objs.append(textbox(f"توضیح تایپ {i}", tdesc, 40, ty, 290, 18, 11, 400, COLOR_TEXT_SECONDARY, "left"))
        
    # 3. Spacing & Radius Rules Card
    objs.append(rect("کارت فاصله و گوشه‌ها", 24, 510, 342, 150, COLOR_SURFACE, 14, 14, COLOR_BORDER, 1))
    objs.append(textbox("تیتر گوشه‌ها", "۳. شبکه، فواصل و انحنا", 40, 522, 310, 20, 13, 800, COLOR_TEXT_PRIMARY, "right"))
    
    rules = [
        ("شبکهٔ فاصله مبنا:", "شبکهٔ ۴ و ۸ پیکسلی (۴، ۸، ۱۲، ۱۶، ۲۴، ۳۲)"),
        ("حاشیه امن اطراف صفحه:", "۲۴ پیکسل از چپ و راست در کادر ۳۹۰ پیکسلی"),
        ("ارتفاع دکمه‌های اصلی لمس:", "۵۲ پیکسل با انحنای ۱۴ پیکسل (کف استاندارد ۴۸)"),
        ("انحنای کارت‌های محصول:", "۱۲ تا ۱۶ پیکسل با حاشیهٔ ۱ پیکسلی نازک"),
        ("انحنای چیپ‌ها و نشان‌ها:", "۱۴ تا ۱۶ پیکسل کاملاً کپسولی و گرد"),
    ]
    for i, (rk, rv) in enumerate(rules):
        ry = 548 + i * 20
        objs.append(textbox(f"عنوان قاعده {i}", rk, 220, ry, 130, 16, 11, 700, COLOR_TEXT_PRIMARY, "right"))
        objs.append(textbox(f"مقدار قاعده {i}", rv, 36, ry, 180, 16, 11, 400, COLOR_TEXT_SECONDARY, "right"))
        
    # 4. RTL & Persian Quality Rules Card
    objs.append(rect("کارت قواعد فارسی", 24, 670, 342, 140, COLOR_PRIMARY_LIGHT, 14, 14, "#BFDBFE", 1))
    objs.append(textbox("تیتر قواعد فارسی", "۴. قواعد حیاتی زبان فارسی و راست‌به‌چپ", 40, 680, 310, 20, 13, 800, COLOR_PRIMARY_DARK, "right"))
    
    rtl_rules = [
        "✓  حذف کامل نویسه‌های عربی و استفادهٔ انحصاری از حروف اصیل فارسی",
        "✓  استفادهٔ ۱۰۰٪ از ارقام فارسی (۰۱۲۳۴۵۶۷۸۹) در قیمت‌ها و شماره‌ها",
        "✓  رعایت دقیق نیم‌فاصله در «دسته‌بندی‌ها»، «می‌شود» و «ساده‌تر»",
        "✓  نمایش صریح واحد بسته‌بندی عمده (کارتن، کیسه) در کنار قیمت واحد",
    ]
    for i, rr in enumerate(rtl_rules):
        objs.append(textbox(f"قاعده فارسی {i}", rr, 36, 705 + i * 22, 318, 18, 11, 600, COLOR_TEXT_PRIMARY, "right"))
        
    objs.extend(home_indicator())
    return {
        "id": "10000000-0000-4000-8000-000000000011",
        "name": "۱۱. راهنمای طراحی پل",
        "background": {"type": "solid", "color": COLOR_BG},
        "objects": objs
    }

def page_reference_components() -> Dict[str, Any]:
    """Page 12: Reference Component Library for Pol."""
    objs = []
    
    # Header
    objs.append(rect("کادر سربرگ اجزای مرجع", 24, 24, 342, 60, COLOR_SURFACE, 14, 14, COLOR_BORDER, 1))
    objs.append(textbox("تیتر اجزای مرجع", "کتابخانهٔ اجزای مرجع «پل»", 36, 34, 318, 24, 17, 800, COLOR_TEXT_PRIMARY, "right"))
    objs.append(textbox("زیرعنوان اجزای مرجع", "اجزای استاندارد قابل استفادهٔ مجدد جهت حفظ یکپارچگی", 36, 56, 318, 18, 11, 400, COLOR_TEXT_SECONDARY, "right"))
    
    # Component 1: Buttons
    objs.append(rect("کارت نمونه دکمه‌ها", 24, 95, 342, 110, COLOR_SURFACE, 14, 14, COLOR_BORDER, 1))
    objs.append(textbox("عنوان جزء ۱", "۱. دکمه‌ها", 40, 105, 310, 18, 12, 700, COLOR_TEXT_PRIMARY, "right"))
    # Primary Button
    objs.append(rect("دکمه اصلی نمونه", 195, 130, 155, 46, COLOR_PRIMARY, 12, 12))
    objs.append(textbox("متن دکمه اصلی نمونه", "دکمهٔ اصلی", 195, 143, 155, 20, 12, 700, "#FFFFFF", "center"))
    # Secondary Button
    objs.append(rect("دکمه فرعی نمونه", 36, 130, 150, 46, COLOR_PRIMARY_LIGHT, 12, 12, COLOR_PRIMARY, 1))
    objs.append(textbox("متن دکمه فرعی نمونه", "دکمهٔ فرعی", 36, 143, 150, 20, 12, 700, COLOR_PRIMARY, "center"))
    # Disabled button state
    objs.append(rect("دکمه غیرفعال نمونه", 195, 185, 155, 32, "#E2E8F0", 8, 8))
    objs.append(textbox("متن دکمه غیرفعال", "غیرفعال", 195, 192, 155, 16, 11, 500, COLOR_TEXT_MUTED, "center"))
    # Destructive button state
    objs.append(rect("دکمه حذف نمونه", 36, 185, 150, 32, "#FEE2E2", 8, 8, COLOR_DANGER, 1))
    objs.append(textbox("متن دکمه حذف", "حذف / انصراف", 36, 192, 150, 16, 11, 700, COLOR_DANGER, "center"))
    
    # Component 2: Inputs
    objs.append(rect("کارت نمونه فیلدها", 24, 215, 342, 105, COLOR_SURFACE, 14, 14, COLOR_BORDER, 1))
    objs.append(textbox("عنوان جزء ۲", "۲. فیلدهای ورودی", 40, 225, 310, 18, 12, 700, COLOR_TEXT_PRIMARY, "right"))
    objs.append(rect("کادر ورودی نمونه", 36, 250, 318, 44, "#F8FAFC", 10, 10, COLOR_PRIMARY, 1.5))
    objs.append(textbox("آیکون سرچ ورودی", "🔍", 320, 260, 26, 20, 15, 400, COLOR_TEXT_MUTED, "center"))
    objs.append(textbox("متن داخل ورودی نمونه", "متن تایپ‌شده مغازه‌دار...", 50, 261, 260, 20, 12, 600, COLOR_TEXT_PRIMARY, "right"))
    objs.append(textbox("راهنمای زیر فیلد نمونه", "پیام راهنمای استاندارد زیر فیلد ورودی", 40, 298, 310, 16, 11, 400, COLOR_TEXT_SECONDARY, "right"))
    
    # Component 3: Steppers & Badges
    objs.append(rect("کارت نمونه شمارنده‌ها", 24, 330, 342, 100, COLOR_SURFACE, 14, 14, COLOR_BORDER, 1))
    objs.append(textbox("عنوان جزء ۳", "۳. شمارنده و نشان‌ها", 40, 340, 310, 18, 12, 700, COLOR_TEXT_PRIMARY, "right"))
    # Stepper
    objs.append(rect("کادر استپر نمونه", 220, 368, 130, 36, COLOR_PRIMARY_LIGHT, 8, 8, COLOR_PRIMARY, 1))
    objs.append(textbox("منفی استپر نمونه", "-", 322, 372, 24, 24, 16, 700, COLOR_PRIMARY, "center"))
    objs.append(textbox("عدد استپر نمونه", "۳ کارتن", 254, 376, 68, 20, 12, 700, COLOR_PRIMARY_DARK, "center"))
    objs.append(textbox("مثبت استپر نمونه", "+", 224, 372, 24, 24, 16, 700, COLOR_PRIMARY, "center"))
    # Badges
    objs.append(rect("بج موفقیت نمونه", 125, 368, 85, 26, "#ECFDF5", 13, 13, "#A7F3D0", 1))
    objs.append(textbox("متن بج موفقیت", "موجود در انبار", 125, 373, 85, 16, 10, 700, COLOR_SUCCESS, "center"))
    
    objs.append(rect("بج تخفیف نمونه", 36, 368, 75, 26, "#FEE2E2", 13, 13, "#FCA5A5", 1))
    objs.append(textbox("متن بج تخفیف", "۱۵٪ تخفیف", 36, 373, 75, 16, 10, 700, COLOR_DANGER, "center"))
    
    # Component 4: Alerts
    objs.append(rect("کارت نمونه پیام‌ها", 24, 440, 342, 115, COLOR_SURFACE, 14, 14, COLOR_BORDER, 1))
    objs.append(textbox("عنوان جزء ۴", "۴. جعبه‌های پیام و هشدار", 40, 450, 310, 18, 12, 700, COLOR_TEXT_PRIMARY, "right"))
    # Success Alert
    objs.append(rect("پیام موفقیت نمونه", 36, 474, 318, 34, "#ECFDF5", 8, 8, COLOR_SUCCESS, 1))
    objs.append(textbox("متن پیام موفقیت", "✓  سفارش شما با موفقیت در سیستم ثبت گردید.", 46, 481, 298, 18, 11, 700, COLOR_SUCCESS, "right"))
    # Error Alert
    objs.append(rect("پیام خطا نمونه", 36, 514, 318, 34, "#FEF2F2", 8, 8, COLOR_DANGER, 1))
    objs.append(textbox("متن پیام خطا", "✕  کد تأیید واردشده نادرست است. دوباره تلاش کنید.", 46, 521, 298, 18, 11, 700, COLOR_DANGER, "right"))
    
    # Component 5: Mini Product Card Component
    objs.append(rect("کارت نمونه محصول", 24, 565, 342, 105, COLOR_SURFACE, 14, 14, COLOR_BORDER, 1))
    objs.append(textbox("عنوان جزء ۵", "۵. ساختار کارت محصول استاندارد", 40, 575, 310, 18, 12, 700, COLOR_TEXT_PRIMARY, "right"))
    objs.append(rect("عکس کالا نمونه", 286, 600, 68, 60, "#F8FAFC", 8, 8, COLOR_BORDER, 1))
    objs.append(textbox("آیکون کالا نمونه", "🥫", 286, 615, 68, 28, 24, 400, COLOR_TEXT_PRIMARY, "center"))
    objs.append(textbox("نام کالا نمونه", "روغن مایع ۱٫۸ لیتری لادن", 40, 598, 235, 18, 13, 800, COLOR_TEXT_PRIMARY, "right"))
    objs.append(textbox("بسته کالا نمونه", "واحد پایه: کارتن ۶ عددی • بنکدار رضایی", 40, 618, 235, 16, 11, 400, COLOR_TEXT_SECONDARY, "right"))
    objs.append(textbox("قیمت کالا نمونه", "۱۲۵٬۰۰۰ تومان (کارتن: ۷۵۰٬۰۰۰)", 40, 638, 235, 18, 12, 800, COLOR_PRIMARY, "right"))
    
    # Component 6: Bottom Navigation Component
    objs.append(rect("کارت نمونه ناوبری", 24, 680, 342, 130, COLOR_SURFACE, 14, 14, COLOR_BORDER, 1))
    objs.append(textbox("عنوان جزء ۶", "۶. ساختار نوار پیمایش ۵ گزینه‌ای", 40, 690, 310, 18, 12, 700, COLOR_TEXT_PRIMARY, "right"))
    # Miniature 5 tabs preview
    mtabs = [("خانه", "🏠", 295, True), ("دسته‌ها", "📁", 230, False), ("سبد", "🛒", 165, False), ("سفارش‌ها", "📋", 100, False), ("پروفایل", "👤", 35, False)]
    objs.append(rect("کادر نوار مینیاتوری", 30, 715, 330, 52, COLOR_SURFACE, 10, 10, COLOR_BORDER, 1))
    for tname, ticon, tx, act in mtabs:
        tc = COLOR_PRIMARY if act else COLOR_TEXT_MUTED
        objs.append(textbox(f"مینی آیکون {tname}", ticon, tx, 722, 60, 20, 14, 400, tc, "center"))
        objs.append(textbox(f"مینی نام {tname}", tname, tx, 744, 60, 16, 10, 700 if act else 500, tc, "center"))
        
    objs.extend(home_indicator())
    return {
        "id": "10000000-0000-4000-8000-000000000012",
        "name": "۱۲. اجزای مرجع",
        "background": {"type": "solid", "color": COLOR_BG},
        "objects": objs
    }
