---
name: drive-iso27001
description: "Use when driving ISO 27001 work: Drata, Jira, docs, AWS."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, iso27001, isms, drata, jira, aws, compliance, security]
    category: bitpool
    related_skills: [ask-drata, aws-context, aws-query, drata-control-insights, manage-drata-control, isms-draft, isms-prod, bitpool-docs, bitpool-writing-standard, change-request, update-devsecops-ticket]
---

# Drive ISO 27001

A repeatable "sit down and drive the ISO 27001 project forward" command. It reconciles **Drata**
(what the framework needs, READ-ONLY), **Jira** (CSIP plus security-labelled OP/BT — the work to
satisfy it), **GitBook** (whether the supporting documentation exists) and **AWS** (live, read-only
infrastructure state), keeps a persistent auditable worklog in a synced SharePoint folder, and always
proposes a prioritised next-actions plan before doing anything. Bounded to ≤5 controls per session.

## When to Use

- The user runs `/drive-iso27001` (full session), or `/drive-iso27001 DCF-xxx` to focus one control.
- Proactively, on a **security-programme** meeting transcript with a request to update CSIP
  (transcript mode).
- Mid-session, when the question becomes "what's the risk, cost and effort of this change?"
  (advisory mode).

Don't use for:
- A DevSecOps engineering transcript aimed at the OP board: use `/update-devsecops-ticket`.
- The user merely naming a DCF/CSIP key without asking to work on it — don't auto-run. Single-control
  visuals are `/drata-control-insights`.
- ISMS policy authoring or promotion: `/isms-draft`, `/isms-prod`.
- Raising a change-management ticket: `/change-request` (this skill only recommends one).

## Prerequisites

- **Drata** and **Atlassian (Jira)** MCP servers connected in Hermes (`hermes mcp add ...` or
  `manage_connections`); **GitBook** MCP too if available. Tool names used in the references
  (`Drata_searchControls`, `searchJiraIssuesUsingJql`, `createJiraIssue`, ...) are those servers'
  tools — find them with `tool_search` if names differ. AWS is optional (`/aws-context`, `/aws-query`).
- `/bitpool-writing-standard` (section `bitpool-general`) installed — rule 9.
- The synced SharePoint folder **Cyber Security - Documents → General → Claude files** (the folder's
  real name). It syncs under the user's OneDrive org folder `Bitpool Pty Ltd/`. Missing → tell the
  user to sync it, and stop.

## Procedure

Full step detail is in `references/iso27001-session-playbook.md`; read it with `read_file` before
pulling any snapshot. Read `references/iso27001-drata-mapping.md` before writing JQL and
`references/aws-evidence-map.md` before offering any AWS check. Read the whole file you reach for.

1. **Locate the state directory fresh** (rule 1) with `search_files` (target files) or `terminal`,
   using a username wildcard under the users' home root, e.g.
   `ls -d /c/Users/*/Bitpool\ Pty\ Ltd/Cyber\ Security\ -\ Documents/General/Claude\ files`.
   Done when an absolute path resolves — or you've told the user to sync it and stopped.
2. **Load prior context** — tail of `_STATE/worklog.md`, `_STATE/task-queue.md`,
   `_STATE/control-index.md` (create from `references/iso27001-state-files.md` on a first run).
   Done when a 3-5 line "where we left off" summary is written.
3. **Pull a bounded snapshot** in parallel — Drata (read-only) unhealthy controls and failing tests,
   CSIP and security-labelled OP/BT via JQL, documentation coverage from
   `references/documentation-index.md`; tag infra-relevant controls **without** querying AWS. Large
   results go to a file and are parsed (jq/python or a `delegate_task` subagent). Consult
   `/ask-drata` before concluding a Drata record is absent. Done when each source has a snapshot.
4. **Reconcile and prioritise** on DCF/domain, in CSIP stage order, flagging exceptions (no ticket,
   no DCF, no doc, no evidence/owner, infra-relevant with no monitor). Done when
   `_STATE/control-index.md` is refreshed.
5. **Recommend next actions** and offer choices (playbook step 4); wait for the user to choose.
   Done when the user has picked — nothing written, no AWS queried yet.
