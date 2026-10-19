# Golden rules — full text

> Relocated verbatim from this skill's `SKILL.md` when it was ported to Hermes; `SKILL.md` keeps the
> route and a summary of each rule, and this file is the full text. Bold section names refer to:
> **golden rules** → `references/golden-rules.md`; **Invoke the downstream skills** and **Bitpool
> context** → `references/bitpool-context.md`; **Batched policy changes**, **Writing a queue row** and
> **Rules for the index** → `references/policy-queue.md`; **Step 0–11** → `references/workflow.md`.

**Golden rules**

- **This skill writes to Drata. What it may call is defined in `/ask-drata`, rules 8–10 — not
  here.** Read that skill before any Drata call. Connection-level facts (which verbs work, what
  each one's trap is, which status flags lie) belong to `/ask-drata` because they are true of the
  connection regardless of which workflow is using it; copying them into a workflow skill is how
  this file ended up with four contradictory copies of the permission rule on 2026-08-21.
  In short, and **`/ask-drata` wins if these disagree**: risks may be created and updated; a
  control may have a policy or owner attached, and **its text may be corrected — see "A control's
  text CAN be corrected" below, which gates it**; control *creation* is outside this skill's write
  model; **this skill does not write evidence.** No write happens without an approved block.
  **Verified 2026-08-25, re-probed 2026-08-28: `update:evidence` is NOT granted on this
  connection.** The probe returns `403 Missing required OAuth scope(s). Required one of:
  update:evidence` (code 12330), and Bitpool enables only `read:evidence` of Drata's four evidence
  scopes. `Drata_updateEvidenceArtifacts` and `Drata_deleteEvidenceArtifact` are exposed in the
  toolset and **will 403 if called**. So evidence upload is **a real capability limit, not a policy
  choice** — say so plainly, and never offer to upload. Evidence is the one place that distinction
  runs this way: everywhere else a skill's read-only posture is policy, so never tell the user a
  skill *cannot* write when it simply *must not*. The authority is the **"Granted scope matrix"**
  section of `/ask-drata`'s `references/drata-mcp-gotchas.md` — re-probe there rather than
  re-deciding here.
  **When you confirm a new connection-level quirk, add it to `/ask-drata`, not to this skill.**
- **Requires `/bitpool-writing-standard` (section `bitpool-general`).** Before drafting text for
  Drata, for the `IRT` and `ICR` projects, proposed ISMS policy wording or register rationale, load
  it. If it is not installed, **stop and tell the user once per chat**: *"`/bitpool-writing-standard`
  isn't installed, so the Security Drata, Security Jira, ISMS Policy and Security Documentation
  writing profiles can't be applied. Installing it from the `bitpool-general` section is recommended. Proceed
  without it?"* Continue only on a yes, and do not ask again in the same chat.

  That skill decides *what the words say* in a registered target; this one decides which fields are
  written, when, and on whose approval. Read its `SKILL.md` first — the target gate and the six core
  rules — then the profile for where the output lands:

  | This skill's output | End location | Writing profile |
  |---|---|---|
  | Risk `title`, `description`, `treatmentDetails` | Drata — risk register | **Security Drata** |
  | A corrected control `name`, `description`, `activity` or `question` | Drata — controls | **Security Drata** |
  | An evidence `name` or `description` drafted for the user to paste in | Drata — evidence library | **Security Drata** |
  | SoA exclusion justification on a framework requirement | Drata — framework requirements | **Security Drata** |
  | `IRT` summaries and descriptions; `IRT` comments, including the policy queue's | Jira `IRT` | **Security Jira** |
  | The policy queue page's index rows, Status notes and At promotion steps | `security-documentation` — `compliance/isms-policy-queue.md` | **Security Documentation** — register content: structured, and dated where it records an event |
  | The `ICR` outcome, hold and in-progress comments | Jira `ICR` | **Security Jira** |
  | Proposed policy wording handed to `/isms-draft` | ISMS policy drafts | **ISMS Policy** — drafted here to that profile, written by `/isms-draft` |
  | Register `Rationale` text, mirror and procedure pages handed to `/bitpool-docs` | `security-documentation` or `it-documentation` | **Security Documentation** / **IT Documentation** — the repo's own `_meta/writing-standard.md`, where it exists. A repo whose profile is missing, and every other repo, is out of scope |

  `CSIP` is Security Jira too, but this skill never writes it (see below). Every approval block that
  stages **durable** text for one of these targets — the risk block, the control-correction prompt,
  an `IRT` create or description edit, an evidence description, register rationale, the
  policy-drift handoff's proposed wording — shows the standard's **durability check** directly
  under the staged text (its `durability-check.md` §1).
  **Snapshots** in these targets — `IRT` and `ICR` comments, the queue's detail comments — stay as
  specific as the moment warrants and take no check. **Everything else this skill produces is outside
  the register** — the paths block, the chat, the Step 11 summary, a recommendation to the `CYB`
  owner. Counts, names and dates are fine there, and neither the standard nor its check applies.
- **A control's text CAN be corrected — and doing so is a rare, explicitly approved exception,
  never a routine edit.** Superseded 2026-08-28: this file previously said a control may "never"
  have its text edited. That was stated as a capability limit and it was **false**.
  `Drata_updateControl` exposes `description` (30,000 chars), `name`, `activity`, `question` and
  `code`, and `/ask-drata` gotcha #9 records the live probe returning **404, not 403** — meaning
  `controls-put` **is** granted. The cost of believing the old rule is not theoretical: it leaves
  a Drata control asserting something untrue because the skill thinks it has no way to fix it, and
  tells the user the same. Worked example, 2026-08-28 — `DCF-558` described Windows Defender
  Application Control long after ThreatLocker replaced it, the description claimed deployment to
  *all* Windows devices when enforcement was partial, and the same false text had already been
  copied into `compliance/drata-controls-register.md`.

  **So: know the capability exists, and weigh the impact before using it.** A control description
  is auditor-facing — it is the statement an auditor tests the evidence *against* — so rewriting it
  changes what Bitpool asserts about itself. Establish all five before proposing anything:

  1. **What the current text claims that is untrue**, quoted verbatim.
  2. **Whether the correction narrows or widens the claim.** Narrowing is usually the right move and
     needs no new evidence — it stops a control over-asserting. **Widening needs evidence first**;
     never write a stronger claim than the artefacts support.
  3. **Every other copy of the same text.** A control description is routinely mirrored into
     `compliance/drata-controls-register.md` and sometimes into an ISMS document. Fixing Drata alone
     leaves the records contradicting each other, which is worse than one wrong record.
  4. **Whether the underlying gap is already treated.** Correcting the description is a record fix,
     not a treatment — if the control genuinely under-performs, that still needs a risk entry and an
     IRT ticket. Do not let a tidier description stand in for the work.
  5. **Whether the replacement will stay true** — the writing standard's rules for a control
     description (Security Drata §3.3): the capability, not the product; scope by reference to the
     policy or register that defines it, never a list; claimed only as far as the true population,
     so where enforcement is partial, state by criterion what is enforced and that the remainder is
     carried on the risk register; no project state; no risk ID standing in for a link. `DCF-558`
     is the case: swapping one product's name for its successor's only sets up the next identical
     correction.

  **Never write control text without explicit, specific approval of the wording.** A general "fix
  it" earlier in the run does **not** authorise it, and neither does an approved risk block. Raise a
  dedicated approval prompt in the same shape as the risk approval block — the current text, the
  proposed replacement, a change table saying what moved and why, the other copies needing the
  same correction, the **durability check** on the replacement, and the **dated change-record
  comment** recording what changed, why and on whose decision, on the ticket named under **Confirm
  the risk wording** below (Drata keeps no readable history of a control, so that comment is the
  record — core rule 6) — and get an explicit yes on that exact wording before calling
  `Drata_updateControl`. The user is the only person who can confirm the
  replacement is true.
- **Confirm the risk wording before writing it — every time, no exceptions.** Render the complete
  risk as the approval block in `references/drata-fields.md` §4, show it, and get an explicit yes
  before calling `Drata_createRisk` or `Drata_updateRisk`. Not a paraphrase, not "I'll create a
  risk covering X" — the block, exactly as it will be written, with one durability check under the
  staged text, covering `title`, `description`, `treatmentDetails` and any rationale text
  (`drata-fields.md` §4). **The user is the only person who
  can tell you whether the compensating controls you are about to assert actually operate**, and
  they cannot tell that from a summary. Having write access does not remove the confirmation step;
  it removes the excuse for skipping it. **An amendment — or a create whose `treatmentDetails`
  anchors an approval or acceptance to that comment — also stages its dated change-record
  comment** — what changed, why and on whose decision — in the same approval. Drata keeps no
  readable history of a risk, so that comment is the reassessment record (core rule 6); the history
  never goes in `treatmentDetails` itself. **Which ticket carries it is this skill's decision**, for
  a risk change and a control rewrite alike: the `IRT` ticket of the risk concerned where one
  exists, otherwise this run's `ICR` ticket. Where this skill can write neither, stage the comment
  for the user to post and say so in the approval block.
- **Never set a risk reviewer.** Bitpool decision, 2026-08-24: `reviewers` is left empty on every
  risk, create or amend — clause 6.1.3(f) requires the *risk owner's* approval, not a second
  party's. An empty field is correct and is never a finding; a populated one is drift to clear.
  Full rule, drift handling and the `DCF-16` reasoning: `references/drata-fields.md` §7.
- **Show approval blocks as formatted markdown in the chat — never inside a fenced code block.**
  The templates in `references/` are fenced *there* only to delimit them within the file; that is
  not how they should reach the user. A block you are asking someone to check line by line has to
  be scannable, and a wall of monospace is exactly where an untrue claim survives unnoticed. Use a
  table for fields and headed lists for prose. Applies to all three templates: the risk approval
  block (`drata-fields.md` §4), the paths block (`treatment-decisions.md` §7) and the policy-drift
  handoff (`policy-alignment.md` §4). The durability check under a block is a markdown table too —
  one per block, never a fenced code block.
- **When a defect in an output traces to a rule in this skill, fix the rule before the output.**
  Otherwise the next control review reproduces it, and you spend the session correcting copies
  instead of the cause. The order is: name the defect, find the rule that permitted it, change
  the rule, *then* correct the artefact. Say plainly which of the two you are doing at any
  moment — a user watching you edit a skill mid-review needs to know it is deliberate.
  This is not perfectionism about the skill; a control review touches dozens of controls, so a
  rule that produces one false claim will produce dozens.
  **Where the defect is text in a registered target that is too specific** — a count, a name, a
  copied value, a date, record history — **check `/bitpool-writing-standard` before touching this
  skill.** One of its six core rules almost always covers it. Then follow that standard's own steps
  for a record rejected as too specific, instead of the order above: correct the record, then add
  the before/after pair to the target's profile rather than a new rule, fix any template or worked
  example in this skill that produced the text, and offer `/log-skill-divergence` against the
  standard. Add a rule *here* only
  for a workflow decision — which field, when, on whose approval — never another offender. A list
  of offenders is an open set: this skill's grew one incident at a time and still missed people,
  mailboxes and products.
- **A policy is not evidence that a control operates — and during a control review the policies are
  the least reliable source in the room.** This skill exists precisely because Bitpool's documented
  position and its actual practice have diverged. The policies are the *record of that divergence*,
  not the correction for it, and a review like this one rewrites several of them before it ends.
  So: **never lift a control statement out of a policy and assert it in `treatmentDetails` as
  something Bitpool does.** For every compensating control you are about to enumerate, name where
  you verified it — a Drata control with `isReady: true` *and* evidence, a live system observation,
  a Jira workflow you actually read, or the user saying so in this conversation. If none of those
  apply, **ask**, or write it as a gap. Never split the difference by hedging the wording.
  Worked failure, 2026-08-21: the Separation of Duties Policy states that code changes are
  peer-reviewed by someone other than the author, enforced by branch protection. That went into a
  risk as an operating preventive control. It does not happen at Bitpool — and `DCF-5` was sitting
  at `isReady: false` the entire time, which would have caught it for the cost of one flag check.
  One unchecked sentence put a false control statement into the register, which is the single
  fastest way to discredit every other entry in it.
- **Mandatory clauses cannot be accepted.** Clauses 4–10 have no applicability and no acceptance
  route. If the control maps to a clause, the *only* legal answer is a **committed plan to comply**.
  This is a hard gate at Step 2 — never offer acceptance for a clause gap. A **risk treatment plan is
  also not available** for a clause, and there is **no risk register entry at all** either way. Two
  instruments exist, and which applies decides the ticket's label:
  - **A corrective action under clause 10.2**, where the gap is a **nonconformity** — the organisation
    is not meeting a requirement it is bound by. Label `Clause` + `Corrective`.
  - **An information security objective under clause 6.2**, where the work is **planned
    betterment** rather than a gap being closed. Label `Clause` + `Improvement`.

  If the user proposes a "risk management plan" for a clause control, say plainly that route doesn't
  exist and name the one that does. **Added 2026-09-15:** this rule named only 10.2, while the label
  scheme (`references/irt-tickets.md` §3) has carried an `Improvement` route since 2026-08-26 — so a
  6.2 objective was funnelled into "nonconformity" at the Step 2 gate and never recovered.

  **Where that plan's date lives:** in the **controlled document**, which clauses 6.2(k) and 10.2
  oblige to state a completion date and which the IRT deferral does not touch. The IRT ticket carries
  the estimate now and its `duedate` after the prioritisation pass. Never read "committed plan" as
  licence to put a date on the ticket at creation — see **Dates live in Jira `IRT`** below.
- **Read the clause's own words before deciding anything.** `Drata_listRequirements` returns
  `longDescription` — the actual requirement text. Read it. Clause wording is routinely narrower or
  more permissive than the control description and the Drata evidence guidance imply, and the
  difference frequently decides the whole question. Never reason about a clause from memory.
- **Gather fully, then offer paths, then ask.** Finish Steps 1–3 before proposing anything, then run
  Step 4: 2–3 named paths, each with its cost, its document/ticket consequences, and what an auditor
  would make of it. Recommend one. Do not survey every theoretical option, and do not skip the ask.
- **Never invent risk-scoring or acceptance criteria.** Read the **Risk Assessment Policy** first
  (Drata policy id `17`). It defines the scales and the acceptable level of risk. A residual score
  above that threshold cannot be accepted without an explicit, escalated exception.
- **Policy renewal lapse is a known, accepted state — do not report it.** Bitpool decision,
  2026-08-24: the ISMS policy set is renewed **once, in bulk, after the control review programme
  resolves** — not policy-by-policy as each control is reviewed. So a `renewalDate` in the past and
  an `approvedAt` of `null` are the *expected* condition of every policy until that bulk event.
  **Never raise it as a finding, an unconditional, a risk, or a bottom-line row**, and never caveat
  a score with it. Read policy *content* freely — that is still the source for scoring — and say
  nothing about its dates. The bulk renewal is tracked by the policy queue ticket (see **Batched
  policy changes** below); if that ticket is missing, its absence is the finding, never the dates.
- **Policy edits are queued, not promoted per control.** A control review that finds drift hands the
  wording to `/isms-draft`, claims a row on the policy queue page, and posts the row's detail comment
  on the policy queue ticket. It never creates its own "promote policy X" subtask, because many
  controls touch the same few policies. **Nothing row-related goes in the ticket's description** —
  the detail is the comment, and the index, the Status notes and the At promotion steps are the
  page. See **Batched policy changes**.
- **Withdrawing a control means rewriting the document section, never deleting it.** When a decision
  removes a control a policy claimed, A.5.3 still requires the conflicting duty to be *identified
  and documented* — so the section stays and is rewritten to say the duty is not segregated, why
  that is acceptable, and what covers it instead. Deleting it removes the identification along with
  the control, and a duty absent from the record reads as one nobody noticed. In the risk entry the
  same item moves to `ACCEPTED EXPOSURE`; it is not struck out. Worked example, 2026-08-24: the
  Separation of Duties Policy's `### Control Attestation and Compliance Evidence` was slated for
  deletion when Bitpool dropped second-person control approval, and was rewritten instead.
- **A deferral must point at a control that actually has a position.** `"treated under DCF-x"` in
  `treatmentDetails` is only legitimate if `DCF-x` carries a recorded decision. Before writing one,
  check: does that control have a risk linked, and a `Rationale` entry in
  `compliance/drata-controls-register.md`? If not, the deferral is a dead end that reads as coverage.
  Worked failure, 2026-08-24: `CR-05` item 12 said *"Code review — not performed; treated under
  DCF-5"*, and `DCF-5` had no position and — verified with
  `Drata_searchRisks(controls=["DCF-5"])` → `totalCount: 1` — no risk other than `CR-05` itself.
  The pointer looped back to its own source. Say so plainly and raise the second control's review;
  do not let a circular reference stand as a treatment.
- **Never remove a plan before the document that declares the gap is fixed.** Retiring an IRT ticket
  or closing a commitment while an ISMS document still says the gap exists leaves the worst of both:
  a self-declared nonconformity with nothing tracking it. Document first, ticket second — always,
  and state the ordering explicitly when staging.
- **Write risks in risk language, never as a restated control gap.** "We don't do X" is not a risk;
  it's the gap. See `references/treatment-decisions.md` §4 — this is the single most common way
  these entries fail an audit.
- **One direction of truth per fact — this skill names the homes; `/bitpool-writing-standard`
  governs the words.** Scores, treatment rationale and the register position live in Drata.
  Execution — scope, estimate, progress and, once the prioritisation pass has run, the date — lives
  in `IRT`. Never restate one system's fact in the other: they drift, and three different dates for
  one commitment discredits everything else. **Inside a durable field, what may be written is the
  standard's core rules plus the Security Drata and Security Jira profiles, and this skill does not
  restate them.** Every pattern that kept reaching `treatmentDetails` is covered there — a scoring or
  review paragraph, a re-explanation of what another control owns, a measured count, a threshold,
  SLA, cadence or tier a policy sets, a control already linked in `control_ids` (the link *is* the
  reference; `references/drata-fields.md` §4). Two of them were rejected by the risk owner on
  2026-08-27, in terms worth keeping as the reason this skill defers to the standard rather than
  judging "specific enough" for itself: **"stop committing to specifics in the risk treatment plan…
  THIS WILL CAUSE SO MUCH DRIFT"**; and, of a draft that named its linked neighbours in prose, that
  it *"is almost saying 'hey, here is a list of shit not treated by this RTP'"*.
- **Measurements go in a snapshot, never a durable field.** An `IRT` ticket is not one kind of
  record: its summary and description are durable, exactly as a risk entry is, and its comments are
  snapshots. So a count, an N-of-M, a per-account tally, a resource name or an observed setting goes
  in the **Observed** section of the `ICR` outcome or hold comment (Step 10), an `IRT` comment, or the evidence
  artefact — never into a risk, a control description or an `IRT` description. A verification a
  risk relies on stays only as core rule 4 allows: the latest one, written as a past-tense event
  with its date, its method and where the result is recorded, with no counts inside it, and with
  what re-performs it where it is relied on as present assurance. **Adding a date to a count does
  not make it durable** — *"24 of 25 devices as at `<date>`"* is a snapshot line and an anti-pattern
  in any durable field, although an earlier edition of this rule offered it as the durable form.

- **Dates live in Jira `IRT` and nowhere else — and, until the review programme lands, not yet even
  there.** The first half is a Bitpool decision of 2026-08-21, which removed the old "mirror the
  date" exception entirely. The second is a Bitpool decision of **2026-09-15**, which defers *when*
  a date is set without changing *where* it lives:
  - **Create every IRT ticket with no `duedate` at all** — not a date copied from a controlled
    document, not a date agreed with the risk owner. A date chosen one ticket at a time, while the
    **`ICR` control review programme** is still discovering the scope, is a guess made without
    knowing what else is committed or how much of it there is. Every date is set at once, in a
    prioritisation-and-planning pass across the whole board, after every `ICR` ticket has closed on
    the audit-ready gate (Step 10) — a few deliberate holds excepted — and the board is complete.
    **That pass is not this skill** — it is tracked by the standing
    **`IRT prioritisation pass`** ticket (`project = IRT AND labels = PrioritisationPass`), whose own
    `duedate` is the pass date. Read it there; never copy it into a ticket body or into this file.
  - **The Original Estimate carries the load instead** — mandatory, in hours, on every `Task`. It is
    the input the pass plans from, which is exactly what it was captured for.
  - **Say the cost out loud on every ticket you stage** — in the approval block, and in the
    creation comment staged with the create (`references/irt-tickets.md` §4) — a Sub-task gets one
    only where it has creation-time state. Never in the description, where
    *"not yet scheduled"* goes false for every ticket at once when the pass runs (Security Jira
    §3.1). An undated ticket cannot appear in an overdue query, so nothing chases it until the pass
    runs. Findable, not chased:
    `project = IRT AND duedate IS EMPTY AND statusCategory != Done AND labels in (RTP, Clause)`.
  - **Not retrospective, and exactly two exemptions.** Existing dated tickets keep their dates; the
    standing `PolicyQueue` and prioritisation-pass tickets keep theirs. Full rules in
    `references/irt-tickets.md` §1.

  The rest of this rule is unchanged, and none of it is weakened by the deferral:
  - Drata's `anticipatedCompletionDate` on a risk is **deliberately left blank**. It is optional, it
    triggers nothing, and populating it creates a second copy of a date that nothing chases.
  - A Drata **control** has no target-date field at all, and control readiness is not treatment
    progress — one control can carry several treatments with different dates, so it could never
    represent them.
  - **ISMS documents carry a date only where ISO requires one — and then the document is
    authoritative.** Two cases require it and no others:
    - **Clause 6.2(k)** — an information security objective must state *when it will be completed*.
      A 6.2 objective without a date is nonconforming, so the document must carry it.
    - **Clause 10.2** — a corrective action's dated commitment.

    In both cases the **controlled document is the parent of record**, and its date is quoted
    verbatim into the IRT ticket's **description** under `Date constraint:` — naming the document's
    version or the date it was quoted, so it reads as what the document said then — never into
    `duedate`, which stays empty until the prioritisation pass. **A kind C ticket whose document
    states a date while the ticket carries none is therefore the expected state, not drift.** If
    the pass later lands on a different date, the document still wins: amend it via `/isms-draft`
    in the same change, rather than letting the two disagree.
    Everywhere else, a document states the commitment and points at the IRT ticket **without**
    restating the date — the worst drift found so far came from a Skills Matrix carrying its own
    dates when nothing obliged it to.
  - **Never take a date from a mirror.** `IRT-1`'s `duedate` was 2027-01-17 — exactly six months
    after the wiki mirror's 2026-07-17 sync, while the controlled document still said "end 2024" —
    until it was cleared on 2026-09-15. The ticket had inherited the wrong parent. Read the
    controlled document, never its copy.
  - A risk's `treatmentDetails` **does** reference its IRT key, because that pointer is the only
    path from the register to the authoritative record of the commitment — its scope, its owner, its
    estimate, and once the prioritisation pass has run, its date. That is load-bearing, not
    decorative, and while the date is pending it is *more* load-bearing, not less: the pointer is
    the only thing connecting the register to anything at all.
  - **And the IRT key is *all* it carries. No date, no month, no year, anywhere in the prose.**
    Added 2026-08-27, because the rule above was read as governing only the
    `anticipatedCompletionDate` field while dates went into the text beside it — which is the same
    second copy, in a field nobody diffs. *"September 2026 application cycle"* and *"May 2026 API
    artefacts"* are both dated commitments; `IRT-28` already holds them, and the moment a cycle
    moves the register contradicts the ticket.

    Write **"outstanding execution is tracked in `IRT-n`"**, with its recovery query (Step 9), and
    stop. Where two commitments need telling apart, distinguish them by *what they are* — the
    application, the API — never by when they fall due. Month names look durable and are not:
    Bitpool intends to consolidate two penetration test cycles into one, at which point every
    "September cycle" in the register is wrong and nothing will have flagged it.

    The one exception is an **anchored historical fact**, on the writing standard's terms (core
    rule 4): an event the entry's own claim rests on, kept only where it is needed and only the
    latest of each, written in the past tense with its date, how it was established and where the
    result is recorded — *"verified closed at re-test on `<date>` by `<method>`; the result is the
    evidence on the linked controls"*. It states what happened rather than what will, so it stays
    true; commitments do not. Rejected by the risk owner, 2026-08-27: *"why commit to specific
    dates in the risk treatment plan? that will cause drift right? Jira carries the dates."*
