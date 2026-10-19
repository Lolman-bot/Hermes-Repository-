# Canonical Layouts — the Four Reference Pages

These are the proven compositions. Pick the closest one, then adapt. All use the
**1280 × 700** viewBox (AHU uses 1240 × 600), the shell from `assets/shell.html`, glyphs
from [Glyph Library](hvac-glyph-library.md), and the JS pattern from [Live Data Model](hvac-live-data-model.md).

---

## A. Air Handling Unit (AHU) — single-line ducted
Air path drawn as a **channel** (`.duct-border` + `.duct-fill`), supply left→right on top,
return right→left on the bottom, feeding a conditioned space on the right.

**Layout (viewBox 0 0 1240 600), supply centreline y=110, return y=470:**
- Far left: outdoor-air damper (top) + exhaust/relief damper (bottom), each with an intake/discharge chevron cap.
- Vertical **return-air damper riser** at x≈250 joining return (bottom) to the mixing point (top).
- Top run, left→right: mixing point → **heating coil** (orange `+`) → **cooling coil** (blue `−`) → **supply fan** (scroll) → discharge → elbow down into the conditioned space.
- Return fan on the bottom run.
- Conditioned space: `spaceGrad` box on the right, supply enters top / return leaves bottom.

**Extra CSS this page needs** (add to the shell `<style>` if not present):
```css
.duct-border { fill:none; stroke:var(--hair-strong); stroke-width:42; stroke-linejoin:round; stroke-linecap:round; }
.duct-fill   { fill:none; stroke:var(--bg);          stroke-width:38; stroke-linejoin:round; stroke-linecap:round; }
.coil-sym { font-family:var(--sans); font-size:24px; font-weight:700; fill:#fff; }
.space-label { font-family:var(--sans); font-weight:500; font-size:14px; fill:var(--ink-70); }
.blade { stroke:var(--ink); stroke-width:3.4; stroke-linecap:round; transition:transform .7s cubic-bezier(.2,.8,.2,1); }
```
**Supply scroll fan** (larger than a pump):
```html
<g id="g_sf">
  <path class="housing" d="M700,75 a35,35 0 1 0 28,57 l24,0 l0,-22 l-18,0 a35,35 0 0 0 -34,-35 z"/>
  <g class="fan-spin" id="sfBlades" style="transform-box:fill-box;transform-origin:center;">
    <circle cx="700" cy="110" r="22" fill="none" stroke="var(--accent)" stroke-width="2" opacity="0.6"/>
    <line x1="700" y1="110" x2="700" y2="88" stroke="var(--accent)" stroke-width="2.4"/>
    <line x1="700" y1="110" x2="719" y2="121" stroke="var(--accent)" stroke-width="2.4"/>
    <line x1="700" y1="110" x2="681" y2="121" stroke="var(--accent)" stroke-width="2.4"/>
    <circle cx="700" cy="110" r="5" fill="var(--ink-50)"/>
  </g>
</g>
```
**Strip**: Unit Mode · Space Temp · Supply Air Temp · Duct Static · Active Alarms.
**Commands**: Occupancy (Occupied/Unoccupied) · Control (Auto/Manual) · Supply fan (Start/Stop) · Economiser (Enabled/Disabled).
**Points**: OAT, MAT, SAT, RAT, ZONE, CO₂, STAT, SF/RF speed, HW/CHW valve, OA/RA/EA damper.

---

## B. Chilled Water Plant (CHW) — primary/secondary, variable flow
Blue **CHWS** header on top, red **CHWR** header on the bottom, both full width.

**Layout (viewBox 0 0 1280 680), supply y=72, return y=600:**
- **Left:** 3 chillers (centres 170/360/550, box y 180–300). Each: supply riser up through
  flow meter (F) + check valve to the top header; return riser down through an isolation valve;
  a DP-sensor chip across the evaporator; a per-chiller status/temp/load chip below.
