---
name: bitpool-search
description: "Use when a Bitpool page needs a search or typeahead box."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, search, typeahead, autocomplete, component, javascript]
    category: bitpool
    related_skills: [bitpool-design-system]
---

# Bitpool Search

A drop-in, dependency-free predictive search widget in the Bitpool design language. It's the Google-style search built for the Support Forecast report, packaged for reuse. Type to get ranked suggestions with brand-cyan match highlighting, type-coloured icon chips and full keyboard control. Pick a suggestion, or just keep typing, to live-filter a table or list. It is opinionated on purpose, so every Bitpool page searches the same way instead of each one inventing its own input.

## When to Use

- A Bitpool page, dashboard, report or internal tool needs a search bar, predictive/typeahead search, autocomplete, an omnibox, a quick-find or a live filter box.
- The user says "add a search", "make it searchable", "Google-style search", "autocomplete", "typeahead", "filter as I type" or "search bar" in any Bitpool context.
- You're building a Bitpool page with a list, table or directory (projects, people, clients, sites, equipment, points) that users will want to find things in quickly.

Don't use for:
- Search in a non-Bitpool product.
- Server-side or full-text search back ends: this is a client-side widget over an in-page index.

## Procedure

1. **Copy the assets** into the page's folder with `terminal` (`cp`): `assets/bitpool-search.js` and `assets/bitpool-search.css`. Never reconstruct them from prose; these files are the component. Done when both files exist beside the page.
2. **Read `references/search.md`** sections for mounting, config, item shape and wiring patterns before writing the integration. Done when every config key you use appears in that file.
3. **Build the index.** Every item is `{type, label, meta, tag, ref}`. Done when each data source maps to that shape.
4. **Mount it.** Call `BitpoolSearch({mount, items, types, onInput, onSelect})` on a host element that sits in a flex row or has a width. Done when typing shows ranked suggestions.
5. **Wire the filter** (table or list) following the wiring patterns in `references/search.md`. Done when picking a suggestion highlights the row and typing live-filters.
6. **For a full page**, load `/bitpool-design-system` so the real brand tokens are present.
7. **Deliver.** Give the path in a terminal session. On a messaging platform, attach the HTML and assets with `MEDIA:/absolute/path`. `assets/demo.html` is a complete working example to compare against.

## Load-bearing rules

1. **Mount, don't rebuild.** Never hand-roll a Bitpool search input.
2. **Every item is `{type, label, meta, tag, ref}`.** `label` is the bold primary line, `meta` the muted secondary line, `tag` the right-hand label, and `ref` whatever object you want handed back on select.
3. **Cyan match highlight, never italics.** Matched substrings get a `<mark>` with the brand-cyan wash.
4. **Type chips, no emojis.** Use 1–2 character letter marks (`BP`, `@`, `C`) on a type colour.
5. **Keyboard is part of the contract.** `↓`/`↑` move, `Enter` selects, `Esc` closes. Don't suppress it.
6. **Token-aware with fallbacks.** The CSS reads `--accent`, `--bg`, `--hair`, `--ink-50`, `--text-strong` and `--sans`, and falls back to built-in brand values on a bare page.

## Pitfalls

- **Guessing the API.** If a config key or callback isn't in `references/search.md`, it doesn't exist. Don't invent one from memory.
- **Host element with no width.** The widget collapses unless its mount sits in a flex row or has an explicit width.
- **Editing the JS without the docs.** When changing `assets/bitpool-search.js` or `.css`, update `references/search.md` in the same change so they don't drift.

## Verification

- `bitpool-search.js` and `.css` in the output are byte-identical to the shipped assets (or deliberately edited, with the reference updated).
- Typing shows ranked suggestions with cyan highlights. `↓`/`↑`/`Enter`/`Esc` work. The clear button resets.
- Selecting a suggestion triggers `onSelect` with the item's `ref`, and the table or list filters.
- No emojis in type chips.

## Reference files

| File | Covers |
|---|---|
| `references/search.md` | Mounting (four steps), config reference, item shape, the controller API, behaviour (ranking, highlighting, keyboard), wiring patterns, brand rules |

Assets: `assets/bitpool-search.js` (the component), `assets/bitpool-search.css` (styling), `assets/demo.html` (working example).
