---
name: pol-persian-rtl-qa
description: Automated QA tool and linter for Persian RTL UI text, typography, numerals, and zero-width non-joiners (ZWNJ).
license: MIT
metadata:
  version: 1.0.0
  category: quality-assurance
  domain: persian-rtl
  tags: [persian, farsi, rtl, qa, typography, zwnj, arabic-glyphs]
---

# Persian & RTL Quality Assurance Skill (`pol-persian-rtl-qa`)

Automated validation tool for Persian UI content, ensuring:
1. No Arabic glyph substitution (enforces Persian `ی` over `ي` U+064A and `ک` over `ك` U+0643).
2. Proper Persian numerals (`۰۱۲۳۴۵۶۷۸۹`) for prices, counts, and phone numbers.
3. Correct Zero-Width Non-Joiner (ZWNJ / نیم‌فاصله - `\u200c`) in verbs, plurals, and compound nouns (`می‌شود`, `دسته‌بندی‌ها`).
4. Detection of unintended English text leakage in user-facing UI labels.
5. Verification of packaging units and currency notation (`تومان`).
6. Consistent, natural Iranian Persian phrasing without awkward translations.

## Usage

Run the checker script against any JSON design, template, or dictionary:

```powershell
python "C:\Users\rrasi_oorj8fq\.gemini\config\skills\pol-persian-rtl-qa\scripts\qa_checker.py" <path_to_file.json>
```
