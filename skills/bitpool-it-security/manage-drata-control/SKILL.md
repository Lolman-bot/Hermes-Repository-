---
name: manage-drata-control
description: "Use when treating a Drata control gap. Decide and record it."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, drata, iso27001, isms, risk-register, jira, grc]
    category: bitpool
    related_skills: [ask-drata, bitpool-writing-standard, manage-drata-risks, drive-iso27001, drata-control-insights, create-drata-test, create-devsecops-ticket, describe-dcf-jira-ticket, isms-draft, isms-prod, bitpool-docs, log-skill-divergence]
---

# Manage Control

Takes one Drata control whose position is **unresolved** and drives it to a defensible, recorded one:
a committed plan to close a gap (an `IRT` ticket, sized in hours, dated later), a documented risk
acceptance, compensating controls with an accepted residual, or a correction to an ISMS document that
misstates what Bitpool does. Output: the exact Drata risk text plus the Jira, `/isms-draft` and GitBook
follow-up the decision implies. A run ends on the control's `ICR` ticket — closed when the control is
audit ready on its position, otherwise held with a comment saying what closes it.

**"Unresolved" is wider than "failing."** A control can be `isReady: true` and still unresolved —
usually because a Bitpool ISMS document declares a gap the control doesn't show. Never scope this skill
to `is_ready=False` (Step 3, outcome 4). This is the **gather → advise → decide** skill: assemble the
whole picture, put **2–3 concrete paths** in front of the user, recommend one, and let them choose.

## When to Use

- `/manage-drata-control`, `/manage-drata-control DCF-xxx`, `… CSIP-nnn`, `… ICR-nnn`, or `… audit`.
- The user asks how to handle, treat or justify a control Bitpool does not comply with, or to write a
  risk-treatment plan or SoA justification.

Don't use for:
- A bare DCF/CSIP key with no ask to treat it — `/drata-control-insights`.
- Program-wide driving of ISO 27001 — `/drive-iso27001`.
- Custom Test design — `/create-drata-test`. ISMS policy authoring — `/isms-draft`, `/isms-prod`.
- Verifying whether an existing risk entry is still true — `/manage-drata-risks`.

## Prerequisites

- **The Drata MCP server added to Hermes** (`hermes mcp add …` or `manage_connections`). Tool names in
  this skill (`Drata_searchControls`, `Drata_createRisk`, `Drata_updateRisk`, `Drata_updateControl`,
  `Drata_listRequirements`, `Drata_listEvidence`, …) are the Drata MCP server's tools; Hermes may prefix
  them — find them with `tool_search` if the names differ.
- **The Atlassian (Jira) MCP server** for `IRT`, `ICR` and `CSIP` (`searchJiraIssuesUsingJql`,
  `createJiraIssue`, `editJiraIssue`, `addCommentToJiraIssue`, transitions) — again via `tool_search`.
  Cloud id `bitpool.atlassian.net`.
- **`/ask-drata` — read it before any Drata call.** Its rules 8–10 define what this skill may call;
  rules 1–5 explain why an empty result is usually the tool, not the data. **`/ask-drata` wins** if it
  and this skill disagree; new connection-level quirks go there, not here.
- **`/bitpool-writing-standard`** (section `bitpool-general`) before drafting any text for Drata, `IRT`,
  `ICR`, policy wording or register rationale. If it is not installed, **stop and tell the user once per
  chat**: *"`/bitpool-writing-standard` isn't installed, so the Security Drata, Security Jira, ISMS
  Policy and Security Documentation writing profiles can't be applied. Installing it from the
  `bitpool-general` section is recommended. Proceed without it?"* Continue only on a yes. Output →
  profile table: `references/golden-rules.md` (second rule).
- The main local working copy of `security-documentation` (path rules: `references/bitpool-context.md`).

## Procedure

Modes: `DCF-xxx` → steps below. `CSIP-nnn` / `ICR-nnn` → resolve the control from the ticket first (an
`ICR` ticket, titled `DCF-xxx | [Control Name]`, is the one Step 10 ends on). No argument → ask which
control with `clarify`, offering Drata's not-ready set as a shortlist and noting a ready control can still
be unresolved. `audit` → register-wide hygiene sweep, `references/hygiene-sweep.md` and
`references/audit-and-integration.md`. **One control per run** in default mode.

Full text of every step, with worked failures: `references/workflow.md`. Read it at runtime.

0. **Pre-flight.** Read the Risk Assessment Policy (`Drata_listPolicies(name="risk")`, id `17`) for its
   scales and acceptable level — content only, **never its `renewalDate`/`approvedAt`**. Read the policy
   queue page and every comment on the queue ticket (`project = IRT AND labels = PolicyQueue`). Done when
   you can state the scales, the threshold and which policies already carry queued draft edits.
