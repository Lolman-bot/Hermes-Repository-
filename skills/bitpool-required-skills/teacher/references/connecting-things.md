# Connecting things — MCP, browser, desktop control, chat apps

**Snapshot: 2026-10-16**, built from the Hermes Agent docs
(https://hermes-agent.nousresearch.com/docs/). Hermes changes quickly. If something isn't covered
here, that does **not** prove Hermes can't do it — only that this snapshot doesn't say. Point at the
docs rather than guessing.

Claude's "connectors" map onto a few different things in Hermes.

## MCP servers (connections to other systems)

> MCP is a standard way to plug outside tools into Hermes — GitHub, databases, Linear, Figma,
> internal APIs — without anyone writing new Hermes code.

- `hermes mcp` opens an interactive picker of approved servers; `hermes mcp catalog` lists them;
  `hermes mcp install <name>` installs one. Some need a sign-in afterwards (`hermes mcp login <name>`).
- You choose which of a server's tools Hermes may use.
- Many jobs need no MCP at all: Hermes can already run command-line tools like `gh` (GitHub) and
  `git` directly. For GitHub at Bitpool, `gh auth login` is the usual route.
- Treat a new connection like giving someone access: only add what you trust.

## Browser use

Hermes can drive a web browser — open pages, click, fill forms, read what's there. It can use a
cloud browser or your own Chrome/Edge (`/browser connect`, which can use your logged-in sessions).
It reads pages as text structures, so it's good at forms and data, less good at purely visual
judgements.

## Computer use (your desktop)

Hermes can click, type and scroll in desktop apps on macOS, Windows and Linux — in the background,
without taking over your mouse. It's switched on through `hermes tools` (Computer Use) or
`hermes computer-use install`; `hermes computer-use doctor` checks it. macOS needs Accessibility and
Screen Recording permission. Use it when there's no better route (an API, a command, a browser) —
it's the slowest and most fragile option.

## Chat apps (the messaging gateway)

`hermes gateway setup` connects Discord, Telegram, Slack, Teams, WhatsApp, email and more; `hermes
gateway` runs it. For Discord you create a bot in Discord's developer portal first, and the setup
wizard checks the token and gives you an invite link. Only allow-listed users can talk to the bot.

## Where this hands over

- First-time setup → `/onboarding`.
- "Can it log into X for me?" — passwords are never typed into chat; Hermes has a credential vault
  for saved logins. If this snapshot doesn't cover their case, point at the docs.
