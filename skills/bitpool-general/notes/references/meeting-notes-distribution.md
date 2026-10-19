# Meeting Notes Distribution

Processes any transcript or document and distributes structured notes into the matching
organisational-unit (OU) subfolders of a target repo's `notes/` section. The OU structure is
discovered from the repo itself — no folder names are hardcoded.

## Core rules

| Type | Rule |
|---|---|
| **Action items** | Live in EXACTLY ONE OU — whichever is most responsible. Never duplicated. |
| **Notes & context** | Can appear in ONE OR MORE OUs — wherever the information is relevant. |
| **Unclassifiable** | Goes into `notes/misc/`. |
| **Original file** | Always stored in `notes/transcripts/` with a clean `.md` summary alongside it. |

## Collect inputs

Parse the invocation for a **transcript path** (a file path, or "paste") and a **repo path** (the
root of the target documentation repo).

If either is missing, ask before proceeding. **Do not assume a default repo.** If both are given
positionally, the first file-like argument is the transcript and the second directory-like
argument is the repo path.

## Discover OUs

**Not for `bitpool-projects`.** That repo's top-level folders are projects, not OUs, and it has no
`notes/` tree: a project meeting is a `Note` page in the project's own folder. If the repo path is
`bitpool-projects`, stop and hand the transcript to `/bitpool-docs`.

List the top-level directories in the repo path. These are the OUs.

Exclude: `.git`, `.github`, `.claude`, `.hermes`; `_meta`, `_`, or any folder starting with `_` or `.`;
`notes` (the output folder itself); and build artefacts — `node_modules`, `vendor`, `dist`,
`build`.

Always add `misc` as an implicit OU — it does not need to exist in the repo beforehand.

### it-documentation

```
aws, collaboration, compliance, endpoints, identity-access, infrastructure,
integrations, microsoft-365, networking, onboarding, runbooks, security
→ + misc (implicit)
```

### security-documentation

```
compliance, incident-response, policies, procedures, risk-management,
supplier-management, training-awareness
→ + misc (implicit)
```

## Parse the source file

**VTT files** — strip all of:

- Timing cue lines: `HH:MM:SS.mmm --> HH:MM:SS.mmm`
- UUID/cue identifiers (lines matching `[a-f0-9-]{36}` or plain integers)
- Speaker tags: `<v Speaker Name>` and `</v>`
- The `WEBVTT` header line

Preserve speaker names as a label prefix where multiple speakers are present (e.g. `Eric: …`). If
only one speaker is detected — a single-mic recording — note this and focus on content without
speaker prefixes.

**Other formats** — read as-is. PDF: read the text content. MD/TXT and pasted content: use
directly.

## Store the source file

Regardless of content, always:

1. Write or copy the original to `<repo>/notes/transcripts/YYYY-MM-DD-<slug>.<ext>`. Infer the
   date from the filename, file metadata, or content — if unclear, ask. `<slug>` is a short
   kebab-case name from the filename or meeting title.
2. Create a clean narrative `.md` summary at
   `<repo>/notes/transcripts/YYYY-MM-DD-<slug>.md`. This is flowing prose — no VTT markup, no raw
   transcript. Cover what the meeting was about, who attended, key decisions, key action items,
   and overall themes. Aimed at a reader who wasn't there.
3. Update `<repo>/notes/transcripts/README.md` with a row:
   `| YYYY-MM-DD | [Meeting title](YYYY-MM-DD-<slug>.md) | Brief description |`

## Extract and classify all items

**A. Action items** — concrete tasks someone agreed to do. Identified by phrases like "I'll do
X", "can you do X", "we need to", "action:", "TODO", "will follow up", "[name] to [task]".

For each, record the **owner** (use "Unknown" if unclear), the **task**, the single most relevant
**OU**, and one sentence of **context**.

**B. Notes & context items** — everything else: decisions, discussions, information shared,
future plans, risks raised, background. For each, record the **content**, **all** relevant OUs,
and a **type**: decision / discussion / risk / info / future-plan.

## Create or update OU note files

Path: `<repo>/notes/<ou>/<topic-slug>.md`. The topic slug derives from the primary subject —
`change-management`, `api-keys`, `disaster-recovery`. One file per distinct topic per OU.

**If the file already exists**, append a new dated `## YYYY-MM-DD — Meeting Name` section under
the existing `## Discussions` heading. **Do not overwrite.**

<details>
<summary>OU note file format</summary>

