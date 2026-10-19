# WSL Conversion Toolchain

Four Bitpool skills — `/docx-to-md`, `/pdf-to-md`, `/pdf-to-md-rich` and `/transcribe-video` —
all run their engine inside **Ubuntu WSL** and share the same shape: check the toolchain, list
the files, convert one at a time, report. This page holds the parts they have in common.

> **Important**
> Every one of these skills is **engine-only with no fallback**. If the toolchain isn't available
> in WSL, **stop and do not convert anything.** Setup needs `sudo`, so the user runs it — never
> attempt `apt` or `sudo` yourself.


## Toolchain checks and install commands

### docx-to-md (pandoc)

Check:

```bash
wsl.exe -d Ubuntu bash -lc "command -v pandoc >/dev/null && pandoc --version | head -1 || echo MISSING"
```

A pandoc version → continue. `MISSING` → give the user this:

> **pandoc isn't installed in WSL. Paste this into a terminal, then re-run `/docx-to-md`:**

```powershell
wsl -d Ubuntu -- bash -lc "sudo apt-get update && sudo apt-get install -y pandoc && pandoc --version | head -1"
```

### pdf-to-md (pymupdf4llm)

The Python packages live in a dedicated venv at `~/.venvs/pdf2md` so they're isolated from the
system Python — Ubuntu's is externally-managed (PEP 668). OCR needs `tesseract-ocr`,
`ghostscript` and `qpdf` as system packages.

Check:

```bash
wsl.exe -d Ubuntu bash -lc '[ -x "$HOME/.venvs/pdf2md/bin/python" ] && "$HOME/.venvs/pdf2md/bin/python" -c "import pymupdf4llm, ocrmypdf" 2>/dev/null && command -v tesseract >/dev/null 2>&1 && echo OK || echo MISSING'
```

`OK` → continue. `MISSING` → give the user this:

> **The PDF→Markdown toolchain isn't set up in WSL yet. Paste this into a terminal, then re-run
> the skill:**

```powershell
wsl -d Ubuntu -- bash -lc 'sudo apt-get update && sudo apt-get install -y tesseract-ocr ghostscript qpdf python3-venv python3-pip && python3 -m venv ~/.venvs/pdf2md && ~/.venvs/pdf2md/bin/pip install --upgrade pip && ~/.venvs/pdf2md/bin/pip install pymupdf4llm ocrmypdf && echo DONE'
```

### transcribe-video (whisper)

`whisper-ctranslate2` lives in a dedicated venv at `~/.venvs/whisper`, for the same PEP 668
reason.

Check:

```bash
wsl.exe -d Ubuntu bash -lc 'command -v ffmpeg >/dev/null && [ -x "$HOME/.venvs/whisper/bin/whisper-ctranslate2" ] && echo OK || echo MISSING'
```

`OK` → continue. `MISSING` → give the user this:

> **The transcription toolchain isn't set up in WSL yet. Paste this into a terminal, then re-run
> `/transcribe-video`:**

```powershell
wsl -d Ubuntu -- bash -lc 'sudo apt-get update && sudo apt-get install -y ffmpeg python3-venv python3-pip && python3 -m venv ~/.venvs/whisper && ~/.venvs/whisper/bin/pip install --upgrade pip && ~/.venvs/whisper/bin/pip install whisper-ctranslate2 && echo DONE'
```

After the user confirms it printed `DONE`, re-run the check and proceed.

## Path translation — Windows → WSL

The engine runs in WSL, so convert Windows paths to `/mnt/<drive>/…`:

- `D:\Projects\Reports` → `/mnt/d/Projects/Reports`
- `C:\BitpoolDev\Github - Bitpool\…` → `/mnt/c/BitpoolDev/Github - Bitpool/…`

Lowercase the drive letter; backslashes become forward slashes; keep spaces and quote the whole
path.

Where a skill ships a helper script next to its `SKILL.md`, resolve it to its actual installed
path and translate that the same way. In Hermes the installed skill folder is under
`$HERMES_HOME/skills/` (typically `$HERMES_HOME/skills/bitpool/<skill>/`); confirm it with
`search_files` for the script name rather than guessing.

Hermes's `terminal` on Windows is git-bash, which can call `wsl.exe` directly. Keep the WSL-side
command in **single quotes** so git-bash doesn't expand `$HOME` / `$PATH` before WSL sees them.

> **Note**
> There is no default target folder for `/pdf-to-md`, `/pdf-to-md-rich` or `/transcribe-video` —
> ask the user for the input folder or single file if they didn't give one. `/docx-to-md` defaults
> to the Bitpool ISMS draft area but works on any folder.


## Listing the files

Always **show the user the list first**, then convert.

- **Skip** a source file that already has a sibling `.md` (already converted) unless the user says
  re-convert. For `.docx`, also skip Word lock files (`~$*.docx`).
- By default list only the **top level**. Mention subfolders if present and ask whether to
  include them.
- Report the count and the list. If nothing matches, say so and ask for the right folder or file.

## Test-one-then-batch

If there are several files, convert or transcribe **one** first, let the user inspect the output,
and **wait**. Do not batch the rest until they confirm it looks right. Then loop the remaining
files.

This matters most where quality is variable: an OCR'd scan, or a Whisper model size that may need
stepping up.

## Shared boundaries

- Write output next to each source file, or to a path the user names. **Never overwrite an
  existing output without confirmation.**
- **Never move or delete the source file.**
- Don't add YAML frontmatter and don't commit or push anything — these skills convert, nothing
  more. For ISMS policy drafts, `/isms-draft` adds the frontmatter.
- If one file errors, report it and continue with the rest.
