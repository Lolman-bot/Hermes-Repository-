# AI Spend Report — Report Contract

Everything on this page describes what `references/scaffold.html` expects. The scaffold itself
ships with the skill and is never reconstructed from GitBook.

## Data constants

Populate every `/*INJECT:**/` placeholder in the data block with values from the
[Queries](ai-spend-report-queries.md).

| Constant | Source query | Shape |
|---|---|---|
| `BILLING_BY_VENDOR_MONTH` | 3a | `[{vendor, month, total, txns}]` |
| `BILLING_BY_VENDOR` | 3b | `[{vendor, total, txns}]` |
| `BILLING_GRAND_TOTAL` | 3b (sum totals) | number |
| `BILLING_TOTAL_TXNS` | 3b (sum txns) | number |
| `BILLING_BY_MONTH` | 3c | `[{month, total}]` |
| `BILLING_TXN_AN` | 3d (Anthropic rows) | `[{d:'YYYY-MM-DD', a:number}]` |
| `BILLING_TXN_OR` | 3d (OpenRouter rows) | `[{d:'YYYY-MM-DD', a:number}]` |
| `USAGE_BY_MONTH` | 3e | `[{month, spend, requests, users}]` |
| `USAGE_BY_USER` | 3f (pivoted) | `[{u, m0_s, m1_s, m0_r, m1_r, m0_w, m1_w}]` |
| `USAGE_BY_PRODUCT` | 3g (pivoted) | `[{product, m0, m1}]` |
| `CC_LINES_BY_USER` | 3h (pivoted) | `[{u, m0, m1}]` |
| `CC_TOTALS` | 3i | `[{month, total, users}]` |
| `GH_CONTRIBUTORS` | 3j | `[{login, commits, additions, deletions, net, bot?}]` |
| `GH_WEEKLY` | 3k | `[{w:'MMM D', commits, additions, deletions}]` |
| `REPORT_PERIOD_LABEL` | user input | string, e.g. `'June – July 2026'` |
| `REPORT_GENERATED` | today's date | string, e.g. `'1 July 2026'` |
| `MONTH_LABELS` | derived from period | `['June 2026', 'July 2026']` |

### Field naming rules

- `USAGE_BY_USER` — `m0_s`/`m1_s` (spend), `m0_r`/`m1_r` (requests), `m0_w`/`m1_w` (web
  searches). Never month-name fields.
- `USAGE_BY_PRODUCT` and `CC_LINES_BY_USER` — `m0`/`m1`. Never month-name fields.
- `GH_CONTRIBUTORS` — set `bot:true` for `github-actions[bot]` and `dependabot[bot]`; set
  `agent:true` for the `claude` login.
- `GH_WEEKLY` — `w` is a short display label derived from `week_start`, e.g. `'Jun 2'`.

### Period metadata

```javascript
const REPORT_PERIOD_LABEL = 'June – July 2026';
const REPORT_GENERATED    = '1 August 2026';
const MONTH_LABELS = ['June 2026', 'July 2026'];
```

> **Warning**
> All dynamic text in the report — header, table headers, chart labels, KPI subtitles, GitHub
> section labels — derives from `MONTH_LABELS` and `REPORT_PERIOD_LABEL`. Never write a month
> name anywhere else in the output file.


## Report structure — fixed, do not reorder

```
Header (dark navy gradient · AUD currency tag · period from user input)
Report Notes (3 fixed notices — see below)
Section 1 — Billing
  KPIs: Total · Anthropic · OpenRouter · OpenAI · Txn count
  Chart: Monthly spend by vendor (grouped bar)
  Chart: Vendor share donut
  Chart: OpenRouter cumulative spend (line)
  Chart: Anthropic Direct cumulative spend (line)
Section 2 — Claude Subscription Usage
  2a — Per-User Usage Detail
    KPIs: Total spend · Active users · Total requests · Top spender
    Chart: Spend by user — [M1] vs [M2] (bar)
    Chart: Spend by product — [M1] vs [M2] (horizontal bar)
    Chart: Requests vs spend trend (mixed bar+line)
    Chart: Web searches by user (bar)
    Table: Per-user detail
  2b — Claude Code: Lines Committed
    KPIs: [M1] total · [M2] total · Top contributor [M1] · Top contributor [M2]
    Chart: Lines per user — [M1] vs [M2] (bar)
    Chart: Lines by month (donut)
  2c — GitHub Commit Activity
    Chart: Weekly commits + additions (mixed)
    Chart: Commits by contributor (horizontal bar)
    Table: Contributor summary with net lines
Footer
```

`[M1]` and `[M2]` are derived from the period the user provided — never hardcoded.

## Fixed report notices — include verbatim

These three notices appear in the info box directly below the header. The wording is fixed;
do not paraphrase.

> **Note**
> **Usage data availability** — "Claude subscription usage statistics are sourced from
> Anthropic's manual monthly CSV exports. Data is only available after the prior month has been
> exported — figures may lag by up to one billing cycle."


> **Note**
> **Billing data currency** — "AI billing figures are sourced from Xero bank transactions. This
> data reflects reconciliation completed by Finance at the time of export — charges may not
> appear until reconciliation is done."


> **Note**
> **OpenRouter & OpenAI — Phil Smith** — "Usage costs for OpenRouter and OpenAI currently
> include Phil Smith's activity alongside production platform usage. There is no breakdown
> available between Phil's personal API usage and production system calls within these figures."


## Styling

The report uses the Bitpool `custom.css` design language. The scaffold already implements all
of it — this is here so a deliberate change can be made knowingly, not so it can be rebuilt.

- White cards with a 1.5px gradient border — blue→purple `#0066ff→#8b5cf6` for primary,
  cyan→green `#0891b2→#10b981` for alt/usage sections
- Dark navy header: `linear-gradient(135deg, #061325, #0a2540, #0f2f55)`
- Typography: `"Segoe UI", Roboto, Arial, sans-serif`
- Text: `#111827` primary · `#6b7280` muted · `#9ca3af` subtitle
- KPI accent bar: 32×4px gradient pill above the label
- No glowing shadows, no animated hover effects — professional and print-safe
