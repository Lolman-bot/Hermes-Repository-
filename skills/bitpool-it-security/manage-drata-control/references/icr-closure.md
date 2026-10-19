# ICR closure — the audit-ready gate

`SKILL.md` Step 10 ends every run on the control's `ICR` ticket: closed when the control is ready for
audit on its recorded position, held otherwise. It states the gate's three conditions — **Recorded**,
**True**, **Carried** — what never holds the ticket and what does, the endings and the permissions.
This file is how to check them.

Bitpool decision, 2026-09-29, settled with the risk owner on 2026-09-30. In the risk owner's words:
*"ICR is about being audit ready, not about being reviewed."* §5 records the rule it replaced.

---

## §1 When to run this

Before any ending at Step 10, for every control the run reviewed — and for a `Done` ticket Step 1
found, whose closure an earlier run asserted. Run every check that applies, then record the result
in the comment you post: a **Gate** table in the outcome comment when it passes, the list of what
holds it in the hold comment when it does not. One row per check — pass, carried by `IRT-n`, or holds.

A check that holds the ticket is usually cheap to clear in the same run, so try that before holding:
raise the missing `IRT` ticket, make the record true, write the empty `Rationale`. What only the user
can do — an upload, a step in the Drata UI, a commit and push — ask for there and then, wait, and
re-check.

---

## §2 The checks

| # | Check | How | Holds the ticket when |
|---|---|---|---|
| 1 | Linked risks | `Drata_searchRisks(controls=["DCF-xxx"])`; read each `description` and `treatmentDetails` against what Step 3 established | A claim is untrue today and no open `IRT` ticket carries its correction |
| 2 | Control record | The Step 1 cursor seek; read `description`, `activity`, `question` and `flags.isReady` | The text is untrue, with no approved correction written this run and no open `IRT` ticket carrying one; or `isReady` is `false` for a cause §4 says holds |
| 3 | Register row | The `DCF-xxx` row of `compliance/drata-controls-register.md` as it stands on `main`: in `security-documentation`, `git fetch origin`, then `git show origin/main:compliance/drata-controls-register.md`. The working-tree copy is where this run edits, never what the gate reads | Its description differs from Drata's, or its `Rationale` is untrue, and no open `IRT` ticket carries the correction. **An empty `Rationale` is written by this run** via `/bitpool-docs`, and holds only if the run cannot write it. Any edit this run made holds until it is on `main` |
| 4 | SoA row (Annex A) | The control's row in the ISMS Plan draft | Its `Implemented` value contradicts the position and no queue row carries the change |
| 5 | ISMS documents | Every document Step 8 read for this control. Read the queue page as it stands on `main`, as check 3 does: in `security-documentation`, `git fetch origin`, then `git show origin/main:compliance/isms-policy-queue.md`. The working-tree copy is where runs claim numbers, never what the gate reads. Find each drift's row there **by content**: open the row's detail comment and confirm it names this `DCF-xxx` and this change, and that the draft edit it records exists on `main`. Never trust a row number an earlier comment cites — rows were overwritten on 2026-08-26, and `ICR-5`'s cited rows came to belong to other controls | Drift with no row; a row not yet on `main`; a row whose detail comment belongs to another control; a row whose draft edit was never made or is not yet on `main`, **whichever run left it** |
| 6 | Every gap | List the gaps from Step 3 and the risk. For each, query `project = IRT AND statusCategory != Done AND text ~ "DCF-xxx"`, and `text ~ "<riskId>"` where a risk exists, then read each hit's deliverable. §3 says what counts | No open `IRT` ticket whose deliverable closes the gap |
| 7 | Evidence | Each evidence gap — missing, lapsed, lapsing, or blocked behind other work. `Drata_listEvidence` sees Evidence Library buckets only, so confirm external evidence with the user (`/ask-drata` rule 10) | The artefact **exists but is not uploaded** — this skill cannot upload, so ask the user to, then re-check; or it cannot exist yet and no open `IRT` ticket or evidence sub-task will produce it |
| 8 | Owner steps in the Drata UI | Anything handed to the owner — by this run, or in an earlier `ICR` comment Step 1 read: a control approval to remove, an artefact to upload, an evidence description to rewrite | Any of them is not yet done — ask, wait, re-check |
| 9 | Clause controls | The controlled document, each kind C ticket's `Date constraint:`, any lapsed commitment | The document does not state a commitment, or a date clause 6.2(k) or 10.2 requires; a kind C ticket does not quote it; a lapse has no clause 10.2 record, minuted or staged |
| 10 | Temporary states | Anything left out of the gate because it will revert before audit — recorded only in an `ICR` comment with the trigger that reverts it, instead of being amended into a durable record | The user has not confirmed, in this run, that it should be left out |
| 11 | This run's comment | Read the outcome comment before posting it | It says an item is untracked, or asserts no gap and then records one |

