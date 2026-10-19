# Sending: modes, isolation, guards, and the confirm gate

## The two modes

| | Individual (`--to`) | Batch (`--csv`) |
|---|---|---|
| Input file | `<slug>.html` (from draft-marketing-email, individual mode) | `<slug>.html` (from draft-marketing-email, batch mode — Graph batch template) |
| Recipients | A few named addresses, comma-separated | One row per recipient in a CSV |
| Personalisation | None — name is hardcoded in the draft | `{{column_name}}` tokens, filled per row |
| Unsubscribe | N/A — a personal send, not a list | Manual `mailto:` convention only — see the caveat below |
| Isolation | One Graph `sendMail` call per address | One Graph `sendMail` call per row |

**Never a shared To/Cc/Bcc list.** Every recipient — in either mode — gets their own
isolated API call with only their own address in `toRecipients`. No one ever sees
anyone else's address, and one bad address or a mid-batch failure can't affect
anyone else's copy. This is the same guarantee `send-modes.md` in
draft-marketing-email describes for the old manual `.oft`+Bcc path, just enforced
structurally here instead of by a human addressing a compose window correctly.

## Before invoking the script — always ask, never assume

Ask these every time, and check `campaign.md` for values already captured at draft
time — but **re-confirm rather than blindly reuse them**, since time may have passed
since drafting:

1. **Recipient(s) or CSV.** Individual: the address(es), comma-separated. Batch: the
   path to a CSV with an `email` column (see `assets/recipients-template.csv`) plus a
   column for every `{{token}}` the chosen template uses.
2. **Reply-To**, if different from whichever mailbox will actually sign in (or, with
   Send As, different from the shared mailbox). If it's the same, don't pass
   `--reply-to` at all.
