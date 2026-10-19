---
name: bitpool-3d-image
description: "Use when turning a photo or plan into a 3D render prompt."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, image-generation, gemini, archviz, 3d, image-to-image, prompt-writing]
    category: bitpool
    related_skills: [bitpool-cinematic-photo, bitpool-cinematic-video, bitpool-design-system]
---

# Bitpool 3D Image — Photo/2D → 3D Render Prompt Creator

Builds Gemini **image-to-image** prompts that transform a source image (photo, 2D plan, diagram, screenshot, schematic) into a stunning 3D-modelled archviz render — buildings, plant rooms, equipment, data centres, floor plates. The user runs the prompt in Gemini with the source image attached; this skill writes the prompt, not the image.

**This skill is a reference, not a content store.** Every rule, template and prompt lives in `references/`. Do not answer from memory, and do not write the prompt before reading the relevant file.

## When to Use

- The user attaches an image and asks to "turn this into 3D", "make this a render", "convert this photo/plan/diagram", "3D model this", "make this look rendered", "remove X and render it".
- Any photo-to-render, 2D-to-3D or plan-to-3D request in a Bitpool context — even if they just say "make this incredible" or "render our office/plant room" with an image attached.
- The user types `/bitpool-3d-image`.
- Do NOT hand-roll conversion prompts. The conversion method and proven templates ship with this skill in `references/`.

Don't use for:

- Original stills with no source image → `/bitpool-cinematic-photo`.
- Video (Veo, assembly/stacking, fly-throughs) → `/bitpool-cinematic-video`.
- Generating the image itself — the output is always a prompt.

## Prerequisites

- A source image from the user. Read it natively or with `vision_analyze` (local path or URL) to build the fidelity inventory.
- For the optional HTML deliverable: the `bitpool-design-system` skill installed (brand tokens). See `references/html-output.md`.

## Procedure

1. **Read the reference files first, each in full** with `read_file` — `references/visual-language.md`, then `references/3d-image-conversion.md`. Nothing is fetched; the whole method ships with the skill. Done when both files are read this run.
2. **Look at the source image** — natively or with `vision_analyze` — and list its distinctive features (six to ten), plus any removals or changes the user asked for. If no image is attached, ask for one (or route to `/bitpool-cinematic-photo`). Done when you have a written feature inventory and removal list.
3. **Pick the conversion template** from `references/3d-image-conversion.md` that matches the source (building photo, plant room photo, isometric cutaway, 2D floor plan, systems overlay). Done when one template is chosen.
4. **Reproduce the template exactly as written**, substituting only the `[bracketed]` slots. Never paraphrase or trim one. Done when every slot is filled and no template line is missing.
5. **Deliver per the output contract** in `references/visual-language.md` — the prompt in one fenced code block, 2–4 terse lever notes, 2–5 one-line swap-in variants, plus attachment advice (full-zoom PNG over PDF, one floor level per generation). Done when all three parts are in the reply.
6. **Only if the user asks to see it** — "mock it up", "show me what it will look like", "an HTML version", "storyboard it" — read `references/html-output.md` and build the HTML with `write_file`. Give the absolute path (CLI) or attach it as `MEDIA:/absolute/path` (messaging). It is additive: the prompt is still delivered in chat. Done when the file exists and its path was given.

## Load-bearing rules

1. **The inventory is the whole game.** Gemini redesigns what you don't name — itemise every distinctive feature of the source in the FIDELITY paragraph.
2. **Counter all four failure modes** in every prompt: unnamed features get redesigned, removals get half-done (state critical removals three times), photo filter instead of re-render (`idealised digital-twin aesthetic`), grainy renders (`completely denoised`).
3. **Templates are reproduced whole.** Only `[bracketed]` slots change.
4. **A mockup is a composition preview, never presented as the real render.** Never redraw the user's photo in HTML.
5. **No text, labels or logos inside generated imagery** — the typography rule in `references/visual-language.md`.

## Pitfalls

- **Writing from memory.** The phrases that do the work (`idealised digital-twin aesthetic`, `completely denoised`, the removal triple) are easy to drop; read the files.
- **Thin inventories.** Under six named features and Gemini starts inventing; a feature missing from the mockup is one Gemini will redesign.
- **Offering HTML unprompted.** Only build it when asked.
- **Optional preview with Hermes's own `image_generate` tool** — only if the user asks for a quick look and has image generation configured. It is a text-to-image FAL/Nous model, not Gemini image-to-image with the source attached, so never present its output as what Gemini will produce.

## Verification

- Both reference files were read this run; the chosen template appears whole with only slots changed.
- The FIDELITY paragraph names six to ten features seen in the source; critical removals appear three times.
- Reply = one code block + 2–4 notes + 2–5 variants; any HTML was requested, lives in a file, and is captioned as a composition preview.

## Reference files

Read the file itself — the table is an index, not a substitute.

| File | Covers |
|---|---|
| `references/3d-image-conversion.md` | The image-to-image method that turns an attached photo, plan, diagram or schematic into a Bitpool archviz render — the four failure modes, the fidelity inventory rule, and the five proven conversion templates. |
| `references/html-output.md` | The optional HTML deliverable — an on-brand composition mockup of the shot, or a formatted handoff page carrying the prompt. Two modes, the brand dependency, and the CSS keyframe spec for animating a video's beats. Identical copy in all three imagery skills. |
| `references/visual-language.md` | The shared foundation every Bitpool image and video prompt is built on — the five campaign motifs, the typography rule, the standard quality blocks, realism anchors, the system colour map, and the output contract. Identical copy in all three imagery skills. |

Change the prompt craft in `references/`, not here. Keep `html-output.md` and `visual-language.md` identical across `bitpool-3d-image`, `bitpool-cinematic-photo` and `bitpool-cinematic-video` — edit every copy the same way.
