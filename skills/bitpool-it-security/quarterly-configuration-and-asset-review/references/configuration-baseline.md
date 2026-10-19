# The configuration baseline

Read before phase 3. Covers sub-task 7 — generating the rows, the diff and its dispositions — and the
ratification that establishes a baseline in the first place.

The values-free description of this stream, for auditors, is
`security-documentation/compliance/configuration-baseline-diff.md`. **This file is the executable
half**; that page is the published half. Do not duplicate one into the other.

## Standard versus dump — the distinction everything rests on

| | Normative (a **standard**) | Descriptive (a **dump**) |
|---|---|---|
| States | What the configuration **ought** to be | What it **is**, at a point in time |
| Changes | Only by a deliberate, approved act — `ratify`, with a named approver | Whenever the estate changes |
| Lives in | `configuration-hardening/hardening-standard-{windows,macos,ios}-endpoints.md` | `configuration-hardening/dumps/YYYY-MM-DD/` |

Both sit in `security-documentation-restricted`. **A snapshot regenerated each cycle cannot be
deviated from, because it IS the configuration** — that is the defect this stream exists to fix.

### What keeps them apart now that they share a repository

Changed 2026-09-24. Until then the dumps were kept out of the standards repo altogether, on the
argument that physical separation was the cheapest guarantee that a commit to a standard is a human
act. **The user decided to retain the dumps in the repo**, one dated folder per cycle: a dump held in
the exporter's scratch folder was one run away from being overwritten, and without the previous
cycle's dump there is nothing to diff against. The guarantee is now carried by mechanism instead of
by distance:

- **Machine-written content on a standard page is confined to two marker lines**,
  `<!-- GENERATED:START -->` and `<!-- GENERATED:END -->`. Outside them, only the approval-header
  value cells and the frontmatter `status` / `last_reviewed` are ever machine-written.
- **Only `ratify` writes there**, and it will not run without `--approved-by "<name>"`. `generate`,
  `diff` and `pack` write into a dated folder and never touch a standard page.
- **The one cell between the markers a human writes is a row's `Deviation`**, and it holds `none` or
  an `EXM-nnn` reference into the ISMS exemption register — nothing else. `ratify` reads it back and
  carries it forward; see *The standard schema* below.
- **So a commit that changes a standard's generated tables is always a ratification** — reviewable
  as one, and attributable to the name in its `Approved by` cell — or a `Deviation` cell set to an
  `EXM-nnn`, reviewable against that register entry.

## The dated folder — one per cycle

`security-documentation-restricted/configuration-hardening/dumps/YYYY-MM-DD/`, named for the UTC
collection date the exporter fixes once, when the run starts. The exporter places its files there
itself at the end of a run.

| File | Written by | Nature |
|---|---|---|
| `intune-config-export.json` | the exporter | **Raw, unaltered**, `-text -diff` |
| `intune-config-export-readable.json` | the exporter | **Raw, unaltered**, `-text -diff` — group GUIDs rewritten as names |
| `setting-definitions.json` | the exporter | **Raw** Graph setting-definition bodies, keyed by settingDefinitionId, `-text -diff` |
| `collection-manifest.json` | the exporter | Provenance — when, who, which tool commit, the sha256 of every file, and `incidents`: everything the run failed to fetch. **Read `incidents` before using the folder** — see the acceptance test |
| `baseline-rows.json` | `generate` | Generated rows, generator version `2.0` |
| `README.md` | `generate` | Generated cycle record, frontmatter `type: Record` / `doc_type: record` |
| `diff-vs-YYYY-MM-DD.md` and `.json` | `diff` | Generated diff report; the date in the name is the **baseline** folder |
| `evidence-pack.html` | `pack` | Generated, self-contained — see `configuration-evidence-pack.md` |

Two files sit at the `dumps/` root, because they span cycles:

- **`id-map.json`** — the permanent `row_key` to `BP-` id map. See *Ids are permanent* below.
- **`RATIFIED`** — plain text, exactly one line: the `YYYY-MM-DD` name of the dated folder the
  current standards were ratified from. It is what `diff` compares against by default. **It does
  not exist until the first ratification** — its absence is the machine-readable form of every
  standard's `status: draft`.

