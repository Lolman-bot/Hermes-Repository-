# Maintaining the register — adding targets and fixing the standard

Moved here from `SKILL.md` so the skill body stays the route. Both processes can change this skill:
publish the change through `/edit-skill` (repo `Lolman-bot/Hermes-Repository-`, path
`skills/bitpool-general/bitpool-writing-standard/`) and bump its `version`.

## Adding a target, or splitting a profile — the standard process

A platform can hold several profiles, one per subsection, when its sections need different styles.
Security Drata is one profile today; its evidence library could become its own profile tomorrow.
Every change to the register follows the same five steps:

1. **Copy `references/profile-template.md`** — for a docs repo, into that repo as
   `_meta/writing-standard.md`.
2. **Name the profile** — *Security Drata — Evidence*, *IT Documentation*.
3. **List its platform and the exact subsections it covers.** Each subsection has exactly one
   profile, so remove what the new profile takes from its parent's scope list in the same change.
4. **Add or amend its row in the register above.**
5. **Fill in the template** — readers, record kinds, rules beyond the core, calibration pairs — and
   bump this skill's `version`.

Nothing is in scope until it has a row here.

## When a record is rejected as too specific — fix the standard, not just the text

1. Correct the record.
2. Find which of the six rules covers the defect. It will almost always be one of them.
3. If a rule covers it, **put the before/after pair in that target's profile** — replacing that
   field's weakest pair rather than appending, because every profile is loaded before every write
   to its target. A new rule is warranted only for a genuinely new kind of record.
4. If a skill's template or worked example produced it, fix that template. Templates teach more
   strongly than rules.
5. Offer `/log-skill-divergence` against this skill, naming the rule that should have caught it and
   the flag or disposition that let it through.

A set of offender rules, each written for one incident and scoped to one field, is an open set: it
misses the next kind of value, as earlier per-skill rules missed people, mailboxes and products —
exactly the values in the `DCF-527` failure. The six rules are a closed definition of what a durable
record may say; the calibration pairs are the part that changes.
