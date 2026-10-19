# Drata field map, the write model, and the approval block

Field names, enum values and behavioural limits — verified against the Bitpool account via the
Drata MCP. Where a fact is unverified it says so; don't upgrade a guess to a fact.

> **No static measurements in this file.** Counts, statuses, readiness and treatment splits change
> continuously and are always one MCP call away — fetch them live. This file records *structure*
> and *behaviour*, which are stable. If you find yourself about to write a number here, write the
> query that produces it instead.

> **What the staged text says is governed by `/bitpool-writing-standard` (section `bitpool-general`).**
> Every text field this file stages for Drata — a risk's `title`, `description` and
> `treatmentDetails`, and a requirement's SoA exclusion `rationale` — lands in a registered target,
> writing profile **Security Drata**. The `Rationale` column of `compliance/drata-controls-register.md`
> lands in the `security-documentation` repo, profile **Security Documentation**. Load the standard
> (its `SKILL.md`, then the named profile) before drafting any of them; if it is not installed, stop
> and ask once per chat as `SKILL.md` sets out. This file keeps the Drata field behaviour and the
> Bitpool-specific shape of `treatmentDetails`; the standard decides what the words may say, and
> where the two disagree the standard wins. Structured fields — `owners`, scores, `control_ids`,
> `treatmentPlan` — hold their values exactly and are never restated in prose.

---

## 1 — Where each ISO requirement actually lives in Drata

The answer to "can this all live in Drata?" is **yes for everything ISO requires**, with one
exception (review dates, §3).

| ISO requirement | Drata home |
|---|---|
| Risk identified and analysed (6.1.2) | Risk `title`, `description`, `impact`, `likelihood`, `score` |
| Treatment option selected (6.1.3a) | Risk `treatmentPlan` |
| Controls determined (6.1.3b) | Risk → `controls` link, plus the control records themselves |
| SoA justification for **exclusion** (6.1.3d) | **Requirement** `rationale` — manual UI edit, renders only on out-of-scope Annex A requirements. See §2 |
| SoA justification for **inclusion** (6.1.3d) | ❌ **no home in Drata** — `compliance/drata-controls-register.md`, `Rationale` column. See §2 |
| Treatment plan (6.1.3e) | Risk `treatmentDetails` + `owners`, plus the `IRT-n` ticket it points at — **not** `anticipatedCompletionDate`, which is blank by decision. Clause 6.1.3(e) wants the plan and its owner; the schedule lives on the IRT board. See §3 |
| Residual risk accepted by owner (6.1.3f) | Risk residual triplet (the current residual) + the acceptance record — a management review minute for anything material, otherwise the dated change-record comment (§4 block) — naming the person, the risk, the residual level accepted and the date. An acceptance still awaiting its minute is recorded in the control's `ICR` outcome comment until then, and does not hold that ticket (`treatment-decisions.md` §5). `owners` names only the *current* owner and is never evidence of a past acceptance |
| Implementation results retained (8.3) | Evidence library, `completionDate` |
| Next review date | ❌ **no field** — see §3 |

GitBook is **not** part of this trail. It earns a place only when the decision creates a procedure a
human must follow, because staff don't hold Drata licences. That's operational documentation, not a
second copy of the audit record.

---

## 2 — Control fields, and what MCP can and cannot write

### The write model lives in `/ask-drata`, not here

**What this skill may and may not call is defined in `/ask-drata`, rules 8–10.** Read it before
any Drata call. It is not restated here, deliberately: a permission rule copied into a workflow
skill drifts from the connection it describes, which is exactly how this file ended up with four
contradictory copies on 2026-08-21.

The short version, for orientation only — **`/ask-drata` wins if these disagree**: risks may be
created and updated; a control may have a policy or owner attached, **and its text may be
corrected** — a rare, explicitly approved exception gated by the golden rule in `SKILL.md`, never a
routine edit; control *creation* is outside this skill's write model (`/ask-drata` records
`Drata_createControl` as exposed but unprobed); this skill **cannot** write evidence —
`update:evidence` is not granted on this connection (`403` probe, re-confirmed 2026-08-28); see the
**"Granted scope matrix"** section of `/ask-drata`'s `references/drata-mcp-gotchas.md`. Every write
goes behind an approved block (§4).

The per-verb traps — the 768-character `description` cap, the absent `riskId` parameter, numeric
`control_ids`, silently dropped non-admin owners, dates that cannot be cleared, relation fields
that replace rather than append — are all in `/ask-drata` rule 9. §7 below covers only what is
specific to *authoring a risk entry*, not how the API behaves.

`Drata_searchControls` returns: `id`, `code`, `name`, `description`, `activity`, `rationale`,
`question`, `slug`, `controlTemplateId`, `customFields`, `frameworkTags`, `topics`, `owners`, and a
`flags` object.

`flags` is the fastest gap signal — no extra calls needed:

| flag | `false` means |
|---|---|
| `isReady` | **something configured on the control is failing — NOT "work outstanding"**. See the readiness rule below |
| `hasTicket` | ⛔ **do not use.** Provenance, not coverage — see the warning below |
| `hasEvidence` | manually attached external evidence absent — **but the evidence list is not authoritative either.** `/ask-drata` rule 10 |
| `hasPolicy` | no policy linked (informational) |
| `hasOwner` | assign an owner |
| `isMonitored` | manual control, no automated test |

**⛔ Readiness is failure-driven, not completeness-driven — established 2026-08-28.** Drata marks
a control ready **unless something attached to it is failing**. A control needs **no** evidence,
**no** policy, **no** owner, **no** linked risk and **no** monitoring test to be ready. A list-mode
sweep on that date found ready controls with no evidence, ready controls with no policy, many
controls carrying no risk at all, and one control ready holding nothing but a policy — no evidence,
no owner, no risk, not monitored. For current figures, read `pagination.totalCount` live with the
`is_ready` / `has_evidence` / `has_policy` filters. Attaching any of those creates a way to fail;
attaching none leaves the control green by default.

