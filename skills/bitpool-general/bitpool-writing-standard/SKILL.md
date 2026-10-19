---
name: bitpool-writing-standard
description: "Use when text lands in Drata/IRT/ISMS docs. Keep it durable."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, writing, durability, drata, jira, isms, documentation, iso27001]
    category: bitpool
    related_skills: [bitpool-docs, isms-draft, manage-drata-control, manage-drata-risks, manage-drata-vendors, ask-drata, aws-query, log-skill-divergence, edit-skill]
---

# Bitpool writing standard

Some Bitpool records are read months after they were written, by someone who will not re-check
them — an auditor testing evidence against a Drata record, a colleague deciding from an IRT ticket,
the next Hermes session copying a risk entry. In those places, AI-written text has been far more
specific than the record needs: it copies values that live somewhere else — who holds a role, when
they were appointed, which mailboxes, how many AWS accounts and what they are called — so the record
is true on the day it is written and silently false soon after.

**This standard applies to named places, not to a topic.** Security text headed for a board report
does not get it; a finance figure headed for an IRT description does. The register below is closed:
if the end location is not in it, this skill does not apply. In scope, it keeps each fact in one
home and describes a record's shape instead of copying its values.

## When to Use

- The user runs `/bitpool-writing-standard`.
- **Unprompted**, before drafting or staging text whose end location is a registered target —
  including text drafted in chat for someone to paste into one.
- Whenever another skill says to apply it (the Drata, Jira and ISMS skills, `/bitpool-docs`).

Don't use for:
- **Any end location not in the register, whatever the topic** — board reports, management packs,
  presentations, emails, Teams and chat, customer documents, other Jira projects, other docs repos.
  Write as the task needs, apply none of these rules, and do not mention this skill.

## Procedure

1. **Run the target gate** (Step 1 below) before anything else. Done when you have named the end
   location and either stopped (out of scope) or named the writing profile that applies.
2. **Load the core rules and the profile** with `read_file`: `references/core-rules.md`, then the
   target's profile from the register (a docs repo's profile is its `_meta/writing-standard.md`).
   Read the whole file. Done when both were read this run.
3. **Decide the record kind** — durable, snapshot or structured field (Step 2) — for each field
   before writing a word. Done when every field you will write has a kind.
4. **Draft durable text under the six core rules** (Step 3). Done when the draft points at homes
   rather than copying their values, and every pointer was confirmed against the version in force.
5. **Show the durability check** (Step 4). Done when exactly one check sits under the staged text
   (or in the report / staging file / paste draft, per Step 4), or one line says nothing was flagged.

### Step 1 — the target gate

1. **Name the end location** — the platform, and the subsection within it, where the text will be
   stored. Not the subject matter. Text drafted in chat for someone to paste into Drata has Drata as
   its end location. If the end location is genuinely unknown, ask with `clarify`.
2. **Is the platform in the register?** No → **stop. This skill does not apply.**
3. **Is the subsection in scope for that platform's profile?** No → **stop. It does not apply.** A
   finance board in Jira, an OP or BT ticket, a docs repo with no profile — all out.
4. **Yes to both** → load the core rules **and** that target's writing profile. Where two targets
   overlap, the more specific wins: a draft in either ISMS draft folder is **ISMS Policy**, not
   Security Documentation.
5. **A registered repo profile that is missing from the repo** means that repo is not in scope until
   it is restored. Say so once.

#### The target register

| # | Platform | Subsections in scope | Writing profile | Profile |
|---|---|---|---|---|
| 1 | Drata — Bitpool workspace | Risk register · Evidence library · Controls · Vendors · Framework requirements (SoA exclusion rationale) · Custom Tests | **Security Drata** | `references/profile-security-drata.md` |
| 2 | Jira — `bitpool.atlassian.net` | Projects `IRT`, `ICR` and `CSIP`. **No other project.** | **Security Jira** | `references/profile-security-jira.md` |
| 3 | ISMS policy drafts | `security-documentation/ISMS/ISMS - Draft/` and `ISMS/ISMS - Draft (New)/`, written through `/isms-draft` | **ISMS Policy** | `references/profile-isms-policy.md` |
| 4 | `security-documentation` repo | The folders that profile lists, excluding row 3's folders | **Security Documentation** | `security-documentation/_meta/writing-standard.md` |
| 5 | `it-documentation` repo | The folders that profile lists | **IT Documentation** | `it-documentation/_meta/writing-standard.md` |
| 6 | `bitpool-projects` repo | The folders that profile lists | **Projects Documentation** | `bitpool-projects/_meta/writing-standard.md` |

