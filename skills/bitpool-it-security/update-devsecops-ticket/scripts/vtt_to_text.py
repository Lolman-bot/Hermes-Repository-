#!/usr/bin/env python3
"""
vtt_to_text.py - flatten a WebVTT (.vtt) meeting transcript into one timestamped
line per cue, so a whole meeting can be read in a single pass.

    python3 vtt_to_text.py "/mnt/c/path/to/Meeting.vtt" [--merge] [--gap S] [--max-chars N]

Why this exists: a per-line regex over a .vtt silently drops every continuation
line of a multi-line cue, because only the FIRST line of a cue carries the
<v Name> tag. This parses by cue BLOCK instead, so no words are lost.

Output (stdout), one line per cue:

    [HH:MM:SS] Speaker Name: text of the cue
    [HH:MM:SS] | text of the cue        <- when speaker tags are meaningless

Diagnostics go to stderr, never stdout, so stdout can be redirected cleanly.

Standard library only. Python 3.8+.
"""

import argparse
import html
import os
import re
import sys

# <v Eric Sharp>  /  <v.loud.first Eric Sharp>  /  <v Eric Sharp.>  /  bare <v>
# The name group is optional and must be preceded by whitespace, so a stray tag
# such as <video> is not mistaken for a speaker called "ideo".
VOICE_OPEN = re.compile(r"<v(?:\.[^\s>]+)*(?:\s+([^>]*))?>", re.IGNORECASE)
VOICE_CLOSE = re.compile(r"</v\s*>", re.IGNORECASE)
# Other WebVTT inline cue tags: <c.colour>, <i>, <b>, <00:00:01.000>
OTHER_TAGS = re.compile(
    r"</?(?:c|i|b|u|ruby|rt|lang|v)(?:\.[^\s>]+)*(?:\s[^>]*)?>"
    r"|<\d{1,3}:\d{2}[:.][\d:.]+>",
    re.IGNORECASE,
)
TIMESTAMP = re.compile(r"(?:(\d{1,3}):)?(\d{1,3}):(\d{2})[.,](\d{1,3})")

SKIP_PREFIXES = ("NOTE", "STYLE", "REGION", "WEBVTT")
SENTENCE_END = (".", "?", "!", '"', "”")


def parse_ts(raw):
    """Parse one WebVTT timestamp -> (seconds, "HH:MM:SS"). None if unparseable."""
    m = TIMESTAMP.search(raw)
    if not m:
        return None
    hh = int(m.group(1)) if m.group(1) is not None else 0
    mm, ss = int(m.group(2)), int(m.group(3))
    ms = int(m.group(4).ljust(3, "0")[:3])
    total = hh * 3600 + mm * 60 + ss + ms / 1000.0
    return total, "%02d:%02d:%02d" % (hh, mm, ss)


