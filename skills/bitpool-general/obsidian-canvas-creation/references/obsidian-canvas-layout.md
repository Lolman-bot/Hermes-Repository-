# Obsidian Canvas Layout

Produce a `.canvas` file — Obsidian's JSON canvas format — that is **readable without manual
cleanup**. The hard part is not the JSON. It is spacing, so edge labels don't overlap tiles. This
page encodes a layout method that works.

> **Warning**
> Before drawing an architecture or system diagram, understand the real system first — read the
> code and docs. A pretty diagram of the wrong architecture is worse than no diagram.


## The `.canvas` JSON format

A canvas is a single JSON object with two arrays: `nodes` and `edges`. Write it with the
`write_file` tool. Obsidian re-saves (minifies) it on focus — that's fine.

### Nodes

Every node needs a unique string `id`, plus `x`, `y`, `width`, `height` — integers, world units ≈
px at 100% zoom. `y` increases **downward**.

```json
{"id":"n_lambda","type":"text","x":2716,"y":1585,"width":400,"height":230,"color":"5","text":"### λ Lambda\nbody text with \\n line breaks, **bold**, `code`, *italics*"}
```

| Type | Use |
|---|---|
| `"text"` | Markdown card, using `text`. Your default. |
| `"group"` | A labelled bounding box drawn *behind* its children. Uses `label`, not `text`. |
| `"file"` | Embeds a vault file (`"file":"path/to/note.md"`). Rare for diagrams. |
| `"link"` | Embeds a URL (`"url":"…"`). |

> **Important**
> A group has **no real parent/child link** — membership is purely geometric. Children are nodes
> whose rect falls inside the group rect, so the group rect MUST enclose every child. A child poking
> outside silently drops out of the group.


`color` is optional: presets `"1"`–`"6"` are red, orange, yellow, green, cyan, purple — or a hex
string like `"#7b6cd9"`. Pick by role and stay consistent.

### Edges

```json
{"id":"e1","fromNode":"n_a","fromSide":"right","toNode":"n_b","toSide":"left","label":"launches","color":"6"}
```

`fromNode`/`toNode` are node ids. `fromSide`/`toSide` are `"top"|"right"|"bottom"|"left"` — the
anchor point on each node. `label` and `color` are optional. `fromEnd`/`toEnd` can be
`"none"|"arrow"`, defaulting to from=none, to=arrow.

Obsidian attaches the edge at the **centre of the named side** and draws a bezier. So for a clean
horizontal arrow, the two nodes must share the same vertical centre.

## Layout method

## Swimlanes

Group the diagram into 2–4 horizontal lanes, one concept each — "Auth", "Backend", "Data sync".
Stack lanes top-to-bottom with a clear vertical gap (≥40px between one group's bottom and the
next group's top). Each lane is a `group` node containing a left-to-right flow.

## Horizontal flow, centres aligned

Lay each lane's main chain left→right, and **align the vertical centre of every tile** so the
connecting arrows are perfectly horizontal:

```
center_y = tile.y + tile.height/2     // keep this constant across the row
tile.y   = center_y - tile.height/2   // derive each tile's y from its height
```

Aligned centres mean `fromSide:"right"` / `toSide:"left"` edges render as straight horizontal
arrows, and the label sits in the clear gap between tiles.

## Horizontal spacing — the formula

This is the whole point. The gap between two tiles must fit the edge label. Set the **clear
gap** — the space between the right edge of tile A and the left edge of tile B — from the label's
character count:

```
gap = (label character count) × 12 + 344
```

Then place the next tile: `nextTile.x = prevTile.x + prevTile.width + gap`.

| chars | gap |
|------:|----:|
| 6 | 416 |
| 8 | 440 |
| 16 | 536 |
| 21 | 596 |
| 24 | 632 |
| 31 | 716 |

Why this exact formula: a fixed pitch makes short labels fine but long labels overflow; a steep
per-char slope (say ×55) leaves long labels floating in absurd whitespace. `×12 + 344` keeps the
slope gentle and anchors the short end at the known-good 440 — the empirically "looks good" value
for an 8-character label like `"launches"`.

> **Note**
> If the user wants tighter or looser spacing overall, change the **+344 buffer**, not the slope. If
> they want label length to matter more or less, change the **×12 slope**.
>
> **Don't shrink labels to fit a small gap** — size the gap to the label.


## Vertical taps for secondary tiles

Secrets, sub-components, role lists and similar that hang off a main tile go **below** it as a
vertical drop (`fromSide:"bottom"` → `toSide:"top"`) with a ~260px vertical gap.

Vertical labels rarely overflow — there's open space left and right of the pill — so a fixed gap
is enough; no need to apply the character formula vertically. Centre the tap under its parent:
`tap.x = parentCenterX - tap.width/2`.

## Group bounding boxes

After placing children, size each group to enclose them with padding:

- `group.x = minChildX - 40`
- `group.y = minChildTop - (room for the label, ~120)` or a fixed lane top
- `group.width = (maxChildRight - group.x) + 40`
- `group.height = (maxChildBottom - group.y) + 40`

Verify every child rect is fully inside the group rect.

## Long, return and cross-lane edges

Backward arrows (a return step) and cross-lane links are fine as long beziers — they're long, not
cramped, so the label formula doesn't apply. Give them a distinct `color` so they read as "out of
band". Keep them few.

## Build procedure

1. **Model the system.** List the tiles, what each says, and the directed connections with their
   labels. Decide the 2–4 lanes.
2. **Choose tile widths and heights.** Roughly 320–400 wide, height to fit the text. Keep widths
   roughly uniform within a lane.
3. **Compute X positions** left→right per lane using the gap formula; **compute Y** from a
   constant lane centre.
4. **Place vertical taps** below their parents, ~260px.
5. **Size groups** to enclose children plus padding.
6. **Write the file** with `write_file`, at an absolute path ending in `.canvas`. It goes wherever the
   user keeps their Obsidian vault — ask if unknown.
7. **Sanity-check the maths, don't eyeball it.** For each horizontal edge confirm
   `gap == chars×12+344`; for each group confirm it encloses its children. Report the gap table so
   the user can adjust the buffer or slope.

## Colour conventions

Suggested — keep them consistent within a diagram.

| Colour | Role |
|---|---|
| `5` cyan | Clients / compute / transport — the "happy path" tiles |
| `6` purple | Auth / identity-adjacent steps, or a lane accent |
| `1` red | External identity providers / warnings |
| `3` yellow | Secrets / credentials / config |
| `4` green | Datastores / persisted data / roles |
| `2` orange | External source systems / ingestion |

Lanes (`group` nodes) can take a lane-level accent colour; tiles inside take role colours.

## Gotchas

- **JSON validity.** Escape `\n` for line breaks inside `text`; double-quote keys; no trailing
  commas. A malformed `.canvas` opens blank in Obsidian.
- **Emoji and markdown in `text`** render in the card — `### Heading`, `**bold**`, `` `code` ``
  and bullet lists all work.
- **Centres, not tops, drive horizontal arrows.** If arrows look diagonal, the two tiles' vertical
  centres differ.
- **Group membership is geometric** — see the warning above.
- Tell the user to **Zoom-to-fit** (the fit button, or `Shift+1`) to see the whole canvas. Wide
  lanes are expected when labels are long.
- Don't leave scratch or example canvases in the vault unless asked — offer to delete them.
