# Models and providers

**Snapshot: 2026-10-16**, built from the Hermes Agent docs
(https://hermes-agent.nousresearch.com/docs/). Hermes changes quickly. If something isn't covered
here, that does **not** prove Hermes can't do it — only that this snapshot doesn't say. Point at the
docs rather than guessing.

## "What's a provider? Which model should I use?"

> Hermes is the agent; the **model** is the brain it drives, and the **provider** is who you get the
> model from (Nous Portal, Anthropic, OpenAI/ChatGPT subscription, OpenRouter, GitHub Copilot, a
> local model, and many more).

- **Choosing or changing provider:** run `hermes model` in a terminal. `hermes setup` covers it on a
  fresh install. Nous Portal is the docs' easiest path (`hermes setup --portal`: one login, a model
  plus web search, image generation and cloud browser tools).
- **Switching model mid-conversation:** `/model` inside a chat — but only between providers already
  set up. Adding a *new* provider is `hermes model`, outside the chat.
- **Minimum size:** Hermes needs a model with at least 64K tokens of context; smaller ones are
  refused at startup. Most hosted models are far above that.
- If Bitpool has a standard provider or account, that's a company decision — ask rather than
  picking one with a personal card.

## Cost and behaviour notes

- **Switching model mid-conversation costs more on the next turn** — the provider's cache resets, so
  the whole conversation is re-read at full price. Fine occasionally; avoid flip-flopping.
- `/usage` shows token use and cost for the current conversation.
- **Smaller/local models are weaker at tool use** — they sometimes claim to have done something
  (like saving a memory) without doing it. If it matters, use a stronger model.
- Secrets (API keys) live in the profile's `.env`; normal settings in `config.yaml`. `hermes config
  set` puts each value in the right file.

## When it's broken

The docs' recovery order: `hermes doctor` → `hermes model` → `hermes setup`. Get one plain
conversation working before adding anything else.
