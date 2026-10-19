# Drata Custom Test Design

Designs a Drata Custom Test for a named control, grounded in the control's real record and the
real shape of the data it will evaluate, then writes the finished rule and its rationale into
`security-documentation` as living reference documentation. Never writes test *results* — those
are point-in-time and belong in Drata itself.

**Why the mandatory schema step exists:** an Advanced Editor rule is only as good as its `fact`
names matching the connected resource's real fields exactly. Guessing a plausible-looking field
name (e.g. `CidrBlock` instead of the real `IpRanges[].CidrIp`) produces a rule that silently
never matches anything — Drata won't error, it will just never fire. There is no way to see the
real schema from outside Drata's UI, so this skill treats the user pasting it as a hard
prerequisite, not an optional nicety.

> ## 🛑 THE SINGLE MOST IMPORTANT RULE IN THIS SKILL
>
> **Write a rule for exactly what the control's description says. Nothing more.**
>
> Once a rule correctly satisfies the literal wording of the control, **stop**. Do not keep
> "hardening" it to close every theoretical gap you can imagine — wider port ranges, other
> protocols, edge cases the control never mentioned, resources the control doesn't cover. Every one
> of those is a *different, unrequested* control, and chasing them is how a working, verified,
> already-correct rule gets rewritten into a fragile mess that introduces new bugs while fixing
> nothing the control actually asked for.
>
> **This happened for real, on this exact skill's own worked example.** DCF-92's rule
> (`encrypted-remote-production-access.md`) was designed, scoped tightly to the control's literal
> wording ("remote access... only via an encrypted connection"), and confirmed live with 3 correct
> findings and zero false positives — done. Then, unprompted, the design was "improved" to also
> catch wide TCP port *ranges* that might theoretically span a flagged port. That rewrite:
> introduced a genuine false positive (flagged a GRE/VPN tunnel rule that has no ports at all),
> forced an unresolved philosophical question about whether internal EKS node traffic should count
> as a violation, and burned an entire extra design cycle — to defend against a gap that had **zero
> live impact** and that **the control's own wording never asked about**. The fix was to revert to
> the original, simple, already-correct rule and document the gap as an accepted limitation instead
> of chasing it — stated by its shape (Step 8, item 6). Don't repeat this — if the rule already
> satisfies the literal description, that is the finish line, not a floor to build on.
>
> A genuinely new gap or a broader hardening opportunity is real information — write it down as a
> "known limitation" (by its shape: what the rule does not catch and why, never how many resources
> it affects today) or a suggestion for a *separate* future control/test, and stop there. Do not
> fold it into the current rule uninvited.

---

## Workflow

### Step 1 — Resolve the control

- Get the DCF code or control name from the user.
- Call `Drata_searchControls` (search mode, `query: "DCF-xxx"`).
  **Known gotcha, confirmed live:** search mode can return an empty result even when the control
  genuinely exists — this happened repeatedly for a real, live control before it was found. Do
  **not** conclude "the control doesn't exist" from an empty search alone. Fall back to list mode
  (no `query`): seek straight to the control with `cursor` = base64 of `id|<id + 1>` and
  `size: 1`, taking the id from the Drata Controls Register URL, and confirm the returned `code`.
  If the seek misbehaves, paginate via `cursor` to `null`. Searching by the plain-English name
  does not help — exact-name `query` searches return empty too. See `/ask-drata` gotchas #1, #2
  and #11 (archived controls appear in no list at all).
- Capture `id`, `code`, `name`, `description`, and `flags` — especially `isMonitored`. If it's
  already `true`, tell the user a test likely already exists and check
  `Drata_searchMonitoringTests` (`expand: ["controls"]`) before designing a duplicate.

### Step 2 — Read the control's actual wording, scope tight

- Restate the control's `description` in your own words. Don't drift into a broader security
  best practice that happens to be adjacent — a control about "remote access only via VPN" is not
  the same test as "no security group is ever open to the internet." The second is broader and is
  very likely some *other* control's job.
- **Confirm scope with the user before writing anything.** They know the actual implementation
  (which VPN, which mechanism, which resource) — don't guess generic hardening advice in its
  place.
- One control, one test, one stated requirement. Resist testing everything a resource happens to
  expose just because the data is sitting there.
