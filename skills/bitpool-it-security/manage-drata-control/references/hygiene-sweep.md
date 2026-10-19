# Register hygiene sweep (`/manage-drata-control audit`)

Individual treatment decisions can each be sound while the register as a whole is indefensible. This
mode sweeps for the structural defects — the ones an auditor finds by reading down a column rather
than by examining any single entry.

**Risk-field fixes may be applied; everything else is staged.** A null residual, a missing control
link or a `treatmentDetails` correction can go in with `Drata_updateRisk` after one approval block
covering the batch. See `drata-fields.md` §2 for exactly what this skill may write.

**Text this mode drafts for Drata, `IRT` or the policy queue page follows `/bitpool-writing-standard`
— load it first.** Four of its outputs land in registered targets of Bitpool's writing standard:

| Output | Target | Writing profile |
|---|---|---|
| `treatmentDetails` or `description` corrections in the batched `Drata_updateRisk` | Drata risk register | **Security Drata** |
| Drafted rewrites of an evidence `name` or `description`, or of a customised control description (checks 10 and 12) | Drata evidence library, controls | **Security Drata** |
| A policy-queue detail or correction comment (check 8), an `IRT` summary or description rewrite (check 12), and the dated comment that records each Drata-side change | Jira `IRT` (and `ICR` for that comment) | **Security Jira** |
| A policy-queue page row, Status note or At promotion step (check 8) | `security-documentation` — the queue page | **Security Documentation** — register content |

