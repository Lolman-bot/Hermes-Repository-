# Snapshot and diff

Shared by AWS, Azure and GitHub. Read this before any of the three per-register files — they
assume it.

## Why a snapshot exists at all

The obvious objection: if the tags **are** the register, and they maintain themselves, what does a
quarterly file add?

**A live query only ever shows today.** Run `az resource list` and you learn what exists now. You
do not learn that a storage account appeared in July, that a resource group was deleted in August,
or that something lost its `OwnerGroup` along the way. "Show me the register as at 30 June" has no
answer unless a dated extract was retained, and neither does "what changed since last quarter, and
did anyone account for it".

So the cycle does two different things and they must not be confused:

| | Answers | Mechanism |
|---|---|---|
| **Coverage** | *Is the register accurate right now?* | Tags on the live estate |
| **Diff** | *Did anything change without being accounted for?* | This cycle's snapshot vs last cycle's |

A cycle that reports coverage and skips the diff has done half the job, and the half it skipped is
the one a live query cannot do for you later.

## The snapshot format

One shape for all three registers, so `diff_snapshots.py` needs no per-register logic.

```json
{
  "register": "aws | azure | github",
  "cycle":    "2026-09",
  "captured": "2026-09-17T05:57:31Z",
  "source":   "what produced this, in words",
  "scope":    { "resource_groups": 8, "resources": 34 },
  "excluded": { "by_type": 0, "by_tag": 0, "ephemeral": 0 },
  "coverage": { "units_bearing_tags": 8, "all_required_keys_present": 8 },
  "items": {
    "<stable id>": {
      "name":  "Sentinel",
      "type":  "resourceGroup",
      "unit":  "group | resource | repository",
      "attrs": { "OwnerGroup": "Security", "Criticality": "Critical" }
    }
  }
}
```

### Stable ids, never names

| Register | Key |
|---|---|
| AWS | ARN |
| Azure | Resource id / resource group id, **lowercased** |
| GitHub | Numeric repository id |

A rename must read as **changed**, not as a delete plus an add. Keying on names turns every rename
into a phantom decommission beside a phantom new asset, and both get chased.

Azure ids are lowercased because `az resource list` and `az group list` disagree about the case of
`resourceGroup` for the same group — `Sentinel` against `sentinel`. Group on the raw string and one
resource group appears twice.

### `unit` decides what is expected to carry tags

**Azure tags at resource-group level**, so its `resource` items are tracked for *existence only*
and are not expected to carry governance keys. An untagged Azure resource is not a finding; an
untagged Azure resource **group** is. AWS and GitHub tag the thing itself.

This is why `diff_snapshots.py` computes coverage per register rather than counting every item — a
naive count would invent a 34-resource shortfall in Azure that does not exist.

## Running it

### 1 — Collect

Through `/aws-query` or `/azure-query`. Never write collection commands here. Write raw JSON to
disk first and parse it afterwards; piping `az` or `aws` into an inline parser breaks on nested
quoting in ways that produce a confusing `SyntaxError` rather than a clear failure.

### 2 — Snapshot

```bash
wsl -e bash -lc 'python3 scripts/snapshot.py azure \
  --resources resources.json --groups groups.json \
  --cycle 2026-09 --source "az resource list + az group list, sub 3e13a29f" \
  -o azure_2026-09.json'
```

```bash
wsl -e bash -lc 'python3 scripts/snapshot.py aws \
  --resources tagged-resources.json --cycle 2026-09 -o aws_2026-09.json'
```

```bash
wsl -e bash -lc 'python3 scripts/snapshot.py github \
  --values github-repo-properties_2026-09-17.json --repos repos.json \
  --cycle 2026-09 -o github_2026-09.json'
```

GitHub's values file is what `Export-GhRepoProperties.ps1` retains. `--repos` is optional and adds
visibility and archived state.

### 3 — Diff against last cycle

```bash
wsl -e bash -lc 'python3 scripts/diff_snapshots.py azure_2026-06.json azure_2026-09.json --format markdown'
```

Last cycle's snapshot lives in the **previous cycle's evidence folder** — that is what the folders
are for. Retain this cycle's snapshot alongside the raw dump it came from, per
`references/evidence-contract.md`.

## Reading the diff

Four sets. The first two are the review's actual output.

| Set | Means | What it obliges |
|---|---|---|
| **ADDED** | In the new snapshot, absent from the old | A disposition for each. Who created it, under what change, is it tagged? **An addition nobody can explain is the finding this cycle exists to produce** |
| **REMOVED** | In the old, absent from the new | Record the removal. Decommissioned deliberately, or deleted without anyone noticing? Never let a row vanish silently |
| **CHANGED** | Same id, different attributes | Usually benign — a `Purpose` reworded, a resource moved group. Scan for ownership and classification changes, which are not benign |
| **REGRESSED** | Held all required keys, no longer does | A **register defect** rather than an estate change: the asset still exists, but the register stopped describing it. Marked `!` and listed separately because it is invisible in a coverage count that only went from 8/8 to 7/8 |

`*` beside a changed attribute marks a governance key. Unmarked changes are positional —
`resourceGroup`, `location`, `visibility`, `archived`.

**A clean diff is a result.** Print it, record it with the counts, and do not shorten it to "no
change".

## Failure modes that make a diff lie

**Diffing a snapshot against one built from the same dump.** Always clean, always convincing,
always worthless. If the previous cycle's snapshot cannot be found, say so and record this cycle as
a **baseline** — do not manufacture a comparison.

**A hand-edited snapshot.** `diff_snapshots.py` recomputes coverage from the items for exactly this
reason; the stored `coverage` block reflects capture time and will disagree with edited items. The
rule from the evidence contract applies here too: a closed cycle's folder is not reopened.

**A partial collection.** A dump taken with insufficient permissions produces a snapshot that looks
complete, and every removed item in the next diff is an artefact of the permission gap rather than
a decommission. GitHub is where this bites — see `github-repository-properties.md`, and note that
`Export-GhRepoProperties.ps1` refuses to produce an unstamped partial export.

**Ephemeral or non-primary resources in an AWS snapshot.** AWS tracks **primary assets only** —
an allow-list of 13 types, per the 2026-09-17 decision. Pods and spot requests turn over
constantly, and backup snapshots turn over on a schedule; either would produce a diff with
hundreds of additions and removals nobody will read, and a real finding buried in one is a finding
nobody sees. `snapshot.py` reports what it dropped in `excluded`, and every excluded *type* it saw
in `scope.excluded_types_seen`.

**The allow-list's own failure mode.** It cannot drop a type by accident, but it can drop a
genuinely new primary type silently — a new data store service, say. `scope.excluded_types_seen`
is the guard: read it each cycle, and treat an unfamiliar type there as a scope decision rather
than noise.

**Comparing across registers.** `diff_snapshots.py` refuses two snapshots whose `register` differs.