So `isReady: false` means one of three things, and you must establish which before reporting
anything: an **approval requirement** configured and not granted; a **monitoring test** attached and
failing; **evidence** attached and expired. It does **not** mean the control has a gap. Bitpool
decided on 2026-08-24 not to use control approvals, but approvals remain configured on many controls
from earlier setup — **that is the most common cause of a not-ready control here**, and it says
nothing about the control's substance. Removing one flips the control to ready with no other change,
verified on `DCF-777` on 2026-08-28 as a single-variable experiment.

**The corollary matters more than the rule. Evidence is not what makes a control ready — it is a
tripwire you arm.** An artefact with a renewal schedule is what makes the control fall *out* of
readiness when it lapses, which is how Drata monitors ongoing compliance rather than one-time
completion. Attach evidence for that reason, set the renewal interval to match whatever cadence the
control's own wording promises, and record the expectation on the IRT ticket. Never attach it to
turn a control green, and never withhold it because the control is green already.

**Three states, one control — do not collapse them.** *Audit ready* is carried by the `ICR` ticket
and set by this skill at Step 10: the position is recorded truthfully in every auditor-facing home
and every remaining gap is carried by an open `IRT` ticket (`icr-closure.md`). A not-ready flag
holds that ticket or not according to its cause — an approval still configured holds it, and so do a
test failing because of how it is set up in Drata and a failing test nothing carries; evidence an
open `IRT` ticket will produce does not, and nor does a failing test whose control or custom-test
logic an open `IRT` ticket will fix (`icr-closure.md` §4). *Implemented* is the Statement of Applicability column and changes
only through the policy queue; the controls register's `Rationale` row states it too — the register
has no other home for it — and the plan's closing step flips it when the work completes
(`treatment-decisions.md` §5). *Ready* is Drata's `flags.isReady`, is **computed and not settable** —
`Drata_updateControl` has no `is_ready` parameter — and attests only that nothing configured is
failing. These diverge in both directions and neither divergence is a defect: a control can be
Drata-ready while `Implemented: N`, audit ready while `isReady: false` where every cause is
evidence an open `IRT` ticket will produce or a failing test whose control or custom-test logic one
will fix, and `isReady: true` while
not audit ready. Say which you mean, every time, and where a run leaves a control ready but not implemented, state why in the register entry —
an auditor will ask.

**⛔ Evidence cannot be resolved from either signal alone — corrected 2026-08-28.** The rule here
previously read *"never conclude a control has evidence from the flag — resolve it with
`Drata_listEvidence`"*. The second half is wrong. `Drata_listEvidence` covers **Evidence Library
buckets only**, and Drata's **external evidence** — artefacts attached directly to a control in the
UI — is unreachable through this connection entirely. **An empty list means "no bucket", never "no
evidence."** Where the flag reads `true` and the list is empty, the honest output is *"external
evidence indicated, not readable via API — verify in the Drata UI"*, and it must never become a
"no evidence" finding. Confirmed the hard way on 2026-08-28: a false "no evidence" statement was
written into `CR-09` on the strength of an empty list, and the control owner then confirmed the
artefact existed all along. When checking currency, read `versions[].createdAt`, never the bucket's
`updatedAt`. See `/ask-drata` rule 10.

**⛔ `hasTicket` and `ticket_status` are both untrustworthy — never use either as a gap signal.**
`/ask-drata` rule 10 owns this fact. Verified 2026-08-21, two independent failures:

1. `DCF-179` reads `hasTicket: false` while `CSIP-521` exists, is titled
   `Drata | Bitpool | DCF-179 | Evidence competence records`, and is `Done`. The flag tracks
   **Drata-integration provenance**, not whether a ticket exists — and most CSIP issues were not
   integration-created when this was checked, so it is blind to most of them.
2. Filtering `ticket_status="IN_PROGRESS"` returns a set in which **every single control carries
   `hasTicket: false`**, while controls that *do* report `hasTicket: true` are absent from the
   result. The filter and the flag contradict each other; at least one is wrong.

Resolve ticket existence by Jira query on the control code (`text ~ "DCF-xxx"`, across `CSIP`, `ICR`
and `IRT`) and ignore both Drata signals entirely.

**⛔ `rationale` — resolved 2026-08-21. It is not what it looks like.**

A `rationale` field appears on **both** the control object and the framework-requirement object.
They behave completely differently, and the useful one is not on the control:

| | Control `rationale` | Requirement `rationale` |
|---|---|---|
| Populated at Bitpool? | **Never.** `null` on every control, enabled *and* disabled, when checked | Only on out-of-scope requirements |
| Semantics | Appears unused; no UI surface found | **The SoA exclusion justification** |
| Renders in the Drata UI | Not found on the control page | Only where an Annex A requirement is marked out of scope |
| Writable via MCP | No — `Drata_updateControl` omits it | No — there is no `Drata_updateRequirement` tool at all |

Whether any requirement is currently marked out of scope is a live question — list the
requirements rather than assuming. The exclusions this file once quoted (`A.7.11`, `A.7.8`) were
restored to scope on 2026-09-24 and their justifications cleared, as the controls register records.
Both had named cloud providers instead of stating a basis in ISMS-scope and risk-assessment terms,
and `A.7.8`'s is the SoA calibration pair in the Security Drata profile §4.

**Consequences for this skill:**

1. **Never stage text for a control's `rationale` field.** It has no UI home and no writer. Earlier
   versions of this file told you to stage SoA justification there; that was wrong.
2. **Exclusion justification** goes in Drata, on the *requirement*, by hand — and only when marking
   an Annex A control out of scope. Word it per the Security Drata profile §3.5.
