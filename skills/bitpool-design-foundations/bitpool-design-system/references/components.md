# Bitpool components

Copy-paste components. All assume the tokens from [Tokens](tokens.md) are loaded and theme it via `data-theme` on `<html>`. For the full visual catalogue (axiom grids, growth pillars, SKA promise, scale stats, values grids, page composition) see the standalone brand-guide HTML (ships with the skill) — open it in a browser and lift any section.

---

## Logo — always included

**Every Bitpool artifact carries the logo.** No exceptions — page, deck, report, dashboard, one-pager. It appears in the **top-left of the nav/header** and again in the **footer**. The cube is the only visual identifier; "Bitpool" is set as Inter text beside it (the lockup), never as a separate wordmark graphic.

The cube PNG (`assets/cube-logo.png`, 256×227, transparent) is embedded **once** as the `--logo` custom property and reused everywhere via `background: var(--logo)`. `assets/logo-b64.txt` holds the **complete** data URL — it already begins `data:image/png;base64,`. Paste its contents as-is in place of the `…` below; do **not** write a `data:image/png;base64,` prefix yourself. Doing so produces a doubled prefix, which fails to decode silently — a CSS `background-image` that will not load shows no broken-image icon and logs no console error, so the page just renders with a blank space where the cube should be. `starter.html` already has this wired up.

```css
:root { --logo: url("…"); }   /* paste assets/logo-b64.txt as-is — it already carries the data: prefix */

/* Cube mark on its own */
.brand-mark {
  width: 28px; height: 28px;
  background: var(--logo) center/contain no-repeat;
  filter: var(--logo-filter);          /* none in both themes; see note */
}

/* Lockup: cube + "Bitpool" wordtext */
.lockup {
  display: inline-flex; align-items: center; gap: 0.6rem;
  font-family: var(--sans); font-weight: 500; letter-spacing: -0.01em;
  color: var(--text-strong); font-size: 1.1rem;
}
.lockup .brand-mark { width: 26px; height: 26px; }
```

```html
<!-- Nav (top-left) -->
<nav class="nav">
  <a class="lockup" href="#"><span class="brand-mark"></span>Bitpool</a>
  <!-- nav links … -->
</nav>

<!-- Footer -->
<footer class="footer">
  <a class="lockup" href="#"><span class="brand-mark"></span>Bitpool</a>
  <p class="footer-meta">© 2026 Bitpool · Buildings that run themselves.</p>
</footer>
```

**The cube is a true-colour PNG with transparency** (cyan + navy facets), so it reads correctly on both light paper and near-black — `--logo-filter` is `none` in both themes. Do **not** invert, recolour, rotate, or add effects (this is a brand rule). The only adjustment ever permitted is sizing. Minimum size 22px; clear space at least one cube-face height on every side.

> Contrast with Swing Katz: the SSK wordmark is a flat white PNG that needs `filter: invert(1)` on light backgrounds. The Bitpool cube does **not** — it's full-colour and needs no filter either way. Don't carry the SSK invert trick over.

---

## Nav & footer shells

```css
.nav {
  position: fixed; top: 0; left: 0; right: 0; z-index: 100;
  display: flex; align-items: center; justify-content: space-between;
  padding: 1.25rem 4rem;
  background: color-mix(in srgb, var(--bg) 80%, transparent);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--hair);
}
.nav-links { display: flex; gap: 2rem; }
.nav-links a {
  color: var(--ink-70); text-decoration: none; font-size: 0.9rem; font-weight: 400;
  letter-spacing: -0.01em; transition: color 0.3s;
}
.nav-links a:hover { color: var(--text-strong); }

.footer {
  border-top: 1px solid var(--hair);
  padding: 4rem; display: flex; align-items: center; justify-content: space-between;
  flex-wrap: wrap; gap: 1.5rem;
}
.footer-meta { color: var(--ink-50); font-size: 0.85rem; }
```

A small pulsing cyan dot is a recognisable Bitpool nav detail:

```css
.pulse-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--accent); box-shadow: 0 0 8px var(--accent);
  animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.35; } }
```

---

## Hero (text + default patterned beat)

The hero is just the `.beat` from [Tokens](tokens.md) at full height. Use it as the opening moment; the logo still sits in the fixed nav above it.

```html
<header class="beat" style="min-height: 92vh;">
  <div class="beat-bg"></div>
  <div class="beat-overlay"></div>
  <div class="beat-content">
    <div class="eyebrow">Bitpool · 2026</div>
    <h2 style="font-size: clamp(3rem, 8vw, 7rem);">
      We help <strong>buildings</strong><br>run themselves.
    </h2>
    <p>Tomorrow's autonomy, <strong>shipping today.</strong></p>
  </div>
</header>
```

For a marketing hero you *may* swap the `.beat-bg` for a real photograph (Brisbane, blue hour) with the same atmospheric overlay + cyan glow + Ken Burns drift — but the patterned beat is the default and is always acceptable.

---

## Axiom card (kicker → title → payoff)

```css
.axiom {
  padding: 2.5rem; border: 1px solid var(--hair); border-radius: 6px;
  background: var(--bg-2); transition: border-color 0.4s, transform 0.4s;
}
.axiom:hover { border-color: color-mix(in srgb, var(--accent) 40%, transparent); transform: translateY(-3px); }
.axiom .kicker { font-size: 10px; letter-spacing: 0.25em; text-transform: uppercase; color: var(--accent); font-weight: 600; }
.axiom h3 { margin: 1rem 0 0.6rem; font-weight: 500; font-size: 1.25rem; color: var(--text-strong); letter-spacing: -0.02em; }
.axiom p { color: var(--ink-70); line-height: 1.6; font-size: 0.95rem; }
.axiom p strong { color: var(--accent); font-weight: 700; font-style: normal; }
```

```html
<div class="axiom">
  <div class="kicker">01 · Autonomy</div>
  <h3>Buildings that decide.</h3>
  <p>Not dashboards that <strong>wait for you</strong> — systems that act.</p>
</div>
```

## Stat cell

```css
.stat .value {
  font-weight: 300; font-size: clamp(3rem, 7vw, 6rem);
  line-height: 1; letter-spacing: -0.04em; color: var(--text-strong);
}
.stat .value strong { color: var(--accent); font-weight: 300; font-style: normal; }
.stat .label { margin-top: 0.75rem; color: var(--ink-50); font-size: 0.9rem; letter-spacing: 0.02em; }
```

```html
<div class="stat">
  <div class="value">60<strong>B</strong></div>
  <div class="label">records under management</div>
</div>
```

---

## Reveal-on-scroll machinery

```css
.reveal { opacity: 0; transform: translateY(24px); transition: opacity 1.6s cubic-bezier(0.2,0.8,0.2,1), transform 1.6s cubic-bezier(0.2,0.8,0.2,1); }
.reveal.in { opacity: 1; transform: none; }
```

```js
const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) e.target.classList.add('in'); }), { threshold: 0.15 });
document.querySelectorAll('.reveal').forEach(el => io.observe(el));
```

Everything else — growth pillars, SKA promise, values grids, scale rows, page composition — is in the standalone brand-guide HTML (ships with the skill). Lift sections from there and swap any literal `#0b1218`/`#fff` colours for the matching `var(--…)` token so they theme correctly.
