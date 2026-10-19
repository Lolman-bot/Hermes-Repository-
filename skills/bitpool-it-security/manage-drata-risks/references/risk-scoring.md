# Risk scoring — the scales, the criteria, and the threshold trap

Read at Phase 3, before proposing any score change.

> **Snapshot — 2026-08-24.** The tables below are transcribed from Bitpool's `Risk Assessment
> Policy`. **Always read the live policy content** with `Drata_listPolicies(name="risk")` (id `17`)
> and reconcile. If the live policy differs, the policy wins and this file needs correcting. A band
> absent from this page does **not** prove the policy lacks it — it may have been added since.
> These values are for scoring. A risk entry cites the policy by name and never copies a scale, band
> or threshold into its text (`/bitpool-writing-standard` rule 1).
>
> **The matrix — updated 2026-09-29.** The 5×5 matrix is a Markdown table in the Risk Assessment
> Policy draft, under `## Risk Score Matrix`, so it reads as text. A copy for the wiki sits at
> `security-documentation/risk-management/risk-matrix.md`; **the policy governs**, and where the two
> differ the policy wins. The table replaced an embedded image (`image7.emf`) that disagreed with the
> Risk Rating Criteria in three places: **Minor (2) × Possible (3) read 3; the correct value is 6**,
> crossing from Low to Medium; and the score-5 and score-10 cells were each shaded one band low
> (5 as Low, 10 as Medium). The promoted policy, in the `isms` repo and in Drata's Policy Center, carries that
> image until the draft is promoted, so never read a score off the image or a `.docx` built from it.
> Compute `impact` × `likelihood`, then take the band from the table below.

---

## 1 — The scales

`impact` × `likelihood` = `score`. Same arithmetic for the residual triplet.

### Impact

| Level | Definition (abridged — the policy is authoritative) |
|---|---|
| **Incidental (1)** | Minimal financial or operational loss · not reportable to a regulator · isolated staff dissatisfaction |
| **Minor (2)** | Minor financial loss · reportable with no significant enforcement action · general morale issues |
| **Moderate (3)** | Moderate financial loss · breach report requiring timely corrective action · widespread morale problems and noticeable turnover |
| **Major (4)** | Significant financial loss · national sustained negative coverage · report requiring major corrective projects · loss of some senior management |
| **Extreme (5)** | Massive financial loss · international long-term reputational damage · significant prosecution, fines, class actions · multiple senior leaders resign or are removed |

**The impact bands are qualitative only.** There are no dollar thresholds anywhere in the policy.
This matters because the proportionality test in the acceptance criteria compares *cost* against
*assessed impact* with no monetary calibration available — so any proportionality argument is a
reasoned judgement, and must be written as one rather than presented as arithmetic.

### Likelihood

| Level | Description |
|---|---|
| **Rare (1)** | Once in 100+ years (<10% over the life of the company) |
| **Unlikely (2)** | Once in 50–100 years (10%–35%) |
| **Possible (3)** | Once in 25–50 years (35%–65%) |
| **Likely (4)** | Once in 5–25 years (65%–90%) |
| **Certain (5)** | Up to once in 5 years (90% or greater) |

Note how long these horizons are. A control failing "probably within a couple of years" is
**Certain (5)** on this scale, not a middling 3. Scoring likelihood by gut feel rather than against
these definitions is the most common scoring error, and it biases the whole register downward.

### Bands

| Band | Score |
|---|---|
| **Low** | ≤ 4 |
| **Medium** | > 4 and ≤ 9 |
| **High** | > 9 and ≤ 16 |
| **Critical** | > 16 |

---

## 2 — The Risk Acceptance Criteria

Five criteria. A decision falling outside them **is not a documented acceptance** and must be
escalated to the CEO as an exception.

1. **Threshold.** Low or Medium may be retained without further treatment, subject to a recorded
   review date. **High or Critical must be treated**, and may be retained only where treatment has
   reduced the residual to Medium or below.
2. **Proportionality test.** Where a risk is retained, the decision must record that the cost of
   further treatment exceeds the assessed impact — assessed across **direct** cost (personnel,
   tooling, licensing, external services), **opportunity** cost (work displaced, including
   productive time lost acquiring the competence a control requires), and **operational** cost
   (latency, availability, process burden).
3. **Competence-constrained controls.** Where a control requires competence held by nobody other
   than its own operator, all four clause 7.2 options — training, mentoring, reassignment, hiring —
   must each be considered and each selected or rejected against criterion 2. *A control is not
   exempt merely because the competence is concentrated in one individual.* The decision must state
   which options were evaluated and why each cost exceeded the assessed impact.
4. **Acceptance authority.** The risk owner records the acceptance; clause 6.1.3(f) requires the
   *risk owner's* approval, not a second party's. No separate reviewer is recorded against an
   individual entry (Bitpool decision, 2026-08-24). Retention of any risk assessed **High or
   Critical before treatment** additionally requires acceptance by the CEO or the CTO, minuted at
   management review.