Before drafting any of them, load the standard — its `SKILL.md` for the target gate and the six core
rules, then the named profile. The batch approval block shows **one durability check** directly
under the staged durable text (the standard's `references/durability-check.md` §1). Structured values
in the same batch — residual scores, control links, the emptied `reviewers` list — are their own
home and are not checked. Because Drata keeps no readable history of a risk, the same block stages
the dated comment recording each score or `treatmentDetails` change: what changed, why, and on whose
decision (core rule 6). It goes on the risk's `IRT` ticket where one exists, otherwise on the `ICR`
ticket of a control this run reviewed; audit mode usually reviews none, so where this skill can
write neither, stage the comment for the user to post and say so in the block — a change is never
made without its record staged. That comment is a snapshot, so it stays specific. Everything else
this mode produces — the findings table, the report to the user, the worklog, anything read from
`CYB` — is outside the register: no check, and none shown.

**Requires `/bitpool-writing-standard` (section `bitpool-general`).** Before drafting text for Drata,
Jira `IRT` or the policy queue page, load it. If it is not installed, **stop and tell the user once
per chat**: *"`/bitpool-writing-standard` isn't installed, so the Security Drata, Security Jira and
Security Documentation writing profiles can't be applied. Installing it from the `bitpool-general` section is
recommended. Proceed without it?"* Continue only on a yes, and do not ask again in the same chat.

---

## The checks

Run checks 1–13 in parallel where possible, then report as one prioritised table.

### 1 — Null residual scores

```
Drata_searchRisks(treatment_plan=["ACCEPT","MITIGATE","TRANSFER","AVOID"], size=50,
                  expand=["owners","controls"])
```

Flag any risk where `residualScore` is `null`.

Why it matters: clause 6.1.3(f) requires the risk owner to **accept the residual risk**. A residual
that was never calculated cannot have been accepted. For `ACCEPT` the residual legitimately equals
the inherent score — but it must be *stated*, not blank. Blank reads as an omission; an explicit
equal figure reads as a decision.

### 2 — Risks with no linked control

Same query; flag `controls.totalCount == 0`.

Why it matters: an accepted risk with no control link is unreachable from the SoA side. When an
auditor works from the control list inward, the justification appears not to exist.

### 3 — Controls with no linked risk

For each control in scope, `Drata_searchRisks(controls=["DCF-xxx"])`. Flag empty results **only for
controls that are not ready** — a fully implemented control needs no register entry.

Don't over-report this. It is a soft check: the goal is that every *gap* traces to a risk, not that
every control has one. Many-to-many is correct; one-risk-per-control is a red flag.

### 4 — Review commitments with no driver

Two sub-checks, resolved against **different systems** — this is the part that changed on
2026-08-21:

1. **Execution commitments → IRT. Does every one have a driver ticket?** Query:
   `project = IRT AND text ~ "<riskId>"`. The check is whether the commitment has a ticket at all —
   **not whether that ticket carries a date.**

   > **Re-keyed 2026-09-15, because both halves of the old test had gone structurally empty.** It
   > read: *"any risk with an `anticipatedCompletionDate` and no `completionDate` — is there an IRT
   > ticket with a matching `duedate`?"* The trigger field is mandated blank (`drata-fields.md` §3),
   > and the thing it looked for — a matching `duedate` — is now deliberately absent on every new
   > ticket, so the test could never fire in either direction. Its underlying purpose survives and is
   > what the rewritten check does. The old note that this branch usually terminated empty — because
   > risks already carried a `completionDate` and none was forward-dated — was the early warning that
   > it had stopped testing anything.
2. **Review cadences → `CYB`, not IRT.** Every `ACCEPT` risk is re-examined by the periodic risk
   review under `DCF-16`, generated in **`CYB` — Cyber Security Recurring Tasks** (id `13173`) by
   Automation for Jira; the entry itself carries no review line (Security Drata profile §3.2), so its
   absence is correct and never a finding. **Do not flag a missing IRT review ticket — IRT does not
   hold review cadences.** Flag instead: is the `CYB` generator for that review in place, is its
   current instance actioned, and is `DCF-16`'s newest evidence version (`versions[].createdAt`)
   inside the cycle the Risk Assessment Policy in force sets? Find the current instance live in
   `CYB` each time; an instance key or its age written here would be stale by the next cycle. A
   `treatmentDetails` that promises a review of the entry ("annually", "each year", "will review")
   is a check 12 flag, not a missing driver — the cadence belongs to the policy and the
   periodic-review control, not to the entry.

   Also flag any **`ACCEPT` risk with no acceptance sentence** — does its minute now exist? If it
   does, stage the edit that adds the anchored acceptance (`treatment-decisions.md` §5, Scenario 2);
   if not, report it as awaiting management review.

Also flag **overdue**: `project = IRT AND duedate < now() AND statusCategory != Done`, and the same
for `CSIP`, which has no overdue automation, so this query is the only thing that surfaces a slip
there.

**Keep running that query**, even though no ticket created since 2026-09-15 can match it: legacy
dated tickets, the standing `PolicyQueue` and prioritisation-pass tickets, and everything the
prioritisation pass has dated all still do — and those are precisely the clause 10.2 population this
check exists to surface. **Run the undated census alongside it**, so the sweep sees the whole board:

```
project = IRT AND duedate IS EMPTY AND statusCategory != Done AND labels in (RTP, Clause)
```

An undated ticket there is **expected and is never a finding** (`irt-tickets.md` §1). What *is* a
finding is **an undated `Task` with no Original Estimate**, or **any undated ticket with no label** —
the first has nothing for the prioritisation pass to plan from, the second is invisible to the pass
altogether.

**Read `issuetype` before applying the estimate half.** The census query is issue-type-blind and
`RTP` is carried by parents and sub-tasks alike, so sub-tasks are in the result set — and
`irt-tickets.md` §5 is absolute that an estimate belongs on the parent `Task` **only**. A sub-task
*without* an estimate is correct; a sub-task **carrying** one is the finding.

Why it matters: **Drata's risk object has no date-based trigger** — confirmed with Drata support
2026-08-18, see `drata-fields.md` §3. But be precise about what follows: a Jira `duedate` is a field,
not a trigger, and it alerts only where an Automation rule stands behind it. **`IRT` has such a rule**
— it raises an "IRT overdue" sub-task, see `irt-tickets.md` §1 — so for `IRT` a reader exists, and
recording it as "NONE" is wrong. **`CSIP` has none.** So the honest finding is not "no ticket exists"
but **"which project is this in, and does a reader exist there"** — name what would surface the slip
and who runs it. Accepted risks that are never revisited are a standard clause 9.3 finding.

> Corrected 2026-09-15: this passage implied no such rule existed anywhere at Bitpool. That was wrong
> for `IRT`, and the same error had propagated into eleven IRT ticket bodies.

### 5 — Shared load-bearing assumptions

Group `treatmentDetails` by the factual claim they rest on. Flag any claim that carries **three or
more** acceptances.

Why it matters: concentration risk in the justifications themselves. If one shared premise turns out
to be false — or simply becomes false as the business changes — several acceptances collapse at once
and nobody notices, because each entry looks fine in isolation.

### 6 — Register overstates reality

For each `MITIGATE`, read `treatmentDetails` against what is actually in place (Jira status,
evidence, `flags.hasEvidence`, live infrastructure via `/aws-query` where relevant). Flag any entry
claiming broader coverage than the evidence supports.

Why it matters: a mismatch between the register and reality is a finding **regardless of how
defensible the underlying decision is**. This is the most damaging category on this list.

### 7 — Auditor-facing prose quality

Flag `treatmentDetails` with obvious typos, garbled sentences, or unexplained abbreviations. Values
that will go stale — counts, names, dates, status words — are check 12, not this one.

Why it matters: these are read verbatim by auditors as the organisation's reasoning. Sloppy prose in
a justification undermines its credibility, and it is the cheapest thing on this list to fix.

### 8 — The policy queue exists and is current

`project = IRT AND labels = PolicyQueue` → confirm the single policy queue ticket exists, has a
`duedate`, and carries nothing row-related in its description, and that every pending draft edit
found in this sweep appears **both** as a detail comment on the ticket and as a row on the queue
page. Read the page file from disk in the one main `security-documentation` working copy — the
register of record for row numbers (see **Writing a queue row** in `SKILL.md`) — never a git
worktree, a second clone or the published page.

**Read the comments, not just the page.** The index is three cells — row number, policy name and a
link to the row's comment — so it cannot tell you whether a queued change covers the thing you are
checking. A sweep that reads only the table will report coverage it has not verified.

**Check the page file against the comments — by comment id, never by heading.** Match each comment
on the ticket to the page's `Detail` links by the comment id each link carries, because some real
row comments are not headed `Queue row <n>` and some comments headed that way are notes, not rows.
Three half-finished states to look for, and to name individually rather than lumping together:

- **A row comment no `Detail` link points at** — the comment has not claimed a number. Treat a
  comment as an unclaimed row only when it carries the `Policy` / `Origin` / `Draft edited` /
  `Clause` header table **and** no `Detail` link on the page points at it. Check the next state
  first: where a row for the same policy and number reads `pending`, this is its comment — link it,
  never claim again. And before claiming for one, read the page's rows for the same policy, because
  a comment restating a change already indexed is a note on that row. Otherwise claim a number for it on the page and link the new row to
  that original comment; where the comment claims a number the page gives to another row, post a
  short correction comment naming the new number. The comment is always the side that moves.
- **A row whose `Detail` reads `pending` and whose comment exists** — the link step never ran. Find
  its comment — the header-table comment for this row's policy and number that no `Detail` link
  points at — and link it.
- **A row whose `Detail` reads `pending` with no comment** — a claimed number whose comment was
  never posted. Act on it only once the run that claimed it has ended: post the comment and link it,
  or withdraw the row — strike its `Policy` cell through, write `withdrawn YYYY-MM-DD` after the
  policy name, and set `Detail` to `withdrawn, no comment`. Where you cannot tell whether the
  claiming run is still going, leave the row and report it. The number is never reused.

Each fix is a staged write, made by the procedure in **Writing a queue row** in `SKILL.md`: page
edits are left uncommitted for the user to commit and push, and nothing goes in the description. A
row added or linked here is the same three cells — a pointer, never a description of the change.

Why it matters: policy promotion is one bulk event, and the queue is the only thing tracking it.
A drift finding that never became a queue row is an untracked commitment — which is the defect this
project exists to prevent.

**Do not check `renewalDate` or `approvedAt` on any policy, and do not report them.** Bitpool
renews the whole set in one bulk event after the control review programme resolves (decision
2026-08-24), so a lapsed renewal is the expected state between events. The finding is a missing or
undated queue ticket, never the policy dates.

### 9 — Commitments stated in ISMS documents with nothing chasing them

The register-side mirror of Step 3 outcome 4. Drata and IRT can both look clean while an ISMS
document carries dated commitments that no system tracks.

For each ISMS document holding dated commitments — Skills Matrix, objectives, improvement plans —
extract every date and check it against today and against `project = IRT`. Flag:

- a commitment whose date has **passed**, especially in a document whose version-control table shows
  a *later* review — the review saw it and left it, which is clause 9.3 as well as 10.2
- a commitment with **no IRT ticket** at all
- a commitment where the document's date and the IRT `duedate` **disagree** — noting which is newer,
  since a mirror or ticket updated ahead of its controlled document is itself a 7.5.3 defect.
  **An empty IRT `duedate` is not a disagreement**; since 2026-09-15 it is the expected state until
  the prioritisation pass runs. What to check instead on an undated ticket: that the document's date
  is quoted in the ticket body as its `Date constraint:`, so the pass will inherit it rather than
  rediscover it. A missing constraint line on a ticket whose document states a date **is** a finding
- a `Date constraint:` quote that **no longer matches the controlled document** — re-read the
  version in force (the approved document, never a mirror or a draft edit) and compare the quoted
  text. A quote the document no longer contains means the pass would inherit a superseded date:
  that is a confirmed finding. Where a ticket carries both forms, test `Date constraint (approved):`
  against the approved document and `Date constraint (queued):` against the draft and its queue row
  (`irt-tickets.md` §6); after the bulk promotion, the approved line is caught by the same test. A
  quote naming neither the document's version nor the date it was quoted cannot be told apart from
  what the document says now — report it as latent (Security Jira profile §3.2)

Why it matters: these are self-declared nonconformities. Unlike a control gap, the organisation has
already written down that it isn't meeting its own commitment — an auditor doesn't have to find it,
only read it.

---

### 10 — Controls carrying a risk but no evidence

For every control linked from a risk in the register, is there evidence attached to it?
**Resolve this with `Drata_listEvidence(control_code="DCF-xxx")`, not with the flag** —
`has_evidence` / `flags.hasEvidence` reports `true` on invalid references and on evidence that
belongs to a different control (see `drata-fields.md` §2). Use `has_evidence=False` only to
narrow the candidate set, never to conclude a control *has* evidence.

A control that a risk entry names as a compensating control, but which carries no evidence, is the
register asserting something nothing backs. That is the same defect as an overstated
`treatmentDetails` (check 6), reached from the other direction — and it is the one an auditor hits
first, because they read the control before they read the risk.

Report the artefact that *would* evidence each one, using the house heading **"Evidence Drata will
look for"**. This skill does not upload evidence, so this check always produces a list for the user,
never an applied fix. The list is a report; but a bucket `name` or `description` you draft for the
user to paste into Drata is Security Drata text — write it to the evidence rules in that profile
(§3.1) and show its check.

### 11 — Risk reviewer populated

Bitpool sets no reviewers (decision 2026-08-24; governing rule in `drata-fields.md` §7). This check
needs **its own unfiltered call** — the checks 1–2 query filters by `treatment_plan`, and facets are
first-page-only, so that call cannot substantiate a register-wide statement:

```
Drata_searchRisks(facets=["reviewerEmails"], size=1)
```

**An empty `reviewerEmails` facet is the correct state — never report it as a finding.** Any risk
carrying a reviewer is drift: clear it with an explicit empty list, **passing `treatment_plan` on
the same call** or the field is silently dropped along with every other treatment field, and quote
the returned array back. Raise it in the batch approval block like any other write.

Also flag any `treatmentDetails` prose asserting a reviewer exists — that is a check-6 overstatement,
and it survives the field being cleared, so clearing alone does not close it.

### 12 — Drift-prone text in durable records

A durable field can be true today and written to go false: a count, an account name, a named owner,
a quoted date or a status word stays correct only until its home changes, and nothing re-checks the
copy. Check 6 catches a claim only after it has gone false, and only on `MITIGATE`; check 7 reads for
typos, not values. This check runs the standard's audit sweep (`/bitpool-writing-standard`,
`references/durability-check.md` §5) over the durable fields of the registered targets this skill
works in — **and nowhere else**.

