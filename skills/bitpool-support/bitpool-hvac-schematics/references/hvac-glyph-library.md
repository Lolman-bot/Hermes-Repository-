# Glyph Library — SVG Components for HVAC Schematics

Copy these into the `<svg viewBox="0 0 1280 700">` in the shell. They depend on the
CSS primitive classes already defined in `assets/shell.html` (`.pipe-s`, `.pipe-r`,
`.flow`, `.tower`, `.basin`, `.glyph`, `.sens`, `.chip`, etc.). Coordinates use a
**1280 × 700 viewBox** so everything scales together.

## Contents
1. Drawing order (read first)
2. Colour convention
3. Pipes, ducts & flow
4. Sensors (flow / temp / DP / generic)
5. Valves (isolation/2-way, check, balancing/make-up)
6. Pumps (centrifugal, VSD)
7. Fans (axial/scroll, with plume)
8. Coils (heating / cooling)
9. Chillers
10. Cooling towers (body + fill + basin)
11. Conditioned space & decoupler/buffer
12. Data chips
13. Side-rail markup (commands / points / alarms)

---

## 1. Drawing order
SVG paints in document order. Always layer in this sequence so nothing is hidden wrongly:
1. **Headers / ducts** (`.pipe-s` / `.pipe-r` borders, or `.duct-border` then `.duct-fill`)
2. **Flow overlays** (`.flow` — white marching dashes that sit *inside* the coloured pipe)
3. **Equipment** (chillers, towers, coils, fans, pumps, valves)
4. **Sensor nodes + leader lines** (`.sens`, `.lead`)
5. **Data chips** (`.chip`) — always last so they sit on top and stay legible.

## 2. Colour convention (functional — the one allowed departure from cyan-only)
- `--cws` / supply-blue `#1E74C8` = **cold/supply** water (CHWS, CW supply).
- `--cwr` / return-red `#D9534F` = **warm/return** water (CHWR, CW return).
- `--heat` `#E8843A` (orange) = heating coil; `--cool` `#2BA6E0` = cooling coil.
- `--bal` `#E8843A` = balancing / make-up / bleed valves.
- `--accent` `#00ADEF` (brand cyan) is reserved for **sensors, flow, valve-open fill, fan blades, accents** — never for a pipe.
- State dots: `--ok` green (running/normal), `--warn` amber, `--alarm` red (pulses), `--off` grey.
Always add a `.legend` row explaining the colours actually used on that page.

## 3. Pipes, ducts & flow

**Water pipe** (single bold coloured stroke). Supply blue / return red:
```html
<path class="pipe-s" d="M70,72 H1240"/>      <!-- supply header -->
<path class="pipe-r" d="M70,600 H1240"/>     <!-- return header -->
<!-- white marching-dash flow overlay, SAME path. fwd = along path dir, rev = against -->
<path class="flow fwd" id="fl_s" d="M70,72 H1240"/>
<path class="flow rev" id="fl_r" d="M1240,600 H70"/>
```

**Air duct** (channel with hairline walls — used on AHU pages). Draw border then fill, same `d`:
```html
<path class="duct-border" d="M40,110 H1000 V200 H1030"/>
<path class="duct-fill"   d="M40,110 H1000 V200 H1030"/>
<path class="flow fwd" id="f_sup" d="M40,110 H1000 V200 H1030"/>
```
> If `.duct-border`/`.duct-fill` aren't in your CSS, add them (see AHU example in [Canonical Layouts](hvac-canonical-layouts.md)).

**Stopping flow** (pump/fan off): toggle the `stopped` class in JS — `el.classList.toggle('stopped', !running)`. `.flow.stopped` fades to 0; fans get `.fan-spin.stopped`.

**Direction chevron** (static arrowhead, optional):
```html
<path d="M1052,64 l11,8 l-11,8 z" fill="var(--cws)" opacity="0.6"/>
```

## 4. Sensors
A small circle + a one/two-letter code, with a dashed `.lead` to a data chip.
```html
<!-- temperature -->
<circle class="sens" cx="940" cy="72" r="12"/><text x="940" y="76" class="sens-t">T</text>
<!-- flow meter (F), DP (ΔP), conductivity (C), wet-bulb (WB), level (L) — same shape, change the letter -->
<line class="lead" x1="940" y1="60" x2="940" y2="36"/>   <!-- leader to chip -->
```
A **plant flow meter** is often drawn as an inline orange block instead:
```html
<rect class="bal" x="990" y="60" width="40" height="24" rx="3"/>
<text x="1010" y="76" class="sens-t" fill="#fff" font-size="9">F</text>
```

