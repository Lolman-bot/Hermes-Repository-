# PDF to Markdown

Convert PDF files to Markdown with **pymupdf4llm, run inside Ubuntu WSL**, with an automatic
**OCR pre-pass** (ocrmypdf + tesseract) for scanned or image-only pages.

Toolchain check, install command, path translation, file listing and the test-one-then-batch rule
are shared — see [WSL Conversion Toolchain](wsl-conversion-toolchain.md).

> **Note**
> pandoc can't read PDF input directly — it has no PDF reader — which is why this uses a dedicated
> Python engine rather than the same tool as DOCX to Markdown (see the `/docx-to-md` skill).


## The two variants

### `/pdf-to-md`

**Text only.** No image extraction, no assets folder, no image links.

Never pass `--images-dir`. If the user wants images, hand off to the rich variant rather than
adding the flag here.

### `/pdf-to-md-rich`

**High fidelity.** Every embedded image, diagram and screenshot extracted into an assets folder
and linked inline, via `--images-dir`.

Same engine, same OCR pre-pass, same cleanup pass.

Activate the rich variant only on an explicit request — "/pdf-to-md-rich", "convert with images",
"keep the diagrams". Generic phrasing like "convert this pdf to markdown" goes to the plain
text-only variant.

## Converting

For each `<file>.pdf`, run the helper script in WSL. It auto-detects scanned pages and OCRs them
first, then converts.

### Text only (/pdf-to-md)

```bash
wsl.exe -d Ubuntu bash -lc 'export PATH="$HOME/.venvs/pdf2md/bin:$PATH" && cd "/mnt/c/PATH/TO/folder" && "$HOME/.venvs/pdf2md/bin/python" "<skill-dir-in-wsl>/scripts/pdf_to_md.py" "<file>.pdf" "<file>.md"'
```

### With images (/pdf-to-md-rich)

```bash
wsl.exe -d Ubuntu bash -lc 'export PATH="$HOME/.venvs/pdf2md/bin:$PATH" && cd "/mnt/c/PATH/TO/folder" && "$HOME/.venvs/pdf2md/bin/python" "<skill-dir-in-wsl>/scripts/pdf_to_md.py" "<file>.pdf" "<file>.md" --images-dir "assets/<file-slug>"'
```

> **Warning**
> **Always export the venv's `bin/` onto `PATH` first.** The script shells out to the `ocrmypdf`
> CLI, and without this it fails with `[Errno 2] No such file or directory: 'ocrmypdf'` on any file
> that needs OCR.


`<skill-dir-in-wsl>` is this skill's installed folder (under `$HERMES_HOME/skills/`) translated
to its `/mnt/<drive>/…` form — see the path-translation section of the toolchain page.

The script prints `OK ocr=<yes|no> pages=<n>` on success, or `ERROR <message>` on failure.

### OCR modes

- `--ocr auto` (the default) only OCRs pages without an extractable text layer — safe for both
  fully-scanned and mixed documents.
- `--ocr force` flattens each page to an image and OCRs it whole.
- `--ocr skip` skips OCR entirely, when the user knows a PDF is text-only and wants it faster.

Scanned-page OCR is slower per file than a purely text-based PDF — mention this when converting
many scanned documents.

### Design-heavy PDFs

A PDF exported from a slide deck with per-phrase build animations, or a photo-heavy deck, can
confuse pymupdf4llm's layout classifier. Body text sitting inside a graphic or background element
gets emitted as `<!-- Start of picture text -->` … `<!-- End of picture text -->` fragments
instead of flowing into the paragraph.

This happens regardless of image extraction — it's driven by text layout classification, not by
the images. If the first file's `.md` is full of these, re-run it with `--ocr force`; flattening
each page often reads as more continuous prose. Some blocks typically remain either way.

## The picture-text cleanup pass — required, every file

> **Important**
> **No `<!-- Start of picture text -->` / `<!-- End of picture text -->` markup may remain in the
> final `.md`.** This pass is what distinguishes the skill from a bare script invocation. Read the
> converted file and resolve every block by judgment — a mechanical flag can't tell genuine content
> from noise.


**Genuine content** — a real sentence, paragraph or table that happens to sit over a background
shape or design element. Strip the comment markers and the `<br>` join tags, and reflow it as a
normal paragraph in place, in plain prose. If a picture-text block only repeats a phrase already
fully covered by the surrounding paragraph — common on animated build-style decks, where each
reveal step re-emits a growing subset of the same sentence — delete the block instead of
duplicating the sentence.

**Garbled OCR noise** — tesseract misreading a decorative photo, artwork or background graphic
that never contained real text. Recognisable as strings of near-random characters, punctuation or
symbols (e.g. `{ . | 7 ' ——— = = ——a ~ =SN`, or a wall of stray `~~`/`<`/`@`). Delete it
entirely, along with any stray noise lines sitting *outside* a picture-text block that came from
the same source image — OCR sometimes leaks fragments into the surrounding flow.

**Repeated logo/footer misreads** — the same logo or footer OCR'd slightly differently on every
page (e.g. "PA Mirvac" / "PP rIrVac" / "PHA mirvac" all being one footer logo). Collapse to
nothing, or at most one clean mention.

**In the rich variant, leave the `![]()` image links and the `assets/<file-slug>/` files
untouched.** This cleanup is text-only — it removes text pymupdf4llm found sitting inside
picture-classified *regions* of the page, and has nothing to do with the extracted image files.

> **Note**
> When genuinely unsure whether a fragment is real content, **keep it** (lightly cleaned) rather
> than delete it. The goal is a readable, markup-free document, not maximum aggressiveness. This is
> a judgment pass, not a lossless transform — so say roughly what was removed when reporting.


## Report

After each file, and as a summary at the end:

- ✅ `<file>.pdf → <file>.md` — ocr yes/no, pages n, and what the cleanup did, e.g. "stripped
  picture-text markup from 6 blocks, removed 3 blocks of OCR noise from decorative images".
- ⚠️ anything needing a human check: OCR'd content to verify, misdetected headings, unusual table
  layouts, any borderline picture-text judgment call.
- ❌ any file that errored — show the `ERROR` message and continue with the rest.

Then review the `.md`:

- Headings look sensible. pymupdf4llm infers them from font size, so a subtitle or pull-quote
  occasionally gets promoted — demote if so.
- Tables rendered as Markdown tables, not garbled text.
- No `<!-- Start/End of picture text -->` markup survived.
- If the source was OCR'd, spot-check a paragraph against the original. OCR isn't perfect,
  especially on low-quality scans.
