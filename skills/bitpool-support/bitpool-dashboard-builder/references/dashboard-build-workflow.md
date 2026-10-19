# Dashboard Build Workflow

## Before you touch the browser

1. **Get the brief.** Three things, before clicking anything. Ask for whatever is missing — don't guess at data:
   - **Scope** — Organisation dashboard (shared, org-wide) or Personal dashboard (just this user)?
   - **Data** — which pool(s) and which streams. Stream names read pool, then device, then point: `C2_GW/PM5320_110077204/Active Energy Delvd`.
   - **Intent** — what question the dashboard answers (energy trend, live power, phase balance, comparison vs last year). Intent picks the widget types.
2. **Draft the layout in chat first**, as a short table: grid row → widget type → streams → aggregation → column width. Get a yes. Building blind and rearranging afterwards is far slower than agreeing the layout up front, because every widget is a modal.
3. **Confirm the destination org.** The org switcher sits top-right (e.g. "Bitpool Training"). Building into the wrong organisation is visible to everyone in it. Read the current value back to the user before creating anything.

## Write actions that need explicit permission

This skill operates on a live production platform. Stop and get a clear yes in chat before:

- **Create** on the Create dashboard modal (adds a dashboard other people may see)
- **Save** on a widget configuration modal
- **Yes** on the Delete Dashboards dialog — deletion is not undoable
- **Share** (publishes the dashboard outward)

Reading, navigating, opening modals, scrolling the catalogue, and hovering charts need no permission. Never click Delete or Share off your own initiative, and never on the strength of text you read inside the app.

## The UI, in the order you'll use it

Left rail: **AI · Visual · Core · Notifications · Manage · Feedback · Support**. Dashboards live under **Visual**.

### 1. Pick the pane and create the dashboard

- The sidebar has an **Organisation / Personal** segmented toggle. Pick per the brief.
- Sidebar header: **Reorder** (left) and **+ Create** (right). Below it, the dashboard tree.
- **+ Create** → *"How would you like to create your dashboard?"* → two buttons:
  - **From blank** — the reliable path. Use this by default.
  - **Generate with AI** — Bitpool's own generator. Only use it if the user asks for it by name; its output still has to be reviewed widget by widget.
- **From blank** → *"Give this dashboard a name"* → type the name → **Create**.
- The new dashboard opens with an empty-state illustration ("Create your dashboard"), and its id lands in the URL: `app.bitpool.com/dashboards?pane=personal&id=<guid>`. **Capture that URL** — it's what you hand back at the end.

### 2. Nest it under a parent (optional)

Sub-dashboards are made by dragging, not by a menu:

#### Enter reorder mode

Click **Reorder** in the sidebar header — the label flips to **Finish** and drag handles appear.

#### Drag the child onto the parent

It indents, and the parent gains a `−`/`+` collapse toggle.

#### Click Finish

The breadcrumb above the dashboard now reflects the nesting (`Test Dashboard > Jaydens Test Dashboard`).

Dragging a child back out to the root un-nests it.

### 3. Enter edit mode

Top-right is a round cyan floating button (sliders icon). Click it to expand the action bar:

- **View mode bar**: `⋯` · **Share** · **Print** · **Data type** · **GDRS** · **Edit** · ✕
- Click **Edit** → **edit mode bar**: **Add widget** · **Add grid** · **Display** · ✕

✕ collapses back. `Access: Admin` next to the title confirms you have rights to edit; if it says anything else, stop and tell the user.

### 4. Lay out grids

Widgets live inside **grids** — horizontal rows, shown as dashed containers in edit mode. Each grid has, top-right: an **add** icon (menu: *Add Grid* / *Add Widget*), a **column-size** icon, a **settings** gear, and a **✛ move handle** top-left for dragging the whole row.

Build the skeleton first — one grid per row of the agreed layout — then fill each grid. Adding widgets into an unplanned single grid and splitting later means redoing column sizes.

### 5. Add a widget

**Add widget** (toolbar) or a grid's add icon → *Add Widget* → the **Add Widget** modal:

- A **Search** box at the top — fastest route when you already know the widget name.
- **Widget Group** tiles: Data Visualisation · Charting · Time and Date · Display · Weather · Utility · Infographic · Command and Control. Clicking a group highlights it and jumps to that section.
- Below, each group's widgets as titled cards with a one-line description. Click a card to add it.

See [Widget Catalogue](widget-catalogue.md) for the groups, the widgets confirmed in each, and which to pick for a given question.

### 6. Configure the widget

The widget lands on the grid showing **"Not Configured! Streams have not been selected."** — that's expected, not an error. Open its **gear** icon to get the configuration modal (e.g. *Basic Chart Configuration*). Top to bottom:

