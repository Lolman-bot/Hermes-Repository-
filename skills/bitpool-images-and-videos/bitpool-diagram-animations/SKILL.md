---
name: bitpool-diagram-animations
description: "Use when animating a diagram PNG in the Bitpool style."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, animation, diagram, html, svg, css, motion]
    category: bitpool
    related_skills: [bitpool-design-system, bitpool-3d-image, bitpool-cinematic-video, bitpool-hvac-schematics, bitpool-presentation-creator]
---

# Bitpool Diagram Animations

Takes a PNG of an ordinary diagram (flow chart, system or network diagram, process, schematic or architecture drawing) and gives back one self-contained HTML file: the same diagram, redrawn sharp as HTML and SVG on the Bitpool background, light or dark, and animated with motion from the *Buildings that run themselves* animation library. It builds in piece by piece in story order, then keeps a gentle live motion looping (data flowing, a pulse, a sweep). The file works offline, fits any window and replays on click.

Recipes, template and font ship in `assets/`, the assembler in `scripts/`, the method in `references/`.

## When to Use

- The user runs `/bitpool-diagram-animations`.
- The user hands over a PNG and asks to "animate this diagram", "make this an animation", "bring this diagram to life" or "Bitpool-ify this into an animation".

Don't use for:
- A 3D render of an image: use `/bitpool-3d-image`.
- Video prompts for Veo/Gemini: use `/bitpool-cinematic-video`.
- HVAC or plant schematics built from scratch: use `/bitpool-hvac-schematics`.
- Whole decks: use `/bitpool-presentation-creator`.

## Prerequisites

- Python 3 (stdlib only) for `scripts/assemble.py`.
- A headless Chromium-family browser (Edge or Chrome) for the screenshot checks, or the Hermes browser tools. If neither is available, say so at hand-over (rule 10).

## Procedure