**The raw files are evidence and are never edited, renamed or re-serialised.** `baseline-rows.json`
records `source_sha256` and `definitions_sha256`, and `collection-manifest.json` records the sha256
of every file, so an alteration is detectable. `.gitattributes` marks the raw files `-text -diff`, so
the repo-wide line-ending normalisation cannot rewrite a byte. Compare dumps with the differ, never
with `git diff`.

**The markdown in a dated folder is a record, not a page.** It carries `type: Record` frontmatter
and is never added to `SUMMARY.md` by hand. What keeps it out of the repo's page indexes is
`EVIDENCE_TREES` in `_meta/skill/scripts/regenerate-indexes.py`: `collect_pages()` skips every file
under `configuration-hardening/dumps` before reading it, so none reaches `manifest.json`,
`INDEX.md` or `SUMMARY.md`, and each run reports the count —
`Evidence trees not indexed (configuration-hardening/dumps): N .md file(s) skipped.`
`OKF_INDEX_SKIP_DIRS` is seeded from the same entry, but it only stops a per-directory `index.md`
being written; it is a redundant second guard, not the exclusion. GitBook publication is governed
by the sync scope, which the user controls; narrowing it to a dedicated published folder puts the
dumps tree outside it entirely.

**Never hand-edit a generated file.** `generate` and `diff` rewrite them — byte-identically for the
same inputs, so an edit is silently lost on the next run. A human note about a cycle belongs in the
ticket comment.

## Running phase 3 — `run_config_cycle.py`

**This is the way to run it.** The wrapper calls the generator, the differ and the pack builder
through their own CLIs, so what it does is exactly what running each by hand would do. What it adds
is the path resolution, the defaults and the refusals.

Paths resolve **argument, then environment variable, then default**, and the wrapper prints which
one won:

| Argument | Environment | Default |
|---|---|---|
| `--standards-repo` | `STANDARDS_REPO` | The nearest ancestor of the script with a `security-documentation-restricted` child |
| `--dumps-dir` | `CONFIG_CYCLE_DUMPS_DIR` | `<repo>/configuration-hardening/dumps` |
| `--standards-dir` | `CONFIG_CYCLE_STANDARDS_DIR` | `<repo>/configuration-hardening` |
| `--generator`, `--differ`, `--pack-builder` | `CONFIG_CYCLE_GENERATOR`, `CONFIG_CYCLE_DIFFER`, `CONFIG_CYCLE_PACK_BUILDER` | The scripts beside it |

The `STANDARDS_REPO` default works from a skills-repo checkout (`ai-skills` or the Hermes skills repo) that sits beside
`security-documentation-restricted`, as both do under `C:\BitpoolDev\Github-Bitpool\`. **Run from an
installed Hermes skill copy (under `$HERMES_HOME/skills/`), it does not resolve — set `STANDARDS_REPO`.** The exporter reads the same
variable, so one setting serves both. `--help` on the script lists every argument.

```bash
S=<this skill's scripts/ folder, as a WSL path>   # e.g. under $HERMES_HOME/skills/

# every cycle, first
wsl -e bash -lc "python3 $S/run_config_cycle.py status"

# cycle 1: generate, then ratify (dry-run first, and only on the approver's word).
# YYYY-MM-DD is 2026-09-27, the first export carrying collection-manifest.json and
# setting-definitions.json; see "Which folder cycle 1 ratifies"
wsl -e bash -lc "python3 $S/run_config_cycle.py generate YYYY-MM-DD"
wsl -e bash -lc "python3 $S/run_config_cycle.py ratify YYYY-MM-DD --approved-by '<approver name>' --dry-run"
#   ...then, on the approver's word, the same command without --dry-run
wsl -e bash -lc "python3 $S/run_config_cycle.py pack YYYY-MM-DD"