**Read in full**, in structured list mode, following pagination to the end (`/ask-drata`):

| Target | Durable fields read | Profile |
|---|---|---|
| Drata risk register | `description` and `treatmentDetails` of every risk — an unfiltered `Drata_searchRisks`, not the checks 1–2 call, which filters by `treatment_plan` | Security Drata §3.2 |
| Drata evidence library | `name`, `description` and `implementation_guidance` of the evidence on each control linked from a risk — the `Drata_listEvidence` calls check 10 already makes | Security Drata §3.1 |
| Drata controls | `name`, `description`, `activity` and `question` of each control linked from a risk, where Bitpool has customised them | Security Drata §3.3 |
| Jira `IRT` | `summary` and `description` of every open ticket in `project = IRT AND statusCategory != Done AND labels in (RTP, Clause, PolicyQueue, PrioritisationPass)` — dated and undated alike, and including the two standing tickets, whose durable descriptions take the standing-ticket shape. Check 8 checks the queue page against its comments | Security Jira §3.2–§3.4 |

**Skip what is not Bitpool's to rewrite:** Drata's stock text — its own control statements and its
seeded test-result evidence (*"Drata inspected… and confirmed…"*) — and any labelled anti-pattern
example. Text naming Bitpool's platforms, registers, policies,
people or risk IDs is Bitpool's, whatever the object. **Not swept here:** `CSIP` descriptions
(read-only to this skill; `/describe-dcf-jira-ticket` writes them), vendor free text
(`/manage-drata-vendors`), ISMS policy text (Step 8 and check 9 — wholesale policy review is a
separate exercise), and anything outside the register — `CYB`, `OP`, `BT`, the worklog.

