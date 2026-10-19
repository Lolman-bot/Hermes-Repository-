# Cinematic Video

Production-grade Veo prompts for Bitpool cinematic marketing video — building assembly and stacking sequences, plant room self-assembly, digital-twin fly-throughs.

> **Note**
> Read [Visual Language & Standard Blocks](visual-language.md) first. If the task turns out to be a still rather than a video, use Cinematic Photo (see the `/bitpool-cinematic-photo` skill) instead.
>
> If the user also wants to **see** the sequence — "mock it up", "show me the pacing", "an HTML version" — read [HTML Output](html-output.md). The video mockup is an 8-second CSS keyframe animation whose timings must match this page's timestamped beats exactly; that page carries the beat→percentage mapping for both templates below.


## Prompt architecture

```
[FORMAT LINE]        — medium, duration, style anchor, quality anchor
[FIDELITY / LAYOUT]  — what must be preserved exactly (itemised inventory)
[SCENE / SEQUENCE]   — timestamped beats
[CAMERA]             — one continuous move, start/end framing
[LIGHTING & GRADE]
[QUALITY BLOCK]      — the video quality closer
```

## Video prompt rules

> **Warning**
> **8 seconds is the sweet spot.** Veo holds temporal stability there; at 15+ seconds facade grids start swimming. For longer choreography, split into multiple 8-second generations with a continuous camera instruction so the cuts hide.


- **Timestamped beats** — OPENING (0.0–0.5s) → main sequence → FINAL BEAT with a 1.5s locked hero still, `frame-matched to the reference image for a seamless cut to the end card`.
- **One continuous camera move** — orbital drift, `velvet-smooth, no handheld shake, no drone wobble — a perfect virtual camera on rails`. State start and end framing explicitly; the end framing equals the reference image framing when one exists.
- **Mass and rhythm** — heavy items descend slow, small items land quick (`like keys being pressed in order`). Tempo accelerates through the sequence. Every landing gets: gentle deceleration, a 2-centimetre settle, and a soft cyan pulse at the contact line.
- **Anti-morph clause** — always include for assembly sequences: `each module is rigid, complete and fully finished from the moment it appears — no bare structure, no scaffolding, no morphing, no deformation.`
- **Pipework GROWS, never drops** — telescoping extension with valves snapping on as the runs pass. Falling pipes read wrong; growth reads as connection, which is the Bitpool story.
- **Real install order sells it** — pads → major plant → pumps → switchboards (LEDs flicker awake on seating) → pipework growth → overhead services → full cyan wake-up wave. Audiences who have commissioned plant rooms feel the correctness subconsciously.
- **CGI, not footage** — for the rendered look, state `rendered entirely as premium CGI, not drone footage`, and quiet the context (`surrounding city as simplified light-grey massing models`) so the hero owns the frame.
- **Sound-feel line helps pacing** — `suited to a confident bass-pulse soundtrack with a soft impact accent on each landing.`
- **Reverse variant** — disassembly (plates lifting away to reveal interiors) reads as "Bitpool peels your building open", and reversed motion is often more temporally stable.

## Fidelity paragraphs (image-to-video)

When a reference image is attached, itemise every feature to preserve — the model keeps what you name and redesigns what you don't.

```
FIDELITY — preserve the building's exact architecture, proportions and camera
angle: [itemised list of every distinctive feature]. Do not redesign, simplify
or modernise. Rebuild this exact structure as clean CGI geometry.
```

---

# Proven templates

## 1. Building stacking assembly

8-second Veo. The building assembles itself floor by floor from finished plates.

Lessons baked in from the v1 review: plates must be FINISHED modules (v1 produced bare concrete frames), the final building must KEEP the exposed floor (v1 sealed it), and the whole scene must be declared CGI (v1 read as drone footage).

