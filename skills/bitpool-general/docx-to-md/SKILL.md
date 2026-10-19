---
name: docx-to-md
description: "Use when converting Word .docx files to Markdown."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [windows]
metadata:
  hermes:
    tags: [bitpool, conversion, docx, markdown, pandoc, wsl]
    category: bitpool
    related_skills: [pdf-to-md, isms-draft]
---

# docx-to-md

Convert Word `.docx` files to Markdown with **pandoc, run inside Ubuntu WSL** — real headings, bullets, tables and image extraction. Basic and explicit: check pandoc, list the files, then loop through them one at a time.

The commands and review pass ship with this skill in `references/`. Output is a `.md` next to each `.docx`, with no frontmatter.

## When to Use

- The user runs `/docx-to-md`, or asks to "convert these docx to markdown" / "convert the docx in [folder]".
- One `.docx` file or a folder of them. The default target is the Bitpool ISMS draft area, but any folder or single file works.

Don't use for:
- PDFs: use `/pdf-to-md` (text only) or `/pdf-to-md-rich` (with images).
- Adding ISMS policy frontmatter or moving a draft through the ISMS lifecycle: use `/isms-draft`.
- Creating, editing or inspecting a Word document itself (not converting it): use the bundled `/docx` skill.

## Prerequisites

- Windows host with **Ubuntu WSL** (`wsl.exe -d Ubuntu`). Hermes's `terminal` on Windows is git-bash, which calls `wsl.exe` directly.
- **pandoc installed inside WSL.** The check and the user's copy-paste install command are in `references/wsl-conversion-toolchain.md`.

## Procedure

1. **Run the toolchain check** from `references/wsl-conversion-toolchain.md` (docx-to-md section) with `terminal`. Done when it prints a pandoc version — or, on `MISSING`, you have stopped and given the user the install command (rule 1).
2. **Read the method** — `read_file` the whole of `references/docx-to-markdown.md` and `references/wsl-conversion-toolchain.md` before converting anything. Skimming for the line you expect is how a flag gets missed. Done when both are read this run.
3. **Resolve the target.** Use the folder or file the user named, otherwise the default ISMS draft folder in `references/docx-to-markdown.md`; translate it to its `/mnt/<drive>/…` form. Done when you have a quoted WSL path.
4. **List the files and show them** (rule 2). Skip `~$*.docx` lock files and any `.docx` with a sibling `.md`; top level only unless the user includes subfolders. Done when the user has seen the count and list.
5. **Convert one file** with the exact pandoc command in `references/docx-to-markdown.md` (`-t gfm`, `--extract-media`, `--wrap=none`), then run the review pass on it. Done when the `.md` exists, its first heading is the H1 title, and the user has been asked to inspect it.
6. **Batch the rest** only after the user confirms the test file looks right; review each one. Done when every listed file is converted or reported as failed.
7. **Report** per file and as a summary, in the ✅ / ⚠️ format in `references/docx-to-markdown.md`. Done when every file has a line.

## Load-bearing rules

Each one prevents a silent data problem.

1. **pandoc-only, no fallback.** If the check prints `MISSING`, **stop** — convert nothing — and give the user the install command to run themselves. Setup needs sudo; never attempt `apt`/`sudo` yourself.
2. **Show the file list before converting.** Skip Word lock files (`~$*.docx`) and any `.docx` that already has a sibling `.md`, unless the user says re-convert.
3. **Test one, then batch.** Convert one file, let the user inspect it, and wait for confirmation before looping the rest.
4. **Never add YAML frontmatter.** This produces the Markdown body only — `/isms-draft` adds policy frontmatter, and doing it twice has to be unpicked by hand.
5. **Never overwrite an existing `.md` without confirmation**, and never move or delete the source `.docx`.
6. **Don't push anywhere.** Conversion only.

## Pitfalls

- **Improvising the pandoc flags.** `-t gfm`, `--extract-media` and `--wrap=none` each do a specific job; dropping one silently degrades the output.
- **Letting git-bash expand variables meant for WSL.** Keep the WSL-side command in single quotes, exactly as written in the reference.
- **Unquoted paths.** Bitpool folder names contain spaces (`ISMS - Draft`); quote the whole `/mnt/...` path.
- **Leaving pandoc artefacts** — `{.underline}`, empty `[]{#anchor}` spans, stray `:::` divs. The review pass trims them.
- **Falling back to another converter** (python-docx, LibreOffice, the bundled `/docx` skill) when pandoc is missing. There is no fallback — stop instead.

## Verification

- The toolchain check printed a pandoc version this run.
- Each converted `.md` sits next to its `.docx`, has an H1 title, rendered tables as Markdown tables, and has no YAML frontmatter.
- Images (if any) are under `assets/<file-slug>/` and linked.
- No source `.docx` was moved or deleted; no existing `.md` was overwritten without confirmation.

## Reference files

Read the file itself — the table is an index, not a substitute.

| File | Covers |
|---|---|
| `references/docx-to-markdown.md` | Converting Word .docx files to Markdown with pandoc in WSL — the default folder, the flags that matter, the post-conversion review, and why frontmatter is deliberately left off. |
| `references/wsl-conversion-toolchain.md` | The shared mechanics behind the WSL-backed conversion skills — toolchain checks and their copy-paste install commands, Windows→WSL path translation, the file-listing rules, and the test-one-then-batch discipline. |

Toolchain check, install command, path translation, batching → edit `references/wsl-conversion-toolchain.md` (it is shared with `/pdf-to-md`, `/pdf-to-md-rich` and `/transcribe-video`; keep all copies identical). pandoc flags, default folder, review pass → edit `references/docx-to-markdown.md`.
