---
name: report-skill-builder
description: "Use when making a SQL report repeatable. Builds the skill."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, skills, authoring, report, sql, html, bi]
    category: bitpool
    related_skills: [create-new-skill, ai-spend-report, edit-skill, build-skill-from-examples, update-hermes-skill]
---

# Report Skill Builder

Converts an interactively-built SQL report into a repeatable, self-contained Hermes skill — or
improves an existing report skill. The output is a `SKILL.md` plus a verified HTML scaffold where
every visible value derives from SQL against the Bitpool BI MCP server, with no hardcoded business
figures. The seven-phase method, the query rules, the scaffold contract and the pre-delivery
checklist ship in `references/`.

## When to Use

- `/report-skill-builder`.
- The user wants to capture a report workflow as a reusable skill: "turn this into a skill", "make
  this a skill", "create a report skill", "build a skill for this report", "make the report
  repeatable".
- Creating a new report skill for any data source in the BI MCP server, or improving an existing one.

Don't use for:
- Running an existing report: run that report's own skill (e.g. `/ai-spend-report`).
- A skill that isn't a SQL-driven report: `/create-new-skill` or `/build-skill-from-examples`.
- Publishing the finished folder or editing a published skill's non-report content:
  `/create-new-skill` and `/edit-skill` (this skill hands off to them).

## Prerequisites

- The Bitpool Internal Business Intelligence MCP server added to Hermes (find its tools with
  `tool_search` if names differ), so queries can be run and verified.
- The report's source conversation, or a user available to interview with `clarify`.

## Procedure

Read `references/report-skill-method.md` before writing any SQL or HTML, and
`references/report-skill-authoring.md` before writing the new `SKILL.md`. Read the whole file you
reach for — skimming for the line you expect is how a threshold or a flag gets missed.

1. **Understand the report** (method, Phase 1): data sources, every successful query, date
   parameterisation, sections, corrections made in-session, fixed config. Interview with `clarify`
   if building from scratch. Done when all six items are written down.
2. **Audit for hardcoded values** (Phase 2). Done when every displayed value maps to a query, and
   each corrected one carries a `# CORRECTED` note.
3. **Define the query library** (Phase 3), parameterised with `:start` / `:end`, each block with
   `PURPOSE` and `POPULATES`, following the query rules. Done when every query has run successfully
   through the BI MCP server.
4. **Write the validation checks** (Phase 4) — totals, transaction sums, pivots, period coverage.
   Done when each check passes on the current data and would have caught this session's errors.
5. **Build the HTML scaffold** (Phase 5) with `// DATA START` / `// DATA END` markers, `// SOURCE:`
   on every constant, the mandatory helpers and Bitpool styling. Done when it renders standalone with
   real data.
6. **Write the `SKILL.md`** (authoring, Phase 6) in Hermes house frontmatter and the fixed section
   order; overflow (queries, contract) goes to `references/`. Done when the description is <= 60
   chars and starts `Use when`.
7. **Run the ten-point checklist, then hand off** (Phase 7). Try it locally from
   `$HERMES_HOME/skills/` if useful, then hand the folder to `/create-new-skill` to publish into
   `Lolman-bot/Hermes-Repository-`. Done when all ten boxes are ticked and `/create-new-skill` has
   taken over.

## Load-bearing rules

Restated here because a report skill that violates these produces confident, wrong numbers on every
future run.

1. **The scaffold is fixed; the data is always live.** Structure is baked in once. Data is
   re-queried every run. Nothing else changes.
2. **No hardcoded business values, ever** — no revenue figure, user name or count. The only
   hardcodable values are stable config: contact UUIDs, project keys, schema names.
3. **Aggregate in SQL, not by hand.** A figure displayed as one number comes from
   `SUM`/`COUNT`/`ROUND`, never from manual arithmetic over raw rows.
4. **Every JS constant carries a `// SOURCE:` comment** naming the query that produced it.
5. **Validation checks are mandatory and halting.** Define them, run them, and stop if one fails —
   don't ship the report with a caveat.
6. **Period labels derive from query results**, never from hardcoded month-name strings.
7. **Only the block between `// DATA START` and `// DATA END` is replaceable.** Everything outside
   it is structure.
8. **Never improvise a query rule from memory.** The timezone conversion, the cent-division, the
   fan-out ban and the soft-delete filter are each a class of silently-wrong report.
9. **Self-contained.** The new skill ships its queries and scaffold in `references/`; it never
   fetches its instructions from GitBook or any live page at run time.

## Pitfalls

- **Hand-copied numbers from raw query output** look right in the session they were built in and
  are wrong in every later one — Phase 2 exists to catch them.
- **Chargebee Skyvia money columns are cents.** Divide by `100.0` before rounding.
- **Timezones.** `chargebee` / `xero` timestamps need the Brisbane conversion or month boundaries
  shift.
- **Subscriptions joined to invoices** fan out and inflate totals; keep them in separate queries.
- **`anthropic."AllActivity"` system rows** — filter with `user_email NOT LIKE '(%'`.
- **Claude-era packaging** (`.skill` zips, a `present_files` call, a fixed skills build folder)
  doesn't exist in Hermes; publishing goes through `/create-new-skill`.

## Verification

- Every query in the library ran successfully and every validation check passed on real data.
- The scaffold renders standalone with no external dependency except the Chart.js CDN, and contains
  no business value outside the data block.
- The new `SKILL.md` passes the house rules (`/update-hermes-skill`'s `verify_repo.py`, run by
  `/create-new-skill`).
- All ten checklist items in `references/report-skill-authoring.md` are ticked.

## Reference files

| File | Covers |
|---|---|
| `references/report-skill-method.md` | Phases 1–5: understanding the report, auditing for hardcoded values, the query library and its rules, validation checks, and building the HTML scaffold (helpers, styling). |
| `references/report-skill-authoring.md` | Phases 6–7: the new skill's frontmatter and fixed section order, the folder shape, handing off to `/create-new-skill`, and the ten-point pre-delivery checklist. |

Editing this skill: phases, query rules, scaffold contract, `SKILL.md` shape, packaging and the
checklist live in those two files.
