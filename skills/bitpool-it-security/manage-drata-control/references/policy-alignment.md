# Policy alignment — detect drift, draft the fix, hand it over

Read at Step 8 — and at Step 3 when the gap turns out to be against one of our own documents
(outcomes 2 and 4). This skill **never writes policy text to `security-documentation`** — the one
file there it edits is the policy queue page (§2). Its job is to notice that a policy no longer
describes reality, draft the correction with evidence, and hand it to `/isms-draft`.

**Text drafted here for a registered target follows `/bitpool-writing-standard` — load it first.**
The handoff is a working artefact and stays as specific as the finding needs. Four of its parts
are stored in registered targets of Bitpool's writing standard:

| Handoff part | Where it is stored | Writing profile |
|---|---|---|
| `Proposed text` | The policy draft in `ISMS/ISMS - Draft/` or `ISMS/ISMS - Draft (New)/`, applied by `/isms-draft` | **ISMS Policy** |
| `Queue page row` | The policy queue page, `compliance/isms-policy-queue.md` in `security-documentation` | **Security Documentation** — register content: structured, and dated where it records an event |
| `Queue comment` | The policy queue ticket in Jira `IRT` | **Security Jira** — a snapshot |
| The mirror page under `Also required` | `security-documentation`, outside both ISMS draft folders | **Security Documentation** — that repo's `_meta/writing-standard.md` |

Before drafting any of them, load the standard — its `SKILL.md` for the target gate and the six core
rules, then the named profile — and show the durability check (the standard's
`references/durability-check.md` §1) under the proposed policy wording wherever it is put in front
of the user, on the text you changed. `Current text`, `Contradicted by`, `Date reconciliation` and
`Reasoning` are the evidence, not stored records; a management review minute is a snapshot wherever
it is kept; the report to the user is outside the register.

**Requires `/bitpool-writing-standard` (section `bitpool-general`).** Before drafting text for an ISMS
policy draft, the policy queue ticket or page, or a `security-documentation` mirror page, load it. If it is
not installed, **stop and tell the user once per chat**: *"`/bitpool-writing-standard` isn't
installed, so the ISMS Policy, Security Jira and Security Documentation writing profiles can't be
applied. Installing it from the `bitpool-general` section is recommended. Proceed without it?"* Continue only
on a yes, and do not ask again in the same chat.

---

## 1 — Why this skill doesn't do the edit

`/isms-draft` and `/isms-prod` implement Bitpool's documented-information change control:
draft in Markdown → produce the `.docx` → upload to Drata → obtain approval → commit. That chain is
itself a **clause 7.5.2 / 7.5.3 control** (documented information must be reviewed, approved, and
version-controlled). A policy edited from outside it is an unapproved, unversioned change to a
controlled document — a nonconformity, discovered exactly when someone diffs the Markdown against
the approved `.docx` in Drata.

There is also a plain engineering reason: two skills writing the same 35 policy files will conflict.

So: **detect and draft here, apply there.** Always.

---

## 2 — Who owns which path

`security-documentation` has several owners. Know whose territory you're in before suggesting
anything.

| Path | Owner | This skill may |
|---|---|---|
| `ISMS/ISMS - Draft/`, `ISMS/ISMS - Draft (New)/` | `/isms-draft` (→ `/isms-prod`) | **read + draft a fix only** |
| `ISMS/ISO27001 Controls/`, `ISMS/Drata Policy templates/` | `/isms-draft` | read |
| `policies/`, `procedures/`, `risk-management/` | `/bitpool-docs` | read + recommend |
| `compliance/drata-tests/` | `/create-drata-test` | read |
| `compliance/isms-policy-queue.md` — the policy queue page | `/manage-drata-control` | **write** its index rows, Status notes and At promotion steps, and mark rows promoted after the bulk promotion, by **Writing a queue row** in `SKILL.md` — never its front matter, and never commit or push |
| `compliance/` (other) | `/bitpool-docs` | read + recommend |
| `notes/` | `/notes` | read |

Apart from those parts of the queue page, nothing in `security-documentation` is written by this
skill — route it through `/bitpool-docs` so that repo's taxonomy, frontmatter schema and index
tooling stay intact.

**The *why* behind a policy clause is not available to this skill.** It usually lives in meeting
notes and prior discussion, which this skill does not read. Establish it from the two sources you do
have — the clause's own commit history in `security-documentation` (see
`isms/_meta/commit-convention.md`), and the user — before proposing a change. A clause that looks
like an oversight often had a reason that still applies, so if you can't establish one either way,
say so and let the user decide rather than proposing the strip.

---

## 3 — The four drift shapes

### A. The policy sets a bar we don't meet

Our own document demands more than the standard does, and we don't satisfy our own text.

*Example:* an ISMS competence page requiring a named certification, where clause 7.2 only requires
competence on the basis of education, training, **or** experience, with retained evidence.

