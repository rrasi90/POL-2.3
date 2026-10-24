# -*- coding: utf-8 -*-
"""Comprehensive page definitions for the 10 mobile pages of Pol."""

import uuid
from typing import Any, Dict, List
from design_builder_tokens import (
    COLOR_PRIMARY, COLOR_PRIMARY_LIGHT, COLOR_PRIMARY_DARK,
    COLOR_BG, COLOR_SURFACE, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY,
    COLOR_TEXT_MUTED, COLOR_BORDER, COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER,
    rect, textbox, circle, status_bar, home_indicator, bottom_navigation
)

def page_splash() -> Dict[str, Any]:
    objs = status_bar()
    
    # Background soft gradient accent
    objs.append(circle("هاله آبی بالای صفحه", 95, 120, 100, "#EFF6FF"))
    
    # Modern Store / FMCG Illustration Container
    objs.append(rect("کادر تصویرسازی مغازه", 45, 180, 300, 240, "#FFFFFF", 20, 20, COLOR_BORDER, 1))
    objs.append(rect("سایبان مغازه", 65, 200, 260, 48, COLOR_PRIMARY, 8, 8))
    objs.append(textbox("نوار سایبان مغازه", "🏬   فروشگاه و بنکداری   🏬", 65, 212, 260, 24, 16, 700, "#FFFFFF", "center"))
    
    # Store window and shelves
    objs.append(rect("ویترین مغازه", 80, 265, 230, 135, "#F8FAFC", 12, 12, COLOR_BORDER, 1))
    objs.append(rect("قفسه کالا ۱", 95, 295, 200, 16, "#E2E8F0", 4, 4))
    objs.append(textbox("کالاهای قفسه ۱", "🥫  🧃  🧴  🧼  🥫", 95, 275, 200, 20, 16, 400, COLOR_TEXT_PRIMARY, "center"))
    objs.append(rect("قفسه کالا ۲", 95, 360, 200, 16, "#E2E8F0", 4, 4))
    objs.append(textbox("کالاهای قفسه ۲", "📦  🍪  🧻  🥫  📦", 95, 340, 200, 20, 16, 400, COLOR_TEXT_PRIMARY, "center"))
    
    # Brand Identity Section
    objs.append(textbox("نشان تجاری پل", "پل", 45, 450, 300, 65, 58, 900, COLOR_PRIMARY, "center"))
    objs.append(textbox("شعار اصلی پل", "خرید عمده، ساده‌تر از همیشه", 30, 525, 330, 36, 21, 700, COLOR_TEXT_PRIMARY, "center"))
    objs.append(textbox("توضیحات کوتاه پل", "سامانهٔ هوشمند اتصال مستقیم مغازه‌داران به تولیدکنندگان و بنکداران سراسر کشور", 35, 568, 320, 48, 14, 400, COLOR_TEXT_SECONDARY, "center", 1.5))
    
    # Feature Badges
    objs.append(rect("کادر مزیت ۱", 35, 635, 320, 42, "#FFFFFF", 12, 12, COLOR_BORDER, 1))
    objs.append(textbox("متن مزیت ۱", "⚡  قیمت‌های به‌روز و رقابتی بازار بنکداری", 45, 645, 300, 22, 13, 600, COLOR_PRIMARY, "center"))
    
    objs.append(rect("کادر مزیت ۲", 35, 685, 320, 42, "#FFFFFF", 12, 12, COLOR_BORDER, 1))
    objs.append(textbox("متن مزیت ۲", "📦  تضمین تحویل سفارش‌ها در محل فروشگاه", 45, 695, 300, 22, 13, 600, COLOR_SUCCESS, "center"))
    
    # Version Footer
    objs.append(textbox("شماره نسخه", "نسخهٔ ۱٫۰ • ویژهٔ مغازه‌داران و خرده‌فروشان", 45, 785, 300, 20, 12, 500, COLOR_TEXT_MUTED, "center"))
    objs.extend(home_indicator())
    
    return {
        "id": "10000000-0000-4000-8000-000000000001",
        "name": "۱. شروع",
        "background": {"type": "solid", "color": COLOR_SURFACE},
        "objects": objs
    }

def page_onboarding() -> Dict[str, Any]:
    objs = status_bar()
    
    # Top skip button
    objs.append(textbox("دکمه رد کردن", "رد کردن", 24, 48, 60, 24, 14, 500, COLOR_TEXT_SECONDARY, "left"))
    
    # Hero Visual Card
    objs.append(rect("کارت تصویر هیرو", 24, 85, 342, 260, COLOR_PRIMARY_LIGHT, 24, 24, "#BFDBFE", 1))
    objs.append(circle("هاله آبی هیرو", 120, 115, 75, "#DBEAFE"))
    objs.append(textbox("تصویرسازی هیرو", "🚚\n🏢 ⇄ 🏪", 24, 135, 342, 100, 44, 400, COLOR_PRIMARY, "center", 1.2))
    objs.append(textbox("برچسب هیرو", "اتصال بی‌واسطه به شبکهٔ بنکداران", 24, 280, 342, 26, 15, 700, COLOR_PRIMARY_DARK, "center"))
    
    # Page Indicator Dots
    objs.append(rect("نشانگر نقطه فعال", 195, 365, 26, 8, COLOR_PRIMARY, 4, 4))
    objs.append(circle("نشانگر نقطه ۲", 175, 365, 4, "#CBD5E1"))
    objs.append(circle("نشانگر نقطه ۳", 155, 365, 4, "#CBD5E1"))
    
    # Title & Subtitle
    objs.append(textbox("تیتر معرفی", "دسترسی به عمده‌فروشان معتبر", 24, 395, 342, 36, 23, 800, COLOR_TEXT_PRIMARY, "center"))
    objs.append(textbox("توضیح معرفی", "قیمت‌های به‌روز، تنوع بیشتر و خرید آسان برای مغازهٔ شما\nبدون نیاز به مراجعهٔ حضوری و با تحویل یکپارچه", 24, 435, 342, 46, 14, 400, COLOR_TEXT_SECONDARY, "center", 1.6))
    
    # 3 Value Props Cards
    y_starts = [495, 565, 635]
    values = [
        ("⚡", "قیمت‌های رقابتی مستقیم بنکدار", "خرید به قیمت کف بازار بدون پرداخت کمیسیون واسطه"),
        ("📦", "تحویل یکپارچه در محل مغازه", "هماهنگی دقیق ارسال و تخلیه در ساعت کاری فروشگاه"),
        ("💳", "تسویه نقدی و اعتباری منعطف", "امکان پرداخت نقدی در محل یا شرایط اعتباری بنکدار"),
    ]
    for (icon, title, desc), y in zip(values, y_starts):
        objs.append(rect(f"کارت مزیت {title}", 24, y, 342, 60, COLOR_SURFACE, 14, 14, COLOR_BORDER, 1))
        objs.append(textbox(f"آیکون {title}", icon, 310, y + 16, 40, 30, 20, 400, COLOR_PRIMARY, "center"))
        objs.append(textbox(f"تیتر {title}", title, 36, y + 10, 270, 20, 14, 700, COLOR_TEXT_PRIMARY, "right"))
        objs.append(textbox(f"توضیح {title}", desc, 36, y + 32, 270, 18, 12, 400, COLOR_TEXT_SECONDARY, "right"))
        
    # Primary CTA Button
    objs.append(rect("دکمه شروع کنیم", 24, 725, 342, 52, COLOR_PRIMARY, 14, 14))
    objs.append(textbox("متن دکمه شروع کنیم", "شروع کنیم", 24, 739, 342, 24, 17, 700, "#FFFFFF", "center"))
    objs.extend(home_indicator())
    
    return {
        "id": "10000000-0000-4000-8000-000000000002",
        "name": "۲. معرفی پل",
        "background": {"type": "solid", "color": COLOR_BG},
        "objects": objs
    }

