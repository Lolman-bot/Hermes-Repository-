# Slide layouts and planning — steps 5 and 6

Every slide is one of the 28 layouts in `assets/deck-template.html`: twelve content layouts and
sixteen visual layouts. Each one is marked in the template with a `<!-- LAYOUT: name -->` comment.
Copy the whole `<section>` and change the words — never write slide markup from scratch.

`assets/example-deck.html` is a finished Bitpool training deck (its subject is an older AI-tools
course; screenshots swapped for placeholders). It is a **style reference only**: open it to see how
the layouts mix, how often a visual or dark slide breaks up the content, and how the copy reads.
Never build from it and never reuse its content — always build from the template.

## Content layouts

| Layout | Use it for | Limits so it fits 1920×1080 |
|---|---|---|
| `cover` | Slide 1, always. Big headline with one cyan phrase, one-line intro. | Headline ≤ 6 words; intro ≤ 2 lines. |
| `three-cards` | Three parallel ideas: problem/cost/result, three habits, three options, three models. | 3 cards; ≤ 4 bullets each; optional `.eg` line and `.tip`. Two ideas → use `c2`. |
| `badge-grid` | Four to six short benefits or points with a number badge each. | ≤ 6 points; ≤ 2 sentences each. |
| `divider` | Start of every section. Big number (01, 02…), section title, one line. | Title ≤ 7 words. |
| `text-and-media` | A product, tool or place explained beside one screenshot or video. | Card ≤ 2 labelled lists of ≤ 3 bullets. |
| `steps-on-screenshot` | "Click here, then here" walkthroughs on one screenshot with pins. | ≤ 5 steps per slide — split into "(1–3)" and "(4–6)" slides beyond that, as the example does. |
| `concept-with-images` | A concept with two short points and one or two supporting images stacked. | ≤ 3 steps. |
| `two-images` | Two places or screens compared side by side with captions. | 2 images. |
| `steps-only` | A walkthrough with no picture — what a command does, a process. | ≤ 5 steps. |
| `command-grid` | A list of commands, shortcuts or terms with one line each. | ≤ 9 items. |
| `tile-grid` | A map of named things (plugins, products, sites) each with a tag. | ≤ 12 tiles. |
| `closing` | Last slide: what to do next. | ≤ 5 steps. |

If content won't fit the limits, split it across two slides; never shrink the type.

## Visual layouts

Each one is a drawn scene with its own motion that plays when the slide comes up and replays on every
visit. Their geometry is fixed: lines, chips and SVG paths are placed for **exactly** the item count
shown. Keep that count — if the content has a different number of items, use a content layout
instead. Never move the drawn parts around to fit.

| Layout | Use it for | Fixed items |
|---|---|---|
| `stacked-sheets` | The problem: three symptoms or costs as a stack of offset pages. | 3 sheets, ≤ 3 bullets each. |
| `rising-chart` | A trend or gap: a small line chart above three cards that rise in height. | 3 cards, ≤ 3 bullets; 3 chart chips. |
| `hub-spokes` | One thing feeding three outcomes, with pulses running down the lines. Dark. | 3 cards, ≤ 3 bullets. |
| `orbit-panels` | What something is: four inputs orbiting a core, plus is / good at / is not panels. | 4 orbit chips; 3 panels. |
| `compare-habits` | A strong-versus-weak example, three habit rows, and a two-point recap. | 2 example bars; 3 rows; 2 recap points. |
| `tier-columns` | Three options in rising tiers (models, plans, levels) with a level bar and price line. Dark. | 3 columns. |
| `share-network` | Why sharing beats keeping it to yourself: solo → hub → many, plus three cards. | 3 cards. |
| `terminal-list` | A dark command listing beside a short explanation. | ≤ 13 rows. |
| `journey-line` | A short sequence of stages along a line that lights up in turn. Typed title. | 4 stages. |
| `chat-window` | A question-and-answer exchange in a chat window beside four steps. Typed title. | 5 messages; 4 steps. |
| `search-results` | A search being typed, with result cards. Dark. Typed title. | 4 results. |
| `stations` | Four stations on a rail with a card under each. Typed title. | 4 stations. |
| `pipeline-canvas` | Four steps beside a drawn flow from inputs to a finished output. Typed title. | 4 steps; 3 chips. |
| `commit-funnel` | Many parts funnelling into one result behind an approval gate. Typed title. | 4 steps; 6 parts. |
| `toolbox-zones` | A grid of named things plus a separate dark panel for a second group. | 9 grid tiles + 2 panel tiles. |
| `closing-loop` | A closing slide: a loop around the cube with next-step rows. Dark. | 5 rows. |

