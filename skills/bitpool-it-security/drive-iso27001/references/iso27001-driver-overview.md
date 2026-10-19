# ISO 27001 Driver — Overview

A repeatable "sit down and drive the ISO 27001 project forward" command. It reconciles **Drata**
(what the framework needs), **Jira** (the work to satisfy it), **GitBook** (whether the supporting
documentation exists), and **AWS** (what the infrastructure actually looks like right now), keeps a
persistent auditable worklog, and always proposes a prioritised next-actions plan before doing
anything.

## Golden rules

> **Important**
> - **Drata is READ-ONLY — no write verb, named or unnamed.** Never call any `Drata_create*` or
>   `Drata_update*` verb from this skill, **the risk verbs included**. Default-deny, not a list:
>   OAuth scope is account-level, so the driver holds the same write verbs as
>   `/manage-drata-control` and the connection will not refuse them — the restriction is policy,
>   not capability. Drata edits are a deliberate human action in the Drata UI. The driver reads
>   Drata and writes only to **Jira** (with approval) and the local worklog. Policy authority: the
>   **"Drata write policy by skill"** table in `/ask-drata`.
> - **AWS is READ-ONLY and never automatic.** The access is view-only by design.
>   **Identify** which controls are infrastructure-relevant during the scan, then **ask before
>   querying** — a session touches up to 5 controls across every account in the Organization, so
>   unprompted fan-out is slow and noisy.
> - **An AWS result is an observation, not evidence.** It informs the Jira work and tells the human
>   what's worth attaching in the Drata UI. It never satisfies a control by itself, and it is never
>   a substitute for a Drata test.
> - **Never write a Jira change without staged approval.** Stage every proposed change, get a yes,
>   then execute.
> - **Text for a registered target follows `/bitpool-writing-standard`.** CSIP summaries and
>   descriptions → writing profile **Security Jira**; a
>   suggested Drata evidence name or description, drafted for a person to paste → **Security
>   Drata** (§3.1). Load the standard before drafting them, and show its durability check under the
>   staged text. Comments and the worklog are snapshots and stay specific; the chat advisory, the
>   state files and OP/BT are outside the register. The full rule, including what to do when the
>   standard isn't installed, is load-bearing rule 9 in `SKILL.md`.
> - **Never author or edit ISMS policy content** anywhere. Policies belong to `/isms-draft` and
>   `/isms-prod`. Redirect if asked.
> - **Bounded batch:** scan broadly, but deep-dive or act on **≤5 controls per session**. AWS adds
>   its own cap: **≤12 calls per deep-dived control**.


Query construction is **not** the driver's job — `/aws-context` runs the session check once and
`/aws-query` builds the calls. Never inline CLI commands, profile names or account IDs into the
driver.

## Bitpool context — reused across the security skills

- **Jira Cloud ID:** `bitpool.atlassian.net`
- **Projects:** `CSIP` (all issues); `OP` (board 98) and `BT` (board 82) filtered to
  `labels = security`. *The `security` label isn't adopted yet, so OP/BT queries return empty for
  now — run them anyway so they light up automatically once labels are applied.*
- **CSIP transitions:** Done = `41`, In Progress = `31`, To Do = `21`
- **Issue types:** `Task` (standalone), `Sub-task` (child of a Task)
- **People:** the roles this skill assigns or routes work to, with their Jira account IDs, are one
  table in [Drata & Jira Mapping](iso27001-drata-mapping.md) §4 — the only place the skill's
  instructions name them, apart from the illustrative examples in the
  [State File Schemas](iso27001-state-files.md) templates, which are snapshots.
- **DCF ↔ CSIP linkage:** the Drata control id is embedded in the CSIP parent title
  `Drata | Bitpool | DCF-xxx | [Control Name]`. Find a control's ticket by searching Jira for the
  `DCF-xxx` string. Drata's own `flags.hasTicket` also tells you whether a control has a linked
  ticket at all — `false` means no CSIP ticket yet, which is an action item.
- **AWS:** one Organization, reached through IAM Identity Center SSO with a view-only permission
  set. The account list, how many accounts there are, profile names and CLI mechanics live in
  AWS Querying (see the `/aws-query` skill) — not restated here. The driver only needs to know that
  infrastructure state is queryable read-only, and that the [AWS Evidence Map](aws-evidence-map.md)
  says which query answers which control.

### CSIP stage semantics → prioritisation order

CSIP uses these stages, worked in this order:

1. **`In Progress`** — started; drive to completion first.
2. **`To Do`** — new tasks and sub-tasks, likely ready but unconfirmed; pick up next.
3. **`Ready`** — vetted backlog, ready to work to completion.
4. **`Re-assess`** — needs re-evaluation, a large bucket. **Low priority** — only triage once
   buckets 1–3 are nearly clear.
5. **`To Discuss`** — needs an initial direction chat before real work, with the **`To Discuss`
   direction** role in [Drata & Jira Mapping](iso27001-drata-mapping.md) §4. Help here only once
   the earlier buckets are low; the driver's job on these is to prep the discussion, not to
   execute.

**`Waiting`** — blocked on something external. Actively surface it and propose a follow-up to
unblock it (a chase task, or a comment on the CSIP ticket — never on another team's OP/BT ticket,
per `SKILL.md` rule 9) rather than leaving it idle. **`Done`** — ignore.

The full status table and per-stage JQL are in [Drata & Jira Mapping](iso27001-drata-mapping.md).

## State directory — SharePoint "Claude files"

Locate it fresh every run with a **username wildcard**, since OneDrive sync paths vary:

```
C:\Users\*\Bitpool Pty Ltd\Cyber Security - Documents\General\Claude files
```

Use `search_files` (target files) or `terminal` to resolve the real path.

