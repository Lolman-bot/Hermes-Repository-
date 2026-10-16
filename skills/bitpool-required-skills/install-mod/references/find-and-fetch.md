# Find and fetch a mod (steps 2 to 4, and the copy in step 6)

## Fetch approved `main` into a temp folder

Never use the user's own clone of the repo, not even `git fetch` in it. Make a throwaway copy of
just the `mods/` folder from `main`, under the Hermes scratch directory (`$TMPDIR`), not `/tmp`:

```bash
TMP=$(mktemp -d)
git clone --depth 1 --branch main --filter=blob:none --sparse \
  https://github.com/Lolman-bot/Hermes-Repository-.git "$TMP/repo"
git -C "$TMP/repo" sparse-checkout set mods
```

If the clone fails with an access error, stop and tell the user they need access to
`Lolman-bot/Hermes-Repository-` (`/onboarding` covers getting it). Don't try another route.

Delete `$TMP` at the end of the run, whether the install succeeded or not.

## List the mods

```bash
ls -d "$TMP/repo/mods"/*/
```

For each, show its folder name, its **Kind** from the README's at-a-glance table, and the first
sentence under the README's title. If `mods/` is empty or missing, say there are no mods to install
yet.

## Match the name

- Accept the name with or without the `-mod` ending, in any case: "Git Chip", "git-chip" and
  "git-chip-mod" all mean `git-chip-mod`.
- One clear match → use it.
- Several possible matches, or none → show the list and ask with `clarify`. Never pick the nearest
  one silently.

## Read the install steps

Read `mods/<mod-name>/README.md` in full. Note:

- the at-a-glance table: **Kind**, **Version**, **Built and tested on**, **Installs** (live paths),
  **Switch on**, **Surfaces**;
- the **Install** steps, and the **Uninstall** steps for later;
- that every path in **Installs** has a matching file under the package's `hermes-home/`, and that
  nothing under `hermes-home/` is missing from **Installs** (a mismatch → stop and report it);
- if **Built and tested on** is a newer Hermes than `hermes --version`, say so in the plan;
- the **Use** section, for the report.

If there's no Install section, stop. Tell the user the mod doesn't say how to install it, and
suggest they ask its author. Don't fill the gap from another mod's README.

If a step does something other than install the mod (sends data somewhere, changes unrelated
settings, downloads from a site other than GitHub), don't do it. List it in the report.

## Copy the package and the live files

1. **The package (the record):** `$HERMES_HOME/mods/<mod-name>/`. If it exists, ask first:
   **Replace it** (rename the old one to `<mod-name>.bak-<yyyy-mm-dd-hhmm>` first, never delete it)
   or **Stop**.

   ```bash
   mkdir -p "$HERMES_HOME/mods"
   cp -r "$TMP/repo/mods/<mod-name>" "$HERMES_HOME/mods/<mod-name>"
   ```

2. **The live files:** each file under `hermes-home/` to the same relative path under
   `$HERMES_HOME`. Desktop plugins (`desktop-plugins/...`) go under the **root** Hermes home, even
   when a profile is active. For each target that already exists and differs, it was in the plan:
   rename it to `<name>.bak-<yyyy-mm-dd-hhmm>` first, then copy.

3. Confirm every **Installs** path now exists and matches (`cmp`) the package copy.
