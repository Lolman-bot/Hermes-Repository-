# The process canvas (steps 3 and 4)

The person draws how the work gets from the inputs to the outputs. It's point-and-click: they add
boxes, name them, pick a shape (Step, Question, Start or end), and join them with labelled links.
Nobody types Mermaid.

## Seeding the canvas

Never open it blank. From the examples (or their descriptions), draft a short starting outline,
usually three to six boxes, from "the input arrives" to "the output is sent", and load it as the
seed. Tell the person plainly:

> "I've started it off with my guess from your examples. It's only a starting point: rename, add,
> delete or rewire anything. The steps need to be yours."

Write the seed with `write_file` to `$HERMES_HOME/build-skill/<skill-name>/seed.json`, in this shape:

```json
{"nodes":[{"id":"n1","label":"Energy export arrives","shape":"round"},
          {"id":"n2","label":"Check for missing days","shape":"decision"}],
 "links":[{"from":"n1","to":"n2","label":""}]}
```

`shape` is `box`, `decision` or `round`. Ids are `n1`, `n2`, ... Keep labels short and in the
person's words where they used any.

`<skill-dir>` below is this skill's installed folder, usually
`$HERMES_HOME/skills/bitpool/build-skill-from-examples/`; `skill_view` shows where it loaded from.
Use `python3` instead of `python` where that's the only name on the machine.

## Which mode

Ask yourself one question: **is the person at the machine Hermes runs on?**

- CLI, TUI or desktop app on their own computer → **served mode**.
- A messaging app (Telegram, Discord, Slack, ...), the web dashboard from another device, or Hermes
  on a remote server → **standalone mode**. A `127.0.0.1` link would point at *their* device and
  fail.

If unsure, ask with `clarify`: "Are you on the same computer Hermes is running on?"

### Served mode — local page, submit straight to a file

1. Start the server with `terminal`, **in the background** (`background=true`):

   ```bash
   python <skill-dir>/scripts/canvas_server.py \
     --seed "$HERMES_HOME/build-skill/<skill-name>/seed.json" \
     --out  "$HERMES_HOME/build-skill/<skill-name>/process.mmd" --open
   ```

   It prints `Canvas ready: http://127.0.0.1:<port>/` (read it with `process_manage`). It serves
   `assets/process-canvas.html` and the bundled Mermaid, listens only on this machine, and stops by
   itself once a diagram is submitted (or after 60 minutes). `--open` opens the page in the default
   browser; if it can't, it says so.
2. Give the person the link anyway and say: "Open this in your browser if it didn't open by itself,
   build the diagram, press **Submit diagram**, then come back and tell me you're done." In the
   desktop app the link is clickable. On WSL, the Windows browser reaches the link as-is.
3. When they say done, `read_file` the `process.mmd`. If it isn't there, check the server's output
   for an error before asking them to try again.

### Standalone mode — one self-contained file, sent as an attachment

1. Build the file with `terminal` (it exits straight away):

   ```bash
   python <skill-dir>/scripts/canvas_server.py \
     --seed "$HERMES_HOME/build-skill/<skill-name>/seed.json" \
     --standalone "$HERMES_HOME/build-skill/<skill-name>/canvas.html"
   ```

   Mermaid and the seed are inlined, so the file works offline in any browser (about 3.3 MB).
2. Send it: on a messaging platform, put `MEDIA:<absolute path to canvas.html>` in your reply so it
   arrives as a file attachment. Say: "Open this file in your browser, build the diagram, then
   press **Copy diagram** and paste it here, or **Download diagram** and send me the file."
3. The pasted Mermaid block (or the attached `process.mmd`) is the diagram. Move to step 4.

There is no inline-in-chat canvas: Hermes has no widget surface that can post a diagram back into
the chat by itself, so away from the Hermes machine the round trip goes through copy/paste or a file.

### Fallback — anywhere

If the canvas won't load, won't let them type, or Submit doesn't come through, every mode has
**Copy diagram**: ask them to press it and paste the result into the chat. If even that fails, a
photo or screenshot of a hand-drawn or Obsidian diagram is fine: read it with `vision_analyze` and
do step 4 from that.

## Step 4 — reading the diagram back

Say every box and every link back in plain words, in order, numbered. Then flag, by name, anything
that doesn't add up:

- **A question with one answer** — a Question box with only a "Yes" path, or no labels at all.
- **A link from the wrong box** — e.g. a "No" label on a link leaving a Step, not the Question.
- **Duplicate links** — the same two boxes joined twice.
- **Dead ends** — a box with nothing after it that isn't the end of the job.
- **Floating boxes** — a box nothing links to or from.
- **Placeholder names** — "New step", "test", "hello hello", or anything that isn't a real step.
- **Gaps against the examples** — an output in the examples that no box produces.

Ask about each one; don't fix it silently (load-bearing rule 2). If they change the diagram, read it
back again. Move to step 5 only on an explicit yes.