3. **Inclusion justification and decision rationale have no home in Drata at all.** Every in-scope
   requirement has `rationale: null`. Bitpool's home for these is the **`Rationale` column of
   `compliance/drata-controls-register.md`** in `security-documentation` — hand-maintained, and the
   source the wiki page mirrors. Stage rationale text for *that* column, not for Drata, and edit the
   repo copy rather than the mirror. Its wording follows the **Security Documentation** profile
   (`security-documentation/_meta/writing-standard.md`); if that file is missing, the standard's
   gate treats the repo as out of scope until it is restored — say so once.
4. Worth knowing: ISO 27001 **6.1.3(d)** requires the SoA to justify **inclusions** as well as
   exclusions. Bitpool's inclusions were previously only inferable from risk→control links; that
   register column is now the written record.

**`customFields` — the feature is on; sampled controls have no field defined.** Sampled controls
return `customFields: []`. That reflects the definitions, not the account: Bitpool has the "Custom
Fields & Formulas" feature, and a field can be defined on controls in the Drata UI. The MCP
populates an existing field by id; it cannot define one. Detail: `/ask-drata`, *Custom fields and
formulas* in `references/drata-mcp-gotchas.md`.

Enabled controls carry `frameworkTags: ["ISO270012022"]`. For counts, read
`pagination.totalCount` live from list mode with the relevant filter (`is_ready=False`,
`has_evidence=False`, `is_monitored=False`) — never quote a remembered figure.

Governance controls worth knowing by code: `DCF-162` Statement of Applicability · `DCF-164`
Management System Management Review · `DCF-179` Competence Records (clause 7.2 — mandatory) ·
`DCF-566` Management of Nonconformities · `DCF-171` Documented Operating Procedures (reviewed at
least annually).

---

## 3 — Risk fields, and the review-date gap

`Drata_searchRisks` returns: `id`, `riskRegisterId`, `riskId`, `title`, `description`,
`treatmentPlan`, `treatmentDetails`, `anticipatedCompletionDate`, `completionDate`, `impact`,
`likelihood`, `score`, `residualImpact`, `residualLikelihood`, `residualScore`, `status`,
`identifiedAt`, `createdAt`, `updatedAt`. Expandable: `owners`, `reviewers`, `controls`,
`categories`, `documents`, `notes`, `tickets`, `tasks`, `customFields`.

- Register: id `1`, name `Risk Management`.
- `treatmentPlan` enum: `UNTREATED` · `ACCEPT` · `TRANSFER` · `AVOID` · `MITIGATE`.
- Scoring: `impact` 1–5 × `likelihood` 1–5 = `score` 1–25. Same for the residual triplet.
- Observed `riskId` prefixes: `SD-`, `CR-`, `AI-`, `IN-`. Reuse the domain's existing prefix.
- For the current treatment split, call
  `Drata_searchRisks(facets=["treatmentPlan","status"], size=1)` — don't carry a remembered one.

### Dates: Drata records them, it does not chase them — SETTLED

Confirmed with Drata support (Dratanaut, technical support, 2026-08-18):

> "there isn't a built-in trigger for the Anticipated Completion Date. […] date-based triggers
> (like 'Anticipated Completion Date passed without Completed Date filled') are not available. So
> the Anticipated Completion Date and Completed Date fields are mainly for record keeping and
> tracking on the risk itself, rather than automated alerts."

Drata workflows trigger on **risk score changes, treatment option changes, evidence updates and
personnel compliance status** — never on dates. There is also no field named "next review date";
the date fields are `identifiedAt`, `anticipatedCompletionDate` and `completionDate`.

**Consequence: a treatment plan whose target date passes sits silently overdue in Drata forever.**

So every commitment gets a ticket in the **`IRT` — ISO27001 Plans** project, which is the only place
a date for it can ever live. **Two corrections to the old form of this sentence**, both 2026-09-15:
it said a ticket required a *parent of record* for its date, which is no longer a precondition for
creating one; and it said Jira's `duedate` "supplies the alerting", which was never true — nothing at
Bitpool alerts on a Jira due date without an Automation rule, and none exists.

**And the ticket is created undated.** While the `ICR` control review programme runs, every new IRT
ticket carries an empty `duedate` and a mandatory Original Estimate in hours; all dates are set
together in one prioritisation pass across the whole board. See `irt-tickets.md` §1.

Bitpool also has a separate control requiring annual risk review — resolve it live and reference it
on review tickets.

This is settled. **Do not re-open it, and never propose relying on Drata to flag a slipped date.**

---

## 4 — The risk approval block (Step 9)

**Never create or amend a Drata risk without showing this block first and getting an explicit yes.**
See the golden rule in `SKILL.md`. Render it complete — every field, with the real values, not
placeholders and not a summary. The reason is not ceremony: you cannot tell from Drata whether a
compensating control actually operates, and the user can tell you in one line.

**Render it as markdown in the chat — not inside a fenced code block.** The fence below delimits
the template *within this file*; it is not how the block should look when you show it. A fenced
wall of monospace is exactly where an untrue claim survives unread. Use a table for the fields,
headed lists for `treatmentDetails`, and a table for the durability check directly under the staged
text, so the user can scan it line by line. The truth questions (the Unverified list) and the
durability check are different: the first asks whether each claim is true today, the second shows
which spans could stop being true and what was removed.

