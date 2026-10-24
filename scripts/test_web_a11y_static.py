"""TODO-144 - web a11y static guards.

No JS test runner installed (risk to TODO-084 advisory blocker). These guards are
pure Python / shell greps against the source tree; they verify the a11y markers that
are under our control and document known gaps.

Run with:  python scripts/test_web_a11y_static.py
"""

import glob, io, os, re, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WEB_DIR = REPO_ROOT / "mvp" / "apps" / "web"
os.environ.setdefault("POL_JWT_SECRET", "test-secret-key-for-auth-contract-tests-only-32bytes!!")

# ── helpers ────────────────────────────────────────────────────────────────

def _pages():
    for p in sorted(glob.glob(str(WEB_DIR / "src" / "app" / "**" / "*.tsx"), recursive=True)):
        yield Path(p)


def _css():
    p = WEB_DIR / "src" / "globals.css"
    if p.exists():
        return io.open(p, encoding="utf-8").read()
    return ""


def _has(needle: str, haystack: str) -> bool:
    return needle in haystack


# ── guards ─────────────────────────────────────────────────────────────────

def test_html_lang_dir():
    """Root layout must declare lang + direction."""
    # layout.tsx is the only file that renders <html>
    layout = Path(WEB_DIR / "src" / "app" / "layout.tsx")
    if not layout.exists():
        raise FileNotFoundError("layout.tsx not found")
    txt = io.open(layout, encoding="utf-8").read()
    assert "lang=" in txt, "Root layout missing `lang=` on <html>"
    assert "dir=" in txt, "Root layout missing `dir=` on <html>"
    print("PASS: HTML lang / dir present in layout.tsx")


def test_focus_visible_in_css():
    """focus-visible utility should be present in the global stylesheet."""
    css = _css()
    assert "focus-visible" in css, (
        "focus-visible not found in src/globals.css; "
        "add a :focus-visible { ... } rule or import from the design system"
    )
    print("PASS: focus-visible utility in globals.css")


def test_no_unnamed_buttons():
    """Every <button> in a dashboard page should carry an accessible name."""
    bad = []
    for pg in _pages():
        txt = io.open(pg, encoding="utf-8", errors="ignore").read()
        for m in re.finditer(r"<button\b[^>]*>", txt):
            segment = txt[m.start(): m.start() + 300]
            # a button is "named" if the 300-char segment contains aria-label,
            # title, or inner text that isn't just whitespace
            if not re.search(r"aria-label|title|>[^<>\s]+", segment):
                # avoid false positives on <button disabled> etc.
                label = re.search(r">\s*([^<>\s]+)", segment)
                if not label:
                    bad.append(str(pg.relative_to(WEB_DIR)))
    if bad:
        raise AssertionError(
            f"Unnamed buttons found in: {bad}"  # noqa: E501
        )
    print(f"PASS: no unnamed buttons across {len(list(_pages()))} page files")


def test_no_alt_less_images():
    """Every <img> in a page should carry an alt attribute."""
    bad = []
    for pg in _pages():
        txt = io.open(pg, encoding="utf-8", errors="ignore").read()
        for m in re.finditer(r"<img\b[^>]*>", txt):
            seg = txt[m.start(): m.start() + 300]
            if not re.search(r'\balt\s*=', seg):
                bad.append(str(pg.relative_to(WEB_DIR)))
    if bad:
        raise AssertionError(f"Images without alt: {bad}")
    print(f"PASS: all images have alt attributes across {len(list(_pages()))} pages")


def test_viewport_meta():
    """Viewport meta should be declared (Next.js default or explicit)."""
    # Check the page's HTML template; Next auto-inserts it but we verify presence.
    # Search across all page files for <meta name="viewport">
    found = False
    for pg in _pages():
        txt = io.open(pg, encoding="utf-8", errors="ignore").read()
        if "name=\"viewport\"" in txt:
            found = True
            break
    if not found:
        raise AssertionError("viewport meta not found in any page; Next.js adds it by default")
    print("PASS: viewport meta present")


# ── runner ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    tests = [
        test_html_lang_dir,
        test_focus_visible_in_css,
        test_no_unnamed_buttons,
        test_no_alt_less_images,
        test_viewport_meta,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"FAIL: {t.__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed out of {len(tests)} a11y guards")
    sys.exit(0 if failed == 0 else 1)