---
name: manage-drata-vendors
description: "Use when adding or fixing Drata vendors. Stages each write."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, drata, vendors, third-party-risk, iso27001, grc]
    category: bitpool
    related_skills: [ask-drata, bitpool-writing-standard, manage-drata-control, manage-drata-risks, quarterly-configuration-and-asset-review, isms-draft]
---

# Manage Drata vendors

Drata is **the register of record for Bitpool's SaaS vendors and third parties** — its device and
cloud-resource lists are not the register for anything. This skill owns the vendor side: it adds and
classifies a vendor, corrects a record field by field, or runs the whole-register review cycle, and
stages every write as a per-vendor note the risk owner approves in a file before anything reaches Drata.

## When to Use

- `/manage-drata-vendors`, `/manage-drata-vendors add <name>`, `/manage-drata-vendors <name or id>`, or
  `/manage-drata-vendors review`.
- The user asks to add a vendor to Drata, fix a vendor record, re-score a vendor, find which vendors need
  a security review, or tidy the vendor register.

Don't use for:
- Uploading a security review or SOC 2 report — impossible on this connection (rule 6).
- A control's treatment or an `IRT` ticket — `/manage-drata-control`. Verifying a risk — `/manage-drata-risks`.
- The quarterly asset register cycle — `/quarterly-configuration-and-asset-review`.
- Drata connection quirks — `/ask-drata`. ISMS policy text — `/isms-draft`.

## Prerequisites

- **The Drata MCP server added to Hermes** (`hermes mcp add …` or `manage_connections`). Tool names here
  (`Drata_listVendors`, `Drata_getVendor`, `Drata_createVendor`, `Drata_updateVendor`,
  `Drata_listVendorSecurityReviews`, `Drata_listVendorDocuments`) are that server's tools; Hermes may
  prefix them — find them with `tool_search`. Read `/ask-drata` for connection-level behaviour.
- **Read `references/field-contract.md` before any write** — the authority on which fields this skill
  sets, wipes and never touches, exact enums, custom field ids, and verified vs inferred write shapes.
  Never reconstruct any of it from memory.
- **`/bitpool-writing-standard`** (section `bitpool-general`) — load it before drafting text for its
  registered targets, and only then. If it is not installed, **stop and tell the user once per chat**:
  *"`/bitpool-writing-standard` isn't installed, so the Security Drata writing profile can't be applied.
  Installing it from the `bitpool-general` section is recommended. Proceed without it?"* Continue only on
  a yes, and do not ask again in the same chat.

  | Output | End location | Writing profile |
  |---|---|---|
  | Proposed `services_provided`, `data_stored`, `location` | Drata — Vendors | **Security Drata** (§3.4) — durable |
  | Security review text the user pastes (staging note section 7) | Drata — Vendors | **Security Drata** — dated snapshot, no durability check |

  Durable text gets the standard's durability check (its durability-check reference, §1) directly under
  it — in the staging note, because approval happens there. Structured fields (enums, booleans, dates,
  `owner`, custom fields) take no check. Everything else this skill produces — the staging note, its
  section 10 hand-off, the cycle worksheet and handover, the `CYB-530` comment, the `ITS` exemption
  draft, the session log, chat reports — is outside the register.