1. **Resolve the control and its position.** In parallel: the control (list mode + cursor seek, per
   `/ask-drata` gotcha #2), `Drata_searchRisks(controls=["DCF-xxx"])`, Jira `text ~ "DCF-xxx"` across all
   projects, the control's `ICR` ticket and all its comments, and the **controlled** ISMS document for the
   domain (`references/documentation-index.md`; quote the controlled text, never a mirror). Done when a
   table of what exists today is shown.
2. **The gate — clause or Annex A?** `Drata_listRequirements(framework_tag=["ISO270012022"],
   expand=["controls"])`; read and quote `longDescription`. Clause 4–10 → committed plan only. Done when
   the mapping is stated, the operative requirement text quoted and sibling controls noted.
3. **What is the gap against?** Standard wording / Bitpool's own document / no real gap / declared only in
   a document (outcome 4: clause 7.5.3, 9.3, 10.2 exposure; tabulate every date source). Done when one of
   the four outcomes is named with its evidence.
4. **Present 2–3 paths and ask** (`clarify`, recommended first). Format: `references/treatment-decisions.md`
   §7 — what changes, cost, documents/tickets that move, what an auditor would make of it, residual
   exposure. Unconditionals listed separately; include the pragmatic "just do it" path where the work is
   small. Done when the user has chosen. Clause control → skip to Step 8.
5. **Choose the treatment** (`MITIGATE`/`ACCEPT`/`AVOID`/`TRANSFER`; `treatment-decisions.md` §2–3). Done
   when the ISO term and Drata value are agreed.
6. **Draft the risk in risk language** (`treatment-decisions.md` §4) and agree it before scoring. Done when
   the user agrees the statement.
7. **Score against the policy** — inherent *and* residual triplet (residual = inherent for `ACCEPT`). Done
   when both triplets are set and the residual is within the acceptable level, or escalated.
8. **Check the policy still tells the truth.** If drift: draft the wording (ISMS Policy profile), invoke
   `/isms-draft` **now**, then claim a queue row, post its detail comment, link it
   (`references/policy-queue.md`). Done when drift is handed off and queued, or "no drift" is stated.
9. **Approval block, then write.** Render the risk approval block (`references/drata-fields.md` §4) as
   formatted markdown, get an explicit yes, call `Drata_createRisk`/`Drata_updateRisk`. Clause control:
   no risk — stage the register `Rationale` via `/bitpool-docs`. Done when the returned record is read back.
10. **Close the loop outside Drata.** Three-project check (`project in (CSIP, ICR, IRT) AND text ~
    "DCF-xxx"`), stage and create undated, estimated, labelled `IRT` tickets, then end on the `ICR`
    ticket: close (`41`) when the audit-ready gate passes, else hold with a dated comment
    (`references/icr-closure.md`). Done when the `ICR` ticket has this run's comment and its ending.
11. **Summarise** — decision, where each fact lives, what Drata *returned*, tickets and estimates, each
    `ICR` ending, drift handed off (with queue-row link), evidence still to upload, intended absences
    stated affirmatively. Done when nothing is reported as written that was not.

## Load-bearing rules

Summaries — the full text, reasoning and worked failures are `references/golden-rules.md`.

- **Write model is `/ask-drata`'s.** Risks: create/update. Controls: attach policy/owner; text correction
  only by gated exception. No control creation. **No evidence writes — `update:evidence` is not granted**
  (`403`, code 12330); evidence upload is a real capability limit, so never offer it. Everywhere else a
  read-only posture is policy — never say "cannot" when you mean "must not".
- **No write without an approved block.** Every risk create/amend shows the full §4 block plus one
  durability check; amendments also stage their dated change-record comment (on the risk's `IRT` ticket,
  else this run's `ICR`). Approval blocks render as markdown, **never in a fenced code block**.
- **Control text correction** (`Drata_updateControl`) is rare: establish the five points (untrue claim,
  narrow vs widen, every other copy, whether the gap is treated, whether it stays true), then a dedicated
  approval of the exact wording. A general "fix it" or an approved risk block does not authorise it.
- **Never set a risk reviewer** — `reviewers` stays empty (`drata-fields.md` §7).
- **A policy is not evidence a control operates.** Name where each compensating control was verified, or
  ask, or write it as a gap.
- **Mandatory clauses (4–10) cannot be accepted** and take no risk entry: 10.2 corrective action
  (`Clause` + `Corrective`) or 6.2 objective (`Clause` + `Improvement`).
- **Never invent scoring or acceptance criteria**; above-threshold residual needs an escalated exception.
- **Policy renewal lapse is expected — never report it.** Policy edits are queued for one bulk
  promotion; the draft edit itself happens in the run.
- **Withdrawing a control rewrites the section, never deletes it.** A deferral (`"treated under DCF-x"`)
  must point at a control with a recorded position. **Document first, ticket second** when retiring a plan.
- **Risk language, not restated gaps.** One home per fact: scores and rationale in Drata, execution in
  `IRT`. Measurements go in snapshots (`ICR`/`IRT` comments), never durable fields.
- **Dates live in `IRT` only — and new `IRT` tickets are created with no `duedate`.** Original Estimate
  (hours, `Task` only) is mandatory; dates come from the board-wide prioritisation pass
  (`labels = PrioritisationPass`). Never propose a `duedate`; `anticipatedCompletionDate` stays blank;
  `treatmentDetails` carries the `IRT` key and recovery query, never a date.
- **Every Jira write is staged, then approved; re-read immediately before each update and send only the
  changed fields** (`editJiraIssue` replaces whatever you pass).
- **`CSIP` is read-only and never cross-referenced** — the durable handle is `DCF-xxx`.
- **Detect policy drift; never edit policy text.** `/isms-draft` writes it; the queue page
  (`compliance/isms-policy-queue.md`) is the only `security-documentation` file this skill edits.
- **Invoke downstream skills yourself** (`skill_view` / slash command) — `/bitpool-docs`, `/isms-draft` —
  never print "you should now run…" (`references/bitpool-context.md`). Never invoke `/isms-prod`.
- **When an output defect traces to a rule here, fix the rule before the output** — but over-specific text
  is `/bitpool-writing-standard`'s to calibrate (offer `/log-skill-divergence`), not a new rule here.
- **Never hardcode counts or statuses** — read them live. Default assignee / risk owner: see
  `references/bitpool-context.md` (durable text names the role, never the person).

## Pitfalls

- Walking one presumed route and presenting the result as the answer instead of offering paths.
- Offering acceptance or a "risk treatment plan" for a clause control.
- Lifting a control statement from a policy into `treatmentDetails` (the `DCF-5` peer-review failure).
- Trusting `flags.hasEvidence`, `flags.hasTicket` or the `ticket_status` filter — use the evidence list
  and a Jira query on `DCF-xxx`.
- Using search-mode `query` on Drata — it returns empty on this account; list mode, follow `cursor`.
- Framework tag `"ISO27001"` — silently empty; the tag is `ISO270012022`.
- Queuing a draft edit for later (`Draft edited: pending`) instead of invoking `/isms-draft` now.
- Wrapping Jira queue text in a blockquote — Jira's conversion silently drops it; read back what landed.
- Reporting an empty `IRT` `duedate` or blank `anticipatedCompletionDate` as drift — both are deliberate.
- Closing `ICR` over corrections still only in the working tree — "landed" means on `origin/main`.
- Copying a date from a wiki mirror or an evidence `renewalSchema`.
- Writing a `C:\…\Github - Bitpool` (with spaces) path — it does not exist.

## Verification

- Every Drata/Jira write was preceded by an approved block and its returned record was read back
  (`riskId`, `owners`, empty `reviewers`).
- Every new `IRT` ticket has a label, an Original Estimate, no `duedate`, and a `Date constraint:` line.
- Any drift found has an `/isms-draft` edit made and a linked queue row; the page is left for the user to
  commit and push.
- The `ICR` ticket carries a dated comment from this run and is closed, held or marked in progress.
- The durability check sits under every block staging durable text.

## Reference files

| File | Covers |
|---|---|
| `references/golden-rules.md` | Full golden rules: write model, writing-standard output → profile table, control-text correction gate, approval blocks, dates, Jira write discipline, CSIP, drift |
| `references/bitpool-context.md` | Invoking downstream skills; repo paths; Bitpool's three estates; register ids, enums, scoring; Jira projects (`IRT`, `ICR`, `CYB`, `CSIP`); default assignee |
| `references/workflow.md` | Steps 0–11 in full, including the `ICR` audit-ready gate and endings |
| `references/policy-queue.md` | Batched policy changes: the queue ticket and page, writing a row, index rules |
| `references/audit-and-integration.md` | Audit mode and how this skill hands to and from other skills |
| `references/treatment-decisions.md` | Clause/Annex A gate, ISO treatment options, scenarios, wording templates, §7 paths format |
| `references/drata-fields.md` | Drata field map, §2 write model and flags, §4 risk approval block, §7 `Drata_createRisk` constraints |
| `references/irt-tickets.md` | `IRT` project: naming, labels, description template, kinds, subtasks, Original Estimate, retiring |
| `references/icr-closure.md` | The audit-ready gate: checks, carriers, not-ready flags, the rule it replaced |
| `references/policy-alignment.md` | Where policies live, ownership, drift categories, `/isms-draft` handoff format |
| `references/hygiene-sweep.md` | Audit-mode checks and queries |
| `references/documentation-index.md` | 2026-08-21 snapshot of policies/procedures by domain — an absent entry is a candidate gap, not a confirmed absence |
