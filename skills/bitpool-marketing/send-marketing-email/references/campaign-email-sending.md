# Sending a campaign email

Sends a campaign email that drafting already built, verified and published (`<slug>-cdn.html`).

**Sends via Microsoft Graph** (`POST /me/sendMail`), not Outlook. Outlook re-renders HTML through Word's engine on every send path (compose, forward, `.eml`→`.oft`), which mangles styling unpredictably — a pure REST call to Exchange Online never touches that engine, so the authored HTML arrives exactly as built. Sign-in is **delegated** (a real person signs in via a real browser) — never an application permission, and there is no client secret anywhere. See [Graph sign-in and config](graph-signin-and-config.md).

> **Important**
> **Never pass `--confirm` without a fresh, explicit yes from the user for that exact send** — not to "test the pipeline", and not on a retry if anything about the send changed. These guards are the load-bearing part of this workflow and are also kept locally in the skill, so they apply whether or not this page was fetched.


> **Note**
> `assets/send-via-graph.py` and `assets/recipients-template.csv` ship locally with the `send-marketing-email` skill. This page is the method; those files are the machinery.


## 0. Environment check — every invocation, before anything else

This runs in **WSL Ubuntu**, not native Windows Python. Work through the four tiers in [Environment setup](environment-setup.md), in order, stopping at the first one that fails:

1. Is WSL itself installed?
2. Is the standard `Ubuntu` distro installed?
3. Has the Ubuntu user account actually been created (first-launch setup)?
4. Is `python3` with `requests` importable ready?

**Tiers 1–3 are Windows-feature or credential-creation steps — hand them to the user with the exact command, and never attempt them yourself, even if you technically could.** Tier 4 needs `sudo` the first time (installing the `python3-requests` apt package — no venv needed, see [Environment setup](environment-setup.md) for why) — same rule, hand it over. Once Tier 4's package is installed, later invocations should find it already there.

Don't proceed to step 1 until all four tiers pass.

## 1. Confirm the input file is the published one

The `--html-file` argument must be the **published** artifact — `<year>/<slug>/<slug>-cdn.html`, with every image already verified live on the CDN (drafting (see the `/draft-marketing-email` skill) step 7).

**Never point this at the local `<slug>.html` draft** — it still has local `email assets/`/`Common resources/` paths that only resolve on the machine that drafted it, and every recipient would get broken images. The script's guard checks catch this automatically, but confirm it yourself first so a guard failure isn't the user's first surprise.

If asset verification hasn't actually happened yet (check `campaign.md`'s checklist), stop and send the user back to finish drafting (see the `/draft-marketing-email` skill) steps 6–7 first.

**Also check for a `follow-up.md` in the campaign folder.** If it exists and has any unresolved item, that's a hard stop — same weight as an un-rewritten local-path token. Tell the user exactly what's outstanding and send them back to drafting; don't proceed on the assumption an item is probably fine by now.

## 2. Choose the mode

Ask (state a recommendation if the context clearly fits one):

- **Individual** (`--to`) — a few named recipients, no CSV, no merge tokens. Built from `individual-template.html`.
- **Batch** (`--csv`) — a list, one row per recipient, `{{merge}}` tokens filled per row. Built from `graph-batch-template.html`. **Not for a genuine bulk/uninformed marketing blast** — that still needs SendGrid's real unsubscribe-suppression behaviour, which Graph batch doesn't have. Graph batch is the right call for smaller, already-informed lists: existing customers, partners, event registrants.

Full mode comparison, isolation model, and every guard check in [Sending and guards](sending-and-guards.md) — read it before gathering details in step 3.

## 3. Gather send details — ask every time, don't assume

See [Sending and guards](sending-and-guards.md) for the full list and reasoning. In short: recipients or CSV path, Reply-To (only if different from whoever signs in), which mailbox needs to do the signing in, whether this sends as that signed-in mailbox or **Send As** a shared mailbox (and if so, which one — ask fresh every time, never reuse a previous answer), whether anything needs attaching, and a plain confirmation that the signature/name fields were actually filled in during drafting.

