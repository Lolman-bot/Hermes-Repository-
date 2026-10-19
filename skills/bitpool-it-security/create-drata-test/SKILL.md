---
name: create-drata-test
description: "Use when writing a Drata Custom Test for a DCF control."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, drata, custom-test, compliance, iso27001, security, gitbook]
    category: bitpool
    related_skills: [ask-drata, bitpool-writing-standard, aws-context, aws-query, bitpool-docs, gitbook-docs, drata-control-insights, drive-iso27001]
---

# Create Drata Test

Designs a Drata Custom Test (Test Builder Advanced Editor JSON rule) for a named control, grounded in the control's real record and the real shape of the data it will evaluate. Stages the test's name and description for the user to paste into Drata, then writes the finished rule and its rationale into `security-documentation` under `compliance/drata-tests/` — one page per test, code and description only. Never writes test *results* — those are point-in-time and belong in Drata itself.

The workflow ships with this skill in `references/`.

> ## 🛑 THE SINGLE MOST IMPORTANT RULE IN THIS SKILL
>
> **Write a rule for exactly what the control's description says. Nothing more.**
>
> Once a rule correctly satisfies the literal wording of the control, **stop**. Do not keep
> "hardening" it to close every theoretical gap you can imagine — wider port ranges, other
> protocols, edge cases the control never mentioned, resources the control doesn't cover. Every one
> of those is a *different, unrequested* control, and chasing them is how a working, verified,
> already-correct rule gets rewritten into a fragile mess that introduces new bugs while fixing
> nothing the control actually asked for.
>
> **This happened for real, on this skill's own worked example.** DCF-92's rule was designed,
> scoped tightly to the control's literal wording, and confirmed live with 3 correct findings and
> zero false positives — done. Then, unprompted, it was "improved" to also catch wide TCP port
> *ranges*. That rewrite introduced a genuine false positive, forced an unresolved philosophical
> question about internal EKS node traffic, and burned an entire extra design cycle — to defend
> against a gap with **zero live impact** that **the control's own wording never asked about**. The
> fix was to revert and document the gap as an accepted limitation, stated by its shape.
>
> A genuinely new gap is real information — write it down as a "known limitation" (by its shape:
> what the rule does not catch and why, never how many resources it affects today) or a suggestion
> for a *separate* future test, and stop there. Do not fold it into the current rule uninvited.

## When to Use

- The user types `/create-drata-test`, or asks to "create a drata test for DCF-xxx" or "write a custom test for [control]".
- A control needs automated monitoring (`isMonitored: false`) and the data already flows through a Drata infrastructure connection.

Don't use for:
- Reading a control's status: `/drata-control-insights`.
- Broad ISO 27001 driving: `/drive-iso27001`.
- ISMS policy authoring: `/isms-draft`, `/isms-prod` — never this skill.

## Prerequisites

- **The Drata MCP server added to Hermes** (read-only use here). Tool names below are the server's own; in Hermes they carry an `mcp_<server>_` prefix — find them with `tool_search`. Its quirks are `/ask-drata`'s.
- A local clone of `security-documentation` (located via `/bitpool-docs`).
- `/bitpool-writing-standard` (section `bitpool-general`) — see rule 7.

## Procedure

Full steps, operator list and write-up conventions: `references/drata-custom-test-design.md` — read it whole with `read_file` before designing anything.

1. **Resolve the control** (Step 1). Empty search mode is not absence — seek or paginate list mode per `/ask-drata`. If `isMonitored` is already `true`, check `Drata_searchMonitoringTests` for an existing test. Done when you hold the control's `id`, `code`, `name`, `description` and `flags`.
2. **Scope to the literal wording and confirm with the user** (Step 2), using `clarify` for the scope question. Done when the user has agreed the one requirement the test checks.
3. **Determine the data source** (Step 3): native infrastructure connection, or Custom Connections & Tests. Done when the path is named to the user.
4. **Get the real schema** (Step 4): ask the user to paste the Test Builder Resource Guide's "Example data structure". Done when the schema for this resource type is in the conversation — never before.
5. **Optionally validate against live AWS** (Step 5) via `/aws-context` then `/aws-query`. Done when any estate value the rule uses was observed, not assumed.
6. **Design the rule JSON** (Step 6), then re-read the control's wording (rule 4). Done when the rule satisfies the literal wording and nothing more.
7. **Verify as a draft and stage the name and description** (Step 7) with the durability check beneath them. Done when the user confirms a draft run without engine errors.
8. **Write the page progressively** (Step 8) with `write_file` / `patch` in `compliance/drata-tests/draft/`, promote to `prod/` once verified, and regenerate indexes with `terminal`. Done when the `Using repo root: …` line names `security-documentation`.
9. **Report back** (Step 9) with the page-prose durability check. Done when the user has control, rule summary, path and verification state.

## Load-bearing rules

Restated here because each one has already caused a real, documented failure.

