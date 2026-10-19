# Visual Language & Standard Blocks

Read this page first for **any** Bitpool image or video prompt task, then read the page for the specific medium. Everything here applies to all three skills.

## The Bitpool visual language

Every image and every video serves one campaign story: **Bitpool sees inside buildings.** Five recurring motifs carry it.

1. **The lit office** — one glowing room in an otherwise dark or sealed building. Carries "we never leave the office" without text. Goes in every variant of a tower shot.
2. **The cyan pulse** — thin cyan (`#00ADEF`) light lines and accents tracing edges, walkways, aisles, junctions and system paths. The brand accent quietly owning the data and power story. Never arrows, never labels.
3. **The cutaway reveal** — roof or walls removed, a fully furnished interior exposed like a dollhouse. The product promise made physical.
4. **The digital twin** — physical plant rendered as its idealised clean CGI model. The phrase **"idealised digital-twin aesthetic"** is the term that flips Gemini out of photo-filter mode into a true render.
5. **Systems as light** — hydraulic and electrical systems as glowing volumetric flows through real pipework. Matches real pipe ID conventions *and* the brand.

## The typography rule

> **Important**
> **Always end a prompt with `no text, no labels, no logos, no watermarks`.**


Gemini and Veo both mangle type. The bitpool wordmark and tagline are composited afterwards — so hero stills should also request **clean negative space** (usually the upper-right third) for the lockup.

## Standard quality blocks

Use verbatim. **"Completely denoised"** is the phrase that kills the speckled, under-sampled look — never drop it.

### Image quality closer

```
fully ray-traced global illumination, completely denoised, zero grain, zero noise,
perfect anti-aliasing, physically based materials, sharp focus across the entire
frame, no depth-of-field blur, no film grain, no chromatic aberration, 8K production
render, Octane / V-Ray quality, no text, no labels, no logos, no watermarks, 16:9.
```

### Image quality closer — conversion variant

For image-to-image render conversions, which need the specular and people/vegetation negatives:

```
fully ray-traced global illumination, completely denoised, zero grain, zero noise,
perfect anti-aliasing, physically based materials with crisp specular highlights,
sharp focus across the entire frame, no depth-of-field blur, no film grain, no
chromatic aberration, 8K production render, Octane / V-Ray quality, no people,
no text, no labels, no logos, no watermarks, 16:9.
```

### Video quality closer

```
fully ray-traced global illumination, completely denoised, zero grain, zero noise,
zero flicker, temporally stable geometry and textures across all frames, physically
based materials, sharp focus across the entire frame, no motion blur smearing, no
warping geometry, no flickering windows, 4K, 16:9, no text, no labels, no logos,
no watermarks.
```

## The three-times rule

State critical negatives — `remove all trees`, `no people` — **three times**: the opening line, the body or setting paragraph, and again in the quality block. Gemini half-does single-mention removals.

## Photoreal camera anchors

Swap the render terms for camera language when the brief is photography, but keep the negative list.

| Subject | Anchor |
| --- | --- |
| Towers / buildings | `full-frame camera, 35mm lens, f/8, deep depth of field, high dynamic range, editorial real-estate photography style` |
| Plant rooms | `24mm wide-angle, f/8, deep depth of field, one-point perspective down the aisle, editorial industrial photography style` |
| Detail / over-the-shoulder shots | `f/2.8 shallow depth of field` |

## The render flip trio

Three phrases together flip Gemini from photo to render — use all three:

```
isometric cutaway view from above at a 30-degree angle
roof and walls removed
architectural visualisation style
```

Add `shown floating where the ceiling is cut away` for overhead services — it stops Gemini re-drawing a ceiling.

## Realism anchors

These stop invented nonsense equipment. Keep them in **every** variant of a subject.

### Plant rooms

`silver-jacketed insulated pipework` · `flanged valve assemblies` · `housekeeping pads` · `concrete inertia bases` · `red flexible couplings` · `VSD displays glowing` · `binder test points` · `Y-strainers`

### Data centres

`42U racks` · `hot-aisle/cold-aisle containment` · `perforated cooling tiles` · `busway with tap-off boxes` · `CRAC units`

### Bitpool HQ

**37 Brandl St, Eight Mile Plains** — use this inventory verbatim in the fidelity paragraph whenever the source is the office:

two-storey commercial office; green-tinted reflective glass curtain wall; rhythm of slender white vertical mullion fins across both wings; bold dark-grey cantilevered roof canopies projecting over each glazed volume; central copper-bronze panelled feature box rising above the recessed ground-level entry; low grey boundary wall and driveway on the left.

Render style notes: glass with rich green-teal reflectivity and subtle sky reflections; copper box with a warm brushed-metal sheen catching the light; white fins crisp and clean; grey canopies matte with sharp shadow lines; late-afternoon directional sun from the left.

## System glow colour map

Real pipe ID convention, plus cyan for electrical so the brand owns the power story.

| System | Colour |
| --- | --- |
| Chilled water | luminous cool blue |
| Condenser water | luminous emerald green |
| Electrical | luminous cyan (`#00ADEF`, brand) |
| Refrigerant | faint warm amber |
| Heating water | warm orange-red |

Flow direction is shown by **taper and motion streaks**, brighter at the source — **never** arrows, never labels. Ban arrows and text *twice* in a systems prompt; Gemini loves turning these into labelled diagrams.

## Selective transparency

```
pipework becomes 30% transparent only where the flow is visible
```

Selective transparency reads as x-ray vision. Full transparency reads as a ghost.

## Series consistency suffix

Append to every variant in a set so a batch stays visually coherent:

```
same [subject], same [layout/equipment], consistent [photography / 3D architectural
visualisation] series, [grade], 16:9, no text, no watermarks.
```

## The after-hours variant

Always offer at least one — it's the sibling of the night office tower campaign image and the most on-brand frame Bitpool has.

```
lights dimmed to near-dark, equipment status LEDs and VSD displays glowing, single
cyan ambient accent washing the [aisle/entry], dark cinematic low-key grade
```

## Output contract

These are **prompt-writing** skills. The output is always a prompt — never the generated image or video.

### The prompt, in one fenced code block

A single block. Use CAPS section headers inside long prompts — Gemini and Veo both respect them.

### 2–4 terse bullet notes

Only the levers that actually matter for this prompt. Not a description of what you did.

### 2–5 one-line variants

Swap-in fragments, not full rewrites. One of them is always the after-hours variant.

**Voice:** David's style — terse, outcome-focused, no process narration.

### The optional HTML deliverable

If the user asks to *see* it — "mock it up", "show me what it'll look like", "an HTML version" — also produce HTML per [HTML Output](html-output.md): a composition mockup of the shot, or a formatted handoff page carrying the prompt. It's **additive**; the prompt above is still delivered in chat. Don't offer it unprompted on every request, and never present a mockup as the real render.

## Attachment handling

- PDFs render small in Gemini. Advise a **full-zoom PNG screenshot** instead.
- **One floor level per generation** for floor plans. Multi-level attachments drift.