# every later cycle: generate the new folder, diff it against RATIFIED, pack it
wsl -e bash -lc "python3 $S/run_config_cycle.py generate YYYY-MM-DD"
wsl -e bash -lc "python3 $S/run_config_cycle.py diff"
wsl -e bash -lc "python3 $S/run_config_cycle.py pack YYYY-MM-DD"
```

| Subcommand | Does | Refuses when |
|---|---|---|
| `status` | Lists every dated folder: which one `RATIFIED` names, which carry `baseline-rows.json`, and whether each raw file still matches the sha256 in `collection-manifest.json` | Writes nothing. **Exits `1` on an integrity problem** — a raw file that no longer matches its manifest, or stale rows. Run it first, every cycle |
| `generate <date>` | Writes `baseline-rows.json` and `README.md` for that folder and updates `id-map.json`. The generated timestamp comes from the manifest's `collected_at_utc`, else `<date>T00:00:00Z`, so regenerating a folder is **byte-identical** | A raw file no longer matches the manifest; the dump carries none of the three collections; the id map is v1; **the dump is truncated** — any `configurationPolicies` entry, assigned or not, whose `settingCount` differs from its `settings`. The generator names every offending policy with both numbers and writes nothing. Only `generate_baseline.py --allow-truncated` gets past it, and that override is written into `meta.setting_count_check`, the cycle record and the preview, so a baseline built from a truncated dump always says so. A policy with no `settingCount` at all is a warning, listed under `meta.setting_count_check.uncounted`, not a pass |
| `diff [--baseline D] [--current D]` | Baseline defaults to `RATIFIED`, current to the newest dated folder. Writes `diff-vs-<baseline>.md` and `.json` into the current folder, prints the text summary, exits with the differ's code | Nothing is ratified and no `--baseline` was given — there is no standard to diff against; baseline and current are the same folder; the differ refuses the comparison |
| `ratify <date> --approved-by "<name>" [--approved-on D] [--dry-run]` | Renders the per-platform tables between the markers of each standard page, fills five approval-header value cells, sets `status: active` and `last_reviewed`, and writes `RATIFIED` last. All three pages are checked before any is written, so a refusal never leaves the set half-ratified. Each row's `Deviation` cell is carried forward by BP id — see *The standard schema* | `baseline-rows.json` is missing or its `source_sha256` does not match the raw dump; a raw file no longer matches the manifest; a row id disagrees with `id-map.json`; a page lacks the markers. **Weak provenance, each with its own override:** no `collection-manifest.json` (`--allow-missing-manifest`); the manifest records incidents (`--accept-incomplete-baseline`, and every incident is then printed beside the approver's name); **any label left raw** — display resolution is not `catalog`, or it is `catalog` but records unresolved rows or no usable unresolved count (`--allow-raw-labels`, and every affected row is printed by BP id and setting id). A malformed `incidents` list has no override. **Every refusal that applies is reported together**, so one `--dry-run` shows the approver all of them. Also: the folder is older than the current `RATIFIED` one (`--allow-backdate`); rows exist for a platform no page covers (`--allow-unmapped-platforms`); an already-ratified folder whose rows, approver or approval date would change (`--re-ratify`, a minor version bump) |
| `pack <date> [--baseline D \| --no-baseline] [--allow-missing-manifest]` | Builds `evidence-pack.html` in that folder. The baseline defaults to `RATIFIED` unless that is the folder being packed | The baseline is the folder being packed; the folder has no `collection-manifest.json` and `--allow-missing-manifest` was not given. See `configuration-evidence-pack.md` |

Exit codes: `0` success (for `diff`, no differences), `1` differences (`diff`) or an integrity problem
(`status`), `2` an error or a refusal. **A refusal writes nothing.**

The same-folder refusal is `SKILL.md` load-bearing rule 2 made mechanical: **a diff of a dump against itself
always comes back clean**, and a clean self-comparison is the most convincing wrong answer the cycle
can produce.

Every file the wrapper writes lands in the working tree of `security-documentation-restricted`.
**The user commits them** — never commit or stage on their behalf.

### Which folder cycle 1 ratifies — 2026-09-27

**Cycle 1 ratifies `dumps/2026-09-27`**, the first export from the current exporter, collected
2026-09-27T23:30:30Z by `eric-mcp@Bitpool.com` from committed code (`tool.git_commit` `08af99e`,
`tool.git_dirty: false`). Its manifest records `incidents: []`, all 691 setting definitions
resolved, 36 of 36 `configurationPolicies` passed the `settingCount` gate, and
`baseline-rows.json` reports `display_resolution.mode: catalog` with 149 rows resolved and 0
unresolved. It replaced, under `--force-replace`, an export taken 90 minutes earlier by
uncommitted exporter code; the two gave identical rows. **It was ratified on 2026-09-28**
(GMT+10) by Eric Sharp as version 1.0 of BP-WIN, BP-MAC and BP-IOS. Test-group policies were
kept as they stood.

**The 2026-09-24 folder was retired on 2026-09-28** and no longer exists. It was a dump of the
same tenant from before the manifest and the definitions existed. Its raw export differs from
2026-09-27's only in the order Graph returned the two `targetedManagedAppConfigurations` in, which
is why the raw sha256 moved (`8f8d089285c2c0b2…` to `bab0a439d6382639…`) with nothing changed:
**a raw hash is not a change detector; the diff is.** Before it went, a diff of its rows against
2026-09-27's gave 0 differences, 149 display-only relabels and 0 of 522 ids moved — real-data
proof that labels are never diffed. `id-map.json` was kept: re-seeding it from 2026-09-27 gave
identical ids.

**The rule it illustrated still holds for any folder.** A folder without
`collection-manifest.json` or `setting-definitions.json` is never a ratification source. A
standard ratified from one would

- **show raw Graph ids where the user decided values are shown human-readable.** With no
  definitions, `generate` runs with `display_resolution.mode: none`, so a rendered row reads
  `BP-WIN-0006 | device_vendor_msft_bitlocker_allowstandarduserencryption | device_vendor_msft_bitlocker_allowstandarduserencryption_1`
  — the raw setting id as the label and the raw choice id as the value;
- **cite a dump nobody can date, attribute or show complete.** There is no recorded collection time
  or collector, its generated timestamp falls back to midnight UTC on the folder date, `status`
  has no recorded hash to check its raw files against, and there is no `incidents` record to show
  the run fetched everything.

**The wrapper refuses one, on every count at once.** `ratify <date> --dry-run` exits `2` and
writes nothing, reporting each reason together: no `collection-manifest.json`
(`--allow-missing-manifest`), and rows generated with display resolution `none`
(`--allow-raw-labels`). **Never pass those flags to get a folder through** — they exist so an
approver can ratify a weak folder knowingly. A ratification source is an export from the
current exporter whose folder carries

- `collection-manifest.json`, with `incidents` empty or every entry dispositioned — see the
  acceptance test;
- `setting-definitions.json`, so that `baseline-rows.json` reports `display_resolution.mode: catalog`
  with no unresolved rows. A single unresolved label is also refused without `--allow-raw-labels`.

A folder without a manifest is a descriptive dump only. `pack` refuses it (exit `2`) unless
`--allow-missing-manifest` is given; with it, every provenance field reads `NOT RECORDED` and a
high-severity finding says so. **Do not backfill a manifest**: one written after the fact would
assert a collection time and a collector that nobody recorded.

## Ratify, then freeze

Bitpool decision, 2026-09-18, refined 2026-09-25. **The first corrected dump of a platform is
ratified as the approved baseline.** From then on every difference is authorised, rationalised or
recorded as a gap. *Corrected* means an export from the current exporter, carrying a manifest and
the setting definitions — see *Which folder cycle 1 ratifies*. For Intune that is 2026-09-27.

**Frozen means no cycle ever changes a standard as a side effect.** A later dump reaches a standard
only through another `ratify` — a deliberate, reviewed act, never an automatic step of each cycle,
and normally made only once every difference in the diff has a disposition. The first ratification
sets `Version` to `1.0`; each later one bumps the minor (`1.0` to `1.1`). Re-ratifying the same
date is idempotent — the version, the approval date and the page bytes stay the same.

**The approval date is Bitpool's calendar day in GMT+10** (user decision, 2026-09-28). Without
`--approved-on`, `ratify` stamps today's GMT+10 date, so an approval given at 09:48 on the 28th reads
the 28th, not the UTC 27th. Collection times and dump folder names stay UTC, so a folder can be
dated a day before its approval: cycle 1 is `dumps/2026-09-27`, approved on 2026-09-28.

**Never run `ratify` on your own initiative.** It writes a named person's approval into a normative
document. Run it only when that person has said to, with their name, and show them the `--dry-run`
output first.

- `Authority` on every generated row reads `bitpool:ratified <date>`.
- **Never write a `cis:` citation that has not been read out of the benchmark.** A fabricated
  citation survives review in a way an empty cell does not, which makes it worse than nothing.
- The accepted residual — that nobody verified the day-one configuration against an external
  benchmark — is **stated in the standard's scope section**, not left implied. An unstated residual
  reads as a claim of benchmark derivation.

**What `ratify` writes**, between the markers of each page: an *In scope* table, an *Excluded, and
why* table, then one `### <object name>` section per object, each opening with the object id and then
the eight-column table. In the approval header it fills five value cells — `Version`,
`Approved by`, `Approved on`, `Effective from` and `Ratified from`, the last as
`dumps/YYYY-MM-DD (sha256 <first 16 hex>)` — and every other byte of the page stays as a human wrote
it. The header must carry exactly these labels: `Standard ID`, `Version`, `Approved by`,
`Approved on`, `Effective from`, `Ratified from`, `Next review`, `Supersedes`, `Authority`.

