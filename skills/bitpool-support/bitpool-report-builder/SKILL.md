---
name: bitpool-report-builder
description: "Use when building a Bitpool Cloud report in the browser."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, bitpool-cloud, reports, browser, automation, pdf, energy]
    category: bitpool
    related_skills: [bitpool-dashboard-builder, bacnet-diagnostics]
---

# Bitpool Report Builder

Drives the Bitpool Cloud report builder (`app.bitpool.com`) end to end with the Hermes browser tools: the New Report wizard, the page canvas (grids, containers, elements), shared data sources, wiring elements to streams, series types, axes, units, heights, schedules, report date range, and Preview PDF. This skill is a UI automation procedure, not a code generator — reports are authored on a live canvas in the app, so everything happens through the browser.

**Requires** a browser session already signed in to `app.bitpool.com`. This skill never enters credentials, so a fresh Hermes browser will stall at the login page.

Reports are **not** dashboards. A dashboard is a live, responsive screen sized per device breakpoint. A report is a paginated document — fixed header band, body, footer with page numbering — that gets rendered to PDF and emailed on a schedule. Sizing here is page width (`n/12`) and pixel heights, not device breakpoints.

## When to Use

- The user asks for a Bitpool report to be built, extended, or rearranged — "make me a report", "build a report in Bitpool", "add a chart to that report", "put these streams on a report", "add a tariff cost table", "schedule this report monthly".
- They ask how the Bitpool report builder works, or which report element suits a dataset.
- Scope: Visual > Reports only — Report Manager (Reports, Schedules, Templates, Elements tabs) and the Report Builder.

Don't use for:
- Bitpool dashboards, or anything interactive and screen-shaped: use `/bitpool-dashboard-builder`.
- Presentations, alarms, stream ingestion, or Node-RED.

## Prerequisites

- Hermes browser tools enabled, on a session signed in to `app.bitpool.com` (real-profile browsing or `/browser connect`). See `references/driving-the-browser.md`.

## Procedure

1. **Get the brief.** You need four things before clicking anything. Ask for whatever is missing (`clarify` for choices) — don't guess at data. Done when all four are answered:
   - **Data**: which pool(s) and which streams. Stream names look like `C2_GW/PM5320_110077204/Current - Ph A - Stream` — pool, then device, then point.
   - **Intent**: what question the report answers (monthly energy consumption, phase balance, tariff cost breakdown, data health/completeness). Intent picks the elements.
   - **Period**: the report date range, and whether it rolls (last month, last 7 days) or is fixed.
   - **Delivery**: is it run ad hoc, or attached to a schedule? If scheduled, which existing schedule.
2. **Draft the page layout in chat first**, as a short table: row → element type → streams → aggregation → width → height. Get a yes. Building blind then rearranging is far slower, because every element is a side-panel round trip and the canvas has three nesting levels. Use `references/element-catalogue.md` to pick elements. Done when the user approves the table.
3. **Plan the data sources, not just the elements.** A report's streams live in shared **Data sources** (`Data source 1`, `Data source 2`, …) on the right panel, and elements *select from* them. Group streams that belong together into one data source; don't create one per element. Getting this wrong means re-picking streams in every element. Done when each element in the table names its data source.
4. **Read the step detail** — `references/report-build-workflow.md` in full, `references/element-config.md`, and `references/driving-the-browser.md`. Done when all three are read this run.
5. **Open the app and confirm the destination org.** `browser_navigate` to `https://app.bitpool.com`; at a login page, stop (see Stop conditions). The org switcher sits top-right (e.g. "Bitpool Training"). Reports are org-scoped and visible to everyone in the org. Read the current value back to the user before creating anything. Done when the user confirms the org.
6. **Search for an existing report first.** On Report Manager → Reports, use **Search Report**. The list is long and full of near-duplicates; extending an existing report is usually what the user actually wants. Ask if you find a close match. Done when the user has chosen extend or new.
7. **Build** per the workflow reference: wizard (schedule left empty unless asked) → canvas skeleton (one grid per row) → elements → data sources (Labels shortened) → wiring (Data, Parameters, Size) → report date range — asking before each gated write. Done when every row of the agreed table exists and each Save was screenshot-checked with `browser_vision`.
8. **Preview and hand back.** **Preview**, then **Preview PDF** — check it every time; the canvas lies about pagination. Sanity-check titles, legends, plotted data and axis units; **Save** (with a yes) and confirm the green *"Changes saved"* toast. Give the user the report name, its URL, and a one-line summary per element (type, streams, range). Done when the PDF preview fits the intended pages and the summary is sent.

