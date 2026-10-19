# Deck Systems Reference

How the viewer, animation engine, and PDF export work. All of this already exists in `assets/deck-template.html` — never rewrite these systems, only reuse them. This doc explains the contracts so new slides plug in correctly.

## Contents
1. Slide geometry & viewer
2. Slide scaffolding contract
3. Animation system (class-by-class)
4. Running-order editing: reorder, lock, delete, save
5. PDF export system
6. Adding/removing slides checklist
7. QA workflow

---

## 1. Slide geometry & viewer

- Every slide is a fixed **1920×1080** `<div class="slide" id="sN">` inside `#deck`. Never change these dimensions.
- `fitToWindow()` scales slides to fit **both width and height** of the viewport (minus 64px topbar + 40px breathing room) via `transform: scale()`. It runs on load and on debounced window resize. Do not revert to width-only fitting — slides must always fit one screen.
- `scroll-margin-top: 84px` on `.slide` + `scrollIntoView({block:'start'})` makes arrow-key navigation snap each slide's top just under the topbar.
- Keyboard: ←/→/↑/↓/PageUp/PageDown navigate. Topbar has a **☰ navigator toggle**, Prev/Next, zoom −/+, Fit, and **PDF ↓**.
- **Slide navigator side pane** (`#thumbs`, built by `buildThumbs()` at load): a fixed, scrollable left pane (224px) of live slide thumbnails — each is a DOM clone of the slide scaled to `0.103125` with all animations forced to final state (`.in` + inline transform override, `animateMotion`/`.flow-dot` removed, counters/qring/chart-bars set to final values). Clicking a thumb jumps to that slide; `update()` syncs the active highlight and keeps it scrolled into view; ☰ collapses the pane (body gets `.nothumbs`, `--sbw` → 0) and `fitToWindow()` subtracts the pane width when visible. The pane is hidden in print. **Important:** clones must override the inline `transform` that `applyZoom()` writes on originals — `cloneNode` copies it and it will clip the thumbnail otherwise.
- `let TOTAL = N;` in the script MUST equal the slide count. The progress bar, counter, and Prev/Next disabling all depend on it. It is `let`, never `const` — `renumberDeck()` reassigns it when slides are deleted or restored (see §4).
- The IntersectionObserver (`threshold: [0.35, 0.5]`) does double duty: ≥0.35 triggers slide animations, ≥0.5 updates the current-slide counter.

## 2. Slide scaffolding contract

Every slide follows this skeleton:

```html
<div class="slide" id="sN">
  <div class="s-pad">                 <!-- main content area; flex column, justify-content:center -->
    <div class="eyebrow rv">Section Label</div>
    <h2 class="title rv d1">Headline with <strong>cyan emphasis.</strong></h2>
    <!-- ... content ... -->
  </div>
  <div class="s-head"><a class="lockup"><span class="brand-mark"></span>Bitpool</a><span class="eyebrow" style="font-size:11px;">Chapter</span></div>
  <div class="s-foot"><span></span><span class="pageno">NN</span></div>
</div>
```

- `.s-pad` — `position:absolute; inset:0; padding:110px 120px; flex column; justify-content:center`. Content vertically centres automatically.
- `.s-head` — lockup top-left (cube mark + "Bitpool" text), chapter eyebrow top-right.
- `.s-foot` — optional left text, two-digit `.pageno` right. Keep page numbers sequential.
- **Divider slides** add `<div class="beat-bg"></div><div class="beat-overlay"></div>` as the first children (patterned hairline-grid + cyan-glow background) and use `.giant` for the title.
- `.cols` is the standard grid: `display:grid; gap:4rem; align-items:center; flex:1; align-content:center;`. The `align-content:center` keeps row tracks vertically balanced when the grid stretches — do not remove it (it fixes top-heavy dead space).
- Logo: embedded ONCE as the `--logo` CSS variable (base64 cube PNG, already in the template). Reuse everywhere via `background: var(--logo) center/contain no-repeat` on `.brand-mark`. NEVER embed the base64 a second time — for logos inside SVG diagrams, overlay an absolutely-positioned `.brand-mark` div instead.

## 3. Animation system (class-by-class)

Animations trigger when a slide scrolls into view (`.in` added by the observer). All are one-shot (`dataset.done` guards).

