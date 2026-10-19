# HTML Output

An **optional second deliverable**. The default output of all three skills is still a prompt — see the output contract on [Visual Language](visual-language.md). This page covers what to do when the user also wants HTML.

> **Important**
> **A mockup is a composition preview, not a render.** It exists so composition, framing and pacing can be judged before spending Gemini or Veo credits. Every mockup carries a caption saying so. Never present one as the generated image or video, and never imply the real output will look like CSS.


## Choosing the mode

Two modes. Infer from the user's wording; ask only if genuinely ambiguous, and ask in one line.

| The user says… | Mode |
| --- | --- |
| "show me what it'll look like", "mock it up", "preview it", "storyboard it", "can I see it" | **Scene Mockup** |
| "make me a page for this", "send this to \[person]", "an HTML version of the prompt", "document this prompt set" | **Prompt Handoff** |
| "an HTML version" with nothing else to go on | Ask which — one line, offer both |

Both modes are additive. The prompt still gets delivered in chat as normal; the HTML is extra, not a replacement.

## Brand — read it, don't invent it

HTML output follows the Bitpool design system. Take the values from the `bitpool-design-system` skill — load its files with `skill_view` (for example `skill_view(name='bitpool-design-system', file_path='references/tokens.md')`) and never approximate the palette from memory.

| Need | Read |
| --- | --- |
| Colour tokens, type scale, motion easing, breakpoints | `bitpool-design-system/references/tokens.md` — both themes, values verbatim |
| The patterned background beat, nav, hero | `bitpool-design-system/references/components.md` |

That skill ships in the **bitpool-design-foundations** section, not this one. If it isn't installed, ask the user to install it (`hermes skills install Lolman-bot/Hermes-Repository-/skills/bitpool-design-foundations/bitpool-design-system --category bitpool`) or to paste the token sheet — never guess the values.

**Theme by mode:** Scene Mockup uses **dark** — it stands in for a marketing surface. Prompt Handoff uses **light** — it's a document, read closely and often printed. That split is the design system's own rule, not a preference.

> **Warning**
> **The cube logo cannot be reconstructed.** Its bytes live in the `bitpool-design-system` skill's `assets/` folder and corrupt when round-tripped through text-based tools. These three imagery skills ship in a different section and don't carry that asset.
>
> - **Scene Mockup** — no logo, and that's correct. It stands in for a generated image, and the typography rule bans logos from generated imagery anyway.
> - **Prompt Handoff** — it's a Bitpool document, so the logo rule applies. If the cube is wanted, ask the user for the PNG or to run `bitpool-design-system` alongside. **Never redraw, approximate or SVG-trace the cube.**


## Mode A — Scene Mockup

A single self-contained HTML file rendering the composition of the shot.

### Build it from these

| Scene element | Technique |
| --- | --- |
| Building massing | Positioned `div`s; `transform: perspective() rotateY()` for three-quarter angles |
| Glass curtain wall | `repeating-linear-gradient` for the mullion grid over a green-teal or anthracite base |
| The lit office | One bright cell in the facade grid with a warm `box-shadow` bloom |
| Isometric cutaway | SVG with `transform: rotateX(60deg) rotateZ(45deg)`, or hand-plotted 30° polygons |
| Plant equipment | Simple SVG silhouettes — chiller barrels as rounded rects, pumps as circles on pads |
| Pipework | SVG `<path>` with round caps, `stroke-width` for diameter, a lighter parallel path for the jacketed highlight |
| Glowing system loops | SVG `<path>` + `filter: drop-shadow()` + animated `stroke-dashoffset` for flow direction |
| The cyan pulse | Animated `box-shadow` or `stroke` opacity, `#00ADEF` |
| Sky / ground | `linear-gradient` — neutral light-grey gradient for archviz, deep navy for dusk |

### Rules

- **16:9, always.** `viewBox="0 0 1600 900"` for SVG; `aspect-ratio: 16/9` for CSS layouts. Every prompt on these pages ends in `16:9` — the mockup matches.
- **Self-contained.** One file. No CDN, no external fonts, no remote images. Inline everything. Load Inter if available, but always give a system-sans fallback in the stack.
- **Responsive.** `max-width: 100%`, scale with the container. It gets viewed on a phone.
- **No text inside the frame.** The scene carries no labels — same rule as the prompts. The one exception is Mode-specific markers below.
- **Caption underneath, outside the frame.** One line: what template, what subject, and that it's a composition preview.

### Per-medium notes

#### Cinematic Photo

Single 16:9 frame.

Mark the **lockup zone** — the clean negative space the typography rule reserves, usually the upper-right third — as a dashed hairline outline labelled `lockup zone` *outside* or at low opacity. It's the one permitted label, because reserving that space is a load-bearing requirement of the prompt.

For a series, render each variant as its own frame in a vertical stack with its variant name as a caption.

#### 3D Image Conversion

Even when you can see the source image (natively or through `vision_analyze`), a CSS/SVG mockup can't reproduce its pixels, so **do not attempt to redraw the user's photo.** Two acceptable layouts:

- **Target only** — mock up the intended render, captioned with which source it converts.
- **Side-by-side** — a labelled placeholder panel (`source photo — attached in Gemini`) beside the target mockup, so the fidelity inventory can be reviewed against a real photo held next to the screen.

Where the fidelity inventory names features, make each one visible in the mockup. The point of this mockup is to check that the inventory is complete — a feature you can't see in the mockup is a feature Gemini will redesign.