1. **Get the PNG.** Ask for the file path with `clarify` if it wasn't given, and look at it with `vision_analyze`. One diagram per run; several are done one at a time. Done when you have seen the image.
2. **Ask: light or dark?** Every run, with `clarify`: light (white, grid, cyan glow) or dark (navy, cyan glow). Don't default and don't carry the last run's answer over. Done when the user has picked one this run.
3. **Read the diagram and plan the motion.** Write the inventory (every node, label, value, connection and group, plus the story order) and the motion plan (build-in order, which recipe carries which part, the live loop). Show both in one message and wait for a yes. Detail in `references/reading-the-diagram.md` and `references/motion-catalogue.md`. Done when the user has confirmed both.
4. **Redraw and animate.** With `write_file`, write `diagram.html` and `diagram.css` in a scratch folder, laid out on the 1680×852 stage, using the Bitpool parts and borrowing or adapting library recipes (find them with `search_files` in `assets/`). Detail in `references/reading-the-diagram.md` §3–5 and `references/motion-catalogue.md`. Done when both files exist and every inventory item is in the markup.
5. **Assemble.** Run `python <skill-dir>/scripts/assemble.py ...` with `terminal` to join the template, font, recipes and diagram into the single HTML file, next to the PNG as `[png name]-animation.html`. Detail in `references/build-and-check.md`. Done when the script reports `Wrote ...` with no error (and, for dark, no white-background warning).
6. **Check, fix, recheck.** Screenshot the finished and mid-build states, inspect them with `vision_analyze` against the PNG and the inventory, and fix every failure before handing over. Detail in `references/build-and-check.md`. Done when all seven checks pass (or the ones that couldn't run are named).
7. **Hand over.** The path, the theme, what moves and why, how to replay it, and anything you were unsure of. Offer one round of changes. Done when the user has the file.

## Load-bearing rules

1. **Redraw, never embed.** The PNG is a reference only. Every element is rebuilt as HTML/SVG, and the output contains no `<img>` of the original. Embedding the PNG gives a blurry animation, which is the opposite of what this skill is for.
2. **Every label exactly as written, nothing invented.** Spelling, capitals, numbers and units are copied from the diagram. Anything unreadable is asked about, not guessed. A wrong label in a polished animation is worse than no animation.
3. **The user confirms the inventory and motion plan before you build.** Misreading the diagram is the expensive mistake; one "yes" up front prevents it.
4. **Diagram only.** The output is the animated diagram on the Bitpool background: no slide heading, eyebrow, lede, logo bar or footer. The diagram's title goes in the HTML `<title>`.
5. **Light or dark is asked every run.** Both are fully supported; neither is assumed.
6. **Build in, then loop.** The build-in plays once per replay (2.5–6s, in story order); one or two calm live motions then loop forever and carry the diagram's meaning.
7. **Keep the motion contract.** An element's own style is its finished state, keyframes say where it comes from (`backwards`), and motion is gated on `.on`. This is what makes reduced-motion and print show the complete diagram, so it isn't optional.
8. **Bitpool style only.** Inter, the tokens in the template, a single cyan accent, nothing italic, bold cyan for emphasis. The original's colours, fonts and clip-art are translated, not kept.
9. **One self-contained file.** Font inlined, no external URLs, no separate CSS or JS. Built with `scripts/assemble.py` from the shipped assets, never by retyping them.
10. **Don't hand over a file you haven't checked.** Run every check in `references/build-and-check.md`. If a check couldn't be run (no headless browser, say), say which one and why.

## Pitfalls

- **Missing a label.** The most common failure, and the user notices it before the motion. On a dense PNG, look at each region in turn with `vision_analyze` before writing the inventory.
- **Hiding elements with `opacity:0` in their own style.** With motion off (reduced-motion, print) they vanish. Put the hidden state in the keyframes' `from`.
- **Retyping the assets.** The font is a base64 woff2 and the recipes are verbatim library CSS; neither survives retyping. Let `assemble.py` inline them.
- **Dark theme with white recipe surfaces.** Several recipes hard-code `#fff`; override them in `diagram.css` with `var(--bp-white)` / `var(--bp-surface-2)` until the script's warning is gone.
- **A mid-build screenshot identical to the finished one** means the `.on` gating or the `backwards` fill is wrong.
- **Hand-editing the assembled file** for changes. Edit `diagram.html` / `diagram.css` and re-run the script.
- **Overwriting an existing `-animation.html`.** Ask first, or add `-2`.

## Verification

- `assemble.py` wrote the file with no error, no unfilled `@@` marker, no external URL, and (dark) no white-background warning.
- Finished and mid-build screenshots were inspected this run: every inventory node, label, value and connection is present and spelled the same, nothing invented, no overlaps or clipping, text ≥15px, contrast holds on the chosen theme, and the mid-build shot is part-way in.
- No rule in `diagram.css` sets `opacity:0` or `display:none` outside a `@keyframes` block.
- The output contains no `<img>` of the original PNG and sits next to it as `[png name]-animation.html`.

## Reference files

Read the file itself — this table is an index, not a substitute.

| File | Covers |
|---|---|
| `references/reading-the-diagram.md` | Reading the PNG, writing the inventory the user confirms, laying the redraw out on the 1680×852 stage, translating the original's parts into Bitpool parts, and text rules. |
| `references/motion-catalogue.md` | The motion contract, the build-in-then-loop pattern, which of the 50 library recipes suits which diagram feature, how to borrow or adapt a recipe, and fixing recipes for the dark theme. |
| `references/build-and-check.md` | Running `assemble.py`, output name and place, the seven checks (with the headless screenshot commands), and what to say at hand-over. |

### Assets and scripts

Copied, never retyped from memory.

| File | What it is |
|---|---|
| `assets/animation-template.html` | The single-file shell: Bitpool light and dark tokens, the 1920×1080 stage scaled to fit, the grid-and-glow background, the motion contract, and the play/replay script, with `@@…@@` markers the assembler fills. |
| `assets/motion-recipes.css` | All 50 motion recipes from the *Buildings that run themselves* animation library, verbatim. |
| `assets/recipe-examples.html` | The markup for every recipe, verbatim. Search it for the one you need. |
| `assets/inter-font.css` | Inter (variable weight) as an embedded woff2 `@font-face`, so the output works offline. |
| `scripts/assemble.py` | Joins the template, font, chosen recipes and the diagram's markup and CSS into one HTML file. Refuses to write if a marker is left unfilled or anything would load from the network; warns about white surfaces when building dark. |

### Editing this skill

The motion recipes come from the *Buildings that run themselves · Animation library* deck. If that deck gains or changes recipes, re-copy its animation-library CSS block into `assets/motion-recipes.css` and its `m-` slides into `assets/recipe-examples.html`, then update the table in `references/motion-catalogue.md` in the same pass. Brand tokens in the template follow the Bitpool design system (`/bitpool-design-system`); change them there first. Every change bumps `version` and syncs this skill's README row.
