# Case Studies

A Bitpool customer case study is a single self-contained HTML file in the exact format and behaviour of the canonical Bitpool × BAC data-centre story: five A4 portrait pages, full-bleed hero renders, a visual Outcome dashboard with percentage rings, and built-in pixel-perfect PDF export.

> **Note**
> The template, the image pipeline and the QA scripts ship locally with the `bitpool-case-study-creator` skill (`assets/case-study-template.html`, `logo-b64.txt`, `prep-images.py`, `build.py`, `qa.py`, and `references/example-bac-case-study.html`). This page is the method; those files are the machinery. Never hand-roll new case-study HTML — start from the template.


## When to use it

A **case study, customer story, success story, reference story, partner or client win write-up**, or "a case study like the BAC one" — even a casual "make a case study about X", or the user handing over a project, a partner quote and some renders.

For slide decks use Presentations (see the `/bitpool-presentation-creator` skill); for a priced offer use Proposals (see the `/bitpool-proposal-creator` skill). Load the `bitpool-design-system` skill for brand tokens and `bitpool-brand-guidelines` for voice.

## Non-negotiables — the "exact format"

1. **Single self-contained HTML file.** No external assets except Google Fonts (Inter + JetBrains Mono). The cube logo, partner logo, headshot and all renders are embedded as data URLs.
2. **Five fixed A4 pages** in order — Cover, Challenge, Solution, Outcome dashboard, Strategic Value + Partner. Every page measures one A4 (1123px at the QA viewport); content never overflows onto a sixth page. See [Page archetypes](page-archetypes.md).
3. **Light Bitpool theme** — white paper, near-black ink, **bold cyan `#00ADEF` replaces italics**, Inter only, hairline borders, the cube logo in every header, footer and the favicon.
4. **Full-bleed cinematic heroes** with strong-scrim captions; a full-page visual Outcome dashboard (3 percentage rings + 4 impact tiles + closing beat); a transparent partner logo in the header chip, testimonial and "Delivered with"; a circular headshot in the byline. See [Image system](image-system.md).
5. **Animation + print system** — scroll-triggered `.rv` reveals, `data-count` count-ups, `data-pct` ring draws, all forced to final state on print via a `beforeprint` handler; toolbar hidden; one A4 per page.

## Workflow


## Load brand context

Read `bitpool-design-system` (tokens, the six non-negotiables) and `bitpool-brand-guidelines` (voice, the bold-cyan rule, banned clichés). Skim [Page archetypes](page-archetypes.md) and [Image system](image-system.md).


## Pull current product detail — always

Fetch `https://www.bitpool.com/product` and read [Product source](product-source.md). Ground the Solution items and Strategic-Value points in the platform's *current* capabilities and language, and source the Outcome dashboard and Solution infographics from the page's infographic concepts — rebuilt in the light theme, never screenshotted. Never describe a capability the platform lacks or invent a product name. If the fetch fails, fall back to the snapshot in [Product source](product-source.md) and flag it on delivery.


## Gather assets and content

Client, sector, location; a headline and lead; ~4 challenges; ~4 solution items; outcome metrics (flagging which are *real* numbers vs qualitative); ~5 strategic-value points; a partner quote plus contact name and role; the partner/client logo; a contact headshot; and 2–4 renders (exterior + interiors). If real outcome percentages aren't available, ask — never invent performance claims.


## Copy the template

`cp assets/case-study-template.html ./<client>-case-study.html`


## Fill the content

Edit every `[BRACKETED]` region directly in the copied file — title, eyebrow, lead, stat cells, meta row, challenge cards, solution items, the three rings (set `data-pct` *and* `data-count` to the same real value plus label), impact tiles, strategic bullets, quote and byline, captions, closing line.


## Prep images

Edit the `PATHS` in `assets/prep-images.py` and run it to produce `imgs.json` — heroes to JPEG, partner logo to a background-stripped transparent PNG, headshot to a square JPEG.


## Build

`python3 assets/build.py <client>-case-study.html imgs.json out.html` injects the cube logo and all data URLs. It warns if any `[placeholder]` is unfilled.


## QA — mandatory

`python3 assets/qa.py out.html`. Confirm all five page heights are ~1123 (≤1126) and JS errors are none; eyeball `page*.png` and the rasterised `pdf-*.png`. Fix any overflow with the knobs in [Fitting to A4](fitting-to-a4.md) and re-run. Never ship a case study where a page overflows or the PDF differs from the screen.


## Deliver

The single `out.html` to the outputs directory. Default filename: `<client>-bitpool-case-study.html`.

## Content rules (voice)

- Boldly practical, unapologetically real. State outcomes, don't sell them.
- Short declarative titles; numbers over adjectives; two-tier sentences.
- Cyan `<strong>` emphasis on ~1–2 phrases per block — never italics, never a second accent colour.
- **Performance percentages are claims.** Only publish measured, client-approved figures; otherwise use a qualitative tile or a plain metric.

## Anti-patterns

- Hand-rolling new HTML instead of starting from the template.
- Describing capabilities from memory instead of fetching bitpool.com/product — stale or invented features, or wrong product names.
- Pasting website screenshots as infographics — rebuild them in the light theme and embed as data URLs.
- Presenting the product page's illustrative "real results" numbers as the client's measured outcomes.
- A dark fill behind a transparent partner logo (reads as a black box) — the header chip is transparent plus hairline.
- Letterboxed thin hero strips — interior renders are full-bleed and tall.
- Invented performance percentages presented as measured results.
- Letting a page overflow A4 to fit more copy — split or trim, then re-QA.
- Italics, a second accent colour, or dropping the cube logo.
