# Drata risk fields, the write model, and the approval block

Read §1 during Phase 1, §2 before any write, and §3 to build the gate at Phase 3.

> **`/ask-drata` is the authority on the connection.** Which verbs exist, the trap in each, and
> which flags cannot be trusted all live there, because they are true of the connection regardless
> of which skill is using it. What follows is only what is specific to *reading and repairing a risk
> entry*. **If this page and `/ask-drata` disagree, `/ask-drata` wins.**

---

## 1 — The field map

`Drata_searchRisks` returns: `id`, `riskRegisterId`, `riskId`, `title`, `description`,
`treatmentPlan`, `treatmentDetails`, `anticipatedCompletionDate`, `completionDate`, `impact`,
`likelihood`, `score`, `residualImpact`, `residualLikelihood`, `residualScore`, `status`,
`identifiedAt`, `createdAt`, `updatedAt`.

Expandable, and **expand all of them in Phase 1** — a missing expansion reads as an absence:
`owners`, `reviewers`, `controls`, `categories`, `documents`, `notes`, `tickets`, `tasks`,
`customFields`.

- Register: id `1`, name `Risk Management`.
- `status`: `ACTIVE` (monitored, applicable) · `CLOSED` (resolved) · `ARCHIVED` (not applicable).
- **There is no "next review date" field.** The only dates are `identifiedAt`,
  `anticipatedCompletionDate` and `completionDate`. The entry's own review therefore cannot live on
  the risk, and its text does not state it at all — no cadence, no review date, no reviewing
  control. It belongs to the periodic risk review control (`DCF-16`) and its recurring task in
  `CYB`. The review date the acceptance criteria require lives there too — see `risk-scoring.md` §2.

### Search-mode quirks that will mislead Phase 1

- **`query` (AI/semantic) mode fails account-wide** — silently empty, or hard 500s — and it
  **silently discards every structured filter passed alongside it**. Use `q` (keyword) plus
  structured filters instead, and paginate `cursor` to `null` before concluding anything is absent.
- **`facets` is the cheap way to check register-wide claims.** `facets=["ownerEmails",
  "reviewerEmails","treatmentPlan","status"]` with `size=1` returns grouped counts without
  fetching every row. This is how a claim like *"the reviewer is never the owner"* gets tested in
  one call.
- **`controls=["DCF-xxx"]`** finds every risk linked to a control. Use it to test whether a
  deferral — *"treated under DCF-5"* — actually resolves anywhere.
- `inherent_score_gte` / `residual_score_lte` and the date ranges are the way to test threshold
  claims against criterion 1 without reading every entry.

### Dates: Drata records them, it does not chase them — settled

Confirmed with Drata support, 2026-08-18: **nothing fires** when `anticipatedCompletionDate` passes
without `completionDate` set. Drata workflows trigger on score changes, treatment-option changes,
evidence updates and personnel compliance — never on dates.

Consequence: **Bitpool deliberately leaves `anticipatedCompletionDate` blank.** A populated
`anticipatedCompletionDate` on a Bitpool risk is a **finding**, not data — the field triggers
nothing, so a date in it is chased by nobody and will contradict whatever `IRT` eventually holds. Do
not re-open this; do not propose relying on Drata to flag a slipped date.

> **The reason had to be restated on 2026-09-15, because the old one stopped being true.** It read:
> *"Dates live on the IRT ticket, where Jira's `duedate` at least makes them findable in one query …
> it is a second copy of a date that nothing chases."* That presupposes a **first** copy on the IRT
> ticket. Since 2026-09-15 IRT tickets are created with an empty `duedate` and scheduled later in a
> board-wide prioritisation pass, so for most risks there is no first copy yet, and a populated Drata
> field would be **the only date in existence**.
>
> **That is an argument for leaving it blank, not against it.** The rule stands on two things that do
> not depend on a date already existing: the field triggers nothing, and `IRT` is the single home for
> this commitment's date whether or not one has been set. Never read *"it isn't a duplicate any
> more"* as permission to populate it.

Note also that a Drata **evidence** `renewalSchema` date *does* fire — but it re-attests an artefact
rather than chasing a deliverable, so it is never the parent of record for a commitment.

---

## 2 — The write model, for risks