**`RATIFIED` and every page's `Ratified from` cell must name the same folder.** If they disagree, the
standard and the diff's default baseline are two different things — an integrity finding to raise
before any diff is read.

## Scope: assigned objects only

An unassigned policy enforces nothing, so it is not part of a baseline and a change to one is not
drift. Measured by the v2 generator on the cycle 1 export (2026-09-27): **44 assigned objects in scope, 19
excluded as unassigned** — 14 `configurationPolicies` of 36, 3 `deviceConfigurations` and 2
`deviceCompliancePolicies` — including all four dormant Security Baseline profiles. The v1 figure
was 43, because v1 emitted rows only for settings and one assigned object,
`Default Device Features Configuration` (macOS `deviceConfigurations`), carries only metadata.
Under v2 its name row keeps it in scope and visible.

**A policy assigned to a test group is in scope, and is not a finding.** User decision,
2026-09-28: test groups are expected in most exports. Cycle 1 ratified six such policies as they
stood, among them `PHIL LAPS` and two `TESTING …` policies targeting `Phil PC (TESTING)` and
`Test User 1 (TEMP)`. Do not suggest unassigning them before a ratify. When one comes or goes, the
diff records it like any other object and the approver disposes of it.

**List every exclusion with its reason.** The generator records each one under
`meta.scope.excluded_objects` with its `object_id`, and `ratify` renders them into each standard's
*Excluded, and why* table. The dormant Security Baseline profiles record an intention to adopt the
Microsoft baselines that was never completed — a future reader must not mistake that for an
oversight. `TROUBLESHOOTING Disable all firewalls` is deliberately unassigned and used for
troubleshooting only; say so, because the name invites the question.

