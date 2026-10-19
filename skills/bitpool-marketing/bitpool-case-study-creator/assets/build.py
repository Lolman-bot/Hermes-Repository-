#!/usr/bin/env python3
"""
build.py — inject the Bitpool cube logo and all prepared image data URLs into a
filled case-study template, producing the final self-contained HTML.

Run AFTER you have:
  1. copied case-study-template.html to your working dir and edited every
     [BRACKETED] content region for the new client, and
  2. run prep-images.py to produce imgs.json.

Usage:
    python3 build.py case-study-template.html imgs.json out.html

Token map (template placeholder  ->  imgs.json key / file):
    __LOGO__         -> logo-b64.txt           (Bitpool cube; used for header, footer, favicon)
    __IMG_HERO__     -> img_hero               (cover exterior)
    __IMG_A__        -> img_a                  (Challenge-page hero)
    __IMG_B__        -> img_b                  (Solution-page hero)
    __IMG_C__        -> img_c                  (Strategic-Value photo)
    __PARTNER_LOGO__ -> partner_logo           (header chip, testimonial, "Delivered with")
    __HEADSHOT__     -> headshot               (testimonial avatar)

Missing image keys fall back gracefully: the hero token is left pointing at an
empty string (the patterned background still shows), and a missing partner logo
leaves an empty chip — but for the canonical look, supply all assets.
"""
import sys, json, os

def main():
    tpl, imgs_json, out = sys.argv[1], sys.argv[2], sys.argv[3]
    here = os.path.dirname(os.path.abspath(__file__))
    h = open(tpl, encoding="utf-8").read()
    imgs = json.load(open(imgs_json))

    # cube logo ships with the skill
    logo_path = os.path.join(here, "logo-b64.txt")
    if not os.path.exists(logo_path):
        logo_path = "logo-b64.txt"
    logo = open(logo_path).read().strip()

    sub = {
        "__LOGO__": logo,
        "__IMG_HERO__": imgs.get("img_hero", ""),
        "__IMG_A__": imgs.get("img_a", ""),
        "__IMG_B__": imgs.get("img_b", ""),
        "__IMG_C__": imgs.get("img_c", ""),
        "__PARTNER_LOGO__": imgs.get("partner_logo", ""),
        "__HEADSHOT__": imgs.get("headshot", ""),
    }
    for k, v in sub.items():
        h = h.replace(k, v)

    # warn on any unfilled content placeholders
    import re
    leftover = re.findall(r"\[[A-Z][^\]]{3,}\]", h)
    if leftover:
        print("WARNING — unfilled content placeholders remain:")
        for x in sorted(set(leftover))[:40]:
            print("   ", x)

    open(out, "w", encoding="utf-8").write(h)
    print(f"wrote {out}  ({round(len(h)/1024/1024,2)} MB)")

if __name__ == "__main__":
    main()
