# Ask Drata — scope and maintenance

## Where this fits vs. the other Drata skills

- **This skill** — connection-level operational notes only. No workflow, no per-control logic. It owns the write *model* (rules 8–10), the writable-field inventory and the write *policy* table above; consuming skills inherit all three rather than restating them.
- `/create-drata-test`, `/drata-control-insights`, `/drive-iso27001`, `/describe-dcf-jira-ticket` and `/create-devsecops-ticket` are workflows that **consume** Drata data, read-only. They should assume these gotchas apply rather than re-deriving them — the control-mapping steps in `/create-devsecops-ticket` and `/describe-dcf-jira-ticket` lean on rules 1–4 directly.
- **Which skills write to Drata, and which verbs each may call, is the write-policy table above** — never this list, and never a skill's own claim. If the write model or the policy changes, it changes **here** and every skill inherits it.
- `/bitpool-writing-standard` (section `bitpool-general`) — what the words say in a Security Drata field (rule 16). This skill records which fields the connection can write and the trap in each; the standard governs their content. Neither restates the other.

## Editing this skill

New confirmed quirks → add a numbered entry to `references/drata-mcp-gotchas.md`, with the date, the exact call and response, and the rule; then add the rule itself to the load-bearing list above if it changes what a caller may conclude.

Keep entries about the *connection's behaviour*, not about a specific control's content or a workflow's steps. The test: would this still be true for a different company using the same Drata MCP? If yes it belongs here. If it depends on how Bitpool treats a control, it belongs in that workflow's skill.

Entries are dated observations, so they carry the exact call and response — with every count stated as what a call returned on a date, never as a baseline or a standing figure. This skill ships to every Bitpool user, so a colleague's email address or third-party login goes in as a placeholder (`<user-email>`); where whose account it was matters to the finding, say so by role, as the scope matrix does for the account that ran the probes. A tool's presence or absence is an observation too: date it. The writing standard's content stays out of this skill — rule 16 points at it and never paraphrases it.
