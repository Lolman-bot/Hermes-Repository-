# Search

The Bitpool predictive search is a dependency-free, on-brand typeahead — the same Google-style search built for the Support Forecast report, packaged for reuse. Type to get ranked suggestions with brand-cyan match highlighting, type-coloured chips and full keyboard control; pick one (or just keep typing) to live-filter a table or list.

It is **opinionated on purpose**: using it means every Bitpool page searches identically instead of each one inventing its own input.

> **Note**
> This page is the prose reference. The actual `bitpool-search.css`, `bitpool-search.js` and `demo.html` ship locally inside the `bitpool-search` skill's `assets/` folder and are **not** published here — code has to be byte-exact, and a synthesized answer cannot guarantee that. Edit behaviour here; edit code in the skill repo.


## Mounting it — the whole job in four steps


## Include the CSS and JS

Paste `assets/bitpool-search.css` into a `<style>` block (or `<link>` it) and `assets/bitpool-search.js` into a `<script>` block (or `<script src>`). Both are small and self-contained — no dependencies, no build step.


## Add a host element

The widget fills its host, so put the host in a flex row or give it a width.

```html
<div class="bar"><div id="searchHost"></div></div>
```


## Build the search index

One entry per searchable thing, each tagged with a `type`. Concatenate across data sources.

```js
const index = [];
projects.forEach(p => index.push({type:'project', label:p.code, meta:p.title, tag:p.won?'WON':p.prob+'%', ref:p}));
people.forEach(m   => index.push({type:'person',  label:m.name, meta:m.role,  tag:'PERSON', ref:m}));
clients.forEach(c  => index.push({type:'client',  label:c.name, meta:c.count+' projects', tag:'CLIENT', ref:c}));
```


## Mount it with two callbacks

`onInput` to live-filter, `onSelect` to jump to a result.

```js
BitpoolSearch({
  mount: '#searchHost',
  placeholder: 'Search projects, people or clients…',
  items: index,
  types: { project:{icon:'BP'}, person:{icon:'@'}, client:{icon:'C'} },
  onInput:  (q)    => filterTable(q),
  onSelect: (item) => { filterTable(item.label); flashRow(item.ref); }
});
```


That is the entire integration. `assets/demo.html` in the skill folder is a complete working end-to-end version (search → live-filtered list with the picked row highlighted) — open it in a browser and copy its wiring.

## Config reference

`BitpoolSearch(config)` mounts the search into a container element and returns a small controller object.

| Key            | Type                       | Default                | What it does                                                                                                             |
| -------------- | -------------------------- | ---------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `mount`        | selector \| Element        | — (required)           | Where to render. The component replaces the element's contents.                                                            |
| `items`        | array                      | `[]`                   | The searchable dataset. See **Item shape**.                                                                                |
| `types`        | object                     | project/person/client  | Maps `item.type` → `{icon, color}` for the left chip. Define your own types freely.                                        |
| `placeholder`  | string                     | `'Search…'`            | Input placeholder.                                                                                                         |
| `maxResults`   | number                     | `8`                    | Max suggestions shown.                                                                                                     |
| `minChars`     | number                     | `1`                    | Minimum characters before suggesting.                                                                                      |
| `searchFields` | `(item) => string[]`       | `[label, meta]`        | Which text fields to match against. The first field is treated as the "primary" for ranking.                               |
| `rank`         | `(query, item) => number`  | startsWith→includes    | Lower score ranks higher; return `Infinity` to exclude. Override for custom relevance.                                     |
| `onInput`      | `(query, item\|null) => void` | —                   | Fires on every keystroke and on select/clear. **Use this to live-filter a table or list.** `item` is set only when a suggestion was chosen. |
| `onSelect`     | `(item) => void`           | —                      | Fires when the user clicks a suggestion or presses Enter on one. Use to scroll-to / open / flash a row.                    |
| `onClear`      | `() => void`               | —                      | Fires when the clear (×) button is pressed.                                                                                |

### Item shape

