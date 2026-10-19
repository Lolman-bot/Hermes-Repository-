# 3D Image Conversion

Gemini **image-to-image** prompts that transform a source image — photo, 2D plan, diagram, screenshot — into a stunning 3D-modelled archviz render. A source image is always attached alongside the prompt.

> **Note**
> Read [Visual Language & Standard Blocks](visual-language.md) first. For original stills with no source image, use Cinematic Photo (see the `/bitpool-cinematic-photo` skill); for video, Cinematic Video (see the `/bitpool-cinematic-video` skill).
>
> If the user also wants to **see** the intended result — "mock it up", "show me what it'll look like" — read [HTML Output](html-output.md). A conversion mockup renders the *target* only; a CSS/SVG mockup can't reproduce the source photo's pixels, so never attempt to redraw it. Make every feature named in the fidelity inventory visible in the mockup — a feature you can't see there is one Gemini will redesign.


## The conversion method

Gemini's failure modes for image-to-image are predictable, and every prompt counters all four.

### It redesigns what you don't name

Write a FIDELITY paragraph that itemises every distinctive feature of the source. **The inventory is the whole game.** Six to ten named features is the sweet spot.

### It half-does removals

State critical removals (`remove all trees`) **three times**: opening line, setting paragraph, quality block.

### It applies a photo filter instead of re-rendering

Use the phrase **`idealised digital-twin aesthetic`** and declare the job: `rebuild this exact structure as clean CGI geometry.` Escalation if texture persists — prepend:

```
full 3D re-render, not a photo filter — rebuild the scene as CGI geometry
```

### It produces grainy under-sampled renders

Close with the standard quality block. **`completely denoised`** is the phrase that kills speckle.

## Prompt skeleton — every conversion

```
Transform this exact [subject] into a stunning ultra high-quality 3D architectural
visualisation render. [Critical removals/changes stated up front.]

FIDELITY — preserve the exact [architecture/layout], proportions and camera angle:
[itemised inventory of every distinctive feature]. Do not redesign, simplify or
modernise — rebuild this exact [structure/scene] as clean CGI geometry.

SETTING — replace the photographic surroundings with a minimal idealised archviz
environment: [clean ground plane, neutral light-grey sky gradient, soft grounded
shadow]. The [subject] is the only hero in frame.

RENDER STYLE — pristine production archviz: [quality block], idealised digital-twin
aesthetic, [restate removals], 16:9.
```

## The four conversion families

| Family | What it does |
| --- | --- |
| **Photo → render (same camera angle)** | Building exteriors, plant rooms, equipment. Keep the source framing; swap the world for a clean archviz environment. |
| **Photo → isometric cutaway** | Re-stage the subject as a bird's-eye 30° cutaway, roof and walls removed, overhead services shown floating where the ceiling is cut away. |
| **2D plan / diagram → 3D** | Floor plans, schematics. Fidelity stated three ways. Advise a full-zoom PNG screenshot over an embedded PDF; one floor level per generation. |
| **Render → systems overlay** | Take an existing cutaway render and add glowing volumetric system loops, pipework 30% transparent only where the flow is visible. |

---

# Proven templates

Adapt; don't rewrite.

## 1. Building photo → 3D render

Same camera angle as the source; world swapped for a clean archviz environment. Shown populated with the Bitpool HQ inventory — replace the FIDELITY list for other buildings.

```
Transform this exact building into a stunning ultra high-quality 3D architectural visualisation render. Remove all trees and street vegetation completely so the full facade is unobstructed from corner to corner.

FIDELITY — preserve the building's exact architecture, proportions and camera angle: the two-storey commercial office with its green-tinted reflective glass curtain wall, the rhythm of slender white vertical mullion fins across both wings, the bold dark-grey cantilevered roof canopies projecting over each glazed volume, the central copper-bronze panelled feature box rising above the entry, the recessed ground-level entry beneath it, and the low grey boundary wall and driveway on the left. Do not redesign, simplify or modernise the building — rebuild this exact structure as clean CGI geometry.

SETTING — replace the photographic surroundings with a minimal idealised archviz environment: a clean light-grey paved forecourt and dark asphalt street in the foreground with crisp kerb lines, low sculpted hedging where the garden strips sit (no trees), a soft neutral light-grey sky gradient behind the building, and the structure casting a single soft grounded shadow. The building is the only hero in frame.

RENDER STYLE — pristine production archviz: fully ray-traced global illumination, completely denoised, zero grain, zero noise, perfect anti-aliasing, physically based materials — the glass rendered with rich green-teal reflectivity and subtle sky reflections, the copper feature box with a warm brushed-metal sheen catching the light, the white fins crisp and clean, the grey canopies matte with sharp shadow lines. Late-afternoon directional sunlight from the left, warm key light raking across the copper and glass, gentle ambient occlusion under the canopies and along the fin reveals. Sharp focus across the entire frame, no depth-of-field blur, 8K, Octane / V-Ray quality, idealised digital-twin aesthetic, no people, no cars, no trees, no text, no logos, no watermarks, 16:9.
```

