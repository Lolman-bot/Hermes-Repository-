# ISO 27001 — Drata & Jira Mapping

Reference for how the three systems join up. Read this whenever resolving a control to its ticket or building a query.

---

## 1 — The DCF ↔ CSIP link

Bitpool tracks each Drata control's *work* as a CSIP parent issue whose title encodes the control:

```
Drata | Bitpool | DCF-xxx | [Control Name]
```

- **Given a DCF number** → find the ticket by searching Jira for the literal `DCF-xxx` string:
  - `search` (free text) with `DCF-xxx`, or
  - `searchJiraIssuesUsingJql` with `project = CSIP AND text ~ "DCF-xxx"`.
  Then `getJiraIssue` the match for full detail.
- **Given a CSIP key** → `getJiraIssue` directly; read the title/description for the DCF code.
- **No match** → the control likely has **no ticket yet** — a prime action item (propose creating the parent).

There is no Drata API field that returns the Jira key; the link lives in the Jira title/description. Keep the reconciled map cached in `_STATE/control-index.md` so you don't re-search every run.

---

## 2 — Drata status semantics (what "outstanding" means)

`Drata_searchControls` is the primary read. Two modes:
- **List mode (no `query`)** — use for counting/filtering. `is_ready=False` returns the outstanding set; `pagination.totalCount` on page 1 is the authoritative count — read it live each run (framework `ISO270012022`). Paginate with `cursor`.
- **Search mode (`query`)** — AI/keyword search to find a control by topic; does **not** respect `is_ready`. Never use it for counting.

Each control carries a **`flags`** object — the fastest gap signal, no extra calls needed:

| flag | meaning | use |
|------|---------|-----|
| `isReady` | control has everything it needs to be compliant | `false` = outstanding |
| `hasTicket` | a task-management (Jira/CSIP) ticket is linked | **`false` = no CSIP ticket → action item** |
| `hasEvidence` | evidence is attached | `false` on a ready control = evidence gap |
| `hasPolicy` | a policy is linked | informational (policy authoring is /isms-draft/-prod) |
| `hasOwner` | an owner is assigned | `false` = assign an owner |
| `isMonitored` | an automated monitor exists | `false` = manual control |

So "outstanding / needs work" = `isReady:false`, and within that, prioritise by the concrete missing pieces the flags reveal. Also:
- **Failing monitoring tests** — `Drata_searchMonitoringTests` (or `has_passing_test=False` in list mode) surfaces tests not passing; the fastest, most concrete fixes.
- **`expand: ["frameworkTags"]`** for framework tags, or `["requirements"]` for the ISO 27001 clause mapping (large payload — deep-dive only).
- Control fields worth capturing: `code` (DCF-xxx), `name`, `description`, `flags`, `updatedAt`.

> Don't hardcode a brittle status list — read `flags`/`isReady` and treat "ready + passing + has current evidence" as *done*, everything else as *candidate work*. When unsure, surface it as a candidate rather than silently dropping it.

**READ-ONLY reminder:** never call **any** Drata write verb from this skill — no `Drata_create*`, no `Drata_update*`, the risk verbs included. Default-deny, not a list: scope is account-level, so this skill is handed the same write verbs as `/manage-drata-control` and the connection will not refuse them. Report gaps; the human closes them in the Drata UI (or via a Jira task that drives the work). Policy authority: the **"Drata write policy by skill"** table in `/ask-drata`.

Useful read-only Drata tools:
- `Drata_searchControls` — control inventory + status.
- `Drata_searchMonitoringTests` — automated test pass/fail.
- `Drata_listRequirements` — framework requirement → control mapping (ISO 27001 clauses).
- `Drata_listEvidence` / `listEvidence` — evidence attached to a control (deep-dive only).
- `Drata_listPolicies` / `Drata_searchPolicies` — policy status (informational; policy *authoring* is /isms-draft/isms-prod).
- `Drata_listRiskRegisters` / `Drata_searchRisks` — risk register context.

---

## 3 — JQL library

Cloud ID: `bitpool.atlassian.net`. Use `searchJiraIssuesUsingJql`. Request fields:
`summary, description, status, issuetype, assignee, duedate, subtasks, parent, labels`.

