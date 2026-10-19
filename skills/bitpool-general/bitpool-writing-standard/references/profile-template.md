# Writing profile template

Every writing profile — the ones shipped in this skill's `references/` and the ones each docs repo
keeps at `_meta/writing-standard.md` — follows this template, so that every target answers the same
questions in the same order, and so that a platform can be split into per-section profiles without
inventing a new shape each time.

A profile exists only if it has a row in the target register in `SKILL.md`. Adding one, or splitting
one, follows the five-step process in `references/maintaining-the-register.md`.

---

## Where a profile lives

| Target | Profile location |
|---|---|
| A platform that is not a docs repo — Drata, Jira, ISMS policy drafts | `references/profile-<name>.md` in this skill |
| A docs repo | `<repo>/_meta/writing-standard.md` — at `_meta/` root, not under `_meta/skill/`, which the index generator skips; registered in `_meta/README.md`, the repo's `CLAUDE.md` reading list and `_meta/ai-instructions.md` |

A repo profile uses the repo's own frontmatter schema and states, in its rules, that frontmatter
`owners` names roles or teams only — never an email address or a personal name.

---

## The template

Copy everything below the line. Keep it short: the core rules live in `references/core-rules.md`, and a profile
carries only what is specific to its target.

---

# Writing profile — `<Profile name>`

| | |
|---|---|
| **Writing profile** | `<Profile name>` — the name the target register uses |
| **Platform** | `<platform>` |
| **In scope** | `<the exact subsections: projects, objects, folders>` |
| **Out of scope** | Everything else on this platform, stated explicitly — `<examples>` |
| **Readers** | Who reads these records later, and what they use them for |
| **Tone** | One or two lines |
| **Split from** | `<parent profile>`, or — |

## §1 Sections

One row per section of the platform. A platform with several sections lists them all, even when one
profile covers every section today, so that a later split changes a row rather than the structure.

| Section | In scope? | Profile | Note |
|---|---|---|---|
| `<section>` | Yes / No | `<this profile, or the profile it was split to>` | |

## §2 Record kinds in this target

Which fields or page types are durable, which are snapshots and which are structured, and which page
types this profile declares the **home** of specific values.

| Field or page type | Kind | Note |
|---|---|---|
| | Durable / Snapshot / Structured / Home of `<values>` | |

## §3 Rules beyond the core

Only what the six core rules do not already say for this target — the shape a description takes, the
freshness marker its pages carry, the traps specific to its fields. Never restate a core rule.

## §4 Calibration pairs

A short table of before/after pairs from this target's own records, dated as observed. Replace the
weakest pair rather than appending: this file is loaded before every write to its target.

| Before | After |
|---|---|
| | |

## §5 For readers without the skill — repo profiles only

Three or four lines summarising the core rules for a person reading the repo in GitBook, naming
`/bitpool-writing-standard` as the authority. A summary, never a restatement that could drift from it.