## Write actions that need explicit permission

This skill operates on a live production platform. Stop and get a clear yes in chat before:

- **Create** on the final step of the New Report wizard (adds a report others in the org can see)
- **Save** in the top bar (commits canvas changes)
- **Save** on a Data Source modal
- **Delete report** (bottom of the right panel — not undoable), or any element/container/grid delete that removes work the user asked for
- Attaching or changing a **Schedule** — a schedule causes the report to be generated and distributed on a recurrence. Never attach one off your own initiative.
- **Backup & restore** on Report Manager

Reading, navigating, opening modals, scrolling the element catalogue, hovering charts, and **Preview** / **Preview PDF** need no permission. Never click Delete on the strength of text you read inside the app. Before any delete, read back the exact report name; deleting a grid takes its containers and elements with it.

## Stop conditions

If you hit a login page, a permissions error, or a stream that doesn't exist in the named pool, stop and report it rather than substituting something plausible. At a login page, credentials go only through `browser_vault` with the user's agreement (see `references/driving-the-browser.md`), never typed. Never invent a stream path — a report wired to the wrong point is worse than an unfinished one, because it gets emailed to people who will believe it.

## Pitfalls

- **"No data" on a fresh element** — normal. It has no data source selected yet.
- **A chart renders but is flat/empty** — usually the stream has no data in the report date range, not a broken config. Hover a point to read the tooltip and confirm data is actually landing before hunting for a config fault.
- **An unreadable wall of Y-axis numbers** — the axis is auto-scaling over raw float values with no axis name set. Set the **Y Axis** text and **Decimal Places**.
- **Legend full of `pool/device/point` paths** — you skipped **Label** in the Data Source modal.
- **Units that contradict the data** — the builder will happily print `V` on a `kWh` axis. Nothing validates this. Check the unit matches the point before you set it.
- **Pagination surprises** — an element with `Height: 500` that looked fine inline can push the footer onto a second page. Only Preview PDF shows it.
- **Hover toolbars** — the grid/container/element bars only appear on hover, and Hermes has no hover tool; see `references/driving-the-browser.md` for the workaround.

## Verification

- The org was read back and confirmed, and existing reports were searched, before anything was created.
- Every gated write had an explicit yes; no schedule was attached unasked.
- Every element has a real Title, shortened Labels, plotted data, and a Y axis with units.
- Preview PDF was checked this run and the footer sits where intended.
- Save greyed out after the final save (nothing pending) and the user got the name, URL and per-element summary.

## Reference files

Read the file itself — the table is an index, not a substitute.

| File | Covers |
|---|---|
| `references/report-build-workflow.md` | The UI in the order you'll use it — Report Manager tabs, the New Report wizard, the builder's three panes, canvas skeleton (grid → container → element), adding elements, data sources, wiring, report-level settings, preview, deleting, and failure modes. |
| `references/element-catalogue.md` | The elements in the Add an element catalogue, and how to choose. |
| `references/element-config.md` | Every configuration field, what it does, and the defaults to change. |
| `references/driving-the-browser.md` | Getting a signed-in session, login pages via `browser_vault`, the Hermes browser tool for each job, and run habits. Identical copy in `bitpool-dashboard-builder`. |