```
DRATA RISK — [CREATE NEW | AMEND <riskId>]
Register: Risk Management (id 1)

riskId ................ [CREATE: assigned by Drata, you cannot supply one — see §7.
                         AMEND: the existing id.]
title ................. [short risk name, in risk language]
description ........... [the risk as a consequence to information — NOT a missing control.
                         Affected systems as a population, never listed by account, host
                         or product (Security Drata profile §3.2).
                         HARD LIMIT 768 characters. Count it; the API rejects at 769.]

treatmentPlan ......... [MITIGATE | ACCEPT | AVOID | TRANSFER]
treatmentDetails ...... [the required shape and the seven content rules below, worded
                         per the Security Drata profile §3.2 — no scores, owner,
                         linked-control names, cadences or history; no date beyond an
                         anchored fact the entry's claim rests on; the IRT key with its
                         recovery query]

impact ................ [1-5]
likelihood ............ [1-5]
residualImpact ........ [1-5 — equal to inherent when treatmentPlan is ACCEPT]
residualLikelihood .... [1-5 — equal to inherent when treatmentPlan is ACCEPT]

owners ................ [the default risk owner (§7) unless the user names someone else
                         for this risk. A structured value — never repeated in prose]
reviewers ............. [EMPTY — Bitpool sets no reviewers, decision 2026-08-24.
                         Omit the field; do not pass an empty list unless clearing one]
control_ids ........... [NUMERIC control ids, not DCF codes — see §7. List the DCF code
                         beside each so the user can check them.]
anticipatedCompletionDate [LEAVE BLANK — it triggers nothing, and IRT is the single home
                         for this commitment's date whether or not one has been set yet;
                         see irt-tickets.md §1. An empty IRT duedate is NOT a licence to
                         populate this field instead]

--- Outside Drata ---
Rationale ............ [text for the `Rationale` column of
                        compliance/drata-controls-register.md, keyed by DCF-xxx.
                        Opens with the applicability and implementation state,
                        as the SoA position row in treatment-decisions.md §3
                        sets it — e.g. "Applicable; not yet implemented — plan
                        referenced" (templates: treatment-decisions.md §5).
                        Security Documentation profile §3.3
                        (security-documentation/_meta/writing-standard.md).
                        NOT Drata — the control's rationale field is a dead end (§2).
                        Route via /bitpool-docs.]
Requirement rationale  [ONLY if marking an Annex A requirement out of scope: manual
                        Drata UI edit on the REQUIREMENT, not the control. Worded per
                        the Security Drata profile §3.5.]
Change record ........ [AMEND, or a CREATE whose treatmentDetails anchors an approval
                        or acceptance to it: the dated comment saying what changed,
                        why and on whose decision — naming who approved, the risk,
                        the residual level accepted and the date — posted in the
                        same change. It goes on the risk's IRT ticket where one
                        exists, otherwise on this run's ICR ticket; where this skill
                        can write neither, stage it for the user to post and say so
                        here. Correction and history text goes here, never in
                        treatmentDetails — Drata keeps no readable history of a risk.
                        A snapshot, so specifics are correct here.]
Jira ................. [IRT parent + subtasks — see irt-tickets.md §6. No review
                        tickets; recurrence goes to CYB. Their text follows the
                        Security Jira profile and is checked when it is staged.]
GitBook .............. [only if a human-facing procedure is needed — route via /bitpool-docs,
                        which applies the destination repo's own profile where it has one]

--- Durability check — one table, directly under the staged text ---
[Per /bitpool-writing-standard references/durability-check.md §1, over title,
 description, treatmentDetails and both rationale texts: flag every span against its
 §2 patterns, dispose of each (kept, generalised, moved or cut), then show the
 judgement calls left in the final wording as a markdown table with a Field column —
 and a Profile column whenever the register Rationale is in the same block, since the
 block then spans Security Drata and Security Documentation — one collapsed row for
 handles, and a one-line "Removed before staging" list. If nothing is flagged, one
 line says so. Structured fields and the change record are not checked.]

--- Unverified, needs the user to confirm or deny ---
[List every asserted control you could NOT verify from Drata, a live system, or Jira.
 If this list is empty on a first draft, you almost certainly did not check.]
```

### The required shape of `treatmentDetails`

Group every compensating measure under one of four headings, and **number every item** so each can
be referred to and challenged on its own. On the first write, number continuously down the
headings. After that, **numbers are assigned once**: a new item takes the next unused number
whatever heading it sits under, an item that moves between headings — `PLANNED` to operating when
it lands — keeps its number, and a removed item's number is retired, never reused. The entry closes
with the declaration line, which is what lets another record cite an item by number:

```
SEGREGATED TODAY - preventive          (1, 2, 3 … on the first write)
PLANNED - not yet operating,            (4, 5, 6 …)  each naming its IRT subtask
  tracked as subtasks of <IRT-n>
OPERATING TODAY - detective,            (7, 8, 9 …)
  where a preventive split is not proportionate
ACCEPTED EXPOSURE - not segregated,     (10, 11, 12 …)
  and not claimed to be

Item numbers are stable identifiers and are not renumbered on amendment.
```

The headings are the standard's relied-on / planned split — the *position*, not status (core rule 3
of `/bitpool-writing-standard`) — so their words (*today*, *planned*, *not yet operating*) take one
collapsed row in the durability check rather than a flag each.

**This structure surfaces false claims, which is why it exists.** A flat list of "compensating
controls" hides the difference between something that protects Bitpool today and something that is
a decision, an intention, or a sentence lifted from a policy. Forcing every item into one of the
four buckets makes the question *"does this actually happen?"* unavoidable for each one. Verified
2026-08-21: reorganising one flat list into these groups is what exposed that code review was
asserted as an operating preventive control when it is not performed at all.

