---
name: isms-prod
description: "Use when promoting an approved ISMS policy draft to prod."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, isms, iso27001, policy, security, drata, jira, pandoc]
    category: bitpool
    related_skills: [isms-draft, manage-drata-control, bitpool-writing-standard, bitpool-docs]
---

# isms-prod

Promotes an **approved Bitpool ISMS policy draft** into the controlled `isms` production repo and
records the change as **git history** — the commit message in the `isms` repo is the audit record.
Markdown is the source of truth; the `.docx` is **built** from it by a deterministic pandoc +
`docxtpl` toolchain. Everything is staged and the skill STOPS for approval before any commit or
Jira write.

## When to Use

- The user runs `/isms-prod`, or says "promote the [policy]", "publish the [policy] to prod" —
  naming the policy.
- The bulk promotion at the end of a control review programme (reads the policy queue first).

Don't use for:
- Drafting or editing policy text: use `/isms-draft`.
- Non-policy documentation: use `/bitpool-docs`.
- Anything not explicitly requested by name — never infer a promotion.

## Prerequisites

- Local checkouts of `security-documentation` and `isms`. On Bitpool machines both live under
  `C:\BitpoolDev\Github-Bitpool\`; locate them fresh, and ask with `clarify` if they aren't there.
  - **Source (draft):** `security-documentation/ISMS/ISMS - Draft/<policy-slug>.md`, or the same
    name under `ISMS/ISMS - Draft (New)/` — both are live draft folders; ask which holds the draft
    if both do.
  - **Target (prod):** `isms/<Policy Name>.md` + `isms/<Policy Name>.docx`.
- `pandoc` toolchain at `security-documentation/ISMS/_tools/md-to-docx.sh` (bash; run through WSL
  on Windows). The branded cover comes from `Templates/policy-template.docx` — re-theming means
  editing the template and rebuilding, never hand-editing a document.
- The Atlassian MCP server (for the `CYB` tickets) — find its tools with `tool_search`.

## Procedure

1. **Confirm an explicit, named request** (rule 1). Done when the user has named each policy to
   promote in this chat.
2. **Read the workflow** in `references/isms-policy-lifecycle.md` (the *Promotion* part) with
   `read_file`, and also `isms/_meta/commit-convention.md` and `isms/_meta/policy-change-banner.md`
   — those canonical copies win over the reference if they differ. Read the whole file you reach for.
   Done when all three are read this run.
3. **In a bulk promotion, read the policy queue first** — the page `compliance/isms-policy-queue.md`
   and the `IRT` ticket (`project = IRT AND labels = PolicyQueue`), as the reference describes.
   Done when every pending row for the policies in scope is listed.
4. **Identify the pair and diff draft vs production** (`git diff --no-index`). **List every image
   asset the change touches** (rule 5). Done when the diff and asset list are shown to the user.
5. **Draft the change-log commit message** from the draft's version-control table, in the
   commit-convention shape. Done when the message is presented.
6. **Update the production `.md`** and **build the `.docx`** with `md-to-docx.sh` via `terminal`
   (rule 4). For the **Privacy Policy**, also generate the public website extract. Retire a
   superseded supporting document from `isms/Documents/` only when the change replaces one. Done
   when both files are written and the build exited 0.
7. **Prompt the Drata Policy Center upload and capture the named approval** — approver name and
   effective date are agreed with the user, never invented. Done when the user confirms the upload
   and names the approver.
8. **Stage, then STOP** (rule 3): present the `git status`, commit message, `CYB` ticket draft(s)
   with a proposed due date and reasoning (rule 10). Done when the user gives an explicit yes.
9. **Commit the `.md` and `.docx` together** in the `isms` repo only (rules 2, 6). Done when
   `git log -1` shows the commit.
10. **Raise the `CYB` Task(s)** — after the commit lands — one per promoted policy, plus the Privacy
    Policy website-handoff sub-task where relevant (rule 9), from the templates in the reference.
    Done when each ticket key is reported.
11. **Hand the queue update back** as the reference describes, and **end with the warning banner**
    (rule 7) as the final element of the response. Done when the banner lists every touched policy.

## Load-bearing rules

Restated here because this skill changes a controlled ISO 27001 document.

1. **Only promote on explicit request, naming the policy.** Never infer.
2. **Git writes and commits happen ONLY in the `isms` repo.** Read the draft from
   `security-documentation`; never commit there from this skill. The one write outside git is the
   `CYB` ticket in rule 9.
3. **Never auto-commit.** Stage, present, and STOP for explicit approval — plus confirmation that the
   `.docx` is updated, Drata is uploaded, and the approver is captured.
4. **The `.docx` is built, never hand-edited.** Run `md-to-docx.sh` from
   `security-documentation/ISMS/_tools/` (in WSL on Windows). **Corrected 2026-08-25** — this rule
   previously said the CLI must never touch the `.docx` and that a human updated it in Word via the
   Claude add-in. That was wrong: the production `.docx` set in the `isms` repo was generated by this
   toolchain, verified by comparing style distribution, page headers and field structure against a
   freshly built copy. The old rule blocked the tooling that actually produces every published policy.
5. **List every image asset the change touches** at the diff step — both the draft's own
   `assets/<policy-slug>/` and the shared `ISMS - Draft/assets/common/`. Pandoc resolves them
   relative to the `.md`, so a moved asset silently drops out of the build.
6. **Commit the `.md` and `.docx` together.** That pair is the audit record.
7. **Every promotion ends with the warning banner** as the final element of the response — one
   banner, all touched policies listed. Canonical copy: `isms/_meta/policy-change-banner.md`.
8. **Never paste secrets or PII.** Reference locations only.
9. **Every promoted policy gets a `CYB` Jira Task recording that the Drata Policy Center upload is
   still outstanding.** Staged for approval like every other write, and created **after** the commit
   lands — so a ticket never exists for a promotion that didn't happen. Promoting the **Privacy
   Policy** additionally gets a sub-task handing the new content to the website team, because the
   ISMS document is the master and `bitpool.com/privacy` is a downstream copy (Bitpool decision,
   2026-08-25). Templates in `references/isms-policy-lifecycle.md`.
10. **Never invent a due date for the `CYB` ticket.** Propose one with your reasoning and get
    agreement, exactly as the approver name and effective date are agreed.

## Pitfalls

- **The commit is not the end of the promotion.** Drata still needs the upload and the Privacy
  Policy still needs the website team; both outlive the session, so both get a `CYB` ticket.
- **Creating the `CYB` ticket before the commit** — it would record a promotion that may not happen.
- **Committing in `security-documentation`** from this skill. Only `isms`.
- **A moved image** silently drops out of the pandoc build — check the asset list against the build.
- **Following the reference over `isms/_meta/`** when they differ; the `_meta` copies win.
- **Promoting per policy** outside the bulk round, or treating a lapsed `renewalDate` as a reason to.

## Verification

- `git -C <isms> log -1 --stat` shows the `.md` and `.docx` committed together, with the agreed message.
- `git -C <security-documentation> status` shows no commit made there by this run.
- Each promoted policy has a `CYB` Task (and the Privacy Policy its sub-task), created after the commit.
- The response ends with the banner listing every touched policy.

## Reference files

Read the file itself — the table is an index, not a substitute.

| File | Covers |
|---|---|
| `references/isms-policy-lifecycle.md` | The two-stage ISMS policy lifecycle — drafting, then promoting an approved draft into the isms repo with git history as the audit record. Also: how the bulk promotion reads the policy queue page and hands its update back, the `CYB` Drata-upload ticket template, the Privacy Policy website extract and its handoff sub-task, and retiring a superseded supporting document from `isms/Documents/`. |

Workflow, commit format and banner: the canonical copies in `isms/_meta/` are the source of truth;
update `references/isms-policy-lifecycle.md` in the same pass (and its identical copy in
`/isms-draft`'s `references/`) so they don't drift. The `CYB` ticket templates have no canonical copy
elsewhere — they live only in `references/isms-policy-lifecycle.md`.
