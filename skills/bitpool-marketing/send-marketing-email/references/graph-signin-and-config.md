# Graph sign-in, app registration, and troubleshooting

## App registration (already exists, don't recreate it)

Bitpool's **"CLI Email Sender"** app registration in Entra ID:

| | |
|---|---|
| Application (client) ID | `2fb3c6de-8983-4d2e-a3f7-c0964a872d63` |
| Directory (tenant) ID | `820737d5-aa31-442a-8140-9a22577361dc` |
| Platform | Mobile and desktop applications, redirect URI `http://localhost` (no port — Microsoft's endpoint allows any port at runtime for loopback redirects; the script picks a free one locally) |
| Client type | **Public client** — no client secret exists for this app type, so these two IDs are not secrets. They're hardcoded directly in `assets/send-via-graph.py`. |
| API permission | Delegated `Mail.Send`, `Mail.Send.Shared`, `Mail.ReadWrite`, and `Mail.ReadWrite.Shared` (Microsoft Graph), all with admin consent granted |
| "Allow public client flows" | **Off** — not needed for Authorization Code + PKCE via a registered redirect URI (it only governs flows *without* one, like Device Code or ROPC) |

Each non-`Mail.Send` scope is requested in the token only when actually needed (see
`send-via-graph.py`'s `main()`, scope assembly just before `interactive_login()`), so
a plain individual/batch send-as-yourself send never asks for more than `Mail.Send`:

- `Mail.Send.Shared` — only when `--send-as` is used.
- `Mail.ReadWrite` — only when any `--attach` file exceeds `SIMPLE_ATTACHMENT_BYTES`
  (3 MB), since that switches the send to the draft-message + upload-session flow,
  which needs ReadWrite rather than just the `sendMail` action.
- `Mail.ReadWrite.Shared` — only when both of the above apply (a large attachment
  **and** `--send-as`).

## Attachments — permissions and mechanism

Two Graph mechanisms, picked automatically by `send_message()` based on whether any
`--attach` file is "large" (over `SIMPLE_ATTACHMENT_BYTES`):

| | Small only (every file ≤ 3 MB) | Any large file (> 3 MB) |
|---|---|---|
| Mechanism | Single `sendMail` call, attachments embedded inline | Create draft (`POST .../messages`) → attach each file (small ones in one call, large ones via `createUploadSession` + chunked `PUT`) → `POST .../messages/{id}/send` |
| Extra scope needed | None beyond `Mail.Send`(`.Shared`) | `Mail.ReadWrite` (own mailbox) or `Mail.ReadWrite.Shared` (with `--send-as`) |
| Extra Exchange permission (Send As only) | None — "Send As" alone covers `sendMail` | **"Full Access"** on the shared mailbox — "Send As" only covers the `sendMail` action, not creating/modifying a draft message inside someone else's mailbox |

**Live-tested 2026-07-29**: a mixed send (three files under 3 MB + one ~12 MB file,
~14.9 MB combined, send-as-yourself) went through the full draft → attach → chunked
upload-session → send path in one attempt, no retries needed.

`MAX_ATTACHMENT_BYTES` (20 MB) is a safety cap on this script's side, matching
Exchange Online's typical per-message limit — not a guarantee of what any given
tenant/mailbox actually allows. If an org has it configured lower, Graph itself will
reject the send and that surfaces as a `FAILED` line with Graph's own error, not a
silent failure.

## Why PKCE, not Device Code Flow

Device Code Flow was tried first and blocked by Bitpool's tenant — Conditional
Access returned **AADSTS53003**, a deliberate policy (a "BYOD Block Windows Desktop
Apps"-style rule) blocking Device Code Flow specifically, since it's a known
phishing-vector authentication method. Conditional Access can only ever target
**resources/APIs**, never a specific public client app directly (confirmed live via
`PublicClientsAreUnsupported`, error 1034, when trying to add an app-level exclusion
to the policy) — so there was no policy exception to chase. Authorization Code + PKCE
is a different flow, not a workaround: it opens a real browser and catches the
redirect on a local loopback listener, which is the normal interactive sign-in for a
desktop app and not the transfer method the policy blocks.

## Troubleshooting sign-in errors

| Error | Meaning | Fix |
|---|---|---|
| `AADSTS53003` | Conditional Access blocked the sign-in | Expected for Device Code Flow on this tenant — this is exactly why the script uses PKCE instead. If it happens on PKCE too, a CA policy is now also blocking browser-based sign-in; that needs a real tenant-side policy change, not a client-side fix. |
| `AADSTS900144: ... must contain ... 'scope'` (or another param) | The auth URL got truncated before reaching the browser | Almost always the `cmd.exe`/`explorer.exe` shell-metacharacter truncation bug described in `open_browser()`'s docstring in `send-via-graph.py` — confirm the script is current, not an old copy. |
| `50132: SsoArtifactInvalidOrExpired` | Benign session staleness from a previous sign-in attempt | Not the real blocker if it appears alongside another error — ignore it and look at the other one. |
| `1034: PublicClientsAreUnsupported` when editing a CA policy | You tried to add this app directly to a Conditional Access policy's exclusion list | Not possible by design — CA targets resources, never a specific public client. Don't chase this further; if CA is blocking sign-in, the fix is a different auth flow (see above), not a policy exclusion. |
| `403` on a `--send-as` call | Either the signing-in user lacks Exchange "Send As" on that mailbox, or the app registration's `Mail.Send.Shared` grant/consent didn't take | Confirm in Exchange Admin Center (mailbox → Delegation → Send as) that the signed-in user is actually listed, and in Entra ID that `Mail.Send.Shared` shows **Granted** (green tick) under the app's API permissions — not just added. A permission added but never consented looks configured but still 403s. |
| Browser opens but the page hangs / never shows a login prompt, and the URL contains `sso_nonce=`/`mscrid=` params we never generated | The browser (observed with Edge) is attempting a silent "Windows SSO broker" handshake before falling back to interactive login, and that handshake is stalling | Fixed by adding `"prompt": "select_account"` to the `/authorize` request in `interactive_login()` — forces the interactive account picker immediately instead of attempting the silent broker path first. If this reappears, confirm the script still has that parameter before investigating further. |
| `400 RequestBodyRead: The property 'email' does not exist on type 'microsoft.graph.emailAddress'` | `build_email()` was building `{"email": ...}` instead of Graph's actual schema, `{"address": ...}` — a copy-paste holdover from the old SendGrid script, which does use `email` for its own API | Fixed in `build_email()`. Oddly, this didn't surface on the very first `/me/sendMail` tests (test 1/2) — only once a `"from"` object was added for `--send-as` — so treat `/me/sendMail` succeeding as evidence guard checks work, not as proof the recipient/from JSON shape is fully correct if this function gets touched again. |

## The stray browser-open bugs (already fixed, don't reintroduce)

`open_browser()` in `send-via-graph.py` tries PowerShell's `Start-Process` first, then
a properly-quoted `cmd.exe /c start` as a last resort. Two methods were deliberately
dropped after live testing surfaced real bugs — see the function's docstring for the
full detail:

- **`cmd.exe /c start` unquoted** truncated the OAuth URL at the first `&`, which is
  what produced the `AADSTS900144` error above.
- **`explorer.exe`** sometimes opened a stray Explorer window at the user's default
  library folder (e.g. their OneDrive Documents) instead of cleanly resolving the
  URL, while still separately launching the real browser tab — confusing, no upside
  over `Start-Process`.

If browser sign-in stops working again after an edit to this script, check
`open_browser()` hasn't regressed back to one of these first.

## Why every send carries `X-CodeTwoProcessed: exclude`

Bitpool's tenant has a **CodeTwo** mail-flow (transport) rule that stamps a signature
onto outbound mail, with an existing exclusion condition for messages whose
`X-CodeTwoProcessed` header equals `true`. During testing, a Graph-sent message came
through **twice** — once as sent, once re-processed by CodeTwo with its signature
appended — because the transport rule runs on all outbound mail regardless of how it
was submitted (Outlook, OWA, or Graph's `sendMail`).

The fix: every message this script sends carries
`internetMessageHeaders: [{"name": "X-CodeTwoProcessed", "value": "exclude"}]`, and
the CodeTwo rule's condition was extended to also match `exclude` as an accepted
value (not just `true`). `exclude` was chosen deliberately over reusing `true` —
these messages were never actually processed by CodeTwo, so claiming `true` would be
inaccurate; `exclude` says plainly that this is a deliberate opt-out, not a completed
pass through the tool. This message already has its own authored signature baked
into the HTML (see `campaign.md`'s Sender name/role fields upstream in
draft-marketing-email) — CodeTwo reprocessing it is what caused the duplicate, not a
gap this header creates.

If a similar duplication reappears (two copies, one with an unexpected extra
signature or footer), check for **other** mail-flow rules with the same
transport-layer stamping behaviour before assuming the script sent twice — confirm
first via the script's own output, which prints exactly one `SENT ->` line per
recipient it actually called `sendMail` for.

## Send As (shared mailbox)

By default every send goes out as whoever signs in through the browser
(`POST /me/sendMail`). Pass `--send-as <mailbox>` to send *as* a shared mailbox
instead (`POST /users/<mailbox>/sendMail`, with `from` also set explicitly on the
message). This needs two things, both already granted for `partners@bitpool.com` as
the first tested mailbox:

1. **Exchange "Send As" permission** (not "Send on Behalf Of") granted to the signing
   user on the shared mailbox — Exchange Admin Center → Recipients → Mailboxes →
   the shared mailbox → Delegation → Send as.
2. The delegated **`Mail.Send.Shared`** scope added to this app registration, in
   addition to `Mail.Send`, with admin consent granted — Entra ID → App registrations
   → CLI Email Sender → API permissions.

**Adding a new shared mailbox later** means repeating step 1 for that specific
mailbox (step 2 is already done — the scope is granted at the app level, not
per-mailbox). Verify with `--check-only --send-as <mailbox>` first; a genuine
permission gap only surfaces as a 403 during the real send (see the troubleshooting
table above), since `--check-only` never signs in or calls Graph.

**Never hardcode a shared mailbox as a default anywhere** — not in this doc, not in
the [sending workflow](campaign-email-sending.md), not as a fallback in the script. Every send that uses `--send-as` should
have that address supplied fresh by the user in the conversation, every time.
