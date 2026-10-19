# Cinematic Photo

Production-grade Gemini image prompts that produce Bitpool marketing stills — photoreal architectural and industrial photography, 3D archviz renders, and image-to-image conversions.

> **Note**
> Read [Visual Language & Standard Blocks](visual-language.md) first. This page assumes the motifs, quality blocks, realism anchors, colour map and output contract from that page.
>
> If the user also wants to **see** the shot — "mock it up", "show me what it'll look like" — read [HTML Output](html-output.md). A still mockup is one 16:9 frame with the lockup zone marked, since the typography rule reserves that negative space.


## Prompt architecture

```
[FORMAT LINE]        — photoreal photography OR 3D render, style anchor
[FIDELITY / LAYOUT]  — itemised inventory of what must be exact (image-to-image)
[SCENE / COMPOSITION]— subject, environment, negative space
[LIGHTING & GRADE]
[QUALITY BLOCK]      — the standard closer
```

## The two modes

### Photoreal photography

Anchor with camera language:

```
Shot on a full-frame camera, 35mm lens (towers) / 24mm wide-angle (plant rooms),
f/8, deep depth of field, high dynamic range, editorial real-estate / industrial
photography style.
```

### 3D render

Anchor with the flip trio:

```
isometric cutaway view from above at a 30-degree angle, roof and walls removed,
architectural visualisation style
```

Overhead services `shown floating where the ceiling is cut away` — stops Gemini re-drawing a ceiling.

## Fidelity paragraphs (image-to-image)

When the user attaches a reference to transform: **itemise every feature to preserve.** Gemini keeps what you name and redesigns what you don't.

```
FIDELITY — preserve the exact architecture/layout, proportions and camera angle:
[itemised list of every distinctive feature]. Do not redesign, simplify or
modernise — rebuild this exact structure as clean CGI geometry.
```

State critical removals three times (see the three-times rule). If photo texture persists after a render conversion, prepend:

```
full 3D re-render, not a photo filter — rebuild the scene as CGI geometry
```

For floor plans, state fidelity three ways: `Do not add rooms, remove walls, change the layout, or reinterpret the plan.` Escalation if Gemini "improves" the plan:

```
This is a technical conversion task, not a creative one — geometric accuracy to the
source takes priority over aesthetics.
```

---

# Proven templates

Battle-tested. **Adapt; don't rewrite.** Each section notes what the key phrases do.

## 1. Photoreal office tower

Campaign hero still — the "we never leave the office" family. Wordmark composited afterwards into the negative space.

```
Photorealistic architectural photography of a modern 14-storey glass office tower, dark anthracite curtain-wall facade with a tight grid of mullions, shot from an elevated three-quarter aerial angle across the street. Bright mid-morning daylight, crisp blue sky with scattered soft clouds, sun raking across the glass creating subtle reflections of the sky and neighbouring buildings. One corner office on an upper floor has interior lights visibly on, warm glow contrasting the cool daylight — a few silhouetted people inside at desks. Street level: tree-lined boulevard, parked cars, traffic lights, pedestrians small in frame. Surrounding low-rise city skyline in the background haze. Large clean negative space in the upper right third of the frame for typography. Shot on a full-frame camera, 35mm lens, f/8, deep depth of field, high dynamic range, editorial real-estate photography style, ultra-detailed, no text, no logos, 16:9.
```

**Keys:** "negative space upper right + no text" — composite the lockup later. The one-lit-office motif goes in EVERY variant; it carries the tagline without the tagline.

Time-of-day swaps:

- **Golden hour** — `late golden-hour light, low sun flaring off the glass facade, long shadows across the street, amber and teal colour grade`
- **Blue hour** (closest to the original night campaign image) — `pre-dawn blue hour, sky gradient from deep navy to pale orange at the horizon, only that one corner office lit, street lights still on`
- **Overcast moody** — `flat overcast sky, soft diffuse light, rain-slicked street with reflections, muted desaturated grade, single lit office cutting through the grey`
- **Storm** — `dramatic storm front approaching behind the tower, dark clouds, shaft of sunlight still hitting the facade, that one office glowing`
- **Ground-level hero** — `shot from street level looking up at the tower corner, extreme wide 24mm perspective, sky filling the frame, the lit corner office visible 12 floors up`
- **Through-the-window** — `interior shot from inside that corner office at dusk, two engineers at standing desks with wall-mounted dashboards glowing cyan, floor-to-ceiling windows showing the city below, cinematic`

## 2. Photoreal chiller plant room