6. **Run approved AWS checks only if chosen** via `/aws-context` (once) and `/aws-query`, ≤12 calls
   per control; record each as in place / gap / not checked with date. Done when every approved
   check has a recorded result.
7. **Deep-dive ≤5 chosen controls** and write `controls/DCF-xxx.md`. Done when each has a gap-to-done.
8. **Stage Jira changes for approval** in groups, with one durability check under the staged
   durable text (rule 9). Done when the user approves all, by group, or amends.
9. **Execute approved Jira writes** only. Done when each write returned a key or success.
10. **Close out** — append the worklog session block, refresh the task queue and control index, give
    the user a concise changelog. Done when all three state files are updated.

Focused, advisory and transcript modes are in `references/iso27001-driver-overview.md` (*The four
modes*) and the playbook's *Transcript mode*.

## Load-bearing rules

Restated here because each one prevents an unauthorised write, an unbounded session, or a wrong conclusion.

1. **Locate the state directory fresh every run**, with a username wildcard
   (`…\Bitpool Pty Ltd\Cyber Security - Documents\General\Claude files` under any user). If it
   doesn't resolve, **stop** and tell the user to sync **Cyber Security - Documents → General →
   Claude files**.
2. **Drata is READ-ONLY — no write verb, named or unnamed.** Never call any `Drata_create*` or
   `Drata_update*` verb from this skill, **including `Drata_createRisk` and `Drata_updateRisk`**. This
   is default-deny and covers verbs that do not exist yet. It has to be, because OAuth scope is
   **account-level**: this skill is handed exactly the same write verbs as `/manage-drata-control`, and
   nothing in the connection will stop it — the restriction is policy, not capability. An earlier
   edition enumerated four control and evidence verbs, written before the risk-write scopes were
   granted, which left risk writes unforbidden by omission. **Do not reintroduce a list.** Drata edits
   are a deliberate human action in the Drata UI. The authority on which skill may write is the
   **"Drata write policy by skill"** table in `/ask-drata`.
3. **AWS is READ-ONLY and never automatic.** Tag which controls are infrastructure-relevant during
   the scan, then **ask before querying**. Call `/aws-context` once for the session check and
   `/aws-query` for the calls — never inline CLI commands, profile names or account IDs here.
4. **An AWS result is an observation, not evidence.** It informs the Jira work and tells the human
   what's worth attaching in Drata. It never satisfies a control by itself.
5. **Never write a Jira change without staged approval.** Stage, get a yes, then execute.
6. **Never author or edit ISMS policy content.** Redirect to `/isms-draft` and `/isms-prod`.
   - **6a. Policy work goes to the policy queue — never a promotion task, never a lapse finding.**
     Bitpool decision, 2026-08-24: policy drafts are edited continuously and promoted **once, in
     bulk**, after the control review programme resolves.
     - **Never raise a "promote policy X" task.** One standing `Task` in `IRT` labelled `PolicyQueue`
       holds every pending change as **a comment carrying the detail, indexed by a row on its page**
       in `security-documentation` (`compliance/isms-policy-queue.md`). Find it with
       `project = IRT AND labels = PolicyQueue`, and hand the drift to `/manage-drata-control`, which
       owns the queue and claims the row before posting the comment — this skill writes only to Jira
       and its SharePoint state files. **Never write anything row-related into the ticket's
       description.** A second promotion ticket is a duplicate commitment, not coverage.
     - **Never report a lapsed `renewalDate` or a null `approvedAt` as a finding, a risk, or a
       bottom-line row.** Between bulk promotions that is the *expected* state; the user has asked to
       stop hearing it. Read policy content freely; say nothing about policy dates.
7. **Bounded batch: ≤5 controls deep-dived per session, ≤12 AWS calls per deep-dived control.**
   Scan broadly; act narrowly.
