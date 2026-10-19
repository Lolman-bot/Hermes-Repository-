---
name: bitpool-presentation-creator
description: "Use when building a Bitpool HTML deck or slides."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, marketing, presentation, deck, slides, html, pdf]
    category: bitpool
    related_skills: [bitpool-brand-guidelines, bitpool-design-system, bitpool-case-study-creator, bitpool-proposal-creator, bitpool-training-deck-builder]
---

# Bitpool Presentation Creator

Builds presentations in the exact format and functionality of the canonical Bitpool partner pitch deck (V3, June 2026): a single self-contained HTML file with fixed 1920×1080 slides, an auto-fitting viewer, scroll-triggered animations, a running-order editor (reorder, lock, delete with undo, save in place), and built-in pixel-perfect PDF export.

The method ships with this skill in `references/`; the template lives in `assets/` and the verbatim complex example slides in `references/` (the five example slide files listed below). Never hand-roll deck HTML/CSS/JS from scratch.

## When to Use

- `/bitpool-presentation-creator`, or proactively whenever the user asks for a Bitpool presentation, deck, slides or pitch — pitch decks, partner decks, sales decks, board decks, product walkthroughs.
- Even casual asks in a Bitpool context: "make a deck about X", "turn this into a presentation", "reorder the slides", "lock that slide", "delete that slide", "save the deck".

Don't use for:
- A `.pptx` file: use the `/powerpoint` skill.
- Internal staff training decks: use `/bitpool-training-deck-builder`.
- Print case studies or proposals: use `/bitpool-case-study-creator` or `/bitpool-proposal-creator`.

## Prerequisites

- Hermes `terminal`, `read_file`, `write_file`, `patch`.
- Python 3 with Playwright Chromium (`pip install playwright && playwright install chromium`) and `pdftoppm` (poppler) for the mandatory QA.
- `/bitpool-design-system` and `/bitpool-brand-guidelines` — load both with `skill_view`.

## Procedure

1. **Read the method.** `read_file` `references/presentation-workflow.md` before planning, `references/slide-patterns.md` before choosing archetypes, and `references/systems.md` before touching any mechanic or running QA. Read each whole file. Done when all three are read this run.
2. **Load brand context.** `skill_view` `bitpool-design-system` and `bitpool-brand-guidelines`. Done when both are loaded.
3. **Start from the template.** `cp assets/deck-template.html <deck>.html` with `terminal`. Done when the copy exists — the viewer, animation, print CSS, PDF button and logo come from it, never rebuilt.
4. **Plan the slide run** in chat (slide number → archetype → one idea) and get a yes. Done when the user approves the run.
5. **Build slides by adapting archetypes** — copy-adapt the example slide files in `references/` rather than reinventing. Done when every planned slide exists with one idea each.
6. **Wire the mechanics** per `references/systems.md` (add-a-slide checklist): renumber `id="sN"` and `.pageno`, set `let TOTAL = N;`, add print-CSS final states for any new animation class. Done when the checklist is ticked for every new slide.
7. **QA with Playwright Chromium — mandatory** (scripts in `references/systems.md`): per-slide overflow scan, screen-fit at 1440×900 and 1920×1080, and a real `page.pdf` inspected with `pdftoppm` (look at the rasters with `vision_analyze`). Done when no slide overflows and the PDF matches the screen.
8. **Deliver** the HTML path with the slide list. Done when the user has it.

## Load-bearing rules

Restated here because a wrong answer here ships a broken deck.

1. **Single self-contained HTML file**, fixed **1920×1080** slides scaled by the viewer to fit both width *and* height. Content never overflows a slide; the slide never scrolls internally.
2. **QA with Playwright Chromium is mandatory** — per-slide overflow scan, screen-fit at 1440×900 and 1920×1080, and a real `page.pdf` generation inspected with `pdftoppm`. **Never ship a deck where the PDF differs from the screen.**
3. **Every new animation class needs a print-CSS final-state override.** The classic regression is a class that rests invisible and is simply missing from the PDF.
4. **Renumber `id="sN"` and `.pageno` sequentially and set `let TOTAL = N;`** whenever slides are added or reordered. `TOTAL` is `let`, never `const`.
5. **Editing the running order must stay truthful.** Reorder, lock and delete all end in `renumberDeck()`, which reassigns `id="sN"`, `.pageno`, the thumbnail labels and `TOTAL`. Skip it and the failure is silent — navigation lands on the wrong slide and the deck lies about its page numbers. Locked slides can be neither moved nor deleted; deleted slides go on an undo stack, never discarded. Save must scrub the navigator, on-slide controls and animation end-states, and rewrite the `TOTAL` literal. Contract: `references/systems.md` §4.
6. **One idea per slide; split rather than shrink.** If content needs a font-size reduction to fit, it's two slides.
7. **Light theme, bold cyan `#00ADEF` replaces italics**, Inter only. Load `/bitpool-design-system` and `/bitpool-brand-guidelines` alongside this skill.
8. **Copy these files; never reconstruct them from prose.** Never rebuild the viewer, animation or print systems — extend the template.

## Pitfalls

- **Inventing a class contract or QA step from memory** — the animation/print classes are a contract; getting one wrong silently breaks the PDF.
- **`const TOTAL`** — breaks the running-order editor's renumbering.
- **Second base64 logo embed** — the logo is embedded once as the `--logo` CSS variable; in SVG diagrams the cube is a `.brand-mark` overlay div.
- **Trusting the screen alone** — the PDF is where missing print overrides show up.

## Verification

- QA scripts ran: zero overflowing slides, fits at both viewports, PDF rasters match the screen.
- `id="sN"`, `.pageno` and `TOTAL` are sequential and consistent with the slide count.
- Every new animation class has a print final-state rule.

## Reference files

Read the file itself — the table is an index, not a substitute.

| File | Covers |
|---|---|
| `references/presentation-workflow.md` | The full deck workflow — the seven non-negotiables of the canonical partner pitch deck, the build steps, content rules, and the mandatory QA. |
| `references/slide-patterns.md` | The slide archetype catalogue and composition rules for a Bitpool HTML deck. |
| `references/systems.md` | Viewer, animation, running-order editing (reorder, lock, delete, save) and PDF contracts, the add-a-slide checklist, and the mandatory Playwright QA scripts. |
| `references/example-svg-flow-diagram.html`, `references/example-quadrant-map.html`, `references/example-roadmap-timeline.html`, `references/example-stats-slide.html`, `references/example-case-study.html` | Verbatim complex slides — copy-adapt, don't reinvent. |
| `assets/deck-template.html` | THE starting point: a complete 8-slide deck with every core system (viewer, animations, print CSS, PDF button, logo). |

Archetypes, contracts, QA procedure and content rules are edited in `references/`; the template in `assets/`.
