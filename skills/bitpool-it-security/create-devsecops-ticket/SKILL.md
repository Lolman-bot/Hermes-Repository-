---
name: create-devsecops-ticket
description: "Use when giving devsecops ISO 27001 context on a ticket."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, iso27001, drata, jira, devsecops, csip, aws, compliance]
    category: bitpool
    related_skills: [ask-drata, bitpool-writing-standard, aws-context, aws-query, drive-iso27001, drata-control-insights, update-devsecops-ticket, describe-dcf-jira-ticket]
---

# Create DevSecOps Ticket

Takes an existing (or newly described) piece of engineering/infrastructure work and gives the devsecops team the ISO 27001 compliance angle: which Drata controls the work touches, how (not just topical overlap), and where to look — Drata, GitBook and each control's CSIP tracking ticket. **Default action is editing the source ticket's own description in place** — appending a clearly delimited section, never destroying what's already there. Only when there's no source ticket at all does this fall back to creating a new standalone Task, and it never creates formal Jira issue-links.

The output is deliberately high-level; it's a triage handoff, not a worked solution. It confirms the real reason for the work, grounds infrastructure claims in live read-only AWS state, stages the exact text for approval, and once the write lands asks separately whether to move the starting CSIP ticket to In Progress.

## When to Use

- **Only when the user invokes `/create-devsecops-ticket`** — with an OP/BT ticket key, a starting CSIP ticket ("create an OP task for CSIP-659"), or a description of new work.
- Do NOT activate on any natural-language phrase or identifier match. These are anti-triggers, not triggers: "create a devsecops ticket", "raise a security ticket", a bare DCF/CSIP/OP/BT key, "does this relate to ISO27001", "what controls does this touch".

Don't use for:
- Posting meeting decisions as comments on existing OP tickets: `/update-devsecops-ticket`.
- Writing the control explainer on a CSIP DCF ticket: `/describe-dcf-jira-ticket`.
- Driving the ISO 27001 programme or CSIP compliance work: `/drive-iso27001`.
- Seeing a control's status: `/drata-control-insights`.

## Prerequisites

- **Atlassian (Jira) MCP server** and **Drata MCP server** added to Hermes (`hermes mcp add ...` or the `manage_connections` tool). The workflow names their tools by their connector names (`getJiraIssue`, `editJiraIssue`, `createJiraIssue`, `transitionJiraIssue`, `addCommentToJiraIssue`, `Drata_searchControls`, ...); if the names differ on this install, find them with `tool_search`.
- **`/ask-drata`** for connection-level Drata behaviour — this skill leans on it directly and doesn't re-derive it.
- **`/aws-context` + `/aws-query`** for any live AWS check (read-only).
- **`/bitpool-writing-standard`** (section `bitpool-general`) before drafting a Step 4e CSIP ticket — rule 13.

## Procedure

**Check rule 1 before drafting anything for approval** — it is the single highest-value check in the whole workflow. Read `references/devsecops-ticket-workflow.md` in full before resolving anything; it holds the hardcoded Bitpool config (Jira cloud ID, default assignees, Drata link pattern, CSIP transition ids) — use it before building any payload. Read the whole file you reach for; skimming is how a threshold or a flag gets missed.