8. **Every new task or sub-task cites a DCF** in its description — `Related DCF: DCF-xxx`, by code
   only (the control's name is a Drata field and can change), or an explicit "unable to match" line.
   Prefer updating an existing issue over creating a new one.
9. **Text for a registered target follows `/bitpool-writing-standard`.** Two outputs land in its register:
   - **CSIP** task and sub-task summaries and descriptions — new, edited, or drafted from a
     transcript → profile **Security Jira**.
   - **Drata evidence it suggests** a person attach in the Drata UI, wherever it drafts the bucket's
     name or description → profile **Security Drata** (§3.1). Text drafted in chat to paste into
     Drata is still Drata text.

   Before drafting either, load the standard with `skill_view`: its `SKILL.md` (target gate, six core
   rules), then the named profile. Every approval block staging that text shows the standard's
   durability check (`bitpool-writing-standard/references/durability-check.md` §1) directly under it. Comments on CSIP and
   IRT tickets are snapshots and stay specific: counts, account names, observation dates and meeting
   attribution go in the dated comment staged with the change (for a new ticket, the creation
   comment) and the worklog. Specific is not unrestricted: security-sensitive identifiers go to a
   restricted home (the GRC evidence library) and the comment points there (Security Jira §3.5).
   Outside the register: the SharePoint state files and worklog, the chat plan and advisory, and OP
   and BT (read only for security-labelled work; never comment on another team's ticket for ISO
   needs). `/bitpool-docs` writes any documentation hand-off.

   **If `/bitpool-writing-standard` isn't installed, stop and tell the user once per chat:**
   *"`/bitpool-writing-standard` isn't installed, so the Security Jira and Security Drata writing
   profiles can't be applied. Installing it (section `bitpool-general`) is recommended. Proceed
   without it?"* Continue only on a yes; don't ask again in the same chat.

## Pitfalls

- **Concluding a Drata record is absent** from a `query`-mode search — unreliable on this account; check `/ask-drata`.
- **Reading a huge JQL result inline** — CSIP descriptions blow the token cap; parse the saved file.
- **Querying AWS during preflight** or before the user picks it — wastes a sign-in prompt.
- **Letting "not checked" read as "in place"**, or acting on a stale dated observation without re-querying.
- **Treating a documentation-index miss as a confirmed gap** — it's a 2026-08-21 snapshot; confirm with the user.
- **Putting counts, account names or meeting attribution in a CSIP description** — they go in the dated comment.
- **Calling any Drata write verb** because the connection allows it.

## Verification

- No Drata write verb was called; Jira writes match exactly what the user approved.
- ≤5 controls deep-dived; ≤12 AWS calls per control; every AWS check recorded with a date.
- Every new task/sub-task description carries a `Related DCF:` line.
- `_STATE/worklog.md`, `_STATE/task-queue.md` and `_STATE/control-index.md` updated this session.

## Reference files

Read the file itself — the table is an index, not a substitute.

| File | Covers |
|---|---|
| `references/aws-evidence-map.md` | Which read-only AWS checks evidence which control domain, the relevance test, per-control call budgets, and the risk/cost/effort advisory shape. Shared with `/drata-control-insights`. |
| `references/iso27001-drata-mapping.md` | DCF to CSIP resolution, Drata status semantics, and the JQL library. |
| `references/iso27001-driver-overview.md` | Golden rules, the Bitpool Jira and Drata context, CSIP stage prioritisation, the state directory, and the four modes. |
| `references/iso27001-session-playbook.md` | The full step-by-step session playbook — locate state, bounded snapshot, reconcile, recommend, execute approved writes, transcript mode. |
| `references/iso27001-state-files.md` | Schemas for the worklog, task queue, control index and per-control note files. |
| `references/documentation-index.md` | Which policies and procedures exist, by control domain. A 2026-08-21 snapshot — an absent domain is a candidate gap, never a confirmed absence. |

Golden rules, context, modes → `references/iso27001-driver-overview.md`. Session steps → the
playbook. JQL and DCF↔CSIP → the mapping. State schemas → the state-files reference. What text for a
registered target may say → `/bitpool-writing-standard`, never this skill. AWS mappings, budgets and
the advisory shape → `references/aws-evidence-map.md`, shared with `/drata-control-insights` — extend
it rather than either skill.
