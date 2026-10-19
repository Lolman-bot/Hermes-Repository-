---
name: notes
description: "Use when filing a transcript to notes/. Splits items by OU."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, notes, meetings, transcripts, documentation, action-items]
    category: bitpool
    related_skills: [bitpool-docs, gitbook-docs, transcribe-video]
---

# Notes

Processes a meeting transcript or document (`.vtt`, `.txt`, `.md`, `.pdf`, or pasted content) and
distributes structured notes into the matching organisational unit (OU) subfolders of the target
repo's `notes/` section. The OU structure is discovered from the repo itself — no folder names are
hardcoded. The parsing rules, note format and templates ship with this skill in `references/`.

Usage: `/notes [transcript-path] [repo-path]` — both arguments are optional; the skill asks for
anything missing.

## When to Use

- The user runs `/notes`.
- The user shares a transcript and asks to add it to a docs repo.

Don't use for:
- Questions about existing notes, or general questions unrelated to processing a document.
- A meeting of a cross-OU project in `bitpool-projects`: hand it to `/bitpool-docs` (rule 9).
- Formal documentation — runbooks, policies, procedures: use `/bitpool-docs` (or `/isms-draft`).
- Turning a video into a transcript first: use `/transcribe-video`.

## Procedure

1. **Collect the two inputs** (rule 1) — the transcript (path or pasted) and the target repo root.
   Ask with `clarify` for anything missing; never assume a default. Done when both are known and the
   repo root exists. If the repo is `bitpool-projects`, stop and hand off to `/bitpool-docs`.
2. **Read the method** — `references/meeting-notes-distribution.md` with `read_file`, the whole file,
   before writing any file. Done when it has been read this run.
3. **Discover the OUs** — list the repo's top-level folders with `search_files` / `terminal`,
   applying the exclusions in the reference, plus the implicit `misc`. Done when the OU list is
   written out.
4. **Read the transcript** with `read_file` (PDFs included) and **date it** (rule 5). Done when the
   meeting has a `YYYY-MM-DD` date from the filename, metadata or content, or the user gave one.
5. **Store the original** in `notes/transcripts/` with its clean narrative `.md` summary, and add
   the row to `notes/transcripts/README.md` (rule 6). Done when all three exist.
6. **Classify and distribute** — action items to exactly one OU, context to one or more, the rest
   to `notes/misc/`, using the reference's note file format and templates. Append to existing note
   files, never overwrite (rule 4). Done when every extracted item sits in a file.
7. **Update the indexes** — `notes/index.md`, and the repo's `SUMMARY.md` if it has one (load
   `/gitbook-docs` before touching it). Done when every OU that received content is indexed.
8. **Report and offer the gap analysis** described in the reference. Done when the user has the
   list of files touched and the offer.

## Load-bearing rules

These are the invariants the whole notes system depends on.

1. **Never assume a default repo path.** Ask for anything missing — transcript and repo root both.
2. **Action items live in exactly ONE OU** — the most responsible one. Never duplicated across folders; link instead.
3. **Notes and context can appear in one or more OUs.** Unclassifiable items go to `notes/misc/`.
4. **Never overwrite an existing note file.** Append a new dated `## YYYY-MM-DD — Meeting Name` section under the existing `## Discussions` heading.
5. **Never create a note without a date.** Infer it from the filename, metadata or content — or ask.
6. **The original file is always stored** in `notes/transcripts/`, with a clean narrative `.md` summary alongside it.
7. **These are informal records.** Never write formal documentation — runbooks, policies, procedures — from here.
8. **Never write secrets, credentials or PII** into a note file. **Never delete notes.**
9. **`bitpool-projects` is not an OU repo.** Its top-level folders are projects, not OUs, and it has no `notes/` tree. If the target repo is `bitpool-projects`, stop and hand the transcript to `/bitpool-docs`, which records the meeting as a `Note` page in the project's own folder.

## Pitfalls

- **Improvising the note file format or a template from memory.** An inconsistent note file breaks
  the repo's gap-analysis reading; copy the templates from the reference.
- **Duplicating an action item** into every OU it touches. One home, links elsewhere.
- **Treating `_meta`, `.git`, `notes` or build folders as OUs.** Apply the reference's exclusion list.
- **Overwriting a note file** when a topic already has one — always append a dated section.
- **Carrying VTT markup or raw timestamps** into the narrative summary.

## Verification

- The original transcript and its narrative summary are in `notes/transcripts/`, and the README row
  exists.
- Every action item appears in exactly one OU file; every note file section is dated.
- No existing note file lost content; `notes/index.md` (and `SUMMARY.md` if present) list the new files.
- No secret, credential or PII was written.

## Reference files

Read the file itself — the table is an index, not a substitute.

| File | Covers |
|---|---|
| `references/meeting-notes-distribution.md` | How a meeting transcript is parsed and distributed into a documentation repo's notes/ folder — OU discovery, item classification, the note file format, index updates, and the templates. |

**Editing this skill:** parsing rules, note file format, templates and index updates live in
`references/meeting-notes-distribution.md`. Publish through `/edit-skill`.
