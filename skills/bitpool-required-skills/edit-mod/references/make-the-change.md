# Make the change (steps 3 to 7)

## Step 3 — what to change

Ask in plain words: "What do you want the mod to do differently?" Don't take the first vague
answer. Push until you can state the change as a **before** and an **after**:

- *"It's wrong when..."* → what happened, and what should have happened instead?
- *"Add a..."* → when does it show or happen, on which surface (desktop, TUI, CLI, messaging), and
  does it need a new command or argument?
- *"It's slow / in the way"* → which event or draw, and what would "fine" look like?
- *"Change how it looks"* → which surface, and what should it look like instead?

Never invent behaviour the user didn't ask for. If one extra seems obviously useful, suggest it and
let them decide. Read the relevant part of `docs/flow.mmd` (or the README chart) back so you both
start from the same picture.

If the change needs a different kind (e.g. a gateway hook should now also work in the CLI, which
needs a shell or plugin hook), say so: it adds a part to the mod, and the README's **Kind**,
**Installs** and **Switch on** rows change with it.

## Step 4 — does the flow chart change?

| The change | Flow chart |
|---|---|
| New event, decision, command, argument, or anything it shows, saves, sends or says | Changes. Do it first. |
| Something it did is removed | Changes. Do it first. |
| A fix that makes the mod do what the chart already says | Stays. Say so and skip to step 5. |
| Looks only (colours, wording, spacing) with the same steps | Usually stays. Check the end-node labels still read true. |

When it changes: edit the Mermaid, show the whole chart in a ```mermaid block, then **read back only
what changed**, numbered, in plain words. Check and flag by name, the same checks
`/build-hermes-mod` runs: a decision with only one labelled way out, a box nothing leads to, a step
with nothing after it that isn't a visible result, something asked for that no box does, something
nobody asked for, and a start event the mod's kind never receives (`mod-kinds.md`). Ask "Is this
what the mod should do now?" and loop until an explicit yes.

## Step 5 — make the change

Load the bundled `hermes-agent` skill (`skill_view(name='hermes-agent')`) and its reference for the
mod's kind first. Then edit **the package**, never the live copy.

**Keep the layout.** Same files in the same places: `README.md`, `docs/flow.mmd`, `hermes-home/...`,
`tests/`. Don't rename files or add folders the layout doesn't have.

| File | What to do |
|---|---|
| The code under `hermes-home/` | The edit itself. Keep it in the chart's order, and pure helpers apart from SDK / `ctx` / I/O code so tests can call them. |
| `tests/` | One test per new or changed branch of the chart. Mock the clock, storage and network. Remove a test only when the agreed chart says that behaviour is gone. Desktop plugins keep the stub kit (`register-sdk-stub.mjs`, `sdk-loader.mjs`, `sdk-stub.mjs`); add a stub export if the plugin now imports a new name. |
| `docs/flow.mmd` | The agreed chart, exactly. |
| `README.md` | The same chart in **How it works**; **How it looks**, **Use**, **Privacy**, **Install**, **Uninstall** if they changed; **Built and tested on** to the `hermes --version` from step 6. |
| README **Version** | Bump: patch (`1.0.0` → `1.0.1`) for a fix, minor (`1.0.0` → `1.1.0`) for new or changed behaviour, major only if the user agrees it breaks how people use it. A Python plugin's `plugin.yaml` `version` moves with it. |

## Step 6 — tests and checks

Run the kind's tests and Hermes checks from `mod-kinds.md` in the package folder (e.g.
`node --import ./tests/register-sdk-stub.mjs --test "tests/*.test.mjs"`, `python -m pytest tests`,
`hermes plugins doctor hermes-home/plugins/<id> --ci`). All must pass. If one fails, read the whole
output, fix the cause in the mod (the test is wrong only if it disagrees with the agreed chart),
and run all again. No failing or skipped tests. Show the user the passing output, briefly.

## Step 7 — sync and the user's check

**Sync.** Warn once that the mod is live: copy each changed file under `hermes-home/` over its live
copy under `$HERMES_HOME` (desktop plugins: the root Hermes home), in one pass. Add new files the
README's **Installs** now lists; remove live files the change dropped. Then make it reload:

| Kind | Reload |
|---|---|
| Desktop plugin | Hot-reloads on save. Plugin package with a `desktop/` half: **Rescan** in Capabilities → Plugins. |
| TUI widget | Hot-reloads; `/widgets-reload`, then `/<id>` to remount. |
| Gateway hook | `hermes gateway restart`. |
| Shell hook | Next session; if the command line changed, approve the new consent prompt. |
| Python plugin | Next session (`/plugins` to confirm it loaded). |
| Skin | Repaints within a second if it's the active skin. |

If the mod isn't switched on, use the kind's trial from `mod-kinds.md` instead.

Tell the user, from the chart, what to look for, what to type and what should happen; list each
command. Ask: "Does it work the way you wanted?" If not, find out what's wrong, back to step 5 (and
step 4 if behaviour changes), then step 6 and 7 again. Only an explicit yes moves on.