> **Warning**
> **If it doesn't resolve, stop** and tell the user:
>
> > The ISO 27001 working folder isn't synced locally. Open OneDrive/SharePoint and sync
> > **Cyber Security - Documents → General → Claude files**, then re-run `/drive-iso27001`.


The driver reads and writes its state under that folder — see
[State File Schemas](iso27001-state-files.md):

- `_STATE/worklog.md`, `_STATE/task-queue.md`, `_STATE/control-index.md`
- `controls/DCF-xxx.md` per deep-dived control

On the first ever run these won't exist — initialise them. Also scan sibling folders for prior
context: `..\Claude ISO27001 Project Review\` (CSIP/OP reports) and
`..\New cyber plan\Meeting transcripts\`.

## The four modes

### Default

`/drive-iso27001` — the full session. See the [Session Playbook](iso27001-session-playbook.md) for
the step detail: locate state → load prior context → pull a bounded snapshot → reconcile and
prioritise → recommend next actions → run approved AWS checks → execute approved Jira writes →
update state files.

### Focused

`/drive-iso27001 DCF-xxx` — one control.

1. Resolve **DCF-xxx → CSIP ticket** (search Jira for the string; `getJiraIssue` for detail).
2. Pull that control's Drata detail (read-only) plus `Drata_listEvidence`; read
   `controls/DCF-xxx.md` if present.
3. Check GitBook for supporting documentation; note gaps.
4. **Apply the AWS relevance test** from the [AWS Evidence Map](aws-evidence-map.md).
   Infrastructure-relevant → say which checks you'd run and ask; on a yes, run them within the
   ≤12-call budget. Not relevant → say "not an AWS question" and move on. One focused control is
   the cheapest case for the check, so lean toward offering it.
5. Summarise status, blockers and gaps, then drive it to completion: stage ticket changes for
   approval, offer the `/drata-control-insights` matrix, route any doc gap to `/bitpool-docs`.
6. Update `controls/DCF-xxx.md` — including AWS observations and their date — and the worklog.

### Advisory

Triggered inside a session when the question stops being *"where are we?"* and becomes *"what's the
risk, cost and effort of this change, and what should we do?"*

Answer using the advisory shape in section 6 of the [AWS Evidence Map](aws-evidence-map.md):

1. **Query the current state first** — advice not grounded in what's actually deployed is
   guesswork. Same rules: ask before querying, stay in budget.
2. **Effort** — a T-shirt size (S/M/L) derived from **real counts** (accounts affected, resources
   affected), not intuition.
3. **Blast radius** — name the accounts, and state explicitly whether production is one of them.
4. **Risk in both directions** — the risk of making the change *and* the risk of leaving it: the
   exposure the control exists to prevent, plus the audit consequence of it staying unevidenced.
5. **Cost** — directional by default. Attempt Cost Explorer **only if the user asks for dollars**;
   it's management-account-scoped and may be denied under view-only access. If denied, **say so** —
   never substitute an invented figure.
6. **Commit to one recommendation** with the cheapest de-risking next step. A survey of options
   isn't advice. "Don't do this yet" is a valid recommendation.

Then land it as work: stage the CSIP ticket or sub-task for approval as usual. The advisory is
chat and stays specific; the ticket does not copy it. Its description states the outcome and the
affected population (*"the account holding production workloads"*), and the named accounts, real
counts and observation date go in its dated creation comment, staged with the create, and the
worklog ([Session Playbook](iso27001-session-playbook.md) step 6). If the change touches production, note
that `/change-request` raises the change-management ticket.

### Transcript

If a `.vtt` or transcript is provided with a request to update Jira, run the transcript workflow in
the [Session Playbook](iso27001-session-playbook.md): chunked read → extract action items →
DCF-match → **stage** → execute → changelog.

Every new task or sub-task cites a DCF in its description:

```
Related DCF: DCF-xxx
```

or, if unmatched:

```
Related DCF: Unable to match — likely relates to [domain]. Please review and link manually.
```

The rest of the description follows [Session Playbook](iso27001-session-playbook.md) step 6: the
action as an outcome, and where its evidence will live. The meeting date, attendees and who the
transcript attributes the action to go in the creation comment and the worklog.

Prefer updating an existing issue over creating a new one, and never touch DCF-controlled parent
issues unless the transcript explicitly discusses them.

## Integration with the other skills

| Skill | Relationship |
|---|---|
| `/bitpool-docs` | Hand off all documentation output — procedures, control mapping, evidence-location notes. **Never** for ISMS policies. |
| `/isms-draft`, `/isms-prod` | The only path for ISMS *policy* documents. Redirect here if policy work comes up. |
| `/drata-control-insights` | The visual single-control matrix. Reads the same evidence map at a smaller budget: ≤2 domains, ≤6 calls. |
| `/aws-context` | The once-per-session AWS environment and identity check. |
| `/aws-query` | **The only place** AWS calls are constructed. The driver supplies the compliance question; that skill supplies the call. |
| `/bitpool-writing-standard` | Section `bitpool-general`. Governs what CSIP summaries and descriptions and suggested Drata evidence text may say — profiles **Security Jira** and **Security Drata**. Load it before drafting them; never restate its rules here. |
| `/manage-drata-control` | Owns the `IRT` policy queue. Policy drift the driver finds is handed to it, never queued by the driver (`SKILL.md` rule 6a). |
| `/change-request` | Raises the Jira change-management ticket when an infrastructure fix needs a controlled production change. The driver recommends and tracks; it doesn't raise change tickets. |
| `/update-devsecops-ticket` | Owns DevSecOps engineering-meeting transcripts destined for the OP (Perun) board, where the output is comments on tickets that already exist. This skill's transcript mode covers security-programme meetings destined for CSIP, where the output is issues that each cite a DCF. |
