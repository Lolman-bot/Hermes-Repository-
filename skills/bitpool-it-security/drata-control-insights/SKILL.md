---
name: drata-control-insights
description: "Use when user runs /drata-control-insights. DCF matrix."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, drata, jira, compliance, iso27001, aws, security]
    category: bitpool
    related_skills: [ask-drata, drive-iso27001, aws-context, aws-query, change-request, bitpool-design-system]
---

# Drata Control Insights

Produces a structured visual matrix for any Drata control (DCF) or CSIP Jira issue, joining the real Drata control record, live Jira data, a GitBook documentation check, and — for controls that touch infrastructure — the **actual current state of Bitpool's AWS accounts** into one status matrix and keyword tag cloud, rendered as a self-contained HTML page.

Read-only across all four systems; this skill never writes anywhere except the local HTML file it renders. For multi-control work, staged Jira writes and a persistent worklog, that's `/drive-iso27001` — this is the single-control snapshot it can render on demand.

**Why the AWS check matters here:** when Drata's `isMonitored` flag is `false` there is no automated test behind the control, so the only other input is someone's recollection of how the environment is configured. A bounded read-only query replaces that with an observation.

## When to Use

- **Only** when the user types the slash command `/drata-control-insights` (with a `DCF-xxx` or `CSIP-xxx` argument).

Don't use for — these are anti-triggers, not triggers:
- Any bare DCF identifier (e.g. DCF-164) or CSIP issue key (e.g. CSIP-760) without the slash command.
- "give me insights on", "what is DCF-NNN", "explain this control", "summarise this control", "Drata", "compliance", or any similar phrasing.
- Multi-control or staged-write work: `/drive-iso27001`. Connection quirks: `/ask-drata`.

## Prerequisites

- **The Drata MCP server** and **the Atlassian (Jira) MCP server** added to Hermes (`hermes mcp add …` or `manage_connections`). Tool names in the reference are the servers' own; in Hermes they carry an `mcp_<server>_` prefix — find them with `tool_search`.
- Optional: an AWS SSO session via `/aws-context` for the infrastructure row.

## Procedure

Full workflow and layout: `references/drata-control-insights-matrix.md` — read it whole with `read_file` before rendering.

1. **Resolve the identifier** (Step 1): DCF → Jira search → CSIP issue; or CSIP → read the DCF code from its title. Done when you hold the CSIP issue fields and a DCF code (or know there is none).
2. **Pull the real Drata record** (Step 1b), read-only, in list mode per `/ask-drata` rules 1–3. Done when you hold `flags`, `name`, `description`, `updatedAt` — or have recorded "no Drata record found for DCF-xxx".
3. **Derive metadata** (Step 2) — real data first, inference only where Drata carries nothing. Done when every matrix field is filled or marked inferred.
4. **Documentation check** (Step 2b) against `references/documentation-index.md`. Done when the domain is "documented: <path>" or "no documentation found in index (snapshot 2026-08-21)".
5. **AWS current-state check** (Step 2c) per `references/aws-evidence-map.md`: relevance test first, then `/aws-context` and `/aws-query`, within budget. Done when each check is **in place** / **gap** / **not checked**, dated.
6. **Render the matrix** (Step 3): one HTML file via `write_file`, opened with the browser tools, path given to the user. Done when all six rows render, including the infrastructure row.
7. **Follow up** (Step 4) with 1–2 sentences on the most actionable, best-grounded insight. Done when the commentary follows the priority order (AWS gap → false flag → doc gap → inferred).

## Load-bearing rules

Restated here because breaking one produces a matrix that misleads rather than informs.

1. **Read-only across all four systems.** Never write to Drata, Jira, GitBook or AWS from this skill. The posture is set in `/ask-drata`'s write-policy table.
2. **Render Drata's `flags` exactly as returned** — `isReady`, `hasEvidence`, `hasPolicy`, `hasOwner`, `isMonitored`. Never guess them. If no Drata record was found, say so instead of fabricating flag values.
3. **An AWS result is an observation, not evidence and not a verdict.** Report "CloudTrail logging in `<n>` of `<m>` accounts, observed `<date>`" — never "control satisfied".
4. **Stay in the snapshot budget: ≤2 domains, ≤6 calls.** This is a snapshot, not an audit. If a control needs more, say so and point at `/drive-iso27001 DCF-xxx`.
5. **Never omit the infrastructure row silently.** Not relevant → one muted line saying why. Relevant but unchecked → one muted line naming the reason. Never let "not checked" read as a pass.
6. **Degrade cleanly.** The matrix must still render from Drata + Jira + GitBook alone. AWS is enrichment.
7. **Never inline AWS CLI commands, profile names or account IDs** — `/aws-context` for the session, `/aws-query` for the calls.
8. **Never use template literals or `${}` interpolation to generate keyword tags inline in HTML** — it breaks rendering. Use a placeholder div populated by a script block.
9. **All colour via CSS variables**, never hardcoded hex — including for the "gap" warning tone. The palette is declared once in the file's `:root` block and nowhere else.
10. **Slash-command only.** A bare DCF or CSIP key is an anti-trigger, not a trigger.

## Pitfalls

- **Using Drata `query` search mode** — it returns `[]` for controls that exist (`/ask-drata` rule 1). An empty result is not "no record".
- **Reading `hasEvidence` as proof either way** — render it as returned, but don't narrate it as an evidence verdict (`/ask-drata` rule 10).
- **Calling the doc index's silence "undocumented"** — it is a dated snapshot; say "not found in index".
- **A policy is not a procedure** — a domain with a policy and no runbook is not fully documented.
- **Fishing in AWS** for physical, HR, policy-existence or training controls — they are not AWS questions.

## Verification

- The flags in Row 2 match the Drata response verbatim, or the row says no record was found.
- The infrastructure row exists, with every check dated and stated as in place / gap / not checked.
- AWS calls ≤6 across ≤2 domains; no CLI, profile name or account ID appears in the output.
- The HTML file contains no hex colour outside `:root` and no `${}` in the keyword markup.

## Reference files

Read the file itself — the table is an index, not a substitute.

| File | Covers |
|---|---|
| `references/drata-control-insights-matrix.md` | Building the single-control insights matrix — resolving the identifier, deriving metadata, the documentation and AWS current-state checks, the six-row layout, rendering it as an HTML file, and the follow-up priority order. |
| `references/aws-evidence-map.md` | Which read-only AWS checks evidence which control domain, the relevance test, per-control call budgets, and the risk/cost/effort advisory shape. Shared by /drive-iso27001 and /drata-control-insights. |
| `references/documentation-index.md` | Which policies and procedures exist, by control domain. A 2026-08-21 snapshot — an absent domain is a candidate gap, never a confirmed absence. |

Workflow, layout, design rules → edit `references/drata-control-insights-matrix.md`. AWS checks → extend the **AWS Evidence Map** (owned by `/drive-iso27001`), never this skill. Adding CLI recipes, profile names or account IDs here is the specific duplication the split exists to prevent.