**Confirmed CSIP statuses** (verified live) and their driver priority:

| Status | Priority | Meaning / handling |
|--------|----------|--------------------|
| `In Progress` | 1 | Started — finish first. |
| `To Do` | 2 | New/likely-ready — pick up next. |
| `Ready` | 3 | Vetted backlog — work to completion. |
| `Re-assess` | 4 (low) | Needs re-evaluation (a large bucket). **Low priority** — only triage once buckets 1–3 are nearly clear (like To Discuss). Some are quick confirmations, some reopen work. |
| `To Discuss` | 5 | Needs a direction chat with the **`To Discuss` direction** role (§4) first — prep, don't execute; help once buckets 1–3 are low. |
| `Waiting` | chase | Blocked on something external — **actively surface each session and propose a follow-up to unblock** (a chase task, or a comment on the CSIP ticket — never on another team's OP/BT ticket, per `SKILL.md` rule 9), rather than leaving it idle. |
| `Done` | — | Complete — ignore for driving. |

> **Prioritisation (confirmed with user):** `In Progress → To Do → Ready → Re-assess → To Discuss`. `Re-assess` and `Waiting` weren't in the original brief; live data surfaced them. `Re-assess` is deliberately low (triage only when actionable buckets are nearly clear); `Waiting` items get chased, not ignored.

**Big JQL result warning:** CSIP issues have large descriptions/ADF — even `fields:["summary","status"]` for 100 issues exceeds the tool's token cap and is auto-saved to a file. **Always** expect to parse the saved JSON with jq/python/a `delegate_task` subagent (schema `{issues:{nodes:[{key,fields:{...}}]}}`), never read it inline. Extract statuses with:
`jq -r '.issues.nodes[].fields.status.name' <file> | sort | uniq -c`.

**Per-stage queries** (run these, parse each saved file):
```jql
project = CSIP AND status = "In Progress" ORDER BY key DESC
project = CSIP AND status = "To Do" ORDER BY key DESC
project = CSIP AND status = "Ready" ORDER BY key DESC
project = CSIP AND status = "Re-assess" ORDER BY key DESC
project = CSIP AND status = "To Discuss" ORDER BY updated DESC
```
Request minimal `fields` and small `maxResults` per stage to keep payloads down; pull full descriptions only when deep-diving a specific issue via `getJiraIssue`.

**Find the ticket for a control:**
```jql
project = CSIP AND text ~ "DCF-xxx"
```

**Security-labelled work in OP and BT** (empty until the `security` label is adopted):
```jql
project = OP AND labels = security AND statusCategory != Done ORDER BY key DESC
project = BT AND labels = security AND statusCategory != Done ORDER BY key DESC
```
> Boards: OP = board 98, BT = board 82. The JQL above covers the whole project; if you need to scope to just the board's issues, add the board's saved filter, but project + label is sufficient for the driver.

**CSIP items awaiting their direction chat (`To Discuss`):**
```jql
project = CSIP AND status = "To Discuss" ORDER BY updated DESC
```

---

## 4 — Write context (Jira only, after approval)

- **Transitions (CSIP):** Done = `41`, In Progress = `31`, To Do = `21`.
- **People — the one place this skill's instructions name them**, apart from the illustrative examples in the [State File Schemas](iso27001-state-files.md) templates, which are snapshots. Everywhere else the instructions refer to the role, so a change of holder is one edit here. Look up anyone else with `lookupJiraAccountId`.

  | Role in this skill | Holder | Jira `accountId` |
  |---|---|---|
  | **Default assignee** — CSIP work with no clearer owner, including transcript action items attributed to someone without a Jira account | Eric Sharp | `712020:997cf0e9-e968-446a-8639-a4664baf291c` |
  | **`To Discuss` direction** — the direction chat a `To Discuss` item needs before real work | Phil Smith | `605d262b557b950068913856` |

- **Sub-tasks** must set the `parent` field. Create parent Tasks first, then sub-tasks.
- Every new task/sub-task description carries `Related DCF: DCF-xxx`, by code. What else the summary and description say, and what goes in a creation comment instead, is Session Playbook step 6.