| Class / attr | What it does | How to use |
|---|---|---|
| `.rv` | Fade-up reveal (opacity 0 → 1, translateY) | Add to any element that should reveal |
| `.d1`–`.d6` | Stagger delays .15s–.9s | Combine with `.rv`: `class="rv d3"` |
| `data-count="N"` | Count-up from 0 to N over 1.8s, locale-formatted | `<span data-count="73">0</span>` — initial text must be `0` |
| `.bar-track` / `.bar-fill` with `--w` | Horizontal bar fills to `--w` percent | `<div class="bar-track"><div class="bar-fill" style="--w:73%;"></div></div>` |
| `.qring` | SVG ring draws to a percentage | Circle with `stroke-dasharray="528"`; JS animates dashoffset to `528 * (1 - 0.71)` for 71%. For a different value, change the 0.71 factor in `animateSlide()` or set a `data-pct` and generalise |
| `.chart-bar` with `data-h` | SVG rect grows from baseline y=240 to height `data-h` | Bars must sit on a 240-baseline chart group |
| `.draw` (inside slide SVG) | Stroke line-draw (dasharray/offset 1000) | Add to SVG paths; reveals on `.in` |
| `.pop` (inside slide SVG) | Scale-in pop via `popIn` keyframe | Dots, nodes, markers in diagrams |
| `.flow-dot` / `<animateMotion>` | Travelling dots along paths (infinite) | Decorative motion on flow diagrams |
| `.beat-bg` / `.beat-overlay` | Divider background pattern | Divider slides only |
| `.pulse-dot` | Pulsing cyan dot | Topbar meta / status labels |

Emphasis rule (brand): **bold cyan replaces italics**. `<strong>` and `<em>` both render as `color:var(--accent); font-weight:700; font-style:normal`.

## 4. Running-order editing: reorder, lock, delete, save

The navigator pane doubles as a running-order editor. Every `.thumb-item` is `draggable` and carries a **padlock button** in its top-right corner.

### Behaviour

- **Drag a thumbnail** onto another to move that slide. A cyan rule on the top or bottom edge of the hover target shows whether it will land before or after it.
- **Padlock** pins a slide to its current *position number*. Locked: solid cyan padlock, dashed cyan thumbnail border, `draggable=false`, always visible. Unlocked: faint open padlock, appears on hover only.
- Locked slides **cannot be dragged** and **cannot be displaced** — unlocked slides shuffle around them. Dragging onto a locked slot shakes its padlock (`.deny`) and the drop snaps to the nearest free slot.
- **Keyboard**: focus a thumbnail (it is `tabindex="0"`) then `Alt+↑` / `Alt+↓` to nudge, `Alt+L` to toggle the lock. The global arrow-key handler early-returns on `e.altKey` so deck navigation doesn't swallow these.
- **Delete** a slide with the ✕ button beside its padlock (turns red on hover), or `Alt+Delete` / `Alt+Backspace` on a focused thumbnail. A toast offers **Undo** for 7 seconds; `Alt+Z` undoes from anywhere, with or without a focused thumbnail.
- Deleted slides are **detached but retained** on `deletedStack` together with their thumbnail and original index — never discarded, so `restoreLastDeleted()` puts them back exactly where they were. The stack is unbounded; repeated `Alt+Z` walks back through every deletion.
- **Locked slides cannot be deleted** — the ✕ is hidden (`display:none`) and `deleteSlide()` returns early, shaking the padlock. The padlock protects the slide, not just its position.
- The deck can never be emptied: `deleteSlide()` refuses when one slide remains.
- Every slide also carries an **on-slide control cluster** (`.slide-ctl`, top-right, on hover): padlock + delete, so you can edit without going to the rail. It inverts to a dark treatment on `.photo` / `.ogphoto` slides and is hidden in print.
- Both padlocks route through **`toggleLock(slide, force)`** — the single source of truth. Wire any new lock affordance through it or the rail and the slide will disagree.
- While dragging, a floating **`#dropLine`** shows the insertion point with the target position number, and the rail **auto-scrolls** when the pointer nears its top or bottom edge (essential past ~20 slides). `Alt+Home` / `Alt+End` jump a slide to either end.
- **`saveDeck(ev)`** (the topbar `Save`) **overwrites the deck file in place** via the File System Access API. Lock state survives the round trip through `data-locked`; order and deletions survive because they are real DOM changes.
- A cyan dot appears on `Save` whenever the deck is dirty (`markDirty()` fires from `renumberDeck()` and `toggleLock()`), and `beforeunload` warns if you close with unsaved edits.
- Lock state lives on the slide as `data-locked="1"` — persisted only through Save, not across a plain reload.

### The two contracts that must not break

