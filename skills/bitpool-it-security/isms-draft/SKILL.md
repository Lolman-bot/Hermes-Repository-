---
name: isms-draft
description: "Use when drafting or editing an ISMS policy in Markdown."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, isms, iso27001, policy, security, markdown, drafting]
    category: bitpool
    related_skills: [isms-prod, bitpool-writing-standard, manage-drata-control, bitpool-docs]
---

# isms-draft

Authors and edits **Bitpool ISMS policy drafts as Markdown** in the `security-documentation` repo,
under `ISMS/ISMS - Draft/` and `ISMS/ISMS - Draft (New)/`. Both are live draft areas, and everything
below applies to a draft in either. **Markdown is the source of truth**; the controlled `.docx` is
produced later, at promotion, by `/isms-prod`. This skill only drafts — it never promotes and never
touches the `isms` production repo.

## When to Use

- The user runs `/isms-draft`, or asks to "draft the [policy]", "seed the [policy] to markdown",
  "edit the [policy] draft".
- A one-time `.docx` → `.md` seed of a policy (Mode A, via `docx2txt`).
- Ongoing editing of an existing draft with clean, readable git diffs (Mode B).
- `/manage-drata-control` hands over a policy correction found in a control review.

Don't use for:
- Promoting or publishing a policy to production: use `/isms-prod`.
- Non-policy documentation: use `/bitpool-docs`.

## Prerequisites

- A local checkout of `security-documentation`. On Bitpool machines the repos live under
  `C:\BitpoolDev\Github-Bitpool\`; locate it fresh each run, and if it isn't there, ask with
  `clarify` rather than guessing.
- `docx2txt` for Mode A seeds; WSL (on Windows) for the image-dedupe snippet in the reference.
- `/bitpool-writing-standard` (section `bitpool-general`) installed — rule 9.

## Procedure

1. **Apply the scope boundaries** (rules 1-3). Done when you've confirmed the request is draft work,
   not promotion, and no write will touch the `isms` repo or a production policy.
2. **Read the procedure** in `references/isms-policy-lifecycle.md` with `read_file` — the whole
   *Drafting* part (scope, Mode A or Mode B, front-matter template, versioning). Skimming for the
   line you expect is how a threshold or a flag gets missed. Done when you know which mode applies.
3. **Load `/bitpool-writing-standard`** with `skill_view` before writing any policy text: its
   `SKILL.md` (target gate, six core rules), then its `profile-isms-policy.md`, and
   its `profile-security-jira.md` when drafting policy queue text. If it isn't installed,
   follow rule 9's stop-and-ask. Done when the ISMS Policy profile is loaded (or the user said
   proceed without it).
4. **Seed or edit the draft** with `read_file` / `patch` (whole-file `write_file` only for a fresh
   Mode A seed). Never invent policy or control content — mark `<!-- TODO: needs owner input -->`.
   For a Mode A seed, flag every docx2txt drop and dedupe images against `ISMS - Draft/assets/common/` (rules 4,
   7). Done when the draft parses, every gap is a TODO marker, and the diff is clean and atomic.
5. **Show the changed wording with one durability check** (rule 9) — on the text you changed only.
   Done when the check sits directly under the changed wording.
6. **Record it in the policy queue** — see *When the draft is ready* below. Done when the row,
   comment and link exist (or, standalone, all three have been handed to the user in order).
7. **Add a row to the document's version-control table** naming what changed and why, with the
   originating `DCF` and clause. Done when the row exists; it is a snapshot and is not checked.
8. **Report** that nothing is promoted and production is untouched. Done when said explicitly.

## Load-bearing rules

Restated here because each one protects a controlled document.

1. **Never write to the `isms` prod repo** (`C:\BitpoolDev\Github-Bitpool\isms`). Promotion is `/isms-prod`.
2. **Never edit production policies, and never claim a draft is "live".**
3. **Never invent policy or control content.** Mark `<!-- TODO: needs owner input -->`.
4. **`docx2txt` is lossy** — plain text only. Images, tables, headers/footers and styling do not
   survive. Flag every drop with `<!-- TODO: image — re-add at promotion -->` and rebuild tables by
   hand from the source `.docx`.
5. **Ask before removing a seeded `.docx`** from the draft area.
6. **Keep the Markdown clean and atomic** so `git diff` is readable — that diff is the working change history.
7. **Shared images live once in `ISMS - Draft/assets/common/`; an image unique to one draft stays in
   `assets/<policy-slug>/`** in the draft's own folder. Reference both as files; pandoc resolves them
   relative to the `.md` at promotion. After a Mode A seed, delete every extracted image that
   duplicates one in `ISMS - Draft/assets/common/` — compared by decoded pixels, not bytes — and repoint any body
   link to the shared copy. Procedure in `references/isms-policy-lifecycle.md`.
8. **Draft commits go in `security-documentation` only.** The authoritative change-log commit
   happens later, in the `isms` repo, via `/isms-prod`.
9. **Policy text follows `/bitpool-writing-standard` — writing profile *ISMS Policy*.** A draft in
   either draft folder is a registered target, body and front matter both. Policy queue text lands
   in two places: the detail comment in Jira `IRT` (a **Security Jira** snapshot) and the row on the
   queue page in `security-documentation` (**Security Documentation** profile, that repo's
   `_meta/writing-standard.md`) — structured, and dated where it records an event. Wherever you
   present policy wording — proposed, or reported once the edit lands — show **one** durability
   check on the text you changed (the standard's `bitpool-writing-standard/references/durability-check.md` §1), directly
   under it. When applying wording `/manage-drata-control` already staged with its check, don't
   repeat it; check only what you change. Not checked: the Document Version Control row, the queue
   comment, draft commit messages, and the report to the user.
   **If `/bitpool-writing-standard` isn't installed, stop and tell the user once per chat:**
   *"`/bitpool-writing-standard` isn't installed, so the ISMS Policy, Security Jira and Security
   Documentation writing profiles can't be applied. Installing it (section `bitpool-general`) is
   recommended. Proceed without it?"* Continue only on a yes; don't ask again in the same chat.
10. **The cover's `owner` names the owning role, never a person.** The named owner's single home is
    the policy's owner in Drata. Existing drafts that still name a person convert to the role —
    **when, and in what batch, is the user's call.** The first time in a chat you edit such a draft,
    ask with `clarify`: convert now, convert a batch, or leave it; never convert silently as a
    side-effect. **Before converting, confirm the policy's owner in Drata holds the named person**
    (ISMS Policy profile §3.2). This skill has no Drata tool, so ask the user to confirm it, and where
    it's blank, have it filled first. A conversion never removes the only record of who owns the
    policy, and is recorded like any other draft edit.

## When the draft is ready

**Do not tell the user to promote it yet.** Bitpool decision, 2026-08-24: ISMS policy changes are
drafted continuously as controls are reviewed, then promoted **once, in bulk, at the end** of a
control review programme — one `.docx` build, one Drata upload, one approval round, one renewal.
Promoting per policy means re-approving the same document for every control that touches it, and
each approval is a clause 7.5.2 event a human has to actually perform.

The policy queue is one standing `Task` in Jira `IRT`, found with
`project = IRT AND labels = PolicyQueue` (via the Atlassian MCP server's tools — find them with
`tool_search`), indexed on its page in `security-documentation` (`compliance/isms-policy-queue.md`).
Three parts, in this order (see *Writing a queue row* in `/manage-drata-control`):

- **The row on the page, claimed first** — the highest number in the page's Pending changes table
  plus one, read from disk just before the edit, with its `Detail` cell reading `pending`, made with
  `read_file` then `patch` — never a shell append or redirect, `sed`, a heredoc or a whole-file
  `write_file`, which skip the stale-read refusal that stops two runs taking the same number.
- **A comment carrying the detail** — Policy, Origin (`DCF-xxx` · risk id · the IRT key where one
  exists, otherwise the ICR review key), Draft edited (date), Clause, then the change in full. Be as
  expansive as the change warrants: the comment is a snapshot. When the edit answers a finding, the
  finding's evidence (observed configuration, names, counts) stays here and in the handoff; the
  policy wording states the requirement in categories (ISMS Policy profile, *Drafting from a
  finding*). Secret values never appear; security-sensitive identifiers go to the restricted home
  the standard names, with the comment pointing to it.
- **The row linked** — `pending` replaced by the link to that comment, plus a Status note or At
  promotion step where the change promotes with other rows or needs a step at promotion.

**Nothing row-related goes in the ticket's description** — it holds only the queue's standing
rules. The queue is owned and written by `/manage-drata-control`; running standalone, hand the user
all three — the page row, the detail comment and the link — in that order, rather than writing them.

Promotion happens later, on explicit request, via **`/isms-prod`**. **Never do any of it here, and
never prompt for it as the next step just because a draft edit finished.** A lapsed `renewalDate` is
the expected state of every policy between bulk promotions — not a finding, and not an argument for
promoting early.

### Withdrawing a rule from a policy — rewrite the section, never delete it

When a decision removes a control the policy claimed, don't delete the section. Annex A **5.3**
requires conflicting duties to be *identified and documented*; a section naming one is part of that
identification. Delete it and the duty disappears from the record — strictly worse than a duty
documented as unsegregated with its compensating controls beside it. Rewrite the section to state
the duty is not segregated, why that is acceptable, and what covers it instead. Worked example,
2026-08-24: the Separation of Duties Policy's `### Control Attestation and Compliance Evidence` was
slated for deletion when Bitpool decided not to use a second-person control approval; it was
rewritten instead — same decision, still on the list.