def page_login() -> Dict[str, Any]:
    objs = status_bar()
    
    # Header Section
    objs.append(rect("کادر نشان کوچک پل", 316, 55, 50, 28, COLOR_PRIMARY_LIGHT, 8, 8))
    objs.append(textbox("نشان پل هدر", "پل", 316, 59, 50, 20, 14, 800, COLOR_PRIMARY, "center"))
    
    objs.append(textbox("تیتر صفحه ورود", "ورود به پل", 24, 100, 342, 38, 26, 800, COLOR_TEXT_PRIMARY, "right"))
    objs.append(textbox("توضیح صفحه ورود", "برای شروع، شمارهٔ موبایل خود را وارد کنید تا کد تأیید ورود برای شما پیامک شود.", 24, 142, 342, 44, 14, 400, COLOR_TEXT_SECONDARY, "right", 1.5))
    
    # Phone Input Form Card
    objs.append(rect("کارت فرم شماره موبایل", 24, 205, 342, 170, COLOR_SURFACE, 16, 16, COLOR_BORDER, 1))
    objs.append(textbox("برچسب فیلد موبایل", "شمارهٔ موبایل مغازه‌دار", 44, 225, 302, 22, 13, 700, COLOR_TEXT_PRIMARY, "right"))
    
    # Input Box
    objs.append(rect("کادر ورودی شماره موبایل", 40, 255, 310, 52, "#F8FAFC", 12, 12, COLOR_PRIMARY, 1.5))
    objs.append(textbox("پیش‌شماره کشور", "🇮🇷  +۹۸", 50, 270, 75, 24, 15, 600, COLOR_TEXT_SECONDARY, "left"))
    objs.append(rect("خط جداکننده پیش‌شماره", 130, 267, 1, 28, COLOR_BORDER))
    objs.append(textbox("متن شماره موبایل نمونه", "۰۹۱۲  ۳۴۵  ۶۷۸۹", 140, 268, 190, 26, 17, 700, COLOR_TEXT_PRIMARY, "right"))
    objs.append(textbox("راهنمای زیر فیلد", "کد تأیید ۶ رقمی به این شماره ارسال خواهد شد.", 44, 320, 302, 20, 12, 400, COLOR_TEXT_MUTED, "right"))
    
    # Submit CTA Button
    objs.append(rect("دکمه دریافت کد تأیید", 24, 395, 342, 52, COLOR_PRIMARY, 14, 14))
    objs.append(textbox("متن دکمه دریافت کد", "دریافت کد تأیید", 24, 409, 342, 24, 17, 700, "#FFFFFF", "center"))
    
    # Terms Note
    objs.append(textbox("متن قوانین و مقررات", "با ورود به پل، قوانین، شرایط استفاده و حریم خصوصی را می‌پذیرید.", 24, 465, 342, 36, 12, 400, COLOR_TEXT_MUTED, "center", 1.5))
    
    # Quick Help Box
    objs.append(rect("کارت تماس پشتیبانی", 24, 690, 342, 65, COLOR_SURFACE, 14, 14, COLOR_BORDER, 1))
    objs.append(textbox("آیکون پشتیبانی", "📞", 310, 708, 40, 30, 22, 400, COLOR_PRIMARY, "center"))
    objs.append(textbox("تیتر تماس پشتیبانی", "نیاز به راهنمایی یا ثبت‌نام تلفنی دارید؟", 40, 702, 270, 20, 13, 700, COLOR_TEXT_PRIMARY, "right"))
    objs.append(textbox("شماره تماس پشتیبانی", "پشتیبانی مغازه‌داران: ۰۲۱-۹۱۰۰۰۰۰۰ (داخلی ۲)", 40, 725, 270, 18, 12, 500, COLOR_PRIMARY, "right"))
    
    objs.extend(home_indicator())
    return {
        "id": "10000000-0000-4000-8000-000000000003",
        "name": "۳. ورود با شمارهٔ موبایل",
        "background": {"type": "solid", "color": COLOR_BG},
        "objects": objs
    }