- **Watch for "encrypted" vs. "restricted" — a real, confirmed mixup.** A control that says
  remote access must be "encrypted" (e.g. "...only via VPN, SSH, etc.") is about the *transport*
  being encrypted, not about *where connections may originate from*. SSH is encrypted by protocol
  design, full stop — a direct SSH connection from anywhere already satisfies that kind of
  control; restricting SSH's source IPs to a VPN/VPC is a **different, adjacent** requirement
  (typically "restrict admin ports to authorized sources," e.g. Bitpool's DCF-73), not the
  encryption one. This exact mixup happened once already: a rule was fully designed and written
  up against DCF-92 before re-reading its literal wording revealed it actually belonged to DCF-73.
  **After the rule is designed (Step 6), re-read the control's literal wording one more time and
  ask: does this rule test the transport being encrypted, or does it test something else entirely
  (source, hardening, rotation, logging)?** If it's testing something else, check whether a
  *different* existing control is the real fit — remap to that control rather than forcing the
  original mapping.

### Step 3 — Determine the data source

- Check whether Drata already has a **native infrastructure connection** (AWS/GCP/Azure) that
  would carry the relevant resource type. Most Bitpool AWS controls already do, since Drata's
  built-in tests already draw from the same connection.
- **Native connection exists:** build directly against it in Test Builder — no custom script, no
  API key, nothing to maintain.
- **No relevant native connection:** this needs Custom Connections & Tests (CCT) instead — a
  separate, heavier path involving your own push script, a Drata Custom Connection, and a
  recurring data push. Flag this explicitly rather than silently defaulting to one path or the
  other.

### Step 4 — Get the real schema (never guess it)

**Always ask the user to open the Drata Test Builder, click the Resource Guide info icon, select
Provider → Service → Resource, and paste the "Example data structure" shown there** before
writing a single line of rule JSON. Reuse a schema already pasted earlier in the same
conversation — don't ask twice for the same resource type.

### Step 5 — (Optional) Validate against real infrastructure

For AWS-backed controls, if the design should reflect what's actually deployed rather than just
the resource shape: use `/aws-context` to confirm a live SSO session, then `/aws-query` to pull
the real values (actual security group rules, actual VPC CIDR, etc.). This is how a durable rule
gets designed — e.g. discovering the real VPC CIDR to hardcode (safe, stable) versus discovering
that a VPN's IP shouldn't be hardcoded (unstable) and using a `Description`-match instead. Values
found this way go into the rule JSON; the page's prose names them by role (Step 8, item 6). Never
inline AWS CLI commands, profile names, or account IDs into this skill file — that's
`/aws-query`'s job, referenced not duplicated.

### Step 6 — Design the Advanced Editor JSON rule

- `fact` names must match the real schema from Step 4 exactly — including case.
- `path` drills into nested object properties. `operator: "all"` applied to an array-valued fact
  iterates every element against a nested condition (and the reverse, checking for *any* match,
  composes with a nested `any`). `all`/`any` are logical AND/OR and can nest arbitrarily deep.
- Prefer values that don't need updating when infrastructure changes: a VPC CIDR is stable and
  fine to hardcode; a specific host or VPN IP is not. If the team consistently labels rules (e.g.
  a `Description` containing "VPN"), matching on that text is often far more durable than the
  literal IP.
- **Fastest way to get the real operator list: trigger the validation error on purpose.** Paste an
  intentionally invalid or blank operator (e.g. `"operator": ""`) into the Advanced Editor. Drata's
  own validation error names every accepted operator directly in the UI — faster and more
  authoritative than guessing from documentation or trial-and-error with Ctrl+Space IntelliSense.
  Do this early whenever a new operator's existence is in doubt, rather than designing a rule
  around an unconfirmed guess.
- **Full confirmed operator list** (obtained this way, not from documentation — this is the
  authoritative source): `equal`, `notEqual`, `in`,
  `notIn`, `contains`, `doesNotContain`, `startsWith`, `endsWith`, `isBefore`, `isAfter`, `exist`,
  `withinLastDays`, `withinNextDays`, `withinLastHours`, `olderThanDays`, `empty`. `all`/`any` are
  a separate category — the structural logical/array operators, not value comparisons. `in`/
  `notIn` are the right choice for "port is one of a list" instead of chaining `notEqual`/`equal`
  per value. `startsWith` is anchored to the start of the string — unlike `contains`, it does not
  match a value appearing mid-string (e.g. `startsWith("10.")` correctly rejects `"12.10.134.123"`,
  which `contains("10.")` would wrongly match). Only `equal`, `notEqual`, and `all` have actually
  been run live and confirmed to work as expected so far — the rest are validated *names*, not yet
  validated *behavior* in a real run. Update this note as more get confirmed live.
- **Watch the Advanced Editor's documented 70-line-per-block limit.** A rule that needs to
  enumerate many discrete values (e.g. checking a CIDR against every `172.16.`–`172.31.` prefix
  because `172.16.0.0/12` doesn't collapse into one string prefix) can realistically approach this.
  Prefer a narrower, real-data-driven check (only the prefixes actually observed in the
  environment) over a fully general one if the general version risks the limit — note the
  narrowing explicitly as a scope tradeoff in the GitBook page rather than leaving it unexplained,
  by its shape: the prefixes the rule recognises are in the rule; the page says what a range
  outside them will do and how to widen the list, not which ranges are deployed today.
- **AWS security group port/protocol fields need care, not just `FromPort == <port>`.** Per the
  EC2 `IpPermission` API reference: `IpProtocol: "-1"` means "all protocols, all ports" — it
  matches SSH/RDP too even though `FromPort`/`ToPort` are typically absent, and any rule checking
  for a specific port must also check for `IpProtocol == "-1"` or it will silently miss
  "all traffic" rules. Conversely, `IpProtocol: "icmp"`/`"icmpv6"` reuses `FromPort`/`ToPort` to
  mean ICMP type/code, not a TCP/UDP port — `-1`/`-1` there means "all ICMP types," which carries
  no port semantics at all and should stay excluded. A wide TCP port *range* spanning a target
  port without starting exactly on it (e.g. `1`–`65535`) still isn't caught by simple equality —
  that needs a numeric range comparison, which requires confirming a `lessThanInclusive`/
  `greaterThanInclusive`-style operator actually exists before relying on it.

**Before moving on: does this rule already satisfy the control's literal wording?** If yes, stop
designing — see the highlighted rule at the top of this file. Resist the urge to keep closing
theoretical gaps the control never mentioned.

### Step 7 — Verify before publishing

Recommend pasting as a **draft** first — drafts run and show results without affecting control
readiness or audit evidence. Run it, sanity-check the pass/fail list against what's actually
true, only then publish and map it to the control. Don't promote the GitBook page to `prod/`
(Step 8, item 2) until the user confirms the rule runs without engine errors — a syntactically
plausible rule Drata rejects isn't documentation-worthy yet.

**Stage the test's Drata name and description with the rule.** Test Builder asks for both when the
test is created, and they are read long after the run that verified it — **Security Drata** text
(`profile-security-drata.md` §3.6, loaded per `SKILL.md` load-bearing rule 7). Stage them for the
user to paste:

> **Name:** `<what the test checks — the documentation page's title>`
>
> **Description:** Checks `<resource type>` across `<the population, by criterion>` for `<the
> condition, by category>`. It evidences `DCF-xxx` — `<the requirement, in the control's terms>`.
> The rule's logic, scope decisions and known limitations are documented on the `<page title>` page
> in the Drata Custom Tests section of `security-documentation`.

*Example description:* "Checks the inbound rules of every AWS security group Drata's
infrastructure connection covers for inherently unencrypted remote-access protocols, and for
'All traffic' rules open to a source outside the private ranges the rule recognises. It evidences
DCF-92 — remote access to production systems only through an encrypted connection. The rule's
logic, scope decisions and known limitations are documented on the Encrypted Remote Production
Access page in the Drata Custom Tests section of security-documentation."

- **The name is the page title** — by function, never by DCF number, for the same reason as the
  page filename (Step 8, item 3).
- **What the description may say is Security Drata §3.6** — the literals live in the rule JSON, and
  results and draft or published state in Drata.
- **Point at the page by title and section, never by path or URL** — the page moves from `draft/`
  to `prod/` when it is verified.

Directly under the staged text, show the durability check (`durability-check.md` §1). The
judgement call that recurs here is the population claim: keep it only where the rule applies no
account or OU filter that narrows it.

**Durability check**

| Field | Span | Why flagged | Disposition |
|---|---|---|---|
| description | `every AWS security group Drata's infrastructure connection covers` | Universal claim | Kept — population; the rule applies no account or OU filter |
| all | `DCF-xxx`; the page title; Drata and `security-documentation` as pointers | Handles | Kept — durable handles |

**Removed before staging** — `<what the draft carried>` → `<where it went>`.

### Step 8 — Write it to the GitBook, progressively

Once the rule is stable enough to be worth keeping — even before final verification, don't wait
until a long design conversation ends to write anything down:

1. Locate `security-documentation` fresh under `C:\BitpoolDev\` every time (never hardcode the
   path — see `/bitpool-docs`), and read its `_meta/` files fresh — the frontmatter schema, and
   `writing-standard.md`, the Security Documentation profile this page follows (`SKILL.md`
   load-bearing rule 7).
2. Target folder: `compliance/drata-tests/` — a **subfolder** of the existing `compliance/` topic,
   which already covers "Drata DCF tracking" per that repo's own taxonomy. This is not a new
   top-level folder, so it doesn't need that bar's ≥3-page/ask-first confirmation. Test pages sit
   in its two lifecycle subfolders: **`draft/`** while the design is unverified, **`prod/`** once
   it is verified live, published and mapped. The promotion criteria are on `draft/README.md` —
   read them fresh. Promotion moves the page and checks its relative links, sets `status: draft` →
   `active`, and adds the verification note (item 6); it does not rewrite the rationale. If any of
   these folders doesn't exist yet, create it with a short `README.md` landing page.
   **A landing page carries no list or count of tests.** It says what the subsection holds, the
   naming convention and the promotion criteria; the page list is the regenerated `index.md`
   (item 9) and GitBook's navigation. Never add a test to a hand-maintained list — every promotion
   would then need two edits, and one gets missed. Where a landing page already carries one, offer
   to replace it with a pointer to the index rather than extending it.
3. **One page per test, named by what it checks — never by DCF number.** File:
   `compliance/drata-tests/draft/<function-slug>.md` (moved to `prod/` at promotion), e.g.
   `encrypted-remote-production-access.md`, not
   `dcf-92-....md`. A test's logic can plausibly satisfy more than one control (an equivalent
   requirement in a different framework, or more than one Drata control at once) — a filename tied
   to one framework's numbering doesn't survive that. If naming it after the anchor control's own
   plain-English title reads well, that's fine (it's descriptive text, not an ID) — the thing to
   avoid is leading with `dcf-<n>-`.
4. **No separate page per control.** A DCF number is a *reference on* the test page it maps to,
   not a page of its own — don't create a `dcf-<n>.md` pointer/redirect file. If a test ever picks
   up a second control, add it to the same page's mapping, don't create anything new for it.
5. Frontmatter per `security-documentation/_meta/frontmatter-schema.md`: `type: Compliance
   Reference`, `doc_type: reference`, `sources: [drata:DCF-<n>, jira-csip:<key if one exists>]`,
   `drata_controls: [DCF-<n>, ...]` (a list — add every control this test actually maps to, not
   just the first one found), plus `keywords`/`related` as normal, and `status: draft` until
   promotion. `owners`, if set, names a role or team, per the frontmatter schema and the Security
   Documentation profile §2. Near the top of the page body, state the mapping in prose too:
   `**Mapped controls:** DCF-<n> (Drata, <framework>).` — plain text, not a link, since there's no
   separate page for it to point to.
6. Page content: the control's stated requirement (from Step 2), the resource/schema it targets
   (from Step 4), the finished rule JSON, the design rationale — why this fact/operator, what
   tradeoff was made (e.g. "matches `Description` containing VPN rather than hardcoding the VPN's
   IP, which can change") — and any known limitations. **Never include test run results,
   pass/fail counts, or specific findings from a live run** — those are point-in-time and belong
   in Drata's test history, not the docs. Under the Security Documentation profile, four things
   are specific to this page:
   - **Values read from the estate live only in the JSON block**, which the Security Documentation
     profile (§2) declares the home of the rule's literals. CIDRs and prefixes read from the estate,
     and any account or OU filter, appear there exactly as the rule needs them; the prose names each
     by its role — *"the private prefixes the rule recognises"*, *"the production VPC's CIDR, as
     held in the rule"* — and never restates the value, so re-addressing a network changes one
     place. The ports, protocols and match conventions the control requires are requirement-level
     identifiers and may be named in the rationale (`/bitpool-writing-standard`, *Where specifics
     are right*) — which ports or protocols the rule flags, and why, is the design itself. Account
     names, resource IDs and counts of what is deployed stay out of the prose.
   - **A design decision is stated by its reason, not by the run that prompted it.** *"The default
     security group's self-referencing rule is exempt, because it is unreachable from outside the
     group"* — not the tally of failures a run returned before the fix.
   - **Known limitations by shape, never by live impact.** What the rule does not catch, why (the
     control's wording does not require it, or an operator or line limit), and what would reopen
     it — *"a wide port range spanning a flagged port without starting on it is not caught; the
     control concerns unencrypted protocols, not port-range analysis"*. Not how many resources show
     that shape today, or that none is exposed now: that is a live finding, and it goes false as
     the estate changes.
   - **The verification note is an anchored event**, added at promotion: the date, how it was
     verified (a draft run in the Advanced Editor without engine errors, its results spot-checked
     against an independent read of the same resource), and that the results are in the test's
     history in Drata. No finding counts. An earlier design the page no longer describes lives in
     git history; the page states the current design and points at any sibling test that took over
     part of it.
7. **Edit the same page as the design changes within the conversation**, rather than waiting to
   write a "final" version once at the end. Treat it as living documentation of the current
   design.
8. Call `/gitbook-docs` for any GitBook block syntax the page needs (hints, tabs) — not duplicated
   here.
9. Regenerate indexes after every add/edit:
   `python3 "<repo-root>/_meta/skill/scripts/regenerate-indexes.py"`. Confirm the `Using repo
   root: …` stderr line points at `security-documentation`, not one of the other two OU repos.

### Step 9 — Report back

Summarize: which control, what the rule checks (one sentence), where it was written (repo path),
and whether it's been verified live in Drata yet or is still a draft-only design. Then show the
durability check (`durability-check.md` §1) for the page prose written or changed this session —
the page is written progressively with no approval block of its own, so this is where the user
sees it. One row covers the rule JSON's literals — kept, home: the Security Documentation profile
(§2) declares that block their home.

---

## What this skill must never do

- **Never extend a rule beyond the literal control description once it already satisfies it** —
  see the highlighted rule at the top of this file. A working, verified rule is the finish line.
  Closing theoretical gaps the control never mentioned is scope creep, not diligence.
- Never fabricate a Drata resource schema — always get the real "Example data structure" from the
  user (Step 4). This is the one rule this skill exists to enforce.
- Never write test run results, pass/fail counts, or specific findings into the GitBook page —
  code and description only (Step 8, item 6).
- Never conclude a control "doesn't exist" from an empty Drata search-mode result alone —
  paginate list mode first (Step 1).
- Never author ISMS policy content. Redirect to `/isms-draft` / `/isms-prod` if the request turns
  out to be about a policy, not a test.
- Never invent a new top-level GitBook folder without asking first. `compliance/drata-tests/` is
  a subfolder of an already-existing, already-relevant top-level folder, which is why it's exempt
  from that confirmation — a genuinely new top-level folder still needs one.

---

## Improving this skill over time

- **Operator vocabulary is incomplete by design** — Drata doesn't publish it, so this list only
  grows from confirmed live use. When a new operator is confirmed working (or found not to
  exist), update the list in Step 6 rather than leaving future runs to re-guess from scratch.
- If Custom Connections & Tests (Step 3's fallback path) becomes common enough to need its own
  detailed walkthrough — connection setup, push-script patterns, API key handling — split it into
  a sibling skill rather than growing this one. This skill's core value is the native-connection
  Test Builder path plus the mandatory real-schema step; don't dilute that.
- Consider adding a lightweight "does a test already exist for this control" check as its own
  early step if duplicate-test reports become a recurring problem.