**Flag** every span matching the pattern table in `durability-check.md` §2 — apply that table, not a
summary of it — plus the two things spans miss:

- **A long entry.** Length is the earliest warning: the entries that drift most are the longest.
- **Status text that has already flipped** — a standing statement whose trigger has since fired. On
  `IRT`: a `NOT YET SCHEDULED` scheduling line, or a `Reader:` line saying nothing reads the ticket
  while `duedate` is empty, on a ticket that now has a `duedate` — the eleven-ticket correction under
  check 4 is this class; `pending bulk promotion` on a `LAPSED` line after the bulk promotion has
  closed. In Drata: *"(pending promotion, `<ticket>`)"* in `treatmentDetails` after that promotion,
  and *"holds no evidence"*, *"newly identified"*, *"is provisioned"* or *"not yet"* on a record
  whose position has since moved.

**Check what can be checked, and report the two results separately:**

- **Confirmed** — the value already disagrees with its home: an account count or name against the
  AWS Organization (`/aws-query`); a quoted document date or `Date constraint:` quote against the
  version in force of the controlled document (shared with check 9); a named owner against Drata's
  `owners`; a person's name against Drata personnel; a `DCF` code in risk prose that is already in
  that risk's `control_ids`; a pointer whose home, read in the version in force, does not hold the
  value; flipped status text.
