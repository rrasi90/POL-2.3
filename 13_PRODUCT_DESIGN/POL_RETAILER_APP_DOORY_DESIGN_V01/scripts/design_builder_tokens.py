# -*- coding: utf-8 -*-
"""Design system builder for Pol B2B FMCG Mobile Application in Doory."""

import json
import uuid
from typing import Any, Dict, List

# Primary Design Tokens
COLOR_PRIMARY = "#246BFD"
COLOR_PRIMARY_LIGHT = "#EFF6FF"
COLOR_PRIMARY_DARK = "#1E40AF"
COLOR_BG = "#F5F7FA"
COLOR_SURFACE = "#FFFFFF"
COLOR_TEXT_PRIMARY = "#172033"
COLOR_TEXT_SECONDARY = "#64748B"
COLOR_TEXT_MUTED = "#94A3B8"
COLOR_BORDER = "#E5EAF2"
COLOR_SUCCESS = "#0DB89D"
COLOR_WARNING = "#F59E0B"
COLOR_DANGER = "#DC3545"

FONT_FAMILY = '"Vazirmatn", sans-serif'

def rect(name: str, left: float, top: float, width: float, height: float,
         fill: str = COLOR_SURFACE, rx: float = 0, ry: float = 0,
         stroke: str = None, stroke_width: float = 1, opacity: float = 1.0) -> Dict[str, Any]:
    return {
        "type": "rect",
        "name": name,
        "left": left,
        "top": top,
        "width": width,
        "height": height,
        "rx": rx,
        "ry": ry,
        "fill": fill,
        "stroke": stroke,
        "strokeWidth": stroke_width if stroke else 0,
        "strokeUniform": True,
        "scaleX": 1,
        "scaleY": 1,
        "angle": 0,
        "opacity": opacity,
        "visible": True,
        "originX": "left",
        "originY": "top",
    }

def textbox(name: str, text: str, left: float, top: float, width: float, height: float,
            size: float, weight: int = 400, fill: str = COLOR_TEXT_PRIMARY,
            align: str = "right", line_height: float = 1.4) -> Dict[str, Any]:
    return {
        "type": "textbox",
        "name": name,
        "text": text,
        "left": left,
        "top": top,
        "width": width,
        "height": height,
        "fontSize": size,
        "fontWeight": weight,
        "fontFamily": FONT_FAMILY,
        "fontStyle": "normal",
        "lineHeight": line_height,
        "charSpacing": 0,
        "textAlign": align,
        "direction": "rtl",
        "originX": "left",
        "originY": "top",
        "fill": fill,
        "stroke": None,
        "scaleX": 1,
        "scaleY": 1,
        "angle": 0,
        "opacity": 1.0,
        "visible": True,
    }

def circle(name: str, left: float, top: float, radius: float,
           fill: str = COLOR_PRIMARY, stroke: str = None, stroke_width: float = 1,
           opacity: float = 1.0) -> Dict[str, Any]:
    return {
        "type": "circle",
        "name": name,
        "left": left,
        "top": top,
        "radius": radius,
        "fill": fill,
        "stroke": stroke,
        "strokeWidth": stroke_width if stroke else 0,
        "strokeUniform": True,
        "originX": "left",
        "originY": "top",
        "scaleX": 1,
        "scaleY": 1,
        "angle": 0,
        "opacity": opacity,
        "visible": True,
    }

def status_bar() -> List[Dict[str, Any]]:
    """iOS standard status bar with Persian numeral time."""
    return [
        textbox("زمان سیستم", "۹:۴۱", 320, 14, 50, 20, 14, 700, COLOR_TEXT_PRIMARY, "center"),
        # Cellular / Wifi / Battery indicators
        rect("نشانگر باتری مرز", 24, 18, 22, 11, "transparent", 3, 3, COLOR_TEXT_PRIMARY, 1),
        rect("نشانگر باتری شارژ", 26, 20, 15, 7, COLOR_TEXT_PRIMARY, 1.5, 1.5),
        rect("نشانگر باتری قطب", 21, 21.5, 2, 4, COLOR_TEXT_PRIMARY, 1, 1),
        circle("وای‌فای ۳", 54, 18, 5, COLOR_TEXT_PRIMARY),
        circle("وای‌فای ۲", 55, 21, 3.5, COLOR_SURFACE),
        circle("وای‌فای ۱", 56, 23, 2, COLOR_TEXT_PRIMARY),
        rect("آنتن ۴", 70, 17, 3, 11, COLOR_TEXT_PRIMARY, 1, 1),
        rect("آنتن ۳", 75, 19, 3, 9, COLOR_TEXT_PRIMARY, 1, 1),
        rect("آنتن ۲", 80, 22, 3, 6, COLOR_TEXT_PRIMARY, 1, 1),
        rect("آنتن ۱", 85, 25, 3, 3, COLOR_TEXT_PRIMARY, 1, 1),
    ]

def home_indicator() -> List[Dict[str, Any]]:
    """Bottom swipe bar."""
    return [
        rect("خط خانه پایین", 125, 830, 140, 5, "#CBD5E1", 2.5, 2.5)
    ]

def bottom_navigation(active_tab: str = "خانه") -> List[Dict[str, Any]]:
    """Standard 5-tab commerce navigation bar."""
    tabs = [
        ("خانه", "🏠", 312),
        ("دسته‌بندی‌ها", "📁", 234),
        ("سبد خرید", "🛒", 156),
        ("سفارش‌ها", "📋", 78),
        ("حساب کاربری", "👤", 0),
    ]
    objects = [
        # Bar background with top border
        rect("پس‌زمینه نوار پایین", 0, 770, 390, 74, COLOR_SURFACE, 0, 0, COLOR_BORDER, 1),
    ]
    for name, icon, left in tabs:
        is_active = (name == active_tab)
        color = COLOR_PRIMARY if is_active else COLOR_TEXT_MUTED
        bg_color = COLOR_PRIMARY_LIGHT if is_active else "transparent"
        
        # Pill highlight for active tab
        if is_active:
            objects.append(rect(f"نشانگر تب {name}", left + 14, 776, 50, 48, bg_color, 12, 12))
            
        objects.append(textbox(f"آیکون {name}", icon, left, 780, 78, 22, 18, 400, color, "center"))
        objects.append(textbox(f"عنوان {name}", name, left, 804, 78, 16, 11, 700 if is_active else 500, color, "center"))
        
        # Cart item badge
        if name == "سبد خرید":
            objects.append(circle("نشان تعداد سبد", left + 46, 776, 8, COLOR_DANGER))
            objects.append(textbox("عدد نشان سبد", "۳", left + 46, 778, 16, 14, 10, 700, "#FFFFFF", "center"))
            
    objects.extend(home_indicator())
    return objects
