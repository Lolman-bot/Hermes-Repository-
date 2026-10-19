# Staging note format

One file per vendor, named for the vendor in lower case — `gitbook.md`, `microsoft.md` — in:

```
%USERPROFILE%\Bitpool Pty Ltd\GRC - Bitpool - Documents\General\Drata\Vendors\<Vendor>\<YYYY MM>\
```

Cycle-level artefacts go in `…\Vendors\Reviews\<YYYY MM>\` instead. See SKILL.md rule 1 for why this
is the GRC document library and not personal OneDrive. Resolve `%USERPROFILE%` to an absolute path
first — the file tools and the other shells do not expand it (SKILL.md rule 1).

That library is an **Obsidian vault**, so frontmatter renders as properties and the file is
navigable, searchable and linkable. Write plain Markdown tables; do not use HTML.

**Why a file rather than the chat:** a vendor record is twenty-odd fields, several of them
judgement. Reviewing that in a scrolling transcript means the reader cannot save it, annotate it, or
return to it. See SKILL.md rule 1 for the decision and the feedback behind it.

---

## Frontmatter

```yaml
---
vendor: GitBook
drata_id: null          # null for a create; the numeric id for an update
action: create          # create | update | archive
status: staged          # staged -> approved (the risk owner changes this)
staged_by: Hermes
staged_on: 2026-09-03
approved_on:            # the risk owner fills this
tags:
  - vendor-staging
  - drata
---
```

`status` is the gate. **Write nothing to Drata until it reads `approved`.** `drata_id` is `null` on
a create and gets filled in from the API response.

---

## Sections, in order

### Header and context

Vendor name as `# <Name> — staged for Drata`, then a callout explaining how to use the file (the
override column, and the `status` change). Then three short facts: **what it is**, **why it is being
added or changed**, and **how its absence or defect was verified** — with the date.

The verification line matters. *"Verified absent 2026-09-03: no GitBook record in `SECURITY` or
`INFORMATION_TECHNOLOGY`, current or archived"* is a dated observation someone can re-run. "Not in
the register" is not.

### 1. Core record

The fields going in the main `Drata_createVendor` or `Drata_updateVendor` call.

| Field | Proposed | Your value | Basis |
|---|---|---|---|

- **On an update, show the current value too** — add a `Current` column before `Proposed`. A reader
  cannot judge a change without seeing what it is changing from.
- `Basis` is one clause, not a paragraph. Why this value, not why the field exists. **The
  verification date and the citation (the URL and the date read) live here, never inside the
  proposed value** — a field reading *"verified `<date>` from …"* has copied the staging note into
  the register. `location` alone names the contract document it rests on inside the value, per
  Security Drata §3.4 — *"`<region>`, as stated in the vendor's Data Processing Addendum"* — but
  never a date.
- Omit fields that are already correct. A table of thirty rows where four matter buries the four.

**Durability check — free-text values only.** `services_provided`, `data_stored` and `location` are
durable text in Drata, under the Security Drata profile of `/bitpool-writing-standard`. Directly
under the table, show **one** check covering whichever of them this note proposes, in the format of
that skill's `references/durability-check.md` §1:

**Durability check**

| Field | Span | Why flagged | Disposition |
|---|---|---|---|

**Removed before staging** — `<span>` → `<new wording, or where it went>`

Enums, booleans, dates, `owner` and the URL fields are structured values or pointers and are not
checked. Where none of the three is proposed, leave the check out; where one is proposed and nothing
was flagged, the one-line form given in `durability-check.md` §1 replaces the table.

### 2. Scores — always its own section

`impact_level` and `risk` never appear in the core table. They get their own section with a fuller
`Reasoning` column, because they are judgement and because `risk` decides the review obligation.

| Field | Proposed | Your value | Reasoning |
|---|---|---|---|

**State the consequence of the score explicitly** — *"residual `MODERATE` means an annual review; at
`LOW` it gets none"*. The reader is choosing a review obligation, not filling in a dropdown.

Say what the score is **deliberately not**, and why. *"Not `CRITICAL` — no production data, no
source code, no credentials, and its failure would not halt the service"* is the sentence that makes
a score defensible at audit.

### 3. Custom fields

Their own section, because they are judged separately — but they are sent **inline on the create**,
not as a second call. Drata rejects a create that omits its required custom fields.

| id | Field | Proposed | Your value |
|---|---|---|---|

