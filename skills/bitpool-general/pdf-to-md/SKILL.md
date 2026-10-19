---
name: pdf-to-md
description: "Use when converting PDFs to text-only Markdown."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [windows]
metadata:
  hermes:
    tags: [bitpool, conversion, pdf, markdown, ocr, pymupdf4llm, wsl]
    category: bitpool
    related_skills: [pdf-to-md-rich, docx-to-md]
---

# pdf-to-md

Convert PDF files to Markdown with **pymupdf4llm, run inside Ubuntu WSL**, with an automatic **OCR pre-pass** (ocrmypdf + tesseract) for scanned/image-only pages. Text-only output: real headings and tables, no image extraction, no assets folder, no image links.

Every converted file then gets a mandatory **cleanup pass** that removes picture-text markup and OCR noise by judgment. The method ships in `references/`; the driver is `scripts/pdf_to_md.py`.

## When to Use

- The user runs `/pdf-to-md`, or asks to "convert this pdf to markdown", "convert the pdfs in [folder]", "turn this PDF into a .md file".
- Any folder or single file — there is no default folder; ask if none was given.

Don't use for:
- Keeping embedded images, diagrams or screenshots: use `/pdf-to-md-rich` (same engine, `--images-dir` on). Only on an explicit request for images.
- Word documents: use `/docx-to-md`.
- Creating, merging, filling or editing PDFs themselves: use the bundled `/pdf` skill.

## Prerequisites

- Windows host with **Ubuntu WSL** (`wsl.exe -d Ubuntu`). Hermes's `terminal` on Windows is git-bash, which calls `wsl.exe` directly.
- The **pdf2md venv** in WSL (`~/.venvs/pdf2md` with pymupdf4llm + ocrmypdf) plus `tesseract-ocr`, `ghostscript`, `qpdf`. The check and the user's install command are in `references/wsl-conversion-toolchain.md`.

## Procedure

1. **Run the toolchain check** from `references/wsl-conversion-toolchain.md` (pdf-to-md section) with `terminal`. Done when it prints `OK` — or, on `MISSING`, you have stopped and given the user the install command (rule 1).
2. **Read the method** — `read_file` the whole of `references/pdf-to-markdown.md` (including the cleanup rules) and `references/wsl-conversion-toolchain.md`. Done when both are read this run.
3. **Resolve paths.** Translate the input folder/file to `/mnt/<drive>/…`. Locate this skill's installed `scripts/pdf_to_md.py` under `$HERMES_HOME/skills/` (use `search_files`) and translate it too. Done when both WSL paths are quoted and known.
4. **List the PDFs and show them**, skipping any with a sibling `.md` unless told to re-convert. Done when the user has seen the count and list.
5. **Convert one file** with the text-only command in `references/pdf-to-markdown.md` — PATH export first, **no `--images-dir`**. Done when the script prints `OK ocr=<yes|no> pages=<n>`.
6. **Run the cleanup pass** on that `.md` with `read_file` + `patch`/`write_file`, following the cleanup rules exactly. Done when `search_files` finds no `picture text` markup in it.
7. **Show the user the test file and wait.** If it is full of picture-text blocks, offer a re-run with `--ocr force`. Done when the user confirms.
8. **Batch the rest**, converting then cleaning each; report and continue past failures. Done when every listed file is converted-and-cleaned or reported as `ERROR`.
9. **Report** per file and as a summary in the ✅ / ⚠️ / ❌ format in `references/pdf-to-markdown.md`, including roughly what the cleanup removed. Done when every file has a line.

## Load-bearing rules

Each one prevents shipping a broken or misleading document.

1. **pymupdf4llm-only, no fallback.** If the check prints `MISSING`, **stop** — convert nothing — and give the user the install command to run themselves. Setup needs sudo; never attempt `apt`/`sudo` yourself.
2. **Never pass `--images-dir`.** That flag is what makes this variant text-only. If the user wants images, hand off to `/pdf-to-md-rich` rather than adding it here.
3. **Export the venv's `bin/` onto `PATH` before running the script.** Without it, any file needing OCR fails with `[Errno 2] No such file or directory: 'ocrmypdf'`.
4. **The cleanup pass is mandatory for every file.** No `<!-- Start/End of picture text -->` markup may survive into the final `.md`. Genuine content is reflowed as prose; OCR noise from decorative graphics is deleted; repeated logo/footer misreads are collapsed.
5. **When unsure whether a fragment is real content, keep it** (lightly cleaned). This is a judgment pass, not a lossless transform — say roughly what was removed when reporting.
6. **Show the file list before converting**, skipping any `.pdf` that already has a sibling `.md` unless told to re-convert. **Test one, then batch.**
7. **Never overwrite an existing `.md` without confirmation**, never move or delete the source `.pdf`, never add frontmatter, and don't push anywhere.

## Pitfalls

- **Reconstructing the driver from prose.** Run `scripts/pdf_to_md.py` as shipped; a paraphrased script is a broken script.
- **Skipping the cleanup pass.** It is what distinguishes this skill from a bare script invocation.
- **Running the script with Windows Python.** It runs inside WSL with the venv's Python; the Windows side has no pymupdf.
- **Letting git-bash expand `$HOME`/`$PATH`.** Keep the WSL-side command in single quotes, exactly as in the reference.
- **Trusting inferred headings.** pymupdf4llm infers headings from font size; a subtitle or pull-quote can get promoted — demote it.
- **Treating OCR as exact.** Spot-check an OCR'd paragraph against the original.

## Verification

- The toolchain check printed `OK` this run, and each file's script run printed `OK ocr=… pages=…`.
- `search_files` for `picture text` across the produced `.md` files returns nothing.
- No `assets/` folder and no `![](...)` image links were created.
- No source `.pdf` moved or deleted; no existing `.md` overwritten without confirmation; no frontmatter added.

## Reference files

Read the file itself — the table is an index, not a substitute.

| File | Covers |
|---|---|
| `references/pdf-to-markdown.md` | Converting PDFs to Markdown with pymupdf4llm in WSL — the OCR pre-pass and modes, the text-only vs image-extracting variants, the exact commands, and the mandatory picture-text cleanup. |
| `references/wsl-conversion-toolchain.md` | The shared mechanics behind the WSL-backed conversion skills — toolchain checks and their copy-paste install commands, Windows→WSL path translation, the file-listing rules, and the test-one-then-batch discipline. |
| `scripts/pdf_to_md.py` | The conversion + OCR driver, executed in WSL with the pdf2md venv's Python. Copy it; never reconstruct it. |

Toolchain, path translation, batching → edit `references/wsl-conversion-toolchain.md` (shared with `/docx-to-md`, `/pdf-to-md-rich`, `/transcribe-video`; keep copies identical). OCR modes, cleanup rules, reporting → edit `references/pdf-to-markdown.md`. The driver → edit `scripts/pdf_to_md.py` here and in `/pdf-to-md-rich`.