**Why it matters:** auditors raise nonconformities against your own documents, not just against the
standard. A self-imposed bar you don't clear is a self-inflicted finding.

**Two valid fixes — present both:** meet the bar, or amend the document to state the competence
Bitpool actually requires and evidences. **Amending is frequently the correct answer and is
routinely overlooked** — people assume the policy is fixed and the reality must change.

**Check the clause text before assuming the bar is required.** Where the standard offers alternatives
and the document picked the most demanding one, that choice was ours and we can revisit it. Quote the
clause and the document side by side so the difference is visible.

**Watch for a self-declared "No".** A document that explicitly records a role as not competent, a
control as not implemented, or a requirement as unmet is the strongest evidence an auditor can be
handed — supplied by us, in writing. Whether it's *true* is the first thing to test, because these
assertions are often stale: written when it was accurate, never revisited as the evidence
accumulated. If the current evidence satisfies the clause, the document is simply wrong and fixing
it is the whole job.

### B. The policy describes a control we implement differently

The policy asserts one implementation; the register, evidence, or live infrastructure show another.

*Example:* a policy stating blanket annual penetration testing where the real approach is
risk-scoped by application exposure.

**Why it matters:** Annex A specifies *what*, not *how* — implementing differently is legitimate.
But a policy that misdescribes the implementation is a documentation defect, and it's the artefact
an auditor reads first.

**Fix:** amend the policy to describe what is actually done, including the risk-based reasoning.
Don't quietly narrow it to whatever we happen to do — state the basis.

### C. The policy's criteria don't match our decisions

The Risk Assessment Policy defines scales, thresholds and an acceptable level of risk that our
actual register entries contradict.

*Example:* accepting a residual above the stated acceptable level; or scoring against scales the
policy doesn't define.

**Why it matters:** this one is different in kind. **It invalidates the treatment decision itself**,
not just the paperwork — clause 6.1.2(a) requires acceptance criteria to be defined in advance, so
a decision outside them isn't a documented acceptance at all.

**Fix:** stop. Resolve before staging anything in Step 9. Either the treatment changes, or the
criteria are formally revised and re-approved — never retro-fit the criteria to the decision that
has already been made.

### D. The document states a commitment whose date has passed

The document declares a gap *and* a dated plan to close it, and the date is behind us.

*Example:* a Skills Matrix committing to "formal lead implementer course completed by end 2024",
read in 2026, in a document whose version-control table records an annual review in 2025 that left
the text unchanged.

**Why it matters:** this is the most damaging of the four, and the least likely to be noticed —
every individual statement in the document is still internally consistent. It compounds:

- **Clause 10.2** — a self-imposed commitment lapsed and was never re-planned or closed out.
- **Clause 9.3** — a management review passed over it. The version-control table proves the review
  happened, which converts "we missed it" into "we reviewed it and left it".
- **Clause 7.5.3** — the controlled document no longer states the truth.

The gap the commitment was about becomes almost secondary. An auditor who finds a lapsed commitment
surviving a documented review will test whether *any* commitment in the system is real.

**Diagnose it properly before proposing a fix:**

1. **Compare every copy.** Controlled document, wiki mirror, and — where an IRT ticket exists — its
   **`Date constraint:`** line. Tabulate source → stated date. Divergence **between two populated
   dates** is itself a finding, and a mirror that is *newer* than the approved original means the
   mirror was updated instead of the document — a 7.5.3 defect in its own right.

   > **Two fields are mandated empty and are never divergence** (added 2026-09-15): the Jira
   > `duedate`, empty until the board-wide prioritisation pass (`irt-tickets.md` §1), and Drata's
   > `anticipatedCompletionDate`, blank by decision (`drata-fields.md` §3) — and absent entirely on a
   > clause commitment, which has no risk record. Record them as deliberate blanks. **On an undated
   > IRT ticket the live test is the `Date constraint:` line**: a ticket whose controlled document
   > states a date but whose body does not quote it **is** the finding, because the prioritisation
   > pass will then schedule it blind.
2. **State the elapsed time explicitly** — "end 2024, 20 months ago", not "overdue" — in the handoff
   and the report. A stored record — the policy text, an `IRT` description — states a lapse with
   absolute dates only: what was committed, where, and the date it passed.
3. **Check whether the commitment is still required at all.** If the clause never demanded it
   (shape A), the fix is to remove the commitment, not to re-date it.

**Fix:** amend the document to state the truth, and — where the commitment remains — re-date it
honestly *and* minute the lapse under 10.2. Re-dating alone overwrites the evidence of the
nonconformity instead of addressing it. Re-date only where the document must carry a date — an
objective's completion date (clause 6.2(k)) or a corrective action's committed date (clause 10.2).
Anywhere else the amended text states the commitment and points at its `IRT` ticket with no date:
the Skills Matrix drift came from a document carrying dates nothing obliged it to.

---

## 4 — Handoff format

