# Widget Configuration

Field-by-field for the widget configuration modal (titled after the widget, e.g. *Basic Chart Configuration*). Sections appear in this order; the modal scrolls internally, and **Close** / **Save** are pinned to the footer.

## Title

Free text. Defaults to the widget type — `Basic Chart Widget`. **Always replace it.** Three widgets all called "Basic Chart Widget" is the single most common way a Bitpool dashboard becomes unreadable.

## GDRS

**GDRS = Global Date Range Setpoint** — the dashboard-wide date range every widget inherits by default.

| Field | Behaviour |
|---|---|
| **Use Global Date Range Setpoint (GDRS)** | On (default) = follow the dashboard's range; the widget header shows the inherited range, e.g. "Rolling Month". Off = this widget uses its own Date Range / Start / End below. |
| **Display Data Gaps** | On (default) = missing intervals render as gaps. Leave on — turning it off makes an offline device look like flat valid data. |
| **Aggregation Period** | `Auto` by default: interval chosen from the range. Set explicitly (hourly/daily/…) when you need bar-per-day regardless of zoom. |
| **Date Range** | Preset picker — `Today`, `Rolling Month`, etc. |
| **Start Date** / **End date** | `dd/mm/yyyy HH:mm`. Only meaningful for a custom range. |

The widget header also carries a GDRS toggle, so the user can override the range on the live dashboard without opening this modal.

## Y Axis (Units)

A `+` button adds a row with a **Y Axis Name** field and a delete (bin) button.

Add an axis here **before** configuring streams — the per-stream **Y-Axis** dropdown can only pick from axes that already exist. Two axes are what you want any time units differ (kWh on the left, °C or kW on the right); one axis forces unrelated magnitudes onto the same scale and flattens the smaller series into the baseline.

## Background Color Range

`+` adds a threshold colour band behind the plot. Use for comfort bands, target zones, or alarm/warning/OK shading. Optional, and usually worth skipping on a first build.

## Streams

Header controls: **+ Single** · **+ Multiple** · **Delete All**.

- **+ Single** adds one empty stream block to configure by hand.
- **+ Multiple** adds several at once from the picker — much faster for "all three phases", but it auto-labels and auto-colours everything, so you still pass through each block to fix labels.

Each block is titled `N. Stream` with: **↑ ↓** (reorder — controls legend and stacking order), **duplicate**, **delete**, and **Hide** (collapse).

### Stream fields

| Field | Notes |
|---|---|
| **Structured Data** toggle | Off by default → the **Unstructured Data** picker below. Leave off for ordinary time-series points. |
| **Unstructured Data** / **Select Stream** | Dropdown → **Find Pools** search → expand a pool (`ASH TRAINING`, `DEMO Pool`, `CSV_TEST`, …) → **Find Streams** search + **Select All** / **Deselect** → stream list. Stream paths read `device/point`, e.g. `C2_GW/PM5320_110077204/Active Energy Delvd`. Use the search boxes — the list is long and virtualised. |
| **Label** | Auto-fills with the full stream path. **Shorten it** — "Active Energy Delivered" not `C2_GW/PM5320_110077204/Active Energy Delvd`. This is the legend text. |
| **Aggregation Type** | `Average` by default. Wrong default for meters: cumulative/consumption points want a sum or delta, not an average. Match it to the point's nature. |
| **Series Type** | `Column` by default. Column for interval consumption, Line for continuous measurements (power, temperature), Area for cumulative. Set per stream, so one chart can mix columns and an overlaid line. |
| **Series Multiplier** | `1.00`. Unit conversion (Wh→kWh = 0.001) or sign flip (−1 for export). |
| **Y-Axis** | Empty by default. Assign to one of the axes defined in **Y Axis (Units)**. |
| **Offset Time** | Value + unit (`Hours`). Shifts the series along the time axis — for last-year overlays or timezone correction. |
| **Stream Color** | Colour swatch. Auto-assigned, and the auto colours are arbitrary (the recording produced olive, green, and salmon in sequence). Set these deliberately, and keep the same stream the same colour across every widget on the dashboard. |
| **Data Type** | **Source** (default, raw as ingested) / **Machine Learned** (Bitpool's modelled series). Use Source unless the user explicitly wants the modelled values. |
| **Use Time Intervals** | Off by default. Turn on for interval-bucketed rather than raw-timestamp plotting. |

## Footer

- **Close** — discards. Nothing is written.
- **Save** — writes the widget.

> **Warning**
> **Get explicit permission before clicking Save.** It writes to a live production dashboard. See the permission gates on [Dashboard Build Workflow](dashboard-build-workflow.md).


## Diagnosing an empty chart after Save

A widget that saves cleanly but renders a flat, empty axis is almost always a *data* problem, not a config problem. Check in this order:

#### Hover a neighbouring chart that does plot

Confirm the range genuinely contains data.

#### Does the stream have data in this range?

Widen Date Range to a year. In the recording, `Active Energy Rcvd` was empty over a rolling month while `Active Energy Delvd` on identical settings plotted ~330 per day — the point simply wasn't logging.

#### Aggregation Type vs point type

Averaging a monotonically increasing meter total can flatten it.

#### Series Multiplier

A stray `0` zeroes the series.

#### Y-Axis assignment

A series on an axis scaled by a much larger series looks like a flat line at zero. Check the axis numbers — e.g. a `0.009` max next to a `350` max.

Report what you found rather than silently reconfiguring — an empty stream is information the user needs.