**Out of scope — every other end location**, for example: any other Jira project (finance, sales,
OP, BT, CYB, CHAN); board reports, management packs and presentations; emails, Teams and chat;
customer and partner documents; the other docs repos, until one has a profile registered here.
Those places may need exactly the point-in-time numbers, names and approvals this standard keeps
out of its targets. Nothing is in scope until it has a row here; adding a target or splitting a
profile follows the five-step process in `references/maintaining-the-register.md`.

### Step 2 — three kinds of record

| Kind | What it is | Specificity |
|---|---|---|
| **Durable** | A standing statement, read later as "how things are" | Shape, categories and pointers — never copied current-state values |
| **Snapshot** | A dated record of a moment, read later as "what was true then" | As specific as the moment warrants — that is its job |
| **Structured field** | A field the system itself treats as the value | The value, exactly — this field is its home |

The test, and the `DCF-527` calibration pair (a labelled anti-pattern — never copy its *before*),
are in `references/core-rules.md`.

### Step 3 — the six core rules (full text: `references/core-rules.md`)

1. **One home per fact — and the pointer must resolve.** Write the value in its system of record;
   everywhere else point at it, after confirming the version in force holds it.
2. **Describe the shape, not the contents** — what it is, where it lives, what kinds of information
   it holds, why that satisfies the requirement, what keeps it trustworthy.
3. **Never copy current state — and never generalise past the truth.** Remove the value, don't
   correct it; the general wording must be exactly as true as the value it replaces.
4. **A fact is a fact — state it where it is needed, anchored as an event:** needed here, anchored
   (date, method or role and forum, where recorded), past tense, the event not the measurement.
5. **Roles, not people.** The person holding a role lives in exactly one named home.
6. **State the position, not the record's own history**, and create the history record (changelog
   comment, Version Control row, new evidence version, ICR/IRT comment) in the same change.

The rules, the twelve-month and owner tests, and *Where specifics are right, even in scope — do not
over-apply* are in `references/core-rules.md`. Apply that file, not this summary.

### Step 4 — the durability check

Every skill that stages durable text for a registered target shows **one** durability check per
approval block, directly under the staged text, as a formatted markdown table — never a fenced code
block.

1. **Flag** the draft against the full pattern table in `references/durability-check.md` §2. Apply
   that table, not a summary.
2. **Dispose of each flag** — kept (and why), generalised (quote the new wording), moved (to
   where), or cut.
3. **Show the result on the final wording**: a table of the judgement calls that remain, one
   collapsed row for handles, and a one-line *Removed before staging* list. More than about eight
   judgement rows means the text is carrying a log — shorten it first. If nothing was flagged, one
   line says so. Durable text with no check shown has not been checked.

Where there is no approval block in the chat: a skill that writes then reports puts the check in its
report; approval in a file puts it beside the proposed text; a draft for pasting has it directly
under the draft; in a handoff the staging skill shows it and a downstream skill applying the same
approved wording checks only what it changes. One check may span profiles — add a `Profile` column.
Out of scope, there is no check — and none should be shown.

## Load-bearing rules — precedence

- **The target gate comes first, always.** No rule below the gate applies outside the register.
- **Against a profile.** A profile sets tone and declares which of its fields or page types are the
  home of which values. It never relaxes rules 1, 4, 5 or 6.
- **Against a workflow skill.** A workflow skill decides *which* fields are written, *when*, and by
  whom. This standard decides *what the words say* in a registered target. Where a workflow skill's
  template or worked example puts a copied value into a durable field of a registered target — a
  score, a named owner, a linked control's name, a scheduling state, a pass date, an elapsed time —
  the standard wins, and the template is the defect to fix. A ticket carries enough to **do the
  work** — outcome, definition of done, pointers — and nothing needed only to re-assess the risk
  without opening Drata.
- **Skill templates are governed by their output's target.** A template that produces text for a
  registered target follows that target's profile. A template whose output lands anywhere else is
  out of scope.