```markdown
---
title: "Notes: <Topic>"
description: <One-sentence summary of what this note tracks.>
audience: [team, ai-agents]
last_reviewed: YYYY-MM-DD
status: active
sources: [internal-transcript]
keywords: [relevant, keywords]
related:
  - path/to/formal/doc.md
---

# Notes: <Topic>

<Brief description of what this note tracks.>

## Current Formal State
<What is formally documented / currently implemented — read from the formal docs in this repo
if they exist, otherwise write "Not yet formally documented.">

---

## Discussions

### YYYY-MM-DD — <Meeting Name>

**Source:** `notes/transcripts/YYYY-MM-DD-<slug>.md`

#### Notes & Context
- <Note 1>
- <Decision:> Something agreed
- <Risk:> Something flagged

#### Action Items
> Action items for this OU live here. Items owned by other OUs are not duplicated — see links
> in related files.

- [ ] **<Owner>** — <Task> _(context: one sentence)_

---

## Gap Analysis

| Item | Status |
|------|--------|
| <Thing> | ✅ documented / ❌ missing / ⚠️ partial |

## Open Actions

- [ ] **<Owner>** — <Task> _(all open actions aggregated here)_
```

</details>

**Cross-OU references.** When a note file has relevant context but the action items for that topic
belong to a different OU, add a callout instead of duplicating them:

```markdown
#### Action Items
> Action items for this topic are tracked in [`<other-ou>/<topic>.md`](<other-ou>/<topic>.md).
```

## Handle misc items

Items that don't fit any discovered OU go in `<repo>/notes/misc/<topic-slug>.md`, using the same
note file format. In the frontmatter add `ou: misc` and a note explaining why it doesn't fit a
standard OU.

## Update indexes

**`<repo>/notes/index.md`** — add or update the entry for each OU that received new content. Each
OU section is a table: `| Topic | Last Updated |`.

**Each subfolder's `README.md`** — add a row for any new topic file.

**`<repo>/SUMMARY.md`** — if the repo has one, add entries under a `## notes` section for any new
files.

Create any of these from the templates below if they don't exist.

## Offer gap analysis

After completing all writes, offer:

> "Want me to do a gap analysis on any of these topics against the existing formal docs in this
> repo?"

If yes: find the formal docs for the topic (search the repo outside `notes/`), compare with the
matching note file, and report the **formal state** (what the docs say is implemented), the
**discussed state** (what the notes say was agreed or planned), the **gap**, and **suggested
steps**.

## Templates

<details>
<summary><code>notes/index.md</code></summary>

```markdown
---
title: Notes
description: Informal meeting notes, decisions, and discussions organised by OU. Used for gap analysis between formal documentation and discussed/intended state.
audience: [team, ai-agents]
last_reviewed: YYYY-MM-DD
status: active
---

# Notes

Informal notes from meetings and working sessions, organised to mirror the repo's folder
structure. Formal documentation lives in the parent folders; these notes capture what was
discussed, decided, and planned.

## How to use for gap analysis

When asked "what state is [topic] in?":
1. Read the formal doc in the relevant OU folder
2. Read the matching note in `notes/<ou>/<topic>.md`
3. The note's **Gap Analysis** table shows what's documented vs. what's been discussed
4. **Open Actions** shows what still needs to be done

## Structure

### [Transcripts](transcripts/README.md)
Original source files and clean narrative summaries.

| Date | Meeting |
|------|---------|
| — | — |

## OUs

<!-- Add an H3 and table per OU as notes are added -->

## Adding new notes
Use the `/notes` skill with a transcript and this repo path.
```

</details>

<details>
<summary><code>notes/transcripts/README.md</code></summary>

```markdown
# Transcripts

Original source files and clean narrative summaries from meetings and working sessions.

| Date | Summary | Source file |
|------|---------|-------------|
| — | — | — |
```

</details>

<details>
<summary>OU <code>README.md</code></summary>

```markdown
# Notes: <OU Name>

Informal notes on <OU topic> from meetings and working sessions.

| Topic | Last Updated |
|-------|-------------|
| — | — |
```

</details>

## What this must never do

- Never overwrite an existing note file — always append a new dated section
- Never delete notes
- Never create a note without a date — infer it or ask
- Never duplicate action items across OU folders — one OU owns each action item
- Never write formal documentation (runbooks, policies, procedures) — notes are informal records
- Never assume a default repo path — always confirm if not provided
- Never write secrets, credentials, or PII into note files
