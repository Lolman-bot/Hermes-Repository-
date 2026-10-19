# Page archetypes

A Bitpool case study is **five fixed A4 portrait pages**, in this exact order. Each
page is a `<section class="page">` with the cyan top rule, a `.doc-head` (cube
lockup left, "Case Study" tag + partner-logo chip right), a faint masked grid, and
a `.doc-foot` (cube + "Bitpool · Case Study" left, "bitpool.com  NN / 05" right).

The rhythm is **solid section → full-bleed image hero → solid section → image hero →
visual dashboard → closing**. Images are the stars: "a picture says a thousand words."

## Page 1 — Cover
- Eyebrow (sector / location), oversized `.hero-title` (weight 200, **bold-cyan** on
  1–2 phrases), `.lead` (3–4 sentences).
- **Full-bleed hero** (`.feature.bleed`, `--ratio:48%`) — the establishing/exterior shot.
- `.hstats` — four headline numbers (count-up). Use real, defensible figures.
- `.metarow` — Client / Sector / Delivered with (partner logo + location) / Platform.

## Page 2 — The Challenge  +  interior hero A
- `01 The Challenge`, intro, **four** `.card`s (icon → title → one sentence).
- **Full-bleed hero** (`.feature.bleed`, `--ratio:62%`, `margin-top:auto`) anchored to
  the page bottom — typically the most infrastructural render (e.g. server hall).

## Page 3 — The Solution  +  interior hero B
- `02 The Solution`, intro, **four** numbered `.sol-item`s in a 2-col grid.
- **Full-bleed hero** (`.feature.bleed`, `--ratio:64%`, `margin-top:auto`) — the
  "system / digital-twin / whole-site" render.

## Page 4 — The Outcome (full-page visual dashboard)
This page is deliberately the most visual. It fills the **entire** page:
- Stacked section head `03 The Outcome` + headline + one-line intro.
- `.perf-row` — **three** performance tiles, each a `.perf` with an animated SVG
  **percentage ring** (`data-pct` on `.prg`, `data-count` on `.num`), a mono label,
  a title and one sentence. Use for enhancement metrics (faster resolution, PUE
  headroom, % within tolerance, uptime, energy saved …).
- `.impact-row` — **four** `.impact` tiles mixing big metrics (count-up `.big` with a
  cyan `.u` unit) and one qualitative `.impact.q` tile (icon + title + copy, no number).
- `.beat.bleed` — full-bleed patterned closing strip with a single **bold-cyan**
  payoff line.
- **Ring percentages are claims. Only use real, client-approved figures.** If a number
  isn't measured, make that tile a qualitative `.impact.q` or a plain metric instead.

## Page 5 — Strategic Value  +  Partner Perspective
- `.sv-band` — image left (`--img` photo, e.g. plant room) with a 105° fade into a
  right panel holding `04 Strategic Value` (cyan h2) and **five** diamond `.bullets`.
- `05 Partner Perspective` — navy `.quote` block (cyan glow, partner logo top-right
  via `.quote-bac`, big quote, byline with **headshot avatar** + name + org·location).
- `.cta-row` — "Want to know more? **Let's talk.**" + cyan "Talk to us →" button.

## Adapting the count
Four challenge cards / four solution items / five outcome tiles / five bullets is the
canonical balance and it fits A4. If a client genuinely needs 3 or 5 of something,
adjust the grid `grid-template-columns` and re-run `qa.py` — never let a page overflow.
