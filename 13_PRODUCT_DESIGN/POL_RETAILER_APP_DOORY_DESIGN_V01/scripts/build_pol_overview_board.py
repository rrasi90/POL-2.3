# -*- coding: utf-8 -*-
"""Overview Presentation Board Builder for Pol 10 Mobile Screens."""

from typing import Any, Dict, List
from design_builder_tokens import (
    COLOR_PRIMARY, COLOR_PRIMARY_LIGHT, COLOR_PRIMARY_DARK,
    COLOR_BG, COLOR_SURFACE, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY,
    COLOR_TEXT_MUTED, COLOR_BORDER, COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER,
    rect, textbox, circle
)
from build_pol_pages import (
    page_splash, page_onboarding, page_login, page_otp_verify, page_city_select,
    page_home, page_categories, page_product_list, page_product_detail, page_cart
)

OVERVIEW_WIDTH = 2200
OVERVIEW_HEIGHT = 1450

def build_overview_board() -> Dict[str, Any]:
    objs = []
    
    # 1. Dark Backdrop
    objs.append(rect("پس‌زمینه تیره ارائه", 0, 0, OVERVIEW_WIDTH, OVERVIEW_HEIGHT, "#0B0F19"))
    
    # Subtle gradient glow circles
    objs.append(circle("هاله آبی بالا راست", 1800, -100, 300, "#1E3A8A", opacity=0.3))
    objs.append(circle("هاله بنفش پایین چپ", -100, 1000, 350, "#1E1B4B", opacity=0.3))
    
    # 2. Presentation Header
    objs.append(rect("نشان کپسولی پل", 1950, 40, 150, 38, "#1E293B", 19, 19, "#334155", 1))
    objs.append(textbox("نشان پل بالا", "پل | POL", 1950, 48, 150, 22, 16, 800, "#60A5FA", "center"))
    
    objs.append(textbox("عنوان اصلی پوستر", "اپلیکیشن مغازه‌داران «پل» — تمام صفحات اصلی و حالت‌های مهم", 400, 35, 1450, 44, 28, 900, "#FFFFFF", "center"))
    objs.append(textbox("زیرعنوان پوستر", "سیستم خرید عمده B2B FMCG • طراحی کاملاً راست‌به‌چپ (RTL) • فونت رسمی Vazirmatn • پالت رنگی مصوب #246BFD", 400, 80, 1450, 24, 15, 500, "#94A3B8", "center"))
    
    # 3. 10 Phone Frames (2 rows of 5)
    # Scale: standard phone 390x844 scaled by ~0.65 => 254 x 550
    # Or width 380 x 580
    frame_w = 380
    frame_h = 580
    
    row1_y = 135
    row2_y = 780
    
    col_xs = [1720, 1310, 900, 490, 80] # RTL order: 0 to 4
    
    page_data = [
        # Row 1
        ("۱. صفحهٔ شروع", "(Splash)", page_splash(), col_xs[0], row1_y),
        ("۲. معرفی اپلیکیشن", "(Onboarding)", page_onboarding(), col_xs[1], row1_y),
        ("۳. ورود با موبایل", "(Login OTP)", page_login(), col_xs[2], row1_y),
        ("۴. تأیید شماره", "(OTP Verify)", page_otp_verify(), col_xs[3], row1_y),
        ("۵. انتخاب شهر", "(City Select)", page_city_select(), col_xs[4], row1_y),
        # Row 2
        ("۶. صفحهٔ اصلی", "(Home)", page_home(), col_xs[0], row2_y),
        ("۷. دسته‌بندی‌ها", "(Categories)", page_categories(), col_xs[1], row2_y),
        ("۸. فهرست محصولات", "(Product List)", page_product_list(), col_xs[2], row2_y),
        ("۹. جزئیات محصول", "(Product Detail)", page_product_detail(), col_xs[3], row2_y),
        ("۱۰. سبد خرید", "(Cart)", page_cart(), col_xs[4], row2_y),
    ]
    
    scale = frame_w / 390.0 # ~0.974
    
    for title_fa, title_en, p_dict, fx, fy in page_data:
        # Outer Bezel
        objs.append(rect(f"قاب گوشی {title_fa}", fx - 6, fy - 6, frame_w + 12, frame_h + 12, "#1E293B", 36, 36, "#334155", 2))
        # Inner Screen Surface
        objs.append(rect(f"صفحه داخلی {title_fa}", fx, fy, frame_w, frame_h, p_dict["background"]["color"], 30, 30))
        # Dynamic Island / Notch
        notch_w = 90
        objs.append(rect(f"ناچ {title_fa}", fx + (frame_w - notch_w) / 2, fy + 8, notch_w, 18, "#000000", 9, 9))
        
        # Scale and add objects from page (clamp y to frame_h)
        for orig in p_dict["objects"]:
            orig_top = orig.get("top", 0)
            orig_left = orig.get("left", 0)
            orig_w = orig.get("width", 0)
            orig_h = orig.get("height", 0)
            
            # Map into phone frame
            mapped_top = fy + orig_top * (frame_h / 844.0)
            mapped_left = fx + orig_left * scale
            mapped_w = orig_w * scale
            mapped_h = orig_h * (frame_h / 844.0)
            
            if mapped_top + mapped_h > fy + frame_h - 10:
                continue
                
            o_copy = dict(orig)
            o_copy["left"] = mapped_left
            o_copy["top"] = mapped_top
            o_copy["width"] = mapped_w
            o_copy["height"] = mapped_h
            if "fontSize" in o_copy:
                o_copy["fontSize"] = max(8, o_copy["fontSize"] * scale * 0.95)
            if "rx" in o_copy:
                o_copy["rx"] = o_copy["rx"] * scale
                o_copy["ry"] = o_copy["ry"] * scale
            if "radius" in o_copy:
                o_copy["radius"] = o_copy["radius"] * scale
                
            objs.append(o_copy)
            
        # Label below frame
        label_y = fy + frame_h + 14
        objs.append(textbox(f"عنوان قاب {title_fa}", title_fa, fx, label_y, frame_w, 20, 13, 700, "#F1F5F9", "center"))
        objs.append(textbox(f"عنوان لاتین {title_fa}", title_en, fx, label_y + 18, frame_w, 16, 11, 400, "#94A3B8", "center"))
        
    return {
        "title": "پل | نمای کلی ده صفحه",
        "slug": "pol-ten-screens-overview",
        "schemaVersion": 1,
        "width": OVERVIEW_WIDTH,
        "height": OVERVIEW_HEIGHT,
        "unit": "px",
        "pages": [
            {
                "id": "20000000-0000-4000-8000-000000000000",
                "name": "نمای کلی ده صفحه",
                "background": {"type": "solid", "color": "#0B0F19"},
                "objects": objs
            }
        ]
    }