def page_otp_verify() -> Dict[str, Any]:
    objs = status_bar()
    
    # Back button
    objs.append(textbox("دکمه بازگشت", "←", 336, 48, 30, 30, 22, 700, COLOR_TEXT_PRIMARY, "center"))
    
    # Headers
    objs.append(textbox("تیتر تأیید شماره", "کد تأیید", 24, 95, 342, 36, 26, 800, COLOR_TEXT_PRIMARY, "right"))
    objs.append(textbox("توضیح تأیید شماره", "کد ۶ رقمی ارسال‌شده به شمارهٔ ۰۹۱۲•••۶۷۸۹ را وارد نمایید.", 24, 136, 342, 24, 14, 400, COLOR_TEXT_SECONDARY, "right"))
    objs.append(textbox("لینک ویرایش شماره", "ویرایش شمارهٔ موبایل", 24, 164, 140, 22, 13, 700, COLOR_PRIMARY, "right"))
    
    # 6 OTP Digit Boxes
    otp_start_x = 24
    box_w = 48
    gap = 10
    digits = ["۵", "۲", "۸", "۱", "", ""]
    for i, d in enumerate(digits):
        bx = otp_start_x + i * (box_w + gap)
        is_focused = (i == 4)
        is_filled = bool(d)
        border_col = COLOR_PRIMARY if is_focused or is_filled else COLOR_BORDER
        bg_col = COLOR_SURFACE if is_filled or is_focused else "#F8FAFC"
        
        objs.append(rect(f"کادر رقم {i+1}", bx, 215, box_w, 58, bg_col, 12, 12, border_col, 1.5 if is_focused else 1))
        if d:
            objs.append(textbox(f"رقم {i+1}", d, bx, 227, box_w, 32, 24, 800, COLOR_TEXT_PRIMARY, "center"))
        elif is_focused:
            # blinking cursor indicator
            objs.append(rect("نشانگر مکان‌نما", bx + 23, 228, 2, 28, COLOR_PRIMARY))
            
    # Countdown & Resend
    objs.append(rect("کادر شمارشگر زمان", 110, 300, 170, 34, "#F1F5F9", 17, 17))
    objs.append(textbox("متن زمان باقیمانده", "ارسال مجدد کد تا ۰۱:۴۵", 110, 307, 170, 20, 13, 600, COLOR_TEXT_SECONDARY, "center"))
    
    # CTA Button
    objs.append(rect("دکمه تأیید و ورود", 24, 360, 342, 52, COLOR_PRIMARY, 14, 14))
    objs.append(textbox("متن دکمه تأیید", "تأیید و ورود به پل", 24, 374, 342, 24, 17, 700, "#FFFFFF", "center"))
    
    # Mobile Keypad Mockup
    objs.append(rect("صفحه کلید عددی", 0, 480, 390, 340, "#E2E8F0", 24, 24))
    key_defs = [
        ("۱", 260, 495), ("۲", 150, 495), ("۳", 40, 495),
        ("۴", 260, 560), ("۵", 150, 560), ("۶", 40, 560),
        ("۷", 260, 625), ("۸", 150, 625), ("۹", 40, 625),
        ("⌫", 260, 690), ("۰", 150, 690), ("✓", 40, 690),
    ]
    for k, kx, ky in key_defs:
        objs.append(rect(f"کلید {k}", kx, ky, 90, 52, COLOR_SURFACE, 10, 10))
        objs.append(textbox(f"متن کلید {k}", k, kx, ky + 12, 90, 28, 20, 700, COLOR_TEXT_PRIMARY, "center"))
        
    objs.extend(home_indicator())
    return {
        "id": "10000000-0000-4000-8000-000000000004",
        "name": "۴. تأیید شمارهٔ موبایل",
        "background": {"type": "solid", "color": COLOR_BG},
        "objects": objs
    }

def page_city_select() -> Dict[str, Any]:
    objs = status_bar()
    
    # Back button
    objs.append(textbox("دکمه بازگشت", "←", 336, 48, 30, 30, 22, 700, COLOR_TEXT_PRIMARY, "center"))
    
    # Header
    objs.append(textbox("تیتر انتخاب شهر", "انتخاب شهر", 24, 90, 342, 34, 24, 800, COLOR_TEXT_PRIMARY, "right"))
    objs.append(textbox("توضیح انتخاب شهر", "شهر خود را انتخاب کنید تا عمده‌فروشان و قیمت‌های مرتبط با منطقهٔ شما نمایش داده شوند.", 24, 128, 342, 40, 14, 400, COLOR_TEXT_SECONDARY, "right", 1.5))
    
    # Search Box
    objs.append(rect("کادر جست‌وجوی شهر", 24, 185, 342, 48, COLOR_SURFACE, 12, 12, COLOR_BORDER, 1))
    objs.append(textbox("آیکون جست‌وجو", "🔍", 326, 197, 26, 24, 16, 400, COLOR_TEXT_MUTED, "center"))
    objs.append(textbox("متن راهنمای جست‌وجوی شهر", "جست‌وجوی نام شهر...", 40, 198, 280, 24, 14, 400, COLOR_TEXT_MUTED, "right"))
    
    # Cities List
    cities = [
        ("تهران", "بازار بزرگ، مولوی و حومه — ۱۲۰ بنکدار فعال", True, 250),
        ("مشهد", "خراسان رضوی و شرق کشور — ۸۵ بنکدار فعال", False, 325),
        ("اصفهان", "بازار مرکزی و میدان نقش‌جهان — ۷۰ بنکدار فعال", False, 400),
        ("شیراز", "استان فارس و جنوب — ۶۰ بنکدار فعال", False, 475),
        ("تبریز", "آذربایجان شرقی و شمال‌غرب — ۵۵ بنکدار فعال", False, 550),
        ("اهواز", "خوزستان و بندرگاه‌ها — ۵۰ بنکدار فعال", False, 625),
    ]
    for city_name, desc, is_sel, y in cities:
        border = COLOR_PRIMARY if is_sel else COLOR_BORDER
        bg = COLOR_PRIMARY_LIGHT if is_sel else COLOR_SURFACE
        objs.append(rect(f"کارت شهر {city_name}", 24, y, 342, 65, bg, 14, 14, border, 1.5 if is_sel else 1))
        
        # Radio button
        if is_sel:
            objs.append(circle(f"رادیو خارجی {city_name}", 42, y + 22, 10, COLOR_PRIMARY))
            objs.append(circle(f"رادیو داخلی {city_name}", 46, y + 26, 6, "#FFFFFF"))
        else:
            objs.append(circle(f"رادیو غیرفعال {city_name}", 42, y + 22, 10, "transparent", COLOR_BORDER, 1.5))
            
        objs.append(textbox(f"نام شهر {city_name}", city_name, 75, y + 12, 240, 22, 16, 700 if is_sel else 600, COLOR_PRIMARY if is_sel else COLOR_TEXT_PRIMARY, "right"))
        objs.append(textbox(f"توضیح شهر {city_name}", desc, 75, y + 36, 240, 18, 12, 400, COLOR_PRIMARY_DARK if is_sel else COLOR_TEXT_SECONDARY, "right"))
        
    # Primary CTA Button
    objs.append(rect("دکمه ادامه انتخاب شهر", 24, 715, 342, 52, COLOR_PRIMARY, 14, 14))
    objs.append(textbox("متن دکمه ادامه شهر", "ادامه و ورود به پل", 24, 729, 342, 24, 17, 700, "#FFFFFF", "center"))
    
    objs.extend(home_indicator())
    return {
        "id": "10000000-0000-4000-8000-000000000005",
        "name": "۵. انتخاب شهر",
        "background": {"type": "solid", "color": COLOR_BG},
        "objects": objs
    }

