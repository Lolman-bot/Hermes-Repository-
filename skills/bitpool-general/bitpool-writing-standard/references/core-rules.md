# Core rules — the three record kinds, the six rules, and where specifics are right

Loaded from `/bitpool-writing-standard` **after** the target gate (`SKILL.md` Step 1) has matched a
registered target and its writing profile. Nothing here applies outside the register. Profiles and
`durability-check.md` cite these as *core rule 1* … *core rule 6*.

## Three kinds of record (SKILL.md Step 2)

Within a registered target, decide which kind of record you are writing **before** you write a
word. The profile says which of its fields and page types are which.

| Kind | What it is | Specificity |
|---|---|---|
| **Durable** | A standing statement, read later as "how things are" | Shape, categories and pointers — never copied current-state values |
| **Snapshot** | A dated record of a moment, read later as "what was true then" | As specific as the moment warrants — that is its job |
| **Structured field** | A field the system itself treats as the value | The value, exactly — this field is its home |

**The test.** Will someone read this later as a statement of how things are *now*? Durable. Is it
dated, and read as what was true *then*? Snapshot. Is it the field the system reports, filters and
alerts on? Structured. Get it wrong either way and the record fails: a durable body treated as a
snapshot fills with counts that go stale; a snapshot treated as durable loses the specifics that
were the point of writing it down.

The calibration pair — a Drata evidence description on `DCF-527`, corrected by the Head of
Information Security. The *before* is a labelled anti-pattern: never copy it, and never "fix" it in a
sweep.

> **Before — copies the contents.** *"Bitpool's designated Data Protection Officer. The role is held
> by the Head of Information Security, Eric Sharp, who was appointed and accepted it on 31 July
> 2025. The page sets out the Data Protection Officer's responsibilities for Bitpool's privacy
> program, and their role as the point of contact for authorities and data subjects. It also gives
> the monitored contact mailboxes (dpo@bitpool.com, and privacy@bitpool.com as published in the
> Privacy Policy) and the appointment record."*
>
> **After — describes the shape.** *"URL points at the RACI Designated Roles and Teams page on
> Bitpool's internal wiki. The page is the controlled record of the roles Bitpool designates for a
> specific duty. It evidences DCF-527 by recording the appointment of the Data Protection Officer,
> the role through which it is held, the responsibilities assigned to it, and the contact mailbox
> through which authorities and data subjects reach it. The page is version-controlled, so its
> change history records each appointment and change."*

The second version is not vaguer. It is *more* precise about what the artefact is, where it lives,
what it records and why it can be trusted. It is silent only about the values, because the page
holds those and the page will change.

---

## The six core rules, for durable text in an in-scope target (SKILL.md Step 3)

### 1 · One home per fact — and the pointer must resolve

Every value has exactly one system of record. Write the value there. Everywhere else, **point at
it** — by name, code, key or query — and stop. A second copy is a second truth, and the two will
disagree; nobody updates the copy when the original moves.

Common homes: the current risk owner is Drata's `owners` field; a policy's current named owner is
Drata's policy owner; who currently holds a role is the RACI Role Holders page; the appointment
record for a designated role is the RACI Designated Roles and Teams page; AWS accounts are the AWS
Organization, enumerated live via `/aws-query`; a commitment's date is the IRT `duedate` — except an
objective or corrective-action date that a controlled document carries, where the document is the
home and the ticket quotes it; a threshold, SLA, cadence, scale or tier is the policy that sets it;
which controls a risk treats is its `control_ids` link; another record's content is that record.

So: *"findings are tracked to resolution against the SLAs in the Vulnerability Management Policy"*,
never *"Critical 24 hours, High 3 days"*. *"Tracked in IRT-28"*, never a date. *"Code review — not
performed; treated under DCF-5"*, never a paragraph re-explaining what DCF-5 owns.

**A pointer is a claim that the home holds the value, and an auditor will test it there.** Before
writing *"on the cadence the `<policy>` sets"* or *"as recorded in the `<register>`"*, open the
version **in force** — the approved, promoted document, not a draft — and confirm it holds the
value. Where it does not:

- **The record's claim needs the value to be testable** — a cadence a treatment commits to, a
  criterion a control applies. State it as an anchored fact with its source (*"reviewed every
  `<period>`, as decided at the management review of `<date>`"*), and raise the missing parameter as
  a correction through its owner (a policy through `/isms-draft`). The pointer replaces the value in
  the change that fixes the home.
- **The value exists only in a draft awaiting promotion.** Point at the draft and its tracking
  ticket; the promotion change removes those qualifiers from every record in one pass.
- **Otherwise**, put the value in a dated snapshot, write the durable text at category level without
  a pointer, and tell the person which home is missing and what should become it.

A pointer to a home that does not hold the value is a false statement, not a durable one. Only a
home that exists today may be named.

### 2 · Describe the shape, not the contents

A durable description of an artefact, record or mechanism says five things, and only these five
need to be true for it to stay true:

1. **What it is** — the artefact, record, mechanism or position.
2. **Where it lives** — the system, register, page or library, by title.
3. **What kinds of information it holds** — categories: *"the appointment, the role, the
   responsibilities, the contact mailbox"*.
4. **Why that satisfies the requirement** — the link to the control, clause or risk.
5. **What keeps it trustworthy** — two things. Its **integrity**: where its history is kept
   (version control, a new version per occurrence, generation from live state). Its **currency**:
   what re-checks it and on whose cycle (the policy, control or recurring task, by name). Version
   control shows what changed, not that anyone confirmed it is still right. The next due date is a
   structured renewal date; never restate it.

Other durable text — a risk's position, a ticket's outcome, a policy requirement — takes the shape
its profile sets, under the same principle: **be exact about pointers, general about contents.**
The artefact's name, the register's title, the `DCF` code, the policy, the role — those are the
precise part, and vagueness there is its own failure: *"documentation is maintained"* is not
durable, it is empty. Categories are claims too: *"the contact mailbox"* asserts the page records a
contact channel for the role, so check each category against what the artefact actually holds
before you write it. What you leave out is the values the categories hold.

### 3 · Never copy current state — and never generalise past the truth

Anything true *now* that may not be true next quarter lives in its home or in a snapshot, never in
durable prose:

- **who holds a role** — rule 5;
- **how many** — counts, tallies, *N of M*, totals, in digits or words: write the criterion, not the
  tally — *"risks assessed as High or Critical before treatment"*, never *"three of the 47 active
  risks"*;
- **which ones** — AWS accounts, account names and IDs, hosts, IPs, resource lists, sites: describe
  the population — *"every account in the AWS Organization"*, *"the account holding production
  workloads"*, never *"the seven AWS accounts"* or their names;
- **what is in use** — products, vendors, versions: name the capability — *"application
  allow-listing on managed Windows endpoints"*, not the product doing it this year. Test it: if
  Bitpool replaced the product tomorrow, would the sentence go false? Name a product or vendor only
  where it is a pointer or the subject rather than current state — a system of record the text points
  at (Drata, Jira, the AWS Organization, the Bitpool Private Wiki); a record about that vendor or
  product; a provider whose own assurance the position relies on; or a product a control or policy
  names as the requirement;
- **how it is configured** — config values, retention periods, session lifetimes: point at the
  system or baseline that holds them;
- **contact details** — mailboxes and addresses: name the channel and where it is published;
- **status and progress** — *pending, not yet, currently, at this time, to date, has not been,
  begun, provisioned, being rolled out*: state the standing position and point at where status is
  tracked. A treatment's split between measures **relied on** and measures **planned** is the
  position, not status: state each planned measure as its outcome, the condition on which it will be
  relied on, and its IRT pointer — *"application control enforced across the managed Windows estate;
  relied on once enforcement is complete; tracked in IRT-n"* — never its progress;
- **relative time** — *"20 months ago"*: give the date.

Two tests, both cheap:

- **Twelve months.** Would this sentence still be true in twelve months — or, for a ticket, for as
  long as it is open — with nobody editing it?
- **The owner.** If the record that owns this value were edited tomorrow, would this sentence go
  false?

If either answer is wrong, generalise the sentence to its category and point at the home. **Remove
the value; do not correct it.** Replacing a stale "five accounts" with an accurate "seven" only
resets the clock.

**Generalise to the true boundary, never past it.** The general wording is a new claim and must be
exactly as true as the value it replaces. *"Every account in the AWS Organization"* is false where
an account is excluded by a recorded decision — write *"every account in the AWS Organization
within `<the scope record that sets the boundary>`"*, or name the exclusion rule. *"Enforced on
managed Windows endpoints"* is false while enforcement is partial — write what operates, and that
the remainder is carried on the risk register. **Durability never outranks truth.** If the only
durable wording overstates what operates, write the true position and accept that it will need an
edit when the position changes.

### 4 · A fact is a fact — state it where it is needed, anchored as an event

A **historical fact** — something that happened, on a date — does not become false: *"accepted by
the risk owner at management review on `<date>`; minuted"*. It is not current state, and rule 3
does not remove it. It may appear in a durable record when **all four** of these hold:

- **Needed here, not by reflex.** Keep it only where this record's own claim rests on it — a risk
  asserting that a compensating control operates, an acceptance a clause requires evidenced, a lapse
  a corrective action answers — and keep only the latest of each. An earlier verification of the
  same thing moves to the snapshot; it is not appended. A record that *describes* another artefact
  never repeats what that artefact holds: the `DCF-527` correction dropped the appointment date
  because the evidence describes the appointment record, and the record carries the date.
- **Anchored — all three parts.** The date; how it was established — the method (a tool run, a
  query, an inspection) or, for a decision or attestation, the role that made it and the forum; and
  where the result is recorded (an `ICR` key, the evidence on the linked controls, the minute). A
  date alone, or a date and a name, is not anchored.
- **Written as an event, in the past tense.** *"Time synchronisation was verified on `<date>` by
  `<method>` across every running instance; the result is the evidence on the linked controls."*
  Never a present-tense claim with a date appended — *"No local infrastructure exists at the office.
  Confirmed `<date>`."* That sentence is current state under rule 3; the appended date anchors
  nothing.
- **The event, not the measurement.** Anchoring makes the event true for ever; it does not make the
  values measured that day durable. The outcome the position relies on may be stated as a category —
  *"confirmed operating across every running instance"*. Counts, *N of M*, lists, account and
  resource names, observed settings and progress stay in the snapshot the pointer names, however
  dated. **Adding a date to a count does not make it durable text.**

Two consequences an auditor will test:

- **Relied on as present assurance — say what renews it.** Where an anchored fact is the basis for
  saying something *still* operates, add what re-performs it, by pointer — *"…; re-run by
  `<the control or recurring task>`, each run filed as a new version of that evidence"*. Once the
  date falls outside that cycle the assurance is stale: update it from the newer run, or stop
  relying on it. Never leave it reading as current.
- **An acceptance covers the position it accepted** — the residual level and treatment in force on
  that date. The edit that changes either one removes the acceptance sentence; the next acceptance
  event restores it with its new date and minute.

### 5 · Roles, not people

Durable prose names the accountable **role**. The person holding it is a value (rule 3) whose home
is a structured field or a named-people record (rule 1). Roles survive turnover; names do not.

- **Name a role only where this record assigns the accountability.** Where the record points at
  another that assigns it — a RACI page, a policy, a register — which role holds the duty is that
  record's content. Name the category, as the `DCF-527` correction does (*"the role through which it
  is held"*), not the role.
- **Prefer the function to the job title** — *the risk owner*, *the approver*, *top management as
  the ISMS Plan defines it* — because titles get renamed. Where a title is needed, use it exactly as
  Bitpool's RACI tables name it. One role under two titles is two pointers, and one of them points
  nowhere.
- **The named fact is never dropped — it lives in exactly one home**, reachable from the durable
  text:

| Named fact | Its home |
|---|---|
| Who owns a risk now | Drata risk `owners` |
| Who approved a treatment and accepted its residual risk — at what level, on what date (clause 6.1.3(f)) | The management review minute or acceptance record, naming the person, the risk, the residual level and the date |
| Who owns a policy now | Drata policy owner |
| Who approved a policy version | The `isms` repo commit that promoted that version, and Drata's Policy Center approval — not the draft's Version Control table, which records the date and the change only |
| Who currently holds a designated role | The RACI Role Holders page |
| When a designated role was appointed, and to which role | The appointment record on the RACI Designated Roles and Teams page |
| Who performed a review or confirmed a finding | The review record, or the dated ICR comment |

A current-owner field is never evidence of a past approval: after an ownership change it names
someone who approved nothing. **Snapshots may name people**, because who did what on that date is
the fact being recorded.

### 6 · State the position, not the record's own history

A durable body states the current position only. This rule is about the **record's own
revisions** — corrections (*"Corrected `<date>`: this line read…"*), superseded wording or
numbering, a score change (*"likelihood raised from 3 to 4 on …"*), the meeting or incident that
prompted an edit. It is not about the events the position rests on — an acceptance, a
verification, a lapse — which rule 4 keeps when they are needed and anchored.

Revision history belongs in a record built to hold history, and **the change that keeps it out of
the body creates that record at the same time**: for a Jira description, Jira's changelog plus a
comment giving the reason; for a repo document, git history plus its Version Control row; for a
Drata evidence bucket, a new version. **Drata risks and controls keep no history any skill has
confirmed readable**, so every change to a risk's scores, treatment or `treatmentDetails`, and every
rewrite of a control description, is recorded in a dated comment on the ICR or IRT ticket: what
changed, why, and on whose decision. That comment is the reassessment and corrective-action record
an auditor asks for under clauses 8.2, 8.3 and 10.2. **Which ticket is the owning workflow skill's
decision.** Where it has none it can write, it stages the record for the user to post and says so
in the approval block — a change is never made without its record being staged.

Durable text never carries session voice either — *"another session"*, *"proposed by Claude"* (or *"by Hermes"*),
*"this is yours to perform"*.

---

## Where specifics are right, even in scope — do not over-apply

Inside a registered target, this standard removes copied current state from durable prose. It does
**not** make records vague, and it does not touch:

- **Snapshots** — comments, minutes, approvals, Version Control rows, commit messages, worklogs.
  Put the counts, names, accounts and dates here; a sanctioned home for specifics is what keeps them
  out of durable fields. **Specific is not unrestricted:** secret values never appear in any record,
  and security-sensitive identifiers — allowlisted or hostile public addresses, exposed ports on
  named hosts, break-glass and administrator account names — go to a restricted home (the GRC
  evidence library, a restricted docs repo); the comment records the finding and points there.
- **Structured fields** — they are the home of their value.
- **A value in the record that is its home** — the parameter in the policy that sets it, the asset
  in the inventory register row, the hostname in a runbook its profile declares the home. Writing
  *"the idle period this policy sets"* inside that policy is circular.
- **Durable handles** — `DCF` codes, risk IDs, clause numbers, an `IRT` key with its recovery query,
  policy, page and register titles, row numbers a record declares permanent.
- **Boundaries that are the decision**, stated as the **criterion** that decides membership, with
  the policy or register that sets it — *"platforms that meet the Vulnerability Management Policy's
  criteria for penetration testing are tested; platforms outside them are not"*. A criterion is a
  property a system has or lacks. A named system is a member, not a category, and a list of members —
  in or out — is an inventory however it is phrased.
- **Contact points inside the document that publishes them, or that its reader must act on** — the
  Privacy Policy's contact mailbox in the Privacy Policy, the incident-reporting channel in the
  incident procedure. Any other record names the channel and the document — *"the privacy contact
  mailbox published in the Privacy Policy"* — never the address.
- **Stock text Drata wrote** — Drata's generic template wording (*"Drata inspected… and
  confirmed…"*, a control statement naming no Bitpool system). Leave it. Text that names Bitpool, its
  platforms, registers, policies, people or risk IDs, or carries Bitpool's spelling, is Bitpool's
  whatever the object — flag it; do not rewrite it unasked.
- **Generated artefacts** — specific by design, provided every value is derived from that run's
  data. A hand-typed value inside a generator is durable prose and falls under rule 3.
- **Page types a profile declares the home of specific values** — an operational runbook's
  hostnames and commands, a configuration page's settings. Being in a restricted repo makes a page
  private, not a home.
- **A dated snapshot block inside a durable page, where the target's profile allows one** — a table
  headed *"Verified `<date>` against `<source>"`* that reads as what was true then. Without the
  heading, or where the profile does not allow it, the same table is copied current state.
- **Requirement-level identifiers stated as what must be true** — the resource type, rule name,
  port or setting a control requires (*"no security group allows `0.0.0.0/0` on administrative
  ports"*). That is the requirement, not an observation of the estate.
- **A verbatim quote of another record, anchored** — its source and the date it was read (*"per
  Drata's description, as read `<date>`"*) — so it reads as what the source said then.
