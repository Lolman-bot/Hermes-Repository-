# Bitpool tokens — dark & light

The Bitpool brand ships in **two themes**. Both share one accent (`#00ADEF`), one font (Inter), and one emphasis move (bold cyan replaces italics). They differ only in surfaces and ink.

- **Dark** is the default for marketing surfaces, pitch material, strategic directives, and the public site — deep near-black with photographic/atmospheric moments.
- **Light** is the default for **documents, reports, debriefs, dashboards, and anything that will be read closely or printed** — white paper, near-black ink. (This matches the Bitpool PDF report convention.)

Pick the theme that fits the surface, then build. Never mix the two palettes in one artifact.

---

## Dark theme tokens

```css
:root,
[data-theme="dark"] {
  /* Surfaces */
  --bg: #0b1218;            /* primary background */
  --bg-2: #111b23;          /* hover / elevated card surface */
  --bg-3: #0a1218;          /* deepest panel (atmospheric beats) */
  --navy: #1B2732;          /* deep navy from logo */

  /* Ink */
  --ink: #eef2f6;           /* primary text */
  --ink-70: #aab6c2;        /* secondary text */
  --ink-50: #6e7c8b;        /* tertiary, eyebrows, captions */
  --ink-30: #394652;        /* nearly invisible, framing only */
  --text-strong: #ffffff;   /* pure-white headline ink */

  /* Accent — sacred, identical in both themes */
  --accent: #00ADEF;        /* THE Bitpool cyan */
  --accent-soft: #5cd0ff;   /* very rare, lighter accent */
  --accent-deep: #007db0;   /* very rare, deeper accent */

  /* Borders — hairlines only, never solid */
  --hair: rgba(255,255,255,0.08);
  --hair-strong: rgba(255,255,255,0.14);

  /* Pattern (see "The default background" below) */
  --grid-line: rgba(255,255,255,0.045);
  --grid-line-major: rgba(255,255,255,0.09);
  --glow-1: rgba(0,173,239,0.15);
  --glow-2: rgba(0,173,239,0.10);
  --beat-grade: linear-gradient(135deg, #1B2732 0%, #0a1218 55%, #0b1218 100%);

  --logo-filter: none;      /* logo PNG already reads on dark */

  /* Scrollbars (see "Scrollbars & favicon" below) */
  --scroll-thumb: rgba(255,255,255,0.14);
  --scroll-thumb-hover: rgba(0,173,239,0.55);

  --sans: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --mono: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
}
```

## Light theme tokens

```css
[data-theme="light"] {
  /* Surfaces */
  --bg: #ffffff;            /* paper */
  --bg-2: #f6f8fa;          /* hover / elevated card surface */
  --bg-3: #eef2f6;          /* cool cloud-grey panel (atmospheric beats) */
  --navy: #1B2732;          /* navy stays — used as ink, badges, accents */

  /* Ink */
  --ink: #1B2732;           /* primary body ink (brand navy, not pure black) */
  --ink-70: #44525f;        /* secondary text */
  --ink-50: #6e7c8b;        /* tertiary, eyebrows, captions */
  --ink-30: #aab6c2;        /* framing only */
  --text-strong: #0b1218;   /* near-black headline ink */

  /* Accent — sacred, identical in both themes */
  --accent: #00ADEF;
  --accent-soft: #5cd0ff;
  --accent-deep: #007db0;

  /* Borders — dark hairlines on paper */
  --hair: rgba(11,24,32,0.08);
  --hair-strong: rgba(11,24,32,0.14);

  /* Pattern (see "The default background" below) */
  --grid-line: rgba(11,24,32,0.06);
  --grid-line-major: rgba(11,24,32,0.11);
  --glow-1: rgba(0,173,239,0.30);
  --glow-2: rgba(0,173,239,0.17);
  --beat-grade: linear-gradient(135deg, #ffffff 0%, #eef2f6 55%, #e3e9f0 100%);

  --logo-filter: none;      /* cube reads on paper; see note in components.md */

  /* Scrollbars (see "Scrollbars & favicon" below) */
  --scroll-thumb: rgba(11,24,32,0.18);
  --scroll-thumb-hover: rgba(0,173,239,0.65);

  --sans: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --mono: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
}
```

The two blocks are **mirror images** — same variable names, different values. Author every component against the variables (`var(--bg)`, `var(--ink)`, `var(--hair)`, `var(--grid-line)`, …) and it will work in both themes automatically. Toggle by setting `data-theme="light"` or `"dark"` on `<html>`.

---

## The default background — the patterned beat