def page_home() -> Dict[str, Any]:
    objs = status_bar()
    
    # Header: Pol Brand + City Chip + Notification
    objs.append(textbox("لوگوی پل خانه", "پل", 326, 48, 40, 32, 26, 900, COLOR_PRIMARY, "right"))
    
    # City Chip
    objs.append(rect("چیپ شهر انتخابی", 155, 48, 155, 32, COLOR_SURFACE, 16, 16, COLOR_BORDER, 1))
    objs.append(textbox("متن چیپ شهر", "📍 تهران (بازار بزرگ) ▼", 160, 54, 145, 20, 12, 600, COLOR_TEXT_PRIMARY, "center"))
    
    # Notification & Search icons
    objs.append(rect("دکمه اعلان", 24, 48, 36, 32, COLOR_SURFACE, 10, 10, COLOR_BORDER, 1))
    objs.append(textbox("آیکون زنگوله", "🔔", 24, 53, 36, 22, 16, 400, COLOR_TEXT_PRIMARY, "center"))
    objs.append(circle("نشان نقطه اعلان", 26, 48, 4, COLOR_DANGER))
    
    # Search Bar
    objs.append(rect("کادر جست‌وجوی خانه", 24, 92, 342, 46, COLOR_SURFACE, 12, 12, COLOR_BORDER, 1))
    objs.append(textbox("آیکون ذره‌بین", "🔍", 326, 104, 28, 22, 16, 400, COLOR_TEXT_MUTED, "center"))
    objs.append(textbox("راهنمای جست‌وجو", "جست‌وجوی کالا، برند یا عمده‌فروش...", 70, 105, 250, 22, 13, 400, COLOR_TEXT_MUTED, "right"))
    objs.append(textbox("آیکون بارکدخوان", "📷", 36, 104, 28, 22, 16, 400, COLOR_PRIMARY, "center"))
    
    # Promotional Banner
    objs.append(rect("کادر بنر حراج", 24, 150, 342, 118, "#1E3A8A", 16, 16))
    objs.append(rect("نوار رنگی بنر", 24, 150, 8, 118, COLOR_PRIMARY, 4, 4))
    objs.append(textbox("برچسب حراج بنر", "تخفیف‌های ویژهٔ این هفته تا ۳۵٪", 44, 165, 300, 26, 18, 800, "#FFFFFF", "right"))
    objs.append(textbox("متن توضیحی بنر", "خرید مستقیم روغن، برنج، ماکارونی و شوینده‌ها", 44, 196, 300, 20, 13, 500, "#93C5FD", "right"))
    
    objs.append(rect("برچسب مزیت بنر", 44, 226, 230, 26, "#2563EB", 13, 13))
    objs.append(textbox("متن برچسب مزیت", "🚚  ارسال رایگان سفارش‌های بالای ۳ میلیون تومان", 44, 230, 230, 18, 11, 700, "#FFFFFF", "center"))
    
    # Quick Categories Row
    objs.append(textbox("تیتر دسته‌ها خانه", "دسته‌بندی‌های پرکاربرد", 200, 280, 166, 22, 15, 800, COLOR_TEXT_PRIMARY, "right"))
    objs.append(textbox("لینک همه دسته‌ها", "مشاهدهٔ همه ←", 24, 282, 100, 20, 12, 700, COLOR_PRIMARY, "left"))
    
    cat_items = [
        ("مواد غذایی", "🥫", "#FEF3C7", 305),
        ("نوشیدنی‌ها", "🧃", "#DBEAFE", 225),
        ("شوینده‌ها", "🧼", "#E0E7FF", 145),
        ("تنقلات", "🍪", "#FCE7F3", 65),
    ]
    for cname, cicon, cbg, cx in cat_items:
        objs.append(rect(f"کادر دسته {cname}", cx, 308, 62, 62, cbg, 16, 16))
        objs.append(textbox(f"آیکون دسته {cname}", cicon, cx, 320, 62, 28, 24, 400, COLOR_TEXT_PRIMARY, "center"))
        objs.append(textbox(f"نام دسته {cname}", cname, cx - 10, 376, 82, 18, 11, 600, COLOR_TEXT_PRIMARY, "center"))
        
    # Special Offers Section
    objs.append(textbox("تیتر پیشنهاد ویژه", "پیشنهادهای شگفت‌انگیز عمده", 180, 405, 186, 22, 15, 800, COLOR_TEXT_PRIMARY, "right"))
    objs.append(textbox("لینک همه کالاها", "۲۴ کالا ←", 24, 407, 80, 20, 12, 700, COLOR_PRIMARY, "left"))
    
    # 2 Product Cards
    # Product 1
    p1_x = 202
    objs.append(rect("کارت محصول ۱ خانه", p1_x, 435, 164, 240, COLOR_SURFACE, 14, 14, COLOR_BORDER, 1))
    objs.append(rect("تصویر محصول ۱ خانه", p1_x + 10, 445, 144, 90, "#F8FAFC", 10, 10))
    objs.append(textbox("شکلک محصول ۱", "🍾", p1_x + 10, 465, 144, 40, 36, 400, COLOR_TEXT_PRIMARY, "center"))
    objs.append(rect("برچسب تخفیف ۱", p1_x + 105, 448, 45, 20, COLOR_DANGER, 6, 6))
    objs.append(textbox("متن تخفیف ۱", "۱۵٪", p1_x + 105, 451, 45, 16, 11, 700, "#FFFFFF", "center"))
    objs.append(textbox("عنوان کالا ۱", "روغن مایع ۱٫۸ لیتری لادن", p1_x + 8, 545, 148, 20, 12, 700, COLOR_TEXT_PRIMARY, "right"))
    objs.append(textbox("بسته کالا ۱", "واحد: کارتن ۶ عددی", p1_x + 8, 568, 148, 16, 11, 500, COLOR_TEXT_SECONDARY, "right"))
    objs.append(textbox("قیمت کالا ۱", "۱۲۵٬۰۰۰ تومان", p1_x + 8, 590, 148, 20, 14, 800, COLOR_PRIMARY, "right"))
    objs.append(rect("دکمه افزودن ۱", p1_x + 8, 622, 148, 36, COLOR_PRIMARY, 8, 8))
    objs.append(textbox("متن افزودن ۱", "+  افزودن به سبد", p1_x + 8, 630, 148, 20, 12, 700, "#FFFFFF", "center"))
    
    # Product 2
    p2_x = 24
    objs.append(rect("کارت محصول ۲ خانه", p2_x, 435, 164, 240, COLOR_SURFACE, 14, 14, COLOR_BORDER, 1))
    objs.append(rect("تصویر محصول ۲ خانه", p2_x + 10, 445, 144, 90, "#F8FAFC", 10, 10))
    objs.append(textbox("شکلک محصول ۲", "🍝", p2_x + 10, 465, 144, 40, 36, 400, COLOR_TEXT_PRIMARY, "center"))
    objs.append(rect("برچسب تخفیف ۲", p2_x + 105, 448, 45, 20, COLOR_DANGER, 6, 6))
    objs.append(textbox("متن تخفیف ۲", "۲۰٪", p2_x + 105, 451, 45, 16, 11, 700, "#FFFFFF", "center"))
    objs.append(textbox("عنوان کالا ۲", "ماکارونی ۷۰۰ گرمی زر", p2_x + 8, 545, 148, 20, 12, 700, COLOR_TEXT_PRIMARY, "right"))
    objs.append(textbox("بسته کالا ۲", "واحد: کارتن ۲۰ عددی", p2_x + 8, 568, 148, 16, 11, 500, COLOR_TEXT_SECONDARY, "right"))
    objs.append(textbox("قیمت کالا ۲", "۲۵٬۰۰۰ تومان", p2_x + 8, 590, 148, 20, 14, 800, COLOR_PRIMARY, "right"))
    objs.append(rect("دکمه افزودن ۲", p2_x + 8, 622, 148, 36, COLOR_PRIMARY, 8, 8))
    objs.append(textbox("متن افزودن ۲", "+  افزودن به سبد", p2_x + 8, 630, 148, 20, 12, 700, "#FFFFFF", "center"))
    
    # Wholesaler Spotlight
    objs.append(rect("بنر بنکدار منتخب", 24, 690, 342, 64, COLOR_SURFACE, 12, 12, COLOR_BORDER, 1))
    objs.append(textbox("آیکون بنکدار", "🏢", 310, 705, 40, 30, 24, 400, COLOR_PRIMARY, "center"))
    objs.append(textbox("تیتر بنکدار منتخب", "بازرگانی رضایی (بنکدار برتر تهران)", 40, 702, 260, 20, 13, 700, COLOR_TEXT_PRIMARY, "right"))
    objs.append(textbox("امتیاز بنکدار", "⭐ امتیاز ۴٫۹ از ۵ • تحویل اکسپرس امروز", 40, 725, 260, 18, 12, 500, COLOR_SUCCESS, "right"))
    
    objs.extend(bottom_navigation("خانه"))
    return {
        "id": "10000000-0000-4000-8000-000000000006",
        "name": "۶. خانه",
        "background": {"type": "solid", "color": COLOR_BG},
        "objects": objs
    }

