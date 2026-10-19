# Slide Pattern Library

Every archetype from the canonical Bitpool partner pitch deck. The first 8 live as working slides inside `assets/deck-template.html`; the more complex diagram slides are saved verbatim as `example-*.html` files in this folder — read them when building that slide type, they contain the exact SVG/markup to adapt.

Composition rules that apply to all:
- One idea per slide. Title states the takeaway, not the topic ("Reports that build themselves." not "Reporting features").
- Bold cyan `<strong>` for emphasis — never italics, never more than ~2 emphasised phrases per block.
- Reveal order: eyebrow → title (`d1`) → lede (`d2`) → content groups (`d3+`).
- Numbers do the persuading: prefer a `data-count` stat over an adjective.

---

## 1. Cover (template slide 1)
Patterned beat background, eyebrow meta line, giant two-line title with cyan second phrase, one-sentence lede, pulse-dot tag line. No page furniture beyond the lockup.

## 2. Statement / shift (template slide 2)
A single oversized claim (`.title` or `.giant`) with supporting lede. Use between sections to land one message. Lots of whitespace is the point — don't fill it.

## 3. Stat row (template slide 3, also `example-stats-slide.html`)
Title + 3-column `.cols` of `.stat` blocks: huge `data-count` value, `.bar-track/.bar-fill` with `--w`, bold label, one-sentence `.sub`. The bar width should visually match the number where possible.

## 4. Step flow (template slide 4)
Numbered circles joined by a dashed line (`.flow-dash` + travelling `.flow-dot`), with a card per step beneath (kicker `01 · SEE` style, title, 2-line description). Used for SKAG / how-it-works sequences.

## 5. Two-column feature + framed visual (template slide 5)
Left: title, lede, numbered `.feature-li` list (01/02/03 with `.n` markers and hairline separators). Right: a `.frame` browser-chrome card (`.frame-bar` with three dots + window title) containing a product mock — quality ring (`.qring`), mini bars, composition strip, audit footer. This is the workhorse layout for product capability slides.

## 6. Section divider (template slide 6)
`beat-bg` + `beat-overlay`, centred `s-pad`, eyebrow, `.giant` title (~6.6rem) with cyan strong phrase, lede. Place one at every chapter boundary: Why / How / Product / Roadmap / Market / Partners / Proof / Close.

## 7. Axiom grid + feature cards (template slide 7)
Row of 4 `.axiom` cards (kicker / h3 / short p with one strong phrase) over a row of 3 bordered `.feature-li` cards. Value-proposition slides.

## 8. Closing (template slide 8)
Mirror of the cover: beat background, giant sign-off line, contact/CTA. Footer carries the tagline ("The platform you never have to log in to.").

---

## Advanced diagram slides — read the example file before building

### SVG flow / hub diagram — `example-svg-flow-diagram.html`
Source chips (providers/connectors/subsystems) on the left, curved `.draw` paths converging into a central cube node, outcome list on the right, travelling dots via `<animateMotion><mpath/></animateMotion>`. **The cube in the SVG is an absolutely-positioned `.brand-mark` overlay div — not a second base64 embed.** Certification chips along the bottom.

### Roadmap quarter timeline — `example-roadmap-timeline.html`
Horizontal timeline with quarter nodes (Q1–Q4), `.draw` connecting line, `.pop` markers, feature stacks per quarter with staggered `.rv` delays.

### Strategic quadrant map — `example-quadrant-map.html`
2×2 grid SVG: axis labels on all four sides (letterspaced, rotated on verticals), tinted "sweet spot" quadrant, grey `.pop` competitor dots with cluster labels, pulsing cyan Bitpool dot (halo circle + core). Legend list on the right with one-line definitions per quadrant.

### Case study stat slide — `example-case-study.html`
Client eyebrow, outcome-led title, big stat row (`data-count` values with units as `<strong>`), one-paragraph narrative, footnote credentials (e.g. NIST + ISO27001). One client per slide.

### Carbon/bar chart (in two-col frame variant)
`.chart-bar` rects on a y=240 baseline with `data-h` heights, grey for history + cyan for the highlight year, axis labels beneath. Lives inside a `.frame` card on a reporting slide.

### Data table slide
Hairline-bordered table, letterspaced uppercase header row, mono numerals, cyan highlight on the key column/row. Keep to ≤6 rows on screen — split otherwise.