5. **Expiry.** No acceptance is open-ended. Every retained risk carries a review date no more than
   twelve months from acceptance and is re-presented at management review.

**Criterion 3 is the one that gets skipped.** When a risk exists because only one person can do
something, the honest entry has to show each clause 7.2 option — training, mentoring, reassignment,
hiring — considered, and why its cost exceeds the assessed impact, not merely assert that the
organisation is small.

### Writing the criteria into an entry

The criteria decide what the entry must *show*; `/bitpool-writing-standard` decides what its words
may *say*. Where they meet:

- **Threshold (criterion 1).** Cite the Risk Acceptance Criteria in the Risk Assessment Policy by
  name — *"retained under the acceptance criteria in the Risk Assessment Policy"* — never the band or
  the number. The score fields hold the scores.
- **Proportionality and competence (criteria 2 and 3).** The entry states the reasoning: which
  options were considered and why each cost exceeds the assessed impact, and the competence named by
  role. The costings, quotes and headcounts, and the individual who holds the competence, are
  snapshot detail — they go in a dated comment on the RTP ticket (staged for the user where the risk
  has none), or stay in the decision record they came from (`drata-risk-fields.md` §3).
- **Acceptance (criterion 4).** The named acceptance lives in the management review minute or
  acceptance record, and the current owner in `owners`. Where the entry needs to state the
  acceptance, it is an anchored event — *"accepted by the risk owner at management review on
  `<date>`; minuted"* — and it covers only the residual level and treatment in force on that date
  (the standard's rule 4). A change to either removes the sentence. Where this skill's change
  removes an acceptance, the verification-record comment (`drata-risk-fields.md` §3) states that the
  changed position awaits acceptance at the next management review, and the Phase 4 summary lists
  the risk as awaiting management review and tells the user to table it there. The entry never says
  *pending*; the edit that follows the minute restores the sentence with its new date.
- **Review date (criteria 1 and 5).** Drata has no review-date field, `anticipatedCompletionDate` is
  blank by decision, and no date goes in `treatmentDetails` prose. The review date lives with the
  periodic risk review control (`DCF-16`) and its recurring task in `CYB`, which re-present every
  retained risk — never in the risk text. The entry does not state its own review in any form: no
  *"Review: `<date>`"* line, no *"reviewed annually"*, and no pointer to the review either — not the
  policy that sets its cadence, not the reviewing control. A treatment item that is itself a
  recurring activity is different: it cites the policy that sets its cadence (Security Drata §3.2).

---

## 3 — What `residual` means, and the trap

`residualScore` is **the position after the treatment is implemented** — not the position today.

That distinction is where a well-intentioned re-score does damage. Consider a risk with inherent 16
(High) and residual 6 (Medium), where three of the six measures the residual assumes are still
`PLANNED`:

- **Reading residual as "today"** → the honest number is higher, maybe 12. But 12 is **High**, and
  criterion 1 says a High risk may be retained *only* where treatment has reduced the residual to
  Medium or below. So the entry immediately violates its own governing policy, and the organisation
  is obliged to fund treatment it may have already assessed as disproportionate under criterion 2.
- **Reading residual as "after treatment"** → 6 stands, and the honesty burden moves to the text:
  the entry must state which items the residual assumes, filed as planned — each with its outcome,
  the condition on which it will be relied on, and its IRT pointer.

**Prefer the second.** Leave the score as the post-treatment target and make the text carry the
truth:

> "The residual score assumes the planned items 2 to 6 are operating; each is relied on once it is
> delivered, and each is tracked in `IRT-n` (find by: `project = IRT AND text ~ "<riskId>"`)."

That sentence is worth more to an auditor than a number nudged upward, because it names *which*
measures the number depends on. And it stays true as the items land: it states the dependency, not
their progress, which lives on the ticket (`/bitpool-writing-standard` rule 3). A line such as
*"none of them is operating yet"* goes false the day the first one does, and nothing re-syncs it.

**When a residual re-score genuinely is right:** when the treatment is complete and turned out
weaker than assumed, when a measure has been abandoned rather than delayed, or when the inherent
risk itself has changed. In those cases the target *is* today, and the number should move.

### Rules for touching a score

- **Never change a score unasked.** Propose it with the band it lands in and what criterion 1 then
  requires.
- **Always set the full residual triplet**, including for `ACCEPT`, where residual equals inherent.
  A blank residual is Bitpool's most common register defect: an explicit equal residual reads as a
  decision, a blank one reads as an omission.
- **`residual_impact` / `residual_likelihood` are silently dropped** unless `treatment_plan` is set
  to something other than `UNTREATED` in the same call. The API does not reject them — it discards
  them. Pass `treatment_plan` explicitly whenever you touch them.
- **Check the resulting band against criterion 1 before proposing**, and say what it implies. A
  proposal that quietly makes a risk unretainable is worse than no proposal.
- **If the residual exceeds the acceptable level, stop and say so.** That needs a further control or
  an escalated exception — not a quiet acceptance.
