# <mod-name>

<One paragraph, plain words: what the mod does for the person using it, and where they see it.>

| | |
|---|---|
| **Kind** | <desktop plugin \| TUI widget \| gateway hook \| shell hook \| Python plugin \| skin> |
| **Version** | 1.0.0 |
| **Built and tested on** | Hermes Agent <output of `hermes --version`, first line> |
| **Installs** | `<path under $HERMES_HOME>` (one line per file or folder under `hermes-home/`) |
| **Switch on** | <the one action: toggle in Capabilities → Plugins \| `/<id>` \| `hermes gateway restart` \| `hooks:` entry in config.yaml \| `hermes plugins enable <id>` \| `hermes config set display.skin <id>`> |
| **Surfaces** | <desktop / TUI / CLI / messaging platforms it affects> |

## How it looks

<What appears and where, per surface. "Nothing visible" for a mod that only acts.>

## How it works

```mermaid
<docs/flow.mmd, exactly>
```

<A sentence or two under the chart.>

## Install

With Hermes: run `/install-mod <mod-name>`. By hand:

1. Copy every file under `hermes-home/` to the same path under your Hermes home
   (`$HERMES_HOME`; desktop plugins go in the root Hermes home, not a profile's).
2. <The switch-on step, exactly. For a shell hook, the `hooks:` block to add to `config.yaml`:>

   ```yaml
   hooks:
     <event>:
       - command: "<path under $HERMES_HOME>/agent-hooks/<id>.<ext>"
   ```

3. <How to see it's working.>

## Uninstall

1. <The switch-off step, exactly.>
2. Delete the files listed under **Installs**.

## Use

<Every command, argument or control, and what it does.>

## Tests

<The exact command(s) to run from this folder, e.g.
`node --import ./tests/register-sdk-stub.mjs --test "tests/*.test.mjs"` or `python -m pytest tests`,
plus any Hermes check such as `hermes plugins doctor hermes-home/plugins/<id> --ci`.>

## Privacy

<What, if anything, leaves the machine, and where it goes. "Nothing" if nothing does.>
