---
name: gitbook-docs
description: "Use when editing GitBook-synced docs. Block syntax, SUMMARY."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, gitbook, documentation, markdown, git-sync]
    category: bitpool
    related_skills: [bitpool-docs, notes]
---

# GitBook documentation editing

GitBook spaces can be synced to a Git repo and edited as plain markdown files from Hermes, an editor,
or any Git-synced checkout instead of the GitBook web UI. This skill produces content that renders
correctly in GitBook once pushed — GitBook extends standard markdown with its own block syntax,
frontmatter fields, and a navigation file (`SUMMARY.md`) that has to stay in sync with the file layout.

The full reference ships with this skill in `references/`. The core needed to author safely is
restated below.

## When to Use

- The user asks to edit, create or review docs that live in a GitBook-synced Git repo.
- You see a `.gitbook.yaml`, `SUMMARY.md` or `.gitbook/` directory in a project.
- The user asks about GitBook-specific markdown — hints, tabs, steppers, columns, updates, cards,
  embeds, files, buttons, reusable content blocks, page frontmatter (`description`, `icon`,
  `hidden`, `vars`, `layout`), space/page variables and expressions — even without saying "GitBook".
- Another skill (`/bitpool-docs`, `/notes`) says to load it before writing page content.

Don't use for:
- Deciding *which* Bitpool docs repo or folder content belongs in: use `/bitpool-docs`.
- Filing meeting transcripts: use `/notes`.

## Procedure

1. **Orient before you write** (rule 1): `read_file` the space's `SUMMARY.md`, then `.gitbook.yaml`.
   Done when you know where the root, README and SUMMARY live and whether the page already exists.
2. **Pick the block** from the table below. Done when each piece of content has a block.
3. **Check its exact syntax** in `references/gitbook-custom-blocks.md` (and frontmatter, variables,
   `.gitbook.yaml`, `SUMMARY.md` and assets in `references/gitbook-authoring-basics.md`) before
   writing it. Read the whole file you reach for — tag names make or break rendering, and a
   mismatched tag renders as literal text rather than failing loudly. Done when every tag you use
   was checked against the reference this run.
4. **Write** with `write_file` / `patch`, then re-read the result for unclosed or mismatched tags and
   `SUMMARY.md` indentation. Done when every opening tag has its exact closing tag.
5. **Report honestly** that rendering can only be confirmed after a push (rule 8). Done when the
   report says so for any block or frontmatter change.

If the reference can't answer a question, the local core below is enough for hints, tabs,
frontmatter and `SUMMARY.md`. For anything beyond that, ask the user to paste the GitBook docs
section (or fetch it with `web_extract`) rather than guessing a tag name.

### Which block for which need

| Need | Block |
|---|---|
| Sequential, ordered instructions | `{% stepper %}` |
| Alternatives (languages, platforms, options) | `{% tabs %}` |
| Optional/detailed content that can stay collapsed | `<details><summary>` |
| Warnings, tips, callouts | `{% hint style="..." %}` |
| Side-by-side comparison (max 2) | `{% columns %}` |
| Changelog / dated timeline | `{% updates %}` |
| Clickable navigation cards | `<table data-view="cards">` |
| Downloadable file with a caption | `{% file %}` |
| Primary/secondary call-to-action link | `<a class="button">` |
| Content reused verbatim across pages | `{% include %}` |
| Value that updates automatically | `<code class="expression">` |

Hint styles are `info`, `warning`, `danger`, `success`.

## Load-bearing rules

1. **Read `SUMMARY.md` first, then `.gitbook.yaml`.** `SUMMARY.md` is the full table of contents and the path to every page; `.gitbook.yaml` says where the root, README and SUMMARY actually live. Skipping this is the most common way to break internal links or duplicate a page GitBook already tracks.
2. **Never reference the same markdown file twice in `SUMMARY.md`.** Each page maps to exactly one URL, so GitBook can't resolve a duplicate.
3. **Indent `SUMMARY.md` with spaces, not tabs.** Mixed indentation breaks the nesting.
4. **Always close a custom block, and match the tag name exactly.** `{% endtab %}` where `{% endtabs %}` is needed renders as literal text.
5. **With Git Sync on, edit `README.md` only through the repo**, never also in the GitBook UI.
6. **OpenAPI specs cannot be pasted into markdown.** They must be uploaded via the GitBook API, CLI or UI first.
7. **Prefer `{% columns %}` over a raw markdown table** for parallel content — tables render awkwardly in GitBook's UI editor. Reserve real tables for actual tabular data.
8. **GitBook can't be rendered locally.** If a block or frontmatter change needs verifying, say plainly that it can only be confirmed after a push — don't assert it renders correctly just because the syntax matches the reference.

## Pitfalls

- **Guessing a tag name from memory.** A wrong tag doesn't error; it shows up as literal `{% ... %}`
  text on the published page.
- **Hand-editing a generated `SUMMARY.md`.** Some repos (the Bitpool docs repos) regenerate it with
  their own script; check before editing and run the script instead.
- **Tabs in `SUMMARY.md`.** They silently flatten the navigation tree.
- **Editing `README.md` in both the UI and the repo** under Git Sync — the two copies conflict.
- **Claiming it renders.** Matching syntax is not proof; only a push shows it.

## Verification

- `SUMMARY.md` and `.gitbook.yaml` were read before writing.
- Every custom block used has its exact closing tag and was checked against `references/`.
- No file is listed twice in `SUMMARY.md`, and its indentation is spaces only.
- The report says rendering is confirmed only after a push.

## Reference files

Read the file itself — the table is an index, not a substitute.

| File | Covers |
|---|---|
| `references/gitbook-authoring-basics.md` | How a GitBook-synced repo is laid out and configured — orientation before editing, file layout, page frontmatter, variables and expressions, .gitbook.yaml, SUMMARY.md, the .gitbook directory, and base markdown. |
| `references/gitbook-custom-blocks.md` | Full syntax for every GitBook block — tabs, steppers, hints, expandables, columns, updates, cards, embeds, files, buttons, icons, reusable content and OpenAPI — plus the common pitfalls and what can only be verified after a push. |

**Editing this skill:** block syntax, frontmatter fields, variables and SUMMARY rules live in the two
reference files; keep the core above in sync when a load-bearing rule changes. Publish through
`/edit-skill`.