1. **Stop when the rule satisfies the control's literal wording.** See the highlighted rule above. A working, verified rule is the finish line, not a floor.
2. **Never fabricate a resource schema.** Always ask the user to open the Test Builder Resource Guide and paste the real "Example data structure" before writing any JSON. A plausible-looking but wrong `fact` name produces a rule that silently never matches — Drata won't error, it will just never fire. This is the one rule this skill exists to enforce.
3. **Never conclude a control doesn't exist from an empty Drata search-mode result.** Fall back to list mode and paginate. See `/ask-drata`.
4. **Re-read the control's literal wording after designing.** Ask: does this rule test what the control says, or something adjacent — source, hardening, rotation, logging? A rule was once fully designed against DCF-92 before re-reading revealed it belonged to DCF-73. Remap rather than forcing the original mapping.
5. **Verify as a draft first.** Drafts run and show results without affecting control readiness or audit evidence. Don't mark the write-up "verified" — promote its page from `draft/` to `prod/` — until the user confirms it runs without engine errors.
6. **Never write test run results, pass/fail counts or live findings into the documentation page** — code and description only. Results live in Drata's test history. In the page's prose, name values read from the estate — CIDRs, prefixes, account or OU filters — by role, since they live only in the rule JSON (the ports, protocols and match conventions the control requires may still be named), and state known limitations by their shape, never by their live impact. Detail in `references/drata-custom-test-design.md` Step 8.
7. **The test's Drata name and description, and its documentation page, are written to `/bitpool-writing-standard`.** Two outputs land in registered targets: the **name and description**, staged for the user to paste into Test Builder → Drata Custom Tests, profile **Security Drata**; and the **documentation page** → `security-documentation`, profile **Security Documentation** (that repo's `_meta/writing-standard.md` — if it is missing, the standard's target gate says what follows). Load the standard with `skill_view` — its `SKILL.md` for the gate and the six rules, then the named profile — before drafting either. The staged name and description carry the standard's durability check (§1) directly beneath them; the page's prose is checked each time it is written, and that check is shown in the report back. The rule JSON block is the home of the rule's literals (the Security Documentation profile, §2) and Drata's test history the home of results (Security Drata §3.6) — both specific by design. The design conversation, the schema request and the report to the user are outside the register.

   **Requires `/bitpool-writing-standard` (section `bitpool-general`).** Before drafting text for a Drata Custom Test or its `security-documentation` page, load it. If it is not installed, **stop and ask the user once per chat** (`clarify`): *"`/bitpool-writing-standard` isn't installed, so the Security Drata and Security Documentation writing profiles can't be applied. Installing it (`hermes skills install Lolman-bot/Hermes-Repository-/skills/bitpool-general/bitpool-writing-standard --category bitpool`) is recommended. Proceed without it?"* Continue only on a yes, and do not ask again in the same chat.
8. **One page per test, named by what it checks — never by DCF number.** A test's logic can satisfy more than one control, and a filename tied to one framework's numbering doesn't survive that. A DCF number is a reference *on* the page, not a page of its own.
9. **Write progressively.** Edit the same page as the design changes within the conversation rather than saving a "final" version once at the end.
10. **Never author ISMS policy content.** Redirect to `/isms-draft` / `/isms-prod`.
11. **Regenerate the repo's indexes after every add or edit**, and confirm the `Using repo root: …` line points at `security-documentation`.
12. **Read-only against Drata.** This skill calls no Drata write verb — the posture is set in `/ask-drata`'s write-policy table. Test JSON is pasted by a person.

## Pitfalls

- **"Encrypted" vs "restricted"** — transport encryption is not source restriction; the DCF-92/DCF-73 mixup (Step 2).
- **`IpProtocol: "-1"`** means all protocols and ports — a port check that ignores it silently misses "all traffic" rules (Step 6).
- **Hardcoding an unstable value** (a VPN IP) instead of a stable one (VPC CIDR) or a `Description` match.
- **Guessing an operator.** Trigger the Advanced Editor's validation error with a blank operator to get the real list.
- **The 70-line-per-block limit** in the Advanced Editor — narrow to observed prefixes and say so by shape.
- **Hand-maintained test lists** on landing pages — the index is regenerated; never add a row by hand.

## Verification

- The schema used was pasted by the user this conversation; every `fact` matches it exactly, including case.
- The rule tests only what the control's description says; any extra gap is a "known limitation" by shape.
- The page has no run results or counts, sits in `draft/` until the user confirmed a clean draft run, and the index regeneration named `security-documentation`.
- The staged name and description, and the page prose, each had the durability check shown.

## Reference files

Read the file itself — the table is an index, not a substitute.

| File | Covers |
|---|---|
| `references/drata-custom-test-design.md` | Designing a Drata Custom Test rule for a control — resolving the control, scoping to the literal wording, getting the real schema, the confirmed operator list, verification, staging the test's Drata name and description, and writing it up. |

Workflow, operator list, write-up conventions → edit `references/drata-custom-test-design.md`. What the Drata name and description, or the page's prose, may say → `/bitpool-writing-standard` and its profiles, never a copy here. **The operator vocabulary is incomplete by design** — Drata doesn't publish it, so it only grows from confirmed live use. When a new operator is confirmed working (or found not to exist), update the reference rather than leaving future runs to re-guess.
