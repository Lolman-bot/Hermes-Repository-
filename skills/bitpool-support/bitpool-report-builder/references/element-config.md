# Report element configuration

Every field in the report builder, what it does, and which defaults are worth changing. Configuration
is split across three places: the **Data Source modal** (report-wide stream definitions), the
**left panel** (per element), and the **right panel** (per report).

---

## Data Source modal

Reached from the right panel: **Data sources → + Add**, then click the data source name. This defines
streams *once* for the whole report; elements then select which of them to show.

### Select streams picker

- **Structured Data** toggle (top right) — off = **Unstructured Data**, the normal case for Bitpool
  stream data. Only turn it on if the user is working with a structured source.
- **Find Pools** search over the pool tree (`ASH TRAINING`, `DEMO Pool`, `Jayden Mqtt data`, …).
  Expand a pool to reveal its streams. **Use the search** — the list is long and virtualised.
- **Close** / **Add**.

### Per-stream block

Blocks are numbered and collapsible (`1. C2_GW/PM5320_110077204/Current - Ph B - Stream`), with
**↑ ↓** reorder, **duplicate**, **delete**, and **Hide** on the header row.

| Field | Default | Guidance |
|---|---|---|
| **Structured Data** | off | Leave off. |
| **Unstructured Data** | the picked stream | The stream path. The `⧉` icon beside the label opens the stream. |
| **Label** | the full path | **Always change this.** It's the legend text in the PDF. `C2_GW/PM5320_110077204/Current - Ph B - Stream` → `Phase B`. For **Table – Multi Column Matrix** the Label must use the `RowName\|ColumnHeader` pipe convention. |
| **Aggregation Type** | Average | Match the point's physics. Average for instantaneous values (power, temperature, current); Sum/Total for accumulating ones (energy, pulse counts); Min/Max for envelope reporting. Averaging an energy meter is a common and silent mistake. |
| **Series Multiplier** | `1.00` | Unit conversion or scaling — W→kW is `0.001`. Prefer fixing units at the source; a multiplier here is invisible to the reader. |
| **Offset Time** | `0` + `Hours` | Time-shift the series. For lining up against a different timezone, or overlaying last year on this year. |
| **Stream Color** | auto | Sets the series colour everywhere the stream is plotted. Set it once here rather than per element, so the same stream is the same colour on every chart in the report. |
| **Data Type** | **Source** | **Source** = raw ingested data. **Machine Learned** = Bitpool's modelled series. Reports go to customers — leave on Source unless the user explicitly asked for modelled data, and say so in a Markdown block if you do switch. |
| **Use Time Intervals** | off | Turn on when the element needs interval boundaries rather than point samples. |

Footer: **Cancel** · **Save**. Saving is permission-gated.

**Group streams into data sources deliberately.** One data source per logical group (a meter, a site, a
commodity), not one per element. Elements share them, and an element only shows the streams it has
**Enabled**.

---

## Left panel — per element

Appears when an element is selected, headed by the element name and its one-line description. Four
collapsible sections.

### Size

| Field | Default | Guidance |
|---|---|---|
| **Width** | `12/12 (100%)` | Page width as a twelfth, `1/12 (~8%)` … `12/12 (100%)`. Two side by side = `6/12` each; three = `4/12`. There are no device breakpoints — a report renders to one page width. |

### Space

Padding and margin around the element. Leave at defaults unless elements are visually colliding; the
page already has consistent spacing and ad-hoc adjustments make a report look uneven.

### Data

| Field | Guidance |
|---|---|
| **Data source** | Dropdown of the report's data sources. Pick the one holding this element's streams. |
| **Streams** | Every stream in that data source, each with an **Enabled** toggle, plus **Select all** / **Deselect all**. This is the mechanism for showing different subsets of one data source in different elements. |
| **Series stacked type** | Per stream: **Column · Column 2 · Line · Area · Scatter**. Mixing is supported and is how you overlay — columns for consumption, a line for temperature. **Column 2** is a second column group, for side-by-side rather than stacked bars. |
| **Y Axis** | Free-text axis name per stream. Streams sharing a name share an axis; a distinct name creates a second axis. **The text is printed as the axis label — put the unit there** (`kWh`, `V`, `°C`). Leaving it blank gives an unlabelled axis of raw floats, which is the single most common way a Bitpool report ends up unreadable. |
| **State Name Converters** | **String chart** only. **+ Add** maps raw state values to display names (`0` → `Off`, `1` → `Occupied`). |

### Parameters

| Field | Default | Guidance |
|---|---|---|
| **Title** | empty | Prints above the element. Set it on every element. An untitled chart in a PDF has no context at all — there's no hover, no sidebar, nothing but the picture. |
| **Border** | on | Border around the element. |
| **Border color** | `#D4D4D4` | Leave it. Consistent borders are what make the page look like one document. |
| **Background color range** | none | **+ Add** threshold colour bands behind the plot — e.g. shade the comfort band on a temperature chart. Powerful for exception reporting; state the thresholds in a Markdown block so the reader knows what the shading means. |
| **Height** | `450.00` | Pixel height. **This is real page height** — budget it. Three 450px charts will not fit one page. Confirm with **Preview PDF**, not the canvas. |
| **Total Values** | on (charts) | *"Make the numbers at the side of the columns"* — prints the value beside each bar/point. Useful on sparse charts, unreadable on dense ones. Turn it off when you have more than ~30 points. |
| **Decimal Places** | `2.00` | Applies to printed values. Energy in kWh rarely needs 2dp; current in amps might. Raw float noise (`0.010937500000000001`) means this isn't taking effect where you expected. |
| **Units** | empty | A suffix appended to every printed value — `V` turns `0.01` into `0.01 V`. **Nothing validates this against the stream.** The builder will happily print `V` on a kWh axis. Check the point before you set it. |

---

## Right panel — per report

| Section | Contents |
|---|---|
| **General** | The report **Name**. Same value as the wizard, editable here. |
| **Schedule** | Attach or detach a schedule (defined on Report Manager's Schedules tab). **Permission-gated** — a schedule causes the report to be generated and distributed on a recurrence. |
| **Report date range** | The period the whole report covers. Set once here; elements inherit it. Prefer a rolling range (last month, last 7 days) for scheduled reports and a fixed range for one-offs — a scheduled report on a fixed range sends the same PDF forever. |
| **Data sources** | **+ Add**, then the list (`Data source 1`, `Data source 2`, …) with a `⋮` per row. |
| **Template** | Save this report's layout as a reusable template, or apply one. Worth doing once a layout has been reviewed and approved — it's how the org stops rebuilding the same report per site. |
| **Delete report** | Red, bottom of the panel. Not undoable. Permission-gated. |

---

## Top bar

| Control | Notes |
|---|---|
| **← Back to Report Manager** | Leaves the builder. Save first — it does not prompt. |
| **Edit / Preview** | Preview re-renders without edit chrome. Shows a spinner while regenerating; wait for it. |
| **Preview PDF** | The real paginated output. **Check this before handing back, every time.** The canvas does not show pagination, so heights that look fine inline can push content onto a second page. |
| **Save** | Raises a green *"Reports — Changes saved"* toast. Greys out when there is nothing pending — that's your confirmation the canvas is clean. Permission-gated. |
