# DOCX to Markdown

Convert Word `.docx` files to Markdown with **pandoc, run inside Ubuntu WSL**. High fidelity:
real headings, bullets, tables and image extraction.

Toolchain check, install command, path translation, file listing and the test-one-then-batch rule
are shared — see [WSL Conversion Toolchain](wsl-conversion-toolchain.md).

## Default target folder

Override if the user names another:

```
C:\BitpoolDev\Github-Bitpool\security-documentation\ISMS\ISMS - Draft
```

In WSL form:

```
/mnt/c/BitpoolDev/Github-Bitpool/security-documentation/ISMS/ISMS - Draft
```

## Converting

For each `<file>.docx`, output `<file>.md` next to it and extract images into
`assets/<file-slug>/`:

```bash
wsl.exe -d Ubuntu bash -lc 'cd "/mnt/c/PATH/TO/folder" && pandoc -f docx -t gfm "<file>.docx" -o "<file>.md" --extract-media="assets/<file-slug>" --wrap=none'
```

| Flag | Why |
|---|---|
| `-t gfm` | GitHub-flavoured Markdown — clean tables, portable |
| `--extract-media` | Pulls embedded images out into the assets folder and links them |
| `--wrap=none` | No hard line wrapping, for cleaner diffs |

## Review each file

- Make the first heading the document **title** (H1).
- Trim pandoc artefacts if present: `{.underline}`, empty `[]{#anchor}` spans, stray `:::` divs.
- Confirm the **Document Version Control** table and any other tables rendered as Markdown tables.

> **Warning**
> **Do not add YAML frontmatter here.** This produces the Markdown body only. For ISMS policy
> drafts, `/isms-draft` adds the policy frontmatter — adding it twice creates a conflict that has
> to be unpicked by hand.


## Report

After each file, and as a summary at the end:

- ✅ `<file>.docx → <file>.md`, plus images extracted to `assets/<file-slug>/` if any
- ⚠️ anything needing a human check: complex tables, unusual formatting, artefacts that couldn't
  be auto-cleaned

Don't move or delete the `.docx` — the ISMS lifecycle handles that via `/isms-draft`.
