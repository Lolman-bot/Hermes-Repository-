# ISO 27001 — State File Schemas

Everything the driver persists lives under the SharePoint working folder resolved at runtime:

```
…\Cyber Security - Documents\General\Claude files\
  _STATE\
    worklog.md          # append-only session journal
    task-queue.md       # living prioritised backlog between sessions
    control-index.md    # cached DCF ↔ CSIP ↔ status map
  controls\
    DCF-xxx.md          # per-control working note (one per deep-dived control)
```

Create `_STATE/` and `controls/` on first run if absent. These files are the audit trail — keep them tidy, dated, and factual. Use **absolute ISO dates** (the session date), never relative ("today"). Never store secrets or evidence *content* here — reference locations (Jira keys, GitBook page paths, Drata evidence names) instead.

**AWS observations follow the same rule.** Record the question, the summarised answer, and the observation date — counts and states, not resource inventories. Every AWS line is a **dated observation, not a standing fact**: infrastructure changes between sessions, so re-query before acting on anything recorded in a previous run.

**These files are outside `/bitpool-writing-standard`'s register** — they are working snapshots, and the counts, account names, people and dates in them belong here. They are also seed material, not ticket text: when a task-queue line or a *Gap to done* item becomes a CSIP task or sub-task, restate it as an outcome under the Security Jira profile, and carry its counts and names in the dated creation comment ([Session Playbook](iso27001-session-playbook.md) step 6).

---

## `_STATE/worklog.md` (append-only)

Newest entry at the **top**, under the heading. One block per session.

```markdown
# ISO 27001 Driver — Worklog

<!-- Newest first. Appended by /drive-iso27001. Do not rewrite history. -->

## 2026-07-14 — session
**Where we left off (start):** <1–2 lines>
**Controls touched:** DCF-76 (change mgmt), DCF-776 (access control)
**Jira changes:**
- Updated CSIP-712 — due date → 2026-07-28, assignee → Eric Sharp
- Created CSIP-820 (sub-task of CSIP-712) — "Document emergency change procedure" — Related DCF: DCF-76
**Decisions / notes:** <e.g. "DCF-164 needs Phil discussion re: scope">
**Doc gaps found:** DCF-776 has no GitBook procedure → queued doc task
**AWS checks (observed 2026-07-14):**
- DCF-776 — IAM users with active access keys: 3 in `aws-prod`, oldest 411 days → **gap**
- DCF-776 — root MFA enabled in every account in the Organization → in place
- DCF-421 — clock sync: not verifiable from view-only access → not checked
**Next up:** <the 3–5 things to start with next session>
---
```

AWS lines are omitted entirely when no checks were run — don't write "none run", just leave the field out.

---

## `_STATE/task-queue.md` (living backlog)

The between-sessions to-do list, re-ranked each run. Grouped by CSIP stage priority.

```markdown
# ISO 27001 Driver — Task Queue
_Last refreshed: 2026-07-14_

## In progress (finish first)
- [ ] DCF-76 / CSIP-712 — emergency change procedure doc + evidence
## To do (likely ready)
- [ ] DCF-776 / CSIP-733 — quarterly access review evidence
## Ready (vetted backlog)
- [ ] DCF-201 / CSIP-— — no ticket yet; create parent
## Re-assess (triage)
- [ ] DCF-421 / CSIP-677 — clock sync; confirm still valid after infra change
## To Discuss (direction chat)
- [ ] DCF-164 / CSIP-760 — scope of vendor review cadence
## Waiting (chase the blocker)
- [ ] DCF-xxx / CSIP-xxx — blocked on <external dependency>; next chase: <action>
## Exceptions
- No CSIP ticket: DCF-201, DCF-233
- No DCF on ticket: CSIP-655
- No GitBook doc: DCF-776 (access control)
```

---

## `_STATE/control-index.md` (cached map)

Refreshed each run so we don't re-search Jira/Drata from scratch. One row per control seen.

```markdown
# Control Index (DCF ↔ CSIP ↔ status)
_Last refreshed: 2026-07-14_

| DCF | Control name | CSIP key | CSIP stage | Drata status | GitBook doc | AWS state | Last touched |
|-----|--------------|----------|-----------|--------------|-------------|-----------|--------------|
| DCF-76 | Change Management | CSIP-712 | In Progress | Failing test | yes | in place (2026-07-14) | 2026-07-14 |
| DCF-776 | Access Control | CSIP-733 | To Do | Ready/no evidence | none | **gap** (2026-07-14) | 2026-07-14 |
| DCF-201 | Asset Management | — | — | Not ready | none | not checked | 2026-07-14 |
| DCF-93 | Security Awareness Training | CSIP-701 | Ready | Not ready | yes | n/a | 2026-07-14 |
```

`AWS state` values, and only these: `in place (date)` · `gap (date)` · `not checked` · `n/a` (not an
AWS question — physical/people/policy control). Carrying `n/a` deliberately is what stops the next
session re-running the relevance test on controls already ruled out.

---

## `controls/DCF-xxx.md` (per-control working note)

Written when a control is deep-dived. This is the single-control memory the focused mode reads first.

```markdown
---
dcf: DCF-76
control_name: Change Management
csip_key: CSIP-712
iso27001_clauses: ["A.8.32"]
drata_status: Failing monitoring test
csip_stage: In Progress
aws_state: gap
aws_observed: 2026-07-14
owner: Eric Sharp
last_reviewed: 2026-07-14
---

# DCF-76 — Change Management

## Current state
- Drata: monitoring test "changes reviewed" failing since 2026-06.
- Jira: CSIP-712 in progress; 2 open sub-tasks.
- GitBook: procedure exists at <path> / **missing**.

## Infrastructure (AWS — observed 2026-07-14)
- CloudFormation stacks last updated by pipeline principals in `aws-prod` → in place
- 4 EC2 instances in `aws-test` not SSM-managed → **gap** (changes there aren't observable)
- Not re-verified since 2026-07-14 — re-query before acting.

## Gap to done
- [ ] Emergency change procedure documented (route via /bitpool-docs)
- [ ] Evidence: last 3 changes with approval records attached in Drata (human, in Drata UI)
- [ ] Bring the 4 `aws-test` instances under SSM (effort S, no prod impact)

## Evidence locations (references only — no content stored here)
- Jira: CSIP-712, CSIP-820
- GitBook: <page path>
- Drata evidence item: "<name>"

## History
- 2026-07-14 — reviewed; created CSIP-820 for the procedure doc.
```

---

## Housekeeping rules

- **worklog.md** is append-only — never rewrite past entries.
- **task-queue.md** and **control-index.md** are rewritten each run (they're derived state); keep them short and current.
- Keep per-control notes under `controls/`, one file per DCF, named exactly `DCF-xxx.md`.
- If the folder isn't synced, none of this exists — that's why preflight stops early with the sync message.