- **Never propose a `duedate` for a new IRT ticket at all.** There is nothing to propose while the
  deferral holds, and inventing one so the ticket looks complete is the exact failure this change
  exists to stop. Where a date genuinely *is* being set or changed — the prioritisation pass, or an
  edit to an already-dated ticket — **suggest, never set unasked**: propose it with your reasoning
  and get agreement, on the original value *and* on any later change. When a date changes, **add a
  Jira comment recording why**, so the reasoning sits beside Jira's own changelog entry. The
  changelog proves *what* changed; only the comment explains *why*, and the why is what an auditor
  asks for. A ticket receiving its **first** date from the pass is an origination, not a change —
  record the pass and its reasoning, not an explanation for a move that never happened.
- **Every Jira write is staged, then approved.** Show the exact summary, description, **original
  estimate**, assignee and labels; get a yes; then execute. On a create, show the due date too —
  written as `duedate: (none — set in the prioritisation pass)`, so a reader sees a decision rather
  than an omission. A real staged date appears only where one is genuinely being set or changed.
  Same rule `/drive-iso27001` applies to CSIP. The summary and description are durable Security
  Jira text, so the durability check sits under them. Anything true only at creation — what was
  measured, who confirmed it, the cost of being undated — goes in a dated comment staged in the same
  approval, never in the description; comments are snapshots and take no check.
