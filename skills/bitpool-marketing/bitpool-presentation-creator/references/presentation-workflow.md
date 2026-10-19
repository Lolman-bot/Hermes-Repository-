# Presentations

A Bitpool presentation is a single self-contained HTML file in the exact format and functionality of the canonical partner pitch deck (V3, June 2026): fixed 1920×1080 slides in an auto-fitting viewer, scroll-triggered animations, keyboard navigation, and built-in pixel-perfect PDF export.

> **Note**
> `assets/deck-template.html` and the verbatim `references/example-*.html` complex slides ship locally with the `bitpool-presentation-creator` skill. This page is the method; those files are the machinery. Never rebuild the viewer, animation or print systems — extend the template.
>
> For PPTX files use the `pptx` skill instead. This is the interactive HTML deck format.


## Non-negotiables — the "exact format"

1. **Single self-contained HTML file.** No external assets except Google Fonts (Inter). Logo embedded once as the `--logo` CSS variable.
2. **Fixed 1920×1080 slides** scaled by the viewer to fit the user's screen — both width *and* height. Content must never overflow a slide; the slide never scrolls internally.
3. **Light Bitpool theme.** White paper, near-black ink, **bold cyan `#00ADEF` replaces italics**, Inter only, hairline rules, patterned beat backgrounds on dividers. Load `bitpool-design-system` for brand tokens and `bitpool-brand-guidelines` for voice when writing slide copy.
4. **The viewer chrome** — topbar with lockup, deck meta, Prev/Next plus counter, zoom −/+, Fit, and the cyan **PDF ↓** button. Progress bar under the topbar. Arrow-key navigation snapping one slide per screen. The ☰ navigator pane and every slide carry **drag-to-reorder, a padlock and a delete button with undo**, plus a topbar **Save** that overwrites the deck file in place.
5. **The animation system** — `.rv`/`.d1–.d6` staggered reveals, `data-count` count-ups, `.bar-fill` bars, `.qring` rings, `.chart-bar` charts, `.draw`/`.pop`/`.flow-dot` SVG diagrams, all triggered per-slide by IntersectionObserver.
6. **Editing the running order must stay truthful.** Slides can be drag-reordered, pinned to a position with a padlock, or deleted (with undo) from the navigator or the slide itself. Every one of those paths ends in `renumberDeck()`, which reassigns `id="sN"`, `.pageno`, the thumbnail labels **and `TOTAL`** — so `TOTAL` is `let`, never `const`. Skip the renumber and the failure is silent: navigation lands on the wrong slide and the deck lies about its own page numbers. Locked slides can be neither moved nor deleted; deleted slides go on an undo stack, never discarded. Save must scrub the navigator, the on-slide controls and all animation end-states from what it writes, and rewrite the `TOTAL` literal. Full contract: [Systems](systems.md) §4.
7. **PDF export that is actually perfect** — one slide per page at native 1920×1080, all animations forced to final state, viewer chrome hidden, travelling dots hidden, full colour. Never ship a deck where the PDF differs from the screen.

## Workflow


## Start from the template

Copy `assets/deck-template.html` to the working directory. It is a complete, working 8-slide deck containing every core system — viewer, animations, print CSS, PDF button, embedded logo.


## Plan the slide run

Standard arc: Cover → problem/shift statements → stat slides → how-it-works → capability slides (two-col + frame) → section dividers between chapters → roadmap/market/proof as needed → closing. Read [Slide patterns](slide-patterns.md) for the full archetype catalogue and composition rules.


## Build slides by adapting archetypes

The template holds 8 archetypes in place. Complex diagram slides — SVG flow hub, quadrant map, roadmap timeline, case study, charts — are saved verbatim in the skill's `references/example-*.html`. Copy and adapt rather than inventing markup.


## Wire the mechanics

Renumber `id="sN"` and `.pageno` sequentially and set `let TOTAL = N;`. Update the topbar meta text. Full checklist and class contracts: [Systems](systems.md).


## QA with Playwright Chromium — mandatory

Three checks (scripts in [Systems](systems.md) §7): a per-slide overflow scan (zero elements past slide bounds), screen-fit at 1440×900 and 1920×1080 (zero page errors), and a real PDF generation (`page.pdf` at 1920×1080) with `pdftoppm` visual inspection of sample pages.

The classic regression: a new animation class that rests invisible and is missing from the PDF. Every such class needs a print-CSS final-state override.


## Deliver

The single HTML file to the outputs directory. Default filename pattern: `bitpool-<topic>-deck.html`.

## Content rules

- Slide copy follows Bitpool voice: boldly practical, short declarative titles that state the takeaway, numbers over adjectives, two-tier sentences ("Scale the platform. Scale the business.").
- Cyan `<strong>` emphasis: max ~2 phrases per text block.
- One idea per slide; split rather than shrink. If content needs a font-size reduction to fit, it's two slides.
- Page numbers two-digit, chapter eyebrow top-right of every content slide, divider slide at every chapter boundary.
