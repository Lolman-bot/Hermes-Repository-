---
name: bitpool-cinematic-video
description: "Use when writing a Veo or Gemini video prompt for Bitpool."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, video-generation, veo, gemini, cinematic, digital-twin, prompt-writing]
    category: bitpool
    related_skills: [bitpool-cinematic-photo, bitpool-3d-image, bitpool-design-system]
---

# Bitpool Cinematic Video — Gemini/Veo Prompt Creator

Builds incredible, production-grade prompts for Google Veo (video) and Gemini (images) that produce Bitpool marketing content — building assembly/stacking sequences, plant room self-assembly, digital-twin fly-throughs and exploded systems views. The user runs the prompt in Veo/Gemini; this skill writes the prompt, not the video.

**This skill is a reference, not a content store.** Every rule, template and prompt lives in `references/`. Do not answer from memory, and do not write the prompt before reading the relevant file.

## When to Use

- The user asks for a Veo prompt, video prompt, AI video, "stacking" or "assembly" video, digital-twin visual, fly-through, exploded view, or any cinematic/marketing video concept in a Bitpool context — even if they just say "create a prompt for X" or "turn this image into Y".
- The user types `/bitpool-cinematic-video`.
- Do NOT hand-roll prompts from scratch. The prompt architecture, quality blocks, motion choreography rules, campaign visual language and proven templates ship with this skill in `references/`.

Don't use for:

- A still image rather than a video → `/bitpool-cinematic-photo`; converting an attached photo/plan into a 3D still → `/bitpool-3d-image`.
- Generating the video itself — the output is always a prompt.

## Prerequisites

- If the user attaches a reference image (often the end frame), read it natively or with `vision_analyze` to build the fidelity inventory.
- For the optional HTML deliverable: the `bitpool-design-system` skill installed (brand tokens). See `references/html-output.md`.

## Procedure

1. **Read the reference files first, each in full** with `read_file` — `references/visual-language.md`, then `references/cinematic-video.md`. Nothing is fetched; the whole method ships with the skill. Done when both files are read this run.
2. **Confirm it is a video.** If it turns out to be a still, switch to `/bitpool-cinematic-photo`. Pick the template (building stacking assembly or plant room self-assembly). Done when one template is chosen.
3. **If a reference image is attached, itemise every feature to preserve** (look at it natively or with `vision_analyze`); the end framing equals the reference image framing. Done when the fidelity inventory is written.
4. **Reproduce the template exactly as written**, substituting only the `[bracketed]` slots. Never paraphrase or trim one. Keep it to the 8-second window with timestamped beats. Done when every slot is filled, no template line is missing and the beats end at 8.0s.
5. **Deliver per the output contract** in `references/visual-language.md` — the prompt in one fenced code block, 2–4 terse lever notes, 2–5 one-line swap-in variants including an after-hours option. Done when all three parts are in the reply.
6. **Only if the user asks to see it** — "mock it up", "show me the pacing", "an HTML version", "storyboard it" — read `references/html-output.md` and build the 8-second CSS keyframe preview with `write_file`, timings matching the prompt's beats exactly. Give the absolute path (CLI) or attach it as `MEDIA:/absolute/path` (messaging). It is additive: the prompt is still delivered in chat. Done when the file exists and its path was given.

## Load-bearing rules

1. **8 seconds is the sweet spot.** Veo holds temporal stability there; at 15+ seconds facade grids start swimming. For longer choreography, split into multiple 8-second generations with a continuous camera instruction.
2. **Timestamped beats, one continuous camera move**, ending on a 1.5s locked hero still.
3. **Anti-morph clause in every assembly sequence**; pipework GROWS, never drops; mass and rhythm (heavy slow, small quick, 2-centimetre settle, cyan pulse per landing).
4. **Templates are reproduced whole.** Only `[bracketed]` slots change.
5. **A mockup is a composition preview, never presented as the real video**; an animation whose timings don't match the beats is worse than none.

## Pitfalls

- **Writing from memory.** The clauses that do the work (anti-morph, `rendered entirely as premium CGI, not drone footage`, camera on rails) are exact phrasing; read the files.
- **Going past 8 seconds** in one generation, or a preview longer/shorter than 8s.
- **Offering HTML unprompted.** Only build it when asked.
- **Hermes's own `image_generate` tool makes stills, not video** — at most an optional end-frame preview if the user asks and has it configured; never present it as Veo output.

## Verification

- Both reference files were read this run; the chosen template appears whole with only slots changed.
- Beats are timestamped and end at 8.0s with a hero hold; the anti-morph clause is present for assembly.
- Reply = one code block + 2–4 notes + 2–5 variants, one after-hours; any HTML was requested, lives in a file, runs 8s with matching timings.

## Reference files

Read the file itself — the table is an index, not a substitute.

| File | Covers |
|---|---|
| `references/cinematic-video.md` | Veo video prompt rules for Bitpool — the 8-second window, timestamped beats, camera-on-rails motion, mass and rhythm, the anti-morph clause — plus the two proven assembly sequences. |
| `references/html-output.md` | The optional HTML deliverable — an on-brand composition mockup of the shot, or a formatted handoff page carrying the prompt. Two modes, the brand dependency, and the CSS keyframe spec for animating a video's beats. Identical copy in all three imagery skills. |
| `references/visual-language.md` | The shared foundation every Bitpool image and video prompt is built on — the five campaign motifs, the typography rule, the standard quality blocks, realism anchors, the system colour map, and the output contract. Identical copy in all three imagery skills. |

Change the prompt craft in `references/`, not here. Keep `html-output.md` and `visual-language.md` identical across `bitpool-3d-image`, `bitpool-cinematic-photo` and `bitpool-cinematic-video` — edit every copy the same way.
