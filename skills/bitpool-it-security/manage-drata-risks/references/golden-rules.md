# Manage Drata Risks — golden rules in full

The complete text of the rules summarised under *Load-bearing rules* in `SKILL.md`. Read it whole
before Phase 1. Drata tool names are the Drata MCP server's own; in Hermes they carry an
`mcp_<server>_` prefix — find the live names with `tool_search`.

- **Every enumerated item in `treatmentDetails` is a claim, and each one gets tested on its own.**
  Not the field as a whole — the items. For each, name where you verified it: a Drata evidence list,
  a live system observation, a Jira workflow you actually read, or the user saying so in this
  conversation. If none of those apply, it goes in the discrepancy table as **unverified**. Never
  hedge the wording to make an unverified claim survive.

- **A policy saying something happens is not evidence that it happens.** Policies are the record of
  what Bitpool intends, and this skill exists because intent and practice diverge. Worked failure,
  2026-08-21: the Separation of Duties Policy stated that code changes are peer-reviewed by someone
  other than the author, enforced by branch protection. That went into a risk as an operating
  preventive control. It does not happen, and `DCF-5` was `isReady: false` the whole time.

- **`flags.hasEvidence` and `flags.hasTicket` both lie.** Never read either as a signal. Resolve
  evidence with `Drata_listEvidence(control_code="DCF-xxx")` and ticket existence with a Jira query
  on the control code. Worked failure, 2026-08-24: `DCF-745` reported `hasEvidence: true` while
  `Drata_listEvidence` returned empty — the flag was pointing at an invalid external evidence id
  belonging to another control. **`/ask-drata` rule 10 is the authority.**

- **Never change a score unasked, and check the new score against the acceptance criteria before
  proposing it.** Raising a residual is not automatically the honest move: if it crosses the
  threshold in the Risk Acceptance Criteria, a risk that was legitimately retained becomes one the
  policy forbids retaining, which forces treatment the organisation may have already assessed as
  disproportionate. See `references/risk-scoring.md` §3 — this is the trap.

- **Residual means the position after treatment, not the position today.** Where the treatment is
  incomplete, the honest fix is usually to say so *in the text* and leave the score as the target,
  not to inflate the number. State which items the residual assumes — each planned one as its
  outcome, the condition on which it will be relied on, and its IRT pointer, never its progress
  (`/bitpool-writing-standard` rule 3). Progress lives on the ticket, so the sentence stays true as
  the items land.

- **Never rewrite before the gate.** No `Drata_updateRisk`, no Jira edit, no staged wording, until
  the discrepancies have been shown and answered.

- **What the entry and its tickets say is `/bitpool-writing-standard`'s job — this skill keeps no
  copy of its rules.** Three of this skill's outputs land in registered targets, each under a named
  writing profile:
  - **Drata risk register — writing profile Security Drata.** The risk's `title`, `description` and
    `treatmentDetails` are durable. Scores, `owners`, `control_ids` and `treatmentPlan` are
    structured fields, and prose never restates them.
  - **Jira `IRT` — writing profile Security Jira.** The RTP ticket's `summary` and `description` are
    durable. Comments are snapshots: the verification-record comment, the reason comments and the
    policy queue's detail comment are where the counts, account names, attestations and dates
    belong, and they stay specific.
  - **The policy queue page — writing profile Security Documentation.** A row, Status note or At
    promotion step on the page in `security-documentation` is register content: structured, and
    dated where it records an event.

  Before drafting any of them, load `/bitpool-writing-standard` — its `SKILL.md` for the target gate
  and the six core rules, then the named profile. Every approval block that stages durable text for
  Drata or `IRT` shows the durability check (`references/durability-check.md` §1 in that skill)
  directly under the staged text. Replacement policy wording handed to `/isms-draft` is ISMS Policy
  text, which that skill applies when it writes the draft. Everything else this skill produces — the
  discrepancy table and the Phase 4 summary — is a report to the user and outside the standard.

  **Requires `/bitpool-writing-standard` (section `bitpool-general`).** Before drafting text for the
  Drata risk register, `IRT` or the policy queue page, load it with `skill_view`. If it is not
  installed, **stop and ask the user once per chat** (`clarify`): *"`/bitpool-writing-standard`
  isn't installed, so the Security Drata, Security Jira and Security Documentation writing profiles
  can't be applied. Installing it
  (`hermes skills install Lolman-bot/Hermes-Repository-/skills/bitpool-general/bitpool-writing-standard --category bitpool`)
  is recommended. Proceed without it?"* Continue only on a yes, and do not ask again in the same chat.

- **Confirm the risk wording before writing it — every time.** Render the approval block in
  `references/drata-risk-fields.md` §3 as formatted markdown in the chat, never inside a fenced
  code block, with its durability check, and get an explicit yes. A fenced wall of monospace is
  exactly where an untrue claim survives unread. Invite the user to reject *by item number*.

- **Policy renewal lapse is not a finding.** Bitpool decision, 2026-08-24: the ISMS policy set is
  renewed once, in bulk, after the control review programme resolves. A `renewalDate` in the past
  and an `approvedAt` of `null` are the expected state of every policy between bulk events. Read
  policy content freely; say nothing about its dates.

- **Detect policy drift; never edit a policy.** Where the risk's contents contradict an ISMS
  document, hand the wording to `/isms-draft` and queue the change: claim its row on the policy
  queue page, post the detail comment on the policy queue ticket
  (`project = IRT AND labels = PolicyQueue`), then link the row — the procedure
  `/manage-drata-control` defines under *Writing a queue row*. Claim and link with `read_file` then
  `patch` only, never a `terminal` append or redirect, `sed`, a heredoc or a whole-file
  `write_file`, which skip the stale-read refusal that stops two runs taking the same number. **Nothing row-related goes in the
  ticket's description.** The comment carries the evidence that proves the policy wrong; the wording
  handed over states the requirement in categories (ISMS Policy profile §3.3). This skill never
  writes policy text to `security-documentation`; the queue page is the one file there it edits,
  and it leaves that edit for the user to commit and push.

- **Test for copied values, not only false ones — and repair a wrong specific by generalising it,
  never by re-syncing it.** Verification catches a claim that is false; `/bitpool-writing-standard`
  rule 3 catches one that is true today and will not stay true. Both are discrepancies. Any value
  copied from a system of record — a count, a person, a mailbox, an account name, a configuration
  value, a product, a policy-owned number, another record's content — is flagged
  `OVER-SPECIFIC / DUPLICATED VALUE` at the gate even while it is still accurate. Where a verified
  specific turns out to be wrong, the repair removes it and points at its home: correcting "five
  accounts" to "seven" only resets the clock. What Phase 1 measured is not lost — it goes in the
  dated verification-record comment on the RTP ticket, or is staged for the user where the risk has
  none (`references/drata-risk-fields.md` §3).
  Dated verifications and dated counts follow the standard's rule 4: the latest anchored event may
  stay where the entry's claim rests on it, and **a date added to a count does not make it
  durable**.

- **One risk per run.** Register-wide sweeps are `/manage-drata-control audit`.

- **Read `/ask-drata` before any Drata call.** It is the authority on the connection — which write
  verbs exist, the trap in each, and which status flags cannot be trusted. New connection-level
  findings go there, not here.