- **The GRC document library synced locally** — `%USERPROFILE%\Bitpool Pty Ltd\GRC - Bitpool -
  Documents\General\Drata\Vendors\`. Resolve `%USERPROFILE%` to an absolute path first (`terminal`:
  `echo "$USERPROFILE"`); if not synced, ask for the path with `clarify` (rule 1).

## Procedure

Full step text: `references/workflows.md`. No argument → ask which mode with `clarify`, offering the
action-required set as a shortlist.

**§1 — Add a new vendor** (classify before you create — an unscored vendor makes `DCF-56` less true):
1. Check it is not already there — page `Drata_listVendors` (no text search), include archived, and check
   `drata-vendors-to-add.csv` if the user has one. Done when "new" vs "returning (status change)" is known.
2. Establish what it does for Bitpool — what it holds, reaches, who logs in, personal information. Ask
   rather than infer from marketing. Done when each is answered or asked.
3. Classify against `references/classification-rubric.md` — relationship type, four service-model flags,
   inherent impact, residual risk, review obligation. Done when every element has a value and basis.
4. Write the staging note (`references/staging-note-format.md`) with every field to send and every field
   left unset with what would establish it; durability check under section 1. **Stop until
   `status: approved`.** Done when the note is saved and approved.
5. `Drata_createVendor` — one call, custom fields inline (a create omitting required custom fields
   `400`s; read the error, don't assume the set). Done when the call succeeds.
6. Read back with `Drata_getVendor`; report `id`, returned `owner`, custom fields, anything not landed;
   check `breakdown.current` moved by one. Done when reported.
7. Record results in the note; set `status` (`written-pending-review` while the review is outstanding).
8. Tell the user what remains theirs: the security review, documents, the pre-access agreement review.
9. If the review is deferred: set `status: UNDER_REVIEW`, write the section 10 hand-off, and hand it to
   `/manage-drata-control`, which creates the (undated) `IRT` ticket. Done when the report says the
   ticket is not yet raised.

**§2 — Correct one existing vendor:** read live (`Drata_getVendor` with
`expand=["customFields","vendorUser","scheduleConfiguration","dataAccessedOrProcessed"]`, never trusting
`latestSecurityReviews`); read reviews via `Drata_listVendorSecurityReviews`; diff against the field
contract into separate **fill / fix / wipe** blocks; scores in their own block (rule 5); stage, approve,
write, read back, report. Done when the read-back matches the approved note.

**§3 — Whole-register review cycle** (the register half of `CYB-530`): size cheaply with `size=1` +
filters (`breakdown.current`, not `totalCount`); page the register to `cursor: null`; check each record
for what goes stale; reconcile **both directions** (in use but unregistered; registered but unused —
inactive via `status`, never delete) naming each source and its date; archive only after the access
sweep; produce the worksheet and work it one vendor at a time (parallel analysis via `delegate_task` is
fine, parallel writes are not); record evidence including no-change results in full. Done when every
exception has a disposition and the files are named for the user to attach.

## Load-bearing rules

Summaries — full text, reasoning and worked examples (GitBook, Bitbucket) are `references/vendor-rules.md`.

- **MFA is not a vendor attribute — never record it.** Custom fields `4`–`6` were deleted (2026-09-04);
  never recreate them, never write `password_mfa_enabled`. Authentication posture is an observation in
  the security review.
1. **One vendor per approval, in a file, not the chat.** Staging notes live in the GRC library under
   `Vendors\<VendorName>\<YYYY MM>\`; cycle artefacts under `Vendors\Reviews\<YYYY MM>\`. It is an
   Obsidian vault (frontmatter, `[[wiki links]]`). **Read the `Your value` column** — it wins over your
   proposal. Never leave a copy behind when a file moves.
2. **Re-read the vendor live immediately before each write and compare `updatedAt`.**
3. **Pass only the fields you are changing** — `Drata_updateVendor` is a partial update.
4. **Never write `confirmed`, in either direction.**
5. **Never write `impact_level` or `risk` without explicit per-vendor approval of that score**, in its own
   block; reopen a score whose basis new information invalidates.
6. **You cannot create a security review or upload a document** — no such verb exists. You arm the
   obligation (`renewal_schedule_type`, `renewal_date`, `status`); the user performs and records it.
   `status: UNDER_REVIEW` records an outstanding first review; a future `renewal_date` does not.
7. **You cannot create a custom field definition** — ask for it in the Drata UI, then capture its id.
8. **Never invent a `renewal_date`, and never move one that has passed.**
9. **Free-text vendor fields carry no current-state value** (Security Drata §3.4); every count in a
   snapshot carries its date and query.
10. **Never write ISMS policy text** — register vs Vendor Management Policy drift goes to `/isms-draft`;
    the policy wins unless the risk owner decides otherwise.
11. **Research a field before offering to leave it blank** (citation + date in the `Basis` column, never
    in the value), and **never inherit a classification unverified** — establish who produced it.
12. **A vendor limitation is not a Bitpool control failure.** Exemptions go through the `ITS` ISMS
    Exemption Application, **raised by the risk owner, never by the agent** — draft the seven answers in
    the note, propose an expiry, and first check the clause being exempted from actually exists.
13. **Never infer a capability from a field's name** — check schema, data and UI visibility, and say which.
14. **Never fabricate an authorship record** — Drata stamps author and date; drafts carry none.

## Pitfalls

- Reviewing a vendor record in the chat instead of a staging note.
- Trusting `latestSecurityReviews` or `renewalDateStatus` (reads `COMPLETED` with zero reviews).
- Reporting `totalCount` (includes archived) as the headline; `size=50` blows the response limit.
- Reading `cost` as dollars — it is cents.
- Confusing vendor `status: APPROVED` with a review `decision`.
- Writing `critical` or `is_sub_processor_active` — both on the wipe list.
- Archiving a retired vendor before its access is revoked.
- Accepting a below-raw residual override without writing its conditions into the review.
- Full behaviour table: `references/drata-vendor-behaviour.md`.

## Verification

- Every write traces to a staging note with `status: approved`, re-read immediately before writing.
- Each write sent only changed fields; `confirmed` was untouched; scores had their own approval.
- The read-back (`Drata_getVendor`) is recorded in the note's results section.
- Every count in a snapshot carries its date and the filter that produced it.
- Anything handed off (`/manage-drata-control`, `/isms-draft`, `/ask-drata`) is named in the report.

## Reference files

| File | Covers |
|---|---|
| `references/field-contract.md` | Every field, its disposition, exact enums, custom field ids and option values, and the write shapes — verified versus inferred |
| `references/classification-rubric.md` | Relationship type by standing access, the four service-model flags, inherent versus residual scoring, and the security review threshold |
| `references/staging-note-format.md` | The per-vendor approval note — where it lives, frontmatter, numbered sections, the durability check, and the `Your value` override |
| `references/vendor-rules.md` | The MFA decision and the fourteen rules in full, with worked examples |
| `references/workflows.md` | §1 add, §2 correct, §3 review cycle — full step text |
| `references/drata-vendor-behaviour.md` | Vendor-specific Drata behaviour this skill relies on, and what to do about each |

Hands off to: `/isms-draft` (policy drift), `/manage-drata-control` (deferred-review `IRT` ticket; vendor
control positions `DCF-56`, `DCF-57`, `DCF-132`, `DCF-168`, `DCF-507`, `DCF-762` — A.5.19–A.5.23),
`/quarterly-configuration-and-asset-review` (the wider cycle), `/ask-drata` (new connection findings), and
the user (every review, document, custom field definition and score decision).