**1. Slide ids are positional, not identities.** Navigation calls `getElementById('s' + n)` and the IntersectionObserver recovers the current slide with `parseInt(target.id.replace('s',''))`. So every reorder, delete and restore ends in `renumberDeck()`, which reassigns `id="sN"`, the `.pageno` text, and each thumbnail's `dataset.n` + label from the new DOM order.

**2. `TOTAL` is `let`, not `const`.** Deleting changes the slide count, and `TOTAL` drives the counter text, the progress-bar width and the Prev/Next disabled states. `renumberDeck()` resets `TOTAL = slideEls().length` and clamps `current` into range. A `const TOTAL` will look fine until the first deletion, then the counter reads "4 / 8" on a 7-slide deck and Next stops disabling at the end.

Skip either and the failure is silent — no console error, but navigation lands on the wrong slide and the deck lies about its own page numbers.

### What `saveDeck()` must scrub

The rail, the on-slide controls and every animation end-state are **runtime artefacts**. Serialise them naively and the reopened file is subtly broken:

| Artefact | If not scrubbed |
|---|---|
| the whole `#thumbs` **element** | `buildThumbs()` **creates** the nav, it does not fill an existing one. Emptying it instead of removing it leaves a duplicate in the saved file; `getElementById('thumbs')` returns the empty one and **the navigator renders blank** |
| `.slide-ctl`, `#undoToast`, `#dropLine` | duplicated on next load |
| `.in` / `.dragging` / `.removing` classes | animations start already finished |
| `transform` / `margin-bottom` on slides, `width` on `#deck` | a stale zoom is baked in. Remove **only these properties** — never the whole `style` attribute, because slides carry authored inline styles too (the case studies keep their `--ac` accent there) and wiping it guts them silently |
| `[data-count]` text + `data-done` | counters open on their final value and never animate |
| inline `style` on `.bar-fill`, `.chart-bar`, `.qring`, `.draw` | bars and line-draws open already complete |
| `#progressFill` width | progress bar opens at the wrong position |
| the `TOTAL` literal in the script | **the reopened deck reports the wrong slide count** — rewrite it to the surviving count |

That last one is why `TOTAL` is `let`: `buildSaveHTML()` rewrites the literal via regex before serialising.

### How in-place overwrite works — and its one unavoidable dialog

`showSaveFilePicker()` **is** available on `file://` pages in Chromium, which is what makes true overwrite possible rather than a download into `~/Downloads`. But a page can never silently obtain a write handle to its own file — that would let any local HTML rewrite itself unprompted. So:

- The **first** Save opens the picker once. Point it at the deck file and confirm the replace.
- The handle is then held in `deckFileHandle` for the session, so **every later Save writes straight through with no dialog**.
- **Alt+click** Save re-opens the picker to write somewhere else (Save as).
- Permission is re-checked with `queryPermission` / `requestPermission` before each write, since the browser can revoke it.
- `AbortError` (the user cancelled) is swallowed silently and the deck stays dirty.
- Browsers without the API — Firefox, Safari — fall back to a download, and the toast says so rather than pretending it overwrote.

### Gotcha: hoisting

`slideEls()` and `isLocked()` are **function declarations, not `const` arrows**, because `applyZoom()` calls `slideEls()` and runs earlier in the script. As a `const` they sit in the temporal dead zone at that moment and the whole viewer dies on load with *"Cannot access 'slideEls' before initialization"* — the rail never builds. Keep them hoisted.

### Functions

| Function | Role |
|---|---|
| `slideEls()` | Live array of `#deck > .slide` in DOM order — the single source of truth for order |
| `isLocked(el)` | `el.dataset.locked === '1'` |
| `moveSlide(from, to)` | Lock-aware reorder. Records locked positions, permutes only unlocked slides, reassembles, then `applyOrder()`. Returns `false` if the slide is locked or fewer than two free slots exist |
| `applyOrder(order)` | `appendChild` moves both slides and their thumbnails into the given order, then `renumberDeck()` |
| `renumberDeck()` | Reassigns ids, `.pageno`, thumb `dataset.n` and labels, then `update()` |
| `nudgeSlide(el, ±1)` | Keyboard reorder wrapper |
| `deleteSlide(el)` | Detaches slide + thumbnail onto `deletedStack`, renumbers, shows the undo toast. Refuses on locked slides and on the last remaining slide |
| `restoreLastDeleted()` | Pops `deletedStack`, re-inserts slide and thumbnail at the original index, renumbers, re-applies zoom |
| `undoToast(msg)` / `hideUndoToast()` | The 7-second undo prompt (`#undoToast`, hidden in print) |
| `wireThumbControls(item, slide)` | Builds the rail padlock + delete, wires drag/drop + keyboard, cross-links `slide._thumb` / `item._slide` |
| `buildSlideControls()` | Adds the on-slide `.slide-ctl` cluster to every slide; idempotent, re-run after a restore |
| `toggleLock(slide, force?)` | Single source of truth for lock state — syncs both padlocks, `draggable` and the icons |
| `showDropLine` / `hideDropLine` / `railAutoScroll` / `stopRailScroll` | Drag affordances |
| `buildSaveHTML()` | Scrubs a clone of the document, rewrites `TOTAL`, returns `[html, slideCount]` |
| `saveDeck(ev)` | Overwrites the bound file in place; picks the target on first use or on Alt+click; falls back to download |
| `markDirty()` / `markClean()` | Unsaved-changes dot on the Save button |

