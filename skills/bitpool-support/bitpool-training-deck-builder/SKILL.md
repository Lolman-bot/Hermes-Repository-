---
name: bitpool-training-deck-builder
description: "Use when making a Bitpool training deck. On-brand HTML."
version: 1.1.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, training, slides, deck, html, presentation]
    category: bitpool
    related_skills: [bitpool-design-system, bitpool-brand-guidelines, powerpoint, docx, pdf]
---

# Bitpool Training Deck Builder

Turns a person's raw training material — PowerPoint, Word, PDF, notes, screenshots or screen recordings — into one self-contained HTML slide deck in the Bitpool brand. The deck is 1920×1080 slides that fit any screen, with arrow-key and ☰ navigation, in-place **Edit**, **Save HTML** and one-slide-per-page **PDF**, and screenshots with numbered pins that can be dragged while presenting. Content slides are broken up by animated visual slides and dark slides, the way `assets/example-deck.html` is. It's ready to present to staff or customers.

## When to Use

- The user types `/bitpool-training-deck-builder`.
- They ask for a training deck or training slides — "make a training deck on X", "build slides to train staff/customers on X", "I need a presentation for a training session".

Don't use for:
- Pitch, partner, sales or board decks — this skill is for training only.
- A `.pptx` file as the output: use `/powerpoint`.
- Turning a deck into an interactive click-through lesson.

## Procedure

1. **Ask the three basics.** Deck title, who it's for (staff or customers), and the top-corner label, all in one message. `references/intake.md`. Done when all three are answered.
2. **Read everything already given.** PowerPoint, Word, PDF, pasted notes, images, screen recordings: read all of it in full (the `powerpoint`, `docx` and `pdf` skills via `skill_view`; images with `vision_analyze`), then say back what you found. `references/intake.md`. Done when the say-back is sent.
3. **If anything is missing, ask for only that.** Missing means a section with no content, a "click X" step with no screenshot, an image with no home, or a fact you'd have to invent. Ask for all gaps in one message. Never ask for videos. If nothing is missing, carry on. Done when there are no gaps left.
4. **Plan the outline.** Give each slide one of the 28 layouts, put a visual layout or a dark slide every three or four slides, and suggest extra slides where they'd help ("Why" slides, section dividers, split slides, a closing slide), each marked `[NEW]`. `references/slide-layouts.md`. Done when the outline is shown.
5. **If the outline isn't approved, change it and show it again.** Loop on step 4 until they approve it, including which `[NEW]` slides to keep. Done when they approve.
6. **Build the deck.** Load `/bitpool-design-system` first. Copy `assets/deck-template.html` with `terminal` (`cp`), then fill it slide by slide from the template's layouts (`patch` / `write_file` on slide sections only), and compare it with `assets/example-deck.html`. For extra motion, borrow layouts from `assets/example-animation-library.html` (`references/animation-library.md`). `references/build-check-review.md`. Done when every approved slide exists.
7. **Place the pins and boxes on screenshots.** One cyan box and one numbered pin per step, checked in the browser. `references/screenshot-pins.md`. Done when every box sits on its control in a `browser_vision` check.
8. **Check every slide.** Nothing overflows at laptop size, every image and video shows, and the counter and navigator are right. Fix and recheck. `references/build-check-review.md`. Done when every check there passes.
9. **Show it for review.** If they want changes, make them and go back to step 8. Loop until they're happy. Done when they say it's done.
10. **Hand over the finished deck.** Run `python <skill-dir>/scripts/embed_media.py <deck>-draft.html <deck>.html` to build the single self-contained `.html`, then give it to them (path, or `MEDIA:/absolute/path/<deck>.html` on a messaging platform) with its size and a one-line reminder of the controls. Done when the file is delivered.

## Load-bearing rules

1. **Every deck starts from `assets/deck-template.html`, and its style and scripts are never rewritten.** That's where navigation, Edit, Save HTML, PDF, the reveal animation, the visual slides' motion, the pins and the fix for small screens live. A hand-rolled deck loses them silently. `assets/example-deck.html` is the look to match, never a starting file.
2. **Bitpool design system, always.** Inter, cyan `#00ADEF`, the cube logo on every slide, and cyan `<strong>` for emphasis, never italics or inline colour spans. Load `/bitpool-design-system` before writing slides. This is what makes the deck look professional and the same as every other Bitpool deck.
3. **Ask once, and only for what's missing.** Read what was given before asking anything, and never ask for videos. Asking for things the person already handed over is the fastest way to lose them.
4. **Suggested slides are suggestions.** Mark them `[NEW]` in the outline and never present an invented claim, figure, name or price as fact. Training decks get presented as true.
5. **Nothing is built until the outline is approved, and nothing is handed over until the person has reviewed the deck.** They have to stand up and present it.
6. **Every slide fits and every image shows, checked at laptop size.** Overflowing text or a broken image is the first thing an audience notices. If it doesn't fit, split the slide; never shrink the type.
7. **Customer decks show no internal or customer data.** Check every screenshot for names, chat histories, emails and other customers' data, and offer to blur or crop before it goes in.
8. **Visual layouts keep their item count, and their sample copy never ships.** Their lines and chips are drawn for exactly that many items; a different count means a content layout instead. Every word of the sample copy from the example deck gets replaced.

