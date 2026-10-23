# Reading the screenshot into a meter tree

The renderer draws whatever topology it's given, so the drawing is only as right as the trace.
Read the screenshot carefully, write the topology JSON, then check it against the screenshot.

## What to look for

A BMS single line diagram almost always has the same bones:

- **The incoming line.** Usually enters from the left edge onto the main switchboard (`MSB-1A`,
  `MSB-2`). The board name becomes `"board"` and names the output files.
- **Feeder groups.** Each group is one outgoing feeder from the board, usually with its own
  bracket or heading on the right (`UNMETERED TENANT`, `RETAIL`, `LIFE SAFETY`). The bracket text
  becomes the group's `"name"`. It's never drawn; it just keeps the trace readable.
- **Main meter.** The meter on the feeder before it fans out (`MSB-1A-EY TENANT SB-1`,
  `MSB-1A-DB-RETAIL`, `MSB-1A ATS-3 (LIFE SAFETY)`). It goes in `"main_meter"`. When a feeder has
  no meter of its own, use `null`.
- **Branch meters.** Everything downstream of the main meter, `TDB-L05-B-P` and so on. Each
  horizontal tap off the feeder's riser is one row in `"rows"`. Meters drawn side by side on that
  tap are listed left to right in the row, even when the old BMS only drew a line to the first one.
- **Sub-boards (nested meters).** A branch meter that feeds a sub-board with meters of its own, such
  as a sub-board meter with the meters of its tenancies below it. Write that meter as
  `{"label": "...", "children": [[...], [...]]}` in place of a plain label. `children` takes rows in
  the same shape as `"rows"`: each tap off the sub-board's riser is one row, left to right. Nest as
  deep as the screenshot goes, with children inside children. `assets/example-nested.json` shows
  three levels.

## Order

- **Groups:** the group that sits on the end of the incoming line comes first. On MSB-1A that's the
  tenant feeder, top right. Then list the groups that drop off the incoming line, top to bottom. The
  renderer drops each later group further left so their lines never cross.
- **Rows:** top to bottom, as drawn.
- **Meters within a row:** left to right, as drawn.

## `join`: where the feed enters the riser

It's the row number, counting from 0, where the incoming feed meets the group's riser:

- `0` means the feed runs straight into the top row and the riser hangs down from it. MSB-1A's life
  safety group is like this.
- `2` means the feed runs straight into the third row. MSB-1A's retail group is like this, feeding
  into its middle row.
- `1.5` means the feed meets the riser between rows 2 and 3. Use a half value when a straight join
  would put the feed's junction on top of a row's junction. MSB-1A's tenant group is like this.

Leave `join` out and the renderer uses the middle. Match the screenshot where it's clear.

## Labels

- **Copy them exactly**, including case, spaces, hyphens, slashes and brackets: `LIFT 15 CARPARK
  LIFT`, `SPRINKLER/BOOSTER PUMP-1`. Stage 2 matches streams on these labels, so a "tidied" label
  matches nothing.
- **Labels split over two lines** in the screenshot (`MSB-1A-EY TENANT` / `SB-1`) are one label
  joined by a single space.
- **When a label is unreadable, ask the user.** Never guess one; a guessed label either matches the
  wrong stream or nothing at all.

## What to drop

Everything that isn't wiring or a meter: the `??? 0.00` value boxes, the grey label plates, the
board's outline box, sub-board outline boxes (`DB-Retail`), brackets, group headings and any
header, footer or navigation chrome from the BMS page.

## Check before rendering

Count the meters per group and per row in the screenshot and in the JSON, counting every level of
nesting. They must match. For MSB-1A that's 3 main meters plus 20 + 5 + 11 branch meters.
`assets/example-msb-1a.json` is the reference trace; `assets/example-nested.json` is the shape for
sub-boards.
