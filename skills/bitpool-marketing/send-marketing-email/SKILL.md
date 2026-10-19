---
name: send-marketing-email
description: "Use when sending a drafted Bitpool campaign via Graph."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, marketing, email, campaign, microsoft-graph, send]
    category: bitpool
    related_skills: [draft-marketing-email, bitpool-brand-guidelines]
---

# Send Marketing Email

Sends a campaign email `/draft-marketing-email` already built, verified and published, **via Microsoft Graph** (`POST /me/sendMail`), not Outlook. Outlook re-renders HTML through Word's engine on every send path, which mangles styling unpredictably — a pure REST call to Exchange Online never touches that engine, so the authored HTML arrives exactly as built.

Sign-in is **delegated** (a real person signs in via a real browser, Authorization Code + PKCE) — never an application/client-credentials permission, and there is no client secret anywhere. Individual and CSV-batch modes, one isolated send per address. The script refuses to send with local-path tokens, SendGrid-only tags, or unfilled placeholders, and can send as a shared mailbox — always asked fresh, never assumed.

## When to Use

- `/send-marketing-email`, or requests to send/mail a Bitpool campaign email that `/draft-marketing-email` produced and published (`<slug>-cdn.html`).
- Individual sends to a few named recipients, or a Graph-CSV batch to a smaller, already-informed list (customers, partners, event registrants).

Don't use for:
- Drafting the email: use `/draft-marketing-email`.
- A bulk/uninformed list send that needs real unsubscribe suppression: that stays a manual SendGrid upload, unchanged.
- Anything outside Bitpool marketing email.

## Prerequisites

- Hermes `terminal`, `read_file`, `search_files`, `clarify`.
- **Windows:** WSL with the standard `Ubuntu` distro, a created Ubuntu user, and `python3-requests` — the four-tier check in `references/environment-setup.md` (run via `wsl.exe` from `terminal`). Native Windows Python is not used. **Linux/macOS:** `python3` with `requests`.
- Bitpool's "CLI Email Sender" Entra app registration with delegated `Mail.Send` (plus `Mail.Send.Shared` / `Mail.ReadWrite` scopes where needed) — see `references/graph-signin-and-config.md`.

## Procedure

