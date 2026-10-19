---
name: describe-dcf-jira-ticket
description: "Use when writing the explainer on a CSIP DCF Jira ticket."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, iso27001, drata, jira, csip, compliance, security]
    category: bitpool
    related_skills: [bitpool-writing-standard, ask-drata, drata-control-insights, drive-iso27001, manage-drata-control, create-devsecops-ticket, create-drata-test, aws-context, aws-query, isms-draft, isms-prod, bitpool-docs]
---

# Describe DCF Jira Ticket

Takes one Drata-generated CSIP ticket — the `Drata | Bitpool | DCF-xxx | [Control Name]` parents, which arrive carrying nothing but Drata's stock one-line control text — and replaces that stub with an explainer someone can act on: **What it is / What it actually requires / In practice for Bitpool / Evidence Drata will look for**. It reads the Drata control READ-ONLY, writes durable requirements rather than status, and stages the text for approval before writing `description`, preserving human-authored content. The same approval may offer a status transition (default `To Discuss`), made only on an explicit yes.

This skill **writes prose to a Jira description**. It does not decide treatment (`/manage-drata-control`), render status (`/drata-control-insights`), drive the program (`/drive-iso27001`), or build monitoring (`/create-drata-test`). **One ticket per run** — for batches, run it per ticket; the research step is the value, and it doesn't survive being rushed across twenty controls.

## When to Use

- **Only when the user invokes `/describe-dcf-jira-ticket`**, with a CSIP ticket URL or key.
- Do NOT activate on any natural-language phrase or identifier match. These are anti-triggers, not triggers: a bare DCF or CSIP key, a pasted Jira URL, "write a description for this control", "explain this control", "document this control", "Drata", "compliance".

Don't use for:
- Deciding what to do about an unmet control: `/manage-drata-control`.
- Seeing a control's status: `/drata-control-insights`.
- Finding which controls need attention: `/drive-iso27001`.
- Carrying engineering work to devsecops: `/create-devsecops-ticket`.
- Building a Custom Test for monitoring: `/create-drata-test`.
- Writing ISMS policy: `/isms-draft` / `/isms-prod`.

## Prerequisites

- **Atlassian (Jira) MCP server** and **Drata MCP server** added to Hermes (`hermes mcp add ...` or the `manage_connections` tool). This skill names their tools by their connector names (`getJiraIssue`, `editJiraIssue`, `Drata_searchControls`, ...); if the names differ, find them with `tool_search`.
- **`/bitpool-writing-standard`** (section `bitpool-general` of this repo) — governs the text written (rule 11).
- **AWS is optional and always asked for first** — via `/aws-context` + `/aws-query` only.

## Procedure

Read all four reference files before drafting: `references/workflow.md` (full step detail and Bitpool context), `references/description-format.md`, `references/golden-examples.md`, `references/documentation-index.md`. Read the whole file you reach for.