**This is the default full-bleed atmospheric treatment.** It replaces stock photography as the standard. Real cinematic photography is now an *optional upgrade* for hero/marketing surfaces — but the patterned beat is what you reach for by default, and it's the only correct treatment for documents, reports, and dashboards where photography would be wrong.

It is "same drama, no imagery": a graded panel, two slow-drifting cyan glows, and a masked hairline-grid texture that reads as architectural structure without a literal building. Both themes are driven entirely by the tokens above, so the same markup works in light and dark.

```css
/* ════════════════════════════════════════════════════════
   DEFAULT ATMOSPHERIC BEAT — the patterned background.
   Same drama, no imagery. Drop this in wherever the source
   brand would use a full-bleed cityscape photo. Works in
   both themes via tokens.
════════════════════════════════════════════════════════ */
.beat {
  position: relative;
  min-height: 70vh;
  display: flex; align-items: center;
  margin: 0 -4rem;            /* bleed past the page gutter */
  padding: 0 4rem;
  overflow: hidden;
  background: var(--bg-3);
}

/* Atmospheric layer: graded panel + two cyan glows, slowly drifting */
.beat-bg {
  position: absolute; inset: 0;
  background:
    radial-gradient(ellipse 60% 50% at 75% 40%, var(--glow-1) 0%, transparent 60%),
    radial-gradient(ellipse 80% 60% at 15% 80%, var(--glow-2) 0%, transparent 65%),
    var(--beat-grade);
  animation: glowDrift 32s ease-in-out infinite alternate;
}
@keyframes glowDrift {
  0%   { background-position: 0% 0%, 0% 0%, 0% 0%; }
  100% { background-position: 6% -3%, -5% 4%, 0% 0%; }
}

/* Hairline grid texture — architectural feel, no literal imagery.
   Two layers: a faint minor grid + a brighter major grid (blueprint
   feel). Masked to a soft ellipse so it holds through the centre and
   fades only near the edges. */
.beat-overlay {
  position: absolute; inset: 0;
  background-image:
    linear-gradient(to right,  var(--grid-line-major) 1px, transparent 1px),
    linear-gradient(to bottom, var(--grid-line-major) 1px, transparent 1px),
    linear-gradient(to right,  var(--grid-line) 1px, transparent 1px),
    linear-gradient(to bottom, var(--grid-line) 1px, transparent 1px);
  background-size: 256px 256px, 256px 256px, 64px 64px, 64px 64px;
  background-position: -1px -1px;
  mask-image: radial-gradient(ellipse at center, #000 0%, #000 55%, rgba(0,0,0,0.55) 82%, transparent 100%);
  -webkit-mask-image: radial-gradient(ellipse at center, #000 0%, #000 55%, rgba(0,0,0,0.55) 82%, transparent 100%);
}

/* Edge fade — dissolves the beat into the page top and bottom */
.beat::before,
.beat::after {
  content: ""; position: absolute; left: 0; right: 0;
  height: 80px; z-index: 1; pointer-events: none;
}
.beat::before { top: 0;    background: linear-gradient(180deg, var(--bg) 0%, transparent 100%); }
.beat::after  { bottom: 0; background: linear-gradient(0deg,   var(--bg) 0%, transparent 100%); }

.beat-content {
  position: relative; z-index: 2;
  max-width: 1100px; margin: 0 auto; width: 100%;
  padding: 6rem 0;
}
.beat .eyebrow {
  font-size: 11px; letter-spacing: 0.3em; text-transform: uppercase;
  color: var(--ink-50); font-weight: 500; margin-bottom: 1.5rem;
  display: flex; align-items: center; gap: 0.75rem;
}
.beat .eyebrow::before { content: ""; width: 32px; height: 1px; background: var(--accent); }
.beat h2 {
  font-family: var(--sans); font-weight: 200;
  font-size: clamp(2.8rem, 6vw, 5.5rem);
  line-height: 0.98; letter-spacing: -0.05em;
  color: var(--text-strong); max-width: 16ch;
}
.beat h2 strong { color: var(--accent); font-weight: 700; font-style: normal; }
.beat p { margin-top: 1.5rem; max-width: 52ch; color: var(--ink-70); line-height: 1.6; }
```

```html
<section class="beat">
  <div class="beat-bg"></div>
  <div class="beat-overlay"></div>
  <div class="beat-content">
    <div class="eyebrow">Strategic Directive · 2026 / 2027</div>
    <h2>We help <strong>buildings</strong> run themselves.</h2>
    <p>Tomorrow's autonomy, <strong>shipping today.</strong></p>
  </div>
</section>
```

**Glow tuning:** glows are intentionally stronger in light (`0.30 / 0.17`) than dark (`0.15 / 0.10`) — on paper they need more presence to register; on near-black a quieter glow is enough. The grid runs a faint minor line every 64px with a brighter major line every 256px for a blueprint feel. The token values already encode this; don't hand-tune per instance.

