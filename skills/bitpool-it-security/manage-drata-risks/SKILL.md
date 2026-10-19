---
name: manage-drata-risks
description: "Use when verifying or re-scoring one Drata risk entry."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, drata, risk-register, jira, iso27001, compliance, security]
    category: bitpool
    related_skills: [ask-drata, manage-drata-control, bitpool-writing-standard, drive-iso27001, isms-draft, isms-prod, create-drata-test, drata-control-insights]
---

# Manage Drata Risks

Takes one Drata risk and asks the only question that matters about a register entry: **is what we wrote here still true?** It reads the risk and its treatment plan ticket, tests every claim in them — each compensating control, score, date and pointer — against Drata evidence, Jira, live systems or the user, reports the discrepancies as a gate, and only then offers to rewrite the entry and reassess the inherent and residual scores.

A risk register decays quietly. A control that was "planned" stayed planned, a compensating control was never configured, a policy was drafted but never approved, and nobody re-read the entry. Every sentence stays individually plausible while the entry as a whole becomes a misrepresentation.

**The inverse of `/manage-drata-control`.** That skill starts from a control with an unresolved position and decides what to do, creating a risk as output. This one starts from a risk that already exists and audits it. Use that one to *decide*; use this one to *verify*.

## When to Use

- The user types `/manage-drata-risks`, or `/manage-drata-risks CR-05` for one risk.
- They ask whether a risk entry is accurate or still true, to review or re-score a risk, or to check a treatment plan against what actually operates.

Don't use for:
- Deciding a control's position: `/manage-drata-control`.
- Program-wide driving or transcripts: `/drive-iso27001`. Register-wide sweeps: `/manage-drata-control audit`.
- A control status visual: `/drata-control-insights`. Drata connection quirks: `/ask-drata`.
- ISMS policy authoring: `/isms-draft`, `/isms-prod` — never this skill.

## Prerequisites

- **The Drata MCP server** and **the Atlassian (Jira) MCP server** added to Hermes (`hermes mcp add …` or `manage_connections`). Tool names here are the servers' own (`Drata_searchRisks`, `Drata_updateRisk`, …); in Hermes they carry an `mcp_<server>_` prefix — find them with `tool_search`.
- **`/ask-drata` loaded before any Drata call** — the authority on which write verbs exist, the trap in each, which flags lie, and the write-policy table that grants this skill `Drata_updateRisk` only.
- `/bitpool-writing-standard` (section `bitpool-general`) before any staged wording — see rule 9.
- Read `references/bitpool-risk-context.md` (register id, enums, scoring, governing policy, where RTP dates live) and `references/golden-rules.md` in full at the start of every run.

## The three phases, and the gate between them

This ordering is the skill. Do not collapse it.

| Phase | What happens | Ends with |
|---|---|---|
| **1 — Verify** | Read the risk and its RTP ticket. Test every claim in both. Name a source for each, or mark it unverifiable. | A discrepancy table |
| **2 — Gate** | Put the discrepancies to the user. **Change nothing.** | The user's answers |
| **3 — Repair** | Offer to rewrite the risk and reassess the scores. Approval block, then write. | A verified entry |

**Phase 2 is a hard stop.** Only the user can tell you whether an asserted control actually operates. Drata will not, because Drata records what someone typed. A skill that verifies and repairs in one pass launders its own guesses into a controlled record.

## Procedure

Full steps: `references/risk-workflow.md`. Read it whole with `read_file`.

1. **Resolve the risk** with `Drata_searchRisks(q=<riskId>, expand=[…])`; never `query` mode. Done when every field is captured.
2. **Resolve its RTP** in Jira `IRT` (`project = IRT AND text ~ "<riskId>"`), its comments and subtasks; check `CSIP, ICR, IRT, CYB` for duplicates; read the latest `ICR` outcome comment per linked control. Done when every prior verification record is in hand.
3. **Read the governing policy's content** (scales, acceptable level — never its dates) and **each linked control's real evidence list**, not the flag. Done when each control has a list result, not a flag reading.
4. **Test every claim** per `references/risk-verification.md` §1–§4 and build the §5 discrepancy table. Done when every claim has a named source or is marked unverified.
5. **Gate** — put the table to the user with a recommended disposition per row (**operating**, **planned**, **accepted exposure**, **generalise**, **delete**); use `clarify` where choices fit. Apply nothing. Empty table → say so in one line and stop. Done when the user has answered.
6. **Repair**, only after the gate: statement (`references/risk-verification.md` §6) → scores (`references/risk-scoring.md`, residual triplet always set) → `treatmentDetails` → durability check → approval block (`references/drata-risk-fields.md` §3) → explicit yes. Done when the user has said yes to the rendered block.
7. **Write** with `Drata_updateRisk` and **quote what the API returned**, not what you sent. Done when the returned owners, scores and text are compared with the request.
8. **Close the loop**: verification-record comment on the RTP ticket (or staged for the user on the `ICR` ticket where there is none), RTP corrections, policy queue row for any drift, evidence still to upload. Done when each is written or staged and linked.
9. **Summarise** (Phase 4): decision, what was written, what the returned record says, open discrepancies, RTP changes, queue rows, what stays unverified; reconcile every date. Done when each place the commitment appears agrees.