**Not a check: a pending risk acceptance.** An acceptance awaiting its management review minute does
not hold the ticket — other controls handle the acceptance, and once the ISMS is fully active risks
go through Jira for approval. Record it in the outcome comment: the risk, the residual level to be
accepted and the forum that will minute it.

**Judged at audit, not today.** The gate asks what an auditor will read. That is why a temporary state
that reverts first can be left out (check 10) — and why it takes the user's confirmation each time,
since only they know it will revert.

---

## §3 Carriers

- **An open `IRT` ticket carries a gap when its deliverable closes it.** Read the deliverable. A
  ticket that merely mentions the control, or carries a neighbouring piece of work, is not a carrier.
- **The policy queue carries only what a row's detail comment names**, and only once the row is in
  `git show origin/main:compliance/isms-policy-queue.md` (after `git fetch origin` in
  `security-documentation`) and its draft edit is on `main`. A row only in the working copy carries
  nothing yet. The queue ticket is found with `project = IRT AND labels = PolicyQueue`; the page's
  index alone cannot tell you what it carries.
- **Nothing outside `IRT` carries a gap.** `CSIP`, `OP`, `CYB` and other `ICR` tickets are not
  carriers. Where one of them is all that tracks a gap, the gap is untracked for this gate — raise the
  `IRT` ticket, or hold.
- **A recorded acceptance needs no carrier.** An accepted residual whose acceptance is recorded — a
  minute, or a dated change-record comment — is a position, not a gap. So a pure `ACCEPT` control, or
  one whose only ongoing work is a recurring review routed to `CYB`, needs no carrier. An acceptance
  still waiting for its management review minute does not hold the ticket either (§2, *Not a
  check*); the outcome comment records it as pending.

---

## §4 A not-ready flag, and steps only the owner can take

`isReady: false` holds the ticket or not according to its **cause**, never the flag alone. Find the
cause first — the three that set it are in `drata-fields.md` §2.

| Cause | Holds? | The way out |
|---|---|---|
| A **control approval** still configured, granted or not. A not-granted one sets the flag; approval state is not readable through this connection, so ask | **Yes**, until the user removes it | Bitpool does not use control approvals (decision 2026-08-24) and is removing them as controls are reviewed; they are the most common cause of a not-ready control here. Ask the user to remove it in the Drata UI, re-read the flag, then close |
| A **monitoring test failing because of how it is set up in Drata**: checking resources outside the control's scope, or unable to read the system because its connection is broken; or, **only after the investigation below**, mapped to a control it does not test at all | **Yes**, until the owner fixes it. These are steps only the owner can take in the Drata UI, never `IRT` work | Ask the user to exclude the out-of-scope resources from the test or reconnect the integration; re-read the result, then close. **Never recommend unmapping or remapping a test to clear the flag.** Taking a test off a control is legitimate only when the test checks nothing the control's `description`, `activity` or `question` asserts. Compare the test's check against every element of that text first, and record the comparison in the `ICR` comment. A test that also sits on another control is not misplaced for that reason: shared tests are normal, and overlap is not grounds. Where any element overlaps, the test belongs and its failure is the next row's case. Where none does, a test that belongs to a different control is remapped there rather than simply removed. Either way it is the user's investigated decision, never the recommended option |
| A **monitoring test failing because the control is not operating, or because a Bitpool custom test's logic is wrong** | **No**, when an open `IRT` ticket's work will make it pass. **Yes** when nothing carries it | Record the test against that `IRT` ticket in the Gate table. With no carrier, fix the cause in this run — a custom test's logic through `/create-drata-test` — or raise the `IRT` ticket, then close; otherwise hold, with *"closes when test `<id>` passes, or when an open `IRT` ticket's work will make it pass"* as the condition |
| **Evidence** attached and expired, where the renewed artefact exists | **Yes** — check 7 | The user uploads it; re-check; close |
| **Evidence** attached and expired, where its renewal cannot exist until planned work lands | **No**, when an open `IRT` ticket or evidence sub-task will produce it | Record it in the Gate table against that ticket |