Available and authorised: **`Drata_createRisk`** and **`Drata_updateRisk`**. This skill normally uses
only the second — it repairs entries that exist. Evidence upload is a **human action**; there is no
write verb for it.

Traps specific to `Drata_updateRisk`, all verified:

| Trap | What happens |
|---|---|
| **Relation fields replace, they do not append** | `owners`, `reviewers`, `category_ids`, `control_ids` **replace the entire relation**. To add one, read the current set and pass it back alongside. Omit the field to leave it unchanged; pass an empty list to clear it. |
| **Non-admin users are dropped silently** | Only users holding an admin / risk-management role can be an owner or reviewer. Others are discarded without an error. **Always compare the returned `owners`/`reviewers` against what you sent.** |
| **`control_ids` are numeric** | Not `DCF-xxx` codes. Resolve with `Drata_searchControls` and list the code beside each id in the approval block so the user can check them. |
| **Treatment fields need a non-UNTREATED plan** | `treatment_details`, `residual_impact`, `residual_likelihood`, `anticipated_completion_date`, `completion_date` are **silently dropped** unless `treatment_plan` is set to something other than `UNTREATED` in the same call. Pass `treatment_plan` explicitly. |
| **A date cannot be cleared** | Passing null leaves it unchanged rather than blanking it. A wrongly populated `anticipatedCompletionDate` has to be cleared in the UI. |
| **`description` caps at 768 characters** | The API rejects at 769. Count it before sending. |
| **`riskId` is not settable on create** | Drata assigns it. You cannot choose `CR-06`. |

**Every write goes behind an approved block.** Having write access does not remove the confirmation
step; it removes the excuse for skipping it.

---

## 3 — The approval block

**Render as formatted markdown in the chat — never inside a fenced code block.** The fence below
delimits the template *within this file*; it is not how the block should reach the user. A block
someone is being asked to check line by line has to be scannable, and a wall of monospace is exactly
where an untrue claim survives unread. Use a table for the fields and headed lists for
`treatmentDetails`.

```
DRATA RISK — AMEND <riskId>
Register: Risk Management (id 1)

title ................. [unchanged, or the new short risk name]
description ........... [the risk as a consequence to information — NOT a missing control.
                         HARD LIMIT 768 characters. Count it.]

treatmentPlan ......... [MITIGATE | ACCEPT | AVOID | TRANSFER]
treatmentDetails ...... [Security Drata §3.2 — the bucket headings only where the entry has a
                         coverage story, otherwise a short paragraph — see risk-verification.md
                         §4. Numbered continuously on an entry with no stable-numbering
                         declaration; per repair rule 6 on one that declares it]

impact ................ [1-5]        likelihood ........ [1-5]     = [score, band]
residualImpact ........ [1-5]        residualLikelihood  [1-5]     = [score, band]
                         [state what criterion 1 requires at that band — for the reviewer
                          only; treatmentDetails cites the Risk Acceptance Criteria by policy
                          name and never copies the band or the threshold]

owners ................ [current, unless the user changed it]
reviewers ............. [EMPTY — Bitpool sets no reviewers, decision 2026-08-24.
                         Omit the field; do not pass an empty list unless clearing one]
control_ids ........... [NUMERIC ids, each with its DCF code beside it]
anticipatedCompletionDate [LEAVE BLANK — dates live in Jira IRT only]

--- Changed from the current record ---
[A short diff: which items moved bucket, which were deleted, which scores moved and why —
 items named by number. This is what the user is really approving.]

--- Outside Drata ---
Verification record .. [the dated comment for the RTP ticket — see "Where Phase 1's
                      specifics go" below. A snapshot: specific by design, and not
                      checked. It also records what changed in the risk, why, and on
                      whose decision. NO RTP TICKET: say so here — the text is
                      staged for the user to file on the linked control's ICR
                      review ticket, which this skill does not write]
RTP ticket ........... [IRT corrections — supersessions and content fixes, each with a reason
                      comment. A summary or description edit is durable Security Jira
                      text and goes in the durability check. This skill never sets,
                      changes or clears a duedate]
Policy queue ......... [any row to add to project = IRT AND labels = PolicyQueue -
                      state BOTH the row to claim on the queue page and the detail
                      comment to post; nothing row-related goes in the description]
Evidence ............. [split: available now, vs produced by a planned subtask]

--- Durability check ---
[ONE table for the whole block, directly under the staged text — Field · Span · Why
 flagged · Disposition — covering every durable field staged above: title,
 description, treatmentDetails, and any IRT summary or description edit.
 One collapsed row for handles, then a "Removed before staging" line. Format, flags
 and dispositions: /bitpool-writing-standard references/durability-check.md §1-§3.
 A markdown table, never fenced. Comments are snapshots and are not checked]

--- Still unverified after the gate ---
[Every claim the user could not confirm. If this list is empty on a first pass,
 you almost certainly did not check.]
```

