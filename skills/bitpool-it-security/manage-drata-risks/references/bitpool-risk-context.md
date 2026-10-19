# Manage Drata Risks — Bitpool context

Stable configuration this skill relies on: the register, its enums and scoring, the governing
policy, where risk treatment plans and their dates live, and the 2026-08-24 decisions that shape
what is true. Read it at the start of every run.

**Never hardcode counts or statuses here or in a session summary.** Register totals, treatment
splits and evidence gaps change continuously and are one MCP call away — read them live every run.
What follows is stable configuration.

- **Risk register:** id `1`, name `Risk Management`.
- **`treatmentPlan` enum:** `UNTREATED` · `ACCEPT` · `TRANSFER` · `AVOID` · `MITIGATE`.
- **Scoring:** `impact` 1–5 × `likelihood` 1–5 = `score` 1–25, with a parallel
  `residualImpact` / `residualLikelihood` / `residualScore` triplet.
- **Governing policy:** `Risk Assessment Policy`, Drata policy id `17`. Resolve live with
  `Drata_listPolicies(name="risk")`. Read its **content** — the scales and the acceptable level of
  risk. Ignore its dates.
- **Risk ID prefixes observed:** `SD-`, `CR-`, `AI-`, `IN-`.
- **Risk treatment plans live in Jira `IRT`** — ISO27001 Plans, project id `13535`.
  A risk's RTP is the IRT ticket naming it; find it with
  `project = IRT AND text ~ "<riskId>"`. Dates live there and nowhere else — Drata's
  `anticipatedCompletionDate` is deliberately left blank, and Drata has **no date-based trigger**
  on it (confirmed with Drata support 2026-08-18).

  **And since 2026-09-15, most IRT tickets carry no date yet either.** They are created with an empty
  `duedate` while the `ICR` control review programme runs, and every date is set together in one
  prioritisation pass across the whole board — tracked by the standing `IRT prioritisation pass`
  ticket (`project = IRT AND labels = PrioritisationPass`), whose own `duedate` is the pass's date;
  read it there. The convention itself belongs to `/manage-drata-control`
  (`references/irt-tickets.md` §1); that skill owns it, this one only reads its output.

  **This skill never sets, changes or clears a `duedate`.** And it never reports the **presence or
  absence** of one as a discrepancy — both are normal, and there is no reliable way here to tell a
  legitimate pre-deferral or post-pass date from a mistake, since `created` is not in the capture list
  and the pass has no recorded run date.

  **One narrow exception, which is a different defect entirely:** a **populated** `duedate` that
  contradicts the controlled document it should have come from is still reported. That is
  mirror-inheritance — the failure that gave `IRT-1` a date six months after a wiki sync while the
  controlled document said "end 2024" — and it is about where a date came *from*, not about whether
  one exists. Report it; never fix it here. What this skill still verifies is everything around it: that the ticket exists, that it
  names the right risk, that its description names no person where Security Jira puts a role (the
  person is the assignee, and the risk owner is Drata's `owners`), and that its `Date constraint:`
  line matches the controlled document it quotes.
- **`CSIP`, `ICR` and `CYB` are read-only from this skill**, and are never cross-referenced by key.
  Reference controls by `DCF-xxx`, which is the durable handle. That is why this skill's snapshot
  home — the verification record, and the record of what changed in the risk — is a comment on the
  RTP ticket in `IRT`; this skill never writes an `ICR` review comment. Where the risk has no RTP
  ticket, the record is staged for the user to file on the linked control's `ICR` review ticket,
  and the approval block says so (`references/drata-risk-fields.md` §3).
- **Bitpool decisions of 2026-08-24 that shape what is true:** no `reviewers` value is set on any
  risk entry, and Drata's control approval function is not used. Clause 6.1.3(f) requires the
  *risk owner's* approval, not a second party's, so an empty `reviewers` field is correct and is
  **not** a discrepancy. Do not raise it as one.
- **Never set `reviewers` on a risk, and clear one if you find it set.** An empty field is correct;
  a populated one is drift. Clearing takes an explicit empty list **with `treatment_plan` passed on
  the same call**, or it is silently dropped — read the returned array back. Treatment text must
  never claim a reviewer exists. Governing rule, drift handling and the `DCF-16` reasoning:
  `/manage-drata-control` `references/drata-fields.md` §7.