```
Photorealistic industrial photography of a large commercial HVAC central chiller plant room. Two massive centrifugal water-cooled chillers in pale factory-green and grey enclosures, dominant in frame, with insulated chilled-water and condenser-water pipework — large diameter pipes wrapped in silver-jacketed insulation, painted steel headers in blue and green, flanged valve assemblies, pressure gauges and binder points visible. End-suction and vertical inline centrifugal pumps on concrete inertia bases with flexible couplings and Y-strainers. Along one wall, a row of grey electrical switchboards and motor control centre cabinets with status indicator lights, VSD drives with small digital displays glowing. Sealed concrete floor with painted safety walkways in yellow, floor drains, housekeeping pads under equipment. Overhead: cable trays, sprinkler pipes, LED high-bay lighting casting even cool-white light with soft shadows. Slight haze in the air catching the light. Shot on full-frame camera, 24mm wide-angle lens, f/8, deep depth of field, one-point perspective down the plant room aisle, high dynamic range, editorial industrial photography style, clean and well-maintained facility, ultra-detailed, no people, no text, no logos, 16:9.
```

**Keys:** the realism anchors — "silver-jacketed insulation", "flanged valve assemblies", "housekeeping pads" — stop invented pipework. Keep them in every variant.

Variants:

- **Technician detail** — `one technician in hi-vis and hard hat checking a VSD display, shot over the shoulder, shallow f/2.8 depth of field, chillers blurred behind`
- **After-hours** — `lights dimmed, equipment status LEDs and drive displays glowing in the dark, single work light on, cinematic low-key grade`
- **Switchboard hero** — `close three-quarter shot of the MCC lineup, panel doors closed, indicator lights and digital metering visible, chillers soft in background`
- **Pump gallery** — `row of vertical inline pumps on inertia bases in foreground, symmetrical composition, headers running overhead`
- **Mezzanine wide** — `elevated angle from mezzanine looking down over both chillers and the pipe runs, showing full plant layout`

## 3. Data centre floor — isometric 3D render

```
Ultra high-quality 3D architectural render of an entire data centre floor, isometric cutaway view from above at a 30-degree angle, walls removed to expose the full white-space layout. Long parallel rows of black 42U server racks in hot-aisle/cold-aisle configuration, hot aisles enclosed with clear containment panels and sliding end doors, each rack face showing subtle blue and green LED status lights. Raised access floor with perforated cooling tiles in the cold aisles, a few tiles lifted to reveal underfloor cabling and the chilled air plenum. Overhead: yellow structured cable trays and black ladder racks running above the rows, busway power distribution with tap-off boxes. CRAC cooling units along the perimeter, UPS cabinets and PDUs in an electrical corner. Rendered in Octane / V-Ray quality: fully ray-traced global illumination, completely denoised, zero grain, zero noise, smooth clean surfaces, crisp sharp edges, perfect anti-aliasing. Physically based materials — brushed metal, perforated steel rack doors, matte floor tiles — with soft ambient occlusion and studio-clean lighting. Neutral white-grey environment with cyan accent lighting in the aisles. 8K resolution, pristine archviz production quality, sharp focus across the entire frame, no depth-of-field blur, no film grain, no chromatic aberration, no people, no text, no logos, 16:9.
```

**Keys:** the photo→render flip trio — "isometric cutaway view" + "walls removed" + "architectural visualisation style".

Variants:

- **Photoreal version** — replace the first line with `Photorealistic wide-angle photograph from the corner of a data centre floor, 24mm lens, one-point perspective down a cold aisle`, and drop the cutaway language
- **Dark ops** — `lights off, rack LEDs and cyan aisle containment lighting as the only illumination, dark moody render, glossy floor reflections`
- **Airflow schematic** — `semi-transparent ghosted building shell, racks solid, airflow visualised as soft blue (supply) and red (return) volumetric streams flowing through aisles`
- **Single pod hero** — `close isometric render of one contained pod, eight racks per side, containment doors open at one end, underfloor and overhead infrastructure in cross-section`
- **Heat-map plan** — `straight orthographic top-down render of the full floor, like a live BMS floor plan, rack rows colour-coded by heat zone from cool blue to warm amber`

## 4. Photo → 3D render conversion

Image-to-image. The fidelity inventory is the whole game — Gemini keeps what you name and redesigns what you don't.