def page_categories() -> Dict[str, Any]:
    objs = status_bar()
    
    # Header
    objs.append(textbox("تیتر صفحه دسته‌بندی", "دسته‌بندی کالاها", 24, 48, 342, 32, 22, 800, COLOR_TEXT_PRIMARY, "right"))
    
    # Search Box
    objs.append(rect("کادر جست‌وجوی دسته‌بندی", 24, 88, 342, 44, COLOR_SURFACE, 12, 12, COLOR_BORDER, 1))
    objs.append(textbox("آیکون جست‌وجو دسته‌ها", "🔍", 326, 98, 28, 22, 15, 400, COLOR_TEXT_MUTED, "center"))
    objs.append(textbox("متن جست‌وجوی دسته‌ها", "جست‌وجو در دسته‌بندی‌ها...", 40, 99, 280, 22, 13, 400, COLOR_TEXT_MUTED, "right"))
    
    # 9 Categories (Vertical clean stack)
    categories = [
        ("مواد غذایی", "🥫", "۳۴۵ کالا", "#FEF3C7", 145),
        ("نوشیدنی‌ها", "🧃", "۱۲۰ کالا", "#DBEAFE", 212),
        ("بهداشت و سلامت", "🧴", "۸۵ کالا", "#FEE2E2", 279),
        ("شوینده‌ها و نظافت", "🧼", "۱۱۰ کالا", "#E0E7FF", 346),
        ("آرایشی و بهداشتی", "💄", "۶۰ کالا", "#FCE7F3", 413),
        ("کاغذی و سلولزی", "🧻", "۴۵ کالا", "#ECFDF5", 480),
        ("تنقلات و شیرینی", "🍪", "۱۸۰ کالا", "#FEF9C3", 547),
        ("کالاهای کودک", "🍼", "۵۵ کالا", "#E0F2FE", 614),
        ("سایر کالاهای سوپرمارکتی", "📦", "۹۰ کالا", "#F1F5F9", 681),
    ]
    for cname, cicon, count_str, icon_bg, y in categories:
        objs.append(rect(f"کارت دسته {cname}", 24, y, 342, 58, COLOR_SURFACE, 14, 14, COLOR_BORDER, 1))
        # Icon Box
        objs.append(rect(f"باکس آیکون {cname}", 314, y + 8, 42, 42, icon_bg, 10, 10))
        objs.append(textbox(f"آیکون {cname}", cicon, 314, y + 16, 42, 24, 18, 400, COLOR_TEXT_PRIMARY, "center"))
        # Title and Count
        objs.append(textbox(f"عنوان {cname}", cname, 70, y + 10, 230, 20, 14, 700, COLOR_TEXT_PRIMARY, "right"))
        objs.append(textbox(f"تعداد {cname}", count_str, 70, y + 32, 230, 16, 12, 400, COLOR_TEXT_SECONDARY, "right"))
        # Arrow
        objs.append(textbox(f"فلش {cname}", "‹", 36, y + 16, 20, 24, 18, 700, COLOR_TEXT_MUTED, "center"))
        
    objs.extend(bottom_navigation("دسته‌بندی‌ها"))
    return {
        "id": "10000000-0000-4000-8000-000000000007",
        "name": "۷. دسته‌بندی کالاها",
        "background": {"type": "solid", "color": COLOR_BG},
        "objects": objs
    }

