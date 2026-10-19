# Parsing a Teams .vtt Transcript

DevSecOps meeting recordings arrive as WebVTT (`.vtt`) exported from Microsoft Teams. The format
looks trivially parseable. It is not. Three specific behaviours of the Teams export combine to
hand you a transcript that reads fluently, is missing half the words, and appears to attribute
every decision to one person who may not have said any of them.

Everything on this page was confirmed live against `Meeting in _DevSecOps_ 1.vtt` — 466 cues,
roughly 30 minutes, three people in the room.

> **Rule: never hand-roll the parser.**
> This skill ships `scripts/vtt_to_text.py`. Run it. It is plain Python 3 standard library, it
> handles all three traps below, and it prints the attribution warning for you. Re-deriving a
> regex in the moment is how every one of these traps got hit in the first place.

## The three traps

### 1. Teams collapses every speaker into a single `<v>` tag

**Confirmed live:** every one of the 466 cues in the 2026-08-24 file was tagged `<v Eric Sharp>` —
466 out of 466, a single distinct speaker tag — even though three people spoke throughout. Teams
did not split the diarisation; it stamped the whole meeting with the organiser's name.

Verify it before you trust a single attribution:

```bash
grep -o "<v [^>]*>" "<transcript folder>/Meeting.vtt" | sort | uniq -c
```

On the 2026-08-24 file that returns exactly one line — `466 <v Eric Sharp>`. One distinct tag
across a multi-person meeting means the tags are meaningless, not that one person monologued.

**Rule — three parts, all of them binding:**

