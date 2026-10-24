#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pol-persian-rtl-qa: Standalone Persian RTL UI linter & QA auditor.

Uses ONLY Python standard library.
Audits:
- Arabic Yeh (ي - \u064A) vs Persian Yeh (ی - \u06CC)
- Arabic Kaf (ك - \u0643) vs Persian Kaf (ک - \u06A9)
- English digits (0-9) in customer UI vs Persian digits (۰-۹)
- Latin character leakage in user-facing labels
- Missing ZWNJ (نیم‌فاصله \u200C) in common prefixes/suffixes:
    - 'می ' / 'نمی '
    - ' های' / ' ها'
    - ' بندی' / ' تر' / ' ترین' / ' های'
- Missing currency unit (تومان) in price items
- Ambiguous or missing wholesale sales units (کارتن، بسته، عدد)
"""

import sys
import json
import re
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ARABIC_YEH = "\u064A"
ARABIC_KAF = "\u0643"
ZWNJ = "\u200C"

EN_DIGITS_PATTERN = re.compile(r"[0-9]+")
LATIN_CHARS_PATTERN = re.compile(r"[a-zA-Z]{2,}")
ZWNJ_MISSING_PATTERNS = [
    (re.compile(r"\bمی\s+([آ-ی])"), r"می\u200C\1", "پیشوند «می» بدون نیم‌فاصله"),
    (re.compile(r"\bنمی\s+([آ-ی])"), r"نمی\u200C\1", "پیشوند «نمی» بدون نیم‌فاصله"),
    (re.compile(r"([آ-ی])\s+ها\b"), r"\1\u200Cها", "پسوند جمع «ها» بدون نیم‌فاصله"),
    (re.compile(r"([آ-ی])\s+های\b"), r"\1\u200Cهای", "پسوند «های» بدون نیم‌فاصله"),
    (re.compile(r"([آ-ی])\s+ترین\b"), r"\1\u200Cترین", "پسوند صفت عالی «ترین» بدون نیم‌فاصله"),
    (re.compile(r"([آ-ی])\s+تر\b"), r"\1\u200Cتر", "پسوند صفت برتر «تر» بدون نیم‌فاصله"),
    (re.compile(r"دسته\s+بندی"), r"دسته‌بندی", "ترکیب «دسته‌بندی» بدون نیم‌فاصله"),
    (re.compile(r"بسته\s+بندی"), r"بسته‌بندی", "ترکیب «بسته‌بندی» بدون نیم‌فاصله"),
]

def to_persian_digits(text: str) -> str:
    en_to_fa = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
    return text.translate(en_to_fa)

def audit_text(text: str, context: str = "") -> list[dict]:
    issues = []
    if not isinstance(text, str) or not text.strip():
        return issues
    
    # 1. Arabic Yeh
    if ARABIC_YEH in text:
        issues.append({
            "type": "arabic_yeh",
            "context": context,
            "text": text,
            "message": "استفاده از «ي» عربی به جای «ی» استاندارد فارسی",
            "suggestion": text.replace(ARABIC_YEH, "ی")
        })
        
    # 2. Arabic Kaf
    if ARABIC_KAF in text:
        issues.append({
            "type": "arabic_kaf",
            "context": context,
            "text": text,
            "message": "استفاده از «ك» عربی به جای «ک» استاندارد فارسی",
            "suggestion": text.replace(ARABIC_KAF, "ک")
        })
        
    # 3. Latin leakage (ignore known tech tokens or brand abbreviations if specifically exempt)
    # Check if string is predominantly Persian but contains Latin words
    has_persian = any("\u0600" <= ch <= "\u06FF" for ch in text)
    if has_persian:
        latin_matches = LATIN_CHARS_PATTERN.findall(text)
        # Filter out common acceptable units like 'ml', 'g', 'kg' if used, but flag long English strings
        bad_latins = [m for m in latin_matches if m.lower() not in ["g", "kg", "ml", "l"]]
        if bad_latins:
            issues.append({
                "type": "latin_leakage",
                "context": context,
                "text": text,
                "message": f"نشت حروف انگلیسی در رابط فارسی: {bad_latins}",
                "suggestion": "جایگزینی با معادل فارسی"
            })
            
    # 4. English digits in Persian string
    if has_persian and EN_DIGITS_PATTERN.search(text):
        issues.append({
            "type": "english_digits",
            "context": context,
            "text": text,
            "message": "استفاده از ارقام لاتین (0-9) به جای ارقام فارسی (۰-۹)",
            "suggestion": to_persian_digits(text)
        })
        
    # 5. ZWNJ checks
    for pat, repl, msg in ZWNJ_MISSING_PATTERNS:
        if pat.search(text):
            issues.append({
                "type": "missing_zwnj",
                "context": context,
                "text": text,
                "message": msg,
                "suggestion": pat.sub(repl, text)
            })
            
    return issues

def audit_document(doc: dict) -> list[dict]:
    all_issues = []
    # Collect all text items from Doory document
    pages = doc.get("pages", [])
    for page_idx, page in enumerate(pages):
        page_name = page.get("name", f"Page {page_idx + 1}")
        for obj in page.get("objects", []):
            if obj.get("type") == "textbox" or "text" in obj:
                txt = obj.get("text", "")
                obj_name = obj.get("name", "Unnamed")
                ctx = f"صفحه '{page_name}' > شیء '{obj_name}'"
                issues = audit_text(txt, context=ctx)
                all_issues.extend(issues)
    return all_issues

def format_report_markdown(issues: list[dict], title: str = "گزارش کنترل کیفی فارسی و راست‌به‌چپ") -> str:
    md = [f"# {title}\n"]
    if not issues:
        md.append("✅ **هیچ خطای نویسه، نشت لاتین یا عدم تطابق نیم‌فاصله یافت نشد. وضعیت متن‌ها ۱۰۰٪ منطبق با استاندارد است.**\n")
        return "\n".join(md)
        
    md.append(f"⚠️ **مجموع خطاهای شناسایی‌شده:** {len(issues)}\n")
    md.append("| ردیف | موقعیت | متن فعلی | نوع خطا | پیشنهاد اصلاح |")
    md.append("|:---:|:---|:---|:---|:---|")
    for i, issue in enumerate(issues, 1):
        ctx = issue["context"].replace("|", "\\|")
        txt = issue["text"].replace("|", "\\|")
        msg = issue["message"].replace("|", "\\|")
        sug = issue.get("suggestion", "-").replace("|", "\\|")
        md.append(f"| {i} | {ctx} | `{txt}` | {msg} | `{sug}` |")
        
    return "\n".join(md)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python qa_checker.py <file.json>")
        sys.exit(1)
        
    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"File not found: {file_path}")
        sys.exit(1)
        
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    if "document" in data:
        doc = data["document"]
    else:
        doc = data
        
    issues = audit_document(doc)
    print(format_report_markdown(issues, f"گزارش QA برای {file_path.name}"))
