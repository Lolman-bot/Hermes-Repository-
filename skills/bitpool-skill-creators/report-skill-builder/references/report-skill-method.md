# Report Skill Method

Converts an interactively-built SQL report into a repeatable, self-contained skill. The output
is a SKILL.md plus an HTML scaffold where every visible value derives from SQL queries — no
hardcoded business figures.

> **Note**
> **The core principle: the scaffold is fixed, the data is always live.**
>
> A good report skill separates two concerns completely. **Structure** — HTML, CSS, chart wiring,
> helper functions — is baked into the scaffold once and never changes between runs. **Data** —
> JS constants populated from SQL — is re-queried every run and is the only thing that changes.
>
> The skill therefore never contains a hardcoded revenue figure, user name, or count. It contains
> parameterised SQL, and the report builds itself from the results.


## Phase 1 — Understand the report

If the user is converting a report they just built interactively, extract from the conversation
history:

1. **Data sources** — which schemas and tables were queried (`xero`, `chargebee`, `anthropic`,
   `github`, `crm`, …).
2. **All SQL queries used** — every query that ran successfully and produced data used in the
   report. These become the skill's query library.
3. **Date parameterisation** — how the range works (calendar month, fiscal quarter, arbitrary
   range). Identify the `start`/`end` bounds pattern.
4. **Report sections** — the logical structure: KPI cards, charts, tables.
5. **Any corrections made** — if the user caught a data error during the session, note the root
   cause and add a validation step so it can't recur.
6. **Fixed config** — anything stable across all runs (vendor contact IDs, project keys, schema
   names). These are the *only* values that may be hardcoded in the skill.

If the user is building a new report from scratch, interview them for the same information
before writing any SQL.

## Phase 2 — Audit for hardcoded values

Before writing the skill, identify every value in the current report output that came from
manual transcription rather than a direct SQL result. Flag each one and confirm the query that
actually produces it.

Common failure modes:

- Values copied from raw query output by hand rather than using SQL aggregates
- Row-level data summed or counted manually instead of via `SUM()` / `COUNT()`
- Totals that don't match the sum of their parts — usually fan-out from a bad join
- Date filtering done in the wrong timezone
- Monetary values not divided by 100 for Chargebee Skyvia cent fields
- Missing soft-delete filters (`AND "Deleted" = false`)

For each flagged value, provide the corrected SQL and mark it in the query library with a
`# CORRECTED` note.

## Phase 3 — Define the SQL query library

Write out every query the skill needs, parameterised with `:start` and `:end` (or whatever the
date params are). Format each block as:

````
### Query ID — Human-readable name
PURPOSE: one sentence on what this query produces
POPULATES: JS constant name(s) in the HTML scaffold
```sql
SELECT ...
FROM ...
WHERE ... >= ':start' AND ... < ':end'
```
````

**Rules for queries in skills:**

- Always use SQL aggregates (`SUM`, `COUNT`, `ROUND`) — never return raw rows for a value that
  will be displayed as a single figure.
- Always include soft-delete filters for `chargebee` tables.
- Always use `ROUND(...::numeric, 0)` for monetary display values.
- For Chargebee Skyvia monetary columns: divide by `100.0` before rounding.
- Always apply Brisbane timezone conversion for `chargebee`/`xero` timestamp columns:
  `(col AT TIME ZONE 'UTC') AT TIME ZONE 'Australia/Brisbane'`
- Never join subscriptions to invoices in the same query — fan-out risk.
- Include `user_email NOT LIKE '(%'` on `anthropic."AllActivity"` to exclude system rows.

## Phase 4 — Write the data validation checks

For every report, define cross-checks that verify SQL results are internally consistent before
any HTML is built. At minimum:

- **Vendor/category totals** — sum of per-vendor rows must equal the grand total from a
  separate aggregation query.
- **Transaction array sums** — sum of individual transaction amounts must equal the vendor
  total from the aggregation query.
- **User/period pivots** — sum of per-user figures must equal the monthly total.
- **Period coverage** — the number of distinct months in the results matches the requested
  range.

Document these as a checklist in the new skill under `## Data Validation Checks`, and instruct
it to **halt** if any fail.

## Phase 5 — Build the HTML scaffold

The scaffold is a single self-contained HTML file that:

- Contains all CSS and JS chart wiring (Chart.js via CDN).
- Has clearly marked `// DATA START` and `// DATA END` comment blocks.
- Inside those blocks: only JS constant declarations, each with a `// SOURCE:` comment naming
  the query ID from the library.
- Outside those blocks: helpers, chart initialisation, DOM rendering — all referencing only the
  constants, never an inline number.
- Renders all KPI cards dynamically from a `kpiCard()` helper.
- Uses `Math.round()` for every displayed monetary value.
- Is print-safe: no animations, no hover effects that affect layout.

### Mandatory helper pattern

```javascript
const fmt  = n => '$' + Math.round(n).toLocaleString();
const fmtN = n => Math.round(n).toLocaleString();
const pct  = (a, b) => b === 0 ? null : Math.round((a - b) / b * 100);
const $    = id => document.getElementById(id);

function kpiCard(label, value, sub, delta, dir, alt=false) {
  // Renders a KPI card — never call with hardcoded value strings
}
```

### Styling

Follow the Bitpool `custom.css` design language — the `ai-spend-report` skill's
`references/scaffold.html` is the worked example.

- White cards with a 1.5px gradient border
- Primary gradient `#0066ff → #8b5cf6`; alt/secondary `#0891b2 → #10b981`
- Dark navy header: `linear-gradient(135deg, #061325, #0a2540, #0f2f55)`
- Font: `"Segoe UI", Roboto, Arial, sans-serif`
- No glowing effects, no animated hover — professional and print-safe

Continue to [Report Skill Authoring](report-skill-authoring.md) for the SKILL.md shape,
packaging, and the pre-delivery checklist.
