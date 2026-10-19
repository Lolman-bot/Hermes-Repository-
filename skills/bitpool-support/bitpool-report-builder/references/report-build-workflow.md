# Report build workflow

The Bitpool Cloud report build, in the order the UI presents it: Report Manager, the New Report
wizard, the builder's three panes, the canvas skeleton, elements, data sources, wiring, report-level
settings, preview and hand back, deleting. The permission gates in `SKILL.md` apply at every step;
the browser mechanics are in `driving-the-browser.md`.

## The UI, in the order you'll use it

Left rail: **AI · Visual · Core · Notifications · Manage · Feedback · Support**. Under **Visual** the
sidebar lists **Dashboards · Reports · Presentations**. Reports is the one you want.

### 1. Report Manager

`Visual > Reports` opens **Report Manager**, with four tabs:

| Tab | What lives there |
|---|---|
| **Reports** | Every report in the org — Name, Created, Modified, and a per-row `⋮` menu. A **Search Report** box filters by name. |
| **Schedules** | Named recurrences (e.g. "Ash's Schedule", "AWESOME MONTHLY REPORT SCHEDULE") that reports attach to. |
| **Templates** | Saved report templates that new reports can be built **From template**. |
| **Elements** | The element library backing the *Add an element* catalogue. |

Top right: **+ Add Report** and **Backup & restore**.

**Before creating anything, search the Reports list for a report that already does this job.** The list
is long and full of near-duplicates; extending an existing report is usually what the user actually
wants. Ask if you find a close match.

### 2. The New Report wizard

**+ Add Report** opens a three-step modal with a progress bar: **Report type → Report name → Schedule**.

1. **Report type** — *"What type of report are you creating?"*
   - **Custom** — a blank canvas. The default path.
   - **From template** — start from a saved template on the Templates tab. Use when the user names a
     template, or when the org clearly has a house layout for this report type.
   - **Skip** jumps past the wizard with defaults; **Next** advances. Prefer Next — the wizard is short
     and skipping just means setting the same fields later from the right panel.
2. **Report name** — *"Name your report"*. One text field. Names appear verbatim in the Reports list and
   on generated PDFs, so use something a recipient would recognise: site, subject, period
   (`Delta Canberra — Monthly Energy — 2026`), not `test 3`.
3. **Schedule** — *"Create or choose a report schedule"*. A multi-select dropdown of existing schedules
   with a search box. **Leave this empty unless the user explicitly asked for a schedule** — see the
   permission list. **Back** / **Create**.

**Create** opens the **Report Builder** on the new report.

### 3. The Report Builder layout

Three panes:

- **Left — contextual settings.** Changes with whatever is selected on the canvas. Selecting the page
  body gives **Layout**; a grid gives **Size**; an element gives the element's name, a one-line
  description, and **Size · Space · Data · Parameters**.
- **Centre — the page canvas.** A literal page preview: **header band** (Bitpool logo, year), the body,
  and a **footer** (*Powered by Bitpool*, `Page 1 of 1`).
- **Right — report settings.** Collapsible sections: **General** (Name), **Schedule**,
  **Report date range**, **Data sources**, **Template**. **Delete report** sits at the bottom in red.

Top bar: **← Back to Report Manager** · **Edit / Preview** toggle · **Preview PDF** · **Save**.
Saving raises a green *"Reports — Changes saved"* toast. **Save** greys out when there is nothing
pending — that's your confirmation the canvas is clean.

### 4. Build the canvas skeleton

The canvas nests three levels deep, each with its own hover toolbar and its own coloured selection
outline:

```
Grid (grey bar)          ← a page row
└── Container (purple bar)  ← a cell within the row
    └── Element (blue bar)     ← the actual chart/table
```

Each bar carries: a **+** to add a sibling at that level, a **+ [grid icon] Add Element**, a **trash**
(element/container level), and **⋯ More Actions**. Hover to reveal them; the tooltips name them.

Build the skeleton first — one grid per row of the agreed layout — then fill each grid. Adding elements
into one unplanned grid and splitting later means redoing widths.

**Width** is set on the left panel under **Size → Width**, as a twelfth: `12/12 (100%)` down to
`1/12 (~8%)`. Two elements side by side = `6/12` each. Three = `4/12`. Unlike dashboards there are no
device breakpoints — a report renders to one page width.

### 5. Add an element

The **Add Element** control (on any grid or container bar) opens the **Add an element** modal: a
searchable grid of element cards, each with a title and a one-line description. There are no groups —
use the **Search** box when you know the name, and scroll otherwise.

See `element-catalogue.md` for the elements confirmed in the catalogue and which to pick for
a given question.

A newly added element renders **"No data"** — expected, not an error. It has no streams yet.

### 6. Define the data sources

Right panel → **Data sources** → **+ Add** creates `Data source 1`. Each row has a `⋮` menu; clicking
the name opens the **Data Source** modal.

