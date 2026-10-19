# GitBook Authoring — Custom Blocks

GitBook markdown is GitHub-Flavored Markdown plus block-level tags. Matching opening and closing tags exactly is what makes or breaks rendering — an unclosed or mismatched tag (`{% endtab %}` where `{% endtabs %}` is needed) typically renders as literal text rather than failing loudly, so double-check tag names.

## Custom blocks reference

Full syntax for each block. Matching opening and closing tags exactly is what makes or breaks
rendering — an unclosed or mismatched tag (`{% endtab %}` where `{% endtabs %}` is needed)
typically renders as literal text rather than failing loudly, so double-check tag names.

### Tabs

For alternatives — different languages, platforms, or config options a reader picks between.

````markdown
{% tabs %}
{% tab title="JavaScript" %}
```javascript
const greeting = 'Hello World';
console.log(greeting);
```
{% endtab %}

{% tab title="Python" %}
```python
greeting = "Hello World"
print(greeting)
```
{% endtab %}
{% endtabs %}
````

### Stepper

For sequential, ordered processes — installs, tutorials, onboarding checklists.

```markdown
{% stepper %}
{% step %}
## First step

Complete the initial setup by installing the required dependencies.
{% endstep %}

{% step %}
## Second step

Configure your environment variables in the `.env` file.
{% endstep %}
{% endstepper %}
```

### Hints

Callouts for supplementary info, warnings, or tips. Styles: `info`, `warning`, `danger`,
`success`.

```markdown
{% hint style="info" %}
This is an informational hint with helpful context.
{% endhint %}

{% hint style="warning" %}
Be careful when running this command in production.
{% endhint %}

{% hint style="danger" %}
This action cannot be undone. Make sure you have backups.
{% endhint %}

{% hint style="success" %}
Your configuration has been saved successfully!
{% endhint %}
```

### Expandable

For optional detail that shouldn't clutter the page by default — FAQ answers, advanced config,
long logs.

````markdown
<details>
<summary>Advanced Configuration Options</summary>

Here you can find detailed information about advanced settings that most users won't need.

```yaml
advanced:
  option1: value1
  option2: value2
```
</details>
````

### Columns

Side-by-side content, **max 2 columns** — before/after, pros/cons, parallel instructions.

```markdown
{% columns %}
{% column %}
### Before

Old implementation that was inefficient.
{% endcolumn %}

{% column %}
### After

New optimized approach with better performance.
{% endcolumn %}
{% endcolumns %}
```

### Updates

For changelogs, release notes, or dated announcements — rendered in reverse chronological
order.

```markdown
{% updates format="full" %}
{% update date="2024-01-15" %}
# Version 2.0 Released

We've added new features including dark mode and improved search.
{% endupdate %}

{% update date="2024-01-01" %}
# Bug Fixes

Fixed several issues reported by the community.
{% endupdate %}
{% endupdates %}
```

### Cards

Clickable navigation cards, built as an HTML table with special attributes — good for
dashboards, feature overviews, or "explore related pages" sections.

```markdown
<table data-view="cards">
    <thead>
        <tr>
            <th>Title</th>
            <th data-card-target data-type="content-ref">Target</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Getting Started Guide</td>
            <td><a href="getting-started/quickstart.md">Quick Start</a></td>
        </tr>
        <tr>
            <td>API Reference</td>
            <td><a href="api-reference/overview.md">API Docs</a></td>
        </tr>
        <tr>
            <td>Examples</td>
            <td><a href="/spaces/abc1234/pages/jkl1121">Code Examples</a></td>
        </tr>
    </tbody>
</table>
```

### Embeds

External rich media — videos, sandboxes, tweets.

```markdown
{% embed url="https://www.youtube.com/watch?v=dQw4w9WgXcQ" %}

{% embed url="https://codepen.io/username/pen/example" %}
```

### Files

Downloadable files with a caption.

```markdown
{% file src="https://example.com/document.pdf" %}
Complete documentation in PDF format.
{% endfile %}
```

### Buttons

Call-to-action links. Styles: `primary`, `secondary`.

```markdown
<a href="https://example.com/download" class="button primary">Download Now</a>

<a href="https://docs.example.com" class="button secondary">View Documentation</a>
```

With an icon (Font Awesome name, no `fa-` prefix):

```markdown
<a href="https://github.com/user/repo" class="button primary" data-icon="github">View on GitHub</a>
```

### Icons

Inline Font Awesome icons to improve scannability of status or category text.