**Levers:** the fidelity paragraph names every feature (copper box, white fins, green glass, canopies) — Gemini keeps what you name. `remove all trees` appears three times (opening, setting, quality block) because single mentions get half-done.

**For a different building:** walk the source image and itemise — storey count, facade system, cladding materials and colours, distinctive elements (canopies, fins, feature boxes, signage zones, entries), site features.

## 2. Plant room photo → 3D render

```
Transform this exact chiller plant room into a stunning ultra high-quality 3D architectural visualisation render. Preserve the exact layout, camera angle and equipment placement: the row of grey switchboards and MCC cabinets along the left wall, the silver-jacketed insulated pipework with blue and green flanged valves in the left foreground, the centre aisle of centrifugal pumps on concrete inertia bases with red flexible couplings, the two large pale-green water-cooled centrifugal chillers on the right with their compressors and marine water boxes, the yellow safety line marking on the sealed concrete floor, the overhead cable trays, red fire services pipework and blue/green structural steel. Re-render everything in pristine archviz quality: fully ray-traced global illumination, completely denoised, zero grain, zero noise, perfect anti-aliasing, physically based materials — brushed and jacketed metal with crisp specular highlights, smooth painted equipment surfaces, clean matte concrete. Replace the flat fluorescent lighting with refined studio-grade lighting: soft white key light, subtle cyan accent glow washing the aisle and reflecting off the floor, gentle ambient occlusion in the pipe junctions and under equipment. Make the floor lightly reflective with a subtle polished sheen catching the chillers and lights. Slightly deepen the colour grade — richer greens on the chillers, cleaner whites, controlled contrast. Crisp sharp focus across the entire frame, 8K production render quality, Octane / V-Ray look, idealised digital-twin aesthetic, no people, no text, no logos, keep 16:9 composition.
```

If the first pass keeps too much photo texture, prepend `full 3D re-render, not a photo filter — rebuild the scene as CGI geometry`.

## 3. Photo → isometric bird's-eye cutaway

Re-stages the source subject as a 30° bird's-eye cutaway. Works for plant rooms, offices, whole floors.

```
Using this image as the reference for equipment and layout, create an ultra high-quality 3D architectural render of the entire [room/space] as an isometric cutaway bird's-eye view from above at a 30-degree angle, roof and walls removed to expose the complete layout in one frame. [ITEMISE the contents and their relative positions from the source image — wall by wall, aisle by aisle.] Overhead services — [cable trays, pipework, steel] — shown floating where the ceiling is cut away. [Floor description: sealed concrete, yellow safety walkways, housekeeping pads.] Rendered in pristine archviz quality: fully ray-traced global illumination, completely denoised, zero grain, zero noise, perfect anti-aliasing, physically based materials, soft ambient occlusion, studio-clean neutral lighting with subtle cyan accent glow along the walkways. Crisp geometry, sharp focus across the entire frame, 8K production render, Octane / V-Ray look, idealised digital-twin aesthetic, neutral white-grey environment, no people, no text, no logos, 16:9.
```

**Key phrases:** "isometric cutaway bird's-eye view" + "roof and walls removed" + "complete layout in one frame" flips the perspective; "shown floating where the ceiling is cut away" stops Gemini re-drawing a ceiling for the overhead services.

**Plant room positional inventory** (proven): switchboard/MCC lineup along one wall · centrifugal pumps on inertia bases down the centre aisle · two pale-green centrifugal chillers (compressors, barrels, marine water boxes) opposite · silver-jacketed pipework with blue/green flanged valves connecting all, headers on blue/green structural steel · red fire pipework and galvanised trays at high level.

## 4. 2D floor plan → 3D floor plan

Attach a full-zoom PNG screenshot (beats an embedded PDF); one floor level per generation.