**Attachments (`--attach <path>`, repeatable):** the same file(s) go to every recipient — there's no per-recipient variation. Combined size is capped at 20 MB; any single file over 3 MB automatically switches that send to Graph's draft + upload-session flow (needs `Mail.ReadWrite`, and `Mail.ReadWrite.Shared` + Exchange "Full Access" with `--send-as` — see [Graph sign-in and config](graph-signin-and-config.md)).

**Check the campaign's `attachments/` folder first** — physical files, plus any full paths recorded in `attachments/linked-attachments.md` — rather than asking the user to dictate paths from scratch. Always show the resolved file list back to them for confirmation before passing anything as `--attach`. Never pull from a campaign's `resources/` folder — that's drafting material, not attachments. If the user names a new file that isn't staged yet, offer to record it: a physical copy into `attachments/`, or its full path appended to `linked-attachments.md` if it's a live document they'd rather link than snapshot.

## 4. Validate first — `--check-only`

Run the script with `--check-only` before asking for final approval. It runs every guard check with **zero sign-in and zero network calls** and reports readiness. Fix anything it flags (re-run the publish step, fix a CSV column, fill in a placeholder) and re-check — don't let a raw guard error be the first thing the user sees after they've already said yes.

```bash
wsl -e bash -lc 'python3 -u "<path>/send-via-graph.py" --check-only --subject "<subject>" --html-file "<path>/<slug>-cdn.html" --to "<addr1>, <addr2>"'
```

Swap `--to "..."` for `--csv "<path>/recipients.csv"` in batch mode; add `--attach "<path>"` once per file if anything needs attaching.

## 5. Get explicit approval, then send

Show the user the exact subject, recipient list (or CSV plus template), and — if they want it — the rendered body, and get an explicit yes **in this conversation** before adding `--confirm`.

```bash
wsl -e bash -lc 'python3 -u "<path>/send-via-graph.py" --subject "<subject>" --html-file "<path>/<slug>-cdn.html" --to "<addr1>, <addr2>" --confirm'
```

Add `--send-as "<mailbox>"` to send as a shared mailbox instead of whoever signs in.

A browser opens for sign-in — **the user signs in themselves**; the agent never sees or enters credentials. Once signed in, the script prints who it signed in as, and — with `--send-as` — which mailbox the message will actually go out as, before sending. Relay that to the user so the From identity is confirmed, not assumed.

## 6. Report results

The script sends one recipient at a time and reports `SENT ->`/`FAILED ->` per address plus a final count. Relay this plainly, and if there are failures, **don't blindly re-run the whole batch** — that duplicates every already-sent recipient. Show the user exactly which addresses failed and why, and only retry that specific subset once the cause is understood. Full guidance in [Sending and guards](sending-and-guards.md).

## Send As (shared mailbox)

Pass `--send-as <mailbox>` to send as a shared mailbox instead of whoever signs in. Requires Exchange "Send As" permission on that mailbox for the signing-in user, plus the delegated `Mail.Send.Shared` scope on the app registration (with admin consent) — see [Graph sign-in and config](graph-signin-and-config.md) for what's configured, how to verify it, and the 403 this produces if either is missing or points at the wrong mailbox.

> **Warning**
> **Always ask the user which mailbox to send as, every single time — never hardcode one, never default to the last one used, never assume from context.** This applies even mid-session on a second send: confirm the address fresh rather than reusing the answer from a few messages ago. The script's `whoami()` confirmation before the real send exists specifically so the actual From identity is never assumed either.


## Anti-patterns

- Running any step in native Windows Python instead of WSL Ubuntu.
- Attempting a WSL install, Ubuntu first-launch setup, or `sudo apt` step yourself — all three need the user's own hands (elevation, an interactive credential prompt, or a password), never the agent's.
- Pointing `--html-file` at the local `<slug>.html` draft instead of the published `<slug>-cdn.html`.
- Passing `--confirm` without a fresh, explicit yes from the user for that exact send — including on a retry.
- Skipping `--check-only` and letting a guard failure surface only after the user has already approved the send.
- Re-running a whole batch after a partial failure — retry only the addresses that actually failed.
- Hardcoding, defaulting, or silently reusing a shared-mailbox address for `--send-as` instead of asking fresh every time.
- Using `graph-batch-template.html` for a genuine bulk/uninformed marketing list that needs real unsubscribe suppression — that's SendGrid's job.