---

## Scrollbars & favicon

Two small finishing touches that `starter.html` already wires in, so every page inherits them. Pull them across to any hand-built page too — a Bitpool surface with a default grey scrollbar or a blank tab icon reads as unfinished.

### Scrollbars

Thin, hairline track, an ink-toned thumb that turns cyan only on hover. This follows the brand rule — **cyan punctuates, ink states**: the scrollbar stays quiet until you grab it. Driven by `--scroll-thumb` / `--scroll-thumb-hover`, so the same rules theme automatically (the tokens are in both blocks above).

```css
/* Firefox */
* { scrollbar-width: thin; scrollbar-color: var(--scroll-thumb) transparent; }

/* WebKit / Chromium */
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
  background: var(--scroll-thumb);
  border-radius: 10px;
  border: 2px solid transparent;   /* inset padding → slim pill, not edge-to-edge */
  background-clip: padding-box;
  transition: background 0.3s ease;
}
::-webkit-scrollbar-thumb:hover { background: var(--scroll-thumb-hover); background-clip: padding-box; }
::-webkit-scrollbar-corner { background: transparent; }
```

Keep it subtle — don't make the thumb cyan at rest or widen it past ~10px. The hover cyan is the only accent moment; at rest it's just a hairline-weight ink pill.

### Favicon

The browser-tab icon is the **cube** — the same one identifying every other surface. Reuse the cube that's already embedded as `--logo` rather than pasting the ~40KB base64 a second time (the brand rule is *embed the cube once, reuse everywhere*). `starter.html` does this with a tiny script that runs after the stylesheet, reading `--logo` and setting the icon:

```html
<script>
(function () {
  var logo = getComputedStyle(document.documentElement).getPropertyValue('--logo').trim();
  var href = logo.replace(/^url\((['"]?)(.*)\1\)$/, '$2');
  if (!href) return;
  var link = document.querySelector("link[rel='icon']") || document.createElement('link');
  link.rel = 'icon'; link.type = 'image/png'; link.href = href;
  document.head.appendChild(link);
})();
</script>
```

If you need a purely declarative favicon (no JS — e.g. an email-rendered or sandboxed page), paste the cube data URL from `assets/logo-b64.txt` straight into the markup instead. The file already begins `data:image/png;base64,`, so it goes in the `href` as-is — adding a second prefix breaks the decode:

```html
<link rel="icon" type="image/png" href="…">  <!-- assets/logo-b64.txt as-is; it already carries the data: prefix -->
```

Either way the tab icon is the cube — never a letter, a generic globe, or a recoloured mark.

---

## Typography scale

| Role | Weight | Size | Tracking |
|------|--------|------|----------|
| Section H1 | 300 | clamp(2.5rem · 6rem) | -0.04em |
| Beat headline | 200 | clamp(2.8rem · 5.5rem) | -0.05em |
| H2 | 300 | clamp(1.8rem · 3rem) | -0.03em |
| H3 | 500 | 1.05–1.25rem | -0.01em |
| Body | 300 | 1rem / 1.6 | normal |
| Eyebrow / label | 500 | 10–11px | 0.3em, uppercase |
| Stat value | 300 | clamp(3rem · 7rem) | -0.04em |
| Bold accent | 700 | inherits | normal (never italic) |

## Spacing & layout

- Section padding (desktop): **12–14rem** vertical. Generous breathing room is part of the brand.
- Beat sections bleed with `margin: 0 -4rem` past a `4rem` page gutter.
- Max content width: ~1100px for beats, wider grids allowed for stat/values rows.
- Card radius: 6px. Never pill-rounded panels (pills are only for tiny tag chips).

## Motion

- Reveals: fade-up over **1.4–1.8s**, `cubic-bezier(0.2, 0.8, 0.2, 1)`, triggered ~15% into viewport.
- Atmospheric drift / Ken Burns: **32–50s** cycles, `ease-in-out … alternate`.
- Never bouncy. Never `cubic-bezier(0.34, 1.56, 0.64, 1)`. Never staggered-bounce.

## Breakpoints

- `≤ 980px`: collapse multi-column grids to single column, drop fixed sidebars, reduce beat bleed to the gutter.
- `≤ 640px`: section padding ~6rem, beat `min-height: 60vh`, headline clamps bottom out.

## Fonts

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@100..900&family=JetBrains+Mono:wght@300;400;500&display=swap" rel="stylesheet">
```

Inter is the brand. JetBrains Mono appears only in tiny utility labels (eyebrows in code contexts, metadata rows). No serif, no display face, no italic anywhere.
