#!/usr/bin/env python3
"""
prep-images.py — prepare every image asset for a Bitpool case study and emit a
single imgs.json that build.py injects into the template.

Usage (edit the PATHS below, then run):
    pip install pillow pillow-avif-plugin --break-system-packages
    python3 prep-images.py

Outputs: imgs.json  with keys:
    img_hero, img_a, img_b, img_c   (full-bleed hero renders, JPEG, ~1700px wide)
    partner_logo                    (partner/client logo, bg stripped, PNG, transparent)
    headshot                        (testimonial portrait, square, JPEG)

Notes
-----
* Hero renders are the stars of the document — feed the highest-res source you have.
* AVIF logos open via pillow-avif-plugin; PNG/SVG-rasterised/JPG also fine.
* If a partner logo already has a transparent background, the strip step is a no-op.
* Leave any asset you don't have as None; build.py falls back to the patterned beat
  for missing hero images and to a text chip for a missing partner logo.
"""
from PIL import Image
import base64, io, json

try:
    import pillow_avif  # noqa: enables .avif  (pip install pillow-avif-plugin)
except Exception:
    pass

# ---- EDIT THESE PATHS ------------------------------------------------------
PATHS = {
    "img_hero": "hero.png",        # exterior / establishing shot (cover)
    "img_a":    "image_a.png",     # interior hero #1  (e.g. server hall)  -> Challenge page
    "img_b":    "image_b.png",     # interior hero #2  (e.g. whole-site)   -> Solution page
    "img_c":    "image_c.png",     # interior hero #3  (e.g. plant room)   -> Strategic Value
    "partner_logo": "partner_logo.avif",
    "headshot": "headshot.png",
}
HERO_WIDTH = 1700      # px; heroes are full-bleed so keep them sharp
HERO_QUALITY = 82
HEADSHOT_PX = 360
# ---------------------------------------------------------------------------

def jpeg_dataurl(im, w=None, q=85):
    im = im.convert("RGB")
    if w and im.width > w:
        im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=q, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()

def strip_to_transparent(im, thresh=28):
    """Knock a near-black OR near-white flat background out to transparent."""
    im = im.convert("RGBA"); px = im.load(); w, h = im.size
    # sample the corners to decide which flat colour to remove
    corners = [px[0,0], px[w-1,0], px[0,h-1], px[w-1,h-1]]
    dark  = sum(1 for c in corners if c[0]<thresh and c[1]<thresh and c[2]<thresh)
    light = sum(1 for c in corners if c[0]>255-thresh and c[1]>255-thresh and c[2]>255-thresh)
    if dark >= light and dark >= 2:
        for y in range(h):
            for x in range(w):
                r,g,b,a = px[x,y]
                if r<thresh and g<thresh and b<thresh: px[x,y]=(0,0,0,0)
    elif light >= 2:
        for y in range(h):
            for x in range(w):
                r,g,b,a = px[x,y]
                if r>255-thresh and g>255-thresh and b>255-thresh: px[x,y]=(r,g,b,0)
    bbox = im.getbbox()
    return im.crop(bbox) if bbox else im

def png_dataurl(im):
    buf = io.BytesIO(); im.save(buf, "PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

def square_crop(im, px=360, top_bias=0.06):
    im = im.convert("RGB"); w, h = im.size; s = min(w, h)
    left = (w - s)//2
    top = max(0, (h - s)//2 - int(h*top_bias))   # bias up toward the face
    return im.crop((left, top, left+s, top+s)).resize((px, px), Image.LANCZOS)

out = {}
for key in ("img_hero","img_a","img_b","img_c"):
    p = PATHS.get(key)
    if p:
        try:
            out[key] = jpeg_dataurl(Image.open(p), HERO_WIDTH, HERO_QUALITY)
            print(f"{key}: ok  ({round(len(out[key])/1024)} KB)")
        except Exception as e:
            print(f"{key}: SKIP ({e})")

if PATHS.get("partner_logo"):
    try:
        lg = strip_to_transparent(Image.open(PATHS["partner_logo"]))
        out["partner_logo"] = png_dataurl(lg)
        print(f"partner_logo: ok  ({round(len(out['partner_logo'])/1024)} KB)")
    except Exception as e:
        print(f"partner_logo: SKIP ({e})")

if PATHS.get("headshot"):
    try:
        out["headshot"] = jpeg_dataurl(square_crop(Image.open(PATHS["headshot"]), HEADSHOT_PX), None, 86)
        print(f"headshot: ok  ({round(len(out['headshot'])/1024)} KB)")
    except Exception as e:
        print(f"headshot: SKIP ({e})")

json.dump(out, open("imgs.json","w"))
print("wrote imgs.json with keys:", list(out))
