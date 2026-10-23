---
name: bitpool-sld-converter
description: "Use when redrawing a BMS single line diagram for Bitpool."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, bms, single-line-diagram, sld, meters, svg, png, dashboards, energy]
    category: bitpool
    related_skills: [bitpool-hvac-schematics, bitpool-dashboard-builder, bitpool-report-builder, bitpool-cinematic-photo]
---

# Bitpool SLD Converter

Takes a screenshot of a single line diagram (SLD) from a legacy BMS and gives back the same meter
tree redrawn in Bitpool's style: a cyan incoming line, navy feeders, ringed main meters and cyan open
dots for branch meters, with no text at all. It is spaced so a Bitpool data card fits above every dot
and padded for the dashboard's zoom. You get `[board]-single-line.png` (transparent, high-res),
`[board]-single-line.svg` and `[board]-meters.json` (every meter's label and its position, in pixels
and as a percentage of the image), for an Image Freeform widget.

Optionally it then builds the dashboard as well (stage 2): a root-level dashboard with one
full-width Image Freeform widget and one active power stream per meter, so the user only has to
upload the image and place the point displays.

## When to Use

- The user runs `/bitpool-sld-converter`.
- The user hands over an SLD, meter tree or switchboard screenshot from a BMS and asks to redraw or
  convert it: "convert this single line diagram to a Bitpool graphic", "redraw this SLD as an SVG",
  "turn this old BMS meter screen into a dashboard image".

Don't use for:
- HVAC and plant graphics: use `/bitpool-hvac-schematics`.
- General Bitpool Cloud dashboards: use `/bitpool-dashboard-builder`.
- Paginated reports: use `/bitpool-report-builder`.
- Image or render prompts: use `/bitpool-cinematic-photo`.

## Prerequisites

- Python 3 for `scripts/render_sld.py` (stdlib only for the SVG and `meters.json`). For the PNG,
  either `cairosvg` with the Cairo library (`python -m pip install cairosvg`), or Microsoft Edge or
  Google Chrome installed: with no Cairo, as on most Windows machines, the script screenshots the SVG
  with headless Edge or Chrome instead.
- Stage 2 only: a Bitpool MCP connector with the dashboard and stream tools (see
  `references/dashboard-stage.md`).

## Procedure

1. **Read the screenshot into a meter tree.** Look at it with `vision_analyze`. Work out the
   incoming line, each feeder group, its main meter and every branch meter, including meters nested
   under a sub-board at any depth, and copy each label exactly as written. Read
   `references/trace-the-diagram.md` with `read_file` first. Write the topology JSON with
   `write_file` in the shape of `assets/example-msb-1a.json` (`assets/example-nested.json` for
   sub-boards). Ask with `clarify` about any unreadable label. Done when the per-group and per-row
   meter counts in the JSON match the screenshot.
2. **Render it** with `terminal`:
   `python <skill-dir>/scripts/render_sld.py topology.json --out [output folder]` (`python3` on
   Linux/macOS). Ask the user where the files should go and default to the session's working
   folder. Never hand-draw the SVG: the script carries the agreed styling, spacing and padding.
   Detail: `references/drawing-rules.md`. Done when the script prints the three output paths and
   the main/branch meter counts.
3. **Check it before handing it over.** Render a small preview on `#f4f4f4`, look at it with
   `vision_analyze`, and compare group by group with the screenshot: same groups, same number of
   meters on every branch. Fix the topology and re-render on any mismatch. Done when the preview
   matches the screenshot group by group.
4. **Hand over** the PNG and SVG (on a messaging platform attach them as `MEDIA:/absolute/path`).
   Show the traced labels per group so the user can catch a misread, and say that tweaks such as
   the spacing are a one-line change. Done when the user has the files and the label list.
5. **Offer stage 2.** Ask with `clarify` whether to set up the dashboard too, as an option the user
   can turn down. On yes, ask for the dashboard name and which Bitpool connector to use, then
   follow `references/dashboard-stage.md`: pick the site's pools, find one active power stream per
   meter label, show the match list, and create the dashboard only after the user says go. Then
   finish the widget: walk the user through uploading the PNG to the Graphic Library, attach it
   from the gallery, and place the point displays automatically where the widget allows it,
   otherwise guide the user through placing them. Done when the user declines, or the dashboard
   validates and the hand-over report is sent.

## Load-bearing rules

1. **Only the wiring and the meter dots are drawn.** No labels, values, point displays, borders,
   brackets, headers or footers. The user places their own data cards; anything else drawn on the
   image clutters it. Labels live only in the SVG's `data-label` attributes and in `meters.json`.
2. **The meter count must match the screenshot exactly, branch by branch.** Every dot will be tied
   to a real meter, so a missing or extra dot breaks the dashboard. When a label is unreadable, ask;
   never guess a label or invent a meter.