When drift is found, produce this, then hand it to `/isms-draft` (see **What a control review does**
in `SKILL.md`). Don't edit the policy yourself; don't paraphrase the current text from memory —
quote it.

```
POLICY DRIFT — hand to /isms-draft

Policy ............... [name + path under security-documentation]
Clause / section ..... [where in the document]
Current text ......... "[quote verbatim]"

Contradicted by ...... [the evidence: risk id, control code, Drata field, Jira key,
                        live infrastructure observation — be specific]
Drift shape .......... [A: bar we don't meet | B: describes it differently
                        | C: criteria conflict — BLOCKS the decision
                        | D: commitment date has passed]

Date reconciliation .. [shape D only — every copy and its stated date:
                        controlled doc / wiki mirror / IRT `Date constraint:` line.
                        Jira duedate and Drata anticipatedCompletionDate are mandated
                        empty: list them as deliberate blanks (n/a where no risk
                        exists), never as a divergent date]

Proposed text ........ "[the corrected wording, written to be pasted - the requirement
                        and its basis in roles, criteria and systems of record, none
                        of the specifics above; durability check under it]"
Reasoning ............ [why this wording is accurate, and what in the clause's commit
                        history or the user's account supports or contests it]
Alternative .......... [for shape A: what meeting the existing bar would require instead,
                        so the user can choose rather than default to amending]

Queue page row ....... [claimed first: the three-cell row for the Pending changes table
                        on the queue page - # (the highest row number in the page file
                        plus one, read from disk just before the claim), the policy
                        name, and Detail - "pending" at the claim, then the link to the
                        comment below. Plus any Status note or At promotion step the
                        change needs. A pointer - never a description of the change,
                        and never anything in the ticket's description. See "Writing a
                        queue row" in SKILL.md]
Queue comment ........ [posted second: the detail comment on the policy queue ticket
                        (project = IRT AND labels = PolicyQueue) - Policy, Origin
                        (DCF - risk id - the IRT key where one exists, otherwise the
                        ICR review key), Draft edited, Clause, then the change in
                        full. Be expansive here; the comment is not size-rationed, and
                        the specifics from Contradicted by belong here, not in the
                        policy. See "Writing a queue row" in SKILL.md]
Also required ........ [the mirror page that must follow, via /bitpool-docs - it links
                        to and summarises the controlled document, never restates it;
                        any management review minute needed to close out a lapse]
Ordering ............. [document first, then mirror, then any ticket change —
                        never close a ticket ahead of the document]

Blocks this run? ..... [yes for shape C, otherwise no]
```

**`Proposed text` is policy text, and the evidence above it stays out of it.** `Contradicted by`
should be specific: the account names, observed configuration, counts and dates are what *prove* the
current text wrong. They stay in the handoff and in the queue comment, which is the dated record of
the change and becomes its rationale at promotion. The proposed wording follows the ISMS Policy
profile: it states the requirement and its basis in categories — roles, criteria, systems of
record. It carries a commitment date only where clause 6.2(k) or 10.2 requires the document to carry
one (shape D's re-date).

**Every handoff naming a controlled document must also name its mirrors.** A wiki page that says
"this table mirrors X" will silently re-diverge the moment X changes, and the next run will read the
mirror and reach a different conclusion. Route the mirror via `/bitpool-docs` in the same breath.

**A mirror summarises and links; it never restates.** Mirror pages of ISMS documents sit in
`security-documentation`, under the Security Documentation profile. The mirror says what the controlled document covers and
links to it. It does not copy the document's tables, dates or values — content the page is itself
the home of, such as a link to a credential record, is not a copy. A copied value is a second truth:
`DCF-179`'s commitment came to carry three dates because its mirror held its own copy and was
re-dated without the document changing (`hygiene-sweep.md`, worked examples). Where a mirror already
restates the document, propose cutting the copy to a summary and link, not re-syncing its values.

---

## 5 — Restraint

- **Don't manufacture findings.** If the policy is accurate, say so in one line and move on. A skill
  that reports drift every run trains people to ignore it.
- **One policy at a time.** Only raise drift the current control's decision actually evidences.
  Wholesale policy review is a deliberate, separate exercise.
- **Quote, never paraphrase.** A proposed change against a remembered version of the text is worse
  than no proposal.
- **Establish the reason before calling something wrong.** Clauses that look like mistakes are
  often deliberate, with the reasoning recorded in a meeting note this skill cannot read. Use the
  two sources you do have — the clause's commit history in `security-documentation`, and the user
  — and if you can't establish it either way, say so rather than proposing the strip.
- **Never claim a policy was updated.** This skill hands over; `/isms-draft` applies.
- **Never raise a promotion ticket, and never flag a lapsed `renewalDate`.** Promotion is a single
  bulk event tracked by the policy queue ticket, and renewal lapse between bulk events is the
  expected state, not a finding. Claim a row on the queue page and post its detail comment instead —
  **never anything row-related in the ticket's description**. See **Batched policy changes** in
  `SKILL.md`.
