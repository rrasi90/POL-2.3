import os
import sys
import time
import asyncio
from pathlib import Path
from playwright.sync_api import sync_playwright

asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
sys.stdout.reconfigure(encoding='utf-8')

OUTPUT_IMAGES_DIR = Path(r"C:\Users\rrasi_oorj8fq\Documents\پل\طراحی\نسخه-۰۱\تصاویر")
OUTPUT_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

PAGES_TO_EXPORT = [
    ("01_صفحه_شروع_Splash.png", "d1000000-0000-4000-8000-000000000001"),
    ("02_معرفی_پل_Onboarding.png", "d1000000-0000-4000-8000-000000000002"),
    ("03_ورود_با_موبایل_Login.png", "d1000000-0000-4000-8000-000000000003"),
    ("04_تأیید_شماره_OTP.png", "d1000000-0000-4000-8000-000000000004"),
    ("05_انتخاب_شهر_City.png", "d1000000-0000-4000-8000-000000000005"),
    ("06_صفحه_اصلی_Home.png", "d1000000-0000-4000-8000-000000000006"),
    ("07_دسته‌بندی_کالاها_Categories.png", "d1000000-0000-4000-8000-000000000007"),
    ("08_فهرست_محصولات_Products.png", "d1000000-0000-4000-8000-000000000008"),
    ("09_جزئیات_محصول_Detail.png", "d1000000-0000-4000-8000-000000000009"),
    ("10_سبد_خرید_Cart.png", "d1000000-0000-4000-8000-000000000010"),
]

def export_all():
    print(f"Starting PNG Export to: {OUTPUT_IMAGES_DIR}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, channel="msedge")
        
        # 1. Export 10 Mobile Pages
        context = browser.new_context(viewport={"width": 1440, "height": 1050}, device_scale_factor=2)
        page = context.new_page()
        
        # Login
        print("Authenticating session...")
        page.goto("http://localhost:5173/login")
        page.fill('input[type="email"]', "pol.test@local.dev")
        page.fill('input[type="password"]', "Pol-Test-2026!")
        page.click('button[type="submit"]')
        page.wait_for_timeout(3000)
        
        for filename, design_id in PAGES_TO_EXPORT:
            url = f"http://localhost:5173/design/{design_id}"
            print(f"Exporting {filename} from {url}...")
            page.goto(url)
            page.wait_for_timeout(5000)
            
            # Find the main canvas
            canvases = page.query_selector_all("canvas")
            target_canvas = None
            for c in canvases:
                box = c.bounding_box()
                if box and box["width"] > 200:
                    target_canvas = c
                    break
                    
            out_file = OUTPUT_IMAGES_DIR / filename
            if target_canvas:
                target_canvas.screenshot(path=str(out_file))
                print(f"  ✓ Saved canvas screenshot: {out_file.name} ({out_file.stat().st_size} bytes)")
            else:
                page.screenshot(path=str(out_file))
                print(f"  ⚠ Fallback page screenshot: {out_file.name} ({out_file.stat().st_size} bytes)")
                
        # 2. Export Master Overview Board (High Res 2200x1450)
        print("\nExporting Master Presentation Overview Board...")
        context_ov = browser.new_context(viewport={"width": 2600, "height": 1700}, device_scale_factor=1.5)
        page_ov = context_ov.new_page()
        
        overview_url = "http://localhost:5173/design/e0000000-0000-4000-8000-000000000002"
        page_ov.goto(overview_url)
        page_ov.wait_for_timeout(7000)
        
        ov_canvases = page_ov.query_selector_all("canvas")
        ov_target = None
        for c in ov_canvases:
            box = c.bounding_box()
            if box and box["width"] > 500:
                ov_target = c
                break
                
        ov_file = OUTPUT_IMAGES_DIR / "نمای_کلی_ده_صفحه_Overview_Board.png"
        if ov_target:
            ov_target.screenshot(path=str(ov_file))
            print(f"  ✓ Saved Overview Board: {ov_file.name} ({ov_file.stat().st_size} bytes)")
        else:
            page_ov.screenshot(path=str(ov_file))
            print(f"  ⚠ Fallback Overview Board: {ov_file.name} ({ov_file.stat().st_size} bytes)")
            
        browser.close()
        print("\nAll PNG exports completed successfully!")

if __name__ == "__main__":
    export_all()
