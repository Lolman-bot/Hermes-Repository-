---
name: bitpool-case-study-creator
description: "Use when making a Bitpool customer case study. A4 HTML."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, marketing, case-study, html, pdf, print]
    category: bitpool
    related_skills: [bitpool-brand-guidelines, bitpool-design-system, bitpool-presentation-creator, bitpool-proposal-creator]
---

# Bitpool Case Study Creator

Produces a customer case study in the exact format and behaviour of the canonical Bitpool × BAC data-centre case study: a single self-contained HTML file, five A4 portrait pages, full-bleed hero renders, a visual Outcome dashboard with percentage rings, and built-in pixel-perfect PDF export.

The method ships with this skill in `references/`; the template and scripts live in `assets/`. Light Bitpool theme, count-up stats, animated SVG percentage rings, a partner-logo header chip, a headshot testimonial, and one-click Save-as-PDF that prints one A4 per page.

## When to Use

- The user wants a Bitpool case study, customer story, success story, reference story, or a partner/client win write-up.
- They ask for "a case study like the BAC one", or to turn project notes, outcomes and photos into a print-ready customer story.
- The five-page format is fixed: Cover, The Challenge, The Solution, a full-page visual Outcome dashboard, and Strategic Value plus Partner Perspective.

Don't use for:
- Slide decks or pitch presentations: use `/bitpool-presentation-creator`.
- Sales proposals or quotes with pricing: use `/bitpool-proposal-creator`.
- Marketing emails: use `/draft-marketing-email`.
- Pure copywriting with no document artefact: use `/bitpool-brand-guidelines`.

## Prerequisites

- Hermes `terminal`, `read_file`, `write_file` and `patch` tools (the build is real files on disk).
- Python 3 with Pillow (`prep-images.py`; `pillow-avif-plugin` for `.avif` inputs) and Playwright Chromium (`pip install playwright && playwright install chromium`) for `qa.py`. `pdftoppm` (poppler) rasterises the PDF check.
- `/bitpool-design-system` and `/bitpool-brand-guidelines` installed — load both with `skill_view` alongside this skill.

## Procedure

1. **Read the method.** `read_file` `references/case-study-workflow.md` in full, then `references/page-archetypes.md` and `references/image-system.md` for any real build. Read the whole file you reach for — skimming for the line you expect is how a threshold or a flag gets missed. Done when all three have been read this run.
2. **Load brand context.** `skill_view` `bitpool-design-system` and `bitpool-brand-guidelines`. Done when both are loaded.
3. **Pull current product detail — always.** `web_extract` `https://www.bitpool.com/product` for live capabilities and infographic concepts; fall back to `references/product-source.md` only if the site can't be read (say so). Done when the Solution and Strategic Value content is grounded in one of the two.
4. **Gather assets and content.** Client and partner names, hero renders, partner logo, headshot, testimonial, and the *measured, client-approved* outcome figures. Ask for anything missing in one batch (`clarify` for choices). Done when every page region has a real source — no invented numbers.
5. **Copy the template** `assets/case-study-template.html` to `<client>-case-study.html` with `terminal` (`cp`). Never hand-roll case-study HTML. Done when the copy exists and is untouched.
6. **Fill the content.** `patch` every `[BRACKETED]` region per `references/case-study-workflow.md` and `references/page-archetypes.md`. Leave the `__IMG_*__`, `__LOGO__`, `__PARTNER_LOGO__`, `__HEADSHOT__` tokens for the build. Done when no `[bracketed]` region remains except tokens.
7. **Prep images.** Edit `PATHS` in a working copy of `assets/prep-images.py` and run it to produce `imgs.json` (`references/image-system.md`). Done when `imgs.json` exists with every token key.
8. **Build.** `python3 assets/build.py <client>-case-study.html imgs.json out.html` (use `python` on Windows). It warns on any unfilled `[placeholder]`. Done when it runs with no placeholder warnings.
9. **QA — mandatory.** `python3 assets/qa.py out.html`. Done when all five page heights are ~1123 (≤1126), there are no JS errors, and `page*.png` / `pdf-*.png` (check with `vision_analyze`) match. Fix overflow with `references/fitting-to-a4.md` and re-run.
10. **Deliver** `out.html` (and the PDF if asked) with a one-line summary of each page. Done when the user has the file path.