def clean(text):
    """Strip voice/inline tags, unescape entities, squash whitespace -> (speaker|None, text)."""
    speaker = None
    m = VOICE_OPEN.search(text)
    if m and m.group(1):
        name = m.group(1).strip().rstrip(".").strip()
        speaker = name or None
    text = VOICE_CLOSE.sub(" ", text)
    text = OTHER_TAGS.sub(" ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return speaker, text


def parse_vtt(path):
    """Return cues as a list of dicts with start, end, stamp, speaker, text - in file order."""
    with open(path, "r", encoding="utf-8-sig", errors="replace") as fh:
        raw = fh.read()

    # Normalise CRLF and lone CR before splitting on blank lines.
    raw = raw.replace("\r\n", "\n").replace("\r", "\n")

    cues = []
    for block in re.split(r"\n\s*\n", raw):
        lines = [ln for ln in block.split("\n") if ln.strip() != ""]
        if not lines:
            continue
        # Drop leading header lines (WEBVTT/NOTE/STYLE/REGION) one at a time, never
        # the whole block. A .vtt with no blank line between the WEBVTT header and
        # the first cue puts both in the same block, and discarding the block would
        # silently lose that first cue with no warning and exit 0.
        while (lines
               and lines[0].strip().upper().startswith(SKIP_PREFIXES)
               and "-->" not in lines[0]):
            lines.pop(0)
        if not lines:
            continue

        # Find the timing line. Anything before it is a cue identifier; EVERY line
        # after it is cue payload and belongs to this cue. A NOTE/STYLE/REGION block
        # with no timing line falls out here, exactly as it did before.
        idx = next((i for i, ln in enumerate(lines) if "-->" in ln), None)
        if idx is None:
            continue

        halves = lines[idx].split("-->")
        start_ts = parse_ts(halves[0])
        if start_ts is None:
            continue
        end_ts = parse_ts(halves[1]) if len(halves) > 1 else None
        start, stamp = start_ts
        end = end_ts[0] if end_ts else start

        speaker, text = clean(" ".join(lines[idx + 1:]))
        if not text:
            continue
        cues.append({"start": start, "end": end, "stamp": stamp,
                     "speaker": speaker, "text": text})

    return cues


def merge(cues, gap, max_chars):
    """Merge consecutive same-speaker cues into readable runs.

    A run breaks when the speaker changes, when the pause since the previous cue
    exceeds `gap` seconds, or when the run has passed `max_chars` and has reached a
    sentence boundary (hard break at twice `max_chars`).

    Measured on the 466-cue 2026-08-24 Teams file: the defaults give 51 runs;
    `--max-chars 0` gives 16, because the 2.0s pause rule still breaks them; only
    `--gap 0 --max-chars 0` collapses the meeting into a single 5,394-word line.
    Both caps are doing work - the length cap is not the only thing standing
    between a single-speaker file and one unreadable line.
    """
    out = []
    for cue in cues:
        if out:
            prev = out[-1]
            same_speaker = prev["speaker"] == cue["speaker"]
            close_enough = gap <= 0 or (cue["start"] - prev["end"]) <= gap
            grown = len(prev["text"])
            too_long = (max_chars > 0 and
                        ((grown >= max_chars and prev["text"].endswith(SENTENCE_END))
                         or grown >= max_chars * 2))
            if same_speaker and close_enough and not too_long:
                prev["text"] = (prev["text"] + " " + cue["text"]).strip()
                prev["end"] = cue["end"]
                continue
        out.append(dict(cue))
    return out


def main():
    ap = argparse.ArgumentParser(
        description="Flatten a WebVTT transcript to one timestamped line per cue.",
        epilog="Diagnostics print to stderr; the transcript prints to stdout.",
    )
    ap.add_argument("vtt", help="path to the .vtt file")
    ap.add_argument("--merge", action="store_true",
                    help="merge consecutive same-speaker cues into readable runs")
    ap.add_argument("--gap", type=float, default=2.0, metavar="S",
                    help="with --merge, break a run after a pause longer than S seconds "
                         "(default 2.0; 0 means never break on a pause)")
    ap.add_argument("--max-chars", type=int, default=600, metavar="N",
                    help="with --merge, break a run once it passes N characters at a "
                         "sentence boundary (default 600; 0 means no length cap)")
    args = ap.parse_args()

    if not os.path.isfile(args.vtt):
        sys.stderr.write("vtt_to_text: no such file: %s\n" % args.vtt)
        return 1

    cues = parse_vtt(args.vtt)
    if not cues:
        sys.stderr.write("vtt_to_text: no cues parsed from %s - is it really a WebVTT file?\n"
                         % args.vtt)
        return 1

    speakers = sorted({c["speaker"] for c in cues if c["speaker"]})
    n = len(speakers)

    sys.stderr.write("vtt_to_text: %s - %d cue%s, %d distinct speaker tag%s%s\n"
                     % (os.path.basename(args.vtt), len(cues),
                        "" if len(cues) == 1 else "s", n,
                        "" if n == 1 else "s",
                        (" (%s)" % ", ".join(speakers)) if speakers else ""))

    if n <= 1:
        sys.stderr.write(
            "WARNING: speaker attribution from this file is UNRELIABLE.\n"
            "         Teams routinely tags every cue with one name even when several people\n"
            "         spoke. Do NOT list attendees or attribute a decision to a person from\n"
            "         this transcript. Record decisions as decisions OF THE MEETING, and take\n"
            "         the attendee list from the calendar entry instead.\n")

    if args.merge:
        cues = merge(cues, args.gap, args.max_chars)
        sys.stderr.write("vtt_to_text: --merge collapsed to %d runs (gap %.1fs, max-chars %d)\n"
                         % (len(cues), args.gap, args.max_chars))

    single = n <= 1
    try:
        for c in cues:
            who = "|" if (single or not c["speaker"]) else "%s:" % c["speaker"]
            sys.stdout.write("[%s] %s %s\n" % (c["stamp"], who, c["text"]))
        sys.stdout.flush()
    except BrokenPipeError:          # piped into head or less and cut short
        try:
            sys.stdout.close()
        except Exception:
            pass
        os._exit(0)

    return 0


if __name__ == "__main__":
    sys.exit(main())