**Typed titles** (`<h2 class="title tw" style="--n:11">`) type themselves out — they suit a slash
command or a short name. Set `--n` to the title's character count.

## Rhythm, dark slides and the cover

- **Break the content up.** After every three or four content slides, use a visual layout or a dark
  slide. In the example deck, 16 of 36 slides are visual and 4 are dark.
- **Dark slides:** add `dk` to any slide's class (`class="slide dk"`) and it re-themes itself. Use it
  for emphasis — a hub, a tier comparison, the close — never for two slides in a row.
- **Photo cover:** if the person supplies a hero photo, use the cover layout's optional `has-bg`
  variant (see the comment above it in the template). Otherwise keep the default glow-and-grid cover.

## Mapping input to layouts

- A PowerPoint slide with three columns or cards → `three-cards`.
- A screenshot with numbers over it → `steps-on-screenshot` (numbers become pins).
- A slide that is only a title + one line → `divider`.
- A bullet list of commands or names → `command-grid` or `tile-grid`.
- A summary slide → fold its points into `closing`, or offer `badge-grid` as a recap.
- A chart or diagram image that's hard to read at slide size → offer to replace it with cards that
  say the same thing (the example deck replaced its "Endless Divergence" chart this way). Ask first.
- A "why this matters" or "what is X" slide → offer a visual layout (`stacked-sheets`,
  `rising-chart`, `hub-spokes`, `orbit-panels`) instead of plain cards, when the item count matches.
- One slide per command, skill or tool → a visual layout with a typed title (`journey-line`,
  `chat-window`, `stations`, `pipeline-canvas`, `commit-funnel`), like the example's skill slides.

## Suggested extra slides

Offer these where they'd help, and **mark each as a suggestion** in the outline — the person keeps or
drops each one at step 6:

- **"Why" slides** after the cover (`three-cards` or `badge-grid`): the problem, what the thing is,
  why it helps the audience.
- **A divider** in front of every section that has three or more slides.
- **Splitting** a crowded slide into "(1–3)" and "(4–6)".
- **A closing slide** — "your first week with…", next steps, where to get help.

Never add a suggested slide's content as fact. If it needs a claim the inputs don't support, write
it as a question in the outline for the person to answer.

## Showing the outline (step 6)

One numbered list, one line per slide:

```
01  cover                    Bitpool Cloud Training — "Building dashboards in Bitpool Cloud"
02  stacked-sheets     [NEW] Why: the reporting problem
03  hub-spokes  dk     [NEW] Why we build dashboards in Bitpool Cloud
04  divider            [NEW] 01 · How to build your first dashboard
05  steps-on-screenshot      Adding a widget (1–3)  · image: s05-add-widget.png
...
```

Mark suggestions with `[NEW]`, mark dark slides `dk`, name the image each slide uses, and end with
"Keep, drop or change anything?". Loop until they approve.

## Writing the slide copy

Load `/bitpool-design-system` before writing (step 7) — and `/bitpool-brand-guidelines` for voice. In short:

- **One headline per slide that states the takeaway**, not the topic: "Good answers start with
  good context." not "Prompting".
- **Cyan emphasis is `<strong>`** around one to three words in the headline. Never italics, never
  inline `style="color:…"` spans.
- Eyebrow: section name, plus "· 1 of 3" when a run of slides belongs together.
- Short, plain sentences. Numbers over adjectives. Australian/British spelling.
- Keep the person's own wording for steps and UI names; tighten, don't rewrite meaning.
- Card numbers are `01 02 03`; step badges are `1.0 2.0 3.0`.
