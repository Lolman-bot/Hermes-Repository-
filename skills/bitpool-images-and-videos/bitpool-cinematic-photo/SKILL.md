---
name: bitpool-cinematic-photo
description: "Use when writing a Gemini prompt for a Bitpool still."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, image-generation, gemini, cinematic, archviz, photography, prompt-writing]
    category: bitpool
    related_skills: [bitpool-3d-image, bitpool-cinematic-video, bitpool-design-system]
---

# Bitpool Cinematic Photo — Gemini Image Prompt Creator

Builds production-grade prompts for Google Gemini image generation that produce Bitpool marketing stills — photoreal architectural photography (office towers, the Brandl St HQ), plant room photography, and 3D archviz renders (data centres, isometric cutaways, exploded systems views). The user runs the prompt in Gemini; this skill writes the prompt, not the image.

**This skill is a reference, not a content store.** Every rule, template and prompt lives in `references/`. Do not answer from memory, and do not write the prompt before reading the relevant file.

## When to Use

- The user asks for a Gemini prompt, image prompt, hero image, campaign still, digital-twin image, isometric/cutaway/exploded view, or any marketing image concept for Bitpool — even if they just say "create a prompt for X".
- Photo-to-render or plan-to-3D requests ("turn this photo into a render", "remove X from this image") are covered by templates here too; for the full conversion method prefer `/bitpool-3d-image`.
- The user types `/bitpool-cinematic-photo`.
- Do NOT hand-roll image prompts. The prompt architecture, quality blocks, fidelity rules and proven master templates ship with this skill in `references/`.

Don't use for:

- Video prompts (Veo, stacking/assembly, fly-throughs) → `/bitpool-cinematic-video`.
- Generating the image itself — the output is always a prompt.

## Prerequisites

- If the user attaches a reference image, read it natively or with `vision_analyze` to build the fidelity inventory.
- For the optional HTML deliverable: the `bitpool-design-system` skill installed (brand tokens). See `references/html-output.md`.

## Procedure

1. **Read the reference files first, each in full** with `read_file` — `references/visual-language.md`, then `references/cinematic-photo.md`. Nothing is fetched; the whole method ships with the skill. Done when both files are read this run.
2. **Pick the mode and template** — photoreal photography or 3D render, then one of the seven master templates (office tower, plant room, data centre, photo→render, cutaway, exploded systems, floor plan→3D). Done when one template is chosen.
3. **If a reference image is attached, itemise every feature to preserve** (look at it natively or with `vision_analyze`). For the Bitpool HQ use the verbatim inventory in `references/visual-language.md`. Done when the fidelity inventory is written.
4. **Reproduce the template exactly as written**, substituting only the `[bracketed]` slots. Never paraphrase or trim one. Done when every slot is filled and no template line is missing.
5. **Deliver per the output contract** in `references/visual-language.md` — the prompt in one fenced code block, 2–4 terse lever notes, 2–5 one-line swap-in variants including an after-hours option. Done when all three parts are in the reply.
6. **Only if the user asks to see it** — "mock it up", "show me what it will look like", "an HTML version", "storyboard it" — read `references/html-output.md` and build the HTML with `write_file`. Give the absolute path (CLI) or attach it as `MEDIA:/absolute/path` (messaging). It is additive: the prompt is still delivered in chat. Done when the file exists and its path was given.

## Load-bearing rules

1. **Gemini keeps what you name and redesigns what you don't** — itemise every feature to preserve when transforming a reference.
2. **Templates are reproduced whole.** Only `[bracketed]` slots change.
3. **One variant is always the after-hours variant.** The lit office goes in every variant of a tower shot.
4. **No text, labels or logos inside generated imagery**; reserve the clean lockup zone — the typography rule in `references/visual-language.md`.
5. **A mockup is a composition preview, never presented as the real render.**

## Pitfalls

- **Writing from memory.** The quality blocks and realism anchors are exact phrasing; read the files.
- **Forgetting the after-hours variant** or the lit office in a tower shot.
- **Offering HTML unprompted.** Only build it when asked.
- **Optional preview with Hermes's own `image_generate` tool** — only if the user asks for a quick look and has image generation configured. It runs a FAL/Nous model, not the user's Gemini, so never present its output as what Gemini will produce.

## Verification

- Both reference files were read this run; the chosen template appears whole with only slots changed.
- Reply = one code block + 2–4 notes + 2–5 variants, one of them after-hours.
- Any HTML was requested, lives in a file, and is captioned as a composition preview.

## Reference files

Read the file itself — the table is an index, not a substitute.

| File | Covers |
|---|---|
| `references/cinematic-photo.md` | Gemini still-image prompt architecture for Bitpool marketing stills, plus the seven proven master templates — office tower, plant room, data centre, photo→render, cutaway, exploded systems, floor plan→3D. |
| `references/html-output.md` | The optional HTML deliverable — an on-brand composition mockup of the shot, or a formatted handoff page carrying the prompt. Two modes, the brand dependency, and the CSS keyframe spec for animating a video's beats. Identical copy in all three imagery skills. |
| `references/visual-language.md` | The shared foundation every Bitpool image and video prompt is built on — the five campaign motifs, the typography rule, the standard quality blocks, realism anchors, the system colour map, and the output contract. Identical copy in all three imagery skills. |

Change the prompt craft in `references/`, not here. Keep `html-output.md` and `visual-language.md` identical across `bitpool-3d-image`, `bitpool-cinematic-photo` and `bitpool-cinematic-video` — edit every copy the same way.
