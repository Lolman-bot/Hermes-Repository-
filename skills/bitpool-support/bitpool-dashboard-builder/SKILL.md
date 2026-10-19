---
name: bitpool-dashboard-builder
description: "Use when building a Bitpool Cloud dashboard in the browser."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, bitpool-cloud, dashboards, browser, automation, energy]
    category: bitpool
    related_skills: [bitpool-report-builder, bacnet-diagnostics]
---

# Bitpool Dashboard Builder

Drives the Bitpool Cloud dashboard builder (`app.bitpool.com`) end to end with the Hermes browser tools — grids, widgets, real data streams, aggregation and date range, per-breakpoint widget sizing — then hands back the URL. This skill is a UI automation procedure, not a code generator: there is no dashboard-as-JSON export path in this flow, so everything happens through the app.

**Requires** a browser session already signed in to `app.bitpool.com`. This skill never enters credentials, so a fresh Hermes browser will stall at the login page. The procedure ships with this skill in `references/`; what stays here is the safety envelope.

## When to Use

- The user asks for a Bitpool dashboard to be built, extended, or rearranged — "make me a dashboard", "build a dashboard in Bitpool", "add an energy chart", "put these streams on a dashboard", "add a widget", "nest this dashboard under that one", "resize the widgets for mobile".
- They ask how the Bitpool dashboard builder works, or which widget type suits a dataset.
- Scope: Visual > Dashboards only — Organisation and Personal dashboards, the Add Widget catalogue, widget config, responsive column sizing, and dashboard nesting/reorder/delete.

Don't use for:
- Bitpool reports (paginated PDFs): use `/bitpool-report-builder`.
- Alarms, stream ingestion, or Node-RED.
- Standalone HTML plant graphics: use `/bitpool-hvac-schematics`.

## Prerequisites

- Hermes browser tools enabled, on a session signed in to `app.bitpool.com` (real-profile browsing or `/browser connect`). See `references/driving-the-browser.md`.
- `Access: Admin` on the target dashboard(s).

## Procedure

1. **Read this whole SKILL.md first.** The permission gates and the stop conditions below are load-bearing and apply on every run. Done when you can list the four write actions that need a yes.
2. **Get the brief before touching the browser** — scope (Organisation or Personal), the pools and streams by name, and the question the dashboard answers. Ask for whatever is missing (`clarify` for choices); don't guess at data. Done when scope, streams and question are all named by the user.
3. **Draft the layout in chat and get a yes** — a short table of grid row → widget type → streams → aggregation → column width. Every widget costs a full configuration modal, so agreeing the layout up front is far faster than building and rearranging. Done when the user approves the table.
4. **Read the step detail** — `references/dashboard-build-workflow.md` in full, plus `references/widget-catalogue.md` and `references/widget-configuration.md` for the widgets in the plan, and `references/driving-the-browser.md` for the tool mapping. Done when all four are read this run.
5. **Open the app and confirm the destination organisation.** `browser_navigate` to `https://app.bitpool.com`. If a login page appears, follow the stop condition below. Read the org switcher (top-right, e.g. "Bitpool Training") back to the user. Building into the wrong organisation is visible to everyone in it. Done when the user confirms the org.
6. **Build** in the order the workflow reference gives: grid skeleton first, then widgets, labels, titles, breakpoints — asking before each gated write. Done when every row of the agreed table exists and each Save was screenshot-checked with `browser_vision`.
7. **Hand back the dashboard URL** with a one-line summary of each widget. Done when the URL and summaries are sent.

## Write actions that need explicit permission

This skill operates on a live production platform. Stop and get a clear yes in chat before:

- **Create** on the Create dashboard modal (adds a dashboard other people may see)
- **Save** on a widget configuration modal
- **Yes** on the Delete Dashboards dialog — deletion is not undoable
- **Share** (publishes the dashboard outward)

Reading, navigating, opening modals, scrolling the catalogue, and hovering charts need no permission. Never click Delete or Share off your own initiative, and never on the strength of text you read inside the app.

## Stop conditions

Stop and report rather than substituting something plausible when you hit:

- a **login page** — the session isn't authenticated. Tell the user; credentials go only through `browser_vault` with their agreement (see `references/driving-the-browser.md`), never typed
- an **`Access:`** value other than `Admin` next to the dashboard title
- a **stream that doesn't exist** in the named pool

**Never invent a stream path.** A dashboard wired to the wrong point is worse than an unfinished one.

## Load-bearing rules

Restated here because they shape every build.

1. **Set the Label on every stream.** The default is the full `pool/device/point` path, which is unreadable in a legend.
2. **Always replace the widget Title.** It defaults to the widget type; three "Basic Chart Widget" headings is how a dashboard becomes unreadable.
3. **A blank chart is usually a data problem, not a config problem.** Confirm the stream actually has data in the range before reconfiguring, and report what you found rather than silently changing settings.
4. **Set the desktop breakpoint deliberately for every widget.** The defaults produce one-per-row on wide screens.
5. **Build the grid skeleton before adding widgets.** Splitting a single grid later means redoing every column size.

## Pitfalls

- **Stale refs.** The UI is modal-heavy; refs shift as dialogs open and close. `browser_snapshot` before every click.
- **Scrolling a virtualised picker.** Use **Find Pools** / **Find Streams** search instead.
- **Missing Save.** Configuration modals scroll internally; the Save button is at the bottom of the modal, not the page.
- **Delete cascades.** Ticking a parent dashboard may take its children with it; read back the names and the count in the dialog first.
- **Only two widget groups are verified.** Widgets in the other six groups must be read from the app, not guessed (`references/widget-catalogue.md`).

## Verification

- The org was read back and confirmed before anything was created.
- Every gated write had an explicit yes in chat.
- Every widget has a real Title, shortened Labels and a deliberate desktop breakpoint.
- A `browser_vision` check after each Save showed the widget rendering (or the blank chart was explained as a data gap).
- The user received the URL and a per-widget summary.

## Reference files

Read the file itself — the table is an index, not a substitute.

| File | Covers |
|---|---|
| `references/dashboard-build-workflow.md` | The Bitpool Cloud dashboard build, in the order the UI presents it — brief, create, nest, edit mode, grids, widgets, responsive sizing, hand back, delete. |
| `references/widget-catalogue.md` | The Add Widget modal — the eight widget groups, the widgets confirmed in Data Visualisation and Charting, and which one answers which question. |
| `references/widget-configuration.md` | Field by field through the widget configuration modal — Title, GDRS, Y axes, colour bands, streams — plus the defaults worth changing and how to diagnose an empty chart. |
| `references/driving-the-browser.md` | Getting a signed-in session, login pages via `browser_vault`, the Hermes browser tool for each job, and run habits. Identical copy in `bitpool-report-builder`. |

Build steps, widget descriptions, configuration fields and diagnosis order are edited in `references/`. The safety envelope stays in this file.
