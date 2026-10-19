# Risk verification — Phase 1 and the gate

How to test what a Drata risk asserts. Read §1–§4 during Phase 1, §5 to build the gate, and §6 when
rewriting in Phase 3. What the rewritten text may say is `/bitpool-writing-standard`'s — Security
Drata for the risk, Security Jira for the RTP ticket; this file tests claims against reality and
against that standard.

The premise: **a register entry is a set of factual claims about Bitpool, written at a point in
time.** Each one was probably true when written. The job is to find the ones that no longer are, and
the ones that never were.

---

## 1 — The claim classes

A Bitpool risk entry makes claims of six kinds. Each is tested differently, and the failure mode of
each is different.

| Class | Where it lives | How it fails |
|---|---|---|
| **A. Compensating control claims** | Each enumerated item in `treatmentDetails` | Asserted as operating when it is planned, abandoned, or was never configured |
| **B. Score claims** | `impact`, `likelihood`, `residualImpact`, `residualLikelihood` | Residual assumes treatment that never landed; or scored against scales the policy does not define |
| **C. Control linkage claims** | `control_ids` | A named compensating control has no evidence, or the control that actually treats the risk is not linked at all |
| **D. Date and pointer claims** | `anticipatedCompletionDate`, IRT keys, "tracked in" references | A pointer to a ticket that moved, closed, or never existed; a **populated** `anticipatedCompletionDate`, which is blank by decision. An **empty IRT `duedate` is not a defect** — see "Checking the RTP" |
| **E. Policy-derived claims** | Any sentence lifted from an ISMS document | The policy says it; Bitpool does not do it |
| **F. Ownership and approval claims** | `owners`, `reviewers`, any person named in prose, "approved by" prose | **Names a person at all.** Prose names the role; the current owner is Drata's `owners`, and who approved or accepted what is the management review minute or acceptance record (`/bitpool-writing-standard` rule 5). A name is the defect whether or not its holder still holds the role, so the repair removes it, never re-syncs it. Also: asserts an approval with no record. **Prose claiming a reviewer is recorded against a risk is FALSE by construction** — Bitpool records none (decision 2026-08-24) — not merely possibly stale, so it needs no lookup to refute |

---

## 2 — The source hierarchy

For every class-A claim, name the source. These are the only acceptable ones, strongest first:

1. **A live system observation** — an AWS query, a Jira workflow configuration you actually read, a
   Drata monitoring test result. Strongest, because it cannot be aspirational.
2. **A Drata evidence artefact** resolved with `Drata_listEvidence(control_code="DCF-xxx")` —
   and read, not merely counted. An evidence bucket's own `description` often records who was
   present and what was decided, which is what makes it verification rather than a filename.
