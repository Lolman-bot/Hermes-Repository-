# Product source — bitpool.com/product

**Canonical source of truth for what Bitpool does and how it looks.**
Always `web_fetch https://www.bitpool.com/product` at the start of a case study and
ground the **Solution** page and **Strategic Value** points in the *current* capability
set and language on that page. Never describe a capability the platform doesn't have, and
never invent product names — the live page is authoritative and may have changed since
this file was written.

## Why fetch every time
The product page is the only place the capability set, the integration list, and the
on-brand product language stay current. Pulling it each run keeps case studies honest
(no stale or invented features) and consistent with the website a reader will visit next.

## Workflow
1. `web_fetch https://www.bitpool.com/product`.
2. Map the client's project onto the **real** capabilities below — use them for the four
   Solution items and the Strategic-Value bullets. Prefer the platform's own phrasing.
3. For each Solution item and the Outcome dashboard, reach for a matching **infographic
   concept** below rather than a generic stock render where the story is about the
   product itself (a dashboard, a report, a data-quality score, an AI agent at work).
4. If the fetch fails, fall back to the snapshot below and note in delivery that product
   detail couldn't be refreshed live.

## Capability set (snapshot — verify live)
- **Connect anything in ~5 minutes** — 20+ BMS/protocol integrations. Providers:
  Distech, Tridium, Schneider, Delta, Johnson Controls, Trend, Honeywell, Siemens,
  Alerton, KNX. Connectors: BACnet, Modbus, MQTT, OPC UA, Webhooks, API keys, flat/CSV
  files, email import. Subsystems: water, gas, solar, electricity, security, lighting,
  fire, HVAC, waste, occupancy, lifts. Certifications: BREEAM, LEED, GRESB, NABERS.
- **Smart Digital Canopy** — digitise affordably without costly retrofits.
- **Semantic modelling** — gives data context, clarity, and meaning.
- **Data integrity / quality scoring** — composite score across completeness, accuracy,
  uniqueness; Data Quality Rating over time; full audit log; Poor→Excellent score bands;
  stream- and pool-level visibility.
- **Data at scale** — pools, streams, and ML processing across a portfolio; tens of
  billions of records with real-time quality monitoring.
- **AI agents (specialist)** — Energy & Sustainability, Data-Driven Insights, Asset &
  Infrastructure; configured with natural-language instructions.
- **Task creation in four clicks** — name, agent, schedule, sources; no code. Tasks
  report time saved per task; live on mobile with push notifications.
- **Schedule & visibility** — calendar/grid view of every AI task.
- **AI workspaces** — each task is a persistent workspace with conversation history,
  linked data, and agents that remember context.
- **Conversational AI** — natural-language queries on any building metric; source-cited
  responses; export to PDF; switch agents mid-conversation; voice input.
- **AI diagnostics** — proactive fault detection and diagnostics.
- **Automated reporting** — drag-and-drop report builder, live data, scheduling,
  one-click distribution; polished PDF output.
- **Power tools** — bulk find/replace/refactor of stream references across dashboards
  with before/after comparison and validation warnings.
- **Collaboration** — share reports across organisations; recipients get their own copy.
- Proof point on page: deployed across 500+ commercial buildings in Australia.

## Infographic concepts (reuse these, don't reinvent)
These are the recurring product visuals on the page. When a Solution item or the Outcome
dashboard is about the platform itself, render the matching concept (rebuilt in the
Bitpool light theme via the design system, not screenshotted) rather than a generic photo:
- **Data Quality report card** — composite score + completeness/accuracy/uniqueness bars
  + data-composition split (source / estimated / missing) + audit log entries.
- **Pools at scale** — list of pools with record counts, stream counts, location, and
  source/processed quality bands; "N billion records, one platform" headline stat.
- **Real results tiles** — minutes saved per task, hours recovered weekly, ×faster
  execution, % on-time delivery (these map naturally onto the Outcome dashboard rings).
- **AI agent card** — specialist agent (Energy & Sustainability etc.), online status,
  capability bullets, a sample "try asking" query.
- **Task creation flow** — four steps: Name → Agent → Schedule → Sources.
- **Task calendar / grid** — colour-coded AI tasks with "saving N minutes" per task.
- **Conversational AI** — chat with source-cited, data-backed answers.
- **Report builder + PDF output** — live-data report assembling itself, scheduled,
  distributed.
- **Power tools** — find/replace across dashboards with before/after.

## Rules
- Capabilities and product names come from the live page, not memory.
- Real-results numbers on the page are illustrative product figures — they are **not**
  the client's measured outcomes. Keep the Outcome dashboard tied to real, client-
  approved metrics per the voice rules in the [case-study workflow](case-study-workflow.md).
- Rebuild infographics in the Bitpool light theme (`bitpool-design-system`); embed as
  data URLs like every other asset. Don't paste website screenshots.
