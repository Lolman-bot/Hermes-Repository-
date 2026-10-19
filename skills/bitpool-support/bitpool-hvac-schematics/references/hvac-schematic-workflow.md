# HVAC Schematic Workflow

Build **interactive HTML BMS graphics** for HVAC and central plant in the Bitpool brand — the
kind produced for AHU-01, CHW-01 and CT-01: an SVG plant schematic with live data-point chips,
animated flow, equipment status colours, segmented commands, a live points list, and an alarm
panel, all in one self-contained, self-animating HTML file.

> **Note**
> This is the visual and behavioural counterpart for **mechanical plant mimics**. For general
> Bitpool brand tokens — colours, type, logo, themes — also load the `bitpool-design-system`
> skill. This system assumes that brand and adds the HVAC-specific shell, glyph library and
> live-data pattern on top.


## What you produce

A single `.html` file per system that:

- renders an **SVG schematic** of the plant on the Bitpool **light theme** — white paper,
  near-black ink, Inter, cyan `#00ADEF` accent, hairline borders, cube logo in nav and footer;
- annotates **every device with a live data-point chip** — temps, pressures, flows, valve %,
  damper %, fan/pump speed, levels, status;
- **animates flow** with marching dashes and spins fans and pumps while running, stopping them
  when off;
- carries a **KPI strip**, a **Commands** rail of segmented controls that change the picture, a
  **Live Points** list, and an **Alarm Status** panel;
- uses **functional colour** only where it carries meaning — supply-blue / return-red,
  heating-orange / cooling-blue, green/amber/red equipment states — and brand cyan everywhere
  else.

## Identify the system and topology

Which plant? How many of each unit — chillers, towers, AHUs, pumps? Primary-only,
primary/secondary, variable flow? What instrumentation?

If the user gave a reference image, mirror its topology. If anything material is ambiguous —
unit count, economiser yes/no, decoupler yes/no — ask once with selectable options. Don't stall.

## Load the brand

Read the `bitpool-design-system` skill for current tokens. The shell already encodes the
light-theme tokens, but defer to the design system if they differ.

## Start from the shell

Copy `assets/shell.html` from the skill folder. It contains the full head, CSS (brand tokens
plus every SVG primitive class), nav with cube logo, KPI strip, schematic panel, the
Commands/Points/Alarms side rail, and a JS scaffold.

Fill the `__PLACEHOLDER__` slots: system name, unit id, subsystem, tag, location, description,
panel title and tag.

## Compose the schematic

Pick the closest recipe in [Canonical Layouts](hvac-canonical-layouts.md) — A=AHU, B=chilled
water, C=cooling tower, D=overview — and lay out the SVG using the copy-paste components in the
[Glyph Library](hvac-glyph-library.md). **Read both before drawing.**

Draw in order: headers/ducts → flow overlays → equipment → sensors and leaders → data chips.
Use the **1280 × 700** viewBox (AHU uses 1240 × 600) so everything scales as one unit.

## Wire it live

Implement `model()` / `paint()` / `wire()` per the [Live Data Model](hvac-live-data-model.md).

Give every live value a stable chip `id`. Add roughly four segmented commands that genuinely
change the graphic — staging, enable/disable, setpoint, occupancy. Make off-equipment grey out,
stop its flow, and shut its valves. Fire alarms only on real faults.

## Embed the logo and QA

The shell references the cube logo via a `__LOGO__` placeholder. Inject it and render a preview:

```bash
python <skill-dir>/scripts/build.py inject path/to/page.html
```

```bash
python <skill-dir>/scripts/build.py render path/to/page.html
```

Inspect the PNG: no overlapping glyphs or chips, risers connect, labels legible, flow sensible.
Fix and re-render. Then deliver the final file: give its path in a terminal session, or attach it
as `MEDIA:/absolute/path/page.html` (plus the preview PNG) on a messaging platform.

## Multi-plant sets

If building several plants, also produce the **overview dashboard** (recipe D) and inject the
shared `.nav-links` bar into every page so they cross-link. Keep all files in one folder.

## Hard brand rules — do not drift

> **Important**
> These are absolute. A graphic that breaks one of them is off-brand even if it is technically
> correct.


- **Light theme only** for these graphics — they are read closely, like dashboards and reports.
- Cube logo present in nav **and** footer; "Bitpool" set in Inter beside it.
- **Inter** for everything UI; **JetBrains Mono** for data values and codes. No other fonts.
- **Cyan `#00ADEF` is the only brand accent.** Bold cyan replaces italics. No second decorative
  colour.
- Functional colours are the sole allowed departure and must carry meaning: supply-blue
  `#1E74C8`, return-red `#D9534F`, heating-orange `#E8843A`, cooling-blue `#2BA6E0`,
  balancing/make-up orange, and state dots green/amber/red/grey. Never use them decoratively,
  and always add a `.legend` explaining the ones used.
- Hairline borders only; no heavy rules, no emojis, `cubic-bezier(0.2,0.8,0.2,1)` easing.
- Sensors render as clean Bitpool chips, **not** the yellow instrument boxes seen on generic
  vendor diagrams — unless the user explicitly asks for literal vendor styling.

## Going live with real data

These ship with a mock `model()` so they animate standalone. To bind to Bitpool data:

- replace only the body of `model()` with a read from the live source — Bitpool stream/graph,
  websocket, or polled REST;
- keep `paint()` and the chip `id`s unchanged;
- route commands to point writes.

> **Warning**
> Treat command and write points as side-effecting. Confirm before writing to plant.
