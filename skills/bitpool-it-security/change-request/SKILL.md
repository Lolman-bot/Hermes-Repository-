---
name: change-request
description: "Use when the user types /change-request. Raise CHAN ticket."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, jira, change-management, itsm, iso27001, security]
    category: bitpool
    related_skills: [drive-iso27001]
---

# Change Request — Bitpool

Creates a Bitpool change management ticket in the `CHAN` Jira Service Management project, inferring
as much as possible from the conversation before asking anything. It pre-fills the required custom
fields, creates the issue, then patches the request type. The field reference, component IDs and
step detail ship in `references/`.

## When to Use

- **Only** when the user types the slash command `/change-request`.

Don't use for — these are deliberate anti-triggers, not triggers. Do **not** load or run this skill
on any natural-language phrase, keyword or topic match, including: "raise a change request",
"submit a change", "log a change", "I'm making a change", "I'm deploying", "I'm releasing",
"infrastructure change", "config change", "new change ticket", "raise a ticket", "Jira ticket",
"CHAN-NNN", or any similar phrasing. If the user describes a change without typing
`/change-request`, do not run this skill. (`/drive-iso27001` may *recommend* a change request; it
never raises one.)

## Prerequisites

- The Atlassian (Jira) MCP server connected in Hermes (`hermes mcp add ...` or
  `manage_connections`). This skill uses its `createJiraIssue` and `editJiraIssue` tools; if the
  names differ in this install, find them with `tool_search`.

## Procedure

1. **Read the field reference** — `references/change-request-fields.md` with `read_file`, the whole
   file. Done when you have the cloud ID, project, issue type, custom field keys, allowed values
   and component IDs in front of you.
2. **Infer from conversation context first** (rule 1, reference Step 1). Done when every field you
   can derive from the history is filled.
3. **Ask only for what is genuinely missing** — one grouped batch with `clarify`, never drip-fed,
   and never about change type, standard change, urgency or priority (rule 2, reference Step 2).
   Done when every required field has a value.
4. **Show the summary and get an explicit yes** (rule 3, reference Step 3). Done when the user has
   confirmed.
5. **Create the issue** with `createJiraIssue` using the payload shape in reference Step 4a — backout
   plan as ADF (rule 5). Done when the call returns a `CHAN-` key.
6. **Immediately patch the request type** with `editJiraIssue`: `customfield_10100` = `"633"`
   (rule 4, Step 4b). Done when the edit returns success.
7. **Share the ticket URL**: `https://bitpool.atlassian.net/browse/CHAN-XXX` (Step 5). Done when posted.

## Load-bearing rules

Restated here because each one either prevents a malformed ticket or an unwanted one.

1. **Infer before asking.** Scan the full conversation for the change, the systems involved, risk
   wording, timing and any rollback plan. Then ask only for what's genuinely still missing — grouped
   into one batch, not drip-fed.
2. **Never ask about change type, standard change, urgency or priority.** Change type defaults to
   `Common` unless context clearly says otherwise; the rest are derived — priority from risk
   (Low→`Minor`, Medium→`Major`, High→`Critical`), urgency from change type (Common→`Low`,
   Normal→`High`, Emergency→`Critical`), due date from start date.
3. **Always show the summary and get an explicit yes before creating.** Do not create on inference alone.
4. **The request-type patch is mandatory.** After `createJiraIssue` succeeds, immediately call
   `editJiraIssue` to set `customfield_10100` to `"633"`. Without it the ticket doesn't appear under
   the right request type in the portal.
5. **The backout plan must be ADF**, not a plain string.
6. **Slash-command only.** Never activate on a natural-language description of a change — the
   anti-trigger list is exhaustive and deliberate.
7. **Share the ticket URL** afterwards.
8. **Never guess a custom field key or an allowed value.** A wrong `customfield_` id silently drops
   the value; a wrong select value rejects the whole call.

## Pitfalls

- **Auto-activating** on "I'm deploying X" — slash command only.
- **Forgetting the `editJiraIssue` patch** — the ticket exists but is invisible under the portal's
  request type.
- **Plain-string backout plan** — must be ADF.
- **Looking up the hardcoded Atlassian config** (cloud ID, request type) instead of using the
  reference values.
- **Drip-feeding questions** or asking about derived fields.

## Verification

- The `CHAN-` issue exists and `customfield_10100` reads `633`.
- Priority, urgency and due date match the derivation rules.
- The user saw the summary and said yes before creation; the URL was shared.

## Reference files

Read the file itself — the table is an index, not a substitute.

| File | Covers |
|---|---|
| `references/change-request-fields.md` | The CHAN Jira Service Management field reference and the five-step flow for raising a Bitpool change management ticket — custom field keys, allowed values, component IDs, and the two-call creation pattern. |

Field keys, allowed values, component IDs and the payloads are edited in
`references/change-request-fields.md`.
