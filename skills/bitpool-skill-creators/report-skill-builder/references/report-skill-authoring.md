# Report Skill Authoring

Picks up from [Report Skill Method](report-skill-method.md) once the queries, validation checks
and scaffold exist.

## Phase 6 — Write the SKILL.md

Structure the new skill's `SKILL.md` with these sections, in this order:

```
---
name: [report-name]
description: "Use when [trigger]. [behaviour]."   # <= 60 chars, Hermes house frontmatter
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, report, ...]
    category: bitpool
    related_skills: []
---

## When to Use
[Triggers, and what MCP server is required — the long trigger text lives here, not in the description]

# [Report Name] — Bitpool

## Step 1 — Session setup
[Call the BI MCP server's learn_bitpool_bi_data tool, or equivalent]

## Step 2 — Ask for date range
[Exact prompt to show user via `clarify`, date bound conversion logic]

## Step 3 — Run all SQL queries
[Full query library with IDs, purposes, and JS constant names]

## Step 4 — Data validation checks
[Cross-check list — halt if any fail]

## Step 5 — Build the HTML report
[Rules: no hardcoded values, SOURCE comments, dynamic KPIs, month label handling]

## Step 6 — Output
[Filename pattern; `write_file`, then the absolute path (or `MEDIA:/path` on a messaging platform)]

## Report structure
[Fixed section order — do not reorder between runs]

## Fixed notices (if any)
[Verbatim text for any notices that must always appear]

## Fixed config
[Stable IDs, keys, contact UUIDs — the only values that may be hardcoded]

## Styling reference
[Pointer to scaffold.html]
```

> **Note**
> Keep the SKILL.md to ~100-250 lines (Hermes house rule). If the query library is large, move it to
> `references/queries.md` and index it from the SKILL.md — the way the Bitpool skills themselves
> are structured. Never move it to a GitBook page and leave the SKILL.md as a fetch index: a skill
> must be self-contained, so it works with no connector and offline.


## Phase 7 — Package and deliver

Create the skill folder:

```
[report-name]/
├── SKILL.md
└── references/
    └── scaffold.html   (verified HTML with real data as a worked example)
```

The scaffold should contain real data from the most recent successful run — it serves as both
the template and a worked example for future reference.

### Publishing

There is no `.skill` zip in Hermes. Hand the finished folder to `/create-new-skill`, which places
it at `skills/<section>/[report-name]/` in `Lolman-bot/Hermes-Repository-`, adds the README row,
runs `/update-hermes-skill` and raises the pull request. To try it locally first, put the folder
under `$HERMES_HOME/skills/` (or create it with `skill_manage`) and run `/[report-name]`.

## Quality checklist before delivery

Verify all ten before packaging:

- [ ] Every displayed value in the scaffold derives from a JS constant
- [ ] Every JS constant has a `// SOURCE:` comment
- [ ] No hardcoded business values (revenue, counts, names) outside fixed config
- [ ] All queries use `ROUND(...::numeric, 0)` for monetary display figures
- [ ] Data validation checks are defined, and would have caught the errors found in this session
- [ ] Month/period labels are derived from query results, not hardcoded strings
- [ ] Scaffold renders correctly standalone — no external dependencies except the CDN
- [ ] SKILL.md is ~100-250 lines, with detail in `references/`, and its frontmatter matches the
      Hermes house shape (description <= 60 chars, starts "Use when")
- [ ] Fixed notices, if any, are present verbatim
- [ ] The filename pattern is documented in Step 6