- **You cannot list attendees from the file.** The `<v>` tags are not an attendee list. Get the
  attendees from the **calendar entry** instead (the Microsoft 365 MCP server's calendar search, `outlook_calendar_search`). The `.vtt` carries no
  meeting date either, so the calendar is doing double duty — in the worked example the date was
  pinned by matching an in-audio reference ("meeting tomorrow at 4:00") against a real calendar
  entry, never guessed.
- **You cannot attribute a decision, an opinion or a commitment to a person.** Write every comment
  as a decision **of the meeting** — "the meeting agreed", "the direction is", "this was descoped"
  — not "Dmytro said" or "Armen will".
- **Where a named owner genuinely matters and the audio does not make it unambiguous, say so
  rather than guess.** In the worked example a rapid 00:14–00:16 pass over several tickets was
  left unwritten entirely, and the gap was reported to the user, because it was not clear what had
  already been done or by whom. Three tickets were deliberately left untouched. That is the
  correct outcome, not a failure.

### 2. A cue can span several lines — only the first carries the `<v>` tag

A Teams cue block wraps its text at display width. The opening `<v Name>` sits on the first line
only; the closing `</v>` sits at the end of the last. Every line in between is bare text:

```
76c93719-bba1-4c54-903d-fcd006f10aa1/4-0
00:00:03.149 --> 00:00:06.318
<v Eric Sharp>Essentially, anyhow,
they need to be done as part of business,</v>
```

A per-line regex that requires the `<v>` tag matches the first line and silently discards the
rest. Nothing errors. Nothing looks wrong.

**Confirmed live — the damage, measured on the same file:**

| Approach | Words of speech recovered |
|---|---|
| Parse by cue **block** (the shipped script) | **5,394** |
| Per-line regex requiring `<v ...>` | 2,738 |

The naive version throws away **2,656 words — 49% of the meeting** — and the wreckage is
undetectable by eye, because each surviving fragment joins plausibly onto the next. Its first five
lines read:

```
Essentially, anyhow,
right,
exposures out of the way. I reckon,
position now that you've done the easy
critical and high.
```

That is grammatical, fluent, and wrong. The real first cue is `Essentially, anyhow, they need to
be done as part of business,` — and "to get all those CVEs and all these", "so I think we're in a
much better", and "low-hanging group that people would say" are simply gone. Draft Jira comments
off that and you will confidently post a summary of a meeting that did not happen.

**Rule:** parse by **cue block** — split the file on blank lines, locate the `-->` timing line
inside the block, and join **every** remaining line of the block before stripping tags. Never
iterate line by line.

### 3. A bash heredoc mangles the parser before it ever runs

Writing the parser inline as a `bash` heredoc fails on the punctuation a parser is full of —
apostrophes, quote characters, em-dashes. In the original session this broke twice. It broke again
while authoring this very page: a quoted-heredoc write containing a sentence-punctuation tuple
died with

```
/usr/bin/bash: -c: line 73: unexpected EOF while looking for matching `'
```

even though the heredoc delimiter was quoted, because the tool layer wraps the command in single
quotes of its own.

**Rule:** write the script to a `.py` **file** with `write_file`, then execute that file with
`terminal`. Do not pipe Python source through `bash -c`. On a Windows machine where the native
`python`/`python3` are the Microsoft Store stubs that print *"Python was not found…"* and exit
(as on the original authoring machine), the real Python 3 lives in WSL — run the file there.

## Path translation (WSL fallback only)

Skip this section when a native Python 3 runs the script. WSL sees the Windows drives under `/mnt/c/`. Translate before handing any path to a WSL command,
and **always quote it** — the transcript folder contains spaces (`Bitpool Pty Ltd`, `New cyber
plan`).

| Windows | WSL |
|---|---|
| `C:\X\Y` | `/mnt/c/X/Y` |
| `C:\<home>\Bitpool Pty Ltd\…` | `"/mnt/c/<home>/Bitpool Pty Ltd/…"` |

Backslashes → forward slashes, drive letter lower-cased, whole path in double quotes.

## Running the shipped script

Through `terminal`. `<skill dir>` is this skill's installed folder (shown by `skill_view`,
normally under `$HERMES_HOME/skills/`); `<transcript folder>` is the synced SharePoint folder
*Cyber Security - Documents/General/New cyber plan/DevSecOps meeting transcripts*:

```bash
python3 "<skill dir>/scripts/vtt_to_text.py" "<transcript folder>/<file>.vtt"
```

WSL fallback (Store-stub Windows Python):

```bash
wsl -e bash -lc 'python3 "/mnt/c/<skill dir>/scripts/vtt_to_text.py" "/mnt/c/<transcript folder>/<file>.vtt"'
```

The transcript goes to **stdout**; the diagnostics go to **stderr**, so you can redirect the
transcript to a file and still see the warnings:

```bash
python3 "…/vtt_to_text.py" "…/Meeting.vtt" > "…/parsed.txt"
```

Redirecting is worth doing on a long meeting — you can then re-read slices of `parsed.txt` without
re-parsing. A 30-minute meeting comes out at roughly 460 lines and 5,400 words, which reads
comfortably in one pass.

### What the output looks like

One line per cue. When the file has a single distinct speaker tag — the normal Teams case — the
speaker field is rendered as a bare `|`, because printing a name there would be a lie:

```
[00:00:03] | Essentially, anyhow, they need to be done as part of business,
[00:00:06] | right, to get all those CVEs and all these
[00:00:08] | exposures out of the way. I reckon, so I think we're in a much better
```

When the export genuinely did diarise, the name is printed instead, and a cue with no tag at all
still falls back to `|`:

```
[00:00:01] Ada Lovelace: First line of Ada, second line with no tag, third line too
[00:00:20] | No voice tag at all here
```

And on stderr, before any of it:

```
vtt_to_text: Meeting in _DevSecOps_ 1.vtt - 466 cues, 1 distinct speaker tag (Eric Sharp)
WARNING: speaker attribution from this file is UNRELIABLE.
         Teams routinely tags every cue with one name even when several people
         spoke. Do NOT list attendees or attribute a decision to a person from
         this transcript. …
```

If that warning appears, trap 1 is in force for this file. Act accordingly.

### Timestamps are how you cite a moment

The `[HH:MM:SS]` prefix is not decoration — it is the citation mechanism. When you show the user a
draft comment, when you flag a passage as too ambiguous to write up, or when they ask "where did
that come from", quote the timestamp: *"the WAF scope discussion runs 00:08:12–00:09:40"*,
*"00:14–00:16 is too rushed to attribute"*. It lets them scrub straight to the audio and check
you. Never paraphrase a contested point without one.

### Options

| Flag | Effect |
|---|---|
| *(none)* | One line per cue — the default, and the right choice for drafting |
| `--merge` | Merges consecutive same-speaker cues into readable runs |
| `--gap S` | With `--merge`, breaks a run after a pause longer than `S` seconds (default `2.0`; `0` never breaks on a pause) |
| `--max-chars N` | With `--merge`, breaks a run past `N` characters at a sentence boundary (default `600`; `0` removes the cap) |

`--merge` is for reading, not for citing — it collapses 466 cues to 51 paragraph-sized runs on the
2026-08-24 file, which is far easier to skim, but each run then carries only its **starting**
timestamp. Draft from the unmerged output when precise timestamps matter.

**What each cap is actually worth, measured on that file** — on a single-speaker export every cue
is nominally "the same speaker", so the two caps are the only things breaking a run at all:

| Flags | Runs |
|---|---|
| `--merge` (defaults: gap `2.0`, max-chars `600`) | **51** |
| `--merge --max-chars 0` | **16** — the 2.0s pause rule still breaks them |
| `--merge --gap 0 --max-chars 0` | **1** — a single 5,394-word line |

So the length cap is not the only thing standing between you and one unreadable line: dropping it
alone still leaves 16 readable runs, because **Teams does not emit contiguous cues with no gaps**.
Of the 465 inter-cue gaps in the file, **108 are non-zero**, the longest is **8.5s**, and **15
exceed the 2.0s default** — which is exactly the 15 breaks that produce those 16 runs. Both caps
earn their place; neither is load-bearing on its own.

## Non-`.vtt` input — skip the parse entirely

The script exists for WebVTT only. If the input is pasted text in the chat, a `.txt`, a `.md`, or
notes someone typed up, **read it directly** — no script, no WSL, no translation. Running the
parser on a non-VTT file is harmless but pointless; it exits `1` with `no cues parsed … - is it
really a WebVTT file?`.

Two things still carry over to non-VTT input:

- **Attribution is still suspect** unless the document explicitly names who said what. A `.txt`
  dump of a Teams transcript inherits trap 1 wholesale.
- **There are no timestamps to cite.** Say so when the user asks where something came from, rather
  than inventing a time.