```
Transform this exact [building/room] into a stunning ultra high-quality 3D architectural visualisation render. [Critical removals up front, e.g. "Remove all trees and street vegetation completely so the full facade is unobstructed."]

FIDELITY — preserve the [building's/room's] exact architecture, proportions and camera angle: [ITEMISE every distinctive feature — facades, cladding, equipment, colours, positions]. Do not redesign, simplify or modernise — rebuild this exact structure as clean CGI geometry.

SETTING — replace the photographic surroundings with a minimal idealised archviz environment: clean light-grey paving / dark asphalt with crisp kerb lines, soft neutral light-grey sky gradient, the structure casting a single soft grounded shadow. The [subject] is the only hero in frame.

RENDER STYLE — pristine production archviz: [standard quality block], idealised digital-twin aesthetic, [restate removals], 16:9.
```

**Rules:** removals stated THREE times (opening, setting, quality block); "idealised digital-twin aesthetic" flips photo-filter → true render; if photo texture persists, prepend `full 3D re-render, not a photo filter — rebuild the scene as CGI geometry`.

For the Bitpool HQ feature inventory and its render style notes, see the Bitpool HQ section on [Visual Language](visual-language.md).

HQ variants:

- **Dark twin hero** — `dusk render, deep blue-grey sky, interior lights glowing through the green glass on both levels, one corner office brightest, copper box uplit, cyan accent light washing the entry`
- **Isometric cutaway** — `then present as an isometric cutaway from above, roof lifted to reveal both furnished floor plates`
- **White clay** — `render as a pure white clay architectural model, only the copper feature box and glass retaining colour, studio backdrop`

For the full set of conversion families (isometric cutaway restaging, plan→3D, systems overlay), see 3D Image Conversion (see the `/bitpool-3d-image` skill).

## 5. Plant room — bird's-eye isometric cutaway

```
Ultra high-quality 3D architectural render of an entire commercial HVAC chiller plant room, isometric cutaway bird's-eye view from above at a 30-degree angle, roof and walls removed to expose the complete plant layout in one frame. Along one wall, a continuous row of grey electrical switchboards and MCC cabinets with indicator lights and VSD displays. Down the centre aisle, multiple centrifugal pumps on concrete inertia bases with red flexible couplings, electric motors and suction guides. On the opposite side, two large pale-green water-cooled centrifugal chillers with visible compressors, evaporator and condenser barrels and marine water boxes. Connecting everything: silver-jacketed insulated chilled-water and condenser-water pipework with blue and green flanged valve assemblies, headers running overhead on blue and green structural steel supports, red fire services pipework and galvanised cable trays at high level shown floating where the ceiling is cut away. Sealed concrete floor with yellow safety walkway markings and housekeeping pads under all equipment. Rendered in pristine archviz quality: fully ray-traced global illumination, completely denoised, zero grain, zero noise, perfect anti-aliasing, physically based materials, soft ambient occlusion, studio-clean neutral lighting with subtle cyan accent glow along the walkways. Crisp geometry, sharp focus across the entire frame, 8K production render, Octane / V-Ray look, idealised digital-twin aesthetic, neutral white-grey environment, no people, no text, no logos, 16:9.
```

**Keys:** "shown floating where the ceiling is cut away" prevents Gemini re-drawing a ceiling for the overhead services.

Variants:

- **Plan view** — `straight orthographic top-down, equipment colour-coded by system, like a live BMS floor plan`
- **Dark ops** — `room in darkness, status LEDs, VSD displays and cyan walkway lighting as the only illumination`

## 6. Exploded systems view

The digital-twin money shot — glowing colour-coded system loops over the cutaway plant.