Always address them **by id** — the id is what the write uses. Where a single-select option is
chosen, say which of the options it is and why, so a near-miss is visible: *"your CSV says 'enforced
and monitored', which is option 2, not option 1"*.

### 4. Needs your answer

**The section that makes the note honest.** Anything genuinely undecided, each with a fill-in blank,
and each explaining **what turns on the answer**.

Three kinds belong here, and nothing else:

- **A judgement that changes downstream obligations.** `has_pii` decides which contract clause set
  governs the vendor — so it is not a guess to be made and corrected later.
- **A date.** Never invented, never moved forward past its due date. Propose with reasoning; the
  risk owner chooses.
- **A value where a wrong answer is worse than an empty one.** URLs and `location` are the standard
  cases: `location` feeds data-residency answers in customer questionnaires, so a guess propagates
  into customer-facing statements. **Say that you will write `null` rather than guess**, and mean
  it.

If this section is empty on a first draft of a vendor you have not seen before, you almost certainly
did not look hard enough.

### 5. What stays yours

The things the connection cannot do, stated plainly so the reader is not waiting for them:

- **The security review itself.** Setting `renewal_schedule_type` makes Drata track the vendor as
  due; it does not create a review. There is no create-security-review verb.
- **Any document** — SOC 2, ISO certificate, completed questionnaire. No create-vendor-document verb.
- **The pre-execution agreement review** the policy requires. Note where it is retrospective because
  the vendor already has access.

Never phrase these as "you should" tasks. They are capability boundaries, and the reader needs to
know the boundary, not be assigned homework.

### 6. Result — filled in after the write

Left empty at staging, completed after. It is the audit trail of the write, so it records what the
API **returned**, not what was sent:

| | |
|---|---|
| `create:vendor` scope | untested / granted / 403 |
| `custom_fields` write shape | untested / `{"id": n, "value": v}` / … |
| Assigned `drata_id` | — |
| Fields that did not land | — |

**"Fields that did not land" is not optional.** Drata silently drops values rather than rejecting
them — a non-admin `owner`, a custom field in the wrong shape, a treatment field without its plan.
A response that looks successful is not evidence the write landed, so read the vendor back and diff
it against the approved note.

### 7. Drata security review — paste-ready

**Required on every add, and on any update that changes a score.** The security review is the
instrument that moves inherent risk to residual (see the rubric), so a score proposed without the
review text that justifies it is a number with no evidence behind it.

This skill **cannot create a security review** — there is no verb. So the note carries the text and
the user pastes it. Four subsections, matching what Drata's review form takes.

The review is Drata vendor text, but a **dated snapshot** under the Security Drata profile: Drata
stamps each entry, so specifics that were true at the review belong here and take no durability
check. The one part the next review reads as a standard to meet, rather than a record of the day, is
the conditions — 7.3 says how to write them.

**7.1 Observations.** Discrete, numbered, each in a blockquote so it can be copied cleanly. Each one
is a **separate entry** in Drata and gets its own author/date stamp when pasted.

> **Never write attribution lines.** Drata stamps author and date on entry. Writing
> *"Author: Eric Sharp · Date: 16 Aug 2024, 11:07 am"* into a draft fabricates an authorship record
> in a compliance artefact — say plainly that Drata stamps it and leave it out.

Each observation should be a **standalone factual assertion** that survives being read without the
others. Append `Context: <url>` where a claim rests on a published source, as the existing AWS
review does. Cover, where they apply: what the vendor does for Bitpool; its certifications, cited by
where they are published (`Context: <trust_center_url>`) — the report period, auditor and expiry as
examined go in 7.4; every control limitation found, stated precisely; the legal entity and governing
law; anything that could not be established; and whether personal information is involved.

**7.2 Internal notes.** The scoring reasoning — why that inherent level and not the one above,
and what the residual score depends on. Optional in Drata, but this is the right home for the
"deliberately not `CRITICAL`, because…" sentence.

**7.3 Decision.** One of `APPROVED` · `APPROVED_WITH_CONDITIONS` · `REJECTED`, then the conditions
as a blockquoted note. **Each condition must be something Bitpool can actually do and check** — an
aspiration is not a compensating control.

**State each condition as a testable criterion in role or category terms** — *"administrative
access is limited to the vendor's administrator role and re-verified at each security review"*,
not *"three admins: `<names>`"*. The next review re-tests it (rubric criterion 3) and the residual
score rests on it, so it must still be checkable after the people, counts and settings have moved.
What was observed at this review goes in 7.1 or 7.4, where the date is the point.