- **Primary pumps** (VSD) on each chiller's return riser at y≈470.
- **Hydraulic decoupler** (grey box) at x≈700 bridging the two headers, with a return-temp sensor.
- **Right:** 3 secondary loads (centres 860/1020/1180) — supply branch down through a balancing
  valve to an AHU-coil block, then a **2-way control valve** + branch DP, returning to the bottom header.
- Plant supply-temp sensor + plant flow meter on the top header; return-temp sensor on the bottom header.

**Strip**: Plant Mode · CHWS · CHWR · Plant ΔT · Plant Flow · Active Alarms.
**Commands**: Plant (Enable/Disable) · Sequencing (Auto/Manual) · Chillers staged (1/2/3) · CHWS setpoint (6.0/6.7).
**Alarms**: chillers staged, lead pump proven, CHWS low-limit, header DP control, flow proven, low-ΔT syndrome.

---

## C. Cooling Tower / Condenser Water Plant (CT)
Red **CWR** (warm, to towers) header on top, blue **CWS** (cooled, to condensers) header on the bottom.

**Layout (viewBox 0 0 1280 700), CWR y=80, CWS y=624:**
- **Left:** 3 induced-draft towers (centres 170/360/550, body y 176–336). Each: cyan exhaust
  **plume** above a spinning fan on a deck; **fill** louvers; a blue **basin** with a make-up valve;
  hot inlet riser from the CWR header; basin-outlet riser to the CWS header through an isolation valve.
- **VSD condenser-water pumps** (centres 170/360/550) drawing from the bottom header.
- **Right:** "Chiller Condensers" block (the heat source) — cold supply in at the bottom,
  warm return out at the top to the CWR header.
- **Sensors**: ambient wet-bulb (WB), CW supply & return temps, condenser flow meter,
  per-tower fan-speed/basin-temp/level/make-up, and a conductivity (C) + automatic bleed point.

**Strip**: Plant Mode · CW Supply · CW Return · Range (CWR−CWS) · Approach (CWS−WB) · Active Alarms.
**Commands**: Plant (Enable/Disable) · Sequencing (Auto/Manual) · Towers staged (1/2/3) · CW supply SP (29/27).
**CSS this page adds**: `.tower`, `.deck`, `.fill-line`, `.basin`, `.plume` (all already in the shell style).

---

## D. Central Plant Overview (index.html) — the dashboard that links them
A landing page that ties the three graphics together and cross-navigates.

**Composition:**
- Shared **nav-links** bar (Overview · Cooling Towers · Chilled Water · Air Handling), `active` on the current page.
  Add the same bar to every subpage so navigation works both ways.
- **Roll-up KPI strip**: plant status, cooling load (MW), plant power (kW), efficiency (kW/ton), CHW ΔT, alarms.
- **Heat-flow chain** (viewBox 0 0 1200 320): four nodes — Cooling Towers → Chiller Plant →
  Air Handling → Conditioned Space — connected by labelled supply/return legs carrying live temps,
  each animated with `.flowm`. Wrap the first three nodes in `<a href="...graphic.html">` so they link.
- **Three plant cards** (`.card`, a hover-lift link) each with 4 live KPIs and an "Open live graphic →" link.
- **Plant alarm roll-up** tagged by source (CT-01 / CHW-01 / AHU-01).

**To wire a set together:** keep all files in one folder. Inject the nav-links block right after
the `.lockup` anchor on each page, and add the matching `.nav-links` CSS. The overview's own
`model()` is independent mock — when you go live, point all pages at one feed so the chain temps agree.

---

## Composition checklist (every page)
1. Start from `assets/shell.html`; fill the header/strip/title placeholders.
2. Build the schematic in drawing order (the Glyph Library, §1).
3. Give every live value a stable chip `id`; wire it in `paint()`.
4. Add 4 segmented commands that actually change the picture (staging, enable, setpoint, mode).
5. Write `model()` so off-equipment greys out and flow stops; alarms only fire on real faults.
6. Add a `.legend` describing the colours used.
7. `python scripts/build.py inject page.html` then `… render page.html` and eyeball it.
8. Confirm: cube logo in nav + footer, Inter only, cyan accent, hairlines, light theme,
   functional blue/red (+orange/green/amber/red states) — nothing else.