```
Ultra high-quality 3D architectural visualisation render of a complete commercial HVAC chiller plant room, isometric cutaway bird's-eye view from above at a 30-degree angle, roof and walls fully removed to expose the entire plant layout in a single frame, presented as an idealised digital-twin systems diagram brought to life.

EQUIPMENT LAYOUT — along the left wall, a continuous lineup of grey electrical switchboards and motor control centre cabinets with red and green indicator LEDs and small glowing VSD digital displays. Down the centre aisle, four end-suction centrifugal pumps mounted on raised concrete inertia bases, each with a grey electric motor, red flexible coupling, suction guide and check valve, paired with pressure gauges on chrome pigtails. On the right side, two large pale-green water-cooled centrifugal chillers, each with a visible centrifugal compressor on top, cylindrical evaporator and condenser barrels below, dished marine water boxes with bolted flanges on the ends, and a unit-mounted control panel. Silver-jacketed insulated pipework with blue and green painted flanged valve assemblies, butterfly valves with gear operators, Y-strainers and binder test points connects everything; large-diameter headers run at high level on blue and green structural steel supports, with red fire services pipework and galvanised cable trays floating where the ceiling has been cut away. Sealed light-grey concrete floor with yellow safety walkway line markings, floor drains and housekeeping pads under every item of plant.

SYSTEM FLOW VISUALISATION — overlaid on the physical model, render each hydraulic and electrical system as a softly glowing volumetric flow path travelling through its actual pipework and cabling: the CHILLED WATER LOOP in luminous cool blue, flowing from the chiller evaporator barrels through the supply header, with subtle animated-style streaks and a gentle outer glow, returning via the return header through the pumps and back into the evaporators; the CONDENSER WATER LOOP in luminous emerald green, flowing from the condenser barrels out toward a cutaway edge where it exits to cooling towers implied off-frame, and returning; the ELECTRICAL DISTRIBUTION in luminous cyan, tracing thin bright energy lines from the switchboards along the cable trays down to every pump motor, chiller panel and VSD; the REFRIGERANT CIRCUIT inside each chiller hinted as a faint warm amber glow between compressor, condenser and evaporator. Flow direction shown by the taper and motion-blur of the glowing streams, brighter at the source, never as arrows or text. The glowing systems pass through translucent sections of pipe insulation, as if the pipework becomes 30% transparent only where the flow is visible, revealing the water moving inside.

LIGHTING AND GRADE — the physical room rendered in a clean, slightly darkened neutral grey-white studio environment so the glowing systems carry the image: soft overhead ambient illumination at dusk-level intensity, gentle ambient occlusion in pipe junctions and under equipment, the cyan, blue and green system glows casting soft coloured light onto nearby surfaces and reflecting subtly in the lightly polished concrete floor. Equipment status LEDs and VSD displays lit.

RENDER QUALITY — fully ray-traced global illumination with volumetric light scattering on the glow paths, completely denoised, zero grain, zero noise, perfect anti-aliasing, physically based materials with crisp specular highlights on jacketed insulation and painted steel, sharp focus across the entire frame, no depth-of-field blur, no film grain, no chromatic aberration, 8K production render, Octane / V-Ray quality, crisp clean geometry, no people, no text, no labels, no arrows, no logos, no watermarks, 16:9.
```

**Deliberate choices:** arrows and text banned TWICE (Gemini loves labelled diagrams); 30% selective transparency = x-ray, not ghost; dusk-level room so the glows pop without going full night mode; refrigerant as faint amber gives the chillers internal life without competing; the colour map is real pipe ID convention plus cyan for electrical so the brand owns the power story.

## 7. 2D floor plan → 3D floor plan

Attach the plan. A PNG screenshot at full zoom beats an embedded PDF; one floor level per generation.

```
Convert this 2D architectural floor plan into a stunning ultra high-quality 3D floor plan visualisation, isometric cutaway view from above at a 30-degree angle, walls extruded to approximately 1.2 metre doghouse height so every room interior remains fully visible from this aerial view.

FIDELITY — this is the critical rule: reproduce the floor plan EXACTLY as drawn. Preserve the precise wall positions, room proportions, door swings and openings, window locations, corridor widths, stair and lift core positions, and overall building footprint from the source drawing. Do not add rooms, remove walls, change the layout, or reinterpret the plan. Every room in the source must appear in the render in the same position and at the same relative scale. Read the room labels on the plan and furnish each space according to its labelled function.

PRESENTATION — render as premium architectural visualisation: extruded walls in clean matte white with a subtle crisp top edge, floor finishes differentiated by zone — warm timber or carpet in occupied spaces, large-format grey tile in lobbies and corridors, sealed concrete in plant and back-of-house areas, tile in wet areas. Furnish realistically and sparingly to communicate function, in a restrained modern palette of whites, light timber, charcoal and soft grey, with subtle plants for life. Doors shown open at their hinge positions, glazing rendered as thin transparent panes with light frames.

LIGHTING AND QUALITY — soft studio daylight from above-left, gentle shadows grounding every wall and furniture piece, soft ambient occlusion in corners, lightly reflective floors. Fully ray-traced global illumination, completely denoised, zero grain, zero noise, perfect anti-aliasing, physically based materials, sharp focus across the entire frame, 8K production render, Octane / V-Ray archviz quality, clean white-grey background with a soft contact shadow under the building slab, no people, no text, no labels, no dimensions, no logos, no watermarks, 16:9.
```

Anti-drift escalation — prepend if Gemini "improves" the plan:

```
This is a technical conversion task, not a creative one — geometric accuracy to the source drawing takes priority over aesthetics.
```

Variants:

- **Top-down** — `straight orthographic top-down view with walls extruded, like a dollhouse plan viewed from directly above` (easiest fidelity)
- **Plant / BMS version** — swap the furnishing language for plant room equipment language (template 5), plus the glowing loops (template 6)
- **Dark twin** — `darkened render, rooms softly illuminated from within, cyan accent lighting tracing the corridors`