**Taking a test off a control narrows what the control is monitored for.** Where the comparison shows
a test does not belong, put it to the user with that comparison. Where the test overlaps and the user
still wants it off, that changes what the control asserts. The control text is corrected in the same
decision (`SKILL.md` golden rule *A control's text CAN be corrected*), or the test stays. Never do one
without the other. Worked example, 2026-10-15: *Employee Background Checks* failed on `DCF-46`
(Formal Screening Process) and also sits on `DCF-39`. A run recommended unmapping it as `DCF-39`'s
subject, but `DCF-46`'s description asserts identity and qualification verification, which the
background-check package covers. It stayed mapped.

Missing evidence never sets the flag (`drata-fields.md` §2); check 7 covers it.

The converse holds too: `isReady: true` is not the gate. It says only that nothing configured is
failing — `DCF-20` was ready while `Implemented: N`, and its `ICR` ticket still turned on its register
row. Never trust `flags.hasEvidence` either (`drata-fields.md` §2).

---

## §5 The rule this replaced, and worked examples

- **Superseded 2026-09-29.** Step 10 used to say that closing asserts *"this control has been
  reviewed and is ready for audit"*, while also saying that open `IRT` work, an evidence file not yet
  uploaded or a queued policy row were never reasons to hold the ticket, and that *"a review that
  concluded is a review that is done"* — all attributed to a Bitpool decision of 2026-08-24. The
  instruction that day was narrower: mark the ticket done once *"the control has been reviewed and is
  ready for audit. it doesn't matter if the RTP is completed or not"*. Ready for audit was the
  condition; the file turned it into something closing asserted without checking, and no step ever
  re-tested a closed ticket. So a closure could go false and stay false.
- **Hold, then close — `ICR-191` (`DCF-777`).** Closed 2026-08-28 with its own comment recording the
  control as *"Not ready"*. Its register `Rationale` went false the same day, when `CYB-526` recorded
  the Azure resource groups tagged and verified 21 minutes after the closure, and again on 2026-09-18,
  when the tagging standard's EKS scope rule changed. No run re-tested it for a month. Reopened
  2026-09-29 with its gaps carried under `IRT-45` and the false `Rationale` named as the blocker;
  closed the same day once the row was corrected — 23 seconds before the commit that put the
  correction on `main`, so under this gate it too would have waited for the push. `IRT-49` had
  closed as done minutes before the row
  stopped saying the work was not done — the ordering `irt-tickets.md` §4's *On completion* step now
  prevents.
- **Close — `ICR-16` (`DCF-20`), 2026-09-29.** Applicable, not implemented, every gap carried under
  `IRT-45`, and the register row — the only thing holding it — corrected before the transition. The
  commit that put the correction on `main` came 25 seconds *after* the transition, made by a
  concurrent session. Under this gate that closure would have waited for the push.
- **The case the old rule was written from — `ICR-148` to `ICR-151`**, the four A.8.17 clock
  controls, closed together on 2026-08-24 with `IRT-20` carrying the endpoint gap. `ICR-150` and
  `ICR-151` meet this gate. `ICR-148` and `ICR-149` corrected the Logging and Monitoring Policy draft
  the day the policy queue was created, and no queue row was ever raised for it; under this gate they
  would have held until it was.