> **The headings are for risks with a coverage story to disambiguate — not for every risk.**
> Corrected 2026-08-27. This section previously read "mandatory rather than stylistic", and that
> word is what produced the failure below: applied to a risk that is simply mitigated, the four
> buckets demand an inventory nobody needed and the entry bloats to fill them.
>
> Use the headings where the entry has to distinguish *what protects us now* from *what is
> scheduled* from *what we have consciously left uncovered* — a segregation-of-duties risk, a
> partial-scope acceptance, anything with a residual worth arguing about. Where a risk is
> straightforwardly treated and there is no such distinction to draw, **a short prose paragraph is
> the correct shape**, and forcing headings onto it is padding.
>
> The `ACCEPTED EXPOSURE` heading is the exception that stays near-obligatory: an exposure omitted
> is an exposure hidden, and that is the one thing this field must never do.
>
> **But state exposure as a boundary, not as an inventory — corrected 2026-08-27.** Define what is
> protected and let everything else fall outside it. Do **not** enumerate the things that are not
> covered. The wording rule is the Security Drata profile §3.2 (*Exposure is a boundary, not an
> inventory*) — the criterion that decides membership, with the policy or register that sets it; a
> list of members, in or out, is an inventory however it is phrased. What follows is the reasoning
> and the worked failures behind it.
>
> **This replaces an older allowance.** Content rule 5 used to exempt a scope statement listing the
> platforms subject to a control, on the grounds that the boundary was the decision. The boundary is
> the *criterion*; the list of platforms meeting it is an inventory, held in the record the
> criterion points at.
>
> An enumerated exclusion list is an open set: it is wrong the moment anything is deployed, and it
> is *already* wrong on the day it is written, because nobody lists every uncovered asset. Naming
> two of them and omitting thirty reads as an inventory of exposures, and an auditor reasonably
> infers the unlisted thirty are believed covered. A positive definition is a closed set — it stays
> true as the estate grows, and it needs no maintenance.
>
> | Write this | Not this |
> |---|---|
> | "Platforms that meet `<the policy>`'s criteria for penetration testing are tested; platforms outside them are not." — once the version in force is confirmed to set the criteria | "`estimating.bitpool.com` is not penetration tested." |
> | "Testing covers systems reachable by customers; internally-reachable systems rely on access control instead." | "`protect.bitpool.com`, `test-ftp…` and the raw EC2 hosts are out of scope." |
>
> **The exposure is still stated — it is the complement of the protected set**, and stated that way
> it is broader and more honest than any list. Follow it with *why* the boundary sits there, which
> is the part an auditor actually tests. Worked failure, 2026-08-27: a draft named
> `estimating.bitpool.com` as the accepted exposure on `SD-04`; the risk owner's response was
> *"there are other domains also like protect.bitpool.com. why not define what we DO protect and
> exclude others?"* — and a DNS enumeration of the estate that same day returned dozens more.
>
> Worked failure, 2026-08-27: `SD-04`'s draft ran to fifteen numbered items across four headings for
> a risk whose treatment is *"we penetration test the customer-facing platform annually"*. Nine of
> the fifteen restated controls already linked in `control_ids`. The risk owner's verdict was that
> the entry *"is almost saying 'hey, here is a list of shit not treated by this RTP'"* — which is
> exactly what an over-populated `OPERATING TODAY` list reads as, because every neighbouring control
> it names is one the reader then assumes this risk does *not* cover.

Numbering matters for the same reason. When you show the block, the user reviews it
*line by line* and replies "item 2 is untrue", "item 10 is pointless" — so **invite exactly
that**, and treat each item as a separate claim needing its own confirmation rather than asking
for one blanket yes. Also carry the numbering into the IRT subtasks and the evidence list, so a
reader can trace one measure from the register to its ticket to its artefact. Because those records
then refer to items by number, the entry declares its item numbers stable — the convention `CR-10`
states — and the assign-once rule above keeps that declaration true: renumbering an item breaks
every record that cites it, which is how an `IRT` ticket came to cite an item that had moved. The
declaration is what lets another record cite an item by number under the writing standard
(`irt-tickets.md` §4); an entry without it is cited by what the item is. `/manage-drata-risks`
follows the same rule when it rewrites an entry.

### The seven content rules for `treatmentDetails`

1. **Only assert what operates today.** Every enumerated control is a claim that Bitpool does this
   thing now. A policy saying so is not verification (see the golden rule). If it does not operate,
   it is not a compensating control — it is the gap.

2. **Mark planned controls as planned, and name what delivers them.** A control that *will* exist
   goes in a clearly separated `PLANNED` list with its IRT subtask, never mixed into the operating
   list in the present tense. A reader must be able to tell, without leaving the field, what protects
   Bitpool today versus what is scheduled. Word each planned item as the Security Drata profile §3.2
   sets: its outcome, the condition on which it will be relied on, and its IRT pointer — never its
   progress.

3. **No ritual controls.** A "control" performed by the conflicted party on their own work — the
   alert-raiser reviewing their own closure, the report author reviewing their own report — is not a
   control and an auditor will say so. It is worse than nothing, because it implies coverage that
   does not exist. State the exposure plainly and lean on the measures the conflicted party genuinely
   cannot alter: immutable logs, external audit, a second person who really is independent.

4. **Link other controls; don't narrate them, and don't invent new ones.** Where a measure maps to a
   DCF that already exists, **put it in `control_ids` and stop there.** The link *is* the reference,
   it is machine-readable, and it is what Drata renders on the risk. The wording rule — no linked
   control named in prose, a `DCF` code only for a control deliberately *not* linked because it owns
   part of the risk, and no evidence-bucket or monitoring-test name quoted — is the Security Drata
   profile §3.2.

   **Corrected 2026-08-27.** This rule used to say "add it to `control_ids` **and name it in one
   clause**". That clause is what generated the bloat: a risk with seven linked controls acquired
   seven prose sentences whose entire content was already in the links. Worse, it changes how the
   entry reads — a paragraph listing neighbouring DCF codes stops looking like a statement of
   position and starts looking like a disclaimer of what the risk does *not* treat.

   The one situation where prose names a control — **the risk, or part of it, is deferred to a
   control that is deliberately not linked here** — reads *"Code review — not performed; treated
   under DCF-5."* and stops.

   Two consequences worth stating separately, because both were got wrong on 2026-08-27:

   - **Never name a control to demonstrate thoroughness.** If linking it was right, the link says
     it. If linking it was wrong, prose does not fix that.
   - **Never describe a programme that is not yet running**, even by reference. A referenced control
     is still an assertion that something happens. Bitpool's vulnerability management programme was
     described as operating in a draft on 2026-08-27 when it is **not yet active** — the risk
     owner's response was that this is *"good reason to keep it the fuck out of a risk treatment
     plan that it is not related to"*. Rule 1 already forbids it; rule 4 is where it slips through,
     because a reference feels lighter than a claim. It is not.

   **When does a measure become its own control?** Drata permits control creation, but it is
   outside this skill's write model (§2), so it is a deliberate human action — treat that friction
   as a feature.
   Create one only when **all three** hold: (a) no existing DCF covers it; (b) it needs *recurring*
   evidence rather than a one-off statement; and (c) a named person will maintain it. Otherwise the
   measure belongs in a **policy** — it is a rule people follow — and is referenced from the risk.
   Where nothing fits, say so in one line rather than padding. An inflated control set is its own
   maintenance burden and dilutes the controls that matter.