1. **Environment check — every invocation.** Work the four tiers in `references/environment-setup.md` in order, stopping at the first failure and handing that step to the user with the exact command. Done when all four tiers pass.
2. **Read the method.** `read_file` `references/campaign-email-sending.md` and `references/sending-and-guards.md` in full; `references/graph-signin-and-config.md` whenever anything auth-related comes up. Done when the first two are read this run.
3. **Confirm the input is the published file.** `--html-file` is `<year>/<slug>/<slug>-cdn.html`; `campaign.md` shows asset verification done; `follow-up.md` (if present) has no unresolved item. Otherwise stop and send the user back to `/draft-marketing-email` steps 6–7. Done when all three hold.
4. **Choose the mode** — Individual (`--to`) or Batch (`--csv`, shape per `assets/recipients-template.csv`) — with `clarify`. Done when the user picks.
5. **Gather send details — ask every time.** Recipients or CSV path, Reply-To, which mailbox signs in, whether to **Send As** a shared mailbox and *which one* (fresh, every send), attachments (check the campaign's `attachments/` folder and `linked-attachments.md`, show the resolved list back), and confirmation the signature/name fields were filled. Done when every answer came from the user in this conversation.
6. **Validate with `--check-only`** (zero sign-in, zero network): e.g. `wsl -e bash -lc 'python3 -u "<path>/send-via-graph.py" --check-only --subject "<subject>" --html-file "<path>/<slug>-cdn.html" --to "<addr1>, <addr2>"'` (on Linux/macOS run `python3 -u assets/send-via-graph.py ...` directly). Fix anything flagged and re-check. Done when it reports ready.
7. **Get explicit approval.** Show the exact subject, recipient list (or CSV + template), Send-As mailbox and attachments, and get a fresh, explicit yes for that exact send. Done when the user says yes in this conversation.
8. **Send** — the same command plus `--confirm` (and `--send-as "<mailbox>"` if chosen). The user signs in themselves in the browser; relay the identity and From mailbox the script prints before sending. Done when the script finishes.
9. **Report results** — relay `SENT ->` / `FAILED ->` per address and the final count. On failures, list exactly which addresses failed and why; retry only that subset, only after the cause is understood and with a fresh yes. Done when the user has the per-address outcome.

## The send guards

These are the reason this skill is safe to run. They apply in full, every run, whether or not the references were read.

1. **Never pass `--confirm` without a fresh, explicit yes from the user in this conversation, for that exact send.** Not to test the pipeline, and not on a retry if anything changed.
2. **Always run `--check-only` first.** It runs every guard with zero sign-in and zero network calls. Don't let a raw guard error be the first thing the user sees after they've already approved.
3. **`--html-file` must be the published `<slug>-cdn.html`**, never the local `<slug>.html` draft. If asset verification hasn't happened, send the user back to `/draft-marketing-email` steps 6–7.
4. **An existing `follow-up.md` with any unresolved item is a hard stop.**
5. **Always ask which mailbox to `--send-as`, every single time** — never hardcode, never default to the last one used, never assume from context, even on a second send in the same session.
6. **The user signs in themselves.** The agent never sees or enters credentials (never via `browser_vault` or typing either). Relay the identity the script prints before the send so the From address is confirmed, not assumed.
7. **Never attempt WSL install, Ubuntu first-launch setup, or a `sudo apt` step yourself** — all three need the user's own hands.
8. **After a partial batch failure, never re-run the whole batch** — that duplicates every already-sent recipient. Retry only the addresses that actually failed, once the cause is understood.
9. **Never use `graph-batch-template.html` for a genuine bulk/uninformed list** that needs real unsubscribe suppression — that's SendGrid's job.
10. **Run the shipped script; never reconstruct it.** `assets/send-via-graph.py` is what enforces these guards. If a guard changes in the script, change it in this list too — this list is the copy that always applies.

## Pitfalls

- **Native Windows Python** — the `python`/`python3` stubs there are broken; run in WSL Ubuntu (`references/environment-setup.md`).
- **Windows → WSL paths** — a Windows drive path becomes `/mnt/<drive-letter-lowercase>/...` with forward slashes (`references/environment-setup.md`); quote paths with spaces.
- **Device Code Flow** — blocked by Bitpool's Conditional Access (AADSTS53003); the script uses PKCE on purpose. AADSTS troubleshooting is in `references/graph-signin-and-config.md`.
- **403 on Send As** — missing Exchange "Send As" or `Mail.Send.Shared`, or the wrong mailbox.
- **Attachments over 3 MB** switch to the draft + upload-session flow and need `Mail.ReadWrite` (and `.Shared` + Full Access with `--send-as`); combined cap 20 MB.
- **Pulling attachments from `resources/`** — that's drafting material, not attachments.

## Verification

- All four environment tiers passed this run (Windows).
- `--check-only` passed before approval was requested.
- The user gave an explicit yes for this exact send; the printed sign-in identity / From mailbox was relayed.
- Per-address results were reported; any retry covered only failed addresses.

## Reference files

Read the file itself — the table is an index, not a substitute.

| File | Covers |
|---|---|
| `references/campaign-email-sending.md` | The full send workflow — the WSL environment gate, confirming the published file, choosing a mode, gathering details, the check-only pass, explicit approval, and reporting results. |
| `references/environment-setup.md` | The four-tier WSL / Ubuntu / Python setup check, with the exact hand-off command for each tier. |
| `references/graph-signin-and-config.md` | App registration details, why PKCE rather than Device Code Flow, AADSTS troubleshooting, and Send As setup. |
| `references/sending-and-guards.md` | Individual versus batch in full, recipient isolation, every guard check and why, and the check-only/confirm discipline. |
| `assets/send-via-graph.py` | The send script — guards, PKCE sign-in, per-recipient send. |
| `assets/recipients-template.csv` | Example CSV shape for batch mode (`email` column required, plus one column per `{{merge}}` token). |

Workflow, environment tiers, auth config and the guard reference are edited in `references/`; the script and CSV template in `assets/`.