### Content rules

**What the text says is `/bitpool-writing-standard`'s** — its six core rules, the Security Drata
profile §3.2 for `title`, `description` and `treatmentDetails`, and the Security Jira profile for any
`IRT` summary or description edit. Load them before drafting; this file keeps no copy. What follows
is only what *repairing* an entry adds.

**Rule zero: nothing copied from a system of record.** Before any other content check, strip every
value whose home is elsewhere — not only measurements. Counts, ratios and tallies; accounts, hosts
and resources; people; mailboxes; configuration values; products; policy-owned numbers; another
record's content; status that flips at a known event. The standard's rule 3 lists them, and its two
tests decide: **twelve months** (would this still be true with nobody editing it?) and **the owner**
(if the record that owns this value changed tomorrow, would this go false?). A value can pass the
first and fail the second — a role holder's name may still be right in a year and is still a copy of
`owners`. A scope statement survives only as the criterion that decides membership, with the policy
or register that sets it; a list of members, in or out, is an inventory however it is phrased.

**Repair generalises; it never re-syncs.** Where Phase 1 found a specific wrong — a count of AWS
accounts the Organization has outgrown, a named owner who has moved on — remove the value and point
at its home, to the true boundary and never past it (core rule 3). Writing in the corrected value
only resets the clock. Treat a copied value as a defect to fix even when the user only asked about
something else — it is the same class of error as a false control claim, and it is cheaper to
correct in passing than to leave for an auditor to find.

**Anchored verifications — core rule 4.** Keep one per relied-on compensating control, the latest,
written as a past-tense event with its date, its method and where the result is recorded, with no
counts, lists or observed settings inside it — and, where it is relied on as present assurance, what
re-performs it. Earlier verifications of the same control move to the verification record below;
they are not appended. "The latest" is judged across this skill's verification records and the
linked control's latest `ICR` outcome comment and any hold comment after it, where `/manage-drata-control` records its own — both read in
Phase 1. **A date added to a count does not make it durable.**

#### Where Phase 1's specifics go — the verification record

The counts, account names, observed settings and attestations Phase 1 establishes are snapshot
detail, and they are worth keeping. Their home is a **dated comment on the RTP ticket** in `IRT`,
headed `Verification record — <YYYY-MM-DD>`, holding:

- each claim tested, the status it reached, and what it was tested against — the call, the artefact,
  or who attested it in this conversation and when;
- what was measured, as specifically as the moment warrants;
- the rows still unverified after the gate;
- what changed in the risk, why, and on whose decision — the change record Drata cannot keep for
  itself (core rule 6);
- where the change removed an acceptance, that the changed position awaits acceptance at the next
  management review (`risk-scoring.md` §2) — this record is where that is tracked until the minute
  exists, and the entry never says *pending*.

It is staged in the approval block and posted in the same change as the `Drata_updateRisk` write — or
on its own, behind its own approval, if the user declines the rewrite. Correct an earlier record by
adding a new comment, never by editing the old one.

Not the `ICR` review comment — `ICR` is read-only from this skill. Not an evidence artefact — upload
is a human action, and the artefact holds its own counts. Not the RTP ticket's description — that is
durable Security Jira text.

**Where the risk has no RTP ticket** — normal for a risk retained with no outstanding work — this
skill has no writable home for the record. Stage the comment text anyway, say so in the approval
block and the Phase 4 summary, and hand it to the user to file on the linked control's `ICR` review
ticket, which this skill does not write. Never drop it, and never fold it into `treatmentDetails`
instead.

#### The repair rules for `treatmentDetails`

1. **Only assert what operates today.** Every item in an operating bucket is a claim that Bitpool
   does this thing now.
