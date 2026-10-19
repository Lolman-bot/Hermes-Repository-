# Modes §1–§3 — full procedures

> Relocated verbatim from this skill's `SKILL.md` when it was ported to Hermes; `SKILL.md` keeps the
> route and a one-line summary of each rule, and this file is the full text. Rule numbers (rule 1–14)
> refer to `references/vendor-rules.md`; §1–§3 to `references/workflows.md`; "the behaviour table" to
> `references/drata-vendor-behaviour.md`.

## §1 — Add a new vendor

The order matters: classify before you create, because a vendor created without a score is a
register entry that makes `DCF-56` *less* true, not more.

1. **Check it is not already there.** `Drata_listVendors` has **no natural-language search** — page
   it, or filter by `category`. Check archived too: a returning vendor is a `status` change, not a
   new record. Also check `drata-vendors-to-add.csv` in the vendor working folder if the user has
   one, so the proposed classification is not re-derived from scratch.

2. **Establish what it actually does for Bitpool.** What it holds, what it can reach, whether
   anyone logs into it, whether personal information passes through it. If you cannot answer these,
   **ask** — do not infer a score from a vendor's marketing.

3. **Classify against `references/classification-rubric.md`.** Relationship type, all four
   service-model flags, inherent impact, residual risk, and the review obligation that follows.

4. **Write the staging note** — `references/staging-note-format.md` — showing every field you will
   send, and every field you are deliberately leaving unset with what would establish it. Draft any
   free-text value to Security Drata and show the durability check under section 1. Then stop and
   wait for `status: approved`.

5. **`Drata_createVendor` — one call, custom fields inline.** The tool schema says only `name` is
   required, but **Drata rejects a create that omits its required custom fields**, returning a `400`
   that names them. See `references/field-contract.md` — the current required set is expected to be
   `7`–`10` but has not been re-tested since fields were deleted, so **read the error rather than
   assuming.** There is no useful "create now, classify later" path.

6. **Read the created vendor back with `Drata_getVendor`** and report the assigned `id`, the `owner`
   that came back (non-admin owners are silently dropped), every custom field, and anything that did
   not land. Check `breakdown.current` moved by exactly one.

7. **Record the outcome in the staging note's results section** — the assigned id, what the API
   returned, and any deviation from the approved values with its reason. Then set the frontmatter
   `status`. Use `written-pending-review` rather than `written` where the security review is still
   outstanding; the note should not read as finished when the work is not.

8. **Tell the user what remains theirs**: the security review itself, any document to attach, and
   the agreement review required before access is granted.