```markdown
<i class="fa-check">check</i> Feature enabled
<i class="fa-warning">warning</i> Requires configuration
<i class="fa-info-circle">info</i> Learn more
```

### Reusable content

Content blocks synced across multiple pages — disclaimers, CTAs, repeated instructions. These
are created in the GitBook UI (they get a generated ID) and referenced from any page:

```markdown
{% include "/reusable-content/rc12345" %}
```

They're distinct from ordinary pages — don't try to author a new one by hand-writing a
`{% include %}` pointing at an ID that doesn't exist yet.

### OpenAPI specifications

OpenAPI specs **cannot be embedded directly in markdown**. They must be uploaded first, via:

1. The [GitBook API](https://docs.gitbook.com/developers/gitbook-api/api-reference/openapi)
2. The GitBook CLI (`gitbook openapi`)
3. The GitBook UI

Only after upload can a page reference a method from it:

```markdown
{% openapi src="https://api.example.com/openapi.json" path="/users" method="get" %}
[https://api.example.com/openapi.json](https://api.example.com/openapi.json)
{% endopenapi %}
```

The `src` URL must point at an already-uploaded spec — see the
[GitBook OpenAPI docs](https://docs.gitbook.com/api-references/openapi) for more.

### Nesting markdown inside custom blocks

Standard markdown formatting works fine inside custom blocks — lists, bold/italic, inline code,
and fenced code blocks all render normally within a `{% tab %}`, `{% hint %}`, etc.:

````markdown
{% tabs %}
{% tab title="Example" %}
This tab contains markdown:

- Bullet points work
  - Nested bullets too
- **Bold text** and *italic text*
- `inline code`

```javascript
// Code blocks work too
const example = true;
```
{% endtab %}
{% endtabs %}
````

### Complete worked example

A single page combining hints, tabs, stepper, columns, and an expandable — useful as a template
for how these blocks compose:

````markdown
# API Authentication Guide

Learn how to authenticate with our API using API keys or OAuth 2.0.

{% hint style="info" %}
All API requests require authentication. Choose the method that best fits your use case.
{% endhint %}

## Authentication Methods

{% tabs %}
{% tab title="API Key" %}
The simplest authentication method. Include your API key in the request header:

```bash
curl -H "X-API-Key: your-api-key" https://api.example.com/v1/users
```

{% hint style="warning" %}
Never commit API keys to version control. Use environment variables instead.
{% endhint %}
{% endtab %}

{% tab title="OAuth 2.0" %}
More secure for user-facing applications:

{% stepper %}
{% step %}
## Register your application
Get your client ID and secret from the developer dashboard.
{% endstep %}

{% step %}
## Request authorization
Redirect users to our OAuth endpoint.
{% endstep %}

{% step %}
## Exchange code for token
Use the authorization code to get an access token.
{% endstep %}
{% endstepper %}
{% endtab %}
{% endtabs %}

## Rate Limits

{% columns %}
{% column %}
### Free Tier
1,000 requests/hour
10,000 requests/day
{% endcolumn %}

{% column %}
### Pro Tier
10,000 requests/hour
100,000 requests/day
{% endcolumn %}
{% endcolumns %}

<details>
<summary>Need higher limits?</summary>

Contact our sales team to discuss enterprise plans with custom rate limits and SLAs.
</details>

<a href="https://example.com/signup" class="button primary" data-icon="rocket">Get Started</a>
````

## Common pitfalls

- **Don't reference the same markdown file twice in `SUMMARY.md`** — each page gets exactly
  one URL, so GitBook can't resolve a duplicate.
- **Keep `SUMMARY.md` indentation as spaces, not tabs** — mixed indentation breaks the nesting.
- **If Git Sync is on, edit `README.md` only through the repo**, not the GitBook UI, or the two
  will fight over it.
- **OpenAPI specs cannot be pasted into markdown.** They must be uploaded via the GitBook API,
  CLI, or UI first; only then can a page reference them with `{% openapi %}`.
- **Tables and column layouts render awkwardly in GitBook's UI editor** — prefer `{% columns %}`
  over a raw markdown table when presenting parallel content, and reserve real tables for actual
  tabular data.
- **Always close custom blocks** and double check the tag name matches the opening tag.

## After editing

GitBook can't be rendered locally — if the repo has Git Sync configured, the only way to confirm
a block or frontmatter change actually renders correctly is to push and check the space in
GitBook itself. Say so explicitly if you can't verify rendering, rather than assuming the syntax
is correct just because it matches this reference.
