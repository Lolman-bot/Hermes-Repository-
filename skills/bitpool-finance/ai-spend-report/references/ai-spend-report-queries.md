# AI Spend Report — Queries

Run every query below before building the report. `:start` and `:end` come from step 2 of the
[Workflow](ai-spend-report-workflow.md); `:end` is always an **exclusive** upper bound.

> **Important**
> Never embed a value manually. Every data constant in the HTML must come from a query result.


## Billing — Xero

### 3a · Vendor × month

```sql
SELECT
    "ContactName",
    TO_CHAR(DATE_TRUNC('month',"Date"),'YYYY-MM') AS month,
    ROUND(SUM("Total")::numeric,0) AS total_aud,
    COUNT(*) AS txn_count
FROM xero."BankTransaction"
WHERE "ContactId" IN (
    '9752036a-474f-4c09-99e3-3cee06c7b7a3',  -- Anthropic
    'a87c1eaa-5ee9-45f2-9b32-8f40c1eb5436',  -- OpenRouter
    'dba7c2d4-8594-4255-abbd-8929e14298a2'   -- OpenAI
)
AND "Date" >= ':start' AND "Date" < ':end'
GROUP BY "ContactName", DATE_TRUNC('month',"Date")
ORDER BY "ContactName", month
```

→ Populates `BILLING_BY_VENDOR_MONTH`

### 3b · Vendor totals

```sql
SELECT
    "ContactName",
    ROUND(SUM("Total")::numeric,0) AS total_aud,
    COUNT(*) AS txn_count
FROM xero."BankTransaction"
WHERE "ContactId" IN (
    '9752036a-474f-4c09-99e3-3cee06c7b7a3',
    'a87c1eaa-5ee9-45f2-9b32-8f40c1eb5436',
    'dba7c2d4-8594-4255-abbd-8929e14298a2'
)
AND "Date" >= ':start' AND "Date" < ':end'
GROUP BY "ContactName"
ORDER BY total_aud DESC
```

→ Populates `BILLING_BY_VENDOR`, plus `BILLING_GRAND_TOTAL` (sum of all rows) and
`BILLING_TOTAL_TXNS` (sum of `txn_count`).

### 3c · Monthly grand totals

```sql
SELECT
    TO_CHAR(DATE_TRUNC('month',"Date"),'YYYY-MM') AS month,
    ROUND(SUM("Total")::numeric,0) AS total_aud
FROM xero."BankTransaction"
WHERE "ContactId" IN (
    '9752036a-474f-4c09-99e3-3cee06c7b7a3',
    'a87c1eaa-5ee9-45f2-9b32-8f40c1eb5436',
    'dba7c2d4-8594-4255-abbd-8929e14298a2'
)
AND "Date" >= ':start' AND "Date" < ':end'
GROUP BY DATE_TRUNC('month',"Date")
ORDER BY month
```

→ Populates `BILLING_BY_MONTH`

### 3d · Individual transactions

```sql
SELECT
    "ContactName",
    "Date",
    ROUND("Total"::numeric,2) AS amount,
    "Reference"
FROM xero."BankTransaction"
WHERE "ContactId" IN (
    '9752036a-474f-4c09-99e3-3cee06c7b7a3',
    'a87c1eaa-5ee9-45f2-9b32-8f40c1eb5436',
    'dba7c2d4-8594-4255-abbd-8929e14298a2'
)
AND "Date" >= ':start' AND "Date" < ':end'
ORDER BY "ContactName", "Date", "Reference"
```

→ Split the result into `BILLING_TXN_AN` (Anthropic rows) and `BILLING_TXN_OR` (OpenRouter
rows), for the cumulative charts. OpenAI transactions are low-frequency — include them in a
separate `BILLING_TXN_OAI` array if any are present.

## Usage — Anthropic

> **Note**
> `AND user_email NOT LIKE '(%'` on the `AllActivity` queries excludes Anthropic's aggregate
> pseudo-users. Keep it.


### 3e · Monthly totals