1. **Resolve the source ticket** with `getJiraIssue`, and record the *starting* CSIP ticket and its current status if the run began from one. Done when the source ticket (or "no ticket — new work") and the starting CSIP key + status are noted.
2. **Decide ISO 27001 relevance** — auto-detect first; ask only when genuinely ambiguous. A directive prompt does not end the workflow here. Done when relevance is decided (or the skill has stopped on an obviously unrelated ticket).
3. **Understand what's actually going on.** 3a confirm the underlying reason (ask with `clarify` if not obvious); 3b research the action (`web_search` only for niche tech); 3c check live AWS state via `/aws-context` + `/aws-query` using `references/aws-evidence-map.md` when infrastructure-shaped; 3d on a brand-new ticket, ask "just do it" vs "two-part time quote" with `clarify`. Done when the why, the technical shape and the observed AWS state are established.
4. **Map to real Drata controls.** 4a shortlist codes by searching `references/drata-controls-register.md` with `search_files` (don't read it whole); 4b confirm against live Drata records and build the deep links; 4c one combined JQL `project = CSIP AND (text ~ "DCF-xx" OR ...)` for tracking tickets; 4e put each gap to the user with `clarify` (`multi_select`, ≤ 4 choices per question) and create approved CSIP tickets. Done when every shortlisted code has a live Drata link and a CSIP ticket or an explicit user decision.
5. **Draft the `## DevSecOps / ISO 27001 context` section** — one consolidated section, not one per control. Done when the section has a real controls table with DCF, Drata and CSIP links.
6. **Decide where it goes, show the exact text, get a yes.** Re-check the rule 1 gate. 6a append under the existing description, verbatim; 6b (no ticket) Background + Task + the section. Render as real markdown, never fenced. Done when the user has said yes to this exact text.
7. **Write it** — `editJiraIssue` on `description` only (6a) or `createJiraIssue` (6b). Never `createIssueLink`. Done when the write is confirmed.
8. **(7b) Offer the starting CSIP transition** — only if a starting CSIP ticket exists and the write landed: a separate `clarify` question carrying its current status, then transition id `31` plus the comment on a yes. Done when the user has answered and the outcome is known.
9. **Hand back** — the ticket URL, a one-line summary, and the 7b outcome stated. Done when no status write is left unstated.

## Load-bearing rules

Restated here because each one has already caused a real, documented failure.

1. **Never present a draft for approval without the `## DevSecOps / ISO 27001 context` section already attached.** Steps 4 and 5 are not optional, even when the user's phrasing is a directive description of the engineering ticket itself. **Confirmed twice independently** — a request phrased as "create a task that does X" reads as license to draft the engineering work and stop, skipping the GitBook register search, `Drata_searchControls`, and the CSIP JQL lookup entirely. **Before drafting, check: have the control-mapping steps actually run this session?** If not, stop and run them.
2. **The DCF code is the only reliable identifier — match and create by it, never by control name text.** CSIP titles drift: typos, abbreviations, or the code missing entirely (~26 tickets were found on 2026-08-07 titled with just the bare control name). The JQL `text ~ "DCF-xxx"` is the *only* trustworthy existence check, and every ticket this skill creates or renames must contain the bare `DCF-xxx` code in its summary.
3. **A confirmed gap is a decision point, not a finding.** Surface each gap by DCF code and ask whether to create the CSIP tracking ticket now. Don't silently write "no CSIP ticket yet — gap" and move on.
4. **Ground infrastructure action items in live AWS state — never assume a gap.** An early draft once assumed a region-restricting SCP needed creating when Bitpool already had one; the real task was reconciliation, not creation. A wrong assumption about current state produces a wrong task list no matter how good the control mapping is.
5. **If a ticket's underlying reason isn't obvious from its own text, ask — don't guess.** A wrong "why" produces a wrong mapping however carefully the mapping step runs.
6. **On a brand-new ticket, ask "just do it" vs. "two-part time quote" every time.** Never decide it alone — it depends on cost and opportunity cost this skill has no visibility into.
7. **Drata is READ-ONLY.** Never call `Drata_updateControl` / `Drata_createControl` / etc.
8. **Never create a formal Jira issue link.** Don't call `createIssueLink` — every cross-reference is a plain markdown hyperlink in the description text.
9. **Edit in place beats creating a new ticket**, and never at the cost of existing content. One consolidated section per ticket, never one entry per control.
10. **Never write anything without staged approval**, and **render the preview as real markdown**, not inside a fenced code block — the user needs to see what the ticket will look like.
11. **On the engineering ticket, only the `description` field is ever written** — never `status`, `assignee`, `labels` or anything else. **The one exception in the whole skill is the *starting* CSIP ticket** (Step 7b): once the write has landed, offer to move it to `In Progress` and comment the new ticket onto it.
12. **The starting-CSIP transition is a separate question, asked after the write — never inferred, never silent, never folded into the Step 6 approval.** Two reasons it must be asked: a run can touch several CSIP tickets (the starting one, ones found at Step 4c, ones created at Step 4e) and only the first is ever a candidate; and every CSIP transition is **global**, so `In Progress` is reachable from `Done` too. There is deliberately no status guard — the ask *is* the guard, which only works if the ticket's current status appears in the question.
13. **A CSIP ticket created at Step 4e is durable text in a registered target — apply `/bitpool-writing-standard`.** Its `summary` and `description` are in that standard's register under the **Security Jira** writing profile (§3.2, CSIP work tasks). Load it with `skill_view` before drafting them — its `SKILL.md`, then its `profile-security-jira.md` reference — and show the durability check (its `durability-check.md` reference, §1) in the Step 4e approval, directly under the staged text. The standard decides what the words say; this skill doesn't restate it. The engineering ticket (OP, BT) is outside the register, and the comments this skill posts on CSIP tickets are snapshots, so neither gets a check.

    **Requires `/bitpool-writing-standard`.** Before drafting text for the Step 4e CSIP ticket's summary and description, load it. If it is not installed, **stop and tell the user once per chat**: *"`/bitpool-writing-standard` isn't installed, so the Security Jira writing profile can't be applied. Installing it from the Bitpool Hermes skills repo (section `bitpool-general`) is recommended. Proceed without it?"* Continue only on a yes, and do not ask again in the same chat.

## Pitfalls

- **Drafting the engineering work and stopping** when the prompt is directive ("create a task that does X") — rule 1; the controls table must be there.
- **Mapping off the literal ticket text** — OP-83 read as webhook mechanics; the real driver was data walking out with departing staff on individually-owned accounts.
- **Treating one page of `Drata_searchControls` as proof a code is absent** — page in list mode until `cursor` is `null` (`/ask-drata`).
- **Trusting the register as live truth** — it's a 2026-08-07 snapshot: it shortlists, the live record adjudicates.
- **Reading the 145 KB register whole** — search it for domain keywords instead.
- **Transitioning a CSIP ticket that wasn't the starting one**, or folding the transition into the Step 6 approval.
- **Inlining AWS CLI commands, profiles or account IDs** — `/aws-query` owns call construction.

## Verification

- The approved text contained a `## DevSecOps / ISO 27001 context` section with real DCF, Drata and CSIP links.
- Existing description content is preserved verbatim above the appended section.
- Only `description` was written on the engineering ticket; no issue links; no Drata writes.
- Every created CSIP ticket summary contains its bare `DCF-xxx` code and passed the durability check.
- The hand-back states the Step 7b outcome (moved, with from → to, or left as-is).

## Reference files

Read the file itself — the table is an index, not a substitute.

| File | Covers |
|---|---|
| `references/devsecops-ticket-workflow.md` | Giving devsecops the ISO 27001 control context for a piece of engineering work — the hardcoded Bitpool config, the golden rules, and the eight-step workflow from resolving the source ticket to handing back. |
| `references/aws-evidence-map.md` | Which read-only AWS checks evidence which control domain, the relevance test, per-control call budgets, and the risk/cost/effort advisory shape. Shared by `/drive-iso27001` and `/drata-control-insights`. |
| `references/drata-controls-register.md` | Every enabled Drata control — DCF code, numeric Drata ID, name, description, monitoring-test flag. Search it to shortlist candidates; it's a 2026-08-07 snapshot, so confirm against the live record. |

Config, golden rules, workflow steps → edit `references/devsecops-ticket-workflow.md`. Connection-level Drata behaviour → `/ask-drata`. AWS mappings → `references/aws-evidence-map.md`.