```
Convert this 2D architectural floor plan into a stunning ultra high-quality 3D floor plan visualisation, isometric cutaway view from above at a 30-degree angle, walls extruded to approximately 1.2 metre doghouse height so every room interior remains fully visible from this aerial view.

FIDELITY — this is the critical rule: reproduce the floor plan EXACTLY as drawn. Preserve the precise wall positions, room proportions, door swings and openings, window locations, corridor widths, stair and lift core positions, and overall building footprint from the source drawing. Do not add rooms, remove walls, change the layout, or reinterpret the plan. Every room in the source must appear in the render in the same position and at the same relative scale. Read the room labels on the plan and furnish each space according to its labelled function.

PRESENTATION — premium architectural visualisation: extruded walls in clean matte white with a subtle crisp top edge, floor finishes differentiated by zone — warm timber or carpet in occupied spaces, large-format grey tile in lobbies and corridors, sealed concrete in plant and back-of-house areas, tile in wet areas. Furnish realistically and sparingly to communicate function, in a restrained modern palette of whites, light timber, charcoal and soft grey, with subtle plants for life. Doors shown open at their hinge positions, glazing rendered as thin transparent panes with light frames.

LIGHTING AND QUALITY — soft studio daylight from above-left, gentle shadows grounding every wall and furniture piece, soft ambient occlusion in corners, lightly reflective floors. Fully ray-traced global illumination, completely denoised, zero grain, zero noise, perfect anti-aliasing, physically based materials, sharp focus across the entire frame, 8K production render, Octane / V-Ray archviz quality, clean white-grey background with a soft contact shadow under the building slab, no people, no text, no labels, no dimensions, no logos, no watermarks, 16:9.
```

Anti-drift escalation — prepend if Gemini "improves" the plan:

```
This is a technical conversion task, not a creative one — geometric accuracy to the source drawing takes priority over aesthetics.
```

Variants:

- **Top-down dollhouse** — `straight orthographic top-down view with walls extruded` (easiest fidelity)
- **Plant / BMS plan** — swap the furnishing language for plant equipment language
- **Dark twin** — `darkened render, rooms softly illuminated from within, cyan accent lighting tracing the corridors`

## 5. Render → glowing systems overlay

Second-pass conversion: takes an existing cutaway render and adds the digital-twin system flows.

```
Using this exact render, keep the room, camera angle, equipment and layout completely unchanged, and overlay each hydraulic and electrical system as a softly glowing volumetric flow path travelling through its actual pipework and cabling: the CHILLED WATER LOOP in luminous cool blue, flowing from the chiller evaporator barrels through the supply header with subtle streaks and a gentle outer glow, returning through the pumps; the CONDENSER WATER LOOP in luminous emerald green from the condenser barrels toward the cutaway edge and back; the ELECTRICAL DISTRIBUTION in luminous cyan, thin bright energy lines from the switchboards along the cable trays to every motor and panel; the REFRIGERANT CIRCUIT inside each chiller as a faint warm amber glow. Flow direction shown by taper and motion-streaks of the glowing streams, brighter at the source, never as arrows or text. The pipework becomes 30% transparent only where the flow is visible, revealing the water moving inside. Darken the ambient room lighting to dusk level so the glows carry the image, with the coloured light casting softly onto nearby surfaces and reflecting in the floor. Fully ray-traced with volumetric light scattering on the glow paths, completely denoised, zero grain, zero noise, 8K, sharp focus across the entire frame, no arrows, no text, no labels, no logos, no watermarks, 16:9.
```

**Levers:** "keep … completely unchanged" makes it an overlay, not a redesign; arrows and text banned twice; 30% selective transparency = x-ray, not ghost; dusk-level room so the glows pop.

## Variant blocks

**After-hours dark twin (any conversion)**

```
lights dimmed to near-dark, equipment status LEDs and VSD displays glowing, single cyan ambient accent washing the [aisle/entry], dark cinematic low-key grade
```

**Dusk hero (buildings)**

```
dusk render, deep blue-grey sky, interior lights glowing through the glass on every level, one corner office brightest, feature elements uplit, cyan accent light washing the entry
```

**White clay model** — strong minimal asset for deck covers

```
render as a pure white clay architectural model, only [signature feature, e.g. the copper feature box] and glass retaining colour, studio backdrop
```

**Roof-lift cutaway (buildings)**

```
then present as an isometric cutaway from above, roof lifted to reveal the furnished floor plates inside
```