## 5. Valves
**Isolation / 2-way control valve** (bowtie). Two triangles apex-to-apex. Add `valve-open`
(cyan fill) or `valve-shut` (grey) and toggle in JS. For a *control* valve add an actuator box on top.
```html
<g id="v1">
  <path class="glyph valve-open" d="M158,338 L170,350 L158,362 Z"/>
  <path class="glyph valve-open" d="M182,338 L170,350 L182,362 Z"/>
  <!-- control-valve actuator (omit for plain isolation): -->
  <rect class="glyph" x="162" y="320" width="16" height="12" rx="2"/>
  <line x1="170" y1="332" x2="170" y2="338" stroke="var(--ink-50)" stroke-width="1.4"/>
</g>
<!-- JS: document.querySelectorAll('#v1 path').forEach(e=>{e.classList.toggle('valve-open',open);e.classList.toggle('valve-shut',!open);}); -->
```
**Check valve** (triangle in flow direction + bar). For upward flow:
```html
<path class="check" d="M158,158 L170,142 L182,158 Z"/>
<line x1="156" y1="140" x2="184" y2="140" stroke="var(--ink-50)" stroke-width="1.6"/>
```
**Balancing / make-up / bleed valve** (small orange wedge):
```html
<path class="bal" d="M104,320 l10,-6 l0,12 z"/>
<line x1="98" y1="320" x2="104" y2="320" stroke="var(--cws)" stroke-width="2.4"/>
```

## 6. Pump (centrifugal, VSD)
Circle + triangle (impeller) pointing in discharge direction + a VSD box. Triangle fill = status.
```html
<g id="p1">
  <circle class="glyph" cx="170" cy="470" r="22"/>
  <path id="p1tri" d="M170,455 L156,479 L184,479 Z" fill="var(--ok)" stroke="var(--ink-50)" stroke-width="1"/>
  <rect class="glyph" x="196" y="456" width="26" height="34" rx="3"/>
  <rect x="203" y="470" width="12" height="8" fill="var(--ink-30)"/>
  <text x="209" y="504" class="comp-sub">VSD</text>
  <text x="170" y="510" class="comp-sub">P-01</text>
</g>
<!-- JS: $('p1tri').setAttribute('fill', run?'var(--ok)':'var(--off)'); -->
```
Point the impeller triangle the way water leaves the pump (up / left / right).

## 7. Fan (axial or tower fan, with exhaust plume)
Spinning blade group + optional cyan dashed plume. Use `transform-box:fill-box;transform-origin:center;`
so the blades spin about their own centre.
```html
<!-- exhaust plume (towers): vertical dashed cyan, animates upward -->
<path class="plume rev ct1p" d="M170,150 V88"/>
<!-- fan deck + spinning blades -->
<circle class="glyph" cx="170" cy="167" r="13"/>
<g class="fan-spin" id="ct1fan" style="transform-box:fill-box;transform-origin:center;">
  <line x1="170" y1="167" x2="170" y2="156" stroke="var(--accent)" stroke-width="2.2"/>
  <line x1="170" y1="167" x2="180" y2="173" stroke="var(--accent)" stroke-width="2.2"/>
  <line x1="170" y1="167" x2="160" y2="173" stroke="var(--accent)" stroke-width="2.2"/>
  <circle cx="170" cy="167" r="3.2" fill="var(--ink-50)"/>
</g>
<!-- JS: $('ct1fan').classList.toggle('stopped',!run); plume: querySelectorAll('.ct1p').forEach(e=>e.classList.toggle('stopped',!run)); -->
```
A **supply-air fan** (AHU) is the same idea drawn larger with a scroll housing — see [Canonical Layouts](hvac-canonical-layouts.md).

