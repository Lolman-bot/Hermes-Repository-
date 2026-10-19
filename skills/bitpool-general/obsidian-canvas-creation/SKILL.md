---
name: obsidian-canvas-creation
description: "Use when drawing an Obsidian .canvas diagram."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, obsidian, canvas, diagram, architecture, json]
    category: bitpool
    related_skills: [bitpool-hvac-schematics]
---

# Obsidian Canvas creation

Produce a `.canvas` file — Obsidian's JSON canvas format — for architecture flows, data pipelines and process maps that is **readable without manual cleanup**. The hard part is not the JSON; it is spacing, so edge labels don't overlap tiles.

The JSON schema, swimlane layout method, edge-label gap formula, colour conventions and gotchas ship with this skill in `references/`.

## When to Use

- The user asks to draw/create a diagram in `.canvas` format, an Obsidian canvas, or a visual flow/architecture map for Obsidian.
- Architecture flows, data pipelines, auth flows, process maps — anything that is tiles plus labelled arrows.

Don't use for:
- Reading, searching or editing ordinary Obsidian notes: use the bundled `/obsidian` skill.
- HVAC plant or mechanical schematics: use `/bitpool-hvac-schematics`.
- Standalone diagrams that don't need to live in an Obsidian vault (SVG/HTML): use a diagram skill instead.

## Procedure

1. **Understand the real system first** (rule 1) — read the code and docs with `read_file` / `search_files`. Done when you can list every tile, what it says, and each directed connection with its label.
2. **Read the layout method** — `read_file` the whole of `references/obsidian-canvas-layout.md` before computing any coordinates. Done when it is read this run.
3. **Model the layout.** Decide 2–4 swimlanes, tile widths/heights (~320–400 wide, uniform per lane) and colours by role. Done when every tile has a lane, size and colour.
4. **Compute coordinates in code, not by eye.** Use `execute_code` (or a short Python script) to apply the gap formula left→right per lane, derive each `y` from a constant lane centre, place vertical taps ~260px below parents, and size groups to enclose children plus padding. Done when every node has integer `x`, `y`, `width`, `height`.
5. **Ask where the vault is** with `clarify` if unknown. Done when you have an absolute path ending in `.canvas`.
6. **Write the file** with `write_file` (generate it via `json.dumps` so escaping is right). Done when the file parses as JSON with `nodes` and `edges` arrays.
7. **Sanity-check the maths** (rule 6): every horizontal edge's gap equals `chars × 12 + 344`, every group encloses its children, every edge's `fromNode`/`toNode` exists. Done when the check passes and you report the gap table.
8. **Tidy up.** Tell the user to Zoom-to-fit (`Shift+1`) and offer to delete any scratch or example canvases. Done when nothing stray is left in the vault.

## Load-bearing rules

These make a canvas usable rather than merely valid.

1. **Understand the system before drawing it.** A pretty diagram of the wrong architecture is worse than no diagram.
2. **Size the gap to the label, never the label to the gap.** The clear gap between two tiles is `(label character count) × 12 + 344`.
3. **Align vertical centres across a row**, not tops — that's what makes horizontal arrows straight rather than diagonal.
4. **Group membership is purely geometric.** A child whose rect pokes outside the group rect silently drops out of the group. Verify enclosure.
5. **Escape `\n` inside `text`, double-quote keys, no trailing commas.** A malformed `.canvas` opens blank in Obsidian.
6. **Sanity-check the maths, don't eyeball it.** For each horizontal edge confirm the gap matches the formula; for each group confirm it encloses its children. Report the gap table so the user can tune the buffer or slope.
7. **Ask where the vault is** if unknown, and don't leave scratch or example canvases behind — offer to delete them.

## Pitfalls

- **Guessing the gap formula or a node key from memory.** The formula is calibrated, and a wrong JSON key (e.g. `text` on a group instead of `label`) opens blank or mislabelled.
- **Tuning the wrong knob.** Tighter/looser overall → change the `+344` buffer; label length mattering more/less → change the `×12` slope.
- **Aligning tops instead of centres** — tiles of different heights then get diagonal arrows.
- **Hand-writing the JSON string.** Unescaped newlines or a trailing comma break the whole canvas; serialise with `json.dumps`.
- **Too many long return / cross-lane edges.** Keep them few and give them a distinct colour.

## Verification

- The `.canvas` parses as JSON; every node has a unique `id` and integer geometry; every edge references existing nodes.
- Gap table reported: each horizontal edge's gap == `chars × 12 + 344`.
- Every group rect fully encloses each intended child.
- No scratch canvases left in the vault unless the user asked to keep them.

## Reference files

Read the file itself — the table is an index, not a substitute.

| File | Covers |
|---|---|
| `references/obsidian-canvas-layout.md` | The .canvas JSON schema and the layout method that makes an Obsidian Canvas readable first time — swimlanes, centre alignment, the edge-label gap formula, vertical taps, group bounding boxes, colour conventions and gotchas. |

Schema notes, layout method, gap formula, colour conventions, gotchas → edit `references/obsidian-canvas-layout.md`.