An object that crosses the boundary between cycles is one **`REASSIGNED`** event, matched on
`object_id` — not eighty removed rows. Unassigning one Settings Catalog policy would otherwise read
as a catastrophe instead of one checkbox.

## Before generating: the acceptance test

Run it every cycle, before `generate`, `diff` or `ratify`. **Zero mismatches and zero
undispositioned incidents is the pass condition.**

- **`incidents` in `collection-manifest.json` must be empty, or every entry read and
  dispositioned.** The exporter records as an incident anything that left the export incomplete — a
  list Graph refused or cut off, a failed `$batch` chunk, an object whose assignments or settings
  came back missing, an `isAssigned` it could not determine, and **a setting-definitions fetch
  that did not work**: a `$batch` POST that failed outright while any definition is still
  unresolved, or more than `DEFINITIONS_UNRESOLVED_MAX_PCT` (5%) of the referenced definitions
  unresolved whatever the cause. It refuses to place an export that has any incident unless
  `--accept-incomplete` was passed. A non-empty list therefore means an incomplete
  export was placed deliberately. Missing data diffed against a complete baseline reads as settings
  removed from Intune, and a failed assignments request looks exactly like an unassigned policy.
  Downstream, `status` reports such a folder as a problem and exits `1`, `ratify` refuses it
  without `--accept-incomplete-baseline`, and the pack raises it as a high-severity finding —
  **but `generate` and `diff` run on it without complaint.** So **read it yourself**, before any of
  them, and never ratify a folder with an undispositioned incident. A folder with no manifest has
  no incident record at all — say so, rather than reading the silence as a clean run.
- For every `configurationPolicies` object, `settingCount` must equal `length(settings)`. `generate`
  now refuses a dump where any does not, and writes nothing — see the `generate` row above — so a
  refusal there is this test failing, not a tooling fault. Re-export; do not reach for
  `--allow-truncated`.
- `isAssigned` must be present on every `configurationPolicies` object, and should agree with the
  `assignments` array. The generator lists any disagreement under
  `meta.scope.assignment_disagreements`; **a disagreement is a finding, not a formatting quirk.**
