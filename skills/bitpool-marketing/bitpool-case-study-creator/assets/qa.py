#!/usr/bin/env python3
"""
qa.py — mandatory QA for a Bitpool case study. Every page MUST measure exactly
one A4 (1123px tall at the 900px / 2x reference viewport). Anything taller has
overflowed and will spill onto an extra print page.

Usage:
    pip install playwright --break-system-packages && playwright install chromium
    python3 qa.py out.html

It prints per-page heights + any JS errors, writes page1..N.png screenshots,
generates out.pdf (one A4 per page, animations forced to final state) and
rasterises the pages to pdf-N.png so you can eyeball the print output.

A4 @ 96dpi = 1122.5px. Treat <=1126 as fitting (rounding); fix anything taller
using references/fitting-to-a4.md.
"""
import sys, pathlib, subprocess
from playwright.sync_api import sync_playwright

def main():
    html = sys.argv[1]
    url = "file://" + str(pathlib.Path(html).resolve())
    errs = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width":900,"height":1273}, device_scale_factor=2)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(url); pg.wait_for_timeout(400)
        # scroll to trigger every reveal / count-up / ring draw
        H = pg.evaluate("document.body.scrollHeight")
        for y in range(0, H, 500):
            pg.evaluate(f"window.scrollTo(0,{y})"); pg.wait_for_timeout(60)
        pg.wait_for_timeout(1600)
        heights = pg.evaluate(
            "()=>[...document.querySelectorAll('.page')].map((p,i)=>"
            "({page:i+1,h:Math.round(p.getBoundingClientRect().height)}))")
        print("PAGE HEIGHTS (target 1123):", heights)
        print("JS ERRORS:", errs or "none")
        bad = [x for x in heights if x["h"] > 1126]
        print("OVERFLOWING PAGES:", bad or "none — all fit A4")
        for i, el in enumerate(pg.query_selector_all(".page")):
            el.scroll_into_view_if_needed(); pg.wait_for_timeout(250)
            el.screenshot(path=f"page{i+1}.png")
        # PDF export (fires beforeprint so count-ups + rings reach final state)
        pg.emulate_media(media="print")
        pg.evaluate("window.dispatchEvent(new Event('beforeprint'))")
        pdf = html.rsplit(".",1)[0] + ".pdf"
        pg.pdf(path=pdf, width="210mm", height="297mm", print_background=True)
        b.close()
    try:
        subprocess.run(f"pdftoppm -png -r 70 {pdf} pdf", shell=True)
        print("rasterised PDF pages to pdf-*.png")
    except Exception:
        pass
    print("done")

if __name__ == "__main__":
    main()
