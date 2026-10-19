# Animation library — 50 more visual layouts

`assets/example-animation-library.html` is a finished 50-slide deck ("Buildings that run
themselves", sample content) where **every slide carries a different animation**. Use it as a
library: when a slide in an approved outline would land better with motion than with plain cards,
borrow the matching layout from it.

## How to borrow a layout

1. Find the slide below and open the example deck at that number (☰ lists them by name).
2. Copy its whole `<section class="slide fx mx m-<name>">` into the draft, after the template's
   own slides are filled in. Change the words; keep the item count in the table.
3. Copy two CSS blocks from the example's `<style>` into the end of the draft's `<style>`, **after**
   the template's rules — never edit the template's own rules:
   - the shared `ANIMATION LIBRARY` block (`.mx …`, copied once per deck), and
   - every rule that starts `.m-<name>` or `section.slide.m-<name>`, plus its `@keyframes m-<name>-…`.
4. Replace every sample word. The sample copy uses Bitpool boilerplate facts (60 billion data
   points a year, 500+ buildings across Australia, the UK and Southeast Asia) and generic building
   advice; anything marked **Illustrative** on the slide is invented and must be replaced with real
   data or removed.
5. Image placeholders are inline SVGs labelled "Image placeholder". Swap each `src` for a real
   `media/…` file before `scripts/embed_media.py` runs.

Every layout follows the template's motion contract: the element's own style is the finished
state, keyframes say where it comes from, the motion plays only while the slide is current (`.on`)
and replays on every visit, and print, PDF, **Edit** and reduced motion show the finished slide
(the `fx` class handles that). Infinite loops (radar, marquee, gears…) stop in those modes too.

## The 50 layouts

`dk` = built dark. Any light one can take `dk` if its colours read on navy; check it in the browser.

| # | Class | Motion | Use it for | Fixed items |
|---|---|---|---|---|
| 01 | `m-cov` | Hero words rise out of a blur, grid settles | Cover | 1 headline, ≤ 4 words animated |
| 02 | `m-odo` | Digits roll like an odometer | One big number beside 3 cards | 2 digits; 3 cards |
| 03 | `m-drop` | Tiles fall and bounce into a grid | Nine named things, each with a sparkline | 9 tiles |
| 04 | `m-flick` dk | Screens flicker and dim out | The problem: ignored dashboards | 12 tiles |
| 05 | `m-flip` | Cards flip in 3D | Four pillars or words | 4 cards |
| 06 | `m-iris` | Photo opens through an iris | Steps beside one photo | 3 steps; 1 image |
| 07 | `m-conv` | Scattered chips converge into one box | Many sources becoming one | 8 chips; 1 box |
| 08 | `m-strike` | Old text struck through, new text wipes in | Before/after wording, naming rules | 4 rows |
| 09 | `m-bars` | Bars spring up with overshoot | Steps beside a bar chart | 3 steps; 24 bars |
| 10 | `m-ecg` dk | Heartbeat line sweeps a monitor | Baselines, "normal" vs not | 3 cards |
| 11 | `m-floors` | Floors light up bottom to top | Whole-building view | 3 steps; 8 floors |
| 12 | `m-dial` | Dial needle swings to a setpoint | One setting and its trade-offs | 3 cards |
| 13 | `m-sky` | Sky turns from day to night | Overnight / scheduled work | 3 steps |
| 14 | `m-radar` dk | Radar sweep, blips appear | Things being detected | 4 rows; 4 blips |
| 15 | `m-sieve` | Dots fall, few pass the mesh | Filtering noise to what matters | 3 steps |
| 16 | `m-kanban` | Card travels across columns | A four-stage workflow | 4 columns; 1 card |
| 17 | `m-check` | Checkbox ticks draw in order | A checklist | 6 items |
| 18 | `m-toggle` | Switches flip on (one stays off) | Automatic vs manual | 4 switches |
| 19 | `m-gauge` | Needle swings, damps into a band | A range, not a number | 3 cards |
| 20 | `m-pins` | Pins drop onto a map | Locations | 3 pins; 1 map image |
| 21 | `m-ripple` dk | Ripples radiate, labels light as they arrive | One centre, many sources | 6 labels |
| 22 | `m-flow` | Particle streams in and out of a core | Inputs → process → outputs | 3 in; 3 out |
| 23 | `m-heat` | Heatmap fills in a diagonal wave | Patterns over time | 3 steps; 7×24 grid |
| 24 | `m-wipe` | Timeline wipes in behind a cursor | Stages of a day or process | 5 points |
| 25 | `m-doors` dk | Two doors slide open on a statement | A big single statement | 1 statement; 3 chips |
| 26 | `m-slider` | Before/after divider sweeps | Comparing two screens | 3 steps; 2 images |
| 27 | `m-burns` | Slow zoom and pan on a photo, captions rise | A place told through a photo | 3 captions; 1 image |
| 28 | `m-carousel` | 3D ring of cards rotates | Roles, audiences, options | 6 cards |
| 29 | `m-scale` | Balance tips, then levels | Two things kept in balance | 2 pans; 3 cards |
| 30 | `m-blob` dk | Glowing shape morphs behind a quote | A line to remember | 3 columns |
| 31 | `m-marquee` | Two rows scroll opposite ways | Do / don't word lists | 10 + 10 words |
| 32 | `m-hilite` | Highlighter sweeps behind words | Vague → specific rewrites | 3 rows |
| 33 | `m-toast` | Notifications spring in | What a good message looks like | 3 steps; 3 toasts |
| 34 | `m-env` | Envelope opens, letter rises | Writing to someone | 3 steps; 1 letter |
| 35 | `m-puzzle` | Pieces fly in and snap together | Fitting into what exists | 4 pieces |
| 36 | `m-gears` dk | Interlocking gears turn | A repeating three-step loop | 3 steps; 3 gears |
| 37 | `m-belt` | Conveyor carries items to an output | Raw in, result out | 8 items; 3 cards |
| 38 | `m-venn` | Three circles slide together | Where things overlap | 3 circles; 3 steps |
| 39 | `m-mesh` | Network nodes pop, links draw | Many connected sites or people | 16 nodes; 3 cards |
| 40 | `m-tree` | Decision tree grows top-down | Yes/no triage | 3 questions; 4 outcomes |
| 41 | `m-spot` dk | Spotlight travels card to card | Questions or points in order | 3 cards |
| 42 | `m-scan` | Scan line passes, highlights appear | What to look for on a drawing or screen | 3 steps; 3 boxes; 1 image |
| 43 | `m-stamp` | Stamp slams onto a record | Sign-off, approval | 4 steps; 1 stamp |
| 44 | `m-cal` | Calendar days pop in | A schedule or plan | 10 days |
| 45 | `m-batt` | Battery fills with a moving wave | Something accumulating | 3 cards |
| 46 | `m-stack` dk | Isometric layers gather into a stack | Architecture layers | 4 layers |
| 47 | `m-type` | Terminal record types line by line | A data record, config or command | 3 steps; 6 lines |
| 48 | `m-acc` | Accordion opens row by row | FAQs | 4 questions |
| 49 | `m-deal` | Cards dealt from a pile | Habits or rules | 4 cards |
| 50 | `m-close` dk | Cube faces fly in and assemble | Closing slide | 3 rows; 2 chips |

## Checks specific to borrowed layouts

- **Uniqueness.** Each class appears once per deck; two slides with the same `m-<name>` are fine
  but replay the same motion, so prefer a different layout.
- **Fit.** These layouts place their parts absolutely inside the 1680×852 stage. Run the overflow
  check in `build-check-review.md` — anything listed (other than deliberate full-bleed marquees)
  means the copy is too long. Shorten it; never shrink the type.
- **Finished state.** Turn on **Edit** and look at each borrowed slide: it must read correctly with
  the motion off, because that is what the PDF prints.