- `_unresolved` in `setting-definitions.json` should be empty. A few misses under the exporter's
  threshold are only a warning at placement, so they arrive here rather than as an incident. A
  non-empty list does not block the diff — labels are never diffed — but each entry is a setting
  whose label will show raw, and **any
  in-scope row it leaves unlabelled blocks `ratify`**: rows with even one unresolved label are
  refused without `--allow-raw-labels`, and the refusal lists every affected row by BP id and
  setting id.

```bash
wsl -e bash -lc 'cd "/mnt/c/BitpoolDev/Github-Bitpool/security-documentation-restricted/configuration-hardening/dumps/YYYY-MM-DD" && python3 -c "
import json, os
d = json.load(open(\"intune-config-export.json\", encoding=\"utf-8-sig\"))
p = d[\"configurationPolicies\"]
bad = [x[\"name\"] for x in p if x.get(\"settingCount\") != len(x.get(\"settings\") or [])]
noflag = [x[\"name\"] for x in p if \"isAssigned\" not in x]
print(len(p), \"policies;\", len(bad), \"count mismatches;\", len(noflag), \"missing isAssigned\")
for n in bad + noflag: print(\"  \", n)
if os.path.exists(\"collection-manifest.json\"):
    inc = json.load(open(\"collection-manifest.json\", encoding=\"utf-8-sig\")).get(\"incidents\")
    print(\"incidents:\", \"FIELD MISSING\" if inc is None else len(inc))
    for i in inc or []: print(\"  \", i)
else:
    print(\"incidents: not recorded - no collection-manifest.json\")
"'
```

On the 2026-09-27 dump — a clean export — it prints:

```
36 policies; 0 count mismatches; 0 missing isAssigned
incidents: 0
```

`incidents: not recorded` means a folder with no manifest. `FIELD MISSING` means a manifest written before the
incidents gate existed — treat it as no record, not as a clean run.

The exporter discarded `@odata.nextLink` inside batched sub-responses until 2026-09-18. Four policies
returned 25 settings against declared counts of 306, 287, 65 and 64 — 210 fetched against 832
declared — and the export contained zero occurrences of the link, because it was thrown away with
the response envelope. **A truncated export produces a diff that reports no change.**

## Identity: the object id — and the name is a setting

Changed 2026-09-25, by user decision. **A configuration object is identified by its Intune object id
(GUID), never by its name.** Every row carries

    row_key = collection|object_id|setting_id        (object_id and setting_id lowercased)

**No name and no platform in the key.** The object id is unique on its own, so a platform adds no
uniqueness — only another way for the key to move. `row_key` is the durable identity, the id-map key
and the diff join key.

**The display name is itself a diffed setting.** Every in-scope object gets one synthetic row:
`setting_id` = `@displayName`, `setting_name` = `Policy name`, `required_value` and `display_value`
= the display name verbatim, `mode` = `identity`. It sorts first within its object. So **a rename is
one visible change on one row, and no other row's identity moves.**

### What this supersedes

Until 2026-09-25 the rule was to key on `(collection, @odata.type or platform, normalised name)`,
with the object id recorded alongside. It was written because display names are **ambiguous** in
this tenant, not merely fragile: `deviceConfigurations` holds *"Default Device Restrictions
Configuration"* twice — once macOS, once iOS, both assigned — and two typo spellings are live,
`Defualt` and `Defult`, so normalising one does not reach the other. The v1 generator folded both
typos in its name normaliser for exactly that reason.

**Those facts still stand, and they no longer matter for identity.** Under an object-id key the
duplicate name is simply two objects, and a typo corrected in the Intune UI is a single `RENAMED`
event. They survive as the evidence for why a name can never be a key.

### Ids are permanent

`id-map.json` at the `dumps/` root, schema 2: `{"schema": 2, "ids": {"<row_key>": "BP-WIN-0001"}}`.
Prefixes `WIN`, `MAC`, `IOS` and `GEN`, four digits.

- **Existing ids are always reused.** A new `row_key` takes the next free number for its prefix.
- **A vanished key keeps its id forever.** That is what reserves the number; it is never reissued.
- **A fresh map assigns ids in row sort order**, so they run in reading order on the standard page.
- **A v1 map** — a flat object with no `schema` key, keyed on the old name tuple — **is refused**
  with a message to delete and regenerate it. It is never silently migrated: every v1 key embedded a
  name, so none could be carried across to an object-id key honestly. The v1 map held 478 ids; no
  standard had been ratified from any of them when identity changed.