5. **No point-in-time data — the writing standard governs it.** A register entry states Bitpool's
   *position and its reasoning*, not a measurement taken on the day it was written, and a decayed
   value in an auditor-facing field discredits every other claim in the entry. Counts, inventories,
   account and resource names, configuration values, products, status words, dated verifications
   and scope statements are all governed by `/bitpool-writing-standard` core rules 3 and 4 and the
   Security Drata profile §3.2 (*Anchored verifications*; *Exposure is a boundary, not an
   inventory*) and its calibration pairs. Load them; they are not restated here.

   **Two older rules in this skill are replaced by the standard's.** A dated verification is no
   longer kept by default: an entry keeps one anchored verification per relied-on compensating
   control — the latest — written as a past-tense event with its method and pointer, with no counts
   inside it and with what re-performs it; earlier ones go to the ICR comment. And a date-stamped
   count is not durable text, however it is sourced — the count goes to a snapshot.

   **Where the measurement belongs instead** — the homes this skill writes, so it is not lost:

   | Kind of fact | Its home |
   |---|---|
   | What was found on a given date | The `ICR` review comment for that control |
   | The current inventory, count or coverage | The register or evidence artefact itself |
   | Progress against a commitment | The `IRT` ticket |
   | The magnitude of the risk | The impact and likelihood fields, not the prose |
   | Correction history, a score change, superseded wording | The dated change-record comment — on the risk's `IRT` ticket, otherwise this run's `ICR` ticket (§4 block) |

   **The skill's own environment briefing is held to the same discipline** — not because the
   standard governs skill text (it governs registered targets), but because a count in a skill is
   copied into every record the skill writes. It decays exactly as a count in a risk entry does, and
   is harder to catch because nobody reviews a skill on a cycle — there is no signal in the text
   saying "this was true in 2024", so it gets trusted. Where a skill must describe the size or shape
   of the estate, describe the *kind* of thing and name the command that enumerates it. Never write
   the number.
   Worked failure, 2026-08-28: `SKILL.md`'s environment table said the estate was "across five
   accounts" while the same file, 35 lines earlier, forbade hardcoded counts. Fixed by removing the
   count and pointing at `/aws-query`, not by correcting five to seven — correcting the digit only
   resets the clock.

6. **Never copy a number a policy owns — cite the policy.** Rule 5 covers values that *move on
   their own*; this one covers values that move **when someone edits a controlled document** — a
   different failure and a worse one, because the register then contradicts the controlled document
   it cites, and it is the register that loses: the policy is the approved artefact. How to cite a
   policy-owned parameter, and what to write when the version in force does not hold it yet or holds
   it only in a draft awaiting promotion, is `/bitpool-writing-standard` core rule 1 and the Security
   Drata profile §3.2. Rejected by the risk owner, 2026-08-27, in exactly these terms: *"stop
   committing to specifics in the risk treatment plan like Critical 24 hours, High 3 days, Medium 7
   days, Low 1 month. THIS WILL CAUSE SO MUCH DRIFT."*

7. **Length is a control, not a style preference.** `treatmentDetails` states a position; it is not
   an inventory of the control environment. Every sentence that does not change what a reader
   concludes about *this* risk makes the entry harder to audit and gives an auditor another claim to
   test — so the marginal sentence has negative value, not neutral value.

   Apply this test to each item before it goes in: **does this measure treat the risk statement in
   the `description` field?** Not "is it true", not "is it good practice", not "is it nearby" — does
   it treat *this* risk. If the honest answer is that it treats a neighbouring risk, it belongs on
   that risk, and its control belongs in this one's `control_ids` if the mapping is real.

   A useful proxy: **a well-formed entry for a straightforwardly mitigated risk is a paragraph, not
   a page.** Where an entry is running long, the cause is almost always rules 4, 5 or 6 being
   violated somewhere in it — go and find which, rather than trimming adjectives. Length is the
   warning, not the cut: remove the logs, history and restated records that cause it, never an item
   that does treat this risk (Security Drata profile §3.2).

---

## 5 — In-house precedent to copy (and to avoid)

**Copy these.**

- **`CR-01` — "Allowing personal applications on work devices"** — copy its **structure only**: it
  gives the business reason for the position, enumerates its mitigations individually, and carries a
  residual materially lower than inherent. **Do not copy its item wording.** Its controls were
  unlinked when it was first cited here (2026-08-21) and have since been linked, but as observed on
  2026-09-24 its items still name those linked controls in prose, quote Drata evidence-bucket names
  and describe a product rollout by its progress — each of which the Security Drata profile §3.2
  cuts. If you amend it, fix those rather than extend them.
- **`SD-04` — "Software Development Standards - Product Errors"** — the many-to-many example: one
  risk linked to a whole family of controls, including `DCF-19`. Shows why one-risk-per-control is
  the wrong shape.
- **`IN-37` — "Backup Facility"** — good `ACCEPT` narrative: explicit risk-appetite language
  ("single vendor backups and single region backups fit with Bitpool's risk appetite") rather than
  a bare assertion.
- **`CR-02` — "No staff or visitor badges"** — good compensating-factor narrative: it states the
  criterion the decision rests on — people present are identifiable on sight — and the change that
  would re-open it (headcount, visitor frequency or the office footprint changing materially), with
  no count. That trigger is what to copy; a review cadence is not — the cadence belongs to the
  periodic risk review control. Its items that name linked controls and quote evidence-bucket names
  are not a model either.