3. **Send as yourself, or Send As a shared mailbox?** If a shared mailbox — **ask for
   the exact address fresh, every single time**, even on a second send in the same
   session. Never hardcode one, never default to the last one used, never assume from
   context (e.g. a campaign being "for Partners" doesn't mean the address is
   `partners@bitpool.com` — ask). Pass it as `--send-as <mailbox>`. See
   `graph-signin-and-config.md`'s Send As section for what has to be granted first,
   and tell the user which account needs to sign in (the one with Send As permission
   on that mailbox — not necessarily the mailbox's own account).
4. **Sender name/role in the signature.** This should already be baked into the HTML
   from drafting — not a script argument. The bracket-placeholder guard (below)
   exists specifically to catch it if it was never filled in.
5. **Anything to attach?** Check the campaign's `attachments/` folder first —
   physical files dropped there, plus any full paths recorded in
   `attachments/linked-attachments.md` for live documents the user chose to link
   rather than copy. Show the resolved list back to the user for confirmation before
   using it — don't silently trust whatever's sitting there without a review, and
   don't assume a campaign's `resources/` folder has the right file (that's drafting
   material, never an attachment). Pass each confirmed file as its own
   `--attach <path>`; the same set goes to every recipient in the send (individual or
   batch), there's no per-recipient attachment variation.

## Attachments

`--attach <path>`, repeatable. `send-via-graph.py` picks one of two Graph mechanisms
automatically depending on file size — see `graph-signin-and-config.md`'s
"Attachments — permissions and mechanism" section for the full comparison:

- **Every file ≤ 3 MB** (`SIMPLE_ATTACHMENT_BYTES`) — attached inline as base64
  `fileAttachment` objects on the single `sendMail` call, no extra scope needed.
- **Any file > 3 MB** — switches that send to the draft-message + upload-session +
  send flow, which needs `Mail.ReadWrite` (or `Mail.ReadWrite.Shared` with
  `--send-as`, plus Exchange "Full Access" on that mailbox).

Either way, combined attachment size is capped at `MAX_ATTACHMENT_BYTES` (20 MB) in
`send-via-graph.py` — a safety cap matching Exchange Online's typical per-message
limit, not a guarantee of what a given tenant/mailbox actually allows. Over that, the
script refuses to send rather than letting Graph fail the request mid-flight.
`--check-only` validates attachment paths and the size limit with no network call,
same as every other guard.

**Discovering what to attach:** check the campaign's `attachments/` folder for
physical files, and its `linked-attachments.md` for full paths to live documents
recorded there instead of being copied in — `send-via-graph.py` reads whatever path
it's given fresh at send time, so a linked file always sends its current content,
never a stale snapshot from whenever it was linked.

**`linked-attachments.md` format** — create it the first time a campaign links a
file rather than copying it in; one full path per line, an optional trailing
` — <note>` allowed:

```markdown
# Linked attachments — read fresh at send time, never copied into this folder

- C:\Users\EricSharp\Bitpool Pty Ltd\...\Deployment tracker.xlsx — pricing tab live
- C:\Users\EricSharp\SharePoint\...\Partner briefing.docx
```

Resolve each line to a plain path before passing it as `--attach` (strip the leading
`- ` and any trailing ` — note`).

## `follow-up.md` — a hard stop, checked before the script guards even run

`draft-marketing-email` logs outstanding items (a common-asset curl failure, an image
still waiting on IT, an undecided signature, anything else) to
`<year>/<slug>/follow-up.md` — see its `publishing-and-sending.md` for the
format. Check for this file at the start of every `send-marketing-email` invocation.
If it exists and has any unresolved line, stop — don't run `--check-only`, don't ask
for send details, send the user back to `draft-marketing-email` to clear it first.
This is a broader check than the script's own guards: the guards catch un-rewritten
tokens and broken template syntax mechanically, but they can't know about an image
that curled `404` or a signature nobody's decided on yet — `follow-up.md` is where
that judgment gets recorded.

## Guard checks — what the script refuses, and why

`send-via-graph.py` runs these before any network call, on the template and (in batch
mode) on every rendered row:

- **A `data:` URI image** — Bitpool email is CDN-hosted only, no base64 embedding.
- **Un-rewritten local-path tokens** (`{{CAMPAIGN_LOCAL}}`, `{{COMMON_LOCAL}}`,
  `{{COMMON_CDN}}`, `{{CAMPAIGN_CDN}}`, `sharepoint.com`, or a literal
  `email assets/`/`Common resources/` path) — means draft-marketing-email's publish
  rewrite (its Drafting a campaign email (see the `/draft-marketing-email` skill) step 7) was never run. Every recipient would get broken
  images.
- **SendGrid-only merge/unsubscribe tags** (`<%asm_group_unsubscribe_raw_url%>` etc.)
  — meaningless outside a SendGrid send, would render as broken literal text. Usually
  means the SendGrid batch template was used with this script by mistake.
- **A merge token with no matching CSV column**, or **a row with an empty value for
  a token the template uses** — refuses to send that row rather than mail out a
  literal blank or `{{token}}`.
- **A blank `email` column in any CSV row** — refuses the whole batch rather than
  silently skipping rows, since a silently-skipped recipient is easy to miss.
- **Any `{{token}}` left in an individual-mode (`--to`) template** — there's no CSV to
  fill it from, so this means a batch template was used by mistake, or `--csv` was
  meant instead of `--to`.
- **Any `[bracket]` placeholder** (`[Sender name]`, `[SUBJECT LINE]`, `[CTA URL]`,
  etc.) still present anywhere in the rendered body — the direct answer to "don't
  accidentally send out blank variables." Deliberately does **not** flag MSO
  conditional-comment syntax (`[if mso]`, `[if !mso]`, `[endif]`) that every
  production template carries — an earlier version of this guard flagged those as
  placeholders too, which would have blocked every real send. If a real template
  starts failing this guard on something that looks like `[if ...]`/`[endif]`,
  check `MSO_CONDITIONAL_RE` in `send-via-graph.py` before assuming the template
  itself is broken.

Any guard failure exits before sign-in, before any network call, and before
`--confirm` is even checked — nothing partial happens.

## `--check-only`: validate before asking for approval

Run the script with `--check-only` (no `--confirm`, no `--to`/`--csv` requirement
beyond picking one) to run every guard above with **zero sign-in and zero network
calls**. Use this to verify the template/CSV is clean *before* showing the user the
final subject/body/recipient list for approval — if `--check-only` fails, fix the
underlying issue (re-run draft-marketing-email's publish step, fix a CSV column,
fill in a placeholder) and check again, rather than surfacing a raw guard error as
the first thing the user sees.

## The confirm gate

`--confirm` must only be passed once the user has explicitly approved, in this
conversation, the exact recipient list (or CSV), subject line, and body they're about
to receive. Never pass it as a default, never to "test the pipeline," never on a
retry without re-confirming — a retry after a failure still needs a fresh yes if
anything about the send changed.

## When something fails mid-batch

The script sends recipients one at a time and doesn't stop on a single failure — it
finishes the batch, then reports `SENT ->`/`FAILED ->` per recipient and a final
`N sent, M failed` count. If there are failures:

- **Don't blindly re-run the whole batch** — that would duplicate every already-sent
  recipient's email.
- **Do** show the user exactly which addresses failed and why (the script prints the
  Graph error per failure), and only retry those specific addresses — e.g. a fresh
  `--to` call with just the failed subset, or a trimmed CSV — once the underlying
  cause is fixed.
- Interpret the failure yourself rather than mechanically retrying: a 403 usually
  means a permissions/scope issue (see `graph-signin-and-config.md`), not a transient
  fault worth just trying again. A 403 on a `--send-as` call specifically means the
  signing-in user's Exchange "Send As" grant or the app's `Mail.Send.Shared` consent
  needs checking — not that the address was mistyped.