## Pitfalls

- **Treating the example deck as content.** `assets/example-deck.html` is a finished Bitpool deck about an older AI-tools course ("Learn Claude at Bitpool"). It is a style reference for rhythm and look only; none of its topic, wording or claims belong in a new deck.
- **Leftover sample copy.** The template's visual slides carry that example's words ("Learn Claude", "Bitpool AI Training", "Point one", "Card title"); search the draft for them before review.
- **Retyping the template.** `assets/deck-template.html` is ~270 KB with the logo, Inter and scripts embedded. Copy it with `cp`; never regenerate it through `write_file`.
- **Checking only at 1920×1080.** Overflow shows at laptop size (1440×810).
- **Judging motion in a headless browser.** Turn on **Edit** to see visual slides in their finished state; a mid-animation slide can look empty.
- **Serving to a cloud browser.** A cloud browser backend can't reach `localhost`; use the local browser for checks.

## Verification

- The deck began as a copy of `assets/deck-template.html`; its `<style>` and `<script>` blocks are unchanged.
- The overflow check returns an empty list at 1440×810; no image has `naturalWidth` 0; every video has `readyState > 0`.
- The counter total and ☰ list match the approved outline.
- No sample copy from the template or example deck remains.
- `embed_media.py` ran without "Missing media files" and the final `.html` was delivered after the person's review.

## Reference files

Read the file itself — this table is an index, not a substitute.

| File | Covers |
|---|---|
| `references/intake.md` | The three opening questions, how to read each input type (pptx, docx, pdf, notes, images, video), the `media/` folder, what counts as missing, and screenshot privacy. |
| `references/slide-layouts.md` | The twelve content and sixteen visual layouts with when to use each and their limits, rhythm, dark slides and the photo cover, mapping input slides to layouts, the suggested extra slides, the outline format, and slide-copy rules. |
| `references/screenshot-pins.md` | The box-and-pin markup, percent coordinates, unique `data-k` keys, and checking positions in the browser. |
| `references/animation-library.md` | The 50 extra animated layouts in `assets/example-animation-library.html`: what each one's motion is, what it suits, its fixed item count, and how to copy a slide plus its CSS into a draft without touching the template's own style. |
| `references/build-check-review.md` | Filling the template, adding video, comparing with the example, the overflow, broken-image and sample-copy checks, the review loop, and the final embed and hand-over. |

Assets (copied, never retyped from memory):

| File | What it is |
|---|---|
| `assets/deck-template.html` | The working deck shell: the full style, navigation, Edit, Save HTML, PDF, reveal and pin scripts, with the cube logo and Inter built in, the dark-slide (`.dk`) and photo-cover styles, and one slide for each of the 28 layouts (`<!-- LAYOUT: name -->`). Copied as the start of every deck. |
| `assets/example-deck.html` | A finished Bitpool training deck (an older AI-tools course), screenshots swapped for placeholders. Style reference for look and rhythm only; never copied as a starting file and never a content source. |
| `assets/example-animation-library.html` | A finished 50-slide sample deck ("Buildings that run themselves") where every slide has a different animation, with image placeholders. A library of extra visual layouts to borrow from; never copied as a starting file and never a content source. |
| `assets/cube-mark.png` | The Bitpool cube logo used in the template, kept separately for anywhere else a slide needs it. |

Scripts (executed, not described):

| File | What it does |
|---|---|
| `scripts/embed_media.py` | `python embed_media.py <draft.html> <final.html>`. Inlines every local image and video the draft points at as base64 so the deck is one file. Stops and writes nothing if any file is missing. |

### Editing this skill

The look comes from the template's style block and from `bitpool-design-system`. If the brand changes, update the design system skill first, then bring `assets/deck-template.html` in line in the same pass. Layout limits and copy rules live in `references/slide-layouts.md`. Add a new layout by adding a `<!-- LAYOUT: name -->` section to the template and a row to that table together. Visual layouts' CSS is scoped by an `l-<name>` class; keep new ones scoped the same way. If a newer deck becomes the house example, replace `assets/example-deck.html` with its images swapped for placeholders.