Renumbering a standard silently invalidates every prior review, ticket and auditor note that cited
an id. Never delete an entry from a schema 2 map.

## Human-readable values are for display only

Settings Catalog rows are resolved from `setting-definitions.json`: the definition's `displayName`
becomes `setting_name`, and for a choice value, the option whose `itemId` equals the raw value
supplies `display_value`. A collection value's labels are joined with `; `.

**The diff never reads them.** It compares `required_value` — the raw Graph value — and row
presence, and nothing else. So a Microsoft relabel in the Settings Catalog **never** creates a
phantom difference, and a label that did not move can never hide a value that did.

- Any lookup miss falls back to the raw value and is counted in `meta.display_resolution.unresolved`.
- `deviceConfigurations` and compliance rows keep their Graph property name as `setting_name`.
  **Never invent a label** for them — a paraphrase reads as authoritative and is not.
- Without `--definitions`, `meta.display_resolution.mode` is `none` and every label is the raw id.
- **Labels do not gate the diff, but they gate the standard.** `ratify` refuses rows whose mode is
  not `catalog`, or whose `unresolved` count is non-zero or unreadable, unless `--allow-raw-labels`
  is given — the page a reader approves would otherwise show raw ids with nothing marking which.
  `catalog` alone does not mean every label resolved.

## The row set

Measured on the cycle 1 dump (2026-09-27) by generator version 2: **522 rows — 478 setting rows over 44
assigned objects, plus one name row per object.** One object,
`Default Device Features Configuration` (macOS `deviceConfigurations`), is assigned but carries
only metadata, so its name row is its only row. **All of them are kept** — user decision,
2026-09-25:

- **Collection-valued leaves stay.** The local Administrators group membership, the Edge
  force-install extension list and the Platform SSO URLs live there. A standard that omits who is a
  local admin is worse than no standard.
- **All 226 iOS rows stay**, 216 of them from `deviceConfigurations`.
- Base64 and any other string over `--max-inline` (default 256) is written as `sha256:<hex>`, so the
  diff still fires on any payload change while the page stays readable. Empty lists and dicts are
  dropped. A settingDefinitionId repeated within one policy is disambiguated `<id>#2`.

`mode` is `compliance` on `deviceCompliancePolicies` rows, `identity` on the name row, and
`enforced` on everything else.

## Reading the diff

`diff_baseline.py` joins on `row_key` and **compares only `required_value` and row presence** —
never `setting_name`, `display_value`, `object_name`, `enforced_at` or `verify`. It reports **both
directions**, in-live-not-in-baseline and in-baseline-not-in-live. One direction always looks tidier
and always hides half the drift.

| Event | Means | Reported as |
|---|---|---|
| `RENAMED` | The `@displayName` row changed | **One object event** — old and new name, the object id, and how many settings were unaffected. Never also reported as `CHANGED` |
| `REASSIGNED` | An object moved between assigned and `meta.scope.excluded_objects`, matched on `object_id` | One event, not one per row |
| `OBJECT ADDED` / `OBJECT REMOVED` | Every row of an object appeared or vanished, and it was not merely (un)assigned | One event per object, never a wall of rows |
| `CHANGED` | Same `row_key`, different `required_value` | One per row |
| `ADDED` | A row new to an object that already existed — a setting nobody has ratified | One per row |
| `REMOVED` | A row gone from an object that still exists — a control that stopped being enforced | One per row. Record it; never let a row vanish quietly |
| `INTEGRITY` | The id map broke its promise — one `row_key` carrying two ids across cycles, one id on two rows, or a retired id reissued | Not an estate change, but loud: a renumbered standard silently invalidates every sign-off that cited an id |

**Relabels are listed as not counted.** A changed `setting_name` or `display_value` with an unchanged
raw value is shown so a reader can see it, and never drives the exit code.

- **Exit codes:** `0` no differences, `1` differences — a normal cycle, not a failure — and `2` an
  error, or a comparison that could not be trusted.
- **Generator major versions must match.** A 1.x file against a 2.x file exits `2`: the keys are
  different shapes, and a join across them would report every row as both removed and added. So does
  a file with no `generator_version`, a row whose `row_key` was not built from its own fields,
  duplicate `row_key`s, and a baseline diffed against itself.