def page_product_list() -> Dict[str, Any]:
    objs = status_bar()
    
    # Back + Title + Cart
    objs.append(textbox("دکمه بازگشت لیست", "←", 336, 46, 30, 30, 22, 700, COLOR_TEXT_PRIMARY, "center"))
    objs.append(textbox("عنوان دسته لیست", "مواد غذایی", 120, 48, 200, 28, 20, 800, COLOR_TEXT_PRIMARY, "right"))
    objs.append(textbox("تعداد کالاهای دسته", "(۳۴۵ کالا در انبار تهران)", 120, 74, 200, 16, 11, 500, COLOR_TEXT_SECONDARY, "right"))
    
    # Filter & Sort Chips Row
    objs.append(rect("چیپ مرتب‌سازی", 246, 100, 120, 32, COLOR_PRIMARY, 16, 16))
    objs.append(textbox("متن مرتب‌سازی", "⚡ پرفروش‌ترین‌ها ▼", 246, 106, 120, 20, 11, 700, "#FFFFFF", "center"))
    
    objs.append(rect("چیپ برندها", 130, 100, 110, 32, COLOR_SURFACE, 16, 16, COLOR_BORDER, 1))
    objs.append(textbox("متن فیلتر برند", "برند: لادن، زر (۲) ▼", 130, 106, 110, 20, 11, 600, COLOR_TEXT_PRIMARY, "center"))
    
    objs.append(rect("چیپ حداقل سفارش", 24, 100, 100, 32, COLOR_SURFACE, 16, 16, COLOR_BORDER, 1))
    objs.append(textbox("متن حداقل سفارش", "حداقل سفارش ▼", 24, 106, 100, 20, 11, 500, COLOR_TEXT_SECONDARY, "center"))
    
    # 4 Product Cards
    products = [
        ("روغن مایع ۱٫۸ لیتری لادن", "🍾", "بازرگانی رضایی (امتیاز ۴٫۹ ★)", "۱۲۵٬۰۰۰ تومان", "کارتن ۶ عددی: ۷۵۰٬۰۰۰ تومان", True, 142),
        ("برنج طارم هاشمی ۱۰ کیلویی", "🌾", "بازرگانی شوشتر (امتیاز ۴٫۸ ★)", "۸۵۰٬۰۰۰ تومان", "کیسه ۱۰ کیلویی اعلا", False, 286),
        ("ماکارونی ۷۰۰ گرمی زر ماکارون", "🍝", "پخش مهدوی (امتیاز ۴٫۷ ★)", "۲۵٬۰۰۰ تومان", "کارتن ۲۰ عددی: ۵۰۰٬۰۰۰ تومان", False, 430),
        ("کنسرو تن ماهی ۱۸۰ گرمی شیلتون", "🐟", "بازرگانی خلیج فارس (امتیاز ۴٫۹ ★)", "۶۵٬۰۰۰ تومان", "کارتن ۲۴ عددی: ۱٬۵۶۰٬۰۰۰ تومان", False, 574),
    ]
    for pname, picon, pwholesaler, punit_price, pcarton_price, has_stepper, y in products:
        objs.append(rect(f"کارت محصول {pname}", 24, y, 342, 132, COLOR_SURFACE, 14, 14, COLOR_BORDER, 1))
        
        # Product Image Box
        objs.append(rect(f"کادر تصویر {pname}", 266, y + 14, 88, 104, "#F8FAFC", 10, 10, COLOR_BORDER, 1))
        objs.append(textbox(f"شکلک {pname}", picon, 266, y + 42, 88, 40, 38, 400, COLOR_TEXT_PRIMARY, "center"))
        
        # Details
        objs.append(textbox(f"نام {pname}", pname, 36, y + 12, 220, 20, 14, 800, COLOR_TEXT_PRIMARY, "right"))
        objs.append(textbox(f"بنکدار {pname}", pwholesaler, 36, y + 34, 220, 16, 11, 500, COLOR_TEXT_SECONDARY, "right"))
        objs.append(textbox(f"قیمت تکی {pname}", f"قیمت هر واحد: {punit_price}", 36, y + 54, 220, 16, 11, 500, COLOR_TEXT_SECONDARY, "right"))
        objs.append(textbox(f"قیمت عمده {pname}", pcarton_price, 36, y + 74, 220, 20, 13, 800, COLOR_PRIMARY, "right"))
        
        # Stepper or Add button
        if has_stepper:
            # Active Stepper [- 3 +]
            objs.append(rect(f"کادر شمارنده {pname}", 36, y + 96, 110, 28, COLOR_PRIMARY_LIGHT, 8, 8, COLOR_PRIMARY, 1))
            objs.append(textbox(f"دکمه منفی {pname}", "-", 120, y + 98, 24, 24, 16, 700, COLOR_PRIMARY, "center"))
            objs.append(textbox(f"تعداد فعلی {pname}", "۳ کارتن", 64, y + 101, 54, 18, 12, 700, COLOR_PRIMARY_DARK, "center"))
            objs.append(textbox(f"دکمه مثبت {pname}", "+", 38, y + 98, 24, 24, 16, 700, COLOR_PRIMARY, "center"))
        else:
            objs.append(rect(f"دکمه افزودن {pname}", 36, y + 96, 110, 28, COLOR_PRIMARY, 8, 8))
            objs.append(textbox(f"متن افزودن {pname}", "+  افزودن به سبد", 36, y + 101, 110, 18, 11, 700, "#FFFFFF", "center"))
            
    objs.extend(bottom_navigation("خانه"))
    return {
        "id": "10000000-0000-4000-8000-000000000008",
        "name": "۸. فهرست محصولات",
        "background": {"type": "solid", "color": COLOR_BG},
        "objects": objs
    }