3. **Original flat styling, always.** Cyan `#00ADEF` incoming line, navy `#1B2732` feeders, rounded
   bends, junction dots, white-filled cyan rings for branch meters, navy rings with a cyan centre for
   main meters. The 3D, glow and engraved styles were tried and rejected.
4. **Spacing is fixed for data cards and kept as compact as that allows.** 100 units between rows,
   140 between groups, 400 between branch meters along a row. The wider horizontal spacing applies
   to branch meters only, never the main meters. Change it only when the user asks.
5. **Same padding on every drawing**: 1360 px left, 1500 px right, 1780 px top, 1700 px bottom, at
   1.5 px per unit, with a transparent background. That's what gives the dashboard a consistent
   zoom level, so the script applies it and it is not adjusted per job.
6. **Stage 2 is opt-in and never writes until the user says go.** Show the dashboard name, the
   connector, the organisation, and the matched and unmatched meters first. Create the dashboard at
   the root of the organisation, with exactly one full-width Image Freeform widget.
7. **One active power stream per meter, and never a guess.** Attach only a stream whose name
   contains the meter's label as a whole token and whose point is the meter's total active power,
   not a phase, average, demand, reactive or apparent value. If no stream qualifies, leave the meter
   off and list it as unmatched.
8. **Never claim what the connector can't do.** It can't upload an image, and it can place point
   displays only if the widget's type details name a position setting. Check them each run; use the
   manual walk-through when there is none, and never invent a field name.

## Pitfalls

- **"Tidying" labels.** Stage 2 matches streams on the exact label text; a corrected case, hyphen or
  slash matches nothing. Labels split over two lines are one label joined by a single space.
- **Hand-drawing or retyping the SVG.** The styling, spacing and padding live in the script's
  constants; anything drawn by hand drifts from them. Run the script.
- **Skipping the preview.** A dropped or doubled meter is easy to miss in the JSON and obvious in
  the image.
- **Multi-term stream searches.** `get_streams` matches one substring: search the label alone and
  filter the results yourself.
- **Near-miss matches.** `TDB-L07-A-L` must not match `TDB-L07-A-L2`, and `ACTIVE_POWER_A` is a
  phase value, not the total. Unmatched is the right answer when nothing qualifies.
- **Offering a scheduler-only connector.** Some Bitpool connectors lack the dashboard tools; check
  for all five required tools before offering one.
- **Cairo on Windows.** `cairosvg` often imports but can't find the Cairo library; the script falls
  back to Edge or Chrome on its own, so don't spend time installing Cairo.

## Verification

- The topology's meter count per group and per row matches the screenshot, counting every level of
  nesting.
- `render_sld.py` wrote `[board]-single-line.png`, `.svg` and `[board]-meters.json`, and a preview
  was inspected with `vision_analyze` this run.
- The drawing has no text, values, borders or headers; only wiring and meter dots.
- Stage 2 (if run): nothing was created before the user said go, the dashboard sits at the root
  with one full-width Image Freeform widget, `validate_dashboard` passed, and the unmatched meters
  were listed.

## Reference files

Read the file itself — this table is an index, not a substitute.

| File | Covers |
|---|---|
| `references/trace-the-diagram.md` | Reading a BMS SLD screenshot: what counts as a group, a main meter and a branch meter, how to order rows and meters, the `join` value, label copying rules, what to drop, and the self-check against the screenshot. |
| `references/drawing-rules.md` | The renderer: running it, its outputs, the style tokens, every spacing and padding constant and why it's that value, and how to make the changes users usually ask for. |
| `references/dashboard-stage.md` | Stage 2: the questions to ask, choosing a Bitpool connector that can build dashboards, picking the site's pools, the active-power matching rules with examples, the confirmation step, the tool calls that create the dashboard and widget, validation, and the hand-over report. |

Assets (copy, never retype from memory) and scripts:

| File | What it is |
|---|---|
| `assets/example-msb-1a.json` | The topology for the MSB-1A diagram this skill was built from: 3 groups, 3 main meters, 36 branch meters. The shape to copy and a test input for the renderer. |
| `assets/example-nested.json` | A small made-up board with sub-boards nested three levels deep. The shape to copy for nested meters, and a second test input. |
| `scripts/render_sld.py` | Topology JSON → `[board]-single-line.svg`, `.png` and `[board]-meters.json`. Run it; don't rewrite its drawing logic inline. `--dx` sets branch meter spacing, `--scale` PNG pixels per unit. |

## Editing this skill

The styling, spacing and padding values live in the constants at the top of
`scripts/render_sld.py`. Change them there first, then update `references/drawing-rules.md` and
rules 3–5 above in the same pass, and bump `version`. The dashboard tool calls follow the Bitpool
connector's own `get_dashboard_configuration_guide`: if the connector changes, re-read it and update
`references/dashboard-stage.md`.