Inside the modal, streams are numbered collapsible blocks (`1. C2_GW/PM5320_110077204/Current - Ph B -
Stream`). Add streams through the **Select streams** picker: a **Find Pools** search over the pool tree
(`ASH TRAINING`, `DEMO Pool`, `Jayden Mqtt data`, …); expand a pool, tick streams, **Add**. A
**Structured Data** toggle at the top switches the picker to structured sources — leave it off for
normal stream data.

Each stream block carries **↑ ↓** (reorder), **duplicate**, **delete**, and **Hide**, plus:

- **Structured Data** toggle (off = **Unstructured Data**, the normal case)
- **Unstructured Data** — the stream path
- **Label** — auto-fills with the full path. **Always shorten it.** The raw
  `C2_GW/PM5320_110077204/Current - Ph B - Stream` is unreadable in a PDF legend; `Phase B` is not.
- **Aggregation Type** (Average, …) · **Series Multiplier** (`1.00`) · **Offset Time** (value + Hours)
- **Stream Color** — the swatch drives the series colour everywhere the stream is plotted
- **Data Type** — **Source** / **Machine Learned**
- **Use Time Intervals** toggle

Footer: **Cancel** · **Save**.

Field-by-field guidance and the defaults worth changing are in `element-config.md`.

### 7. Wire the element to data

Select the element, then the left panel's four sections:

**Data**
- **Data source** dropdown — pick one of the data sources you defined.
- **Streams** — every stream in that data source, each with an **Enabled** toggle, plus
  **Select all** / **Deselect all**. This is how one shared data source feeds several elements showing
  different subsets: enable Phase A/B/C on the stacked chart, enable only Phase C on the flowchart.
- **Series stacked type** — per stream: **Column · Column 2 · Line · Area · Scatter**. Mixing types on
  one chart is supported and is how you overlay (e.g. columns for consumption, line for temperature).
- **Y Axis** — a free-text axis name per stream. Streams sharing a name share an axis; a distinct name
  creates a second axis. The text is what gets printed as the axis label, so put the unit there
  (`kWh`, `V`), not a placeholder.
- **State Name Converters** (String chart only) — **+ Add** to map raw state values to display names.

**Parameters** — presentation. **Title** (prints above the chart), **Border** toggle + **Border color**
(`#D4D4D4`), **Background color range** (**+ Add** threshold bands), **Height** in px (`450.00` default
— this is real page height, budget it against the page), **Total Values** toggle (*"Make the numbers at
the side of the columns"*), **Decimal Places** (`2.00`), **Units** (a suffix appended to every printed
value — `V` turns `0.01` into `0.01 V`).

**Size** — **Width** as a twelfth (above). **Space** — padding/margin around the element.

### 8. Report-level settings

Right panel:

- **General** — the report **Name** (same value as the wizard; editable here).
- **Report date range** — the period the whole report covers. Set this once at report level rather than
  per element; elements inherit it.
- **Schedule** — attach/detach a schedule. Permission-gated (see above).
- **Template** — save this report's layout as a reusable template, or apply one.

### 9. Preview and hand back

1. Flip the top-bar toggle to **Preview** — the canvas re-renders without the edit chrome. It shows a
   spinner while regenerating; wait for it.
2. **Preview PDF** for the real paginated output. **Check this before handing back**, every time. The
   canvas lies about pagination: an element with `Height: 500` that looked fine inline can push the
   footer onto a second page.
3. Sanity-check: every element has a real **Title**, a readable legend (shortened labels, not raw
   paths), plotted data, and a Y axis with units.
4. **Save**, and confirm the green *"Changes saved"* toast.
5. Give the user the report name, its URL, and a one-line summary per element (type, streams, range).

### 10. Deleting

**Delete report** at the bottom of the right panel removes the whole report. Elements, containers, and
grids each have their own trash icon on the hover bar.

Get an explicit yes in chat first and read back the exact report name. Deleting a grid takes its
containers and elements with it.

## Failure modes worth knowing

- **"No data" on a fresh element** — normal. It has no data source selected yet.
- **A chart renders but is flat/empty** — usually the stream has no data in the report date range, not
  a broken config. Hover a point to read the tooltip
  (`Wednesday 29 July 2026 · …Current - Ph A - Stream: 0.010937500000000001`) and confirm data is
  actually landing before hunting for a config fault.
- **An unreadable wall of Y-axis numbers** — the axis is auto-scaling over raw float values with no
  axis name set. Set the **Y Axis** text and **Decimal Places**.
- **Values with no unit** — set **Units** in Parameters; it suffixes every printed value.
- **Legend full of `pool/device/point` paths** — you skipped **Label** in the Data Source modal.
- **Units that contradict the data** — the builder will happily print `V` on a `kWh` axis. Nothing
  validates this. Check the unit matches the point before you set it.