1. **Resolve the ticket and read what's already there.** `getJiraIssue` with summary, description, status, labels, assignee, reporter, updated, comment (markdown). Extract `DCF-xxx` from the summary — none → stop and ask (rule 4). Classify the existing description as **stub / human / already-described**, and read the comments, including the parent's when a sub-task owns the question. Done when the DCF code, the description class and any comment-settled facts are noted.
2. **Pull the real Drata control record (READ-ONLY).** `Drata_searchControls` for the code — keep `code`, `name`, `description`, `activity`, `flags`, `frameworkTags`, `owners`, `updatedAt` verbatim and note the read date; then `Drata_listRequirements` (`framework_tag=["ISO27001"]`, `expand=["controls"]`) for clause vs Annex A (rule 8). Empty result → consult `/ask-drata` and paginate in list mode. Done when you hold a verbatim record; never draft against one you couldn't read.
3. **Classify the shape** — automated infrastructure / tooling-endpoint / governance-clause (`references/description-format.md`). Done when the shape is named.
4. **Bounded research.** Check `references/documentation-index.md`, the ticket's comments, and sibling DCFs in Jira. Research only what changes what someone would *do*. Done when every Bitpool fact is either verified or phrased as a requirement.
5. **Ground it in live AWS state — ask first.** Apply the relevance test; if relevant, name the checks and ask with `clarify`. On yes, `/aws-context` once, then `/aws-query` (≤ 8 calls). Observations go in the report and the optional dated comment, never the description. Done when AWS is either queried with approval or explicitly out of scope.
6. **Draft in the house format** — the four sections in order, per `references/description-format.md`, checked against `references/golden-examples.md`, with the Security Jira profile applied (rule 11). Done when the draft has all four sections and no current-state claims.
7. **Choose the write mode** — stub → replace; human → preserve in full at the top, explainer below; already-described → offer to refresh in place. Done when the mode and its reason are stated.
8. **Stage, approve, write.** Show the description as rendered markdown (not fenced), the durability check table directly under it, then what is verified / unverified / observed. Stage the optional "Observations — `<YYYY-MM-DD>`" comment if there are observations or a correction reason. Resolve the transition id with `getTransitionsForJiraIssue` first. Ask everything in **one** `clarify` question and accept a yes to any part alone. On approval: `editJiraIssue` (description), then `addCommentToJiraIssue` only if approved, then `transitionJiraIssue` only if approved. Done when each approved action has landed and nothing unapproved has.
9. **Hand back.** Report what was written, whether the comment was posted and whether the ticket moved (and where); then what's still open, routed to `/bitpool-docs`, `/create-devsecops-ticket`, `/manage-drata-control` or `/create-drata-test`. Offer `/drata-control-insights`. Done when the status outcome is explicitly stated; don't re-summarise the description.

## Load-bearing rules

1. **Drata is READ-ONLY.** Never call `Drata_updateControl`, `Drata_createControl`, `Drata_updateEvidence`, `Drata_createEvidence`, or any other Drata write tool. This skill reads Drata and writes only to Jira, with approval. Matches `/drive-iso27001` and `/manage-drata-control`.
2. **Quote Drata verbatim, never paraphrased.** The blockquote in *What it actually requires* is the control's own wording, character-for-character from `description` (or `activity` when the evidence guidance is the more useful text). If you paraphrase it, the reader loses the one sentence an auditor will actually hold you to. Its lead-in names the source and the date you read it — *"Per Drata's description, as read `<YYYY-MM-DD>`:"* — so the quote reads as what Drata said then, not what it says now (`references/description-format.md` §2).
3. **Never assert an unverified Bitpool fact — and verified is not enough.** Write what the control *requires*, not what Bitpool *currently does*. "S3 Block Public Access is enabled" is a claim; "Block Public Access enabled at account level" as a row in a *What to demonstrate* table is a requirement. The second is always safe, the first almost never is. A wrong status claim sitting in a Jira description is worse than no description, because it stops anyone checking. A fact you *have* verified — observed via `/aws-query` this session, settled in a ticket comment, or told by the user — must also be durable under `/bitpool-writing-standard` (rule 11) before it goes in the description. A current-state value, however well verified, goes in the report to the user instead (step 5); a settled fact goes in as the requirement it implies, pointing at where it was settled (step 1).
4. **The DCF code is the only reliable identifier.** Resolve it from the ticket title, not from the control name — CSIP titles drift, and roughly 26 tickets were found in August 2026 carrying only a bare control name. If the title has no `DCF-xxx`, ask; never infer the control from the name.
5. **Never write without staged approval,** and render the preview as real markdown rather than inside a fenced code block — the user needs to see the ticket as it will look.
6. **Only the `description` field is ever written without asking.** Never `assignee`, never `labels` — those are the human's call and other skills' business. A `status` transition may be *offered*, but only inside the same approval question as the description write (step 8), and only ever performed on an explicit yes. Never transition a ticket as a side effect of writing to it. **One dated comment may also be offered, in that same question** — on the same CSIP ticket only, holding this run's AWS observations and, where a refresh corrects a wrong statement, the reason for the correction (step 8). It is posted only on an explicit yes; a yes to the description is not a yes to the comment. It never comments on any other ticket.
7. **Never destroy human-authored content.** Replacing Drata's stock stub is the whole point; overwriting someone's notes is data loss. See the write-mode decision in `references/description-format.md`.
8. **Mandatory clause and Annex A are different species.** Resolve which via `Drata_listRequirements` — the discriminator is the `A.` prefix (`7.2` Competence is a clause; `A.7.2` Physical entry is Annex A). A clause gap is a **nonconformity requiring corrective action**, not a risk that can be accepted. Never write acceptance or risk-treatment language into a clause control's description.
9. **An AWS result is an observation, not evidence.** It shapes how the *In practice* section frames the requirement and tells the human what's worth attaching in Drata; the observation itself is reported to the user, not written into the description (step 5). It never satisfies a control by itself and is never a substitute for a Drata test.
10. **Never author or edit ISMS policy content.** Policies belong to `/isms-draft` and `/isms-prod`. Referencing a policy is fine; writing policy text into a Jira ticket is not.
11. **The explainer is durable text in a registered target — apply `/bitpool-writing-standard`.** The CSIP `description` this skill writes is in the standard's register under the **Security Jira** writing profile (its §3.7, CSIP descriptions): a standing statement of what the control requires, read long after it was written. Before drafting it, load `/bitpool-writing-standard` with `skill_view` — its `SKILL.md` for the target gate and the six core rules, then its `profile-security-jira.md` reference — and show the durability check (its `durability-check.md` reference, §1) in the step 8 approval block, directly under the staged description. The standard decides what the words may say; this skill does not restate it. A status transition is a structured field and needs no check. The optional observations comment (rule 6) is a snapshot in the same target — specific by design, headed with its date, and not checked (Security Jira §3.5). Everything else it produces — the step 8 notes on what is verified, the step 9 hand-back — is chat to the user and out of the register: specifics are fine there, and no check is shown.

    **Requires `/bitpool-writing-standard`.** Before drafting text for the CSIP ticket description, load it. If it is not installed, **stop and tell the user once per chat**: *"`/bitpool-writing-standard` isn't installed, so the Security Jira writing profile can't be applied. Installing it from the Bitpool Hermes skills repo (section `bitpool-general`) is recommended. Proceed without it?"* Continue only on a yes, and do not ask again in the same chat.