3. **A Jira ticket you read in full** — status and description, not just the summary.
4. **The user saying so in this conversation.** Legitimate, and often the only source available for
   a manual control. Record who asserted it and when in the verification-record comment on the RTP
   ticket (`drata-risk-fields.md` §3) — not beside the item in `treatmentDetails`, where a dated
   attestation reads as current long after its date. Where the item's claim rests on the attestation,
   the entry may carry the latest one as an anchored fact under the standard's rule 4 — the date, the
   attesting role and the forum it was given in (this skill's verification run), and the
   verification-record comment that records it.

And the ones that are **not** sources, however convincing they look:

- **A policy or ISMS document.** See the golden rule. This is the single most common way a false
  claim enters a register.
- **`flags.hasEvidence` or `flags.hasTicket`.** Both lie. See §3.
- **A wiki page**, including one that mirrors a controlled document. The mirror is frequently newer
  than the approved original, which is itself the finding.
- **The risk entry's own earlier wording.** Circular.
- **Another risk entry that asserts the same thing.** Also circular, and it means one unverified
  claim is now propagating.

---

## 3 — The flags that lie

Verified 2026-08-24, and the reason Phase 1 cannot be done from `flags` alone. `/ask-drata` rule 10
is the authority; this is the short version.

| Flag | Why it cannot be used |
|---|---|
| `hasEvidence` | Reads `true` on evidence that is **invalid** or belongs to **another control**. `DCF-745` reported `true` while `Drata_listEvidence(control_code="DCF-745")` returned empty — the pointer was an invalid external evidence id belonging to `DCF-41`. |
| `hasTicket` | Tracks Drata-integration **provenance**, not whether a ticket exists. It is blind to any hand-created ticket, which at Bitpool is the overwhelming majority. The `ticket_status` filter contradicts the flag outright. |
| `isReady` | Usable as a "needs work" signal, but **not** as evidence a control operates. A control can be `isReady: false` purely for want of an attached artefact while the control itself runs fine — and can read green while the thing it describes has lapsed. |

**Resolve evidence with the list, ticket existence with a Jira query, and control operation with a
live observation or the owner.**

---

## 4 — What the four-bucket structure exposes

Phase 1 sorts every measure in `treatmentDetails` into one of four buckets — numbered continuously
across all four on a new entry, or on one with no stable-numbering declaration. Where the entry
declares its item numbers stable, each item keeps the number it already has, so the numbers need not
run in order down the buckets (`drata-risk-fields.md` §3, repair rule 6):

```
SEGREGATED TODAY - preventive            (1, 2, 3 …)
PLANNED - not yet operating              (4, 5, 6 …)   each naming its IRT subtask
OPERATING TODAY - detective              (7, 8, 9 …)
ACCEPTED EXPOSURE - not segregated,      (10, 11, 12 …)
  and not claimed to be
```

**This structure is a verification instrument, not a formatting preference.** A flat list of
"compensating controls" hides the difference between something that protects Bitpool today and
something that is a decision, an intention, or a sentence lifted from a policy. Forcing every item
into a bucket makes *"does this actually happen?"* unavoidable for each one.

So in Phase 1, the highest-yield check is simply: **is each item in the right bucket?** Sort every
item, whether or not the entry uses the headings.

**The written entry uses the headings only where it has a coverage story to disambiguate** — what
protects Bitpool now, what is planned, what is consciously left uncovered. A straightforwardly
treated risk is a short paragraph, and forcing four headings onto it demands an inventory nobody
needed. `ACCEPTED EXPOSURE` stays near-obligatory — an exposure omitted is an exposure hidden — and
is stated as a boundary, the complement of a positively defined protected set, never a list of what
is uncovered (Security Drata §3.2). The authority on the shape is `/manage-drata-control`
`references/drata-fields.md` §4, *The required shape of `treatmentDetails`*.

Worked example, `CR-05`, 2026-08-24 — three items were in the wrong bucket:

| Item | Was filed as | Actually | How it was caught |
|---|---|---|---|
| Independent assurance — "the annual internal audit ... performed wholly outside the conflicted roles" | **OPERATING TODAY** | Does not exist | `DCF-165` had zero evidence and no audit had ever been performed |
| Risk register review — "the reviewer recorded against a risk entry is not its owner" | **SEGREGATED TODAY** | False on most entries | Register facets. **Outcome:** the claim was withdrawn on 2026-08-24 and the reviewer field abandoned entirely — no risk carries one now, and `CR-05` item 10 records why |
| ISMS policy approval — "Approval records are retained in the Drata Policy Centre" | **SEGREGATED TODAY** | No record exists | `approvedAt` null on all 56 active policies |

The pattern to learn from it: **the most dangerous items are the ones in OPERATING TODAY**, because
that bucket is a present-tense factual assertion and it is where the residual score's justification
lives. Check that bucket first and hardest.

Two further checks on the structure itself:

- **No ritual controls.** A "control" performed by the conflicted party on their own work — the
  alert-raiser reviewing their own closure, the author reviewing their own report — is not a control,
  and an auditor will say so. It is worse than nothing because it implies coverage that does not
  exist. It belongs in ACCEPTED EXPOSURE with the exposure stated plainly.
- **No re-explanation of another control's business.** Where part of a risk is treated under a DCF
  deliberately not linked to it, the entry references it by code and stops: *"Code review — not
  performed; treated under DCF-5."* A control already in `control_ids` is not named at all (Security
  Drata §3.2). **But check the pointer resolves** — a deferral to a control that has no recorded
  position is a circular reference, not a treatment. Verified 2026-08-24: `CR-05` deferred code
  review to `DCF-5`, and `CR-05` was the only risk linked to `DCF-5`, which had no recorded position.
  The deferral pointed nowhere.

