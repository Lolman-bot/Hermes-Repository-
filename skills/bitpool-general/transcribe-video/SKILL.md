---
name: transcribe-video
description: "Use when transcribing local video or audio offline."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [windows]
metadata:
  hermes:
    tags: [bitpool, transcription, whisper, video, audio, ffmpeg, wsl, privacy]
    category: bitpool
    related_skills: [docx-to-md, pdf-to-md]
---

# transcribe-video

Transcribe video and audio to text **locally**, using **OpenAI Whisper via `whisper-ctranslate2` + ffmpeg, run inside Ubuntu WSL**. Nothing is uploaded — no API keys, no cloud. This is the privacy-preserving alternative to cloud transcription: good for internal recordings, meetings and demos that shouldn't leave the machine.

Output is a per-file transcript plus one combined Markdown document. The commands ship with this skill in `references/`.

## When to Use

- The user runs `/transcribe-video`, or asks to "transcribe these videos" / "get a transcript of [file/folder]".
- A folder of videos or a single file: mp4/mov/mkv/avi/webm/m4v/wmv/flv and common audio (mp3/m4a/wav).
- Subtitles (`srt`/`vtt`) instead of prose — same toolchain, different `--output_format`.

Don't use for:
- Cloud or API-based transcription, or YouTube links: this skill is local-only by design (Hermes's `youtube-content` skill handles YouTube transcripts).
- Converting documents: use `/docx-to-md`, `/pdf-to-md` or `/pdf-to-md-rich`.

## Prerequisites

- Windows host with **Ubuntu WSL** (`wsl.exe -d Ubuntu`). Hermes's `terminal` on Windows is git-bash, which calls `wsl.exe` directly.
- **ffmpeg** and the **whisper venv** (`~/.venvs/whisper` with `whisper-ctranslate2`) inside WSL. The check and the user's install command are in `references/wsl-conversion-toolchain.md`.

## Procedure

1. **Run the toolchain check** from `references/wsl-conversion-toolchain.md` (transcribe-video section) with `terminal`. Done when it prints `OK` — or, on `MISSING`, you have stopped and given the user the install command (rule 2).
2. **Read the commands** — `read_file` the whole of `references/local-video-transcription.md` and `references/wsl-conversion-toolchain.md`. Done when both are read this run.
3. **Get the input.** Use the folder or file the user named; if none, ask with `clarify` — never assume. Translate it to `/mnt/<drive>/…`. Done when you have a quoted WSL path.
4. **List the media and show it** with the listing command in the reference. Done when the user has seen the count and list (or been told nothing matched and asked for the right folder).
5. **Choose the model.** Show the model table from the reference and ask with `clarify` (default `small`; suggest `small`/`base` for long recordings on a slow machine). Offer `--language` if known, and `srt`/`vtt` if they want captions. Done when a model is chosen.
6. **Transcribe one file** into `transcripts/parts/` with the reference command. Done when its `.txt` exists and the user has been asked whether it reads well; if not, offer a larger model or `--language` before continuing.
7. **Batch the rest** after the user confirms; report and continue past corrupt/unsupported files. Done when every listed file has a transcript or a reported failure.
8. **Assemble** `transcripts/all_transcripts.md` with the reference command. Done when the file exists and has one `##` section per transcript.
9. **Report** per file, plus the combined document's Windows path. Done when every file has a line.

## Load-bearing rules

These define what this skill is for.

1. **Local only, by design.** No cloud service, no API keys. **Never upload the media anywhere.** That is the entire reason this skill exists.
2. **Toolchain-gated.** If the check prints `MISSING`, **stop** — transcribe nothing — and give the user the install command to run themselves. Setup needs sudo; never attempt `apt`/`sudo` yourself.
3. **Ask which model to use.** Default to `small` — good accuracy, roughly 4× faster than large, CPU-friendly. Suggest `small` or `base` for long recordings on a slow machine.
4. **Never assume the input folder.** Ask if the user didn't name one.
5. **Test one, then batch.** Transcribe one file, let the user check quality, and wait. If it reads poorly, offer a larger model or an explicit `--language` before looping the rest.
6. **Write outputs under the input folder** (or a path the user names). Don't move or delete the source media.
7. **Report failures and continue** — a corrupt or unsupported file shouldn't stop the run.
8. **Don't commit or push anything.** This produces transcript files only.

## Pitfalls

- **Reaching for a cloud fallback** (a transcription API, `web_extract`, an upload) when the toolchain is missing. Stop instead.
- **Starting a large-v3 run unasked.** Model size changes runtime by up to ~10×; long recordings can run for hours on CPU.
- **Terminal timeouts on long files.** Run long transcriptions with a generous `timeout`, or in the background and poll, rather than letting the call die mid-file.
- **Letting git-bash expand `$HOME` or `${t%.*}`.** Keep the WSL-side command in single quotes, exactly as in the reference.
- **Unquoted paths** — meeting-recording folders usually contain spaces.

## Verification

- The toolchain check printed `OK` this run.
- `transcripts/parts/` has one transcript per successfully processed file; failures are listed in the report.
- `transcripts/all_transcripts.md` exists, names the model used, and has a `##` section per transcript.
- Nothing was uploaded; no source media was moved or deleted.

## Reference files

Read the file itself — the table is an index, not a substitute.

| File | Covers |
|---|---|
| `references/local-video-transcription.md` | Transcribing video and audio locally with Whisper (whisper-ctranslate2) and ffmpeg in WSL — listing media, model sizing, the per-file loop, the combined Markdown assembly, and why nothing leaves the machine. |
| `references/wsl-conversion-toolchain.md` | The shared mechanics behind the WSL-backed conversion skills — toolchain checks and their copy-paste install commands, Windows→WSL path translation, the file-listing rules, and the test-one-then-batch discipline. |

Toolchain check, path translation, batching → edit `references/wsl-conversion-toolchain.md` (shared with `/docx-to-md`, `/pdf-to-md`, `/pdf-to-md-rich`; keep copies identical). Model table, commands, assembly → edit `references/local-video-transcription.md`.