#### Cinematic Video

Animated, driven by CSS keyframes. See the animation spec below. The timings must match the prompt's timestamped beats exactly — an animation that doesn't is worse than none, because it teaches the wrong pacing.

## Mode B — Prompt Handoff

A formatted page carrying the prompt set, for whoever runs the generation.

### Structure

### Header

Subject, target model (Gemini / Veo), which template it came from, and the attachment requirement if it's image-to-image.

### The prompt, copy-ready

In a `<pre>` with a **Copy** button. Preserve the paragraph breaks and CAPS section headers exactly — they're load-bearing.

```html
<button onclick="navigator.clipboard.writeText(
  document.getElementById('p1').innerText)">Copy prompt</button>
<pre id="p1">…prompt text…</pre>
```

### Lever notes

The 2–4 bullets on what's doing the work, so the operator knows what not to edit out.

### Variants table

Each variant as a row: name, the swap-in fragment in a copy-ready cell, and what it changes.

### Generation notes

Aspect ratio, attachment format (full-zoom PNG over PDF), one-floor-per-generation where relevant, and the escalation fragments to try if the first pass drifts.

Light theme. Print-clean — no dark backgrounds bleeding ink, and let the prompt block wrap rather than scroll horizontally on paper.

## The video animation spec

Total duration **8 seconds**, matching Veo's stability window. Never animate longer — the preview must teach the same pacing the prompt will produce.

### Beat → percentage mapping

`animation-duration: 8s`, so percentages are `time / 8 × 100`.

| Template | Beat | Time | Keyframe % |
| --- | --- | --- | --- |
| Building stacking | Opening | 0.0–0.5s | 0–6.25% |
| | Assembly | 0.5–6.0s | 6.25–75% |
| | Final beat + hero hold | 6.0–8.0s | 75–100% |
| Plant room self-assembly | Opening | 0.0–0.5s | 0–6.25% |
| | Assembly (7 steps) | 0.5–6.5s | 6.25–81.25% |
| | Final beat + hero hold | 6.5–8.0s | 81.25–100% |

Stagger elements with `animation-delay` computed off that table. The plant room's seven steps span 6.0s, so roughly `0.5s + (n × 0.857s)` — but weight it: heavy items (chillers) get a longer slot, the pump series a rapid one, matching the mass-and-rhythm rule.

### Motion rules

- **Easing `cubic-bezier(0.2, 0.8, 0.2, 1)`.** The brand's motion rule. Never bouncy, never a spring overshoot beyond the settle below.
- **The 2-centimetre settle.** Each landing overshoots ~2px past its resting position, then eases back — the prompt's `2-centimetre settle` made literal.
- **A cyan pulse per landing.** A `box-shadow` or border flash in `#00ADEF` at the contact line, decaying over ~0.3s.
- **Pipework grows, never drops.** Animate `stroke-dashoffset` or `scaleX` from the origin — never `translateY`. Falling pipes read wrong; growth reads as connection.
- **Rigid modules.** Animate `transform` and `opacity` only. Never animate `width`/`height`/`border-radius` on a module — that reads as morphing, the exact failure the anti-morph clause exists to prevent.
- **The hero hold.** The last 1.5s is a locked still. No motion in those keyframes at all.

### Keyframe skeleton

```css
@keyframes drop-in {
  0%,   6%   { opacity: 0; transform: translateY(-180px); }
  10%        { opacity: 1; }
  38%        { transform: translateY(2px); }   /* the settle overshoot */
  44%, 100%  { transform: translateY(0); }
}

@keyframes cyan-pulse {
  0%, 40%   { box-shadow: 0 0 0 0 rgba(0,173,239,0); }
  46%       { box-shadow: 0 -2px 18px 2px rgba(0,173,239,0.75); }
  56%, 100% { box-shadow: 0 0 0 0 rgba(0,173,239,0); }
}

.module {
  animation: drop-in 8s cubic-bezier(0.2,0.8,0.2,1) forwards,
             cyan-pulse 8s linear forwards;
}
.module:nth-child(2) { animation-delay: 0.36s; }   /* from the beat table */
```

Use `forwards`, not `infinite` — the sequence ends on the hero still, same as the prompt. Offer a **Replay** button rather than looping.

### Accessibility

```css
@media (prefers-reduced-motion: reduce) {
  .module { animation: none; opacity: 1; transform: none; }
}
```

Reduced motion shows the completed final frame — which is the hero still, so nothing is lost.

## Delivery

Write the HTML to a file with `write_file` and tell the user the absolute path so they can open it in a browser. On a messaging platform (Telegram, Discord, Slack and so on), also send it as an attachment by putting `MEDIA:/absolute/path/to/file.html` in the reply. Never paste a full HTML file into chat as the primary deliverable; it's unreadable at that length.

## Anti-patterns

- Presenting a mockup as if it were the generated render or video
- External assets of any kind — CDN scripts, remote fonts, hotlinked images
- Redrawing, tracing or approximating the cube logo
- Labels or annotations inside a scene frame, beyond the permitted lockup-zone marker
- A video preview longer or shorter than 8 seconds, or with timings that don't match the prompt's beats
- Bouncy or staggered-bounce easing
- Animating a module's geometry (reads as morphing) or dropping pipework (should grow)
- Skipping the brand fetch and approximating the palette from memory
- Delivering HTML *instead of* the prompt — it's an addition, never a substitute