## Load-bearing rules

Restated here because a wrong answer here ships a broken or false document.

1. **Single self-contained HTML file**, five fixed A4 pages in order — Cover, Challenge, Solution, Outcome dashboard, Strategic Value + Partner. Never a sixth page.
2. **Performance percentages are claims.** Only publish measured, client-approved figures. If real outcome numbers aren't available, ask — never invent a performance claim, and never present the product page's illustrative "real results" numbers as the client's measured outcomes.
3. **Never describe a capability the platform lacks or invent a product name** — ground the Solution and Strategic Value sections in the live product page.
4. **QA is mandatory.** `python3 assets/qa.py out.html` — all five page heights ~1123 (≤1126), no JS errors, and the PDF matching the screen. Never ship a page that overflows.
5. **Light theme, bold cyan `#00ADEF` replaces italics**, Inter only, cube logo in every header, footer and the favicon. Load `/bitpool-design-system` and `/bitpool-brand-guidelines` alongside this skill.
6. **Copy these files; never reconstruct them from prose.** `assets/logo-b64.txt` is the cube logo data URL — never edit it.

## Pitfalls

- **Inventing a page structure, ring value or product capability from memory.** If it isn't in the reference or the live product page, ask again for that section.
- **Shrinking fonts to fit.** Use the tighten-to-1123px knobs in `references/fitting-to-a4.md`, not ad-hoc font-size cuts.
- **Illustrative numbers.** The product page's "real results" figures are marketing examples, not this client's outcomes.
- **Windows paths in `qa.py`.** It builds a `file://` URL from the resolved path; if Chromium can't open it on native Windows, run the script under WSL.
- **Missing poppler.** Without `pdftoppm` the PDF rasterisation step fails — install poppler rather than skipping the PDF check.

## Verification

- `out.html` is one file, five pages, no external assets beyond Google Fonts.
- `qa.py` reported five heights ≤1126 and zero JS errors; the screenshots and PDF rasters were looked at.
- Every outcome percentage traces to a user-supplied, client-approved figure.
- `build.py` reported no unfilled placeholders.

## Reference files

Read the file itself — the table is an index, not a substitute.

| File | Covers |
|---|---|
| `references/case-study-workflow.md` | The full case-study workflow — non-negotiables, the nine build steps, voice rules and anti-patterns for a print-ready five-page Bitpool customer story. |
| `references/fitting-to-a4.md` | The tighten-to-1123px workflow and the exact knobs for making a case-study page fit one A4. |
| `references/image-system.md` | Heroes, captions, percentage rings, partner-logo and headshot handling for a Bitpool case study. |
| `references/page-archetypes.md` | The five fixed A4 pages in detail — Cover, Challenge, Solution, Outcome dashboard, and Strategic Value plus Partner Perspective. |
| `references/product-source.md` | The bitpool.com/product capability set and infographic concepts — the snapshot to fall back on when the live site can't be read. |
| `references/example-bac-case-study.html` | The canonical reference build (Bitpool × BAC). |
| `assets/case-study-template.html` | THE starting point — five pages, `[bracketed]` regions and image/logo tokens. |
| `assets/logo-b64.txt` | The cube logo data URL (do not edit). |
| `assets/prep-images.py` | Image pipeline → `imgs.json`. |
| `assets/build.py` | Token injection → final HTML. |
| `assets/qa.py` | Playwright A4-fit scan, screenshots, PDF export check. |

Workflow, archetypes, image rules and voice are edited in `references/case-study-workflow.md`; the template, scripts and reference build in `assets/` and `references/`.