Read each of these live before citing them — they may have been amended since.

**Don't copy these.**

- **The `AI-*` series** (`AI-04`…`AI-14`) — accepted with **no linked controls**, **null residuals**,
  and typo-heavy prose. Four of them also rest on the same load-bearing claim ("Bitpool does not
  store personal data"), so one change to that fact invalidates several acceptances at once. If you
  touch any of them, fix the structure, don't extend the pattern.
- **`SD-04`'s pen-test wording** — `treatmentDetails` claimed *"Bitpool conducts annual penetration
  testing"* broadly, which is wider than the real scope. A register that overstates reality is a
  finding regardless of how defensible the underlying decision is.

  **Corrected 2026-08-27, and the correction matters more than the original note.** Earlier editions
  of this bullet described the real scope as *"authenticated on app.bitpool.com, unauthenticated on
  partner-restricted apps"*. That was wrong on the second half. Bitpool's decision, taken by the risk
  owner: the **customer-facing platform and its API are penetration tested annually, and
  private or semi-private platforms are not tested at all** — their exposure does not justify the
  cost, and access control under DevOps practice is the primary safeguard instead. Do not reinstate
  the partner-app clause; the untested authenticated partner surface is carried as accepted exposure
  on `SD-04`, not as a tested scope. When writing the decision into the entry, state the boundary
  by the criterion the Vulnerability Management Policy sets and the testing frequency by citing that
  policy — once the version in force is confirmed to hold both — never *"annually"* or the platform
  names (Security Drata profile §3.2).

---

## 6 — MCP call notes

- **Structured mode over search mode.** `Drata_searchRisks` / `Drata_searchControls` with `query` set
  is unreliable on this account (see `/ask-drata`). Use filters instead: `controls=[...]`,
  `treatment_plan=[...]`, `is_ready=`, `has_evidence=`, `is_monitored=`.
- **`facets` gives cheap counts.** `Drata_searchRisks(facets=["treatmentPlan","status"], size=1)`
  returns the whole split without fetching rows.
- **`pagination.totalCount` on page 1 is authoritative** for counts. For row-level completeness,
  follow `cursor` to `null` before concluding anything is absent.
- **Find the risk for a control:** `Drata_searchRisks(controls=["DCF-xxx"], expand=["controls","owners"])`.
  An empty result means the control has no risk linked — a traceability gap, not proof there's no risk.
- **The Risk Assessment Policy** resolves via `Drata_listPolicies(name="risk")`. Read its
  **content** before scoring — the scales and the acceptable level of risk. **Ignore `renewalDate`
  and `approvedAt` entirely.** Bitpool renews the policy set in one bulk event after the control
  review programme resolves, so a past renewal date and a null approval are the expected state
  between those events, not a finding. Never report them. See the golden rule on renewal lapse and
  **Batched policy changes** in `SKILL.md`.
- **The ISO framework tag is `ISO270012022`, not `ISO27001`.** `Drata_listRequirements` with the
  wrong tag returns `{"data": []}` — an empty list, **not** an error — which reads exactly like
  "this control has no requirement mapping" and will send the clause/Annex A gate the wrong way.
  Narrow with `code_or_name` (e.g. `"7.2"`) and pass `expand=["controls"]`.
- **Requirements carry the verbatim clause text in `longDescription`.** This is the authoritative
  wording — read it rather than reasoning from the control `description`, which is Drata's paraphrase
  and is often broader. The `controls` expansion also shows every control mapped to that requirement
  with its own `isReady`, which is how you find the *weakest* control under a clause rather than
  assuming the one you were handed is the problem.
- **Personnel tools work** — `read:personnel` was granted on 2026-08-25; `/ask-drata` rule 7 owns
  the scope facts. Use `Drata_listPersonnel` to check whether a name in a draft is a person when
  running the durability check. Who owns a risk is still read from its `owners` expansion, which is
  that fact's home.
- **Check what a policy already covers before staging a policy→control link.**
  `Drata_searchControls(policy_id=N)` lists every control a policy is attached to;
  `has_policy=False` lists controls with no policy at all. **Do not attach a policy to a control
  that already carries its correct governing one** — it makes `hasPolicy` true while sending an
  auditor to the wrong document, which is worse than the gap it papers over. Worked example,
  2026-08-21: the Separation of Duties Policy (id 77) looked like it belonged on DCF-745, DCF-5 and
  DCF-69, since all three mention segregation of duties. In fact DCF-5 already carried the Change
  Management Policy (25) and DCF-69 the System Access Control Policy (18); only DCF-745 was
  unlinked, and it was among the controls then carrying `hasPolicy: false`. One link was right,
  three would have been noise.

---

## 7 — Creating and updating a risk: verified constraints

`Drata_createRisk` became available on **2026-08-21**, when the `create:risk` OAuth scope was
granted. `Drata_updateRisk` followed the same day and **was first exercised on 2026-08-24** — two
calls amending `treatmentDetails` on risk `CR-06`, both returning the updated record. It works;
the earlier "not yet exercised, probe it on first use" note is retired. Two behaviours those calls
confirmed, both of which bite:

- **Pass `treatment_plan` alongside any treatment field.** `treatment_details`, `residual_impact`
  and `residual_likelihood` are silently dropped when `treatment_plan` is absent or `UNTREATED` —
  the same trap as on create, and it fails quietly rather than erroring.
- **Omitted relation fields are left unchanged, not cleared.** `owners`, `reviewers` and
  `control_ids` were omitted on both calls and all came back intact. The "replaces, does not
  append" warning applies only to a field you actually pass.

Everything below was verified by making these calls: each row is a failure that actually happened,
not a caution.

| Constraint | Detail |
|---|---|
| **`description` is capped at 768 characters** | The API returns `400 … maxLength: description must be shorter than or equal to 768 characters`. It **rejects**; it does not truncate. Count the string before calling. A full risk narrative will exceed this — put the detail in `treatment_details`, which has no comparable limit, and keep `description` to the risk statement itself. |
| **There is no `riskId` parameter** | The register assigns its own id and you cannot supply one. A `GV-33` agreed with the user came back as **`CR-05`**. Treat any pre-agreed id as advisory: after creation, report the id Drata actually gave, offer to rename it — whether `Drata_updateRisk` accepts `riskId` is untested, so try it and fall back to the UI — and **fix every downstream reference** — IRT summary and description, Jira comments, handover notes. |
| **`control_ids` takes numeric ids, not DCF codes** | `DCF-745` is `217`, `DCF-5` is `169`, `DCF-69` is `88`. Read them from `Drata_listRequirements(expand=["controls"])`, or from the `control-details/<id>/overview` URL in `compliance/drata-controls-register.md`. |
| **`owners` silently drop non-admin users** | They resolve by name or email, but a resolved user without an admin / risk-management role is dropped **without an error**. Always compare the returned `owners` array against what you asked for, and say so in the summary. `reviewers` is never sent (§7 below); on any risk you touch, confirm the returned `reviewers` array came back empty. |
| **Treatment fields need a non-`UNTREATED` plan** | `treatment_details`, `residual_impact`, `residual_likelihood`, `anticipated_completion_date` and `completion_date` are silently dropped when `treatment_plan` is `UNTREATED` or unset. |

**Bitpool's standing default is `owners` = the default risk owner** (decision, 2026-08-21), unless
the user names someone else for that risk. The person is named once, in `SKILL.md`'s Bitpool
context (*"The default person for structured fields"*); this file never repeats the name. Do not
reason your way to a different owner because the risk happens to describe the owner's own role —
that argument was made and rejected. Ask only when the risk plainly belongs to someone else. The
name goes in the `owners` field only — never into `treatmentDetails` or any other prose, which
names the role (*"the risk owner"*) under the writing standard.

**Creating the risk does not discharge the staging rule.** Show the complete field block, get an
explicit yes, then call — and report the assigned `riskId` back, because it will not be the one in
the block you just showed.

### Reviewers: Bitpool records none — SETTLED

Bitpool decided on **2026-08-24** not to populate Drata's risk reviewer field on any risk. The
decision is recorded in `CR-05`'s `treatmentDetails`, in its item on the reviewer field. It
**supersedes the 2026-08-21 default of a named second-person reviewer (owner ≠ reviewer)**, which
is withdrawn.

**Never pass `reviewers` to set one — omit the field.** The only permitted value is an explicit
empty list, and only to clear one found set (see the drift corollary below).

Why: clause **6.1.3(f)** requires the organisation to *"obtain risk owners' approval of the
information security risk treatment plan and acceptance of the residual information security
risks."* It requires the **risk owner**, not a second party, and the owner's recorded acceptance
satisfies it — recorded in the management review minute or the dated change-record comment, never
inferred from `owners`, which names only the current owner. A reviewer field is the tool's
construct, not an ISO requirement — see `treatment-decisions.md` §8. Independent challenge is intended to come from the **periodic risk
assessment review held with the CEO and CTO present, under `DCF-16`** — a review of the register,
not a per-entry field.

**Where a risk relies on that review, point at `DCF-16` and its evidence — never copy another
risk's wording of it, and never state it as a bare present-tense fact.** This is the review relied
on as a treatment measure — independent challenge — never the entry's own re-examination, which
the entry does not state at all (Security Drata profile §3.2). Where `DCF-16` is in the risk's
`control_ids`, the link is the pointer and prose does not name the code. If the entry states the
review as an event, it follows the Security Drata profile §3.2 anchored-verification rule: the
latest review only, its date, the forum and where it is recorded, and what re-performs it — the
periodic risk review, raised in `CYB`. Its currency is a live condition, not a given: read
`DCF-16`'s readiness and its newest evidence version (`versions[].createdAt`) before writing. Once
the latest review falls outside the cycle the policy sets, the assurance is stale — say so and stop
relying on it. Asserting an operating cadence off a single lapsed record is the error this rule
exists to prevent.

**Scope of the suppression — the field only.** An empty `reviewers` array is the designed state and
is never a finding; do not report it as a gap. Two things that *are* still reportable:

- the **currency** of the `DCF-16` review the decision leans on; and
- the **Risk Assessment Policy criterion** requiring reviewer ≠ owner, whose removal is drafted and
  queued in `IRT-17` for the bulk promotion. Read the version in force before reporting: while it
  still carries the criterion, the approved policy requires a reviewer the register does not carry.
  That divergence is a tracked conformity item — if its queue row disappears before the promotion,
  say so.

Two corollaries, both of which bite in practice:

- **A reviewer found set on a risk is drift, not data — clear it.** Omitting `reviewers` leaves an
  existing one intact (see the relation-field bullet above), so clearing takes a deliberate empty
  list, not silence — **and `treatment_plan` must be passed on the same call**, or the field is
  silently dropped along with every other treatment field. Raise it in the approval block, clear it
  on that write, and quote the returned `reviewers` array back in the summary. *The empty-list clear
  is not yet exercised against this account* — the two logged `Drata_updateRisk` calls omitted the
  field rather than clearing it — so read the response, don't assume.
- **Never write treatment text that claims a reviewer is recorded.** Prose asserting one is false by
  construction and survives the field being cleared — this happened on `CR-07` item 15 and in two
  places in `IRT-21`, all corrected 2026-08-26. Delete the *reviewer claim* only: a genuine approval
  by another party stays, named as what it actually is — by role — and pointed at its own record.

This is settled. **Do not re-open it, and never reach for the reviewer field as the way to get a
second name onto a risk** — that name belongs in a management review minute
(`treatment-decisions.md` §6), not in Drata's register.
