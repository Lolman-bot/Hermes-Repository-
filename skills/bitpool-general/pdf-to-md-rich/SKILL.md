---
name: pdf-to-md-rich
description: "Use when converting PDFs to Markdown keeping images."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [windows]
metadata:
  hermes:
    tags: [bitpool, conversion, pdf, markdown, ocr, images, pymupdf4llm, wsl]
    category: bitpool
    related_skills: [pdf-to-md, docx-to-md]
---

# pdf-to-md-rich

Convert PDF files to Markdown with **pymupdf4llm, run inside Ubuntu WSL**, with an automatic **OCR pre-pass** (ocrmypdf + tesseract) for scanned/image-only pages — **and every embedded image extracted** into `assets/<file-slug>/` and linked inline.

This is the image-extracting sibling of `/pdf-to-md`: same engine, OCR pre-pass and cleanup pass; the only difference is `--images-dir`. The method ships in `references/`; the driver is `scripts/pdf_to_md.py`.

## When to Use

- **Only** the slash command `/pdf-to-md-rich`, or an explicit request to keep/extract images, diagrams, figures or screenshots ("convert this pdf and keep the images", "convert with images", "keep the diagrams").
- Any folder or single file — there is no default folder; ask if none was given.

Don't use for:
- Generic "convert this pdf to markdown" with no mention of images: that goes to `/pdf-to-md` (text only).
- Word documents: use `/docx-to-md`.
- Creating, merging, filling or editing PDFs themselves: use the bundled `/pdf` skill.

## Prerequisites

- Windows host with **Ubuntu WSL** (`wsl.exe -d Ubuntu`). Hermes's `terminal` on Windows is git-bash, which calls `wsl.exe` directly.
- The **pdf2md venv** in WSL (`~/.venvs/pdf2md` with pymupdf4llm + ocrmypdf) plus `tesseract-ocr`, `ghostscript`, `qpdf`. The check and the user's install command are in `references/wsl-conversion-toolchain.md` (the pdf-to-md section covers both variants).

## Procedure

1. **Run the toolchain check** from `references/wsl-conversion-toolchain.md` (pdf-to-md section) with `terminal`. Done when it prints `OK` — or, on `MISSING`, you have stopped and given the user the install command (rule 1).
2. **Read the method** — `read_file` the whole of `references/pdf-to-markdown.md` (including the cleanup rules) and `references/wsl-conversion-toolchain.md`. Done when both are read this run.
3. **Resolve paths.** Translate the input folder/file to `/mnt/<drive>/…`. Locate this skill's installed `scripts/pdf_to_md.py` under `$HERMES_HOME/skills/` (use `search_files`) and translate it too. Done when both WSL paths are quoted and known.
4. **List the PDFs and show them**, skipping any with a sibling `.md` unless told to re-convert. Done when the user has seen the count and list.
5. **Convert one file** with the with-images command in `references/pdf-to-markdown.md` — PATH export first, `--images-dir "assets/<file-slug>"`. Done when the script prints `OK ocr=<yes|no> pages=<n>` and `assets/<file-slug>/` exists.
6. **Run the text-only cleanup pass** on that `.md` with `read_file` + `patch`/`write_file`, following the cleanup rules exactly and leaving every image link alone. Done when `search_files` finds no `picture text` markup and the `![](...)` link count is unchanged.
7. **Show the user the test file and wait.** If it is full of picture-text blocks, offer a re-run with `--ocr force`. Done when the user confirms.
8. **Batch the rest**, converting then cleaning each; report and continue past failures. Done when every listed file is converted-and-cleaned or reported as `ERROR`.
9. **Report** per file and as a summary in the ✅ / ⚠️ / ❌ format in `references/pdf-to-markdown.md`, including the assets folder and roughly what the cleanup removed. Done when every file has a line.

## Load-bearing rules

Each one prevents shipping a broken or misleading document.

1. **pymupdf4llm-only, no fallback.** If the check prints `MISSING`, **stop** — convert nothing — and give the user the install command to run themselves. Setup needs sudo; never attempt `apt`/`sudo` yourself.
2. **Pass `--images-dir "assets/<file-slug>"`.** That flag is the whole difference from the plain variant.
3. **Export the venv's `bin/` onto `PATH` before running the script.** Without it, any file needing OCR fails with `[Errno 2] No such file or directory: 'ocrmypdf'`.
4. **The cleanup pass is mandatory for every file.** No `<!-- Start/End of picture text -->` markup may survive into the final `.md`.
5. **The cleanup is text-only.** Leave every `![]()` link and every file in `assets/<file-slug>/` exactly as the script wrote them — this step removes text found inside picture-classified *regions*, not images.
6. **When unsure whether a fragment is real content, keep it** (lightly cleaned). Say roughly what was removed when reporting.
7. **Show the file list before converting**, skipping any `.pdf` that already has a sibling `.md` unless told to re-convert. **Test one, then batch.**
8. **Never overwrite an existing `.md` without confirmation**, never move or delete the source `.pdf`, never add frontmatter, and don't push anywhere.

## Pitfalls

- **Activating on generic phrasing.** "Convert this pdf to markdown" belongs to `/pdf-to-md`; this variant is for explicit image requests only.
- **Reconstructing the driver from prose.** Run `scripts/pdf_to_md.py` as shipped; a paraphrased script is a broken script.
- **Letting the cleanup touch images.** Picture-text markup is about text regions; deleting a `![]()` link or an asset file is a data loss.
- **Running the script with Windows Python**, or letting git-bash expand `$HOME`/`$PATH` — keep the WSL-side command in single quotes, exactly as in the reference.
- **Trusting inferred headings or OCR text** — demote promoted pull-quotes and spot-check OCR'd paragraphs.

## Verification

- The toolchain check printed `OK` this run, and each file's script run printed `OK ocr=… pages=…`.
- `search_files` for `picture text` across the produced `.md` files returns nothing.
- Every `![](...)` link in each `.md` resolves to a file under `assets/<file-slug>/`.
- No source `.pdf` moved or deleted; no existing `.md` overwritten without confirmation; no frontmatter added.

## Reference files

Read the file itself — the table is an index, not a substitute.

| File | Covers |
|---|---|
| `references/pdf-to-markdown.md` | Converting PDFs to Markdown with pymupdf4llm in WSL — the OCR pre-pass and modes, the text-only vs image-extracting variants, the exact commands, and the mandatory picture-text cleanup. |
| `references/wsl-conversion-toolchain.md` | The shared mechanics behind the WSL-backed conversion skills — toolchain checks and their copy-paste install commands, Windows→WSL path translation, the file-listing rules, and the test-one-then-batch discipline. |
| `scripts/pdf_to_md.py` | The conversion + OCR + image-extraction driver, executed in WSL with the pdf2md venv's Python. Copy it; never reconstruct it. |

Toolchain, path translation, batching → edit `references/wsl-conversion-toolchain.md` (shared with `/docx-to-md`, `/pdf-to-md`, `/transcribe-video`; keep copies identical). OCR modes, cleanup rules, the variant difference → edit `references/pdf-to-markdown.md`. The driver → edit `scripts/pdf_to_md.py` here and in `/pdf-to-md`.
