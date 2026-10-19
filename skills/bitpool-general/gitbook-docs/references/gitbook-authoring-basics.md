# GitBook Authoring — Structure & Frontmatter

GitBook spaces can be synced to a Git repo and edited as plain markdown files. This skill is a
reference for producing content that renders correctly in GitBook once it's pushed — GitBook
extends standard markdown with its own block syntax, frontmatter fields, and a navigation file
(`SUMMARY.md`) that has to stay in sync with the actual file layout.

## Orientation: read before you write

Before editing an existing GitBook-synced space, build a picture of its structure in this order:

1. **Read `SUMMARY.md` first.** It's the full table of contents — page hierarchy, groups, and
   the relative path to every page. If it doesn't exist, GitBook is inferring structure from
   the folder layout, so browse the directories instead.
2. **Check `.gitbook.yaml`.** It says where the root docs directory is, where `README.md`
   and `SUMMARY.md` live (they can be relocated), and lists any redirects.
3. **Look at `.gitbook/assets/`** for uploaded images/files and `.gitbook/vars.yaml` for
   space-level variables, if they exist.

Skipping this step is the most common way to break internal links or duplicate a page GitBook
already tracks elsewhere.

## File layout

```
/
  .gitbook/
    assets/              # GitBook-managed images and files
    includes/            # Reusable content blocks (one .md file per block)
    vars.yaml            # Space-level variables
  .gitbook.yaml          # Space configuration
  README.md              # Homepage
  SUMMARY.md             # Table of contents / nav
  getting-started/
    installation.md
    quickstart.md
```

## Which block for which need

GitBook markdown is GitHub-Flavored Markdown plus block-level tags like `{% hint %}` and
`{% tabs %}`. Pick the block by what the content needs, not by habit:

| Need                                              | Block                        |
| -------------------------------------------------- | ---------------------------- |
| Sequential, ordered instructions                   | `{% stepper %}`               |
| Alternatives (languages, platforms, options)        | `{% tabs %}`                  |
| Optional/detailed content that can stay collapsed   | `<details><summary>`          |
| Warnings, tips, callouts                            | `{% hint style="..." %}`      |
| Side-by-side comparison (max 2)                     | `{% columns %}`                |
| Changelog / dated timeline                          | `{% updates %}`                |
| Clickable navigation cards                          | `<table data-view="cards">`   |
| Downloadable file with a caption                    | `{% file %}`                   |
| Primary/secondary call-to-action link                | `<a class="button">`           |
| Content reused verbatim across pages                 | `{% include %}`                |
| Value that updates automatically                    | `<code class="expression">`    |

## Page frontmatter

YAML frontmatter at the top of a page controls SEO, visibility, variables, and layout chrome:

```markdown
---
description: Page description used for SEO and page previews
icon: book-open
hidden: true
vars:
  page_variable: value
  another_var: another value
if: visitor.claims.unsigned.isPremium
layout:
  width: default
  title:
    visible: true
  description:
    visible: true
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
  metadata:
    visible: true
---
```

- **`description`** — SEO/preview text. Multiline form:
  ```yaml
  description: >-
    This is a longer description
    that spans multiple lines
  ```
- **`icon`** — Font Awesome icon name, no `fa-` prefix (e.g. `book-open`, `bolt`, `stars`,
  `brackets-curly`).
- **`hidden: true`** — removes the page from the published TOC without deleting the file.
- **`vars`** — page-scoped variables (key-value pairs), referenced with `page.vars.name`.
- **`if`** — adaptive content visibility condition based on visitor attributes, e.g.
  `visitor.claims.unsigned.isPremium`. Prefer configuring these through the GitBook UI —
  they're more discoverable for a team there than buried in frontmatter.
- **`layout`** — maps to the "Page Options" panel in the GitBook UI:
  - `width`: `default` or `wide` (wide also widens full-width blocks like tables and code)
  - `title.visible`, `description.visible`, `tableOfContents.visible`, `outline.visible`,
    `pagination.visible`, `metadata.visible` — each a boolean

Example: a landing page with minimal chrome (no sidebar TOC, no outline, no pagination):

```yaml
layout:
  width: wide
  title:
    visible: true
  description:
    visible: true
  tableOfContents:
    visible: false
  outline:
    visible: false
  pagination:
    visible: false
```

## Variables and expressions

**Space-level variables** live in `/.gitbook/vars.yaml` as flat key-value pairs, accessed as
`space.vars.name`:

```yaml
# .gitbook/vars.yaml
food: apple
latest_version: v3.0.4
company_name: Acme Corp
```

**Page-level variables** live under `vars:` in a page's frontmatter, accessed as `page.vars.name`:

```markdown
---
vars:
  page_food: orange
  page_version: v2.1.0
---
```

Use space-level for anything referenced from more than one page; page-level for anything
specific to that page.

