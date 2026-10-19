# GitHub repository properties

> **Read `references/snapshot-and-diff.md` first.** The tags are the live register; the
> snapshot is what lets this cycle be diffed against the last one. Both halves are the job,
> and the diff is the half a live query can never do for you afterwards.

**Snapshot and diff**, from the file `Export-GhRepoProperties.ps1` retains:

```bash
wsl -e bash -lc 'python3 scripts/snapshot.py github --values github-repo-properties_2026-09-17.json \
  --repos repos.json --cycle 2026-09 -o github_2026-09.json'
wsl -e bash -lc 'python3 scripts/diff_snapshots.py github_2026-06.json github_2026-09.json --format markdown'
```

The snapshot keys on the **numeric repository id**, not the name, so a renamed repository reads as
changed rather than as one repository deleted and another created.

**GitHub organisation custom properties are the asset register** for source code repositories.
`OwnerGroup` records the accountable **team**, not an individual.

## Two things to understand before running this

**The properties are not marked required.** All five — `OwnerGroup`, `Purpose`, `Criticality`,
`DataClassification`, `IsPersonalData` — are `required=false` (verified 2026-09-16). A repository can
therefore be created carrying no classification at all, and new repositories land unclassified by
default. The register is **not** self-maintaining.

**Populating the register is not this cycle's job.** Full tagging of the GitHub estate is delivered
under the **cloud resource tagging control** (`DCF-777`), tracked on `IRT-46` / `IRT-47` / `IRT-48`
and `IRT-52`. This cycle **measures and records** coverage; it does not fill it. Unclassified
repositories are an expected interim state, not a finding of this review — report the number, name
where the work is tracked, and move on.

## Access — an admin export, or no export

> **This is the part that was got wrong.** A member token silently returns only the repositories it
> can see, and every coverage figure derived from it is measured against the wrong denominator. On
> 2026-09-16 a member token returned **31 repositories when the organisation held 61**. The resulting
> "25% coverage" number looked like a finding and was meaningless.

**The gate is the organisation ROLE, not the token's scopes.** This is easy to get wrong in a way
that wastes an afternoon:

> `read:org` is sufficient to *read* `properties/values` — verified 2026-09-17 with a token carrying
> only `gist`, `read:org`, `repo`, `workflow`. It returned property values perfectly. It returned
> them for **31 repositories**, because the account is an org `member`.
>
> **No scope grants a member owner-level repository visibility.** Minting a token with `admin:org`
> on a member account gets you the same 31 repositories and no error. Only an account whose
> `user/memberships/orgs/bitpool` → `.role` is `admin` sees the whole estate.

There is also an **admin console** route — GitHub → the `bitpool` organisation → **Settings → Custom
properties**, which lists every repository with its values. There is no CSV export button there;
it is for eyeballing and for bulk *editing*, not for producing the cycle's evidence.

**Completeness is checked by COUNT, not by permission.** Changed 2026-09-17.

The obvious pre-flight check does not work here:

```bash
gh api user/memberships/orgs/bitpool --jq '.role'
```

That endpoint needs the fine-grained permission **Organization → Members: Read-only**, which is
**not offered in bitpool's token UI**, so it returns `403` and aborts the run before a single
repository is fetched. `Administration: Read-only` does not cover it.

So the check moved to where it is stronger anyway — **after** the export, comparing what came back
against the organisation's own total:

```bash
gh api orgs/bitpool --jq '{public: .public_repos, private: .total_private_repos}'
```

A role check only ever *predicted* completeness. The count *measures* it. If the export is short,
**stop**: do not produce a coverage figure, do not file the output as evidence, and do not record a
caveat and carry on — hand it to an owner. A number measured against a partial denominator is worse
than no number, because it reads as a result.

> **A fine-grained token receives `total_private_repos` only with Organizations > Administration: Read-only.** First seen 2026-09-17 against an
> organisation **owner's** fine-grained PAT: `GET /orgs/bitpool` came back without the field at all.
> Classic tokens get it; fine-grained tokens get a reduced organisation payload. Role is irrelevant.
> So there is frequently **no API denominator available**, and the script must not invent one —
> `public_repos + null` silently equals `public_repos` in PowerShell, which would clear a partial
> export against a handful of public repositories and print *"Full export"* over most of the estate.

**So the denominator is resolved in order of strength:**

| | Source | Strength |
|---|---|---|
| 1 | `-ExpectedRepoCount`, read off the organisation's repository list by a person | Strongest — a human looked |
| 2 | `GET /orgs/<org>` → `public_repos + total_private_repos` | Only available to a classic token |
| 3 | None | The run says so, writes a provenance file recording that completeness was **not** verified, and does not invent a total |

**Prefer `-ExpectedRepoCount`.** Open the organisation's repository list, read the count, pass it:

```bash
.\Export-GhRepoProperties.ps1 -OutDir '<cycle folder>' -ExpectedRepoCount 61
```

That turns an eyeball check into recorded evidence. Without it the export still runs and is still
valid as a list — it just carries a provenance file saying completeness was not verified, which is
the honest state and is far better than a confident number with nothing behind it.

### Do not `gh auth login` as the owner

The owner credential must not be left sitting in the keyring on a workstation. `gh auth login`
persists it; `GH_TOKEN` does not. Verified 2026-09-17: with `GH_TOKEN` set, `gh` used that token,
ignored the keyring account entirely, and wrote **zero files** to `GH_CONFIG_DIR`.