9. **Where the review is being deferred, set `status: UNDER_REVIEW` and say what carries the date.**
   That status is the register's own record that the assessment is unfinished, and it is filterable,
   so the obligation is visible in Drata. What `UNDER_REVIEW` does **not** carry is a *date* — and a
   future `renewalDate` makes the vendor invisible to the overdue filters (see the behaviour table).
   So the division is: **`status` records that a review is outstanding; an `IRT` ticket records the
   commitment, its owner and its size** — and carries the date once the board-wide prioritisation pass
   sets it (`/manage-drata-control` `references/irt-tickets.md` §1). Neither substitutes for the
   other. **Do not expect a due date on a newly raised IRT ticket**: since 2026-09-15 they are created
   undated, so an `IRT` ticket cannot be relied on to say *when* a first review lands until that pass
   has run. Where a date is already committed somewhere, it is quoted in the ticket body as its
   `Date constraint:`.

   **The IRT ticket is created by `/manage-drata-control`; this skill never creates it.** That skill
   owns IRT's forms and labels, drafts the `summary` and `description` under Security Jira, shows
   their durability check and creates the ticket behind its own approval block. This skill writes
   the hand-off in the vendor's staging note (section 10), under the note's approval — the vendor as
   the object of the commitment, its Drata vendor record, the outcome needed, the closing step (on
   Done, the review is recorded in Drata and the vendor's `status` leaves `UNDER_REVIEW`), and the
   creation-time context for that skill's dated creation comment. After the write, hand section 10
   to `/manage-drata-control` and say in the report that the ticket is not yet raised.

---

## §2 — Correct one existing vendor

1. **Read live** — `Drata_getVendor` with
   `expand=["customFields","vendorUser","scheduleConfiguration","dataAccessedOrProcessed"]`.
   **Do not add `latestSecurityReviews` and trust it** — see rule 6 and the gotcha below.
2. **Read the review history separately** — `Drata_listVendorSecurityReviews(vendor_id=…)`. This is
   the only reliable source, and it is the only way to evaluate the approved-with-conditions limb of
   the review threshold.
3. **Diff against the field contract.** Separate the changes into three blocks and keep them
   separate: **fill** (mandatory fields that are null), **fix** (values that are wrong — including
   free text that copies current state, against Security Drata §3.4), and **wipe** (fields Bitpool
   has retired).
4. **Score changes go in their own block**, per rule 5.
5. **Stage, approve, write, read back, report.**

---

## §3 — Whole-register review cycle

This is the register half of `/quarterly-configuration-and-asset-review`'s `CYB-530`. That skill is
read-only against Drata and hands the changes here.

1. **Size it first, cheaply.** `Drata_listVendors(size=1)` returns a `breakdown` object —
   `{current, total, prospective, archived}` — respecting whatever filters are active.
   **`breakdown.current` is the headline count, not `totalCount`**, which includes archived.
   Combining a filter with `size=1` gives an exact count in a tiny response; that is by far the
   cheapest way to build a cross-tab. **`size=50` blows the MCP response limit** (~60k characters)
   and gets written to a file instead of returned.

2. **Read the register properly.** Page it to `cursor: null`. A truncated read reports a tidy
   register that is not.

3. **Check each record for what actually goes stale**: a security owner who is still employed; a
   classification and both scores set, not left at default; a review where the threshold calls for
   one, and its date; `status` for vendors no longer in use; and free text in `services_provided`,
   `data_stored` and `location` that copies current state — flagged per the audit sweep in
   `/bitpool-writing-standard`'s `references/durability-check.md` §5, reported, and rewritten only
   through a per-vendor staging note (rule 1).

4. **Reconcile both directions, and name the source and its date.**
   - **In use but not registered** — the finding that matters most, because an unregistered vendor
     has had no security review. Sources: the identity provider's application list, and the vendor
     billing or card-spend view.
   - **Registered but no longer used** — mark inactive via `status`. **Never delete.**
   - A reconciliation against nothing is just the register agreeing with itself.

5. **Sequence archival behind the access sweep.** Archiving a retired vendor removes it from the
   current register while residual access may still be live — that hides the exposure rather than
   closing it. Confirm the tenancy is closed or access revoked *first*. Worked example, 2026-09-03:
   `Bitbucket` (id 123) was `ACTIVE` at inherent `CRITICAL` long after GitHub replaced it, and
   archiving was deliberately held pending the access sweep on `IRT-24`.

6. **Produce the worksheet, then work it one vendor at a time.** Fanning the *analysis* out across
   parallel agents is fine and fast — each vendor is independent. Fanning the *writes* out is not:
   rule 1 stands regardless of how the analysis was produced.

7. **Evidence.** Attach the register extract as pulled, and comment sources, extract dates, each
   check with its dated count, a disposition per exception, and what remains open. **Record a
   no-change result in full** — "no change" alone is indistinguishable from nobody having looked.
   **There is no attachment tool.** Name the files and their paths; the user attaches them.

---

## What this skill hands off

- **`/isms-draft`** — any drift between the register and the Vendor Management Policy. Never edit
  policy text here.
- **`/manage-drata-control`** — the IRT ticket for a deferred first review, from the staging note's
  section 10 hand-off (§1 step 9); and where a register finding is really a control's position
  (`DCF-56` Vendor Register and Agreements, `DCF-57` Vendor Compliance Monitoring, `DCF-132`
  Privacy and Security Requirements in Third-Party Agreements, `DCF-168` Vendor Management Policy,
  `DCF-507` Vendor Due Diligence, `DCF-762` Managing Changes to Supplier Services — the
  A.5.19–A.5.23 family).
- **`/quarterly-configuration-and-asset-review`** — the wider cycle this is one sub-task of.
- **`/ask-drata`** — new connection-level findings.
- **`/bitpool-writing-standard`** (section `bitpool-general`) — the wording of the free-text vendor
  fields (**Security Drata**) and the durability check shown in the staging note. Never restated
  here.
- **The user** — every security review, every document, every custom field definition, and every
  score decision.