### Checking the RTP

The risk treatment plan is the IRT ticket. Read it in full and test:

- **Does every commitment in it still exist and still make sense?** A commitment whose driver was
  reversed should be closed as *superseded*, with a comment saying so — not left open and not
  silently deleted.
- **Does the ticket's description agree with the Drata record — and does it need to say it at
  all?** Verified 2026-08-24: `IRT-3` named the risk owner as one person while Drata named another,
  and named a reviewer where Drata had none. A divergence here discredits both records, and it
  exists only because the description copied a value Drata holds. **The repair removes the copy; it
  never re-syncs it.** The risk owner lives in Drata's `owners`, and whoever does the work is the
  ticket's assignee; the description says *"Risk: `<riskId>` — scores, owner and linked controls in
  Drata"* and names a role only where the ticket assigns one (Security Jira §3.2). **On the reviewer specifically the resolution is
  one-way** — the IRT text is corrected, never the Drata field, which is empty by decision. `IRT-21`
  carried the same error in two places and was corrected on 2026-08-26.
- **Is the description durable?** It states the outcome, the definition of done and pointers. Counts,
  resource and account lists, configuration values, creation-time measurements and status lines
  (*"not yet scheduled"*) in the description are `OVER-SPECIFIC / DUPLICATED VALUE` rows: the repair
  moves them to a dated comment and generalises the description (Security Jira §3.1–§3.3). The
  comments are snapshots and are not findings for being specific.
- **Does every commitment have an Original Estimate and a label?** Those are what the prioritisation
  pass plans from: a ticket missing the estimate has nothing to plan with, and one missing its label
  is invisible to the pass entirely. **Do not test for a `duedate`.**

  > **Reversed 2026-09-15.** This read: *"Does every commitment have a `duedate`? An undated IRT
  > ticket is unfindable, which is worse than a wrongly dated one."* Both halves are now wrong. IRT
  > tickets are created undated by design, and the undated backlog is found by the field's *absence* —
  > `project = IRT AND duedate IS EMPTY AND statusCategory != Done AND labels in (RTP, Clause)`.
  > Left standing, this test would have reported every correctly created ticket on the board as a
  > defect, on every risk this skill touches. See `/manage-drata-control`
  > `references/irt-tickets.md` §1.
- **Date reconciliation.** Tabulate source → date across the Drata field, the IRT `duedate`, any
  controlled document, and any wiki mirror. Divergence is itself a finding. **A date taken from a
  mirror is always wrong** — read the controlled document.

  **Two blanks are the intended state, not divergence:** Drata's `anticipatedCompletionDate` is blank
  by decision, and an IRT `duedate` is empty until the prioritisation pass. Report them affirmatively
  as deliberate blanks rather than as gaps. Where the ticket is undated and its controlled document
  states a date, reconcile against the ticket's **`Date constraint:`** line instead — a missing
  constraint line on such a ticket is the real finding. The quote should name the document's version
  or the date it was quoted, so it reads as what the document said then (Security Jira §3.2).

  **What is still in scope here, so this bullet does not read as cancelled:** a **populated**
  `duedate` that contradicts the controlled document it should have come from. That is
  mirror-inheritance — the defect that gave `IRT-1` a date six months after a wiki sync while the
  controlled document said "end 2024" — and it is about where a date came *from*, not whether one
  exists. It is the one date claim this skill still reports, and SKILL.md's *"never reports one"*
  rule carries the same exception. Report it; never fix it here.

---

## 5 — The discrepancy table (the gate)

