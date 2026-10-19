---
name: bitpool-hvac-schematics
description: "Use when making an HVAC or plant BMS graphic for Bitpool."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, hvac, bms, scada, schematics, html, svg]
    category: bitpool
    related_skills: [bitpool-design-system, bacnet-diagnostics, bitpool-dashboard-builder]
---

# Bitpool HVAC Schematics

Build **interactive HTML BMS graphics** for HVAC and central plant in the Bitpool brand — the same kind produced for AHU-01, CHW-01 and CT-01: an SVG plant schematic with live data-point chips, animated flow, equipment status colours, segmented commands, a live points list, and an alarm panel, all in one self-contained, self-animating HTML file in the Bitpool light theme.

The method ships with this skill in `references/`; the shell, logo and build script ship in `assets/` and `scripts/`. This skill assumes the brand from `/bitpool-design-system` (load it too for tokens) and adds the HVAC-specific shell, glyph library and live-data pattern on top.

## When to Use

- The user asks for an HVAC schematic, mechanical/plant graphic, BMS or SCADA graphic, plant diagram, equipment mimic, or an AHU/chiller/cooling-tower/boiler/pump diagram.
- They want a "graphic with data points on it", or to match the AHU/CHW/cooling-tower pages already built — even if they only say "make a graphic for the chiller/boiler/AHU".
- They mention Bitpool alongside any plant/mechanical equipment and want a visual.
- Covers AHUs, chilled water, condenser water / cooling tower, boiler and heating-water plants, and multi-plant overview dashboards.

Don't use for:
- Diagnosing a BACnet network fault: use `/bacnet-diagnostics`.
- A dashboard inside Bitpool Cloud itself: use `/bitpool-dashboard-builder`.
- General Bitpool pages with no plant content: use `/bitpool-design-system` alone.

## Prerequisites

- Python 3 for `scripts/build.py`. The `render` step also needs Playwright with Chromium (`python -m pip install playwright` then `python -m playwright install chromium`); if it can't be installed, open the page with the Hermes browser tools and check it with `browser_vision` instead.

## Procedure

1. **Identify the system and topology first** — it decides which recipe you pull (AHU, CHW, CT, overview). Ask with `clarify` if it's ambiguous. Done when the system type and topology are stated.
2. **Read the method** with `read_file`: `references/hvac-schematic-workflow.md`, then the matching recipe in `references/hvac-canonical-layouts.md` and `references/hvac-glyph-library.md` **before drawing**, and `references/hvac-live-data-model.md` **before scripting**. Read the whole file you reach for; skimming for the line you expect is how a threshold or a flag gets missed. Also load `/bitpool-design-system`. Done when all four are read this run.
3. **Start from the shell.** Copy `assets/shell.html` to the output location with `terminal` (`cp`); never retype it. Done when the copy exists.
4. **Compose the schematic** from the recipe and glyph library in the drawing order (rule 6). Never invent a glyph, a class name or a colour from memory — the CSS primitive classes in the shell are the binding contract, and a made-up class name renders as nothing. Done when every element uses a shell class or library glyph.
5. **Wire it live** with `model()` / `paint()` / `wire()`: stable chip ids, roughly four segmented commands that genuinely change the graphic, off-equipment behaviour, real-fault-only alarms. Done when each command visibly changes the graphic.
6. **Embed the logo:** `python <skill-dir>/scripts/build.py inject <page.html>`. Done when it reports placeholder(s) replaced.
7. **QA with a render:** `python <skill-dir>/scripts/build.py render <page.html>`, then look at the PNG with `vision_analyze` for overlaps, disconnected risers and illegible labels. Fix and re-render. Done when the PNG shows none of those.
8. **Deliver.** Give the file path in a terminal session; on a messaging platform attach `MEDIA:/absolute/path/page.html` and the preview PNG. For multi-plant sets, also build the overview (recipe D) and the shared `.nav-links` bar, all in one folder. Done when the user has the file(s).

## Local assets

