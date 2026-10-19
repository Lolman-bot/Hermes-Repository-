# ISO 27001 — Session Playbook

This is the detailed procedure the SKILL.md summarises. Follow it top-to-bottom for a default session; jump to the relevant section for focused or transcript mode.

---

## 0 — Preflight

1. **Resolve the state directory** with a username wildcard (paths differ per machine/OneDrive tenant):
   ```bash
   ls -d /c/Users/*/Bitpool\ Pty\ Ltd/Cyber\ Security\ -\ Documents/General/Claude\ files 2>/dev/null
   ```
   or `search_files` (target files) with pattern `C:\Users\*\Bitpool Pty Ltd\Cyber Security - Documents\General\Claude files`.
   - **Not found → STOP.** Tell the user to sync **Cyber Security - Documents → General → Claude files** in OneDrive/SharePoint, then re-run. Do nothing else.
   - Found → store the absolute path; everything below reads/writes under it.
2. **Confirm MCP availability.** This skill needs the Drata, Atlassian, and GitBook MCPs. If one isn't connected, note which and continue with what's available (e.g. Drata down → work from Jira + the cached `control-index.md`).
3. **Don't touch AWS yet.** No session check, no queries during preflight — AWS is offered in step 4 and only runs after the user picks it (step 4b). Running `/aws-context` before you know whether any control in scope is even infrastructure-relevant wastes a sign-in prompt.

---

## 1 — Load prior context ("where we left off")

