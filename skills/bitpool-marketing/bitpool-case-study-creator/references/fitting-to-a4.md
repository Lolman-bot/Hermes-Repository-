# Fitting every page to A4

The format lives or dies on this: **each `.page` must measure 1123px** at the QA
viewport (900px wide, device-scale 2). `qa.py` prints the five heights and flags any
page over 1126px. A page that's even ~30px over will push content onto a 6th print
page, so always close the gap.

## Why a page overflows
Almost always the image-heavy pages (2, 3) or the content-dense page (5). New copy
that runs a line longer, a bigger ring, or a taller hero ratio is the usual cause.

## The knobs (use in this order, smallest visual cost first)
1. **Hero ratio** — drop `--ratio` by 2–4 points on the offending page's
   `.feature.bleed` (e.g. 64% → 60%). Biggest, cleanest lever on pages 2–3.
2. **Section top margins** — the inline `margin-top` on `.sec` blocks (9mm → 5–6mm),
   and `margin-top:auto` already pins heroes to the bottom.
3. **`.sec-intro` margin-bottom** (5mm → 4mm).
4. **Page 5 specifics** — `.sv-band` `min-height`, `.bullets` `gap` (10→8),
   `.sv-text` padding, `.quote` `padding` + `line-height`, `.cta-row` margins.
5. **Page 4 specifics** — `.perf` padding, `.ring` size (148px), `.beat` `min-height`.

Avoid shrinking body font below the set sizes; reach for margins and ratios first.

## Reference heights from the canonical build
All five pages land at **1123** with these settings:
- P1 hero `--ratio:48%`; P2 hero `62%`; P3 hero `64%`.
- P4 ring 148px, `.perf` padding `22px 20px 18px`, `.beat` `min-height:108px`.
- P5 `.sv-band min-height:258px`, bullets `gap:8px`, quote `font 14 / line-height 1.5`.
(Page 5 may read 1128 — within rounding tolerance.)

## Print correctness
`qa.py` generates the PDF with `beforeprint` dispatched, which forces every count-up,
ring, bar and reveal to its final state and hides the toolbar. Always eyeball the
rasterised `pdf-*.png` — the classic regression is an animated element that rests
invisible and is missing from the PDF. Every animated class in this skill already has
a print-CSS / beforeprint override; if you add a new one, give it the same.
