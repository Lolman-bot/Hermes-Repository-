# Reading the diagram and redrawing it

The PNG is a reference, not an ingredient. Nothing from it is embedded in the output; every box,
line, label and icon is rebuilt as HTML and inline SVG so it stays sharp at any size. This file covers
how to read the PNG, write the inventory the user confirms, and lay the redraw out on the stage.

## 1. Look at it properly

Open the PNG with `vision_analyze` so you can see it. If it is large or dense, look again at each region in turn
before writing anything down. A missed label is the most common way this skill gets a diagram wrong,
and the user will notice it before they notice the motion.

## 2. Write the inventory

Write a plain list, in the chat, of everything the diagram contains:

| Kind | What to record |
|---|---|
| **Nodes** | Every box, circle, card, device or icon: its exact text (spelling, capitals and numbers as written), and roughly where it sits (left / centre / right, top / middle / bottom). |
| **Connections** | Every arrow or line: from which node to which, its direction, whether it is solid, dashed or two-way, and any label on it. |
| **Groups** | Every container, swim lane, layer or bracket that holds other nodes, with its title. |
| **Values** | Numbers, percentages, units, readings. Copied exactly; never rounded or "tidied". |
| **Title or caption** | Text that labels the whole diagram. Diagram-only output leaves it out of the stage; it becomes the HTML `<title>` instead. |
| **Story** | One sentence: what the diagram is saying, and in which order a viewer should take it in (left to right, top to bottom, centre out, input to output). This order drives the build-in. |

Anything you can't read with confidence goes in the list as a question, not a guess
("the third box says either *AHU-2* or *AHU-Z*, which is it?").

Then add the **motion plan** under it (see `motion-catalogue.md`) and ask the user to confirm both
together, in one message. Don't build before they say yes. Changing a label after the build is cheap;
discovering the diagram was misread after the user has watched it is not.

## 3. Lay it out on the stage

The stage is 1920×1080. The diagram lives in `.w-stage`, a 1680×852 area at left 120, top 114, so
there is a 120px margin left and right. Every direct child of `.w-stage` is `position:absolute`;
place each with `left` / `top` / `width` in pixels.

- **Keep the original's layout.** Same relative positions, same reading direction, same grouping.
  Tidy it (align to a grid, even out the gaps, straighten near-straight lines) but don't rearrange
  it; people recognise their diagram by its shape.
- **Fit it to the area.** Scale the original's proportions to fill 1680×852 without distorting
  aspect. A tall diagram centres horizontally with space either side; a wide one centres vertically.
- **Snap to the grid.** The background grid is 64px minor, 256px major. Aligning node edges to
  multiples of 32px makes the redraw look designed rather than traced.
- **Connections are one SVG.** Put a single `<svg>` at the size of the area it spans, with one
  `<path>` per connection. Use cubic curves (`C`) for bends, as the library does, and reuse the same
  `d` string for any particle that travels along it (`offset-path:path('…')`).
- **Leave room for motion.** Pulses, ripples and glows extend beyond the element. Keep at least 24px
  clear around anything that pulses.

## 4. Map the original's parts to Bitpool parts

Don't copy the original's colours, fonts, shadows or clip-art. Translate each part into the Bitpool
vocabulary below. All of it is already styled by the template, by `motion-recipes.css`, or by a
small rule in the diagram's own CSS.

| In the original | Redraw as |
|---|---|
| Plain box / process step | `.box` card: `var(--bp-surface-2)` background, hairline border, 6px radius, `h4` title, `p.sm` detail |
| The central or "Bitpool" node | A white or `var(--bp-white)` card with a cyan border and a soft cyan glow, as `.m-flow .core` |
| Small label, tag, device or point name | `.chip` (outlined pill); a highlighted result is a solid cyan chip (`.m-flow .dst`) |
| Numbered step | Cyan circular badge with the number in Inter 600 |
| Arrow / line | SVG `path`: `stroke: rgba(0,173,239,.25–.6)`, width 2; dashed (`4 8`) for "data flowing", solid for "physically connected" |
| Arrowhead | A small SVG `marker` in `var(--bp-accent)`, or let a travelling particle show the direction |
| Container / layer / zone | Large rounded rectangle, hairline border, `var(--bp-accent-tint)` or `var(--bp-surface-2)` fill, an `.eyebrow`-style label top-left |
| Icon or picture of equipment | A simple line-drawn inline SVG in `var(--bp-accent)` / `var(--bp-ink-70)`, 2px strokes. Never a raster image, never an emoji |
| Big number / KPI | Inter 200, large, `var(--bp-accent)`, as `.m-deal .big` |
| Emphasis in a sentence | `<strong>` (bold cyan). Nothing is ever italic |

Colour comes from the tokens only: cyan `var(--bp-accent)` for the one thing that matters, ink
greys for everything else. Keep to a single accent. If the original colour-codes categories
(red / amber / green), keep the meaning but carry it with cyan versus grey, a label, or a fill
strength. Bring in a second hue only when the colour *is* the information (a fault state, say),
and ask the user first.

## 5. Text

- Copy every label exactly as the inventory recorded it. Don't shorten, reword or "improve" it.
- Inter only. Weights: 200 for big display numbers, 500 for node titles, 300 for detail text,
  500–600 uppercase with letter-spacing for chips and eyebrows.
- Minimum size on the 1920×1080 stage: 15px for anything a viewer must read. If a label can't fit
  at that size, widen the node rather than shrinking the text.