- **Latent** — the value still agrees with its home, or has no live home to test against. Still a
  defect: it is correct only until the home next changes.

**Report a summary table first** — one row per record: the record (risk ID, evidence bucket and its
control, `DCF` code or `IRT` key), its profile, its length, and its confirmed and latent defects,
confirmed-defect records and the longest first. Then draft rewrites **only for the records the user
picks, a few at a time**, each under its own durability check (`durability-check.md` §1). Remove a
stale value rather than correcting it — today's count in place of last year's only resets the clock
(core rule 3). The measured value goes in the report and in the dated comment recording the change.

**Report, do not write — except where this mode already authorises the write:**

- **Risk `description` and `treatmentDetails`** — a picked rewrite may join the batched
  `Drata_updateRisk` under the one approval block, with its check and its dated `IRT` or `ICR`
  comment staged alongside (see the top of this file). `description` is capped at 768 characters.
- **Evidence text** — this skill cannot write evidence (`drata-fields.md` §2). Draft the rewrite for
  the user to paste into the Drata UI; it is still Security Drata text and carries its check.
- **Control text** — rewriting it changes what Bitpool asserts about itself, and is the rare,
  explicitly approved exception gated by the golden rule in `SKILL.md`. Never part of the batch.
- **`IRT` summary and description** — staged one ticket at a time, each with its check. The reason
  goes in a comment beside Jira's changelog, never as a correction paragraph in the description
  (Security Jira profile §3.1).

Why it matters: a durable record that disagrees with its home is false in front of an auditor, and
one demonstrably wrong value invites them to test every other claim in the register. The latent ones
are the next findings, and removing them now is cheaper than correcting them one incident at a time.

### 13 — ICR endings that no longer hold