- **Re-read a ticket immediately before you update it, and send only the fields you are changing.**
  `editJiraIssue` replaces whatever you pass. Resending a whole `description` you fetched earlier in
  the run silently reverts anything edited in between — by another session, another skill, or a
  person working in the UI. There is no conflict detection and no warning: the write succeeds and
  the other change is simply gone. Two habits, both cheap:
  1. **Re-fetch the issue immediately before the write**, not once at the start of the run. Compare
     `updated` against what you last saw; if it moved, read the current text and *merge* rather than
     overwrite. A run that creates a ticket then edits it four times needs four re-reads, not one.
  2. **Pass only the fields you are actually changing.** A due-date change sends `duedate` and
     nothing else. That is what lets a concurrent edit survive, rather than making it a race you
     happened to win.

  Worked near-miss, 2026-08-26: while `IRT-21` was open in this skill, another session rewrote its
  description to remove a false reviewer claim and cleared the same field in Drata. The date change
  that followed survived that correction **only because it passed `duedate` alone** — resending the
  full description, which every other write in that run had done, would have reverted it silently
  and nobody would have found out. Treat a whole-object write as the exception needing a reason,
  not the default.

  The same applies to `Drata_updateRisk`, for the opposite reason: there, omitted relation fields
  are left *unchanged* rather than cleared (see `references/drata-fields.md` §7), so passing only
  what you are changing is both safer and sufficient in both systems.
- **`CSIP` is read-only here, and never cross-referenced.** It is Drata's integration lane, and
  `/drive-iso27001` and `/describe-dcf-jira-ticket` already own writes to it. Read it to learn what
  exists; never write to it, and never put a `CSIP-nnn` key in anything this skill stages. The
  durable handle between systems is the control code `DCF-xxx` — a ticket key is a surrogate that
  this skill cannot keep true. See Step 10.
- **Detect policy drift; never edit the policy.** This skill *reads* Bitpool's policies, spots where
  they no longer describe reality, and **drafts the corrected wording with its reasoning** — then
  hands the edit to `/isms-draft`. It never writes policy text to `security-documentation`; the one
  file there it edits is the policy queue page, as **Writing a queue row** sets out. The
  draft → `.docx` → Drata upload → approval pipeline that `/isms-draft` and `/isms-prod` enforce is
  itself a clause 7.5 control; bypassing it to save a step is a nonconformity, not a shortcut.
- **Bounded:** one control per run in default mode. Use `/drive-iso27001` for program-wide work.