**Run `scripts/Export-GhRepoProperties.ps1`.** It prompts for the token, writes both the retained
JSON and the CSV, wipes the token and the throwaway config directory in a `finally` block, and —
if the count falls short of the organisation total — stamps the output
`PARTIAL-DO-NOT-USE-FOR-COVERAGE` **and fails**, rather than warning and exiting zero. Pass
`-AllowPartial` only when the partial list is wanted for something that is not a coverage figure.

**Token permissions it needs:**

| Permission | For |
|---|---|
| Organization → **Custom properties**: Read-only | the property values |
| Repository → **Metadata**: Read-only | the repository list |

### The permission set that actually works

Confirmed by a complete 61-of-61 export on 2026-09-17. **All three are on the ORGANIZATIONS tab**,
plus Metadata on the Repositories tab:

| Tab | Permission | Unlocks |
|---|---|---|
| Organizations | **Custom properties**: Read-only | `GET /orgs/{org}/properties/schema` and `.../values` — the export itself |
| Organizations | **Administration**: Read-only | `total_private_repos` on `GET /orgs/{org}` — the automatic denominator |
| Organizations | **Members**: Read-only | `GET /user/memberships/orgs/{org}` — the caller's role, recorded as provenance |
| Repositories | **Metadata**: Read-only | the repository listing. Marked Required by GitHub anyway |

Repository access must be **All repositories**, not *Only select repositories*.

{% hint style="warning" %}
**Two different permissions are both called "Custom properties", and the UI gives no hint.**

The **Repositories** tab one grants `PATCH /repos/{owner}/{repo}/properties/values` and nothing
else — useless here, while looking exactly like compliance. The **Organizations** tab one is the
one this needs. Granting the wrong one produces `HTTP 403 Resource not accessible by personal
access token` on an endpoint you have apparently just been given access to.
{% endhint %}

{% hint style="info" %}
**Corrected 2026-09-17.** An earlier edition of this page said Administration: Read-only does not
make `total_private_repos` appear, on the strength of GitHub's permission reference not listing
`GET /orgs/{org}` under it. That was wrong in practice — granting it produced the field, and the
denominator went from unavailable to automatic. The documentation's endpoint list is not
exhaustive for payload *fields*; test the call rather than reading off the table.
{% endhint %}

```bash
.\Export-GhRepoProperties.ps1 -OutDir "<cycle evidence folder>"
```

Mint the token as a **fine-grained PAT**: resource owner `bitpool`, all repositories, expiry 1 day,
**Repository → Metadata: Read-only** plus **Organization → Custom properties: Read-only**. That
token cannot read a line of source. Revoke it when the cycle's export is filed. If the fine-grained
token 403s on `properties/values`, fall back to a classic PAT with `read:org` + `repo` — proven
working — and revoke that just as promptly.

> **Never type the token as part of a command.** On a machine running PSReadLine below **2.1.0** —
> which is what Windows PowerShell 5.1 ships — there is no sensitive-input filter and
> `HistorySaveStyle` is `SaveIncrementally`, so `$env:GH_TOKEN = 'ghp_...'` is written in plaintext
> to `ConsoleHost_history.txt` the moment you press Enter. The script uses `Read-Host` precisely so
> the token never becomes a command line. Check with `(Get-PSReadLineOption).HistorySavePath`.

### Commands, if running it by hand

```bash
gh api orgs/bitpool --jq '{public: .public_repos, private: .total_private_repos}'
gh api orgs/bitpool/properties/schema
gh api --paginate orgs/bitpool/properties/values > github-repo-properties_<date>.json
```

> **The denominator is `public_repos + total_private_repos`.** GitHub also reports
> `owned_private_repos`, which is **one lower** (51 against 52 on 2026-09-17) because it excludes
> private *forks*. The review standardises on `total_private_repos` so figures stay comparable
> quarter to quarter. Using the other field silently restates the total as 60 and makes coverage
> look better than the previous cycle measured it.

Run `gh` and `git` from **PowerShell or Git Bash on Windows, not WSL** — `gh` is installed and
authenticated on the Windows side only. This is the exception to the rule that scripting goes through
WSL.

> **Git Bash rewrites a leading `/` into a filesystem path.** `gh api /orgs/bitpool` fails with
> *"invalid API endpoint: C:/Users/.../orgs/bitpool"*. Omit the leading slash — `gh api orgs/bitpool`.

## The cycle

### 1. Establish the true repository count

From `gh api orgs/bitpool`, public plus private. Every coverage figure is reported against this
number, never against what the listing returned.

### 2. Read the schema and the values

Confirm the five properties still exist and whether any has become `required`. Then pull the values
for every repository and count how many carry a complete set.

Expect a **binary split** rather than a gradient: a repository has all five or none, because values
are set per repository by whoever administers it. Partial sets are unusual and worth a second look.

### 3. Report coverage — do not fill it

State the number classified against the organisation total, and name `DCF-777` / `IRT-52` as where
population is tracked. Do not tag repositories as part of this cycle.

### 4. Evidence

Per `references/evidence-contract.md`. Retain the values output produced by the **admin** export,
in the cycle folder.

## Do not bulk-tag

Repository properties are set deliberately, not swept. Where several repositories need the same
property, list them and hand the list over rather than scripting a bulk write — the user has asked
for this explicitly, and population belongs to the tagging control regardless.

## The other trap

> **Branch protection is configured with Rulesets, not classic branch protection.** The classic
> `/repos/{owner}/{repo}/protection` endpoint reports **"not protected" on every repository** and is
> wrong.
>
> Read `.protected` on the branch, or `/repos/{owner}/{repo}/rules/branches/{branch}`, instead.
>
> Not part of the asset register, but it comes up whenever a repository review runs alongside this
> cycle, and the wrong endpoint produces a confident false finding.
