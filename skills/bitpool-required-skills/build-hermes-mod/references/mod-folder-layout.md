# The package folder (steps 5 and 6)

Every mod, whatever its kind, is one package folder laid out exactly like its future home in the
repo, `mods/<mod-name>/`. Load the bundled `hermes-agent` skill and its reference for the kind
(`references/desktop-plugins.md`, `tui-widgets.md`, `themes.md`, or the hooks/plugins docs it
points to) before writing code: it holds the SDK and payload details for the Hermes build that's
running. This file only fixes the layout and what each file must contain.

## Where it goes

`$HERMES_HOME/mods/<mod-name>/`. Hermes doesn't scan `mods/`, so nothing in it runs; the live files
are copies placed in step 8/10. If the folder already exists, stop and ask; never write over it.

## The layout

```
<mod-name>/
├── README.md             from templates/mod-README.md
├── docs/
│   └── flow.mmd          the approved flow chart, exactly
├── hermes-home/          the installed files, at their paths relative to $HERMES_HOME
│   └── ...               see "hermes-home per kind" below
└── tests/
    └── ...               one test file per area of the flow chart
```

No build output, `node_modules/`, `__pycache__/`, logs or secrets in the package.

## hermes-home per kind

| Kind | Files under `hermes-home/` |
|---|---|
| Desktop plugin | `desktop-plugins/<id>/plugin.js` (folder == `id`; default export `{ id, name, defaultEnabled: false, register(ctx) }`) |
| TUI widget | `tui-widgets/<id>.mjs` (default export `register(sdk)`) |
| Gateway hook | `hooks/<id>/HOOK.yaml`, `hooks/<id>/handler.py` |
| Shell hook | `agent-hooks/<id>.<ext>`; the `config.yaml` `hooks:` entry goes in the README, not as a file |
| Python plugin | `plugins/<id>/plugin.yaml`, `plugins/<id>/__init__.py` (+ `desktop/plugin.js`, `dashboard/` if any) |
| Skin | `skins/<id>.yaml` |

A two-kind mod has both sets of files. Never put a whole `config.yaml` in `hermes-home/`.

## Each file

**The code** — follow the flow chart box by box, in the same order, so the code reads like the
chart. Keep pure helpers (no SDK, no `ctx`, no I/O) apart from the code that uses them, so tests
can call them directly:
- desktop plugin: export the helpers as named exports from `plugin.js`;
- TUI widget: keep `init`, `reduce` and helpers as plain functions the test reaches through a fake
  `sdk`;
- Python: module-level functions in `handler.py` / the plugin package.

**`tests/`** — at least one test per branch of the chart (each Yes and No, each command argument).
Mock the clock, storage and network so every run gives the same result.
- Desktop plugin: copy the three files in this skill's `assets/desktop-test-kit/` into `tests/`
  with `terminal` `cp` (byte-exact), then write `tests/*.test.mjs` that import `../hermes-home/desktop-plugins/<id>/plugin.js`
  and `fakeCtx` from `./sdk-stub.mjs`. Add a named export to `sdk-stub.mjs` if the plugin imports
  one the stub lacks.
- TUI widget: `tests/*.test.mjs` building a fake `sdk` (`defineWidgetApp` that captures the app,
  `h` that returns `{ type, props, children }`), then testing `init`/`reduce`/helpers.
- Gateway hook, shell hook in Python, Python plugin: `tests/test_*.py` for `pytest`, importing the
  handler by path and calling it with synthetic `context` / kwargs.
- Skin: `tests/test_skin.py` that parses the YAML, checks every colour is `#rrggbb`, and that the
  `name` matches the file.

**`docs/flow.mmd`** — the approved Mermaid, exactly as agreed in step 4.

**`README.md`** — from `templates/mod-README.md`, every section filled in, written for the person
who'll use it. The at-a-glance table is load-bearing: `/install-mod` and `/edit-mod` read **Kind**,
**Version** (start at `1.0.0`), **Installs** (the `hermes-home/` paths) and **Switch on**.

## Keeping it in step

If a fix in step 7 or 9 changes what the mod does, update `docs/flow.mmd`, the README chart and the
tests in the same pass, and tell the user what changed in the chart.
