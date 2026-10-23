# Drawing rules

`scripts/render_sld.py` holds every value on this page as a constant at the top of the file. Run it;
don't redraw the SVG by hand.

## Running it

```bash
pip install cairosvg   # once, if it's missing
python3 scripts/render_sld.py topology.json --out [output folder] [--dx 400] [--scale 1.5]
```

On Windows the interpreter is usually `python`, not `python3`. Run both commands with `terminal`.
Ask the user where the files should go (`clarify`) and default to the session's working folder. If `pip` refuses
because the Python is system-managed, add `--break-system-packages` or use a virtual environment.

The PNG comes from `cairosvg`. If that or the Cairo library it needs is missing (usual on Windows),
the script falls back to a headless Edge or Chrome screenshot of the SVG on a transparent background.
It stops with a clear message, leaving the SVG, only when neither is available.

It writes three files, named from the board (`MSB-1A` gives `msb-1a-…`):

| File | What it is |
|---|---|
| `[board]-single-line.png` | The deliverable. Transparent background, 1.5 px per unit, padded for the dashboard. MSB-1A comes out at about 6870 × 6620 px. |
| `[board]-single-line.svg` | The same drawing as a vector file. Every meter carries `id` and `data-label` with its label; no text is drawn. |
| `[board]-meters.json` | Every meter's label, role (`main` / `branch`), group, row, nesting `depth` and `parent` label, and position both in PNG pixels (`px`, `py`) and as a percentage of the image (`pct_x`, `pct_y`). Used for the self-check and for stage 2. |

For the self-check, render a small preview on the dashboard grey and look at it with
`vision_analyze`. With `cairosvg`:

```python
import cairosvg
cairosvg.svg2png(url="[board]-single-line.svg", write_to="[temp folder]/preview.png",
                 background_color="#f4f4f4", scale=0.2)
```

Without it, open the PNG at about 1200 px wide on a `#f4f4f4` page in headless Edge or Chrome and
screenshot that.

## Style

These are the original flat styling, which the user chose over 3D, glow and engraved versions.

| Element | Look |
|---|---|
| Incoming line | Cyan `#00ADEF`, 4 wide, round caps, with a small cyan dot where it starts. |
| Feeders, risers, branch lines | Navy `#1B2732`, 2.5 wide, round caps and joins, 12-unit rounded bends. |
| Junctions | Navy dot, radius 4, on every T where a line branches off. |
| Branch meter | White-filled circle, radius 6.5, cyan ring 2.5 wide. |
| Main meter | White-filled circle, radius 11, navy ring 2.5 wide, cyan centre dot of radius 4.5. |

## Spacing

These were set against real Bitpool data cards. A card reads like "Breaker 03 / 982,263.67 kWh",
about 200 × 75 px on screen, sitting just above its dot.

| Constant | Value | Why |
|---|---|---|
| `S` (row spacing) | 100 | A card fits above each dot without touching the row above. |
| `GROUP_GAP` | 140 | The top row's cards in one group clear the bottom row of the group above. |
| `--dx` (branch meter spacing) | 400 | The user asked for double the original 200, which was itself the minimum for side-by-side cards. Applies to branch meters only. |
| `FIRST` | 120 | Gap from the riser to the first branch meter. |
| `MAIN_OFF`, `DROP0`, `DROP_STEP` | 110, 230, 130 | Room for each main meter's card between its drop and the riser. |
| `NEST_GAP` | 250 | Gap after a meter's sub-board before the next meter on its row, so cards clear the sub-board's lines. |

## Nested meters

A meter with `children` gets a sub-riser dropping from it, in the same navy as the other feeders.
Each child row hangs one row (`S`) below its parent and starts `FIRST` to the right of the sub-riser;
children can have children, to any depth. Two things move to make room: the next meter along the
parent's row shifts right by the sub-board's width, and every later row shifts down by the
sub-board's height. A row with no nesting is spaced exactly as before, so older topologies render
identically.

## Padding

1360 px left, 1500 px right, 1780 px top and 1700 px bottom, on a transparent background. This
matches the padding the user added by hand to the MSB-1A reference so every drawing loads at the
same zoom level in the Image Freeform widget. It's measured in PNG pixels, so it stays the same when
the drawing gets bigger or smaller. Don't change it per job.

## Changes users usually ask for

| Ask | Change |
|---|---|
| "More room between the dots" | Raise `--dx`. Main meters don't move. |
| "More room between the rows" | Raise `S` (and `GROUP_GAP` in proportion). |
| "Bigger PNG" | Raise `--scale`. The padding is in PNG pixels, so it doesn't grow with it. |
| "Join the feed into a different row" | Change that group's `join` in the topology JSON. |

After any change, render the preview and look at it again before handing over.
