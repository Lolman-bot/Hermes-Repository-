# Audit mode and integration with other skills

> Relocated verbatim from this skill's `SKILL.md` when it was ported to Hermes; `SKILL.md` keeps the
> route and a summary of each rule, and this file is the full text. Bold section names refer to:
> **golden rules** → `references/golden-rules.md`; **Invoke the downstream skills** and **Bitpool
> context** → `references/bitpool-context.md`; **Batched policy changes**, **Writing a queue row** and
> **Rules for the index** → `references/policy-queue.md`; **Step 0–11** → `references/workflow.md`.

## Audit mode (`/manage-drata-control audit`)

Sweeps the whole register for the structural defects that make individual entries indefensible —
null residuals, risks with no linked control, controls named as compensating controls but carrying
no evidence, review commitments with no driver, and shared load-bearing assumptions where one
false claim collapses several acceptances at once. Read
`references/hygiene-sweep.md` for the check list and the queries. It stores no baseline: measure
live, and take any period comparison from the previous session's `/drive-iso27001` worklog entry.
Its check 12, drift-prone text in durable records, runs the writing standard's audit sweep
(`durability-check.md` §5) — reported, never rewritten unasked. Its check 13 re-tests every `ICR`
ending against the audit-ready gate (Step 10) and reports only: a reopen or a close goes through
`/manage-drata-control DCF-xxx` for that control, with the user's yes one ticket at a time.

Report findings as a prioritised table. Fixes that are risk-field changes — null residuals, a
missing control link, a `treatmentDetails` correction — may be applied with `Drata_updateRisk`
after one approval block covering the batch. That block shows one durability check, with a `Field`
column naming the risk, over every `description` and `treatmentDetails` change in it — and a
`Profile` column where the batch also carries `IRT` text — and stages the change record for each
change on the ticket the golden rules name (core rule 6). Everything else is staged.

---

## Integration with other skills

- **`/manage-drata-risks`** — the reverse direction. This skill decides a control's position and
  writes a risk; that one takes an existing risk and verifies whether what is recorded in it is
  still true, then repairs it. Hand over when the question is "is this entry accurate?" rather than
  "what should we do about this control?"
- **`/drive-iso27001`** — finds which controls need attention and keeps the worklog. Hand back to it
  after a decision so the worklog and task queue reflect it.
- **`/drata-control-insights`** — the visual single-control snapshot. Offer it when the user wants
  to *see* a control's status rather than decide its treatment.
- **`/ask-drata`** — **the authority on the Drata connection**, and a prerequisite for this skill
  rather than an optional lookup. Rules 8–10 define the write model, the trap in each write verb,
  and which status flags cannot be trusted. Rules 1–5 explain why an empty result is usually the
  tool rather than the data — consult them before concluding any record doesn't exist. New
  connection-level findings go there, not here.
- **`/bitpool-writing-standard`** (section `bitpool-general`) — **the authority on what the words
  say** in Drata, `IRT` and `ICR`, and in the policy wording and docs pages this skill hands on. A
  prerequisite before drafting any of it, like `/ask-drata` before any Drata call. Load its
  `SKILL.md`, then the profile for the output's end location (the table in the golden rules); its
  durability check goes under every approval block that stages durable text. A defect in
  over-specific text is fixed there, as a calibration pair, not here as a new rule.
- **`/create-drata-test`** — if the decision is "mitigate and monitor it", a Custom Test is how the
  monitoring gets built.
- **`/create-devsecops-ticket`** — when the plan needs engineering work, that skill gives the
  devsecops team the control context.
- **`/bitpool-docs`** — the only route for non-policy documentation output. **Never** for ISMS
  policies.
- **`/isms-draft` / `/isms-prod`** — the only path that *writes* ISMS policy. This skill detects
  drift and drafts the fix (Step 8, and Step 3 outcomes 2 and 4 when our own document sets the wrong
  bar or declares a gap that no longer exists); those skills apply it. Hand over with the drafted
  wording and the contradicting evidence.
- **Documentation coverage** — [Documentation Index](documentation-index.md), a snapshot of
  which policies and procedures exist by domain. Use it to tell "no procedure documented" from "not
  checked". It cannot see a page added since the snapshot, so a domain with no entry is a candidate
  gap, never a confirmed absence.
- **The *reasoning* behind a policy clause** — not available to this skill. Read the policy's git
  history in `security-documentation`, then ask the user. See Step 8.