```
Cinematic 8-second ultra high-end 3D architectural visualisation video of this exact building assembling itself floor by floor — rendered entirely as premium CGI, not drone footage: the full scene, city and building rebuilt as pristine archviz geometry, Octane / V-Ray / Unreal Engine 5 path-traced quality.

RENDER LOOK — fully ray-traced global illumination, completely denoised, zero grain, zero noise, zero flicker, temporally stable across every frame. Physically based materials with micro-detail: individually modelled curtain-wall panels, crisp aluminium mullion profiles, realistic moving sky reflections during the orbit. The surrounding city rendered as quiet stylised CGI context — simplified light-grey massing models, refined archviz trees, clean asphalt — so the fully detailed hero owns the frame.

OPENING (0.0–0.5s) — bright morning light, the corner site empty except the building's footprint slab, its edge traced by a thin glowing cyan line pulsing once.

ASSEMBLY (0.5–6.0s) — fully FINISHED floor plates descend and stack bottom-up in the exact massing of the reference: wider podium, cantilevered mid-section stepping outward, upper tower stepping back, grey rooftop plant screen last. Critical rule: every plate is a complete, sealed, fully clad module from the moment it appears — facade glass installed, interior fit-out finished, rigid and unchanging during descent, no bare concrete structure, no scaffolding, no morphing. Interiors visible through the glass during descent: furnished open-plan offices, glass meeting rooms, warm light. Each plate decelerates, seats with a 2-centimetre settle and a soft cyan pulse tracing the junction line, then the pulse fades. Stacking rhythm accelerates gently floor by floor.

CAMERA — one continuous slow orbital move from the reference image's elevated three-quarter aerial angle, sweeping ~25 degrees while craning up with the rising stack, then easing back to settle on exactly the reference image's final framing. Velvet-smooth, no handheld shake, no drone wobble — a perfect virtual camera on rails.

FINAL BEAT (6.0–8.0s) — the building stands complete, matched to the reference: one mid-level floor remains OPEN and EXPOSED, its glass held transparent, revealing the furnished interior like a living cutaway — while the corner meeting rooms glow warm amber with silhouetted people. A final slow cyan pulse travels up the full facade, floor junction by junction, and fades. Camera locks to a 1.5-second hero still, frame-matched to the reference image for a seamless cut to the end card.

GRADE AND FEEL — editorial real-estate film grade: clean whites, deep glass tones, warm amber interiors the only warm note, subtle horizon haze. Every plate moves with believable mass — weighty, engineered, satisfying. Pacing suited to a confident bass-pulse soundtrack with a soft impact accent per landing.

QUALITY — 4K, 16:9, sharp focus across the entire frame, no motion blur smearing on the facade grid, no warping geometry, no flickering windows, no text, no labels, no logos, no watermarks.
```

Anti-morph escalation:

```
each floor plate is rigid and unchanging during its descent — no morphing, no deformation, treat each plate as a solid prefabricated module
```

**Reverse variant** — disassembly is often MORE temporally stable, and reads as "Bitpool peels your building open".

## 2. Plant room self-assembly

8-second Veo, reference = the isometric cutaway plant room render. The real install order is the marketing magic.

```
Cinematic 8-second ultra high-end 3D architectural visualisation video of this exact chiller plant room assembling itself piece by piece — rendered entirely as premium CGI in pristine archviz quality, Octane / V-Ray / Unreal Engine 5 path-traced look. The final frame must match the reference image exactly: same isometric cutaway bird's-eye angle, same equipment, same positions.

OPENING (0.0–0.5s) — clean white studio void. The bare concrete floor slab fades in alone in the cutaway style: sealed grey concrete, floor drains, yellow safety walkway lines drawing themselves on in a quick animated sweep. The two cutaway walls rise from the slab edges and lock in. A thin cyan line pulses once around the slab perimeter.

ASSEMBLY (0.5–6.5s) — the plant installs itself in believable construction order, every item descending as a complete, finished, rigid module that settles with engineered precision — gentle deceleration, 2-centimetre settle, soft cyan pulse at its base on landing:
1. Concrete housekeeping pads and inertia bases drop in across the floor.
2. The two pale-green water-cooled centrifugal chillers descend onto their pads — compressors, barrels and water boxes complete — landing one beat apart.
3. The grey standalone compressor unit lowers onto its plinth.
4. The centrifugal pumps arrive as a rapid rhythmic series down the centre aisle, each pump-and-motor set with red flexible coupling landing in quick succession, like keys being pressed in order.
5. The full switchboard and MCC lineup slides in along the wall as one connected row, docking; indicator LEDs and VSD displays flicker awake the instant they seat.
6. The silver-jacketed insulated pipework GROWS through the room — pipes extending and elbowing from chillers and pumps with smooth telescoping motion, blue and green flanged valves snapping on as the runs pass, headers rising onto blue and green structural steel frames which rise just ahead of the pipes they carry.
7. High-level services sweep in last: cable trays and red fire services pipework assembling overhead in fast clean segments where the ceiling is cut away.

FINAL BEAT (6.5–8.0s) — the last overhead segment clicks in. The plant comes alive in one wave: soft cyan glow washing the yellow walkways and under equipment, status LEDs lit, VSD displays glowing — matching the reference image's lighting state. The camera — one continuous velvet-smooth drift, starting slightly lower and closer, gently rising and pulling back throughout — settles into the exact reference framing and locks for a 1.5-second hero still.

MOTION CHARACTER — believable mass and engineered intent: heavy items descend slower, small items land quick and crisp. No floating, no bouncing, no morphing — each module rigid and finished from first frame. Pipework growth smooth and continuous, never snake-like.

RENDER QUALITY — [standard video quality block], soft studio lighting, gentle ambient occlusion under every item as it lands, clean white studio backdrop, no people, no text, no labels, no logos, no watermarks, 4K, 16:9.
```

If Veo fumbles seven steps in one shot: split steps 1–4 and 5–7-plus-finale into two 8-second generations; the continuous camera instruction hides the cut.

## Still-image templates

The office tower, plant room, data centre, photo→render, cutaway, exploded systems and floor plan→3D templates all live on Cinematic Photo (see the `/bitpool-cinematic-photo` skill) — a video brief usually needs one of them as the reference frame the video is built toward.