## 8. Coils (heating / cooling)
Filled gradient block with a `+` (heat) or `−` (cool). Define gradients in `<defs>`:
```html
<defs>
  <linearGradient id="heatGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F0A05A"/><stop offset="1" stop-color="#E2682F"/></linearGradient>
  <linearGradient id="coolGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4FC0EF"/><stop offset="1" stop-color="#1B7FC0"/></linearGradient>
</defs>
<rect x="418" y="80" width="34" height="60" rx="3" fill="url(#heatGrad)" stroke="rgba(0,0,0,0.12)"/>
<text x="435" y="119" class="coil-sym" text-anchor="middle">+</text>     <!-- heating -->
<rect x="504" y="80" width="34" height="60" rx="3" fill="url(#coolGrad)" stroke="rgba(0,0,0,0.12)"/>
<text x="521" y="118" class="coil-sym" text-anchor="middle">&#8722;</text> <!-- cooling -->
```

## 9. Chiller
Soft-blue box with label + tag. Add `.off` class when not running (greys out).
```html
<rect class="chiller" x="120" y="180" width="100" height="120" rx="6" id="ch1box"/>
<text x="170" y="232" class="chiller-lbl" text-anchor="middle" id="ch1lbl">CHILLER</text>
<text x="170" y="250" class="tag" text-anchor="middle">CH-01</text>
<!-- evaporator supply riser up to header, with flow meter + check valve (see §4/§5) -->
<!-- JS: $('ch1box').classList.toggle('off',!run); -->
```

## 10. Cooling tower
Body + fan deck (§7) + fill louvers + basin. `.basin` is a small blue tank; add `.off` when idle.
```html
<rect class="tower" x="115" y="176" width="110" height="160" rx="6" id="ct1box"/>
<rect class="deck" x="140" y="158" width="60" height="18" rx="3"/>            <!-- fan deck -->
<line class="fill-line" x1="128" y1="212" x2="212" y2="212"/>                  <!-- fill louvers -->
<line class="fill-line" x1="128" y1="230" x2="212" y2="230"/>
<line class="fill-line" x1="128" y1="248" x2="212" y2="248"/>
<rect class="basin" x="120" y="308" width="100" height="24" rx="2" id="ct1bsn"/>
<!-- hot inlet riser from CWR header (down into body), basin outlet riser to CWS header (§3) -->
```

## 11. Conditioned space & decoupler
**Conditioned space** (AHU pages) — gradient box, warm top → cool bottom:
```html
<defs><linearGradient id="spaceGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F7E0CB"/><stop offset="0.5" stop-color="#EAE6E2"/><stop offset="1" stop-color="#CBE6F4"/></linearGradient></defs>
<rect x="1030" y="150" width="180" height="320" rx="8" fill="url(#spaceGrad)" stroke="var(--hair-strong)" stroke-width="1.4"/>
<text x="1120" y="305" class="space-label" text-anchor="middle">CONDITIONED</text>
```
**Hydraulic decoupler / buffer tank** (CHW pages) — grey vertical box bridging supply & return:
```html
<path class="pipe-s" d="M700,72 V330"/><path class="pipe-r" d="M700,470 V600"/>
<rect x="678" y="330" width="44" height="140" rx="5" fill="#c3ccd6" stroke="var(--ink-50)" stroke-width="1.2"/>
```

## 12. Data chip
The little white rounded label that carries a live value. Always last in the SVG. Structure:
code (mono, ink-50) on top, big mono value + small unit below. Give the value an `id` so `paint()` writes to it.
```html
<g transform="translate(900,8)">
  <rect class="chip" width="92" height="28" rx="5"/>
  <text x="7" y="12" class="chip-code">CHWS · SUPPLY T</text>
  <text x="7" y="24" class="chip-val" id="c_chws">6.5</text><text x="36" y="24" class="chip-u">°C</text>
</g>
```
Multi-field chips (status dot + two metrics) — see the chiller/tower chips in [Canonical Layouts](hvac-canonical-layouts.md).

## 13. Side-rail markup
**Command (segmented control):**
```html
<div class="ctl"><span class="name">Chillers staged</span>
  <span class="seg" id="seg_stage"><button data-v="1">1</button><button data-v="2" class="on">2</button><button data-v="3">3</button></span></div>
```
**Live points** and **alarms** are rendered from JS into `#ptList` and `#almList` — see
[Live Data Model](hvac-live-data-model.md) for the exact `paint()` builders.