- Read `_STATE/worklog.md` (tail — most recent 2–3 sessions), `_STATE/task-queue.md`, and `_STATE/control-index.md`. If any don't exist, this is a first run — create them from the templates in [State File Schemas](iso27001-state-files.md) after step 3.
- Skim sibling folders for prior artefacts (read-only, for context only):
  - `..\Claude ISO27001 Project Review\` — e.g. `CSIP_Report.html`, `OP_Report.html`, one-off control notes.
  - `..\New cyber plan\Meeting transcripts\` — past meeting material.
- Produce a 3–5 line **"where we left off"** summary: last session date, what was actioned, what was queued as next-up.

---

## 2 — Pull a bounded snapshot

Run Drata, Jira, and GitBook pulls **in parallel**. Keep it a snapshot, not a full export — we act on ≤5 controls this session.

### Drata (READ-ONLY)
- `Drata_searchControls` — filter to controls **not** in a healthy/ready state (see [Drata & Jira Mapping](iso27001-drata-mapping.md) for status semantics). Capture: control code (DCF-xxx), name, status/health, owner.
- `Drata_searchMonitoringTests` — surface **failing/needs-attention** automated tests; these are concrete, high-signal gaps.
- Do **not** pull evidence for everything — `Drata_listEvidence` is only for controls you actually deep-dive (step 5).
- If a result set is large, save it to a temp file and parse with a `delegate_task` subagent/jq rather than reading it all into context.

### Jira
- CSIP open issues via `searchJiraIssuesUsingJql` (see the JQL library in [Drata & Jira Mapping](iso27001-drata-mapping.md)), requesting `summary, description, status, issuetype, assignee, duedate, subtasks, parent, labels`.
- OP and BT security-labelled work (JQL in [Drata & Jira Mapping](iso27001-drata-mapping.md)). Expect **empty** until the `security` label is adopted — that's fine.
- Large result → save to file, extract a flat list (key, summary, status, stage, assignee, subtasks) via a `delegate_task` subagent/jq.

### Documentation coverage
- Look up the domains represented in the outstanding controls (e.g. "access control", "change management", "backup", "incident response") in [Documentation Index](documentation-index.md). Note which domains already have a policy, which have a procedure, and which have neither — a **missing procedure is an action item**.
- The index is a snapshot. Record an absent domain as a *candidate* gap and confirm it with the user before it becomes a worklog finding — a page added since the snapshot would otherwise be reported as missing.

### AWS — tag only, do not query yet
- Apply the relevance test in [AWS Evidence Map](aws-evidence-map.md) (section 2) to each candidate control and **tag** it infrastructure-relevant or not. This is a reading exercise against the control description — **zero AWS calls at this stage**.
- Rank the tagged ones by how much a query would tell you that nothing else can:
  1. Infra-relevant **and** `isMonitored: false` — Drata has no automated test, so current state is otherwise unknown. **Highest value.**
  2. Infra-relevant **and** `hasEvidence: false` — a query tells the human what's worth attaching in the Drata UI.
  3. Infra-relevant with a **failing** Drata monitoring test — the query pinpoints *what* is failing.
  4. Infra-relevant and otherwise healthy — lowest value; usually skip.
- Carry these tags into step 3's reconciliation and step 4's offer.

---

## 3 — Reconcile & prioritise

Build one ranked action list by joining the three sources on DCF/domain:

- **Match** each outstanding Drata control to its CSIP ticket (DCF string search, or `flags.hasTicket`). Record the CSIP **stage**.
- Order by stage priority: **In Progress → To Do → Ready → Re-assess → To Discuss** (see [Drata & Jira Mapping](iso27001-drata-mapping.md)). `Re-assess` is low — only triage once In Progress/To Do/Ready are nearly clear. Within a bucket, prefer controls with failing Drata monitoring tests (concrete, fast wins) and controls nearest to done.
- **`Waiting` items:** surface them and propose a follow-up to unblock (a chase task, or a comment on the CSIP ticket — never on another team's OP/BT ticket, per `SKILL.md` rule 9) — don't leave them idle.
- **Flag exceptions explicitly** — these are the highest-value findings:
  - Drata control with **no CSIP ticket** (`flags.hasTicket:false`) → propose creating one (`Drata | Bitpool | DCF-xxx | [Name]` parent).
  - CSIP ticket with **no DCF reference** → propose linking it.
  - Control/ticket with **no GitBook documentation** → propose a doc task routed via `/bitpool-docs`.
  - Ready control with **no evidence** (`flags.hasEvidence:false`) or **no owner** (`flags.hasOwner:false`) → note the specific gap.
  - **Infrastructure-relevant control with no Drata monitor** (`isMonitored:false`) → propose the live AWS check. Nothing in Drata, Jira or GitBook knows the current state of that control's infrastructure; this is the gap class the AWS integration exists for.
- Refresh `_STATE/control-index.md` with the reconciled map (see [State File Schemas](iso27001-state-files.md)), including the `AWS state` column.

---

## 4 — Recommend next actions

Present a short, scannable plan (not a data dump):

- **"Where we left off"** (from step 1).
- **Top recommendations** — the ranked shortlist (aim for the 5 you'd tackle), each as: `DCF-xxx / CSIP-nnn — [stage] — one-line what-to-do`.
- **Exceptions** — the no-ticket / no-DCF / no-doc flags, plus the infra-relevant/no-monitor set.
- **Offer choices:** (a) deep-dive up to 5 controls now, (b) create/update CSIP tickets, (c) render `/drata-control-insights` for one, (d) route a doc gap via `/bitpool-docs`, (e) prep a `To Discuss` item for its direction chat, (f) **check live AWS state** for the tagged controls.

For (f), make the offer specific enough to answer: name the controls, and for each say in one line what would be queried — e.g. *"DCF-xxx (backup): AWS Backup plans + recent job status, RDS retention — ~4 calls in prod."* A vague "want me to check AWS?" can't be answered well.

Wait for the user to choose. Do not start writing to Jira yet, and do not query AWS yet.

---

## 4b — Run approved AWS checks (only if chosen)

Skip this whole step if the user didn't pick (f) or a deep-dive on an infra-relevant control.

1. **Session** — run `/aws-context` **once**. If there's no session and the user doesn't want to sign in, mark every AWS item **not checked** and continue the session normally; nothing downstream depends on AWS.
2. **Construct and run via `/aws-query`** — it owns the account list, profiles, the single multi-account loop, and the JMESPath traps. Take the *what* from [AWS Evidence Map](aws-evidence-map.md); take the *how* from `/aws-query`. **Never write CLI commands, profile names, or account IDs into this skill or its references.**
3. **Budget: ≤12 calls per control.** Production first, then the account owning the resource class, then org-wide accounts for genuinely org-wide controls (CloudTrail, Organizations, Identity Center, SCPs). Save large result sets to a file and parse — never read a full JSON dump into context.
4. **Record each check** as **in place** / **gap** / **not checked**, with the question asked, the observed result, and the observation date. Never let *not checked* read as *in place*.
5. **A failure is one of two kinds** (per `/aws-query`): session/identity → back to `/aws-context`; query-construction → fix the call. Classify before retrying, and don't retry the same failing call more than once.
6. **Turn gaps into candidate work** — a gap joins the ranked action list like any other finding, and becomes a staged Jira item in step 6. The ticket states the outcome that closes the gap; the observation behind it — the counts, the accounts, the date — goes in its dated creation comment, staged with the create, and the worklog, never the description (step 6). If the user asks what closing it would take, use the advisory shape in section 6 of [AWS Evidence Map](aws-evidence-map.md).

---

## 5 — Deep-dive (per chosen control, ≤5)

For each control the user picks:
1. `getJiraIssue` the CSIP ticket (full description, subtasks, comments if useful).
2. Drata (read-only): control detail + `Drata_listEvidence` to see what proof exists / is missing.
3. Documentation: look the control's domain up in [Documentation Index](documentation-index.md) for the supporting policy or procedure. It's a snapshot — a domain with no entry is a *candidate* gap to raise with the user, not a confirmed absence.
4. **AWS** (if infra-relevant and approved): the checks from [AWS Evidence Map](aws-evidence-map.md), per step 4b. If it isn't infra-relevant, record "not an AWS question" so the next session doesn't re-litigate it.
5. Determine the concrete gap-to-done: missing evidence, an undocumented procedure, an unassigned owner, a stale due date, a needed sub-task, a **live infrastructure gap**, or a point for the `To Discuss` direction chat. For missing evidence, say what's worth attaching in the Drata UI. If you draft the bucket's name or description for the human to paste, write it under the **Security Drata** profile (§3.1) of `/bitpool-writing-standard` — the artefact's shape, never the values seen today — and show the durability check under the draft.
6. Write/refresh `controls/DCF-xxx.md` (schema in [State File Schemas](iso27001-state-files.md)), including the AWS observations and their date.

---

## 6 — Stage changes for approval

Group proposed Jira writes and present **before executing anything**:

- **Group 1 — Updates to existing issues:** key + summary, field, new value. A dated fact — an observation, a decision, a chase — is a new comment, not a description rewrite. Where a description is corrected, the new text replaces the old and the reason goes in a comment.
- **Group 2 — New sub-tasks on existing parents:** parent key, sub-task summary and description, assignee, due date, `Related DCF`.
- **Group 3 — New tasks:** summary, description (incl. `Related DCF`), assignee, due date, and why no existing issue fit.
- **Creation comments** — for a Group 2 or 3 item prompted by an AWS observation, a deep-dive or a meeting, the dated comment carrying that basis, staged with the create in the same approval.

**CSIP summaries and descriptions are durable text** under the **Security Jira** writing profile — load `/bitpool-writing-standard` first (`SKILL.md` rule 9). For this skill that means:

- The **summary** names the outcome, or the object the ticket exists to act on.
- The **description** states what must be true when the work is done, the `Related DCF` line, and where the evidence will live — the artefact kind and the control it attaches to.
- **Policy drift is not staged here.** It goes to `/manage-drata-control`, which owns the `IRT` policy queue (`SKILL.md` rule 6a).
- **Counts and states — never inventories — account names, observation dates and meeting attribution** go in the dated creation comment, staged with the create, and the worklog. That includes the advisory's named accounts and real counts: in a description, the affected scope is a population — *"the account holding production workloads"*, *"every account in the AWS Organization"*. Specific is not unrestricted: security-sensitive identifiers go to a restricted home (the GRC evidence library), and the comment records the finding and points there (Security Jira §3.5).
- A *Gap to done* item or task-queue line is seed material, not ticket text — restate it this way before staging.

Under the staged summaries and descriptions, show **one durability check** for the whole block, in the format the standard's `references/durability-check.md` §1 sets. Comments are snapshots and are not checked.

The user may approve all, approve by group, or amend individual items. **Nothing is written to Jira until approved.** (Reminder: no Drata writes ever.)

---

## 7 — Execute approved Jira writes

- Look up any unknown account IDs (`lookupJiraAccountId`).
- `editJiraIssue` for field edits; `createJiraIssue` for new tasks/sub-tasks (**sub-tasks must set `parent`**); `transitionJiraIssue` for status.
- **Sequencing:** create parent Tasks first, collect keys, then their sub-tasks.
- **Creation comments:** post each approved one with `addCommentToJiraIssue` once its issue's key is back.
- **Hierarchy fallback:** if a Sub-task create fails on a parent error, try the grandparent Task; if that fails, create standalone and note the deviation.
- If the user says an item is already done, create it then transition to Done (`41`).

---

## 8 — Close out the session

- Append a session block to `_STATE/worklog.md` (date, controls touched, tickets created/updated with keys, decisions, next-ups, **AWS checks run and what they observed**).
- Refresh `_STATE/task-queue.md` (remove done, add new next-ups, re-rank).
- Ensure `_STATE/control-index.md` reflects the latest DCF↔CSIP↔status map, including the `AWS state` column.
- Give the user a concise changelog: updates, new sub-tasks, new tasks, deviations, and what's queued for next time.

**Recording AWS observations:** log the question, the answer, and the date — counts and states, not inventories. "GuardDuty enabled in `<n>` of `<m>` accounts (missing in `<account>`), observed `<date>`" belongs in the worklog, or in the dated creation comment of a ticket it prompts — never in a CSIP description (step 6); a dumped list of every security group belongs in none of them. Per [State File Schemas](iso27001-state-files.md), these files reference locations and observations, never resource data. And an observation is stamped with its date for a reason — a check from three sessions ago is context, not current state; re-query before acting on it.

---

## Transcript mode (folded in from security-meeting-to-jira-tasks)

Trigger: a `.vtt`/transcript is provided with a request to update Jira / capture action items.

1. **Read the transcript in chunks** (1500 lines via `offset`/`limit`). Extract meeting date, attendees, every action item + owner + any deadline, and explicit CSIP-xxx refs. If too large, delegate to a subagent (`delegate_task`) for a structured action-item list.
2. **Fetch open CSIP issues** (JQL in [Drata & Jira Mapping](iso27001-drata-mapping.md)), in parallel with the read.
3. **Cross-reference & plan** — priority: update existing → add sub-task to existing parent → create new task. Consider full descriptions, not just titles. **Do not touch** DCF-controlled parents unless the transcript explicitly discusses them.
4. **DCF referencing (required for every new task/sub-task):** use a DCF named in the transcript; else match against a `Drata | Bitpool | DCF-xxx` parent by subject; else use the unmatched form, `Related DCF: Unable to match — likely relates to [domain]. Please review and link manually.` Put it in the **description**.
5. **Stage → approve → execute → changelog**, exactly as steps 6–8 above — including step 6's split: the description carries the action as an outcome; the meeting date, attendees and the transcript's attribution go in the dated creation comment, staged with the create, and the worklog.
6. **Log it** in `_STATE/worklog.md` and note the transcript filename for traceability.

**Defaults:** assignee = the **default assignee** in [Drata & Jira Mapping](iso27001-drata-mapping.md) §4 unless clearly attributed otherwise; due dates from the transcript, else immediate=1wk / short=2wk / medium=3–4wk / long=6–8wk; skip duplicates already captured in a recent open issue; non-Jira attendees → assign to the default assignee, and record the transcript's attribution in the creation comment and the worklog, never the description.