```sql
SELECT
    month,
    ROUND(SUM(total_net_spend_usd)::numeric,0) AS spend_usd,
    SUM(total_requests) AS requests,
    COUNT(DISTINCT user_email) AS active_users
FROM anthropic."AllActivity"
WHERE period_start >= ':start' AND period_start < ':end'
AND user_email NOT LIKE '(%'
GROUP BY month
ORDER BY month
```

→ Populates `USAGE_BY_MONTH`

### 3f · Per user × month

```sql
SELECT
    month,
    user_email,
    ROUND(SUM(total_net_spend_usd)::numeric,0) AS spend_usd,
    SUM(total_requests) AS requests,
    SUM(total_web_search_count) AS web_searches
FROM anthropic."AllActivity"
WHERE period_start >= ':start' AND period_start < ':end'
AND user_email NOT LIKE '(%'
GROUP BY month, user_email
ORDER BY month, spend_usd DESC
```

→ Pivot into `USAGE_BY_USER`: one object per unique user, with spend, requests and web
searches keyed by **month index** (`m0`, `m1`, …) derived from the months the query actually
returned.

> **Warning**
> Do not use hardcoded month-name fields like `apr_s` or `may_s`. Index keys only.


### 3g · Spend by product

```sql
SELECT
    month,
    product,
    ROUND(SUM(total_net_spend_usd)::numeric,0) AS spend_usd,
    SUM(total_requests) AS requests
FROM anthropic."AllActivity"
WHERE period_start >= ':start' AND period_start < ':end'
AND user_email NOT LIKE '(%'
GROUP BY month, product
ORDER BY month, spend_usd DESC
```

→ Populates `USAGE_BY_PRODUCT`

### 3h · Claude Code lines by user

```sql
SELECT
    month,
    user_email,
    lines_this_month
FROM anthropic."ClaudeCode"
WHERE period_start >= ':start' AND period_start < ':end'
ORDER BY month, lines_this_month DESC
```

→ Populates `CC_LINES_BY_USER`

### 3i · Claude Code monthly totals

```sql
SELECT
    month,
    SUM(lines_this_month) AS total_lines,
    COUNT(DISTINCT user_email) AS active_users
FROM anthropic."ClaudeCode"
WHERE period_start >= ':start' AND period_start < ':end'
GROUP BY month
ORDER BY month
```

→ Populates `CC_TOTALS`

## Commit activity — GitHub

### 3j · Contributor totals

```sql
SELECT
    contributor_login,
    SUM(commits) AS commits,
    SUM(additions) AS additions,
    SUM(deletions) AS deletions,
    SUM(additions) - SUM(deletions) AS net_lines
FROM github.contributor_weekly_stats
WHERE week_start >= ':start' AND week_start < ':end'
GROUP BY contributor_login
ORDER BY commits DESC
```

→ Populates `GH_CONTRIBUTORS`.

Flag `github-actions[bot]` and `dependabot[bot]` as bots. Flag the `claude` login as an **AI
agent, not a bot** — it represents direct Claude Code commits and belongs in the real totals.

### 3k · Weekly totals

```sql
SELECT
    week_start,
    SUM(commits) AS commits,
    SUM(additions) AS additions,
    SUM(deletions) AS deletions
FROM github.contributor_weekly_stats
WHERE week_start >= ':start' AND week_start < ':end'
GROUP BY week_start
ORDER BY week_start
```

→ Populates `GH_WEEKLY`

## Validation checks

Before building the report, verify these totals are internally consistent:

1. Sum `BILLING_BY_VENDOR_MONTH` per vendor → must match `BILLING_BY_VENDOR`.
2. Sum `BILLING_BY_VENDOR` → must match `BILLING_GRAND_TOTAL`.
3. Sum `BILLING_TXN_AN` amounts → must match the Anthropic total in `BILLING_BY_VENDOR`.
4. Sum `BILLING_TXN_OR` amounts → must match the OpenRouter total in `BILLING_BY_VENDOR`.
5. Sum `USAGE_BY_USER` spend per month → must match `USAGE_BY_MONTH` spend (± rounding).
6. Sum `CC_LINES_BY_USER` per month → must match `CC_TOTALS`.

> **Important**
> If any check fails, re-run the relevant query and investigate before proceeding. Do not build
> the report with inconsistent data.