```
bitpool-hvac-schematics/
├── assets/
│   ├── shell.html      ← the full reusable page: head, CSS (brand tokens + every SVG
│   │                      primitive class), nav, KPI strip, schematic panel, side rail,
│   │                      footer, JS scaffold. Start here.
│   └── logo-b64.txt    ← the Bitpool cube logo as a base64 data URL
└── scripts/
    └── build.py        ← `inject` the logo, `render` a Playwright preview for QA
```

**Copy these files; never reconstruct them from prose.** The shell's class names must match exactly, and base64 image data does not survive being retyped.

## Load-bearing rules

Restated here because breaking one produces an off-brand or non-functional graphic.

1. **Light theme only.** These are read closely, like dashboards. No dark variant.
2. **Cyan `#00ADEF` is the only brand accent.** Bold cyan replaces italics. No second decorative colour.
3. **Functional colour must carry meaning** — supply-blue `#1E74C8`, return-red `#D9534F`, heating-orange `#E8843A`, cooling-blue `#2BA6E0`, state dots green/amber/red/grey. Never decorative, and always add a `.legend` explaining the ones used.
4. **Inter for UI, JetBrains Mono for values.** Nothing else. Cube logo in nav *and* footer.
5. **Hairlines only**, no heavy rules, no emojis, `cubic-bezier(0.2,0.8,0.2,1)` easing.
6. **Draw in order**: headers/ducts → flow overlays → equipment → sensors and leaders → data chips last, so chips stay legible.
7. **Every live value gets a stable chip `id`.** Those ids are the binding contract when the page goes live — don't rename them.
8. **Off equipment greys out, stops its flow, and shuts its valves.** Alarms fire only on real faults, never on a normal condition.
9. **Confirm before writing to plant.** Command and write points are side-effecting.
10. **QA with a render.** `build.py render`, then actually look at the PNG for overlaps, disconnected risers and illegible labels.

## Pitfalls

- **Retyping the shell or the logo.** Base64 image data does not survive being retyped, and a mistyped class name renders as nothing. Copy with `cp`.
- **Inventing glyphs or class names from memory.** Only the shell's primitive classes and the glyph library are valid.
- **Chips drawn before equipment** end up hidden; follow the drawing order.
- **Renaming chip ids** breaks the binding when the page is wired to real Bitpool data.
- **Skipping the render.** Overlaps and disconnected risers are invisible in the source; only the PNG shows them.

## Verification

- The page started from a copy of `assets/shell.html` and the logo was injected by `build.py inject` (no `__LOGO__` left).
- Light theme, Inter + JetBrains Mono only, cube logo in nav and footer, a `.legend` for every functional colour used.
- Every live value has a stable chip `id`; off equipment greys out, stops flow and shuts valves.
- A render PNG was inspected this run and shows no overlaps, broken risers or illegible labels.

## Reference files

Read the file itself — the table is an index, not a substitute.

| File | Covers |
|---|---|
| `references/hvac-canonical-layouts.md` | The four proven Bitpool plant-schematic compositions — AHU, chilled water plant, cooling tower plant, and the central plant overview dashboard — with coordinates, per-page CSS and the composition checklist. |
| `references/hvac-glyph-library.md` | Copy-paste SVG components for Bitpool HVAC/plant schematics — drawing order, colour convention, pipes and ducts, sensors, valves, pumps, fans, coils, chillers, cooling towers, data chips and side-rail markup. |
| `references/hvac-live-data-model.md` | The model() / paint() / wire() pattern that makes a Bitpool HVAC schematic live — command state, staging, the four paint targets, damper feedback, the tick, and how to swap the mock for a real feed. |
| `references/hvac-schematic-workflow.md` | The seven-step workflow for building a Bitpool HVAC/plant schematic, the hard brand rules that must not drift, and how to bind a finished graphic to real Bitpool data. |

Workflow, glyphs, live-data pattern, layouts and brand rules are edited in `references/`; the shell, logo and build script in `assets/` and `scripts/`.
