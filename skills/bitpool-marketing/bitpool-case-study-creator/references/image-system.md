# Image & visual system

## Full-bleed heroes
Interior renders are **full-bleed** (`.feature.bleed`): they run edge-to-edge of the
white page (negative `--pad` margins), with no side radius. This is what makes them
read as large heroes rather than letterboxed strips.

- Cover hero: `--ratio:48%` (sits between lead and stats).
- Page-2 / Page-3 heroes: `--ratio:62%`–`64%` with `margin-top:auto` so they anchor to
  the bottom of the page and fill the space under the text section.
- Height = `ratio × width`. The bleed width is the full page (≈794px on screen), so 62%
  ≈ 490px — a genuine hero. Push to ~70% only if the text section above is short.

Each hero animates: a 2.8s Ken-Burns `scale(1.08→1)` plus a 1.6s left-to-right
`clip-path` wipe, triggered when it scrolls into view.

## Captions
`.feature .cap` sits over a **tall, strong bottom scrim**
(`rgba(8,14,19,.92)` → transparent). Keep captions to one line, `<b>` (cyan) on a key
phrase, with a mono tag chip on the right (e.g. "Server Hall", "Whole-Site View").
The strong scrim is what keeps text legible over busy renders — never weaken it.

## Source images
Feed the highest-res renders you have; `prep-images.py` downsizes to 1700px JPEG q82.
Best subjects, in order of impact: exterior/establishing (cover), the most
infrastructural interior (server hall / floor), a systems/whole-site/digital-twin
view, and a plant/mechanical room (Strategic Value).

If a hero image is missing, the patterned grid+glow background still shows through —
acceptable as a fallback, but the format is designed around real imagery.

## Outcome performance rings
The ring is an SVG of two `r=52` circles (`stroke-dasharray:327`). The progress arc
fills via `stroke-dashoffset = 327 × (1 − pct/100)` and the centre number counts up,
both on scroll-in and forced to final state on print.

To set a ring: edit `data-pct` on `.prg` **and** `data-count` on the `.num` to the same
value, and write the mono label (`.rl`) and the title/sentence beneath.

> Percentages are performance **claims**. Only publish real, client-approved numbers.
> The skill ships with illustrative values (72 / 85 / 98) — always replace them.

## Partner logo & headshot
- Partner logo: `prep-images.py` strips a flat black **or** white background to
  transparent so it reads on the light header chip, the navy quote block, and the
  light "Delivered with" cell. The header chip is transparent with a hairline border —
  never a dark fill behind a transparent logo (that reads as a black box).
- Headshot: square-cropped (slight upward bias) and shown as a 78px circular avatar
  with a faint ring + shadow in the testimonial byline. Big enough to actually see.

## The non-negotiables (inherited from bitpool-design-system)
Inter only; **bold cyan `#00ADEF` replaces italics**; the cube logo in every header
and footer and as favicon; hairline borders; long slow easing; cyan punctuates, ink
states; light theme (white paper, near-black ink) because this is a read-closely /
printable document.