- **A no-change result still prints full counts** in both directions. That is the evidence the
  comparison ran; "no change" alone is indistinguishable from nobody having looked.

## The standard schema — eight columns

`| ID | Setting | Required value | Authority | Mode | Enforced at | Deviation | Verify |`

| Column | Holds |
|---|---|
| `ID` | `BP-WIN-0001` style, from `id-map.json`. Stable, never reused, retired rather than renumbered |
| `Setting` | `setting_name`, the human label. **Not the join key** — that is `row_key`, and the raw id is in `Verify` |
| `Required value` | `display_value`, the human label for the raw value |
| `Authority` | `isms:<Policy> §<section>` · `cis:<benchmark> <section>` · `vendor:<doc>` · `bitpool:ratified <date>`. **Never empty** — a row with no authority is a dump row that wandered in |
| `Mode` | `enforced` · `compliance` · `identity`, as generated. `compliance` is the *monitored* verb — a compliance policy evaluates and reports device state, it does not set it — and A.8.9 treats implemented and monitored as different verbs |
| `Enforced at` | `Intune > <collection> > <object name>` — the mechanism **and** the object |
| `Deviation` | `none`, or `EXM-nnn` pointing at the ISMS exemption register — nothing else. **Never a rationale**: that lives only in the register |
| `Verify` | `` `<setting_id> = <raw required_value>` `` — the exact value the diff compares |

The name row is always the first row of its object's table.

**The `Deviation` cell is the one cell between the markers a human writes.** A new row renders
`none`. When a permanent departure is approved, its `EXM-nnn` is written into that row's cell by
hand. On every later `ratify`, the wrapper reads each non-`none` cell back and **carries the
`EXM-nnn` forward by BP id** into the re-rendered row — but only while that id still names the same
object and the same setting. One it cannot carry, because the row is gone or the id now names
something else, is printed as a `WARNING` naming the id and the reference, and is not carried: update
the exemption register entry. It is never dropped silently.

## The disposition rubric

Every difference gets exactly one. **Do not default to writing a risk** — a register padded with
routine design decisions dilutes the entries that matter.

| | The finding | Disposition |
|---|---|---|
| **A** | Genuine business need, scoped to it | Record the rationale — in the cycle's ticket comment, or, for a permanent departure from the standard, in an `EXM-nnn` exemption register entry. Never in the standard. The control is **met** |
| **B** | Need genuine, but wider than required | Risk plus treatment plan, via `/manage-drata-control` |
| **C** | Nobody can say why it changed | A real gap. Engineering work, `IRT` ticket, created undated |

A `RENAMED` event is usually disposition **A** with a one-line rationale — but it is still a
difference, and it still gets one.

A permanent approved departure becomes an `EXM-nnn` entry in the exemption register,
`security-documentation-restricted/isms-exemptions/exemption-register.md`, and the standard row's
`Deviation` cell is set to that `EXM-nnn`; `ratify` carries it forward from then on. **The cell holds
`none` or `EXM-nnn` and nothing else — the rationale lives only in the register, never in the
standard.**

## Known blind spots in the current export

Record these rather than letting a reader assume total coverage. Each is a candidate gap, not a
confirmed absence:

- `/deviceManagement/compliancePolicies` — the **new Settings-Catalog-format compliance surface**. A
  compliance policy authored in that format today is invisible, while the legacy collection
  confidently reports its own count.
- `/deviceManagement/intents` and `/templates` — Endpoint Security profiles.
- `/deviceManagement/assignmentFilters` — also returns `payloads[]`, the reverse index of which
  policies each filter scopes.
- The three `windows{Driver,Feature,Quality}UpdateProfiles`.
- `/deviceManagement/reusablePolicySettings` — referenced from Settings Catalog policies by GUID.
- `scheduledActionsForRule` / `scheduledActionConfigurations`.
- **Partly closed 2026-09-25:** `collection-manifest.json` now records the run start time, the
  collector, the tenant, the client id, the tool's git commit and whether the script differed from
  it, and every incident the run recorded. It still does not record the Graph API base or version
  each collection was read from.

## macOS: a possible control gap, not just a doc gap

No macOS software-update policy of any type exists in the tenant, and Microsoft publishes no macOS
security baseline. Apple declarative device management now delivers macOS software-update
enforcement — if Bitpool uses it, the object lives in a collection the export does not touch. **Probe
before concluding the documentation is simply wrong.**