```js
{
  type:  'project',                 // key into `types` → chip icon + colour
  label: 'BP-0726',                 // primary text (matched + shown bold)
  meta:  'Dexus — full-scope',      // secondary line (matched + shown muted)
  tag:   '90%',                     // right-side label (optional)
  ref:   originalObject             // anything you want back in onSelect (optional)
}
```

`label` and `meta` are the only fields searched by default. To search more — a client name, keywords — pass `searchFields`:

```js
searchFields: it => [it.label, it.meta, it.client, (it.keywords||[]).join(' ')]
```

### Returned controller

```js
const search = BitpoolSearch({ … });

search.setItems(newArray);  // swap the dataset (e.g. after a data refresh)
search.setQuery('BP-0726'); // set the box text + fire onInput
search.clear();             // empty the box, fire onClear
search.focus();             // focus the input
search.open(); search.close();
search.el;                  // { host, input, box } for advanced wiring
search.destroy();           // remove listeners + clear DOM
```

## Behaviour

- **Predictive ranking** — `startsWith` on the primary field beats a substring match on the primary, which beats a match in secondary fields.
- **Live highlight** — matched substrings are wrapped in `<mark>` (brand-cyan wash). HTML in item text is escaped first, so it is injection-safe.
- **Keyboard** — `↓`/`↑` move the active row, `Enter` selects it, `Esc` closes. Opening with `↓` from an empty-but-focused box re-runs the last query.
- **Clear + click-outside** — the × clears and refocuses; clicking anywhere outside closes the dropdown.

## Wiring patterns

A search that filters a table is two callbacks:

```js
BitpoolSearch({
  mount: '#searchHost',
  items: index,                          // [{type,label,meta,tag,ref}, …]
  types: { project:{icon:'BP'}, person:{icon:'@'}, client:{icon:'C'} },
  onInput:  (q)    => filterTable(q),    // type → narrow the rows
  onSelect: (item) => {                  // pick → jump to + flash the row
    filterTable(item.label);
    document.getElementById('table').scrollIntoView({behavior:'smooth'});
    flashRow(item.ref);
  }
});
```

For dynamic data, keep the controller and call `setItems()` after each refresh rather than remounting — remounting loses focus and the current query.

## Brand rules the widget enforces

- **Cyan match highlight, never italics.** Matched substrings get a `<mark>` with a brand-cyan wash (`rgba(0,173,239,.22)`) — the Bitpool "bold cyan replaces italics" emphasis move, applied to search.
- **Inter only** — weight 500 for the suggestion title, muted `--ink-50` for the secondary line.
- **Type chips, no emojis.** The left chip is a 1–2 character mark on a type colour (project = navy, person = cyan, client = slate by default). Define your own `types` for sites, equipment or points — short letter codes (`BP`, `@`, `C`), never emoji.
- **Hairline borders, pill input, soft-elevation dropdown**, brand focus glow — consistent with the design-system surfaces.
- **Branded scrollbar.** Once suggestions exceed the dropdown's `max-height`, the scrollbar is a thin hairline-toned bar that turns cyan on hover, in both WebKit/Blink (`::-webkit-scrollbar`) and Firefox (`scrollbar-width`/`scrollbar-color`) — never the chunky OS default.

## Theming

The CSS reads design-system tokens — `--accent`, `--bg`, `--hair`, `--ink-50`, `--text-strong`, `--sans` — with hard-coded brand fallbacks, so it looks correct both inside a full Bitpool page and on a bare one. For a full page, pair it with the Tokens (see the `/bitpool-design-system` skill) sheet so the real tokens are present.

## Anti-patterns

- Hand-rolling a search input on a Bitpool page instead of mounting this one.
- Emoji chips, or chip text longer than two characters.
- Italic emphasis on matches instead of the cyan `<mark>` wash.
- A second accent colour for the active suggestion row.
- Remounting the widget on every data refresh instead of `setItems()`.
- Suppressing the keyboard handlers — arrow/Enter/Esc navigation is part of the contract.