## Load-bearing rules

Condensed — the full text with worked failures is `references/golden-rules.md`.

1. **Every enumerated item in `treatmentDetails` is a claim, tested on its own**, with a named source (Drata evidence list, live observation, a Jira workflow you read, or the user in this conversation). Otherwise it is **unverified** — never hedge the wording to make it survive.
2. **A policy saying something happens is not evidence that it happens.**
3. **`flags.hasEvidence` and `flags.hasTicket` both lie.** Resolve evidence with `Drata_listEvidence(control_code=…)` and tickets with a Jira query. `/ask-drata` rule 10 is the authority.
4. **Never change a score unasked**, and check a new score against the Risk Acceptance Criteria first — the threshold trap (`references/risk-scoring.md` §3).
5. **Residual means the position after treatment**, not today. Say incompleteness in the text; state which items the residual assumes, by outcome and IRT pointer, never progress.
6. **Never rewrite before the gate.** No `Drata_updateRisk`, no Jira edit, no staged wording until the discrepancies are answered.
7. **Confirm the risk wording before writing it — every time.** Render the approval block as formatted markdown in the chat, never in a fenced code block, with its durability check; get an explicit yes; invite rejection by item number.
8. **Write posture:** `Drata_updateRisk` only, per `/ask-drata`'s write-policy table. Never create risks. **Never set `reviewers`, and clear one if found** — explicit empty list with `treatment_plan` on the same call, then read it back.
9. **Wording is `/bitpool-writing-standard`'s** — Security Drata (risk `title`, `description`, `treatmentDetails`), Security Jira (`IRT` summary/description), Security Documentation (policy queue page). If it isn't installed, ask once per chat (`clarify`) whether to proceed — exact wording in `references/golden-rules.md`.
10. **Policy renewal lapse is not a finding.** Past `renewalDate` and `approvedAt: null` are expected between bulk renewals.
11. **Detect policy drift; never edit a policy.** Hand wording to `/isms-draft`; claim the queue row with `read_file` then `patch` only — never a `terminal` append, `sed`, heredoc or whole-file `write_file`; leave the commit and push to the user.
12. **Test for copied values, not only false ones** — flag `OVER-SPECIFIC / DUPLICATED VALUE`; repair a wrong specific by generalising it, never re-syncing it.
13. **Never set, change or clear an IRT `duedate`**, and never report its presence or absence — only a populated date contradicting its controlled document (`references/bitpool-risk-context.md`).
14. **`CSIP`, `ICR` and `CYB` are read-only**; reference controls by `DCF-xxx`. **One risk per run.**

## Pitfalls

- **Promoting an unverified claim on the user's silence.** Anything they cannot confirm stays unverified.
- **Manufacturing findings.** A skill that reports drift every run trains people to ignore it.
- **Inflating a residual** to make an incomplete treatment look honest — it can cross the acceptance threshold and force treatment already judged disproportionate.
- **Reporting what you sent.** Non-admin owners are dropped silently; quote the returned record.
- **Hardcoding counts or statuses** in a summary — register totals change; read them live.
- **Reporting a policy as updated** — this skill only hands drafts to `/isms-draft`.

## Verification

- The discrepancy table was shown and answered before any write or staged wording.
- Every write was approved in a rendered block and its returned record quoted.
- `reviewers` is empty on the returned record; no `duedate` was touched.
- Every date the commitment appears in agrees, and what remains unverified is listed.

## Reference files

Read the file itself — the table is an index, not a substitute.

| File | Covers |
|---|---|
| `references/golden-rules.md` | The full golden rules with their worked failures — claims, flags, scores, residuals, the gate, the writing profiles, policy drift, copied values. |
| `references/risk-workflow.md` | Phases 1–4 step by step: resolving the risk and RTP, the gate, the repair sequence, the write and closing the loop, the summary. |
| `references/bitpool-risk-context.md` | Stable Bitpool configuration: register id, `treatmentPlan` enum, scoring, governing policy, risk ID prefixes, IRT dates and the prioritisation pass, read-only projects, the 2026-08-24 reviewer and approval decisions. |
| `references/risk-verification.md` | Phase 1 in full: the claim classes and how each is tested, the source hierarchy, the four-bucket `treatmentDetails` structure and what it exposes, RTP/IRT checks, date reconciliation, and the discrepancy table format used at the gate. |
| `references/risk-scoring.md` | Bitpool's impact and likelihood scales, the risk rating bands, the Risk Acceptance Criteria and how each is written into an entry, what `residual` actually means, and the threshold trap that makes a naive re-score harmful. |
| `references/drata-risk-fields.md` | The verified risk field map, the write model and its per-field traps, the approval block with its durability check, the verification record and where Phase 1's specifics go, and Bitpool's register conventions. |

Related: `/manage-drata-control` (forward direction — hand back when the control position was never decided), `/drive-iso27001` (finds what needs attention), `/isms-draft` / `/isms-prod` (the only path that writes ISMS policy), `/create-drata-test` (monitoring for a repaired risk's mitigation).