## Pitfalls

- **Paraphrasing the Drata quote** — the auditor's sentence is lost; quote verbatim with the read date.
- **Writing current state into the description** ("X is enabled", a dated gap) — it reads as the control's position long after it changes, and `/drata-control-insights` reads this description. Observations go to the report and the optional comment.
- **Inferring the control from its name** when the title lacks `DCF-xxx`.
- **Missing the parent's comments** — comments don't propagate between parent and sub-task; an empty sub-task thread proves nothing.
- **Concluding a Drata record doesn't exist** off a search-mode `query` — use structured list mode and follow `cursor` to `null` (`/ask-drata`).
- **Hardcoding the `To Discuss` transition by name** — resolve the transition id; if it isn't offered, list what is and ask.
- **Appending a second explainer** on an already-described ticket instead of refreshing in place, or recording the refresh's history in the description.
- **Writing "no procedure exists"** off an absent entry in the dated documentation index.
- **Risk-acceptance language on a clause control** — a clause gap is a nonconformity.

## Verification

- The description's blockquote matches Drata's text character-for-character, with source and read date.
- The four sections are present, in order; no current-state values or comment-copied values in the description.
- The durability check table was shown under the staged description.
- Only approved actions landed: description, comment, transition each traced to an explicit yes.
- The hand-back states whether the ticket moved and where.
- No Drata write tool was called.

## Reference files

Read the file itself — the table is an index, not a substitute.

| File | Covers |
|---|---|
| `references/workflow.md` | Bitpool context (Jira site, CSIP linkage, labels, Drata query quirks) and the full nine-step workflow in detail. |
| `references/description-format.md` | The four-section skeleton, the three shape variants, the house voice rules, the write-mode decision, and what the description never contains. |
| `references/golden-examples.md` | Three production examples spanning the variants, adapted to the writing standard. |
| `references/documentation-index.md` | Which policies and procedures exist, by control domain, for the Step 4 research pass. A dated snapshot (its header gives the date): cite a page it lists, but never write "no procedure exists" off the back of an absent entry. |

Workflow steps and Bitpool context → `references/workflow.md`; format and voice → `references/description-format.md`.
