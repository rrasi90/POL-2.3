# -*- coding: utf-8 -*-
"""Master generator for Pol B2B FMCG App Deliverables in Doory."""

import os
import sys
import json
import uuid
import asyncio
from pathlib import Path

# Fix Windows Proactor policy
asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Change to Doory backend directory
backend_dir = r"C:\Star\Nima instagram\doory\backend"
os.chdir(backend_dir)
sys.path.insert(0, backend_dir)
sys.path.insert(0, r"C:\Users\rrasi_oorj8fq\.gemini\antigravity\brain\153804b2-55ae-45d1-abc6-97fd35b7feee\scratch")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "doory.settings.dev")

import django
django.setup()
asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from django.contrib.auth import get_user_model
from django.core.management import call_command
from apps.designs.models import Design
from apps.gallery.models import Template

from build_pol_pages import (
    page_splash, page_onboarding, page_login, page_otp_verify, page_city_select,
    page_home, page_categories, page_product_list, page_product_detail, page_cart
)
from build_pol_system_pages import page_design_system_guide, page_reference_components
from build_pol_overview_board import build_overview_board

sys.stdout.reconfigure(encoding='utf-8')

DOCS_OUTPUT_DIR = Path(r"C:\Users\rrasi_oorj8fq\Documents\پل\طراحی\نسخه-۰۱")
DOCS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

User = get_user_model()
user = User.objects.filter(email="pol.test@local.dev").first()
if not user:
    user = User.objects.create_user(
        email="pol.test@local.dev",
        password="Pol-Test-2026!",
        display_name="کاربر آزمون پل",
        is_active=True,
        is_email_verified=True,
    )

def generate_master_project():
    print("\n--- 1. Generating Master 12-Page Project ---")
    pages = [
        page_splash(),
        page_onboarding(),
        page_login(),
        page_otp_verify(),
        page_city_select(),
        page_home(),
        page_categories(),
        page_product_list(),
        page_product_detail(),
        page_cart(),
        page_design_system_guide(),
        page_reference_components(),
    ]
    
    doc = {
        "schemaVersion": 1,
        "width": 390,
        "height": 844,
        "unit": "px",
        "meta": {"presetId": "mobile-app"},
        "pages": pages,
    }
    
    project_title = "پل | اپلیکیشن مغازه‌داران | نسخهٔ ۰۱"
    master_uuid = "e0000000-0000-4000-8000-000000000001"
    
    design, created = Design.objects.get_or_create(
        id=master_uuid,
        defaults={
            "title": project_title,
            "owner": user,
            "width": 390,
            "height": 844,
            "preset": "mobile-app",
            "document": doc,
            "page_count": len(pages),
        }
    )
    if not created:
        design.title = project_title
        design.document = doc
        design.page_count = len(pages)
        design.save()
        
    print(f"Master Design Project saved: ID={design.id}, Title='{design.title}', Pages={design.page_count}")
    
    # Also save as local JSON in user output directory
    master_json_path = DOCS_OUTPUT_DIR / "پروژه_اصلی_اپلیکیشن_پل.json"
    master_json_path.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved master JSON to: {master_json_path}")
    
    return design, doc

def generate_individual_page_designs():
    print("\n--- 2. Generating 10 Standalone Page Designs for direct editing ---")
    page_builders = [
        ("پل — ۱. شروع (Splash)", "d1000000-0000-4000-8000-000000000001", page_splash()),
        ("پل — ۲. معرفی پل (Onboarding)", "d1000000-0000-4000-8000-000000000002", page_onboarding()),
        ("پل — ۳. ورود با شمارهٔ موبایل (Login)", "d1000000-0000-4000-8000-000000000003", page_login()),
        ("پل — ۴. تأیید شمارهٔ موبایل (OTP)", "d1000000-0000-4000-8000-000000000004", page_otp_verify()),
        ("پل — ۵. انتخاب شهر (City Select)", "d1000000-0000-4000-8000-000000000005", page_city_select()),
        ("پل — ۶. صفحهٔ اصلی (Home)", "d1000000-0000-4000-8000-000000000006", page_home()),
        ("پل — ۷. دسته‌بندی کالاها (Categories)", "d1000000-0000-4000-8000-000000000007", page_categories()),
        ("پل — ۸. فهرست محصولات (Product List)", "d1000000-0000-4000-8000-000000000008", page_product_list()),
        ("پل — ۹. جزئیات محصول (Product Detail)", "d1000000-0000-4000-8000-000000000009", page_product_detail()),
        ("پل — ۱۰. سبد خرید (Cart)", "d1000000-0000-4000-8000-000000000010", page_cart()),
    ]
    created_designs = []
    for title, did, p_dict in page_builders:
        single_doc = {
            "schemaVersion": 1,
            "width": 390,
            "height": 844,
            "unit": "px",
            "meta": {"presetId": "mobile-app"},
            "pages": [p_dict],
        }
        d_obj, _ = Design.objects.get_or_create(
            id=did,
            defaults={
                "title": title,
                "owner": user,
                "width": 390,
                "height": 844,
                "preset": "mobile-app",
                "document": single_doc,
                "page_count": 1,
            }
        )
        d_obj.document = single_doc
        d_obj.save()
        created_designs.append((title, did))
        print(f"  ✓ Standalone design ready: '{title}' (ID: {did})")
    return created_designs

