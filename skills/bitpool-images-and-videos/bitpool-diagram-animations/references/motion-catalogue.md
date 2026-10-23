# Motion: choosing it, and writing it

Every animation this skill makes draws on the 50 recipes in the *Buildings that run themselves*
animation library. They ship verbatim in `assets/motion-recipes.css` (the CSS) and
`assets/recipe-examples.html` (the markup that goes with it). Find the recipe you need with
`search_files` (e.g. pattern `m-flow` in `assets/motion-recipes.css`), not by reading the whole file.

## The motion contract

Every recipe follows the same rule, and anything you write must too:

1. **An element's own style is its finished state.** Position, colour and size are written as the
   diagram should look at rest.
2. **Keyframes describe where it comes from** (`from{opacity:0;transform:…}`), run with
   `animation-fill-mode: backwards`, so the element sits at the start of its animation during its
   delay and lands on its own style.
3. **Motion only plays while the section has `.on`.** Selectors are
   `section.slide.on .your-thing{animation:…}`. The template adds `.on` once the font is ready and
   re-adds it on click, R or Space, which replays the build-in.
4. **Timing comes from variables.** `--b` is the base delay (0.4s, set by the template). Stagger with
   an index set inline, e.g. `style="--i:2"` and `calc(var(--b) + var(--i)*.15s)`.
5. **Reduced motion and print show the finished diagram.** The template turns every animation off in
   those cases, and because of rule 1 what remains is the complete diagram. Never hide something with
   `opacity:0` in its own style and reveal it with a forwards animation; it would vanish with motion
   off.

## Build in, then loop

Each animation has two layers:

- **Build-in (plays once per replay).** Elements arrive in the story order from the inventory. Keep
  the whole build-in between 2.5 and 6 seconds. Stagger siblings 0.1–0.3s apart. Groups arrive
  before what's inside them, nodes before the lines that join them, lines before the particles that
  travel them.
- **Live loop (repeats forever).** Starts once the build-in has finished (delay it past the last
  arrival) and carries the diagram's meaning. Data flowing becomes particles on the paths; a
  monitored thing becomes a slow pulse or ripple; a scan becomes a sweep. Use one or two live
  motions per diagram, not one per element. Calm beats busy, so loops run 2–4s and stay subtle.

## Which recipe for which part of a diagram

Pick by what the element *means* in the diagram, not by which motion looks nicest. Recipes marked
**dk** were designed on the dark background; they work on light only after their hard-coded dark
colours are swapped for tokens.

### Things arriving (build-in)

| Diagram feature | Recipe | Motion |
|---|---|---|
| Title words or big statement | `m-cov` | words rise out of a blur, then a cyan rule draws |
| Separate items landing in place | `m-drop` | drop and bounce |
| Items coming in from many sources to one place | `m-conv` | items converge on a centre |
| A set of equal cards or options | `m-flip` / `m-deal` | cards flip over / are dealt in |
| A list being ticked off | `m-check` | ticks draw on |
| A sequence of rows or records | `m-type` / `m-acc` | lines type out / rows open |
| Notifications, events, alerts | `m-toast` | toasts stack up |
| Parts that fit together | `m-puzzle` | pieces snap together |
| Layers of a stack or architecture | `m-stack` **dk** | layers gather into a stack, labels slide in |
| A logo-like or 3D block | `m-close` **dk** | cube faces assemble |
| A reveal of a hidden area | `m-iris` / `m-doors` **dk** | iris opens / doors open |
| A before-and-after comparison | `m-slider` | slider wipes between two states |
| A photo or plan to explore | `m-burns` / `m-scan` | slow Ken Burns pan / scan line passes |

### Flows and connections (usually the live loop)

| Diagram feature | Recipe | Motion |
|---|---|---|
| Data moving along arrows, inputs to a hub to outputs | `m-flow` | particles stream along SVG paths |
| A network of sites or devices | `m-mesh` | nodes pop, links draw between them |
| A pipeline or processing chain | `m-belt` | items ride a conveyor |
| Interlocking stages that drive each other | `m-gears` **dk** | gears turn |
| One source reaching many | `m-ripple` **dk** | rings ripple outwards |
| A decision path | `m-tree` | branches draw, then each node pops in |
| Filtering many things down to a few | `m-sieve` | items fall through a sieve |
| Overlapping scopes | `m-venn` | three circles slide in from three sides, the overlap pops |
| Work moving between states | `m-kanban` | cards move across columns |

### Values and states

| Diagram feature | Recipe | Motion |
|---|---|---|
| A headline number | `m-odo` | digits roll like an odometer |
| A trend or bar chart | `m-bars` | bars spring up |
| A live signal or baseline | `m-ecg` **dk** | heartbeat line sweeps |
| A setpoint or single reading | `m-dial` | needle swings to value |
| A value inside a band | `m-gauge` | needle overshoots and settles |
| A level, charge or saving | `m-batt` | fill rises with a wave |
| A grid of values | `m-heat` | colour washes across diagonally |
| Two things in balance | `m-scale` | scale tips and settles |
| Floors or levels of a building | `m-floors` | floors light up in turn |
| Locations on a map | `m-pins` | pins drop |
| Something being detected | `m-radar` **dk** | radar sweep with blips |
| On / off or automated controls | `m-toggle` | switches flip |
| Time of day or a schedule | `m-sky` / `m-wipe` / `m-cal` | day to night / timeline wipes / calendar fills |
| A wrong item replaced by a right one | `m-strike` | strike through, replacement appears |
| Something approved or signed off | `m-stamp` | stamp lands |
| Screens or sources going dark | `m-flick` **dk** | screens flicker out |
| Focusing on one part | `m-spot` **dk** | a spotlight moves along, lighting each item in turn |

Recipes not listed here (`m-blob`, `m-carousel`, `m-marquee`, `m-hilite`, `m-env`) are for slides of
text and rarely fit a diagram. Use them only when the diagram really is that thing.

## Borrowing a recipe directly, or adapting it

- **Directly:** when the diagram matches a recipe's structure (a hub with inputs and outputs is
  `m-flow`), reuse its class names in the markup. Pass `--recipes flow` and
  `--section-classes m-flow` to `scripts/assemble.py` so its CSS is included and its selectors
  (`section.slide.m-flow.on …`) match. Override positions and sizes in the diagram's own CSS.
- **Adapting:** most diagrams need the *technique* but not the layout. Copy the recipe's keyframes
  into the diagram CSS under a new name with a `d-` prefix (`@keyframes d-flow-run`), use `d-`
  classes in the markup, and write selectors as `section.slide.on .d-thing`. Keep the timings and
  easing the recipe uses (`var(--bp-ease)`, the `cubic-bezier` springs), because that's what makes
  it feel like the library.
- **Several recipes in one diagram is normal:** `m-drop` for the nodes arriving, `m-flow` particles
  for the live loop, `m-ripple` on the central node. Pass them all: `--recipes drop,flow,ripple`.

## Dark and light

The template carries both token sets; `--theme dark` adds `.dk`, and every `var(--bp-…)` re-themes
itself. Hard-coded colours don't. Several recipes paint `#fff` surfaces or dark `#0b1218` panels
directly, and `assemble.py` prints a warning listing any white backgrounds when building dark.
Override each one in the diagram CSS with `var(--bp-white)` / `var(--bp-surface-2)` (and
`var(--bp-text-strong)` for text on it), then rebuild until the warning is gone.