def page_product_detail() -> Dict[str, Any]:
    objs = status_bar()
    
    # Top navigation: Back, Share, Wishlist
    objs.append(textbox("دکمه بازگشت جزئیات", "←", 336, 46, 30, 30, 22, 700, COLOR_TEXT_PRIMARY, "center"))
    objs.append(textbox("عنوان نوار بالا", "جزئیات محصول", 100, 48, 220, 26, 17, 700, COLOR_TEXT_PRIMARY, "right"))
    objs.append(textbox("آیکون اشتراک‌گذاری", "↗", 60, 48, 28, 28, 18, 600, COLOR_TEXT_PRIMARY, "center"))
    objs.append(textbox("آیکون پسندیدن", "♡", 24, 48, 28, 28, 20, 600, COLOR_TEXT_PRIMARY, "center"))
    
    # Hero Product Image Card
    objs.append(rect("کارت تصویر محصول جزئیات", 24, 85, 342, 220, COLOR_SURFACE, 18, 18, COLOR_BORDER, 1))
    objs.append(circle("هاله زرد پشت روغن", 135, 115, 60, "#FEF3C7"))
    objs.append(textbox("شکلک تصویر بزرگ روغن", "🍾", 24, 125, 342, 90, 72, 400, COLOR_TEXT_PRIMARY, "center"))
    
    # Stock Status Badge
    objs.append(rect("برچسب وضعیت موجودی", 95, 265, 200, 28, "#ECFDF5", 14, 14, "#A7F3D0", 1))
    objs.append(textbox("متن وضعیت موجودی", "✅  موجود در انبار بنکدار رضایی (تهران)", 95, 271, 200, 18, 11, 700, COLOR_SUCCESS, "center"))
    
    # Title & Brand
    objs.append(textbox("عنوان کالا جزئیات", "روغن مایع ۱٫۸ لیتری لادن", 24, 318, 342, 28, 20, 800, COLOR_TEXT_PRIMARY, "right"))
    objs.append(textbox("برند کالا جزئیات", "برند: لادن  •  دسته‌بندی: روغن‌های خوراکی  •  کد کالا: ۸۸۴۰۲", 24, 348, 342, 18, 12, 500, COLOR_TEXT_SECONDARY, "right"))
    
    # Wholesale Pricing Card
    objs.append(rect("کارت قیمت عمده", 24, 376, 342, 105, COLOR_PRIMARY_LIGHT, 14, 14, "#BFDBFE", 1))
    objs.append(textbox("قیمت تک کالا", "قیمت فروش تکی (هر بطری): ۱۲۵٬۰۰۰ تومان", 40, 390, 310, 20, 13, 600, COLOR_TEXT_PRIMARY, "right"))
    objs.append(textbox("واحد کارتن", "بستهٔ پایه عمده: کارتن ۶ عددی", 40, 414, 310, 20, 13, 600, COLOR_TEXT_PRIMARY, "right"))
    objs.append(textbox("قیمت هر کارتن", "قیمت هر کارتن: ۷۵۰٬۰۰۰ تومان", 40, 438, 310, 24, 16, 800, COLOR_PRIMARY, "right"))
    objs.append(textbox("حداقل سفارش کالا", "حداقل سفارش: ۲ کارتن (۱۲ بطری)", 40, 464, 310, 18, 12, 700, COLOR_PRIMARY_DARK, "right"))
    
    # Product Specs Accordion Card
    objs.append(rect("کارت مشخصات کالا", 24, 492, 342, 140, COLOR_SURFACE, 14, 14, COLOR_BORDER, 1))
    objs.append(textbox("تیتر مشخصات", "مشخصات فنی و بسته‌بندی", 40, 504, 310, 22, 14, 800, COLOR_TEXT_PRIMARY, "right"))
    
    specs = [
        ("تعداد در هر کارتن", "۶ بطری پت شفاف"),
        ("وزن خالص هر واحد", "۱۸۰۰ گرم"),
        ("ماندگاری و انقضا", "۱۴ ماه از تاریخ تولید (تولید ماه جاری)"),
        ("شرایط نگهداری", "محیط خشک و خنک، دور از تابش مستقیم آفتاب"),
    ]
    for i, (k, v) in enumerate(specs):
        sy = 532 + i * 23
        objs.append(textbox(f"کلید {k}", f"• {k}:", 220, sy, 130, 18, 12, 600, COLOR_TEXT_SECONDARY, "right"))
        objs.append(textbox(f"مقدار {k}", v, 40, sy, 175, 18, 12, 700, COLOR_TEXT_PRIMARY, "right"))
        
    # Wholesaler Guarantee Card
    objs.append(rect("کارت ضمانت بنکدار", 24, 642, 342, 60, COLOR_SURFACE, 14, 14, COLOR_BORDER, 1))
    objs.append(textbox("آیکون تایید بنکدار", "🏢", 314, 656, 36, 30, 22, 400, COLOR_PRIMARY, "center"))
    objs.append(textbox("نام بنکدار جزئیات", "تأمین‌کننده: بازرگانی رضایی (بازار مولوی)", 40, 652, 265, 20, 13, 700, COLOR_TEXT_PRIMARY, "right"))
    objs.append(textbox("ضمانت بنکدار", "تضمین اصالت کالا، تاریخ انقضای معتبر و فاکتور رسمی", 40, 674, 265, 18, 11, 500, COLOR_SUCCESS, "right"))
    
    # Sticky Bottom Action Bar
    objs.append(rect("نوار اقدام پایین صفحه", 0, 715, 390, 129, COLOR_SURFACE, 0, 0, COLOR_BORDER, 1))
    
    # Stepper Control
    objs.append(rect("کادر شمارنده پایین", 246, 730, 120, 48, "#F1F5F9", 12, 12, COLOR_BORDER, 1))
    objs.append(textbox("دکمه منفی پایین", "-", 336, 740, 28, 28, 18, 700, COLOR_PRIMARY, "center"))
    objs.append(textbox("عدد شمارنده پایین", "۲ کارتن", 276, 743, 60, 22, 13, 800, COLOR_TEXT_PRIMARY, "center"))
    objs.append(textbox("دکمه مثبت پایین", "+", 248, 740, 28, 28, 18, 700, COLOR_PRIMARY, "center"))
    
    # Add to Cart Button with total price
    objs.append(rect("دکمه افزودن نهایی", 24, 730, 210, 48, COLOR_PRIMARY, 12, 12))
    objs.append(textbox("متن افزودن نهایی", "افزودن به سبد خرید", 24, 736, 210, 20, 14, 700, "#FFFFFF", "center"))
    objs.append(textbox("مبلغ کل دو کارتن", "مبلغ کل: ۱٬۵۰۰٬۰۰۰ تومان", 24, 756, 210, 16, 11, 500, "#BFDBFE", "center"))
    
    objs.extend(home_indicator())
    return {
        "id": "10000000-0000-4000-8000-000000000009",
        "name": "۹. جزئیات محصول",
        "background": {"type": "solid", "color": COLOR_BG},
        "objects": objs
    }

