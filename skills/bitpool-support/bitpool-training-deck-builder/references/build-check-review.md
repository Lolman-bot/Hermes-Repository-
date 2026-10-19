# Build, check and review — steps 7, 9, 10 and 11

## Step 7 — building

1. Copy `assets/deck-template.html` to `<deck-name>-draft.html` in the working folder, next to the
   `media/` folder from intake. Name: `bitpool-<topic>-training.html` unless the person names it.
2. Replace `__DECK_TITLE__`, `__KICKER__` (top-corner label) and `__FOOTER__` everywhere.
3. Delete the template's placeholder slides and build the approved outline by copying layout
   sections (see `slide-layouts.md`). Point `src` at `media/…` files while drafting.
4. Set each slide's `data-t` (its name in the navigator) and its footer number `01, 02…` in order.
   Set `<span id="tot">` to the slide count.
5. A screen recording goes in a `.shot` as
   `<video src="media/x.mp4" autoplay loop muted playsinline data-rate="1"></video>` — raise
   `data-rate` (e.g. 3) to speed up a long recording, and say so in the caption.
6. Visual layouts carry sample copy from the example deck. Replace every word, keep the item count
   the layout table gives, and set `--n` on any typed title to its character count.
7. Leave the `<style>` and every `<script>` block exactly as they are in the template. They carry the
   navigation, Edit, Save HTML, PDF, the reveal animation, the draggable pins, the `.on` marker that
   replays each visual slide's motion, and the cube favicon.

Then compare the draft with `assets/example-deck.html`, side by side. It should read as the same
family: a visual or dark slide every few slides, a takeaway headline on every slide, and not page
after page of plain cards.

## Step 9 — checks (every run)

Serve the draft folder (`python -m http.server 8765` via `terminal` with `background=true`) and open
it with `browser_navigate` at 1440×810 (a laptop) — not only at 1920×1080. Set the size with
`browser_cdp` `Emulation.setDeviceMetricsOverride` when a CDP endpoint is attached, or the Browser
Use CLI tool (`browser_exec`); if neither can resize, render each size with Playwright from a script.
A cloud browser backend can't reach `localhost` — use the local browser for these checks. Then:

- **Fits:** run this on the page (`browser_console` with `expression=`); it must return an empty list.
  If the evaluator rejects top-level `await`, run the first line, wait two seconds, then the rest.

  ```js
  document.querySelectorAll('section.slide').forEach(s=>s.classList.add('in'));
  await new Promise(r=>setTimeout(r,1700));   // let the reveal animation finish
  [...document.querySelectorAll('section.slide')].flatMap((s,i)=>{
    const r=s.getBoundingClientRect();
    return [...s.querySelectorAll('*')].filter(e=>{const b=e.getBoundingClientRect();
      return b.width&&(b.bottom>r.bottom+1||b.right>r.right+1||b.top<r.top-1);})
      .slice(0,1).map(e=>`slide ${i+1}: ${e.tagName}.${e.className}`);})
  ```

  (Pins may sit just outside a screenshot; that's fine. Anything else listed means content overflows
  — split the slide.)
- **Every image and video shows:** `[...document.images].filter(i=>!i.naturalWidth)` must be empty,
  and every `<video>` must have `readyState > 0`.
- **Counter and navigator:** the counter shows the right total; ☰ lists every slide by name.
- **No sample copy left:** search the draft for text from the template's sample slides ("Learn
  Claude", "Bitpool AI Training", "Point one", "Card title") — none of it may remain unless this deck
  really is that one.
- **Look at every slide** (arrow through with `browser_press` `ArrowRight`, `browser_vision` on each). Check the cyan words, the
  pins, and that nothing overlaps the footer or the control bar. Check visual layouts in their
  finished state by turning on **Edit** first: it switches the motion off, and a headless browser
  doesn't always run the animations, so a slide mid-animation can look empty when it isn't.

Fix anything that fails and check again before showing the person.

## Step 10 — review

Embed the media (below) into a review copy and hand it over for review: give the path in a terminal
session, or attach it as `MEDIA:/absolute/path/<deck>-review.html` on a messaging platform. Ask:
"Anything to change — wording, order, images, pin positions?" Make the changes in the draft, go back
to step 9, and show it again. Keep looping until they say it's done.

## Step 11 — hand over

```bash
python <skill-dir>/scripts/embed_media.py <deck>-draft.html <deck>.html
```

This inlines every image and video so the deck is one file that works offline (Inter is embedded in
the template, so it shows correctly offline too). It stops if any media file is
missing. Give the person the final `.html`, its size, and a one-line reminder of the controls:
arrows or ☰ to move, **Edit** to change text, **Save HTML** to keep edits, **PDF** to print. Above
about 50 MB, warn them it may be slow to email and offer to compress the videos.