- **Against a platform's own tool text.** An MCP tool's field description (*"describe the affected
  systems"*) never outranks the profile. The field's constraints — length, required, format — still
  bind; its advice on content does not.
- **Advice versus target text.** Telling the user which artefacts exist or what to upload is chat,
  out of scope. A paste-ready name or description for a registered target is target text, in scope.

## Pitfalls

- **Gating on topic instead of end location.** Security text for a board report is out; a finance
  figure in an IRT description is in.
- **Correcting a stale value instead of removing it.** "Seven accounts" replacing "five" only resets
  the clock.
- **Over-applying.** Snapshots, structured fields, durable handles, generated artefacts and the other
  cases in `references/core-rules.md` keep their specifics. Vague is not durable — *"documentation is
  maintained"* is empty.
- **Pointing at a home that doesn't hold the value.** That is a false statement; open the version in
  force first.
- **Session voice in durable text** — *"another session"*, *"proposed by Hermes"*, *"this is yours to
  perform"*.
- **Mentioning this skill out of scope.** Out of scope, it is silent.

## Verification

- The end location was named and checked against the register before drafting.
- `references/core-rules.md` and the target's profile were read this run.
- Each written field has a kind; durable text holds pointers and categories, not copied values.
- Exactly one durability check was shown, in the right place, on the final wording.

## When a record is rejected, and when the register changes

Fix the standard, not just the text: correct the record, find the core rule that covers the defect,
put the before/after pair in that target's profile, fix any template that produced it, and offer
`/log-skill-divergence`. The full process, and the five steps for adding a target or splitting a
profile, are in `references/maintaining-the-register.md`.

## For skills that depend on this one

This skill lives in section `bitpool-general` of `Lolman-bot/Hermes-Repository-`. Skills in other
sections that write to a registered target — the Drata and Jira skills in `bitpool-it-security` —
load it by name with `skill_view`, and carry this behaviour for when it is not installed:

> **Requires `/bitpool-writing-standard` (section `bitpool-general`).** Before drafting text for
> `<target>`, load it. If it is not installed, **stop and tell the user once per chat**:
> *"`/bitpool-writing-standard` isn't installed, so the `<profile>` writing profile can't be applied.
> Installing it is recommended:
> `hermes skills install Lolman-bot/Hermes-Repository-/skills/bitpool-general/bitpool-writing-standard --category bitpool`.
> Proceed without it?"* Continue only on a yes, and do not ask again in the same chat.

- **Several profiles** — name them all in the one message: *"…so the Security Drata and Security
  Jira writing profiles can't be applied…"*.
- **Once per chat means once for the whole chat**, not once per skill. If the user has already
  answered in this chat — in any skill — carry that answer; do not ask again.
- **A handoff** names only the profiles this skill applies itself; the skill it hands to carries its
  own notice.

Dependent skills point here and never restate these rules: a paraphrased copy drifts from its source
exactly as a copied value does.

## Reference files

Everything this skill needs ships in `references/`, except the repo profiles — register rows 4 to 6
— which each repo owns. Read the file itself; the table is an index.

| File | Covers |
|---|---|
| `references/core-rules.md` | The three record kinds with the `DCF-527` calibration pair, the six core rules in full, and where specifics are right even in scope |
| `references/maintaining-the-register.md` | The five-step process for adding a target or splitting a profile, and what to do when a record is rejected as too specific |
| `references/profile-security-drata.md` | **Security Drata** — scope, sections, every in-scope Drata field by kind, evidence descriptions, risk text, control descriptions, vendor fields, SoA exclusion rationale, Custom Tests, calibration pairs |
| `references/profile-security-jira.md` | **Security Jira** — `IRT`, `ICR` and `CSIP` only: summary and description versus comments, IRT Task and Sub-task wording, creation comments, ICR outcome and hold comments, CSIP explainers, standing tickets |
| `references/profile-isms-policy.md` | **ISMS Policy** — policy drafts written through `/isms-draft` |
| `references/profile-template.md` | The template every profile follows, including the repo profiles, and what a profile must contain |
| `references/durability-check.md` | The check's format, the flag patterns, dispositions, false positives, and how audit modes sweep existing records |

**Editing this skill:** the gate, the register and precedence → this file; the six rules →
`references/core-rules.md`; a target's detail and calibration pairs → its profile; a docs repo's
feel → that repo's `_meta/writing-standard.md`. Hold this skill to its own standard: no counts,
holders or dates in its text except labelled calibration examples, placeholders and anchored
history. Publish through `/edit-skill`.