**Expressions** display variable values dynamically. They're plain JavaScript wrapped in
`<code class="expression">` and evaluated at render time — so they can do string concatenation,
ternaries, comparisons, whatever valid JS supports:

```markdown
<code class="expression">1 + 1</code>

<code class="expression">space.vars.latest_version</code>

<code class="expression">"My favorite food is " + space.vars.food</code>

<code class="expression">page.vars.page_food</code>

<code class="expression">space.vars.latest_version === "v3.0.4" ? "Latest" : "Outdated"</code>
```

The GitBook UI has a visual editor for variables, but they're fully editable as plain
YAML/frontmatter from the repo.

## .gitbook.yaml

Configures a GitBook space. Lives at the root of the docs directory (or in a subdirectory for
monorepos).

```yaml
root: ./

structure:
  readme: ./README.md
  summary: ./SUMMARY.md

redirects:
  old-page: new-page.md
  help: support.md
```

- `root` — root directory for the docs (default `./`)
- `structure.readme` — path to the homepage (default `./README.md`)
- `structure.summary` — path to the table of contents (default `./SUMMARY.md`)
- `redirects` — old-path → new-path map, space-specific only. For redirects that need to work
  across multiple spaces, use the GitBook UI instead — there's no file-based way to do that.

**Monorepo support:** each documentation project gets its own `.gitbook.yaml` in its
subdirectory:

```
/
  packages/
    docs/
      .gitbook.yaml
      README.md
      SUMMARY.md
    api/
      .gitbook.yaml
      README.md
      SUMMARY.md
```

When setting up Git Sync for a monorepo, point the "Project directory" setting at the
subdirectory containing that space's `.gitbook.yaml`.

All paths in `.gitbook.yaml` are relative to `root`. With Git Sync active, manage `README.md`
only through the repo — editing it in both places causes sync conflicts.

## SUMMARY.md

Defines the table of contents / sidebar navigation. It's markdown with a specific structure
GitBook parses into the nav tree.

```markdown
# Summary

## Use headings to create page groups like this one

* [First page's title](page1/README.md)
    * [Some child page](page1/page1-1.md)
    * [Some other child page](page1/page1-2.md)
* [Second page's title](page2/README.md)

## A second page group

* [Another page](another-page.md)
```

Rules:
- `#` — the document title (conventionally "Table of contents" or "Summary")
- `##` — page groups (section headers in the sidebar)
- `*` — list items, each one a markdown link to a page
- Indent with **spaces, not tabs**, to nest child pages
- Paths are relative to whatever `.gitbook.yaml` sets as the root (usually the repo root)

**Custom sidebar title**, distinct from the page's own title — put it in quotes after the path:

```markdown
* [Page main title](page.md "Page link title")
```

The quoted text is used in the sidebar, pagination buttons, and any relative links to that page —
everywhere except the page itself.

`SUMMARY.md` is optional; without it GitBook infers structure from folder hierarchy. A given
markdown file can only be referenced once — each page maps to exactly one URL. Editing through
the GitBook UI updates `SUMMARY.md` automatically; editing it by hand is exactly equivalent, so
it's safe to restructure nav purely in Git.

## The .gitbook directory

Created automatically by Git Sync to hold assets, variables, and generated content.

```
.gitbook/
  assets/          # Uploaded images and files
  includes/        # Reusable content blocks, one .md file per block
  vars.yaml        # Space-level variables
```

- **Assets** uploaded through the GitBook UI land in `.gitbook/assets/`; pages reference them
  with relative paths, e.g. `![alt](<rel>/.gitbook/assets/image-name.svg)`, where `<rel>` is `..`
  for a page one folder below the space root (`../..` for two, and so on).
- **Reusable content** blocks are each exported as their own file under `.gitbook/includes/`,
  and referenced from pages with `{% include "/reusable-content/rc12345" %}`. They're managed
  through the GitBook UI (they get a generated ID), not created by hand.
- `.gitbook/includes/` files sometimes leak into the space's visible table of contents — if that
  happens, hide them from the TOC manually.
- In monorepos, `.gitbook` is created at the root of *each* synced space, not necessarily the
  repo root.

## Standard markdown

GitBook uses GitHub Flavored Markdown as its base:

```markdown
# Heading 1
## Heading 2

**bold text**
*italic text*
`inline code`

- Bullet list item
  - Nested item

1. Numbered list
2. Second item

[Link text](https://example.com)
[Internal link](getting-started.md)
```

Code block with a title bar:

````markdown
{% code title="index.js" %}
```javascript
const foo = 'bar';
console.log(foo);
```
{% endcode %}
````

Links: external `[text](https://example.com)`, internal page `[text](page.md)` (relative path,
also works as `text (see the `/folder` skill)`), email `[text](mailto:email@example.com)`.

Math (TeX), inline and block:

```markdown
Inline formula: $$E = mc^2$$

$$
E = mc^2
$$
```
