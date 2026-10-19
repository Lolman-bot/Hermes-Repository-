# The MFA decision and the fourteen rules — full text

> Relocated verbatim from this skill's `SKILL.md` when it was ported to Hermes; `SKILL.md` keeps the
> route and a one-line summary of each rule, and this file is the full text. Rule numbers (rule 1–14)
> refer to `references/vendor-rules.md`; §1–§3 to `references/workflows.md`; "the behaviour table" to
> `references/drata-vendor-behaviour.md`.

## Scope and the writing standard

**Read `references/field-contract.md` before any write.** It is the authority on which fields this
skill sets, which it wipes, which it never touches, the exact enum values, the custom field ids, and
the write shapes that are verified versus inferred. Do not reconstruct any of that from memory.

**Load `/bitpool-writing-standard` before drafting text for one of its registered targets — and
only then.** Two of this skill's outputs land in that standard's register:

| Output | End location | Writing profile |
|---|---|---|
| Proposed values for the free-text fields `services_provided`, `data_stored` and `location` | Drata — Vendors | **Security Drata** (§3.4) — durable |
| The security review text the user pastes (staging note section 7) | Drata — Vendors | **Security Drata** — a dated snapshot: specific by design, no durability check |

Load the standard's `SKILL.md` for the target gate and the six rules, then the named profile, before
drafting either. Wherever durable text for one of these targets is staged, show the durability
check (that skill's durability-check reference, §1) directly under it — and because approval
happens in the staging note (rule 1), that is where the check goes. Structured fields — enums,
booleans, dates, `owner`, custom fields — are the home of their value and take no check.

**This skill writes no `IRT` ticket.** Where a first review is deferred (§1 step 9), it hands the
ticket to `/manage-drata-control`, which owns IRT's forms and labels, drafts the ticket's words
under Security Jira and shows their durability check in its own approval. The hand-off note
(staging note section 10) carries the facts that skill needs, not paste-ready ticket text.

**Everything else this skill produces is outside the register**, and the standard does not apply
there: the staging note itself (a working file in the GRC library, specific by design), including
its section 10 hand-off note, the cycle worksheet and handover, the comment on `CYB-530`, the ISMS
Exemption Application (`ITS`), the session log, and reports in chat.

> **Requires `/bitpool-writing-standard` (section `bitpool-general`).** Before drafting text for a
> Drata vendor record, load it. If it is not installed, **stop and tell the user once per chat**:
> *"`/bitpool-writing-standard` isn't installed, so the Security Drata writing profile can't be
> applied. Installing it from the `bitpool-general` section is recommended. Proceed without it?"* Continue
> only on a yes, and do not ask again in the same chat.

---

> ## ⛔ MFA is not a vendor attribute. This skill does not record it.
>
> **Bitpool decision, 2026-09-04: MFA scope is carried in a separate register.** Custom fields `4`
> ("Bitpool authenticates to vendor?"), `5` ("MFA required?") and `6` ("MFA note") were created for
> it, used briefly, and **deleted**. Do not recreate them, do not write to `password_mfa_enabled`,
> and do not add an MFA column to a staging note.
>
> **The case that settled it — GitBook has three authentication planes on one vendor record:**
>
> | Plane | Control |
> |---|---|
> | Reading the private wiki (ISMS and IT documentation) | Entra SSO — **technically enforced** |
> | GitBook organisation admin and content editing | **none available at any plan tier** |
> | The public wiki (customer-facing product docs) | none — public by design |
>
> One vendor, three answers. **Any per-vendor MFA field misreports at least two of them**, and the
> single-select that was tried had to be set to `Other` with the real answer in a free-text note —
> which works as a record and is useless as a filter.
>
> Where a vendor's authentication posture matters, it is an **observation in that vendor's security
> review**, where the nuance survives and an auditor will actually read it. Never reduce it to a
> field.

---

## The fourteen rules

1. **One vendor per approval, and the approval happens in a file — not in the chat.** Write a
   per-vendor staging note, let the risk owner read and annotate it, then write to Drata from what
   the file says. A bulk run is one approval per vendor, not one approval; that is the point of it,
   not an inefficiency to optimise away.

   **The chat is the wrong medium for this and using it is a defect.** A vendor record is twenty-odd
   fields, several of them judgement calls, and reviewing that in a scrolling transcript means the
   reader cannot save it, cannot annotate it, and cannot come back to it. Bitpool feedback,
   2026-09-03, in the risk owner's words: *"doing this in the chat is frustrating, can you put the
   vendor in a .md here for me to read, save and then approve?"* An earlier version of this rule
   said "render the block, get an explicit yes" — that produced exactly that frustration.

   **Everything this skill writes lives in the GRC document library**, under:

   ```
   %USERPROFILE%\Bitpool Pty Ltd\GRC - Bitpool - Documents\General\Drata\Vendors\
   ├── <VendorName>\<YYYY MM>\<vendor>.md     ← per-vendor staging notes
   └── Reviews\<YYYY MM>\                     ← cycle-level artefacts
   ```

   `%USERPROFILE%\Bitpool Pty Ltd\` is where the user's machine syncs Bitpool's SharePoint
   libraries; the GRC library sits under it. `%USERPROFILE%` is cmd.exe syntax, and neither
   `read_file`/`write_file` nor the other shells expand it, so **resolve it to an absolute path before
   any file operation** — in Hermes's `terminal` (git-bash on Windows) `echo "$USERPROFILE"`;
   PowerShell `$env:USERPROFILE`; WSL `/mnt/c/Users/<user>/`. If the library is not synced on this
   machine, ask the user for the path with `clarify`.

   Corrected 2026-09-04. An earlier version of this rule pointed at
   `OneDrive - Bitpool Pty Ltd\Eric's Notes\Vendors\`. **That was personal OneDrive and it was the
   wrong home** — these are GRC records, and the library above is a SharePoint-synced Bitpool
   document library that other people can reach and that survives one person's OneDrive. The vendor
   folders sit beside `Drata\Evidence\`, which follows the same dated pattern.

   Both levels are date-partitioned by cycle (`2026 09`), so a vendor reviewed again next year gets
   a new folder rather than overwriting the record of what was decided this time. **Per-vendor** notes
   go in the vendor's own folder; **cycle-level** artefacts — the worksheet, the task tracker, the
   register extracts, the handover — go in `Reviews\<YYYY MM>\`.

   It is an Obsidian vault, so use frontmatter and `[[wiki links]]`. The note format is in
   `references/staging-note-format.md`; follow it rather than inventing a layout each run.

   **Never leave a copy behind when a file moves.** Two copies of a vendor decision in two libraries
   is the same defect this skill spends its whole time correcting elsewhere.

   **The override mechanism, which is the whole reason this works:** every proposed value sits
   beside an empty **`Your value`** column. **Read that column, not your own proposal.** A blank
   means accept as proposed; anything written there wins. When `status:` in the frontmatter changes
   from `staged` to `approved`, re-read the file and write from it.

2. **Re-read the vendor live immediately before the write, and compare `updatedAt`.** Not once at
   the start of a run — immediately before each write. The register is actively edited by hand, and
   `updatedAt` is the only evidence you have that nobody moved underneath you. A value read twenty
   minutes ago is a guess.

3. **Pass only the fields you are changing.** `Drata_updateVendor` is a partial update: omitted
   fields are left unchanged. Sending a whole object you read earlier is how a concurrent edit gets
   reverted silently.

4. **Never write `confirmed`, in either direction.** Setting it stamps `confirmedAt`, which reads as
   a human having verified the record — writing it in bulk manufactures assurance that did not
   happen. Clearing it destroys the genuine confirmations already on the register. It is the one
   field that is neither keep nor wipe: **never touched.**

5. **Never write `impact_level` or `risk` without explicit, per-vendor approval of that specific
   score.** Scores are judgement, and they are load-bearing: `risk` decides the review obligation.
   A parallel AI classification pass over all 35 vendors on 2026-09-03 proposed re-scoring 23 of
   them, and **20 of the 23 moved inherent impact upward** — that is rubric bias, not twenty
   findings. Two moved residual risk *down* from `HIGH`, which would have silently removed those
   vendors from review altogether. Propose scores in a separate, clearly-labelled block; never fold
   them into a field-completeness update.

   **And reopen a score when new information invalidates its basis — never carry it forward because
   the reader left the override column blank.** A blank means "accept as proposed"; it does not mean
   "accept a proposal whose premise you have just disproved". Worked example, 2026-09-03: GitBook was
   proposed at residual `MODERATE` on the basis of *"MFA enforced and monitored"*, taken from the
   handover CSV. The risk owner then annotated the same note to say the admin back end has no MFA
   option at all. The score column was blank, and carrying `MODERATE` forward would have written a
   number whose stated reasoning the file itself contradicted. It was reopened at `HIGH`, with the
   change and its cause called out at the top of the note.

6. **You cannot create a security review, and you cannot upload a document.** Verified twice on
   2026-09-03 across the whole deferred tool list: `Drata_listVendorSecurityReviews` and
   `Drata_listVendorDocuments` exist and there is **no create or update counterpart for either.**
   This is a capability limit — the verb is absent from the MCP server, like `delete:vendor` — not a
   scope that could be granted. **Never offer to record a review or attach a SOC 2 report.**
   What you *can* do is set `renewal_schedule_type`, `renewal_date` and `status`, which is how the
   register carries the obligation. Say it that way: you arm the requirement, the user performs and
   records the review.

   **But be precise about which field does what, because they are not interchangeable.** A
   `renewal_date` in the future puts the vendor in *neither* the `OVERDUE` nor the `DUE_SOON` filter,
   and `renewalDateStatus` will read `COMPLETED` even with zero reviews on file — so the renewal
   fields schedule the *next* review and say nothing about whether a *first* one happened.
   `status: UNDER_REVIEW` is what records that, and it is filterable. Do not tell the user the
   renewal date will surface an outstanding first review; it will not.

7. **You cannot create a custom field definition.** Only populate one that already exists. Defining
   a field is a Drata UI action. If a classification needs a field that is not there, stop and ask
   for it to be created, then capture its `customFieldId` — writes address custom fields by id.

8. **Never invent a `renewal_date`, and never move one that has passed.** An overdue review is a
   review to *perform*. Editing the date forward launders an overdue obligation into a current one,
   which is worse than the overdue state it hides. Propose a date with reasoning and get agreement,
   exactly as for a score.

9. **A vendor field carries no current-state value; a count in a snapshot carries its date.** Two
   halves, and only the first is the writing standard.

   **The free-text vendor fields follow `/bitpool-writing-standard`** — core rule 3 and Security
   Drata §3.4, loaded per the writing-standard rule at the top. No counts, people's names, email
   addresses, dates, versions, configuration values, plan tiers, prices or certificate periods:
   each has its own home — a structured field, the security review, or the staging note's `Basis`
   column — and the field's prose copies none of them. The one reference a value carries is the
   contract document `location` rests on (rule 11). An IRT ticket for a deferred review is drafted
   by `/manage-drata-control`, not here (§1 step 9).

   **The snapshots this skill writes date every count** — the `CYB-530` cycle comment, the
   worksheet, the staging note, the session log. Write *"18 overdue as at 2026-09-03, per
   `next_review_deadline=["OVERDUE"]`"*, never *"18 overdue"*. The register moves daily. This is
   the skill's own convention for its working records, which sit outside the standard's register.

10. **This skill never writes ISMS policy text.** If the register contradicts the Vendor Management
    Policy — the threshold, the classification definitions, the inventory field list — that is drift
    for `/isms-draft`, and the policy is the parent of record. Where they disagree, **the policy
    wins and the register is wrong**, unless the risk owner decides otherwise explicitly.

11. **Research a field's value before offering to leave it blank, and never inherit a classification
    unverified.** Two halves of the same failure.

    **Research first.** "A wrong value is worse than an empty one" is true and is not a licence to
    leave fields null. A vendor's privacy policy, terms, trust centre, legal entity and governing law
    are all published; find them, and propose each field value with the date you verified it and
    its citation (the URL and the date read) in the staging note's `Basis` column, never inside the
    value. `location` alone names, inside the value, the contract document it rests on, per
    Security Drata §3.4 — *"`<region>`, as stated in the vendor's Data Processing Addendum"* — but
    never a date. What has no field of its own — the legal entity, the governing law, a
    certification's report period — belongs in the security review text (staging note section 7),
    not the nearest free-text field.
    Leave a field blank **only** when it genuinely cannot be established from public sources — and
    then say what *would* establish it, so the blank is a next step rather than a shrug. Bitpool
    feedback, 2026-09-03: *"you should propose these and have the link work in this .md file."*

    Worked example: GitBook's `privacy_url`, `terms_url` and `trust_center_url` were all verifiable
    in two lookups, and the trust centre turned out to carry a **SOC 2 Type II report** — which is
    the artefact `DCF-57` exists to collect. Leaving those null would have hidden it. `location` is
    the half that went wrong: no hosting region was published, and the create on 2026-09-03 wrote
    GitBook's legal entity, its governing law and a "hosting region not publicly stated" finding into
    the field instead. None of those says where the service is delivered. They are dated review
    observations; `location` holds the delivery location at the granularity the contract states,
    naming the contract document it rests on, or stays `null` with the Data Processing Addendum
    named in the note's section 4 as what would establish it.

    **Never inherit a classification — and establish who or what produced it before you weigh it.**
    A handover CSV, a prior session's note or a wiki page is a starting point, not evidence.

    Same worked example, and the provenance is the sharp end of it: `drata-vendors-to-add.csv`
    labelled GitBook *"Tier 1 — enforced and monitored"*, and GitBook **has no MFA feature at any
    plan tier**. That single label had set the residual score. It was initially assumed to be the
    risk owner's own classification; it was in fact **produced by a prior Claude session from a Xero
    biller dump** — an AI inference about an authentication control, never checked against the
    vendor's documentation. **Nine further rows carried the same label.**

    So distinguish the two uses of an inherited artefact. That CSV is a good source for **which
    vendors exist** — it came from real billing data. It is not a source for **what their controls
    are**, because nothing in a biller dump can tell you that. Where a prior session's inference has
    been mistaken for an observation, say so, and say how far the same assumption reaches.

12. **A vendor limitation is not a Bitpool control failure — and the difference decides the
    treatment.** Where a control cannot be implemented because *the vendor does not offer it*, that
    is a constraint Bitpool has consciously accepted, not a gap Bitpool failed to close. Recording it
    as a Bitpool failure invites remediation work that cannot succeed; recording it as an accepted
    limitation is both true and auditable.

    The shape: name the limitation precisely, say what Bitpool did to mitigate it, score the residual
    honestly, and get the acceptance recorded. Do **not** soften the score to avoid needing the
    exception — the exception is the artefact that makes the acceptance defensible, so needing one is
    the system working.

    **Where an exemption goes — verified 2026-09-03.** An exemption from an ISMS requirement is
    raised through the Jira service desk, **by the risk owner, never by the agent**:

    > **ISMS Exemption Application** — project `ITS` (IT Service Management, id `12951`), issue type
    > `10597`. Default label `Exemption_Application`, default priority `Major`. Portal:
    > `https://bitpool.atlassian.net/servicedesk/customer/portal/10/group/32/create/10597`

    **The seven questions the form asks** — verified 2026-09-03, draft against these, not against
    generic exemption headings:

    1. Summary
    2. What policy, procedure or control does the exemption relate to? (If known, otherwise N/A)
    3. Describe the requested exemption and justify the request
    4. Who is the exemption requested for? *(e.g. an individual, a type of device, a role)*
    5. Propose controls or measures to mitigate the risk of the exemption
    6. Duration the exemption is requested for *(e.g. 1 year, 1 month, ongoing)*
    7. Date exemption is required by

    Note that 6 and 7 are different questions — duration is how long the exemption runs; "required
    by" is when it must be approved. And note the form has **no residual-risk question and no
    exit-condition question**, so both belong inside answer 3 or the exemption reads as permanent.

    > **⛔ Before drafting anything, find the clause the exemption is *from* and read it. An
    > exemption may not be needed at all.** Worked example, 2026-09-03: an exemption was drafted for
    > GitBook on the strength of a requirement the risk owner described in conversation. Searching the
    > ISMS found that requirement **was not written anywhere**, and that the clauses which did exist
    > were all **conditional** — *"systems that **provide the option**"*, *"**where technically
    > feasible**"* — which GitBook satisfied by failing them. **On the text as written it already
    > complied**, and the exemption was unnecessary.
    >
    > That yields two paths, and they must be put to the risk owner rather than chosen: **record the
    > limitation and raise nothing**, or **amend the policy first, then exempt** — because you cannot
    > be exempt from a requirement that does not exist. Order matters: `/isms-draft` first, exemption
    > second.
    >
    > It is also worth saying which is better policy rather than just presenting both. Here,
    > *"systems that provide the option"* means **a vendor offering no MFA is automatically
    > compliant** — so the weakest vendors pass most easily, which is a gap an auditor can probe.

    **Draft the field values into the vendor's staging note as its own section** so they can be
    pasted; do not propose a mechanism, and do not raise the request. Two things to know about that
    form:

    - The API exposes **only the issue fields** — Summary, Reporter, Approvers (`customfield_11649`),
      Labels, Priority, Due date, Linked Issues, Request participants. There is **no `description`
      field and no exemption-specific field**, which means the portal is almost certainly built with
      Atlassian Forms whose questions are stored as form data and are invisible to the API. So draft
      the narrative under the questions an exemption normally asks, and **say plainly that it may need
      remapping** to the real form rather than implying the mapping is verified.
    - **Always propose an expiry date.** An exemption with no expiry is an acceptance in disguise.
      Aligning it to the vendor's annual review date makes the two reconsidered together instead of
      drifting apart.

    A risk-register entry via `/manage-drata-control` is a different instrument and is still the
    right one where residual risk sits above the acceptable level. The two are not substitutes: the
    exemption records the departure from a stated requirement; the risk entry records the accepted
    exposure.

    Worked example, 2026-09-03: GitBook offers no MFA at organisation or account level; SAML SSO is
    Enterprise-only and Bitpool decided not to upgrade; members inherit Entra MFA via Google
    sign-in, but the magic-link path cannot be disabled, so inheritance is procedural. Residual
    `HIGH`, exception required, compensating controls named as email-domain restriction, a small
    admin count and periodic member review. **Note also that GitBook deliberately preserves non-SSO
    sign-in for organisation admins even on Enterprise** — so "MFA enforced" would have been false at
    any plan level, which is exactly the kind of claim that does not survive an auditor reading the
    vendor's own documentation.

    **The score and the conditions are one decision, not two.** The risk owner overrode GitBook's
    residual from `HIGH` to `MODERATE`, which is defensible — but only because the compensating
    controls are written into the review conditions. A residual score set below where the raw
    limitation would put it is **evidenced by the conditions and by nothing else**. So never accept
    such an override silently: state in the note that the score depends on those conditions being
    recorded, and produce the conditions in the same breath. `MODERATE` with the conditions entered
    is defensible; the identical number with an empty review is a bare assertion.

13. **Never infer a capability from a field's name.** A field called `critical` does not imply
    anything filters on it. A field present in the write schema does not imply it is visible in the
    UI, readable in practice, or used by anything. **Check the tool schema for the filter parameter,
    check the data for whether the field is ever populated, and ask whether the risk owner can see
    it** — then say which of those you actually did.

    Worked failure, 2026-09-03, and it is the second of this shape in one session. The risk owner
    created a custom boolean for business criticality. It was not yet visible via the API, so native
    `critical` was recommended instead, on the stated grounds that it is *"what Drata's own
    critical-vendor filtering reads"*. **That was invented.** `Drata_listVendors` exposes no
    `critical` filter at all. A scan of the register then showed the field is `true` on **zero of 35
    vendors** and the risk owner could not see it in the UI — a dead field, like `rationale` on a
    control. The recommendation would have replaced a working solution with a non-functioning one,
    and the whole error came from reading a field name as a promise.

    The same session produced a second instance: ten vendors were reported as *"silently excluded
    from anything filtering on `critical`"*. Nothing reads the field, so the mismatch was untidy, not
    harmful. **Both claims sounded like findings and neither was checked.**

    The useful rule that survives: *prefer a native field over a custom one where both carry the same
    fact* — **but only after confirming the native field is readable, writable and visible.** Present
    in the schema is not the same as usable.

14. **Never fabricate an authorship record.** Drata stamps author and date on a security review
    observation when it is entered. A drafted observation therefore carries **no** attribution line
    — writing *"Author: Eric Sharp · Date: 16 Aug 2024, 11:07 am"* into draft text invents an
    authorship claim inside a compliance artefact, which is a worse defect than any wrong field
    value in this skill. State that Drata stamps it, and leave it out. The same applies to any
    signature, approval or review date this skill drafts.