Because reordering and deleting operate on real DOM nodes, **PDF export needs no special handling** — the PDF is whatever is in the DOM, in DOM order, so a 5-slide deck prints 5 pages. `applyZoom()` walks `slideEls()` (live) rather than the `slides` NodeList captured at load, so restored slides get the right scale. The `slides` NodeList captured at load is static, so observers and `applyZoom()` keep working after a reorder.

### When adding slides

`wireThumbControls(item, s)` is called from `buildThumbs()` immediately before `sb.appendChild(item)`. New slides picked up by `buildThumbs()` get reorder, lock and delete for free — nothing extra to wire. Set `TOTAL`'s initial literal to the authored slide count as usual; from then on `renumberDeck()` owns it.

---

## 5. PDF export system

The **PDF ↓** button (`#pdfBtn`, cyan, last in `.controls`) calls `downloadPDF()`:

1. `completeAllAnimations()` — adds `.in` to every slide, sets all `data-count` text to final values, sets `.qring` dashoffset, grows all `.chart-bar` rects, with transitions disabled.
2. Double `requestAnimationFrame`, then `window.print()` — the user picks "Save as PDF".
3. A `beforeprint` listener also runs `completeAllAnimations()` so Ctrl+P works too.

The `@media print` block enforces:
- `@page { size: 1920px 1080px; margin: 0; }` — one slide per page at native resolution
- topbar + progress hidden; body/background reset; slide transform/shadow/radius removed
- `page-break-after: always` per slide
- `* { transition:none; animation:none; }` with explicit final-state overrides:
  - `.rv { opacity:1; transform:none; }`
  - `.slide svg .draw { stroke-dashoffset:0; }`
  - `.slide svg .pop { opacity:1; transform:none; }` ← required because `.pop` reveals via keyframe animation, which `animation:none` would otherwise freeze at opacity 0
  - `.flow-dot, circle:has(> animateMotion) { display:none; }` ← travelling dots would freeze mid-path
- `* { -webkit-print-color-adjust:exact; print-color-adjust:exact; }`

**If you add a new animation class whose resting state is invisible, you MUST add a print override forcing its final state**, or it will be missing from the PDF. This is the most common regression.

## 6. Adding/removing slides checklist

1. Copy the closest archetype from the template or `references/example-*.html`.
2. Renumber: `id="sN"`, `.pageno`, and update `let TOTAL = N;`.
3. Keep `.s-head` / `.s-foot` scaffolding and chapter eyebrow consistent.
4. Stagger reveals with `.rv d1…d6` — title gets `d1`, content groups `d2+`.
5. New invisible-at-rest animations → add print override (see §5).
6. Run the QA workflow.

## 7. QA workflow (Playwright Chromium)

Always QA before delivering. Three checks:

**a) Overflow check** — no element may extend past its slide's 1920×1080 bounds:
```js
// for each .slide with transform reset, compare every descendant's
// boundingRect against the slide rect; flag bottom/right overflow > 2px
```

**b) Screen fit** — load at 1440×900 and 1920×1080 viewports; assert the first slide's scaled rect fits the viewport (height ≤ innerHeight − 64) and zero `pageerror`s. (A single 403 console error for Google Fonts is expected in sandboxes.)

**c) PDF check** — `page.pdf({ width:'1920px', height:'1080px', printBackground:true, margin:0 })` after calling `completeAllAnimations()`; verify page count == TOTAL, then `pdftoppm -png -r 50` a few pages and visually inspect: chrome hidden, counters at final values, diagram dots/lines present.