2. **Mark planned measures as planned and name what delivers them** — the outcome, the condition on
   which it will be relied on, and the IRT subtask; never its progress. Never mix a future control
   into an operating list in the present tense.
3. **No ritual controls.** A control performed by the conflicted party on their own work is not a
   control. State the exposure instead.
4. **Link other controls; don't re-explain them.** Put the DCF in `control_ids` and stop — prose names
   a control only where part of the risk is deferred to one that is deliberately not linked (Security
   Drata §3.2). Check the pointer resolves (`risk-verification.md` §4).
5. **Show the diff.** Unlike a fresh entry, a repair is judged against what was there before — so
   the block must make the *change* visible, not just the end state. A user re-reading fourteen
   unchanged items to find the two that moved will skim, and skimming is how the last false claim
   survived.
6. **Keep stable item numbers stable.** Where the entry declares its item numbers stable — the line
   Security Drata §3.2 describes, which `/manage-drata-control` writes on every entry it creates —
   numbers are assigned once: a surviving item keeps its number even when it moves bucket, a deleted
   item's number is retired and never reused, and a new item takes the next unused number. Keep the
   declaration line itself. IRT subtasks and evidence cite those items by number, and a renumbering
   repair silently breaks every one of them. Renumber continuously only an entry with no such
   declaration — and before doing so, check its RTP subtasks and evidence for citations by item
   number; where any exist, recommend at the gate adding the declaration rather than renumbering.

### After the write

**Quote what the API returned, not what you sent.** Check specifically: the `owners` and `reviewers`
that came back, the `residual*` values (silently dropped if `treatment_plan` was omitted), and the
`controls` list. Report the assigned `riskId` and the `updatedAt`.

---

## 4 — Register conventions

- **Risk ID prefixes observed:** `SD-`, `CR-`, `AI-`, `IN-`. Follow the domain's existing prefix.
- **Write risks in risk language**, never as a restated control gap — see `risk-verification.md` §6.
- **One home per fact** — `/bitpool-writing-standard` rule 1. For this skill's two records: scores,
  treatment rationale and the register position live in Drata; execution status and dates live in
  Jira `IRT`. Never state the same fact in both.
- **No date, month or year in `treatmentDetails` prose either** — not only in the date fields. Write
  *"outstanding execution is tracked in `IRT-n`"* and stop; where two commitments need telling apart,
  distinguish them by *what they are*, never by when they fall due. Rejected by the risk owner,
  2026-08-27: *"why commit to specific dates in the risk treatment plan? that will cause drift right?
  Jira carries the dates."* **The ban holds harder while IRT's `duedate` is empty**, because a month
  name in the register would then be the only date in the system and would read as authoritative. The
  narrow exception is an **anchored historical fact** under the standard's rule 4 — *"last performed
  and verified closed at re-test"*, with its date, how it was established and where the result is
  recorded — which states what happened rather than what will. Full rule: `/manage-drata-control`
  SKILL.md, **Dates live in Jira `IRT`**.

  > Added here 2026-09-15. This file listed three things that keep appearing wrongly in
  > `treatmentDetails` and dates were not among them — so the skill that *repairs* `treatmentDetails`
  > carried no local statement of the rule it is meant to enforce.
- **Everything else that never belongs in `treatmentDetails`** — a paragraph restating the scores,
  the entry's own review in any form (a cadence, a review date, or the reviewing control — all owned
  by the periodic risk review control, `DCF-16`, and its `CYB` recurring task), a re-explanation of
  another control, a linked control named in prose, a policy-owned number, an evidence-bucket or
  monitoring-test name, correction history — is listed once, in the Security Drata profile §3.2.
  Apply it from there. A treatment item that is itself a recurring activity is different: it cites
  the policy that sets its cadence.
- **An `IRT-n` key in `treatmentDetails` is permitted** — this skill and `/manage-drata-control` are
  IRT's only writers, so the reference can be kept true. Write it with its recovery query:
  `tracked in IRT-7 (find by: project = IRT AND text ~ "SD-04")`. A `CSIP`, `ICR` or `CYB` key is
  **not** permitted — those are written by other skills and the pointer decays into a confidently
  wrong link.
- **Never use a Drata internal numeric id as an identifier.** `control-details/210/` is Drata's
  surrogate key, owned by nobody at Bitpool. `DCF-179` is the durable handle.