def generate_overview_board():
    print("\n--- 3. Generating Master Presentation Overview Board ---")
    board_data = build_overview_board()
    board_uuid = "e0000000-0000-4000-8000-000000000002"
    board_title = "پل | نمای کلی ده صفحه"
    
    board_design, _ = Design.objects.get_or_create(
        id=board_uuid,
        defaults={
            "title": board_title,
            "owner": user,
            "width": board_data["width"],
            "height": board_data["height"],
            "preset": "presentation",
            "document": board_data,
            "page_count": 1,
        }
    )
    board_design.title = board_title
    board_design.width = board_data["width"]
    board_design.height = board_data["height"]
    board_design.document = board_data
    board_design.save()
    
    print(f"Overview Board Design saved: ID={board_design.id}, Dimensions: {board_design.width}x{board_design.height}")
    
    # Save as JSON in documents
    board_json_path = DOCS_OUTPUT_DIR / "نمای_کلی_ده_صفحه.json"
    board_json_path.write_text(json.dumps(board_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved overview JSON to: {board_json_path}")
    return board_design, board_data

def generate_reusable_base_template():
    print("\n--- 4. Generating Reusable Base Template for Future Projects ---")
    base_template_data = {
        "title": "الگوی پایه اپلیکیشن موبایل پل",
        "slug": "pol-mobile-app-base-template",
        "category": "mobile-app",
        "tags": ["پل", "قالب-پایه", "موبایل", "فارسی", "سیستم-طراحی"],
        "description": "الگوی مرجع و پایهٔ سیستم طراحی اپلیکیشن‌های موبایل پل برای توسعه و ساخت صفحات جدید با حفظ کامل هویت بصری، دکمه‌ها، فیلدها و ساختار RTL.",
        "preset": "mobile-app",
        "is_featured": True,
        "is_published": True,
        "document": {
            "schemaVersion": 1,
            "width": 390,
            "height": 844,
            "unit": "px",
            "meta": {"presetId": "mobile-app"},
            "pages": [
                page_design_system_guide(),
                page_reference_components(),
                page_home(),
            ]
        }
    }
    tpl_file = backend_dir + r"\data\pol_base_template.json"
    Path(tpl_file).write_text(json.dumps(base_template_data, ensure_ascii=False, indent=2), encoding="utf-8")
    call_command("import_template", tpl_file, publish=True, create_categories=True)
    
    # Copy to user documents
    tpl_doc_path = DOCS_OUTPUT_DIR / "الگوی_پایه_پروژه_پل.json"
    tpl_doc_path.write_text(json.dumps(base_template_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Base template imported and saved to: {tpl_doc_path}")

def run_qa_audit(master_doc):
    print("\n--- 5. Running Persian & RTL QA Audit (pol-persian-rtl-qa) ---")
    qa_checker_path = Path(r"C:\Users\rrasi_oorj8fq\.gemini\config\skills\pol-persian-rtl-qa\scripts\qa_checker.py")
    if qa_checker_path.exists():
        import importlib.util
        spec = importlib.util.spec_from_file_location("qa_checker", str(qa_checker_path))
        qa_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(qa_mod)
        
        issues = qa_mod.audit_document(master_doc)
        report_md = qa_mod.format_report_markdown(issues, "گزارش رسمی کنترل کیفی زبان فارسی و استانداردهای RTL اپلیکیشن پل")
        
        report_path = DOCS_OUTPUT_DIR / "گزارش_کنترل_کیفی_فارسی_RTL.md"
        report_path.write_text(report_md, encoding="utf-8")
        print(f"QA Audit Complete! Issues found: {len(issues)}. Report saved to: {report_path}")
        return len(issues), report_md
    else:
        print("QA checker not found at:", qa_checker_path)
        return 0, ""

if __name__ == "__main__":
    master_d, master_doc = generate_master_project()
    generate_individual_page_designs()
    generate_overview_board()
    generate_reusable_base_template()
    run_qa_audit(master_doc)
    print("\nAll deliverables generated successfully in Doory!")
