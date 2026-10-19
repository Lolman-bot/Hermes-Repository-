# AI Spend Report — Workflow

Produces a self-contained HTML report with two sections: **Billing** (Xero) and **Usage**
(Anthropic + GitHub). Every value in the report is derived from SQL — no hardcoded business
figures. The HTML scaffold is fixed; only the data constants change between runs.

> **Note**
> Requires the **Bitpool Internal Business Intelligence** MCP server added to Hermes at full
> permission level (Xero access); find its tools with `tool_search` if names differ. All monetary values in the Billing section are AUD; Anthropic usage
> spend is USD and stays labelled as such.


## Session setup

Call the BI MCP server's `learn_bitpool_bi_data` tool before anything else, to load the full schema context.

Do not skip this even mid-session — it is what ensures correct column quoting, monetary
conventions, and soft-delete filters. A report built without it will be subtly wrong rather
than obviously broken.

## Ask for the date range

**This is the first thing to ask the user (with `clarify`) — every run, without exception.**

> "Which months should the report cover? Please provide a start and end month in MM/YYYY
> format (e.g. 03/2026 – 04/2026). Both months will be included in full."

Do not assume or default to a prior period. Wait for the user's response.

Convert the input to SQL date bounds:

- `start_date` = first day of the start month — `06/2026` → `2026-06-01`
- `end_date` = first day of the month **after** the end month, an exclusive upper bound —
  end `07/2026` → `2026-08-01`

Store these as `:start` and `:end` for every query.

## Run all SQL queries

Run every query on the [Queries](ai-spend-report-queries.md) page before building anything.

Never embed a value manually. Every data constant in the HTML must come from a query result.

## Validate

Run the six internal-consistency checks on the [Queries](ai-spend-report-queries.md) page.

If any check fails, re-run the relevant query and investigate before proceeding. Do not
build the report with inconsistent data — a report that reconciles against nothing is worse
than no report.

## Build the HTML report

Load `references/scaffold.html` from the skill folder (`skill_view` with `file_path`, or
`read_file`). It is a complete, ready-to-render
HTML file.

The only section that changes each run is the data block between `// ══ DATA START ══` and
`// ══ DATA END ══` in the `<script>` section. **Replace only that block.** Do not touch any
CSS, HTML structure, chart wiring, or helper function outside those markers.

Populate every `/*INJECT:**/` placeholder per the
[Report Contract](ai-spend-report-report-contract.md).

## Output

Save as:

```
bitpool_ai_report_[MMMM]_[YYYY]_to_[MMMM]_[YYYY].html
```

e.g. `bitpool_ai_report_april_2026_to_may_2026.html`

Write it once with `write_file` and give the user the absolute path; on a messaging platform
also attach it as `MEDIA:/absolute/path/<file>.html`.

## Vendor contact IDs — hardcoded, do not look up

These IDs are stable and must not be discovered dynamically.

| Vendor | Xero ContactId |
|---|---|
| Anthropic | `9752036a-474f-4c09-99e3-3cee06c7b7a3` |
| OpenRouter | `a87c1eaa-5ee9-45f2-9b32-8f40c1eb5436` |
| OpenAI | `dba7c2d4-8594-4255-abbd-8929e14298a2` |
