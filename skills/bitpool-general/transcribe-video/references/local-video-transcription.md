# Local Video Transcription

Transcribe video and audio to text **locally**, using **OpenAI Whisper via
`whisper-ctranslate2` + ffmpeg, run inside Ubuntu WSL**. Nothing is uploaded — no API keys, no
cloud.

This is the privacy-preserving alternative to cloud transcription: good for internal recordings,
meetings and demos that shouldn't leave the machine.

Toolchain check, install command, path translation, file listing and the test-one-then-batch rule
are shared — see [WSL Conversion Toolchain](wsl-conversion-toolchain.md).

## Listing the media

```bash
wsl.exe -d Ubuntu bash -lc 'cd "/mnt/c/PATH/TO/videos" && shopt -s nullglob nocaseglob && ls -1 *.{mp4,mov,mkv,avi,webm,m4v,wmv,flv,mp3,m4a,wav} 2>/dev/null'
```

Report the count and the list. If nothing matches, say so and ask for the right folder.

## Choosing a model

Show this table and ask which size to use. Default to **small** — good accuracy, roughly 4×
faster than large, and CPU-friendly.

```
 #   Model      Params   Speed (vs large)   Accuracy
---  ---------  -------  -----------------  ----------
 1   tiny        39M     ~10x faster        Low
 2   base        74M     ~7x faster         Low-med
 3   small      244M     ~4x faster         Good      <- recommended
 4   medium     769M     ~2x faster         Very good
 5   large-v3  1550M     1x (baseline)      Best
```

Bigger is slower but more accurate, and it all runs on CPU locally. For long recordings on a slow
machine, suggest `small` or `base`.

## Transcribing

Create `transcripts/parts/` under the input folder, then transcribe each file into a `.txt`:

```bash
wsl.exe -d Ubuntu bash -lc 'cd "/mnt/c/PATH/TO/videos" && mkdir -p transcripts/parts && "$HOME/.venvs/whisper/bin/whisper-ctranslate2" "<file>" --model <MODEL> --output_format txt --output_dir transcripts/parts --verbose False'
```

Then assemble the combined document — the first file initialises the header, each file appends
under its own `##` heading:

```bash
wsl.exe -d Ubuntu bash -lc 'cd "/mnt/c/PATH/TO/videos/transcripts" && { echo "# Video Transcripts"; echo; echo "Generated locally with whisper-ctranslate2 (model: <MODEL>)."; echo; for t in parts/*.txt; do b="$(basename "${t%.*}")"; echo "## $b"; echo; cat "$t"; echo; echo "---"; echo; done; } > all_transcripts.md'
```

> **Note**
> - `--output_format` also accepts `srt` and `vtt` for subtitles — offer these if the user wants
>   captions rather than prose.
> - Whisper auto-detects language. Pass `--language en` (or another code) if the user knows it, to
>   skip detection and improve accuracy.
> - ffmpeg decodes the media under the hood — that's why the toolchain check requires it.


## Report

- ✅ `<file> → transcripts/parts/<file>.txt`, per file
- ✅ Combined document: `transcripts/all_transcripts.md` — give the Windows path so the user can
  open it
- ⚠️ Flag any file that failed (corrupt or unsupported) and continue with the rest

If the test file doesn't read well, offer a larger model or an explicit `--language` before
looping the rest.

## Boundaries

> **Important**
> **Local only, by design.** No cloud service, no API keys. Never upload the media anywhere.


- If the toolchain is missing, stop and have the user run the setup — it needs sudo. Don't attempt
  `apt`/`sudo` yourself.
- Write outputs under the input folder, or a path the user names. Don't move or delete the source
  media.
- Don't commit or push anything — this produces transcript files only.