Phase 2 output. Render it as markdown in the chat, never fenced. One row per claim that failed,
could not be verified, or copies a value whose home is elsewhere — not one row per field.

| Column | Content |
|---|---|
| **#** | The item number from `treatmentDetails` — or the field, for a row about the risk statement or the RTP ticket — so the user can answer by number |
| **Claim** | Quote it. Verbatim, not paraphrased — the wording is what is wrong |
| **Status** | `FALSE` · `UNVERIFIED` · `WRONG BUCKET` · `STALE POINTER` · `CONTRADICTS POLICY` · `OVER-SPECIFIC / DUPLICATED VALUE` |
| **Evidence** | What contradicts it, with the specific call or artefact. "`Drata_listEvidence(DCF-165)` returned empty", not "no evidence found". For `OVER-SPECIFIC / DUPLICATED VALUE`, the value's home |
| **Recommended disposition** | operating / planned / accepted exposure / generalise / delete — **and nothing is applied yet**. For `generalise`, quote the proposed wording |

**`OVER-SPECIFIC / DUPLICATED VALUE`** is a claim that may well be true but copies a value whose home
is elsewhere — a count, a person, an account name, a configuration value, a product, a policy-owned
number, another record's content — or a status that flips at a known event
(`/bitpool-writing-standard` rule 3). Its disposition is **generalise**: point at the home, at the
true boundary and never past it. **Where a copied value is also wrong, the status is `FALSE` and the
disposition is still generalise** — the repair removes the value, never re-syncs it. Correcting
"five accounts" to "seven" only resets the clock; the live count goes in the verification record.

Rules for the gate:

- **Order by severity**: `FALSE` claims in OPERATING TODAY first, then wrong-bucket, then unverified,
  then over-specific.
- **Recommend a disposition per row.** A table with no recommendations pushes the judgment back onto
  the user, which is the opposite of the point.
- **Distinguish `FALSE` from `UNVERIFIED` rigorously.** `FALSE` means you have positive evidence
  against it. `UNVERIFIED` means you found nothing either way — often the case for a manual control,
  where the owner's word is the only available source and is a legitimate answer.
- **Never let silence promote a claim.** If the user does not answer a row, it stays unverified: the
  verification record says so, and the rewritten entry does not assert it — the item is deleted, or
  restated where it claims nothing operates (planned, or accepted exposure). Never write
  *"unverified"* into the entry itself; that label goes false the day someone verifies the claim.
- **An empty table is a real and good result.** Say so in one line and stop.
- **The table is a report to the user; its persistent copy is the verification record** — the dated
  comment on the RTP ticket (`drata-risk-fields.md` §3), where its specifics belong.

---

## 6 — Rewriting the risk statement

Only reached in Phase 3, and only where the statement itself is wrong. The most common defect is a
risk written as a missing control, which can only be treated by doing the thing you just said you
would not do.

| ❌ Control gap dressed as a risk | ✅ An actual risk |
|---|---|
| "Risk that we don't apply application whitelisting to developer machines" | "Unauthorised or malicious code executes on developer endpoints, which hold source code, cloud credentials and production access paths" |
| "Risk that we have no internal audit programme" | (trick — this maps to clause 9.2, so it is a nonconformity, not a risk, and takes no register entry at all) |

**Test:** can the statement be scored for impact and likelihood without referring to the control? If
not, rewrite it.

**The statement is durable Security Drata text** (profile §3.2): it names the affected systems and
data by category — *"the platforms holding customer data"* — never by account, host or product, and
it goes in the approval block's durability check like `treatmentDetails` does.

**And check the gate before rewriting at all:** if the risk turns out to map to a mandatory clause
(4–10) rather than an Annex A control, it should not be in the register. Clause gaps are
nonconformities handled as dated corrective actions under clause 10.2 — not scored, not treated, not
registered. Say so plainly and hand it to `/manage-drata-control`; do not repair an entry that
should not exist.

`description` has a **hard 768-character limit** — the API rejects at 769. Count it.
