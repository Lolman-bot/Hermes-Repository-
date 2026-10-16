---
name: bitpool-design-system
description: "Use when building any visual or web work for Bitpool."
version: 1.0.1
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, design-system, brand, html, css, visual]
    category: bitpool
    related_skills: [bitpool-brand-guidelines, bitpool-search]
---

# Bitpool Design System

A reference and component library for building anything visual in the Bitpool brand. Everything it needs ships with it: prose rules and CSS/component code in `references/`, and the logo, starter template and living style guide in `assets/` and `references/`. Nothing is fetched at run time. The system is opinionated on purpose, so output doesn't drift into generic SaaS aesthetics that miss Bitpool's restrained, confident look.

## When to Use

- Building any web page, section, component, document, slide deck, marketing asset, internal tool or visual artefact for Bitpool: strategic plans, partner pages, landing pages, dashboards, reports, pitch material, or any HTML/CSS in the Bitpool brand.
- The user mentions "Bitpool" alongside any visual or web work.

Don't use for:
- Copy, naming or positioning with no visual output: use `/bitpool-brand-guidelines` (load both when a task has both).
- Adding a search bar or typeahead to a Bitpool page: use `/bitpool-search` together with this skill.

## Procedure

1. **Read this whole SKILL.md** before writing any HTML. The six non-negotiables below are load-bearing. Done when you can list all six.
2. **Pick a theme, light or dark.** It sets every surface and ink value. Dark is the default for marketing and pitch material; light for documents, reports and anything printed or read closely. Done when the theme is chosen and stated.
3. **Start from `assets/starter.html`.** Copy it with `terminal` (`cp`) into the output location; never retype it. It already wires up the nav, footer, scroll machinery, fonts, both theme token sets, the embedded logo, favicon, branded scrollbars and the default patterned background. Done when the copy exists and opens.
4. **Build sections** from `references/tokens.md` (every CSS custom property, both themes) and `references/components.md` (logo lockup, hero, patterned beat, cards, stats). For anything neither covers, search `references/brand-guide.html` with `search_files` and lift the section you need. Done when every component traces to one of these files.
5. **Write copy** to the rules in `references/voice.md`. For anything longer than headings and labels, load `/bitpool-brand-guidelines`.
6. **Check the render.** If the browser tools are available, open the file and take a screenshot to inspect it; otherwise read back the HTML against the Verification list. Done when every Verification item passes.
7. **Deliver.** Give the file path in a terminal session. On a messaging platform, attach the HTML with `MEDIA:/absolute/path/file.html` and add a screenshot if one was taken.

## The six non-negotiables

These are absolute; violations break the brand.

### 1. The logo is always present

Every Bitpool artefact carries the cube logo: nav top-left, and again in the footer. No exceptions. The cube is the only visual identifier; "Bitpool" is Inter text beside it, never a separate wordmark graphic. Use `assets/cube-logo.png` or the version embedded in `assets/starter.html`, and never regenerate it. Never invert, recolour, rotate or filter it.

### 2. One font: Inter

Full weight range (100–900). No serif, no display fonts, no monospace except tiny utility labels.

```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap" rel="stylesheet">
```

### 3. Bold cyan replaces italics

Use `<strong>` in brand cyan at weight 700 wherever italic emphasis would normally go. Nothing is ever italic.

```css
strong, .accent { color: var(--accent); font-weight: 700; font-style: normal; }
```

### 4. Brand cyan is sacred: use it sparingly

`#00ADEF`, identical in both themes. It punctuates (emphasis words, key stats, eyebrow labels). It never carries body copy, headlines or backgrounds, except as the soft glow.

### 5. The patterned background is the default

The imageless patterned beat (graded panel, drifting cyan glows, masked hairline grid) is the default cinematic treatment; full CSS and markup are in `references/components.md`. Never use generated cityscapes, wireframe buildings or HUD chrome.

### 6. Restraint over decoration

No emojis, no HUD overlays. Hairline borders only. Branded scrollbars (already in `starter.html`). Long slow animations (1.4–1.8s reveals). One idea per section. A single accent colour.

## Two themes: light and dark

Both themes share identical variable names; the full sheet is in `references/tokens.md`, and `assets/starter.html` has both built in. Switch with `data-theme="light"|"dark"` on `<html>`. Never mix the two palettes in one artefact.

## Section choreography

A typical page alternates solid sections and full-bleed patterned beats: Hero → Problem → Mission → Axiom grid → Vision (beat) → Scale → Values → Personality → Globe/partners → Growth pillars → Promise → Closing (beat). You don't need every section, but the alternating rhythm is core to the pacing.

## When to depart from this system

Some surfaces, such as dense in-product UI or technical tables, may need more colour for state. Ask with `clarify` whether the user wants the brand/marketing aesthetic or a denser product aesthetic before applying the full system. When in doubt, apply it.

## Pitfalls

- **Logo corruption.** A base64 round-trip through a text tool was measured truncating the logo to under half its length. Never re-encode or reconstruct it: copy `assets/cube-logo.png` as a file, or paste `assets/logo-b64.txt` as-is.
- **Doubled data-URL prefix.** `assets/logo-b64.txt` already begins `data:image/png;base64,`. Writing that prefix yourself makes the logo fail to decode and render as blank space, with no error.
- **Retyping the starter.** `assets/starter.html` is a 53 KB build artefact with the logo embedded. Copy it with `cp`; never regenerate it through `write_file`.
- **Loading the whole style guide.** `references/brand-guide.html` is 135 KB. Use `search_files` to find the section and `read_file` with an offset, rather than reading it all into context.
- Anti-patterns that break the brand:
  - shipping without the logo
  - recolouring the cube or rebuilding "Bitpool" as a wordmark graphic
  - stock or generated cityscapes instead of the patterned beat
  - mixing palettes
  - italic serif emphasis
  - HUD elements, corner brackets or scanlines
  - a second accent colour
  - bouncy easing
  - default OS scrollbars, or a blank, letter or globe favicon

## Verification

- Cube logo present in the nav (top-left) and the footer, from the shipped file.
- Inter is the only font family loaded.
- No `font-style: italic`, `<em>` or `<i>` anywhere.
- One theme only, set via `data-theme` on `<html>`.
- `#00ADEF` appears only on emphasis, stats, eyebrows or glow, never on body copy or backgrounds.
- No emojis; branded scrollbars and the Bitpool favicon present.

## Reference files

| File | Covers |
|---|---|
| `references/tokens.md` | Every CSS custom property, both themes, values verbatim |
| `references/components.md` | Component HTML/CSS: nav, hero, the patterned beat, cards, stats, logo lockup |
| `references/voice.md` | Design copy: headings, labels, microcopy. The working summary only; `/bitpool-brand-guidelines` is the deeper authority on voice |
| `references/brand-guide.html` | The 135 KB living style guide, for anything the three above don't carry |

Assets: `assets/cube-logo.png` (256×227 transparent cube mark), `assets/logo-b64.txt` (complete base64 data URL), `assets/starter.html` (full starter template).
