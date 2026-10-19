---
name: ai-spend-report
description: "Use when running the AI spend report. Xero + usage HTML."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, finance, report, xero, ai-spend, anthropic, html]
    category: bitpool
    related_skills: [report-skill-builder, bitpool-report-builder]
---

# AI Spend & Usage Report — Bitpool

Generates the Bitpool AI Spend & Usage Report as one self-contained HTML file with two sections:
**Billing** — AI vendor charges from Xero BankTransactions for Anthropic, OpenRouter and OpenAI —
and **Usage** — Claude subscription analytics from the Anthropic schema (`AllActivity`,
`ClaudeCode`) plus GitHub commit activity for cross-validation. Every value in the report is
derived from SQL; the SQL, data contract, fixed notices, report structure and HTML scaffold all
ship in `references/`, and nothing is fetched at run time.

## When to Use

- `/ai-spend-report`.
- The user asks to generate, run, produce or refresh the AI spend report, AI usage report or AI
  cost report: "run the AI report", "generate the spend report", "monthly AI report".

Don't use for:
- Turning some other interactively-built report into a repeatable skill: `/report-skill-builder`.
- General Bitpool-branded reports that aren't this fixed AI spend report: `/bitpool-report-builder`.
- Ad-hoc Xero questions with no report output — query the BI MCP server directly.

## Prerequisites

- The **Bitpool Internal Business Intelligence** MCP server added to Hermes (`hermes mcp add ...`
  or `manage_connections`) at **full** permission level, for Xero access. Find its tools with
  `tool_search` (e.g. "bitpool bi learn", "bitpool bi query") if names differ from the ones below.
- All Billing values are AUD. Anthropic usage spend is USD and stays labelled as such.

## Procedure

1. **Load the schema context.** Call the BI MCP server's `learn_bitpool_bi_data` tool before any
   query — every run, even mid-session. Done when it has returned the schema context.
2. **Ask for the period with `clarify`.** Use the exact prompt in
   `references/ai-spend-report-workflow.md` (start and end month, MM/YYYY) and wait. Never default
   to a prior period. Set `:start` = first day of the start month and `:end` = first day of the
   month **after** the end month (exclusive). Done when the user has answered and both bounds are
   written down.
3. **Run every query.** Read `references/ai-spend-report-queries.md` in full, then run 3a–3k
   verbatim through the BI MCP server with `:start` / `:end` substituted. Done when every query has
   a result set.
4. **Validate.** Run the six consistency checks in `references/ai-spend-report-queries.md`. If any
   fails, re-run the relevant query and investigate. Done when all six reconcile — never build on a
   failed check.
5. **Build the HTML.** Read `references/ai-spend-report-report-contract.md`, then load
   `references/scaffold.html` and replace **only** the block between `// ══ DATA START ══` and
   `// ══ DATA END ══`, populating every `/*INJECT:**/` constant from query results in the contract's
   shapes. Done when no `/*INJECT:**/` placeholder remains and nothing outside the markers changed.
6. **Output.** Save with `write_file` as `bitpool_ai_report_[month]_[YYYY]_to_[month]_[YYYY].html`
   (lowercase month names, e.g. `bitpool_ai_report_april_2026_to_may_2026.html`) and give the
   absolute path; on a messaging platform also attach `MEDIA:/absolute/path/<file>.html`. Done when
   the user has the file.

## Load-bearing rules

Restated here because getting these wrong produces a confident report with wrong numbers.

1. **Call `learn_bitpool_bi_data` first**, before any query, even mid-session. It sets column
   quoting, monetary conventions and soft-delete filters.
2. **Always ask for the period, every run.** Never default to a prior period. `:end` is the first
   day of the month *after* the end month — an exclusive upper bound.
3. **Every figure comes from SQL.** No hardcoded business values, ever, anywhere in the output.
4. **Copy each query verbatim.** Never improvise a query, a validation check, a data-constant shape
   or a report notice from memory — a wrong `WHERE` clause produces a plausible report with the
   wrong numbers in it.
5. **Never build on failed validation.** If a consistency check doesn't reconcile, re-run and
   investigate — don't ship the report with a note about it.
6. **Only the data block changes.** Replace what sits between `// ══ DATA START ══` and
   `// ══ DATA END ══`. Never touch CSS, structure, chart wiring or helpers. `scaffold.html` is used
   byte-for-byte; copy it, never regenerate it.
7. **Month keys are indexed (`m0`, `m1`), never named.** All dynamic text derives from
   `MONTH_LABELS` and `REPORT_PERIOD_LABEL`.
8. **The three report notices are verbatim.** They are disclosure wording about data lag and
   attribution, not prose to tidy.
9. **The vendor ContactIds are hardcoded and must not be looked up dynamically.** Anthropic
   `9752036a-474f-4c09-99e3-3cee06c7b7a3`, OpenRouter `a87c1eaa-5ee9-45f2-9b32-8f40c1eb5436`,
   OpenAI `dba7c2d4-8594-4255-abbd-8929e14298a2`.

## Pitfalls

- **The scaffold's own header comment says "build a NEW HTML file from scratch".** The skill's rule
  wins: copy the scaffold and replace only the data block. Rebuilding drifts the styling and the
  chart wiring.
- **The scaffold ships Apr/May 2026 data as a worked example.** Any leftover `'2026-04'`, `'Apr'`,
  `'May'` or dollar figure in the output means a constant wasn't replaced.
- **Usage data lags.** Anthropic usage comes from manual monthly CSV exports, so the latest month may
  be empty or partial; that's what the first notice discloses — don't fill the gap.
- **The `claude` GitHub login is an AI agent, not a bot.** Flag it `agent:true` and keep it in the
  real totals; only `github-actions[bot]` and `dependabot[bot]` are bots.
- **A BI MCP server at a lower permission level** won't see Xero; check the level before blaming
  the queries.

## Verification

- All six validation checks reconciled before the HTML was built.
- `search_files` on the output for `/*INJECT:` returns nothing, and the three notices match the
  contract word for word.
- The file opens standalone in a browser and every chart renders (Chart.js loads from its CDN).
- Header, table headers and chart labels show the requested period, not Apr/May 2026.

## Reference files

| File | Covers |
|---|---|
| `references/ai-spend-report-workflow.md` | The whole run, steps 1–6, the exact date-range prompt, the output filename and the vendor ContactIds. |
| `references/ai-spend-report-queries.md` | Every SQL query (3a–3k) and the six validation checks. |
| `references/ai-spend-report-report-contract.md` | Data-constant shapes, field naming, section order, the three verbatim notices, styling. |
| `references/scaffold.html` | The complete report: all CSS, chart wiring, helper functions and the `/*INJECT:**/` data block. |

Editing this skill: queries, validation checks, data contract, notices, section order and styling
notes live in the matching `references/` file. If you change `references/scaffold.html`, update
`references/ai-spend-report-report-contract.md` in the same pass so the two don't drift.