def page_cart() -> Dict[str, Any]:
    objs = status_bar()
    
    # Header
    objs.append(textbox("تیتر صفحه سبد خرید", "سبد خرید", 24, 48, 342, 30, 22, 800, COLOR_TEXT_PRIMARY, "right"))
    objs.append(textbox("تعداد اقلام سبد", "۳ قلم کالا از بازرگانی رضایی (تهران)", 24, 76, 342, 18, 12, 500, COLOR_TEXT_SECONDARY, "right"))
    objs.append(textbox("دکمه حذف همه", "حذف همه", 24, 52, 60, 22, 12, 600, COLOR_DANGER, "left"))
    
    # Cart Items List (3 items)
    items = [
        ("روغن مایع ۱٫۸ لیتری لادن", "🍾", "۲ کارتن (۱۲ عدد)", "۱٬۵۰۰٬۰۰۰ تومان", 100),
        ("ماکارونی ۷۰۰ گرمی زر ماکارون", "🍝", "۱ کارتن (۲۰ عدد)", "۵۰۰٬۰۰۰ تومان", 205),
        ("کنسرو تن ماهی ۱۸۰ گرمی شیلتون", "🐟", "۱ کارتن (۲۴ عدد)", "۱٬۵۶۰٬۰۰۰ تومان", 310),
    ]
    for iname, iicon, ipack, iprice, y in items:
        objs.append(rect(f"کارت سبد {iname}", 24, y, 342, 95, COLOR_SURFACE, 14, 14, COLOR_BORDER, 1))
        
        # Product Icon
        objs.append(rect(f"باکس آیکون {iname}", 286, y + 12, 70, 70, "#F8FAFC", 10, 10, COLOR_BORDER, 1))
        objs.append(textbox(f"شکلک سبد {iname}", iicon, 286, y + 26, 70, 36, 30, 400, COLOR_TEXT_PRIMARY, "center"))
        
        # Item Details
        objs.append(textbox(f"عنوان سبد {iname}", iname, 70, y + 12, 210, 20, 13, 700, COLOR_TEXT_PRIMARY, "right"))
        objs.append(textbox(f"تعداد و بسته {iname}", ipack, 70, y + 34, 210, 16, 11, 500, COLOR_TEXT_SECONDARY, "right"))
        objs.append(textbox(f"مبلغ سبد {iname}", iprice, 70, y + 56, 210, 20, 14, 800, COLOR_PRIMARY, "right"))
        
        # Delete Icon
        objs.append(textbox(f"حذف کالا {iname}", "🗑️", 36, y + 14, 24, 24, 14, 400, COLOR_TEXT_MUTED, "center"))
        
        # Stepper [ - 2 + ]
        objs.append(rect(f"کادر شمارنده سبد {iname}", 32, y + 54, 80, 26, COLOR_PRIMARY_LIGHT, 6, 6, COLOR_PRIMARY, 1))
        objs.append(textbox(f"منهای سبد {iname}", "-", 88, y + 56, 20, 20, 14, 700, COLOR_PRIMARY, "center"))
        objs.append(textbox(f"عدد سبد {iname}", ipack.split()[0], 52, y + 58, 36, 18, 11, 700, COLOR_PRIMARY_DARK, "center"))
        objs.append(textbox(f"مثبت سبد {iname}", "+", 32, y + 56, 20, 20, 14, 700, COLOR_PRIMARY, "center"))
        
    # Order Summary Card
    objs.append(rect("کارت خلاصه صورتحساب", 24, 418, 342, 175, COLOR_SURFACE, 16, 16, COLOR_BORDER, 1))
    objs.append(textbox("تیتر فاکتور", "خلاصهٔ سفارش و فاکتور", 40, 430, 310, 22, 14, 800, COLOR_TEXT_PRIMARY, "right"))
    
    rows = [
        ("جمع کل اقلام (۴ کارتن)", "۳٬۵۶۰٬۰۰۰ تومان", COLOR_TEXT_SECONDARY),
        ("تخفیف ویژه بنکدار", "- ۱۶۰٬۰۰۰ تومان", COLOR_SUCCESS),
        ("هزینه باربری و حمل به مغازه", "رایگان", COLOR_SUCCESS),
    ]
    for i, (rtitle, rval, rcol) in enumerate(rows):
        ry = 460 + i * 24
        objs.append(textbox(f"عنوان سطر {rtitle}", rtitle, 170, ry, 180, 18, 12, 500, COLOR_TEXT_SECONDARY, "right"))
        objs.append(textbox(f"مقدار سطر {rtitle}", rval, 40, ry, 130, 18, 12, 700, rcol, "left"))
        
    objs.append(rect("خط جداکننده جمع کل", 40, 538, 310, 1, COLOR_BORDER))
    
    # Final Total Row
    objs.append(textbox("عنوان مبلغ نهایی", "مبلغ نهایی قابل پرداخت:", 170, 552, 180, 24, 14, 800, COLOR_TEXT_PRIMARY, "right"))
    objs.append(textbox("عدد مبلغ نهایی", "۳٬۴۰۰٬۰۰۰ تومان", 40, 550, 140, 26, 17, 900, COLOR_PRIMARY, "left"))
    
    # Checkout Button
    objs.append(rect("دکمه ثبت نهایی سفارش", 24, 605, 342, 52, COLOR_PRIMARY, 14, 14))
    objs.append(textbox("متن دکمه ثبت سفارش", "ادامه برای ثبت سفارش  (۳٬۴۰۰٬۰۰۰ تومان)", 24, 619, 342, 24, 15, 700, "#FFFFFF", "center"))
    
    # Security Note
    objs.append(textbox("یادداشت امنیت پرداخت", "🔒  تسویه نهایی پس از تحویل بار و بررسی فاکتور فیزیکی انجام می‌شود.", 24, 665, 342, 34, 11, 500, COLOR_TEXT_MUTED, "center", 1.4))
    
    objs.extend(bottom_navigation("سبد خرید"))
    return {
        "id": "10000000-0000-4000-8000-000000000010",
        "name": "۱۰. سبد خرید",
        "background": {"type": "solid", "color": COLOR_BG},
        "objects": objs
    }