**7.4 Review scope.** What was examined, as at what date, and — the part that matters — **what was
not**. A scope statement that lists only what was covered reads as a claim of completeness. Name the
gaps: no completed questionnaire, DPA not reviewed, tenant configuration not verified from inside.
Record each certification as examined here too — its report period, auditor and expiry — since 7.1
cites it only by where it is published.

> **The dependency to state explicitly in section 2 whenever conditions carry the score.** Where
> residual risk sits below where the raw limitation would put it, it sits there **because of** the
> compensating controls — and those controls only exist as justification once they are recorded in
> the decision. Say so in the scores section: *"score `MODERATE` with no conditions recorded and the
> number is unsupported; with them entered it is evidenced."* Worked example, 2026-09-03: GitBook's
> residual was proposed at `HIGH` on an unmitigable vendor limitation, overridden to `MODERATE` by
> the risk owner, and that override is defensible precisely because the conditions in 7.3 name the
> compensating controls.

### 8. ISMS Exemption Application — field values

**Only where the vendor needs an exemption from an ISMS requirement** — a vendor whose product
cannot support a control Bitpool mandates. See SKILL.md rule 12 for the route and the form's limits.

**Check first whether the requirement is one this skill owns.** Some obligations that look
vendor-shaped are carried in another register — MFA scope is the standing example (see the scope
boundary at the top of SKILL.md). An exemption from a requirement recorded elsewhere is that
register's business, not a section in a vendor staging note.

Two subsections: **the Jira fields with exact values**, and **the narrative content** under the
questions an exemption normally asks. Mark every value the risk owner must choose — the approver, the
expiry date, and any linked issue — rather than filling them in.

**The risk owner raises it. The agent never does.** Draft, hand over, stop.

### 9. Anything needing scoping, not doing

Optional. Where the run surfaces a question too big to answer in passing — a new document format, a
process change, a tooling gap — record the question and what would need deciding, and **do not start
building.** Give a recommendation on sequencing.

### 10. IRT hand-off — only where a first review is deferred

Optional. Where SKILL.md §1 step 9 defers the vendor's first security review, the IRT ticket that
carries the commitment is **handed to `/manage-drata-control`**, which owns IRT's forms, labels,
naming, the undated create, the Original Estimate and the cost of an undated ticket. It drafts the
`summary` and `description` under the Security Jira profile, shows their durability check in its
own approval block, and creates the ticket — as form 1 with the `RTP` label, against the register
risk that carries supplier security exposure (its `references/irt-tickets.md` §3, *Vendor first
reviews*). **This skill creates no IRT ticket and drafts no paste-ready ticket text**; this section
is the hand-off note, approved with the rest of the note.

| Hand-off fact | Value | Your value |
|---|---|---|
| The object | The vendor, by name, and its Drata vendor id | |
| Outcome needed | The vendor's first security review, performed against the review criteria in the Vendor Management Policy and recorded in Drata | |
| Closing step | On Done, the review is recorded in Drata and the vendor's `status` leaves `UNDER_REVIEW` | |
| Why deferred | | |
| Date constraint | Any date already committed elsewhere, with its source — or none known | |
| Creation-time context | What `/manage-drata-control` needs for its dated creation comment: the scores proposed in section 2, and why the review could not be done now | |

- **The ticket points at the Drata vendor record; it never copies it.** The vendor's scores,
  security owner and `status` are that record's fields — they go in the hand-off only as
  creation-time context for the dated comment, never as text for the ticket body.
- **After the write**, hand this section to `/manage-drata-control` and say in the report that the
  ticket is not yet raised. The note's `status` stays `written-pending-review` until the review
  itself is done.

---

## After the write

1. Fill in section 6 from the read-back.
2. Set `approved_on` in the frontmatter if the risk owner left it blank.
3. Change `status` to `written` — or `written-pending-review` where the security review is still
   outstanding (SKILL.md §1 step 7).
4. Where section 10 is filled, hand it to `/manage-drata-control` for the IRT ticket.
5. Append the outcome to the session's decision log — the staging note is the approval record, not
   the programme record.

**Keep the note.** It is the per-vendor evidence that a human approved each field, which is
precisely what the register review has to demonstrate.
