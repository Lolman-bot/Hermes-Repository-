# Pins and boxes on screenshots — step 8

On `steps-on-screenshot` slides, each step gets a cyan dashed box around the control and a numbered
pin beside it, matching the step's badge.

## The markup

Inside the `.shot` after the `<img>`, one pair per step:

```html
<div class="ann" style="left:38.8%;top:14.3%;width:4.7%;height:3.2%;" data-k="s07:0"></div>
<span class="pin" style="left:37.4%;top:12.1%;" data-k="s07:1">2.0</span>
```

- All four numbers are **percent of the screenshot**, not the slide.
- The box (`.ann`) wraps the control with a little breathing room.
- The pin sits on the box's top-left corner (about 1–1.5% left and up of the box) so it doesn't
  cover the control's label.
- The pin text matches the step badge exactly (`1.0`, `2.0`…).
- `data-k` must be unique across the deck: `s<slide number>:<index>`. The deck remembers dragged
  positions by this key.
- An `.ann` must be followed directly by its `.pin` — the deck deletes them as a pair.

## Finding the positions

1. If the input PowerPoint already had numbers over the screenshot, read their positions from the
   slide and convert to percent of the image. Otherwise, look at the screenshot and estimate.
2. Check: serve the draft folder (`python -m http.server 8765` via `terminal` with `background=true`)
   and open the slide with `browser_navigate` (`http://localhost:8765/<deck>-draft.html`). Use
   `browser_vision` to zoom on the screenshot and confirm every box sits on its control. Adjust and
   recheck. Don't paste the deck's data into the browser — load the served file.
3. Tell the person that in the finished deck they can drag any pin or box, resize boxes from the
   corners, and delete one with the × — but dragged positions are saved only in their browser until
   they press **Save HTML**.
