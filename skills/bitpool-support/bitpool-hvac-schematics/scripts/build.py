#!/usr/bin/env python3
"""
Bitpool HVAC schematic builder / QA helper.

Two jobs:
  1. inject  — replace the __LOGO__ placeholder in a built HTML page with the
               base64 cube-logo data URL from assets/logo-b64.txt.
  2. render  — rasterise the page with Playwright Chromium so you can eyeball
               the schematic before shipping (catches mis-placed chips,
               overlapping glyphs, broken risers).

Usage:
    python build.py inject  path/to/page.html
    python build.py render  path/to/page.html  [out.png]  [--width 1480] [--full]

The skill's SKILL.md explains where this fits in the workflow. Run `inject`
once after writing the page, then `render` to QA. Re-run `render` after edits.
"""
import sys, os, pathlib, argparse

SKILL_DIR = pathlib.Path(__file__).resolve().parent.parent
LOGO_TXT  = SKILL_DIR / "assets" / "logo-b64.txt"

def inject(html_path):
    logo = LOGO_TXT.read_text(encoding="utf-8").strip()
    p = pathlib.Path(html_path)
    html = p.read_text(encoding="utf-8")
    n = html.count("__LOGO__")
    if n == 0:
        print(f"[inject] no __LOGO__ placeholder found in {p.name} — already injected?")
        return
    html = html.replace("__LOGO__", logo)
    with open(p, "w", encoding="utf-8", newline="") as fh:  # keep existing line endings
        fh.write(html)
    print(f"[inject] embedded cube logo into {p.name} ({n} placeholder(s) replaced)")

def render(html_path, out=None, width=1480, full=True):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("Playwright not installed. Run: python -m pip install playwright && python -m playwright install chromium")
    p = pathlib.Path(html_path)
    out = out or str(p.with_suffix(".preview.png"))
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": width, "height": 1200}, device_scale_factor=2)
        pg.goto(p.resolve().as_uri())  # correct file:// URL on Windows too
        pg.wait_for_timeout(900)
        pg.screenshot(path=out, full_page=full)
        b.close()
    print(f"[render] wrote {out}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["inject", "render"])
    ap.add_argument("html")
    ap.add_argument("out", nargs="?")
    ap.add_argument("--width", type=int, default=1480)
    ap.add_argument("--full", action="store_true", default=True)
    a = ap.parse_args()
    if a.cmd == "inject":
        inject(a.html)
    else:
        render(a.html, a.out, a.width, a.full)
