# Building the file, checking it, handing it over

## Build

Work in a scratch folder, never next to the user's PNG. Write two files there:

- `diagram.html`: the markup that goes inside `.w-stage`. No `<html>`, `<head>`, `<style>` or
  `<script>`; the template provides all of those.
- `diagram.css`: the diagram's own positions, shapes and motion (`d-` classes, `d-` keyframes,
  selectors gated on `section.slide.on`), plus any overrides of borrowed recipes.

Then assemble with the shipped script:

```bash
python "<skill-dir>/scripts/assemble.py" --markup diagram.html --css diagram.css \
  --theme light --title "[plain title of the diagram]" \
  --recipes flow,ripple --section-classes "m-flow m-ripple" \
  --out "[folder of the PNG]/[png name]-animation.html"
```

- `--theme` is `light` or `dark`: whichever the user chose this run.
- `--recipes` and `--section-classes` only when recipe classes are used directly (see
  `motion-catalogue.md`); leave both out when every rule is adapted into `diagram.css`.
- The script inlines the Inter font, keeps only the named recipes, and refuses to write the file if
  a marker is left unfilled or anything would load from the network.
- **Output name and place:** next to the PNG, as `[png name]-animation.html`
  (`ahu-schematic.png` becomes `ahu-schematic-animation.html`). If that file already exists, ask
  before overwriting it, or add `-2`.

If Python isn't available, do what the script does by hand: copy `assets/animation-template.html`,
replace each `@@…@@` marker, paste `assets/inter-font.css` whole where `/*@@FONT@@*/` is, and paste
only the needed recipe blocks from `assets/motion-recipes.css`. Copy, don't retype.

## Check

Run every check, fix what fails, rebuild, and check again. Don't hand over a file that fails one.

1. **Script output.** No error. If building dark, no white-background warning left.
2. **Finished-state screenshot.** Render the file at 1920×1080 with a headless browser after the
   build-in has finished. On Windows:

   ```bash
   "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" --headless=new --disable-gpu \
     --hide-scrollbars --window-size=1920,1080 --virtual-time-budget=8000 \
     --screenshot="[scratch]/final.png" "file:///[path to output].html"
   ```

   Chrome takes the same flags (on Linux/macOS use `chromium`/`google-chrome` with the same flags).
   If no headless browser runs from `terminal`, open the file with the Hermes browser tools and
   capture it there. Look at the screenshot with `vision_analyze` and compare it with the PNG side
   by side.
3. **Against the inventory:** every node, label, value and connection in the inventory is on screen,
   spelled the same, in the same relative place. Nothing extra has been invented.
4. **Legibility:** no text overlaps another element, nothing is cut off at the edge of the stage or
   of its box, every label is at least 15px, and contrast holds on the chosen theme (no white text
   on a white card, no navy text on navy).
5. **Mid-build screenshot.** Take a second screenshot with `--virtual-time-budget=1200` to see the
   build-in under way. Things should be part-way in, not all present and not all missing. If it
   matches the finished screenshot exactly, the `.on` gating or the `backwards` fill is wrong.
   Judge the live loop (particles, pulses) from this shot too: a long virtual-time budget can leave
   looping particles out of the finished screenshot even when they run fine in a real browser.
6. **Motion off still shows everything.** Search `diagram.css` for any rule that sets `opacity:0` or
   `display:none` outside a `@keyframes` block. Each one would leave that element hidden when
   motion is turned off; move the hidden state into the keyframes' `from`.
7. **Self-contained.** The file opens with no network (the script checks for external URLs) and
   contains no `<img>` of the original PNG.

If no headless browser is available, say so plainly in the hand-over and list which checks you
could not run. Don't claim the file was checked visually when it wasn't.

## Hand over

Tell the user, briefly:

- the full path of the HTML file;
- light or dark, and the build-in length in seconds;
- which motion carries which part of the diagram (one line each, e.g. "particles run along the
  supply and return lines");
- how to use it: open in a browser; it fits any window; click, R or Space replays the build-in;
  with reduced motion on, or when printed, it shows the finished diagram;
- anything from the inventory you weren't sure of, and how you resolved it.

Offer one round of changes (a label, the order things arrive, a calmer or livelier loop). Edit
`diagram.html` / `diagram.css` and re-run the script, rather than hand-editing the assembled file.