Added 2026-09-29, when the closure rule changed from *review concluded* to *audit ready*
(`SKILL.md` Step 10; the gate's checks are `icr-closure.md` §2). Outside a run on that same control,
which re-tests it at Step 1 and Step 10, nothing re-tests an `ICR` ticket after it closes, so a record
that goes false after closure stays false — `ICR-191`'s register `Rationale` did, for a month.

Query `project = ICR AND statusCategory = Done`. For each ticket, read its latest outcome comment and
every outstanding item it names, and flag:

- an item with no open `IRT` ticket whose deliverable closes it — a cited policy-queue row counts only
  if its detail comment names this control, the row is in `origin/main`'s copy of the queue page
  (`git fetch origin`, then `git show origin/main:compliance/isms-policy-queue.md`) and its draft
  edit is on `main` (`icr-closure.md` §3). Find the row by content; never trust the row number the
  comment cites;
- an item carried only by a ticket that is not an `IRT` ticket (`CSIP`, `OP`, `CYB` or another `ICR`
  ticket). The exception is a recurring review routed to `CYB` on a control whose acceptance is
  recorded, which is a position, not a gap (`icr-closure.md` §3);
- a comment that says an item is untracked, or asserts no gap and then records one;
- an auditor-facing record the comment relies on that is no longer true — above all the register
  `Rationale`, once an `IRT` ticket the comment names as a carrier has closed;
- a control whose Drata `isReady` is `false` for a cause `icr-closure.md` §4 says holds — a control
  approval still configured, a test failing because of how it is set up in Drata, or a failing
  monitoring test no open `IRT` ticket's work will make pass — or whose evidence exists but is not
  uploaded (`icr-closure.md` §2, checks 2, 7 and 8).

Then query `project = ICR AND statusCategory != Done AND status != "To Do"` and flag any ticket with
no dated outcome, hold or in-progress comment, and any hold whose *closes when* condition is now met.

**Report only.** A reopen or a close is a Step 10 ending through `/manage-drata-control DCF-xxx` for
that control, with the user's yes one ticket at a time — never in bulk. Why it matters: a closed
`ICR` ticket asserts the control is ready for audit, so one that is not is a false claim on the one
board that measures readiness, and it releases the prioritisation pass before `IRT` holds the scope
the pass has to plan.

---

## No stored baseline — measure it live

**This file deliberately records no counts.** Register composition, control readiness and evidence
coverage all change continuously and are one MCP call away. A number written here becomes wrong
quietly, and a future session that trusts it reports a stale finding as current.

Run the checks above and report what you actually observe. If the user wants a
period-over-period comparison, take it from the previous session's worklog entry under the
`/drive-iso27001` state directory — that's a dated record of what was true then, which a hardcoded
figure in a skill file is not.

Known-recurring patterns worth checking first, without asserting their current size:

- `ACCEPT` risks tend to carry **null residual triplets** — check every one.
- The `AI-*` risk family tends to have **no linked controls** and thin justifications.
- Several acceptances rest on the **same load-bearing claim about personal data** — check whether
  that claim is still true before trusting any of them.
- Human-written evidence descriptions tend to **copy the contents of the artefact** — attendees,
  photo counts, tools, mailboxes — rather than describe it (check 12).

---

## Worked examples

Three real cases the skill was designed against. Verify each live before acting — they may have
moved on.

- **`DCF-19` / [CSIP-558](https://bitpool.atlassian.net/browse/CSIP-558)** — pen test scope. `SD-04`
  already covers this control, so this is an **amendment, not a new risk**. The defect worked here
  was `treatmentDetails` claiming broad "annual penetration testing", which is wider than the real
  scope: **the customer-facing platform and its API are penetration tested annually, unauthenticated
  and authenticated; private or semi-private platforms are not tested at all** — their exposure
  does not justify the cost, and access control under DevOps practice is the primary safeguard
  instead. The untested authenticated partner surface is carried as **accepted exposure** on
  `SD-04`, not as a tested scope. State that boundary positively, never as a list of what is
  excluded (`drata-fields.md` §4, "The required shape of `treatmentDetails`"). This records the
  decision, not the entry's wording: the entry follows Security Drata profile §3.2 — the boundary as
  the criterion that decides membership, and the cadence by pointer to the policy that sets it, once
  the version in force is confirmed to hold them.

  **Corrected here 2026-09-15**, against the live `SD-04` record read the same day (last amended
  2026-08-27). This example had been left describing the real scope as *"authenticated on
  `app.bitpool.com`, unauthenticated on partner-restricted apps like `estimating.bitpool.com`"*.
  The risk owner retired that wording on 2026-08-27 — it was wrong on the second half — and
  `drata-fields.md` §5 ("In-house precedent to copy (and to avoid)") was corrected the same day,
  but this file was not, so the skill shipped two contradicting scopes until now. **Do not
  reinstate the partner-app clause.**
- **`DCF-558` / [CSIP-646](https://bitpool.atlassian.net/browse/CSIP-646)** — ThreatLocker developer
  tooling exception. No risk entry exists. Needs a new entry modelled on `CR-01`, as a sibling to it
  (different risk: developer endpoints holding privileged credentials, not general personal apps).
  Write the entry in capability terms — application allow-listing — not the product.
- **`DCF-179` / [IRT-1](https://bitpool.atlassian.net/browse/IRT-1)** — competence, and the canonical
  **Step 3 outcome 4** case. Worked through 2026-08-21; the shape is worth knowing because every
  Drata signal was green:
  - The control is `isReady: true` with `hasEvidence: true`, and maps to **clause 7.2** (requirement
    id 75) — mandatory, so no risk entry and no acceptance. `Drata_searchRisks(controls=["DCF-179"])`
    returning empty is **correct here**, not a traceability gap.
  - Clause 7.2(b) requires competence on the basis of "education, training, **or** experience" —
    disjunctive. **No certification is required by the standard.**
  - But the controlled [ISMS Plan](https://github.com/bitpool/security-documentation/tree/main/ISMS/ISMS%20-%20Draft/Information%20Security%20Management%20System%20Plan%20ISO%20IEC%2027001%202022.md)
    Skills Matrix self-declared the ISMS lead "Fully Competent: **No**", with commitments dated
    "by end 2024" and "by end 2025" — **both lapsed**, in a document whose version-control table
    records an annual review in July 2025 that left them standing.
  - The same commitment appeared with **three different dates** across the controlled document, its
    wiki mirror (re-dated to ~2027 without the document changing) and IRT-1's `duedate`.
  - So the real exposure was 7.5.3 / 9.3 / 10.2 — **not** the missing certificate. Amending the
    document reduced exposure more than obtaining the qualification would have.
  - Also found in passing: IRT-1's description labelled an ISC2 SSCP badge as a "PECB qualification",
    and `DCF-46` — the *other* control mapped to clause 7.2 — was `isReady: false` with no owner and
    no evidence, making it the weaker half of the clause.

---

## Reporting

One table, most severe first. Suggested severity order:

1. **Policy queue missing, undated, or out of step with this sweep (check 8)** — that ticket is
   the only thing tracking the single bulk promotion, so a drift finding that never became a queue
   row (a detail comment *and* its row on the queue page) is an untracked commitment. **Never report a
   policy's `renewalDate` or `approvedAt` here** — a lapsed renewal between bulk events is the
   expected state, not a finding
2. **Lapsed commitment in an ISMS document (check 9)** — a self-declared nonconformity, worse still
   if it survived a documented review
3. Register overstates reality (check 6)
4. **`ICR` ticket closed but not audit ready (check 13)** — a closure asserting readiness that an
   auditor would fail, reached from the review board rather than the register
5. **Controls carrying a risk but no evidence (check 10)** — the same defect as 3, reached from
   the control side, which is the side an auditor reads first
6. **Drift-prone text, confirmed (check 12)** — a durable record already disagreeing with its home
   is false today, like 3, reached through a copied value rather than a claim
7. Null residuals on `ACCEPT` (check 1)
8. Shared load-bearing assumptions (check 5)
9. Risks with no linked control (check 2)
10. Review commitments with no driver (check 4)
11. Not-ready controls with no risk (check 3)
12. **Risk reviewer populated (check 11)** — drift against a recorded decision; an *empty* facet is
    correct and is never reported
13. Drift-prone text, latent (check 12)
14. Prose quality (check 7)

For each finding give: what it is, why it matters in one line, and the specific fix. Check 12 is the
exception: its rows point at its own summary table, and fixes are drafted only for the records the
user picks. Then offer to walk the highest-priority ones through the default `/manage-drata-control`
workflow one at a time — do not attempt to fix the whole register in one session.