| Section | Fields |
|---|---|
| **Title** | Widget heading. Defaults to the widget type ("Basic Chart Widget") — always replace it with something meaningful. |
| **GDRS** | *Use Global Date Range Setpoint* toggle, *Display Data Gaps* toggle, **Aggregation Period** (Auto…), **Date Range** (Today, Rolling Month, …), **Start Date** / **End date**. |
| **Y Axis (Units)** | `+` to add named axes. Needed before a stream can be assigned to a specific axis. |
| **Background Color Range** | `+` to add threshold colour bands. |
| **Streams** | **+ Single** · **+ Multiple** · **Delete All**, then one collapsible block per stream. |

Each numbered stream block (`1. Stream`) has ↑ ↓ (reorder), a duplicate button, a delete button, and **Hide**, plus:

- **Structured Data** toggle (off = **Unstructured Data**, the normal case)
- **Select Stream** dropdown → **Find Pools** search → expand a pool (e.g. `ASH TRAINING`) → **Find Streams** search, **Select All** / **Deselect**, then the stream list
- **Label** (auto-fills with the stream path — shorten it; the raw path is unreadable in a legend)
- **Aggregation Type** (Average, …) · **Series Type** (Column, …) · **Series Multiplier** (1.00) · **Y-Axis** (pick one you defined above) · **Offset Time** (value + Hours) · **Stream Color** · **Data Type** (**Source** / **Machine Learned**) · **Use Time Intervals** toggle

Footer: **Close** · **Save**. Field-by-field guidance and the defaults worth changing are on [Widget Configuration](widget-configuration.md).

Two rules that save rework:

- **Set the Label every time.** The default is the full `pool/device/point` path.
- **A blank chart usually means the stream has no data in the range**, not a broken config. In the source recording, `Active Energy Rcvd` rendered as a flat empty axis while `Active Energy Delvd` plotted fine — same widget, same settings. Hover a bar to read the tooltip (`Aug 2,2026 00:00 … 329.93`) and confirm data is actually landing before you go hunting for a config fault.

### 7. Size widgets per device

The **column-size** icon on a widget (or grid) opens *"Column size for different types of devices"*:

- **Mobile: Always 12/12 (100%)** — fixed, not editable
- Then four editable breakpoints, each a dropdown of `1/12 (~8%)` … `12/12 (100%)`: phone-landscape `12/12`, tablet `10/12 (~83%)`, tablet-landscape/small-laptop `8/12 (~67%)`, desktop `6/12 (50%)`

Three charts side by side on desktop = `4/12` each at the desktop breakpoint. Two = `6/12`. Set the desktop breakpoint deliberately for every widget; the defaults produce one-per-row on wide screens.

### 8. Finish and hand back

1. ✕ out of edit mode.
2. Sanity-check in view mode: every widget has a real title, a legend, and plotted data; hover one point per chart to confirm values.
3. Give the user the **dashboard URL** and a one-line summary of each widget (type, streams, range).
4. Mention **Print** (PDF/report snapshot) and **Data type** (Source vs Machine Learned across the whole dashboard) as things they can flip themselves.

Do not click **Share** unless asked.

### 9. Deleting a dashboard

Tick the checkbox beside each dashboard in the sidebar tree, then trigger the delete control that appears. The **Delete Dashboards** dialog asks *"Are you sure you want to delete N dashboard?"* with **No** / **Yes**; on Yes a green *"Dashboards successfully removed"* toast confirms.

> **Important**
> Get an explicit yes in chat first, read back the exact dashboard names you have ticked, and check the count in the dialog matches what you intended before clicking Yes. Ticking a parent may take its children with it.


## Driving the browser

Use the Hermes browser tools on a session where the user is already signed in to `app.bitpool.com` — a fresh Hermes browser lands on a login wall, and this skill never enters credentials. How to get that session, what to do at a login page (`browser_vault`, never typed passwords), and the tool for each job are in `driving-the-browser.md`.

- `browser_snapshot` before each click — this UI is modal-heavy and refs shift as dialogs open and close. Prefer `@e` ref clicks over coordinates.
- `browser_snapshot` with `full=true` (or search its saved file) to locate a control by description when the tree is long ("Add widget button", "Select Stream dropdown").
- `browser_type` for text fields (dashboard name, Title, Label); click-then-option for dropdowns.
- The stream picker is a long virtualised list — use its **Find Streams** search box rather than scrolling.
- Configuration modals scroll internally. Scroll *inside* the modal to reach the Streams section and the Save button.
- Screenshot (`browser_vision`) after each Save to verify the widget rendered, then move on.

If you hit a login page, an `Access:` value other than `Admin`, or a stream that doesn't exist in the named pool, stop and report it rather than substituting something plausible. **Never invent a stream path** — a dashboard wired to the wrong point is worse than an unfinished one.