## Pitfalls

- **Prompting for promotion** after a draft edit. Bulk promotion is the rule; say nothing promoted.
- **Trusting docx2txt output** — tables, images, headers and styling are gone; flag and rebuild.
- **Byte-comparing images** for dedupe. Compare decoded pixels.
- **Claiming a queue row number from memory** or appending with a shell redirect — two runs collide.
- **Converting a person-owner to a role silently**, or before Drata holds the named person.
- **Deleting a withdrawn control's section** instead of rewriting it (Annex A 5.3).
- **Reporting a lapsed `renewalDate`** as a finding.

## Verification

- `git -C <security-documentation> status` shows changes only under the draft folders (and the
  queue page, if written); the `isms` repo is untouched.
- Every gap is a `<!-- TODO ... -->` marker; no invented control content.
- The changed wording carries one durability check; the version-control table has a new row.
- The queue row, comment and link exist (or were handed to the user in order).
- The report says nothing is promoted.

## Reference files

Read the file itself — the table is an index, not a substitute.

| File | Covers |
|---|---|
| `references/isms-policy-lifecycle.md` | The two-stage ISMS policy lifecycle — authoring Markdown drafts in security-documentation (Mode A seed, Mode B edit, front-matter template, versioning), then promoting an approved draft into the controlled isms production repo with git history as the audit record. |

Modes, front-matter template and versioning convention are edited in
`references/isms-policy-lifecycle.md` **and its identical copy in `/isms-prod`'s `references/`, in the
same change**. What policy text may say → `/bitpool-writing-standard`'s ISMS Policy profile, never
restated here.
